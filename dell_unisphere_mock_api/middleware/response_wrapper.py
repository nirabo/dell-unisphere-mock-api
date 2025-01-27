import json
import logging
from datetime import datetime
from typing import Callable

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
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

            # Only wrap JSON responses
            content_type = response.headers.get("content-type", "")
            if not ("application/json" in content_type or isinstance(response, JSONResponse)):
                logger.debug(f"Not a JSON response (content-type: {content_type}), skipping")
                return response

            try:
                # Get response body
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk

                # Parse JSON
                data = json.loads(response_body)
                logger.debug(f"Response data: {data}")

                # Don't wrap responses that are already in our format
                if isinstance(data, dict) and ("@base" in data or "errorCode" in data):
                    logger.debug("Response already wrapped or is an error response, skipping")
                    return Response(
                        content=response_body,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type="application/json",
                    )

                # Create response wrapper
                formatter = UnityResponseFormatter(request)

                # If response is an error, format it as an error response
                if response.status_code >= 400:
                    error_response = formatter.format_error(
                        HTTPException(status_code=response.status_code, detail=data.get("detail", str(data)))
                    )
                    return Response(
                        content=json.dumps(error_response.model_dump(by_alias=True), default=json_serial),
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type="application/json",
                    )

                # Otherwise wrap as a normal response
                if isinstance(data, list):
                    wrapped = formatter.format_collection(data)
                else:
                    wrapped = formatter.format_collection([data])

                logger.debug(f"Wrapped response: {wrapped}")

                # Convert to JSON with custom serializer for datetime
                wrapped_json = json.dumps(wrapped.model_dump(by_alias=True), default=json_serial)
                return Response(
                    content=wrapped_json,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type="application/json",
                )
            except Exception as e:
                logger.error(f"Error wrapping response: {e}")
                return response

        except HTTPException as http_exc:
            # Handle HTTP exceptions (e.g., 404, 400, etc.)
            formatter = UnityResponseFormatter(request)
            error_response = formatter.format_error(http_exc)
            return Response(
                content=json.dumps(error_response.model_dump(by_alias=True), default=json_serial),
                status_code=http_exc.status_code,
                headers={"content-type": "application/json"},
                media_type="application/json",
            )
        except Exception as exc:
            # Handle unexpected errors
            logger.exception("Unexpected error in middleware")
            formatter = UnityResponseFormatter(request)
            error_response = formatter.format_error(exc)
            return Response(
                content=json.dumps(error_response.model_dump(by_alias=True), default=json_serial),
                status_code=500,
                headers={"content-type": "application/json"},
                media_type="application/json",
            )
