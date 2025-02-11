import json
import logging
import traceback
from datetime import datetime
from typing import Callable, Any

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from dell_unisphere_mock_api.core.response import UnityResponseFormatter
from dell_unisphere_mock_api.core.response_models import create_error_response

logger = logging.getLogger(__name__)

class UnityJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class ResponseWrapper:
    def __init__(self, response: JSONResponse):
        self.response = response

    def wrap(self) -> JSONResponse:
        content = self.response.body
        wrapped_content = {
            "errorCode": 0,
            "httpStatusCode": self.response.status_code,
            "messages": [],
            "data": content,
        }
        self.response.body = wrapped_content
        return self.response

class ResponseWrapperMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)

            # Skip OpenAPI endpoints and 204 No Content responses
            if (request.url.path.startswith("/docs") or 
                request.url.path.startswith("/openapi.json") or
                response.status_code == 204):
                return response

            # Get response body
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            # Parse JSON
            try:
                # Try to decode as UTF-8 first
                try:
                    response_body_str = response_body.decode("utf-8")
                except UnicodeDecodeError:
                    # If UTF-8 fails, try to decode as latin1
                    response_body_str = response_body.decode("latin1")

                response_data = json.loads(response_body_str) if response_body_str else {}

                # Check if response is already an ApiResponse or ErrorDetail
                if isinstance(response_data, dict) and ("entries" in response_data or "errorCode" in response_data):
                    # Response is already formatted, return as-is
                    return Response(
                        content=response_body,
                        status_code=response.status_code,
                        headers=response.headers,
                        media_type="application/json",
                    )

                # Format response
                formatter = UnityResponseFormatter(request)
                if response.status_code >= 400:
                    error_response = create_error_response(
                        error_code=response.status_code,
                        http_status_code=response.status_code,
                        messages=[str(response_data.get("detail", "Unknown error"))],
                    )
                    content = json.dumps(error_response.model_dump(by_alias=True), cls=UnityJSONEncoder).encode("utf-8")
                    headers = dict(response.headers)
                    headers["content-length"] = str(len(content))
                    return Response(
                        content=content,
                        status_code=response.status_code,
                        headers=headers,
                        media_type="application/json",
                    )

                # For success cases, wrap the response in ApiResponse format if it's not already
                if hasattr(response_data, "model_dump"):
                    response_data = response_data.model_dump(by_alias=True, exclude_none=True)

                # Format as a collection response
                try:
                    # If response_data is already a list, use it directly
                    if isinstance(response_data, list):
                        formatted_response = await formatter.format_collection(response_data)
                    # If response_data is a dict and has 'entries', it's already formatted
                    elif isinstance(response_data, dict) and "entries" in response_data:
                        return Response(
                            content=response_body,
                            status_code=response.status_code,
                            headers=response.headers,
                            media_type="application/json",
                        )
                    # Otherwise, wrap it in a list
                    else:
                        formatted_response = await formatter.format_collection([response_data] if response_data else [])

                    response_model = formatted_response.model_dump(by_alias=True, exclude_none=True)
                    content = json.dumps(response_model, cls=UnityJSONEncoder).encode("utf-8")
                    headers = dict(response.headers)
                    headers["content-length"] = str(len(content))
                    return Response(
                        content=content,
                        status_code=response.status_code,
                        headers=headers,
                        media_type="application/json",
                    )

                except Exception as e:
                    logger.error(f"Error in format_collection: {e}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    error_response = create_error_response(
                        error_code=500,
                        http_status_code=500,
                        messages=[str(e)]
                    )
                    content = json.dumps(error_response.model_dump(by_alias=True), cls=UnityJSONEncoder).encode("utf-8")
                    return Response(
                        content=content,
                        status_code=500,
                        headers={"content-type": "application/json"},
                        media_type="application/json",
                    )

            except json.JSONDecodeError:
                # If response is not JSON, return it as-is
                return Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=response.headers,
                    media_type=response.media_type,
                )

        except Exception as e:
            logger.error(f"Error in middleware: {e}")
            error_response = create_error_response(
                error_code=500,
                http_status_code=500,
                messages=[str(e)]
            )
            return Response(
                content=json.dumps(error_response.model_dump(by_alias=True), cls=UnityJSONEncoder).encode("utf-8"),
                status_code=500,
                headers={"content-type": "application/json"},
                media_type="application/json",
            )
