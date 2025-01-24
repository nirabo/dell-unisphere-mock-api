"""Tests for Quota functionality."""

import pytest
from fastapi.testclient import TestClient

from dell_unisphere_mock_api.controllers.quota_controller import QuotaController
from dell_unisphere_mock_api.models.quota import (
    QuotaConfig,
    QuotaConfigCreate,
    QuotaConfigUpdate,
    TreeQuota,
    TreeQuotaCreate,
    TreeQuotaUpdate,
    UserQuota,
    UserQuotaCreate,
    UserQuotaUpdate,
)


# Quota Config Tests
def test_quota_config_controller_create():
    """Test creating a quota configuration."""
    controller = QuotaController()
    config_data = QuotaConfigCreate(
        filesystem_id="fs_1",
        is_user_quotas_enabled=True,
        is_tree_quotas_enabled=True,
        default_hard_limit=1073741824,  # 1GB
        default_soft_limit=858993459,  # 800MB
    )

    config = controller.create_quota_config(config_data)
    assert config.filesystem_id == "fs_1"
    assert config.is_user_quotas_enabled is True
    assert config.is_tree_quotas_enabled is True
    assert config.default_hard_limit == 1073741824
    assert config.state == "READY"


def test_quota_config_controller_update():
    """Test updating a quota configuration."""
    controller = QuotaController()
    config_data = QuotaConfigCreate(filesystem_id="fs_1", is_user_quotas_enabled=True)

    created_config = controller.create_quota_config(config_data)
    update_data = QuotaConfigUpdate(is_tree_quotas_enabled=True, default_hard_limit=2147483648)  # 2GB

    updated_config = controller.update_quota_config(created_config.id, update_data)
    assert updated_config is not None
    assert updated_config.is_tree_quotas_enabled is True
    assert updated_config.default_hard_limit == 2147483648


# Tree Quota Tests
def test_tree_quota_controller_create():
    """Test creating a tree quota."""
    controller = QuotaController()
    quota_data = TreeQuotaCreate(
        filesystem_id="fs_1", path="/shared/projects", hard_limit=5368709120, soft_limit=4294967296  # 5GB  # 4GB
    )

    quota = controller.create_tree_quota(quota_data)
    assert quota.filesystem_id == "fs_1"
    assert quota.path == "/shared/projects"
    assert quota.hard_limit == 5368709120
    assert quota.state == "OK"


def test_tree_quota_controller_update():
    """Test updating a tree quota."""
    controller = QuotaController()
    quota_data = TreeQuotaCreate(filesystem_id="fs_1", path="/shared/projects", hard_limit=5368709120)

    created_quota = controller.create_tree_quota(quota_data)
    update_data = TreeQuotaUpdate(hard_limit=10737418240, description="Updated quota")  # 10GB

    updated_quota = controller.update_tree_quota(created_quota.id, update_data)
    assert updated_quota is not None
    assert updated_quota.hard_limit == 10737418240
    assert updated_quota.description == "Updated quota"


# User Quota Tests
def test_user_quota_controller_create():
    """Test creating a user quota."""
    controller = QuotaController()
    quota_data = UserQuotaCreate(
        filesystem_id="fs_1", uid=1000, hard_limit=2147483648, soft_limit=1610612736  # 2GB  # 1.5GB
    )

    quota = controller.create_user_quota(quota_data)
    assert quota.filesystem_id == "fs_1"
    assert quota.uid == 1000
    assert quota.hard_limit == 2147483648
    assert quota.state == "OK"


def test_user_quota_controller_update():
    """Test updating a user quota."""
    controller = QuotaController()
    quota_data = UserQuotaCreate(filesystem_id="fs_1", uid=1000, hard_limit=2147483648)

    created_quota = controller.create_user_quota(quota_data)
    update_data = UserQuotaUpdate(hard_limit=4294967296)  # 4GB

    updated_quota = controller.update_user_quota(created_quota.id, update_data)
    assert updated_quota is not None
    assert updated_quota.hard_limit == 4294967296


# API Endpoint Tests
def test_quota_api_endpoints(test_client: TestClient, auth_headers):
    """Test quota API endpoints."""
    headers, _ = auth_headers

    # Test Quota Config endpoints
    response = test_client.post(
        "/api/types/quotaConfig/instances",
        json={
            "@base": "storageObject",
            "filesystem_id": "fs_1",
            "is_user_quotas_enabled": True,
            "is_tree_quotas_enabled": True,
            "default_hard_limit": 1073741824,
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    config_id = data["entries"][0]["content"]["id"]

    response = test_client.patch(
        f"/api/types/quotaConfig/instances/{config_id}", json={"default_hard_limit": 2147483648}, headers=headers
    )
    assert response.status_code == 200

    # Test Tree Quota endpoints
    response = test_client.post(
        "/api/types/treeQuota/instances",
        json={"@base": "storageObject", "filesystem_id": "fs_1", "path": "/shared/projects", "hard_limit": 5368709120},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    tree_quota_id = data["entries"][0]["content"]["id"]

    response = test_client.get(f"/api/types/treeQuota/instances/{tree_quota_id}", headers=headers)
    assert response.status_code == 200

    # Test User Quota endpoints
    response = test_client.post(
        "/api/types/userQuota/instances",
        json={"@base": "storageObject", "filesystem_id": "fs_1", "uid": 1000, "hard_limit": 2147483648},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    user_quota_id = data["entries"][0]["content"]["id"]

    response = test_client.get(f"/api/types/userQuota/instances/{user_quota_id}", headers=headers)
    assert response.status_code == 200

    # Clean up
    response = test_client.delete(f"/api/types/userQuota/instances/{user_quota_id}", headers=headers)
    assert response.status_code == 200

    response = test_client.delete(f"/api/types/treeQuota/instances/{tree_quota_id}", headers=headers)
    assert response.status_code == 200
