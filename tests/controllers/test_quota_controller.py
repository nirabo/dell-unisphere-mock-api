import pytest
from fastapi import HTTPException

from dell_unisphere_mock_api.controllers.quota_controller import QuotaController
from dell_unisphere_mock_api.models.quota import (
    QuotaConfigCreate,
    QuotaConfigUpdate,
    TreeQuotaCreate,
    TreeQuotaUpdate,
    UserQuotaCreate,
    UserQuotaUpdate,
)


@pytest.fixture
def quota_controller():
    return QuotaController()


@pytest.fixture
def mock_request(mocker):
    mock = mocker.Mock()
    mock.base_url = "http://testserver"
    mock.url = mocker.Mock()
    return mock


@pytest.fixture
def sample_quota_config_create():
    return QuotaConfigCreate(
        filesystem_id="test_fs_id",
        is_user_quotas_enabled=True,
        is_tree_quotas_enabled=True,
        default_hard_limit=1024 * 1024 * 1024,  # 1GB
        default_soft_limit=512 * 1024 * 1024,  # 512MB
        description="Test quota config",
    )


@pytest.fixture
def sample_tree_quota_create():
    return TreeQuotaCreate(
        filesystem_id="test_fs_id",
        path="/test/path",
        hard_limit=1024 * 1024 * 1024,  # 1GB
        soft_limit=512 * 1024 * 1024,  # 512MB
        used_capacity=256 * 1024 * 1024,  # 256MB
        description="Test tree quota",
    )


@pytest.fixture
def sample_user_quota_create():
    return UserQuotaCreate(
        filesystem_id="test_fs_id",
        uid=1000,
        hard_limit=1024 * 1024 * 1024,  # 1GB
        soft_limit=512 * 1024 * 1024,  # 512MB
        used_capacity=256 * 1024 * 1024,  # 256MB
        description="Test user quota",
    )


def test_create_quota_config(quota_controller, sample_quota_config_create, mock_request):
    """Test creating a new quota configuration."""
    mock_request.url.path = "/api/types/quota_config/instances"
    response = quota_controller.create_quota_config(sample_quota_config_create, mock_request)
    assert response.base == "http://testserver/api/types/quota_config/instances"
    assert len(response.entries) == 1

    config = response.entries[0].content
    assert config.filesystem_id == "test_fs_id"
    assert config.is_user_quotas_enabled is True
    assert config.is_tree_quotas_enabled is True
    assert config.default_hard_limit == 1024 * 1024 * 1024
    assert config.default_soft_limit == 512 * 1024 * 1024
    assert config.description == "Test quota config"
    assert config.state == "READY"
    assert config.id is not None

    assert response.entries[0].links[0].rel == "self"
    assert response.entries[0].links[0].href == f"/{config.id}"


def test_get_quota_config(quota_controller, sample_quota_config_create, mock_request):
    """Test retrieving a quota configuration by ID."""
    mock_request.url.path = "/api/types/quota_config/instances"
    created = quota_controller.create_quota_config(sample_quota_config_create, mock_request)
    config_id = created.entries[0].content.id

    response = quota_controller.get_quota_config(config_id, mock_request)
    assert response.base == "http://testserver/api/types/quota_config/instances"
    assert len(response.entries) == 1
    assert response.entries[0].content.id == config_id
    assert response.entries[0].content.filesystem_id == "test_fs_id"


def test_get_quota_config_not_found(quota_controller, mock_request):
    """Test retrieving a non-existent quota configuration."""
    with pytest.raises(HTTPException) as exc_info:
        quota_controller.get_quota_config("non_existent_id", mock_request)
    assert exc_info.value.status_code == 404


def test_list_quota_configs(quota_controller, sample_quota_config_create, mock_request):
    """Test listing all quota configurations."""
    mock_request.url.path = "/api/types/quota_config/instances"
    created = quota_controller.create_quota_config(sample_quota_config_create, mock_request)
    config_id = created.entries[0].content.id

    response = quota_controller.list_quota_configs(mock_request)
    assert response.base == "http://testserver/api/types/quota_config/instances"
    assert len(response.entries) == 1
    assert response.entries[0].content.id == config_id
    assert response.entries[0].content.filesystem_id == "test_fs_id"


def test_update_quota_config(quota_controller, sample_quota_config_create, mock_request):
    """Test updating a quota configuration."""
    mock_request.url.path = "/api/types/quota_config/instances"
    created = quota_controller.create_quota_config(sample_quota_config_create, mock_request)
    config_id = created.entries[0].content.id

    update_data = QuotaConfigUpdate(
        is_user_quotas_enabled=False,
        default_hard_limit=2 * 1024 * 1024 * 1024,  # 2GB
        description="Updated quota config",
    )
    response = quota_controller.update_quota_config(config_id, update_data, mock_request)
    assert response.base == "http://testserver/api/types/quota_config/instances"
    assert len(response.entries) == 1

    updated_config = response.entries[0].content
    assert updated_config.is_user_quotas_enabled is False
    assert updated_config.default_hard_limit == 2 * 1024 * 1024 * 1024
    assert updated_config.description == "Updated quota config"
    assert updated_config.is_tree_quotas_enabled is True  # Should remain unchanged
    assert updated_config.default_soft_limit == 512 * 1024 * 1024  # Should remain unchanged


