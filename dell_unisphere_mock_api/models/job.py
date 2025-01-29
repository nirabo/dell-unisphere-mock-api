from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from dell_unisphere_mock_api.schemas.job import Job, JobCreate, JobState


class JobModel:
    def __init__(self):
        """Initialize the job model."""
        self._jobs: Dict[str, Job] = {}

    async def create_job(self, job_data: JobCreate) -> Job:
        """Create a new job."""
        job_id = str(uuid4())
        now = datetime.now(timezone.utc)
        job = Job(
            id=job_id,
            description=job_data.description,
            state=JobState.QUEUED,
            tasks=job_data.tasks,
            created=now,
            modified=now,
            progressPct=0,
        )
        self._jobs[job_id] = job
        return job

    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        return self._jobs.get(job_id)

    async def update_job_state(self, job_id: str, state: JobState) -> Optional[Job]:
        """Update the state of a job.

        Args:
            job_id: The ID of the job to update
            state: The new state to set

        Returns:
            Optional[Job]: The updated job if found, None otherwise
        """
        if job_id not in self._jobs:
            return None

        job = self._jobs[job_id]
        job.state = state
        job.modified = datetime.now(timezone.utc)

        # Update progress based on state
        if state == JobState.RUNNING:
            job.progressPct = 50
        elif state == JobState.COMPLETED:
            job.progressPct = 100

        return job

    async def list_jobs(self) -> List[Job]:
        """List all jobs."""
        return list(self._jobs.values())

    async def delete_job(self, job_id: str) -> bool:
        """Delete a job."""
        if job_id in self._jobs:
            del self._jobs[job_id]
            return True
        return False
