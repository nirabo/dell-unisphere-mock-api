import base64
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from dell_unisphere_mock_api.main import app
from dell_unisphere_mock_api.schemas.job import JobCreate, JobTask

client = TestClient(app)


@pytest.fixture
def auth_headers():
    credentials = base64.b64encode(b"admin:Password123!").decode("utf-8")
    auth_header = f"Basic {credentials}"

    # Login to get CSRF token
    response = client.post(
        "/api/auth",
        headers={"X-EMC-REST-CLIENT": "true", "Authorization": auth_header},
    )
    csrf_token = response.headers.get("EMC-CSRF-TOKEN")
    cookies = response.cookies

    return {
        "X-EMC-REST-CLIENT": "true",
        "Authorization": auth_header,
        "EMC-CSRF-TOKEN": csrf_token,
    }, cookies


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


def test_create_job(sample_job_data, auth_headers):
    headers, cookies = auth_headers
    response = client.post(
        "/api/types/job/instances",
        json=sample_job_data.model_dump(),
        headers=headers,
        cookies=cookies,
    )
    assert response.status_code == 202
    assert "entries" in response.json()
    assert "id" in response.json()["entries"][0]["content"]


def test_get_job(sample_job_data, auth_headers):
    headers, cookies = auth_headers
    create_response = client.post(
        "/api/types/job/instances",
        json=sample_job_data.model_dump(),
        headers=headers,
        cookies=cookies,
    )
    job_id = create_response.json()["entries"][0]["content"]["id"]

    response = client.get(
        f"/api/types/job/instances/{job_id}",
        headers=headers,
        cookies=cookies,
    )
    assert response.status_code == 200
    assert response.json()["entries"][0]["content"]["id"] == job_id


def test_list_jobs(sample_job_data, auth_headers):
    headers, cookies = auth_headers
    # Create a job first
    create_response = client.post(
        "/api/types/job/instances",
        json=sample_job_data.model_dump(),
        headers=headers,
        cookies=cookies,
    )
    assert create_response.status_code == 202
    job_id = create_response.json()["entries"][0]["content"]["id"]

    # List jobs
    response = client.get("/api/types/job/instances", headers=headers, cookies=cookies)
    assert response.status_code == 200
    assert "@base" in response.json()
    assert "entries" in response.json()
    assert len(response.json()["entries"]) >= 1
    assert any(entry["content"]["id"] == job_id for entry in response.json()["entries"])


def test_delete_job(sample_job_data, auth_headers):
    headers, cookies = auth_headers
    create_response = client.post(
        "/api/types/job/instances",
        json=sample_job_data.model_dump(),
        headers=headers,
        cookies=cookies,
    )
    assert create_response.status_code == 202
    job_id = create_response.json()["entries"][0]["content"]["id"]

    # Get the job
    get_response = client.get(f"/api/types/job/instances/{job_id}", headers=headers, cookies=cookies)
    assert get_response.status_code == 200
    assert get_response.json()["entries"][0]["content"]["id"] == job_id

    # Delete the job
    delete_response = client.delete(f"/api/types/job/instances/{job_id}", headers=headers, cookies=cookies)
    assert delete_response.status_code == 204

    # Verify job is deleted
    get_response = client.get(f"/api/types/job/instances/{job_id}", headers=headers, cookies=cookies)
    assert get_response.status_code == 404