def test_delete_quota_config(quota_controller, sample_quota_config_create, mock_request):
    """Test deleting a quota configuration."""
    mock_request.url.path = "/api/types/quota_config/instances"
    created = quota_controller.create_quota_config(sample_quota_config_create, mock_request)
    config_id = created.entries[0].content.id

    response = quota_controller.delete_quota_config(config_id, mock_request)
    assert response is None

    with pytest.raises(HTTPException) as exc_info:
        quota_controller.get_quota_config(config_id, mock_request)
    assert exc_info.value.status_code == 404


def test_create_tree_quota(quota_controller, sample_tree_quota_create, mock_request):
    """Test creating a new tree quota."""
    mock_request.url.path = "/api/types/tree_quota/instances"
    response = quota_controller.create_tree_quota(sample_tree_quota_create, mock_request)
    assert response.base == "http://testserver/api/types/tree_quota/instances"
    assert len(response.entries) == 1

    quota = response.entries[0].content
    assert quota.filesystem_id == "test_fs_id"
    assert quota.path == "/test/path"
    assert quota.hard_limit == 1024 * 1024 * 1024
    assert quota.soft_limit == 512 * 1024 * 1024
    assert quota.used_capacity == 256 * 1024 * 1024
    assert quota.description == "Test tree quota"
    assert quota.state == "OK"
    assert quota.id is not None

    assert response.entries[0].links[0].rel == "self"
    assert response.entries[0].links[0].href == f"/{quota.id}"


def test_update_tree_quota(quota_controller, sample_tree_quota_create, mock_request):
    """Test updating a tree quota."""
    mock_request.url.path = "/api/types/tree_quota/instances"
    created = quota_controller.create_tree_quota(sample_tree_quota_create, mock_request)
    quota_id = created.entries[0].content.id

    update_data = TreeQuotaUpdate(
        hard_limit=2 * 1024 * 1024 * 1024,  # 2GB
        description="Updated tree quota",
    )
    response = quota_controller.update_tree_quota(quota_id, update_data, mock_request)
    assert response.base == "http://testserver/api/types/tree_quota/instances"
    assert len(response.entries) == 1

    updated_quota = response.entries[0].content
    assert updated_quota.hard_limit == 2 * 1024 * 1024 * 1024
    assert updated_quota.description == "Updated tree quota"
    assert updated_quota.soft_limit == 512 * 1024 * 1024  # Should remain unchanged
    assert updated_quota.path == "/test/path"  # Should remain unchanged


def test_create_user_quota(quota_controller, sample_user_quota_create, mock_request):
    """Test creating a new user quota."""
    mock_request.url.path = "/api/types/user_quota/instances"
    response = quota_controller.create_user_quota(sample_user_quota_create, mock_request)
    assert response.base == "http://testserver/api/types/user_quota/instances"
    assert len(response.entries) == 1

    quota = response.entries[0].content
    assert quota.filesystem_id == "test_fs_id"
    assert quota.uid == 1000
    assert quota.hard_limit == 1024 * 1024 * 1024
    assert quota.soft_limit == 512 * 1024 * 1024
    assert quota.used_capacity == 256 * 1024 * 1024
    assert quota.description == "Test user quota"
    assert quota.state == "OK"
    assert quota.id is not None

    assert response.entries[0].links[0].rel == "self"
    assert response.entries[0].links[0].href == f"/{quota.id}"


def test_update_user_quota(quota_controller, sample_user_quota_create, mock_request):
    """Test updating a user quota."""
    mock_request.url.path = "/api/types/user_quota/instances"
    created = quota_controller.create_user_quota(sample_user_quota_create, mock_request)
    quota_id = created.entries[0].content.id

    update_data = UserQuotaUpdate(
        hard_limit=2 * 1024 * 1024 * 1024,  # 2GB
        description="Updated user quota",
    )
    response = quota_controller.update_user_quota(quota_id, update_data, mock_request)
    assert response.base == "http://testserver/api/types/user_quota/instances"
    assert len(response.entries) == 1

    updated_quota = response.entries[0].content
    assert updated_quota.hard_limit == 2 * 1024 * 1024 * 1024
    assert updated_quota.description == "Updated user quota"
    assert updated_quota.soft_limit == 512 * 1024 * 1024  # Should remain unchanged
    assert updated_quota.uid == 1000  # Should remain unchanged
