from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status

from dell_unisphere_mock_api.controllers.job_controller import JobController
from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.response import UnityResponseFormatter
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.schemas.job import Job, JobCreate, JobState

router = APIRouter(prefix="/types/job", tags=["Job"])
controller = JobController()


@router.post("/instances", response_model=ApiResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_job(
    job_data: JobCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """Create a new job."""
    job = await controller.create_job(job_data)
    background_tasks.add_task(simulate_job_processing, job.id)
    formatter = UnityResponseFormatter(request)
    return formatter.format_collection(
        [job], entry_links={0: [{"rel": "self", "href": f"/api/types/job/instances/{job.id}"}]}
    )


@router.get("/instances/{job_id}", response_model=ApiResponse)
async def get_job(
    job_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """Get the status of a job."""
    job = await controller.get_job(job_id)
    formatter = UnityResponseFormatter(request)
    return formatter.format_collection(
        [job], entry_links={0: [{"rel": "self", "href": f"/api/types/job/instances/{job.id}"}]}
    )


@router.get("/instances", response_model=ApiResponse)
async def list_jobs(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """List all jobs."""
    jobs = await controller.list_jobs()
    formatter = UnityResponseFormatter(request)
    return formatter.format_collection(
        jobs,
        entry_links={i: [{"rel": "self", "href": f"/api/types/job/instances/{job.id}"}] for i, job in enumerate(jobs)},
    )


@router.delete("/instances/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a job."""
    await controller.delete_job(job_id)


async def simulate_job_processing(job_id: str):
    """Simulate job processing with progress updates."""
    await controller.update_job_state(job_id, JobState.RUNNING)
    # Simulate some work
    await controller.update_job_state(job_id, JobState.COMPLETED)
