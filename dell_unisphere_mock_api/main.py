"""Main FastAPI application module for Dell Unisphere Mock API."""

import logging
import logging.config
import os
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Request, routing
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.middleware.csrf import CSRFMiddleware
from dell_unisphere_mock_api.middleware.response_headers import ResponseHeaderMiddleware as ResponseHeadersMiddleware
from dell_unisphere_mock_api.middleware.response_wrapper import ResponseWrapperMiddleware
from dell_unisphere_mock_api.routers import (
    acl_user,
    cifs_server,
    disk,
    disk_group,
    filesystem,
    job,
    lun,
    nas_server,
    nfs_share,
    pool,
    pool_unit,
    quota,
    session,
    storage_resource,
    system_info,
    tenant,
    user,
)
from dell_unisphere_mock_api.version import get_version

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(asctime)s - %(name)s - %(levelname)s - %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "DEBUG"},
        "uvicorn.error": {"level": "DEBUG"},
        "uvicorn.access": {"handlers": ["access"], "level": "DEBUG", "propagate": False},
    },
}

logging.config.dictConfig(logging_config)
# Store the original openapi function
original_openapi = FastAPI.openapi

# Module-level variable to store the OpenAPI schema
_openapi_schema = None


def custom_openapi():
    global _openapi_schema
    logger = logging.getLogger(__name__)

    if _openapi_schema:
        return _openapi_schema

    try:
        paths = {}
        tags = []
        components = {
            "securitySchemes": {
                "basicAuth": {
                    "type": "http",
                    "scheme": "basic",
                    "description": "Basic authentication with X-EMC-REST-CLIENT header",
                },
                "emcRestClient": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-EMC-REST-CLIENT",
                    "description": "Required header for all requests",
                },
                "emcCsrfToken": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "EMC-CSRF-TOKEN",
                    "description": (
                        "Required header for POST, PATCH and DELETE requests. "
                        "Obtained from any GET request response headers."
                    ),
                },
            },
            "schemas": {},
        }

        # Group routes by their tags
        logger.debug(f"Total routes: {len(app.routes)}")
        for route in app.routes:
            logger.debug(f"Processing route: {route}")
            logger.debug(f"Route type: {type(route)}")
            logger.debug(f"Route path: {route.path if hasattr(route, 'path') else 'No path'}")

            if not isinstance(route, routing.APIRoute):
                logger.debug(f"Skipping non-APIRoute: {route}")
                continue

            logger.debug(f"Processing API route: {route.path}")

            # Get route info
            path = route.path

            # Extract path parameters from the route
            path_params = []
            for param in route.dependant.path_params:
                path_params.append({"name": param.name, "in": "path", "required": True, "schema": {"type": "string"}})

            # Get route tags from the route
            route_tags = route.tags if route.tags else []
            logger.debug(f"Route tags: {route_tags}")

            # Add tags if they don't exist
            for tag in route_tags:
                if not any(t.get("name") == tag for t in tags):
                    tags.append({"name": tag})

            # Get request body schema if it exists
            request_body = None
            if route.body_field:
                model = route.body_field.type_
                model_name = model.__name__
                logger.debug(f"Request body model: {model_name}")
                if model_name not in components["schemas"]:
                    components["schemas"][model_name] = {"type": "object", "properties": {}}
                request_body = {
                    "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{model_name}"}}}
                }

            # Create operation object
            operation = {
                "tags": route_tags,
                "summary": route.summary if route.summary else "",
                "description": route.description if route.description else "",
                "operationId": route.operation_id if route.operation_id else route.name,
                "parameters": path_params,
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ApiResponse"}}},
                    }
                },
            }

            if request_body:
                operation["requestBody"] = request_body

            # Add security requirements for non-GET methods
            if route.methods and "GET" not in route.methods:
                operation["security"] = [
                    {"basicAuth": []},
                    {"emcRestClient": []},
                ]
                if any(method in route.methods for method in ["POST", "PATCH", "DELETE"]):
                    operation["security"].append({"emcCsrfToken": []})

            # Add path and method to paths
            if path not in paths:
                paths[path] = {}

            for method in route.methods:
                logger.debug(f"Adding method {method} for path {path}")
                paths[path][method.lower()] = operation

        # Add ApiResponse schema
        components["schemas"]["ApiResponse"] = {
            "type": "object",
            "properties": {"content": {"type": "array", "items": {"type": "object", "additionalProperties": True}}},
        }

        openapi_schema = {
            "openapi": "3.0.2",
            "info": {
                "title": "Dell Unisphere Mock API",
                "version": get_version(),
                "description": "Mock API for Dell Unisphere",
            },
            "paths": paths,
            "tags": tags,
            "components": components,
        }

        _openapi_schema = openapi_schema
        logger.debug("OpenAPI schema generation complete")
        logger.debug(f"Final paths: {paths}")
        return _openapi_schema
    except Exception as e:
        logger.exception(f"Error generating OpenAPI schema: {e}")
        raise


