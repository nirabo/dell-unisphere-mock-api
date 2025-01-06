"""Main FastAPI application module for Dell Unisphere Mock API."""

import logging
import logging.config

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware

from dell_unisphere_mock_api.core.auth import get_current_user, verify_csrf_token
from dell_unisphere_mock_api.routers import (
    auth,
    disk,
    disk_group,
    filesystem,
    job,
    lun,
    nas_server,
    pool,
    pool_unit,
    storage_resource,
    system_info,
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
            "fmt": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
            "formatter": "default",
        },
        "access": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "access",
        },
    },
    "loggers": {
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["access"],
            "propagate": False,
        },
    },
}

logging.config.dictConfig(logging_config)
# Store the original openapi function
original_openapi = FastAPI.openapi

# Module-level variable to store the OpenAPI schema
_openapi_schema = None


def custom_openapi():
    global _openapi_schema

    if _openapi_schema:
        return _openapi_schema

    # Get the original schema
    openapi_schema = original_openapi(app)

    # Add security schemes
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
            "description": "Required header for POST, PATCH and DELETE requests. Obtained from /api/auth endpoint.",
        },
    }

    # Apply security schemes to all operations
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            if "security" not in operation:
                operation["security"] = [
                    {"basicAuth": []},
                    {"emcRestClient": []},
                ]
            # Add CSRF token requirement for POST, PATCH, DELETE methods
            if operation.get("method", "").upper() in ["POST", "PATCH", "DELETE"]:
                operation["security"].append({"emcCsrfToken": []})

    _openapi_schema = openapi_schema
    return _openapi_schema


app = FastAPI(
    title="Mock Unity Unisphere API",
    description="A mock implementation of Dell Unity Unisphere Management REST API.",
    version=get_version(),
    swagger_ui_parameters={
        "persistAuthorization": True,
        "requestInterceptor": """(req) => {
            console.log('Starting request interceptor');

            // Add X-EMC-REST-CLIENT header
            req.headers['X-EMC-REST-CLIENT'] = 'true';

            // Add Authorization header if credentials are provided
            const auth = localStorage.getItem('auth');
            if (auth) {
                const {username, password} = JSON.parse(auth);
                req.headers['Authorization'] = 'Basic ' + btoa(username + ':' + password);
            }

            // For POST, PATCH, DELETE requests, add CSRF token
            if (['POST', 'PATCH', 'DELETE'].includes(req.method.toUpperCase()) && !req.url.endsWith('/api/auth')) {
                // First try to get token from localStorage
                const storedToken = localStorage.getItem('emc_csrf_token');
                if (storedToken) {
                    req.headers['EMC-CSRF-TOKEN'] = storedToken;
                    console.log('Added stored CSRF token:', storedToken);
                } else {
                    console.log('No CSRF token found in storage');
                }
            }

            console.log('Final request headers:', req.headers);
            return req;
        }""",
        "responseInterceptor": """(response) => {
            console.log('Response interceptor:', response.url);

            // Get CSRF token from response headers
            const token = response.headers.get('EMC-CSRF-TOKEN');
            if (token) {
                console.log('Got CSRF token from response:', token);
                localStorage.setItem('emc_csrf_token', token);
            }

            return response;
        }""",
    },
)

app.openapi = custom_openapi

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware to verify CSRF token for POST, PATCH and DELETE requests
@app.middleware("http")
async def csrf_middleware(request: Request, call_next) -> Response:
    """Verify CSRF token for POST, PATCH and DELETE requests."""
    try:
        verify_csrf_token(request, request.method)
    except HTTPException as e:
        if e.status_code == status.HTTP_403_FORBIDDEN:
            return Response(content=str(e.detail), status_code=e.status_code, headers=e.headers)
    response = await call_next(request)
    return response


# Configure routers
app.include_router(auth.router, prefix="/api", tags=["Auth"])
app.include_router(
    job.router,
    prefix="/api/types/job",
    tags=["Job"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    storage_resource.router,
    prefix="/api",
    tags=["Storage Resource"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    filesystem.router,
    prefix="/api",
    tags=["Filesystem"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    nas_server.router,
    prefix="/api",
    tags=["NAS Server"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(pool.router, prefix="/api", tags=["Pool"], dependencies=[Depends(get_current_user)])
app.include_router(lun.router, prefix="/api", tags=["LUN"], dependencies=[Depends(get_current_user)])
app.include_router(
    pool_unit.router,
    prefix="/api",
    tags=["Pool Unit"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    disk_group.router,
    prefix="/api",
    tags=["Disk Group"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(disk.router, prefix="/api", tags=["Disk"], dependencies=[Depends(get_current_user)])
app.include_router(user.router, prefix="/api", tags=["User"], dependencies=[Depends(get_current_user)])
app.include_router(system_info.router, prefix="/api", tags=["System Information"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
