import json
import logging
from datetime import datetime
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

from dell_unisphere_mock_api.core.response import UnityResponseFormatter

logger = logging.getLogger(__name__)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat() + "Z"
    raise TypeError(f"Type {type(obj)} not serializable")


class ResponseWrapperMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)

            # Skip OpenAPI endpoints
            if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json"):
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

                if response_body_str:
                    response_data = json.loads(response_body_str)
                else:
                    response_data = {}

                # Check if response is already an ApiResponse (has entries field) or ErrorDetail (has errorCode field)
                if isinstance(response_data, dict) and ("entries" in response_data or "errorCode" in response_data):
                    # Response is already formatted, return as-is
                    content = json.dumps(response_data, default=json_serial).encode("utf-8")
                    headers = dict(response.headers)
                    headers["content-length"] = str(len(content))
                    return Response(
                        content=content,
                        status_code=response.status_code,
                        headers=headers,
                        media_type="application/json",
                    )

                # Format response
                formatter = UnityResponseFormatter(request)
                if response.status_code >= 400:
                    # format_error is a static method
                    error_response = await UnityResponseFormatter.format_error(
                        error_code=response.status_code,
                        http_status_code=response.status_code,
                        messages=[str(response_data.get("detail", "Unknown error"))],
                    )
                    content = json.dumps(error_response.model_dump(by_alias=True), default=json_serial).encode("utf-8")
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
                formatted_response = await formatter.format_collection([response_data] if response_data else [])
                content = formatted_response.model_dump(by_alias=True, exclude_none=True)
                content = json.dumps(content, default=json_serial).encode("utf-8")
                headers = dict(response.headers)
                headers["content-length"] = str(len(content))
                return Response(
                    content=content,
                    status_code=response.status_code,
                    headers=headers,
                    media_type="application/json",
                )

            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON: {e}")
                formatter = UnityResponseFormatter(request)
                error_response = await formatter.format_error(
                    error_code=400, http_status_code=400, messages=[f"Invalid JSON: {str(e)}"]
                )
                content = json.dumps(error_response.model_dump(by_alias=True), default=json_serial).encode("utf-8")
                headers = dict(response.headers)
                headers["content-length"] = str(len(content))
                return Response(content=content, status_code=400, headers=headers, media_type="application/json")

        except Exception as e:
            logger.error(f"Error in middleware: {e}")
            error_response = await UnityResponseFormatter.format_error(
                error_code=500, http_status_code=500, messages=[f"Internal server error: {str(e)}"]
            )
            content = json.dumps(error_response.model_dump(by_alias=True), default=json_serial).encode("utf-8")
            headers = {"content-type": "application/json", "content-length": str(len(content))}
            return Response(content=content, status_code=500, headers=headers, media_type="application/json")
