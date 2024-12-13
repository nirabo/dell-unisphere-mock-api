import pytest
from fastapi.testclient import TestClient
from dell_unisphere_mock_api.main import app

client = TestClient(app)


@pytest.fixture
def sample_pool_data():
    return {
        "name": "test_pool",
        "description": "Test pool for unit tests",
        "raidType": "RAID5",
        "sizeFree": 1000000000000,  # 1TB free
        "sizeTotal": 2000000000000,  # 2TB total
        "sizeUsed": 1000000000000,  # 1TB used
        "sizeSubscribed": 1500000000000,
        "poolType": "Performance",
        "alertThreshold": 80,
        "poolFastVP": True,
        "isFASTCacheEnabled": False,
        "isFASTVpScheduleEnabled": True,
        "isHarvestEnabled": True,
    }


@pytest.fixture
def sample_lun_data():
    return {
        "name": "test_lun",
        "description": "Test LUN for unit tests",
        "lunType": "GenericStorage",
        "size": 100000000000,  # 100GB
        "pool_id": None,  # Will be set in tests after pool creation
        "tieringPolicy": "Autotier",
        "defaultNode": 0,
        "isCompressionEnabled": False,
        "isThinEnabled": True,
        "isDataReductionEnabled": False,
        "hostAccess": []
    }


@pytest.fixture
def auth_headers():
    return {
        "Authorization": "Bearer some_token"
    }


def test_create_lun(sample_pool_data, sample_lun_data, auth_headers):
    # First create a pool
    pool_response = client.post("/api/types/pool/instances", json=sample_pool_data, headers=auth_headers)
    pool_id = pool_response.json()["id"]
    sample_lun_data["pool_id"] = pool_id

    # Then create a LUN
    response = client.post("/api/types/lun/instances", json=sample_lun_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_lun_data["name"]
    assert data["description"] == sample_lun_data["description"]
    assert data["pool_id"] == pool_id
    assert "id" in data
    assert "wwn" in data


def test_get_lun(sample_pool_data, sample_lun_data, auth_headers):
    # First create a pool
    pool_response = client.post("/api/types/pool/instances", json=sample_pool_data, headers=auth_headers)
    pool_id = pool_response.json()["id"]
    sample_lun_data["pool_id"] = pool_id

    # Then create a LUN
    create_response = client.post("/api/types/lun/instances", json=sample_lun_data, headers=auth_headers)
    lun_id = create_response.json()["id"]

    # Then get it by ID
    response = client.get(f"/api/instances/lun/{lun_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == lun_id
    assert data["name"] == sample_lun_data["name"]


def test_get_lun_by_name(sample_pool_data, sample_lun_data, auth_headers):
    # First create a pool
    pool_response = client.post("/api/types/pool/instances", json=sample_pool_data, headers=auth_headers)
    pool_id = pool_response.json()["id"]
    sample_lun_data["pool_id"] = pool_id

    # Then create a LUN
    client.post("/api/types/lun/instances", json=sample_lun_data, headers=auth_headers)

    # Then get it by name
    response = client.get(f"/api/instances/lun/name:{sample_lun_data['name']}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_lun_data["name"]


def test_list_luns(sample_pool_data, sample_lun_data, auth_headers):
    # First create a pool
    pool_response = client.post("/api/types/pool/instances", json=sample_pool_data, headers=auth_headers)
    pool_id = pool_response.json()["id"]
    sample_lun_data["pool_id"] = pool_id

    # Then create a LUN
    client.post("/api/types/lun/instances", json=sample_lun_data, headers=auth_headers)

    # Then list all LUNs
    response = client.get("/api/types/lun/instances", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(lun["name"] == sample_lun_data["name"] for lun in data)


def test_get_luns_by_pool(sample_pool_data, sample_lun_data, auth_headers):
    # First create a pool
    pool_response = client.post("/api/types/pool/instances", json=sample_pool_data, headers=auth_headers)
    pool_id = pool_response.json()["id"]
    sample_lun_data["pool_id"] = pool_id

    # Then create a LUN
    client.post("/api/types/lun/instances", json=sample_lun_data, headers=auth_headers)

    # Then get LUNs by pool
    response = client.get(f"/api/instances/pool/{pool_id}/luns", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert all(lun["pool_id"] == pool_id for lun in data)


def test_modify_lun(sample_pool_data, sample_lun_data, auth_headers):
    # First create a pool
    pool_response = client.post("/api/types/pool/instances", json=sample_pool_data, headers=auth_headers)
    pool_id = pool_response.json()["id"]
    sample_lun_data["pool_id"] = pool_id

    # Then create a LUN
    create_response = client.post("/api/types/lun/instances", json=sample_lun_data, headers=auth_headers)
    lun_id = create_response.json()["id"]

    # Then modify it
    update_data = {
        "name": "modified_test_lun",
        "description": "Modified test LUN",
        "size": 150000000000,  # Increase size to 150GB
        "isCompressionEnabled": True
    }
    response = client.post(f"/api/instances/lun/{lun_id}/action/modify", json=update_data, headers=auth_headers)
    assert response.status_code == 204

    # Verify the changes
    get_response = client.get(f"/api/instances/lun/{lun_id}", headers=auth_headers)
    data = get_response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["size"] == update_data["size"]
    assert data["isCompressionEnabled"] == update_data["isCompressionEnabled"]


def test_delete_lun(sample_pool_data, sample_lun_data, auth_headers):
    # First create a pool
    pool_response = client.post("/api/types/pool/instances", json=sample_pool_data, headers=auth_headers)
    pool_id = pool_response.json()["id"]
    sample_lun_data["pool_id"] = pool_id

    # Then create a LUN
    create_response = client.post("/api/types/lun/instances", json=sample_lun_data, headers=auth_headers)
    lun_id = create_response.json()["id"]

    # Then delete it
    response = client.delete(f"/api/instances/lun/{lun_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"/api/instances/lun/{lun_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_delete_lun_by_name(sample_pool_data, sample_lun_data, auth_headers):
    # First create a pool
    pool_response = client.post("/api/types/pool/instances", json=sample_pool_data, headers=auth_headers)
    pool_id = pool_response.json()["id"]
    sample_lun_data["pool_id"] = pool_id

    # Then create a LUN
    client.post("/api/types/lun/instances", json=sample_lun_data, headers=auth_headers)

    # Then delete it by name
    response = client.delete(f"/api/instances/lun/name:{sample_lun_data['name']}", headers=auth_headers)
    assert response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"/api/instances/lun/name:{sample_lun_data['name']}", headers=auth_headers)
    assert get_response.status_code == 404
