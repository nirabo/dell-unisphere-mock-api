from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from dell_unisphere_mock_api.core.auth import (
    Token,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    verify_password
)
from datetime import timedelta
from dell_unisphere_mock_api.routers import storage_resource, filesystem, nas_server, pool, lun

# Initialize FastAPI app
app = FastAPI(
    title="Mock Unity Unisphere API",
    description="""
A mock implementation of Dell Unity Unisphere Management REST API.

## Authentication

To use this API:

1. Get an access token by sending a POST request to `/token` with your credentials:
   - Username: `admin`
   - Password: `secret`

2. Use the token in the Authorization header:
   `Authorization: Bearer your_token_here`

In the Swagger UI:
1. Click the "Authorize" button (lock icon)
2. Enter your credentials
3. All subsequent requests will include the token

## Features

- Storage Resource Management
- Filesystem Management
- NAS Server Management
- Pool Management
- LUN Management
""",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock user database for testing
MOCK_USERS = {
    "admin": {
        "username": "admin",
        "role": "admin",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # "secret"
    }
}

# Configure security
security = HTTPBearer()

# Include routers
app.include_router(pool.router, prefix="/api", tags=["Pool"], dependencies=[Depends(get_current_user)])
app.include_router(lun.router, prefix="/api", tags=["LUN"], dependencies=[Depends(get_current_user)])
app.include_router(storage_resource.router, prefix="/api", tags=["Storage Resource"], dependencies=[Depends(get_current_user)])
app.include_router(filesystem.router, prefix="/api", tags=["Filesystem"], dependencies=[Depends(get_current_user)])
app.include_router(nas_server.router, prefix="/api", tags=["NAS Server"], dependencies=[Depends(get_current_user)])

@app.post("/api/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Get an access token for authentication.
    """
    user = MOCK_USERS.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/instances/system/0")
async def get_system_details(current_user: dict = Depends(get_current_user)):
    return {
        "content": {
            "id": "APM00123456789",
            "model": "Unity 380",
            "name": "Unity-380",
            "softwareVersion": "5.0.0.0.0.001",
            "apiVersion": "10.0",
            "earliestApiVersion": "1.0",
            "health": {
                "value": 5,
                "descr": "OK(5)",
                "descriptions": ["The system is operating normally."]
            }
        }
    }

@app.get("/api/instances/system")
async def get_system_info(current_user: dict = Depends(get_current_user)):
    return {
        "content": {
            "id": "0",
            "health": {
                "value": 5,
                "descr": "OK(5)",
                "descriptions": ["The system is operating normally."]
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
