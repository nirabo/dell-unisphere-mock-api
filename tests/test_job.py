import pytest
from fastapi.testclient import TestClient
from dell_unisphere_mock_api.main import app
from dell_unisphere_mock_api.schemas.job import JobCreate, JobTask

client = TestClient(app)


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


def test_create_job(sample_job_data):
    response = client.post("/api/types/job/instances", json=sample_job_data.dict())
    assert response.status_code == 202
    assert "id" in response.json()


def test_get_job(sample_job_data):
    create_response = client.post("/api/types/job/instances", json=sample_job_data.dict())
    job_id = create_response.json()["id"]
    response = client.get(f"/api/types/job/instances/{job_id}")
    assert response.status_code == 200
    assert response.json()["id"] == job_id


def test_list_jobs(sample_job_data):
    client.post("/api/types/job/instances", json=sample_job_data.dict())
    response = client.get("/api/types/job/instances")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_delete_job(sample_job_data):
    create_response = client.post("/api/types/job/instances", json=sample_job_data.dict())
    job_id = create_response.json()["id"]
    response = client.delete(f"/api/types/job/instances/{job_id}")
    assert response.status_code == 204
    get_response = client.get(f"/api/types/job/instances/{job_id}")
    assert get_response.status_code == 404
