"""Main FastAPI application module for Dell Unisphere Mock API."""

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
    user,
)

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

    # Add X-EMC-REST-CLIENT header to security scheme
    openapi_schema["components"]["securitySchemes"]["basicAuth"] = {
        "type": "http",
        "scheme": "basic",
        "description": "Basic authentication with X-EMC-REST-CLIENT header",
        "x-emc-rest-client": {"type": "apiKey", "in": "header", "name": "X-EMC-REST-CLIENT", "value": "true"},
    }

    # Apply the security scheme to all operations
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            if "security" not in operation:
                operation["security"] = [{"basicAuth": []}]

    _openapi_schema = openapi_schema
    return _openapi_schema


app = FastAPI(
    title="Mock Unity Unisphere API",
    description="A mock implementation of Dell Unity Unisphere Management REST API.",
    version="1.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True,  # Keep authentication between page reloads
        "requestInterceptor": """(req) => {
            // Add X-EMC-REST-CLIENT header to all requests
            req.headers['X-EMC-REST-CLIENT'] = 'true';

            // Add Authorization header if credentials are provided
            const auth = localStorage.getItem('auth');
            if (auth) {
                const {username, password} = JSON.parse(auth);
                req.headers['Authorization'] = 'Basic ' + btoa(username + ':' + password);
            }
            return req;
        }""",
        "initOAuth": {
            "clientId": "unisphere-client",
            "appName": "Unisphere Mock API",
            "usePkceWithAuthorizationCodeGrant": True,
        },
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


@app.get("/api/instances/system/0", response_model=dict)
async def get_system_details(current_user: dict = Depends(get_current_user)) -> dict:
    """Get system details."""
    return {
        "content": {
            "id": "APM00123456789",
            "model": "Unity 380",
            "name": "Unity-380",
            "softwareVersion": "5.0.0.0.0.001",
            "apiVersion": "10.0",
            "earliestApiVersion": "5.0",
            "platform": "Platform2",
            "mac": "00:60:16:5C:B7:E0",
        }
    }


@app.get("/api/types/system/0/basicSystemInfo", response_model=dict)
async def get_system_info() -> dict:
    """Basic system information. This endpoint is accessible without authentication."""
    return {
        "content": {
            "name": "Unity-380",
            "model": "Unity 380",
            "serialNumber": "APM00123456789",
            "softwareVersion": "5.0.0.0.0.001",
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
