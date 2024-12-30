from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from dell_unisphere_mock_api.controllers.job_controller import JobController
from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.schemas.job import Job, JobCreate

router = APIRouter(prefix="", tags=["Job"])
controller = JobController()


@router.post("/instances", response_model=Job, status_code=status.HTTP_202_ACCEPTED)
async def create_job(
    job_data: JobCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    """Create a new job."""
    job = await controller.create_job(job_data)
    background_tasks.add_task(simulate_job_processing, job.id)
    return job


@router.get("/instances/{job_id}", response_model=Job)
async def get_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get the status of a job."""
    return await controller.get_job(job_id)


@router.get("/instances", response_model=dict)
async def list_jobs(
    current_user: dict = Depends(get_current_user),
):
    """List all jobs."""
    jobs = await controller.list_jobs()
    return {"@base": "/api/types/job/instances", "entries": [{"content": job.model_dump()} for job in jobs]}


@router.delete("/instances/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a job."""
    await controller.delete_job(job_id)


async def simulate_job_processing(job_id: str):
    """Simulate job processing with progress updates."""
    import asyncio

    from dell_unisphere_mock_api.models.job import JobModel
    from dell_unisphere_mock_api.schemas.job import JobState

    job_model = JobModel()
    await asyncio.sleep(1)  # Simulate processing time
    await job_model.update_job_state(job_id, JobState.RUNNING)
    await asyncio.sleep(2)  # Simulate more processing time
    await job_model.update_job_state(job_id, JobState.COMPLETED)
