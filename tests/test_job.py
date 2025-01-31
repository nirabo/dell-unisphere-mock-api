import base64

import httpx
import pytest
import pytest_asyncio

from dell_unisphere_mock_api.main import app
from dell_unisphere_mock_api.schemas.job import JobCreate, JobTask


@pytest_asyncio.fixture
async def async_test_client():
    """Fixture to provide an async test client."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(base_url="http://testserver", transport=transport) as client:
        yield client


@pytest.fixture
def sample_job_data():
    return JobCreate(
        description="Test job",
        tasks=[
            JobTask(
                name="CreatePool",
                object="pool",
                action="create",
                parametersIn={"name": "test_pool", "type": 1, "sizeTotal": 1000000000},
            )
        ],
    )


@pytest.mark.asyncio
async def test_create_job(async_test_client, sample_job_data, auth_headers):
    headers_with_csrf, _ = auth_headers
    response = await async_test_client.post(
        "/api/types/job/instances",
        json=sample_job_data.model_dump(),
        headers=headers_with_csrf,
    )
    assert response.status_code == 202
    assert "entries" in response.json()
    assert "id" in response.json()["entries"][0]["content"]


@pytest.mark.asyncio
async def test_get_job(async_test_client, sample_job_data, auth_headers):
    headers_with_csrf, headers_without_csrf = auth_headers
    create_response = await async_test_client.post(
        "/api/types/job/instances",
        json=sample_job_data.model_dump(),
        headers=headers_with_csrf,
    )
    job_id = create_response.json()["entries"][0]["content"]["id"]

    response = await async_test_client.get(
        f"/api/types/job/instances/{job_id}",
        headers=headers_without_csrf,
    )
    assert response.status_code == 200
    assert response.json()["entries"][0]["content"]["id"] == job_id


@pytest.mark.asyncio
async def test_list_jobs(async_test_client, sample_job_data, auth_headers):
    headers_with_csrf, headers_without_csrf = auth_headers
    # Create a job first
    create_response = await async_test_client.post(
        "/api/types/job/instances",
        json=sample_job_data.model_dump(),
        headers=headers_with_csrf,
    )
    assert create_response.status_code == 202
    job_id = create_response.json()["entries"][0]["content"]["id"]

    # List jobs
    response = await async_test_client.get(
        "/api/types/job/instances",
        headers=headers_without_csrf,
    )
    assert response.status_code == 200
    assert "@base" in response.json()
    assert "entries" in response.json()
    assert len(response.json()["entries"]) >= 1
    assert any(entry["content"]["id"] == job_id for entry in response.json()["entries"])


@pytest.mark.asyncio
async def test_delete_job(async_test_client, sample_job_data, auth_headers):
    headers_with_csrf, headers_without_csrf = auth_headers
    create_response = await async_test_client.post(
        "/api/types/job/instances",
        json=sample_job_data.model_dump(),
        headers=headers_with_csrf,
    )
    assert create_response.status_code == 202
    job_id = create_response.json()["entries"][0]["content"]["id"]

    # Get the job
    get_response = await async_test_client.get(
        f"/api/types/job/instances/{job_id}",
        headers=headers_without_csrf,
    )
    assert get_response.status_code == 200
    assert get_response.json()["entries"][0]["content"]["id"] == job_id

    # Delete the job
    delete_response = await async_test_client.delete(
        f"/api/types/job/instances/{job_id}",
        headers=headers_with_csrf,
    )
    assert delete_response.status_code == 204

    # Verify job is deleted
    get_response = await async_test_client.get(
        f"/api/types/job/instances/{job_id}",
        headers=headers_without_csrf,
    )
    assert get_response.status_code == 404
