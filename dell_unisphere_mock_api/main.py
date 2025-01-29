"""Main FastAPI application module for Dell Unisphere Mock API."""

import logging
import logging.config
import os
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Request
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
        # Get the original schema by calling the original function bound to our app instance
        logger.debug("Getting original OpenAPI schema...")
        openapi_schema = original_openapi.__get__(app, FastAPI)()
        logger.debug(f"Original schema: {openapi_schema}")

        # Add security schemes
        logger.debug("Adding security schemes...")
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}
        openapi_schema["components"]["securitySchemes"] = {
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
        }

        # Apply security schemes to all paths
        logger.debug("Applying security schemes to paths...")
        for path, path_item in openapi_schema["paths"].items():
            logger.debug(f"Processing path: {path}")
            # Add basic security to all operations
            for method, operation in path_item.items():
                if method.upper() != "GET":  # Skip security for GET requests
                    logger.debug(f"Adding security to {method.upper()} {path}")
                    operation["security"] = [
                        {"basicAuth": []},
                        {"emcRestClient": []},
                    ]
                    # Add CSRF token requirement for POST, PATCH, DELETE methods
                    if method.upper() in ["POST", "PATCH", "DELETE"]:
                        operation["security"].append({"emcCsrfToken": []})

        _openapi_schema = openapi_schema
        logger.debug("OpenAPI schema generation complete")
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
