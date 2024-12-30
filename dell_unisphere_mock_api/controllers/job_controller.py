from typing import List

from fastapi import HTTPException, status

from dell_unisphere_mock_api.models.job import JobModel
from dell_unisphere_mock_api.schemas.job import Job, JobCreate


class JobController:
    def __init__(self):
        self.model = JobModel()

    async def create_job(self, job_data: JobCreate) -> Job:
        """Create a new job."""
        return await self.model.create_job(job_data)

    async def get_job(self, job_id: str) -> Job:
        """Get a job by ID."""
        job = await self.model.get_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )
        return job

    async def list_jobs(self) -> List[Job]:
        """List all jobs."""
        return await self.model.list_jobs()

    async def delete_job(self, job_id: str) -> None:
        """Delete a job."""
        if not await self.model.delete_job(job_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )
