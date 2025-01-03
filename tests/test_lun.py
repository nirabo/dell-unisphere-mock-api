import pytest

from dell_unisphere_mock_api.schemas.lun import HostAccessEnum, LUNCreate, LUNTypeEnum, LUNUpdate, TieringPolicyEnum
from dell_unisphere_mock_api.schemas.pool import RaidTypeEnum


@pytest.fixture
def sample_pool_data():
    return {
        "name": "test_pool",
        "description": "Test pool for unit tests",
        "raidType": RaidTypeEnum.RAID5,
        "sizeTotal": 2000000000000,  # 2TB total
        "alertThreshold": 80,
        "isHarvestEnabled": True,
        "poolSpaceHarvestHighThreshold": 85.0,
        "poolSpaceHarvestLowThreshold": 75.0,
        "snapSpaceHarvestHighThreshold": None,
        "snapSpaceHarvestLowThreshold": None,
        "isSnapHarvestEnabled": False,
        "isFASTCacheEnabled": False,
        "isFASTVpScheduleEnabled": False,
        "type": "dynamic",
    }


@pytest.fixture
def sample_lun_data():
    return {
        "name": "test_lun",
        "description": "Test LUN for unit tests",
        "pool_id": None,  # Will be set in tests after pool creation
        "size": 100000000000,  # 100GB
        "lunType": LUNTypeEnum.GenericStorage,
        "tieringPolicy": TieringPolicyEnum.Autotier,
        "isCompressionEnabled": False,
        "isDataReductionEnabled": False,
        "isThinEnabled": True,
        "hostAccess": [],
        "defaultNode": 0,
        "currentNode": None,
        "sizeAllocated": 0,
    }


def test_create_lun(test_client, sample_pool_data, sample_lun_data, auth_headers):
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    print("Test: Creating pool with data:", sample_pool_data)
    pool_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    print("Test: Pool creation response:", pool_response.json())  # Print response for debugging
    assert pool_response.status_code == 201
    pool_id = pool_response.json()["id"]
    print("Test: Created pool with ID:", pool_id)

    # Create LUN data with pool_id
    lun_data = dict(sample_lun_data)
    lun_data["pool_id"] = str(pool_id)  # Ensure pool_id is a string
    print("Test: Creating LUN with data:", lun_data)

    # Create LUN using LUNCreate model
    lun_create = LUNCreate(**lun_data)
    print("Test: Created LUNCreate model:", lun_create)

    # Then create a LUN
    response = test_client.post("/api/types/lun/instances", json=lun_create.model_dump(), headers=headers)
    print("Test: LUN creation response:", response.json() if response.status_code != 404 else response.text)
    assert response.status_code == 201
    data = response.json()
    print("Test: Created LUN:", data)
    assert data["name"] == lun_data["name"]
    assert data["pool_id"] == pool_id


def test_get_lun(test_client, sample_pool_data, sample_lun_data, auth_headers):
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    pool_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert pool_response.status_code == 201
    pool_id = pool_response.json()["id"]

    # Create LUN data with pool_id
    lun_data = dict(sample_lun_data)
    lun_data["pool_id"] = str(pool_id)
    lun_create = LUNCreate(**lun_data)

    # Create a LUN
    create_response = test_client.post("/api/types/lun/instances", json=lun_create.model_dump(), headers=headers)
    assert create_response.status_code == 201
    lun_id = create_response.json()["id"]

    # Get the LUN
    response = test_client.get(f"/api/instances/lun/{lun_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == lun_id
    assert data["name"] == lun_data["name"]
    assert data["pool_id"] == pool_id


def test_get_lun_by_name(test_client, sample_pool_data, sample_lun_data, auth_headers):
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    pool_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert pool_response.status_code == 201
    pool_id = pool_response.json()["id"]

    # Create LUN data with pool_id
    lun_data = dict(sample_lun_data)
    lun_data["pool_id"] = str(pool_id)
    lun_create = LUNCreate(**lun_data)

    # Create a LUN
    create_response = test_client.post("/api/types/lun/instances", json=lun_create.model_dump(), headers=headers)
    assert create_response.status_code == 201

    # Get the LUN by name
    response = test_client.get(f"/api/instances/lun/name:{lun_data['name']}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == lun_data["name"]
    assert data["pool_id"] == pool_id


def test_list_luns(test_client, sample_pool_data, sample_lun_data, auth_headers):
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    pool_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert pool_response.status_code == 201
    pool_id = pool_response.json()["id"]

    # Create LUN data with pool_id
    lun_data = dict(sample_lun_data)
    lun_data["pool_id"] = str(pool_id)
    lun_create = LUNCreate(**lun_data)

    # Create a LUN
    create_response = test_client.post("/api/types/lun/instances", json=lun_create.model_dump(), headers=headers)
    assert create_response.status_code == 201

    # List LUNs
    response = test_client.get("/api/types/lun/instances", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(lun["name"] == lun_data["name"] for lun in data)


def test_get_luns_by_pool(test_client, sample_pool_data, sample_lun_data, auth_headers):
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    pool_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert pool_response.status_code == 201
    pool_id = pool_response.json()["id"]

    # Create LUN data with pool_id
    lun_data = dict(sample_lun_data)
    lun_data["pool_id"] = str(pool_id)
    lun_create = LUNCreate(**lun_data)

    # Create a LUN
    create_response = test_client.post("/api/types/lun/instances", json=lun_create.model_dump(), headers=headers)
    assert create_response.status_code == 201

    # Get LUNs by pool
    response = test_client.get(f"/api/instances/pool/{pool_id}/luns", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(lun["pool_id"] == pool_id for lun in data)


def test_modify_lun(test_client, sample_pool_data, sample_lun_data, auth_headers):
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    pool_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert pool_response.status_code == 201
    pool_id = pool_response.json()["id"]

    # Create LUN data with pool_id
    lun_data = dict(sample_lun_data)
    lun_data["pool_id"] = str(pool_id)
    lun_create = LUNCreate(**lun_data)

    # Create a LUN
    create_response = test_client.post("/api/types/lun/instances", json=lun_create.model_dump(), headers=headers)
    assert create_response.status_code == 201
    lun_id = create_response.json()["id"]

    # Modify the LUN
    update_data = {
        "name": "modified_test_lun",
        "description": "Modified test LUN",
        "tieringPolicy": TieringPolicyEnum.Highest,
    }
    response = test_client.patch(f"/api/instances/lun/{lun_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["tieringPolicy"] == update_data["tieringPolicy"]


def test_delete_lun(test_client, sample_pool_data, sample_lun_data, auth_headers):
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    pool_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert pool_response.status_code == 201
    pool_id = pool_response.json()["id"]

    # Create LUN data with pool_id
    lun_data = dict(sample_lun_data)
    lun_data["pool_id"] = str(pool_id)
    lun_create = LUNCreate(**lun_data)

    # Create a LUN
    create_response = test_client.post("/api/types/lun/instances", json=lun_create.model_dump(), headers=headers)
    assert create_response.status_code == 201
    lun_id = create_response.json()["id"]

    # Delete the LUN
    response = test_client.delete(f"/api/instances/lun/{lun_id}", headers=headers)
    assert response.status_code == 204

    # Verify LUN is deleted
    get_response = test_client.get(f"/api/instances/lun/{lun_id}", headers=headers)
    assert get_response.status_code == 404


def test_delete_lun_by_name(test_client, sample_pool_data, sample_lun_data, auth_headers):
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    pool_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert pool_response.status_code == 201
    pool_id = pool_response.json()["id"]

    # Create LUN data with pool_id
    lun_data = dict(sample_lun_data)
    lun_data["pool_id"] = str(pool_id)
    lun_create = LUNCreate(**lun_data)

    # Create a LUN
    create_response = test_client.post("/api/types/lun/instances", json=lun_create.model_dump(), headers=headers)
    assert create_response.status_code == 201

    # Delete the LUN by name
    response = test_client.delete(f"/api/instances/lun/name:{lun_data['name']}", headers=headers)
    assert response.status_code == 204

    # Verify LUN is deleted
    get_response = test_client.get(f"/api/instances/lun/name:{lun_data['name']}", headers=headers)
    assert get_response.status_code == 404
