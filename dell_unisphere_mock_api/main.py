"""Main FastAPI application module for Dell Unisphere Mock API."""

from typing import Dict, List
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from dell_unisphere_mock_api.core.auth import get_current_user, verify_csrf_token
from dell_unisphere_mock_api.routers import (
    auth,
    disk,
    disk_group,
    filesystem,
    lun,
    nas_server,
    pool,
    pool_unit,
    storage_resource,
    user,
)
class JobTask(BaseModel):
    name: str
    object: str
    action: str
    parametersIn: Dict

class JobCreate(BaseModel):
    description: str
    tasks: List[JobTask]

class JobState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class Job(BaseModel):
    id: str
    state: JobState
    description: str
    tasks: List[JobTask]
    progressPct: Optional[float] = None
    errorMessage: Optional[str] = None

# In-memory store for jobs
jobs: Dict[str, Job] = {}

app = FastAPI(
    title="Mock Unity Unisphere API",
    description="A mock implementation of Dell Unity Unisphere Management REST API.",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},  # Keep authentication between page reloads
)

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


@app.get("/api/instances/system/0", response_model=Dict)
async def get_system_details(current_user: Dict = Depends(get_current_user)) -> Dict:
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


@app.get("/api/types/system/0/basicSystemInfo", response_model=Dict)
async def get_system_info() -> Dict:
    """Basic system information. This endpoint is accessible without authentication."""
    return {
        "content": {
            "name": "Unity-380",
            "model": "Unity 380",
            "serialNumber": "APM00123456789",
            "softwareVersion": "5.0.0.0.0.001",
        }
    }


@app.post("/api/types/job/instances", response_model=Job, status_code=202)
async def create_job(job_data: JobCreate, current_user: Dict = Depends(get_current_user)):
    """Create a new job for aggregated operations"""
    job_id = str(uuid4())
    job = Job(id=job_id, state=JobState.PENDING, description=job_data.description, tasks=job_data.tasks)
    jobs[job_id] = job

    # Here you would implement the actual job processing logic
    # For now, we'll just mark it as completed
    job.state = JobState.COMPLETED
    job.progressPct = 100.0

    return job


@app.get("/api/instances/job/{job_id}", response_model=Job)
async def get_job_status(job_id: str, current_user: Dict = Depends(get_current_user)):
    """Get the status of a job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
