from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from dell_unisphere_mock_api.schemas.job import Job, JobCreate, JobState


class JobModel:
    # Store jobs at class level to share between instances
    _jobs: Dict[str, Job] = {}

    def __init__(self):
        pass

    async def create_job(self, job_data: JobCreate) -> Job:
        """Create a new job."""
        job_id = f"job_{str(uuid4())}"
        job = Job(
            id=job_id,
            state=JobState.PENDING,
            description=job_data.description,
            tasks=job_data.tasks,
        )
        self._jobs[job_id] = job
        return job

    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        return self._jobs.get(job_id)

    async def update_job_state(self, job_id: str, state: JobState) -> Optional[Job]:
        """Update the state of a job."""
        job = self._jobs.get(job_id)
        if job:
            job.state = state
            return job
        return None

    async def list_jobs(self) -> List[Job]:
        """List all jobs."""
        return list(self._jobs.values())

    async def delete_job(self, job_id: str) -> bool:
        """Delete a job."""
        if job_id in self._jobs:
            del self._jobs[job_id]
            return True
        return False