def create_application() -> FastAPI:
    """Create FastAPI application.

    Returns:
        FastAPI application.
    """
    application = FastAPI(
        title="Dell Unisphere Mock API",
        description="Mock API for Dell Unisphere",
        version=get_version(),
    )

    # Add middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(GZipMiddleware)
    application.add_middleware(ResponseHeadersMiddleware)
    application.add_middleware(ResponseWrapperMiddleware)
    application.add_middleware(CSRFMiddleware)

    # Set custom OpenAPI schema generator
    application.openapi = custom_openapi

    # Add debug endpoint for OpenAPI schema
    @application.get("/debug/openapi", include_in_schema=False)
    async def debug_openapi():
        """Debug endpoint to view the raw OpenAPI schema."""
        try:
            schema = custom_openapi()
            return JSONResponse(content=schema)
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": str(e), "traceback": traceback.format_exc()},
            )

    # Add custom exception handler for validation errors
    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors in a Unity API compatible way."""
        error_messages = []
        for error in exc.errors():
            field = error["loc"][-1] if error["loc"] else "unknown"
            error_messages.append(f"Invalid value for field '{field}': {error['msg']}")

        error_response = {
            "errorCode": 422,
            "httpStatusCode": 422,
            "messages": error_messages,
            "created": datetime.now(timezone.utc).isoformat(),
        }
        return JSONResponse(
            status_code=422,
            content=error_response,
        )

    # Configure routers
    application.include_router(session.router, tags=["Session"], prefix="/api")
    application.include_router(
        storage_resource.router, tags=["Storage Resource"], dependencies=[Depends(get_current_user)], prefix="/api"
    )
    application.include_router(
        filesystem.router, tags=["Filesystem"], dependencies=[Depends(get_current_user)], prefix="/api"
    )
    application.include_router(lun.router, tags=["LUN"], dependencies=[Depends(get_current_user)], prefix="/api")
    application.include_router(pool.router, tags=["Pool"], dependencies=[Depends(get_current_user)], prefix="/api")
    application.include_router(
        pool_unit.router, tags=["Pool Unit"], dependencies=[Depends(get_current_user)], prefix="/api"
    )
    application.include_router(
        disk_group.router, tags=["Disk Group"], dependencies=[Depends(get_current_user)], prefix="/api"
    )
    application.include_router(disk.router, tags=["Disk"], dependencies=[Depends(get_current_user)], prefix="/api")
    application.include_router(
        nas_server.router, tags=["NAS Server"], dependencies=[Depends(get_current_user)], prefix="/api"
    )
    application.include_router(job.router, tags=["Job"], dependencies=[Depends(get_current_user)], prefix="/api")

    application.include_router(user.router, tags=["User"], dependencies=[Depends(get_current_user)], prefix="/api")
    application.include_router(system_info.router, tags=["System Info"], prefix="/api")
    application.include_router(
        cifs_server.router, tags=["CIFS Server"], dependencies=[Depends(get_current_user)], prefix="/api"
    )
    application.include_router(
        nfs_share.router, tags=["NFS Share"], dependencies=[Depends(get_current_user)], prefix="/api"
    )
    application.include_router(
        nfs_share.router, tags=["NFS Share"], dependencies=[Depends(get_current_user)], prefix="/api"
    )
    application.include_router(
        quota.router, tags=["Quota Management"], dependencies=[Depends(get_current_user)], prefix="/api"
    )
    application.include_router(
        acl_user.router, tags=["ACL User"], dependencies=[Depends(get_current_user)], prefix="/api"
    )
    application.include_router(tenant.router, tags=["Tenant"], dependencies=[Depends(get_current_user)], prefix="/api")

    return application


app = create_application()


if __name__ == "__main__":
    import traceback

    import uvicorn

    # Get port from environment variable or use default
    port = int(os.getenv("PORT", "8000"))

    # Run server
    uvicorn.run(
        "dell_unisphere_mock_api.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )
