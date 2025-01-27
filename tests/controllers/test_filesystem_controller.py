import pytest
from fastapi import HTTPException

from dell_unisphere_mock_api.controllers.filesystem_controller import FilesystemController
from dell_unisphere_mock_api.schemas.filesystem import FilesystemCreate, FilesystemUpdate


@pytest.fixture
def filesystem_controller():
    return FilesystemController()


@pytest.fixture
def sample_filesystem_create():
    return FilesystemCreate(
        name="test_fs",
        description="Test filesystem",
        nasServer="test_nas_server",
        pool="test_pool_id",
        size=1099511627776,  # 1TB
        isThinEnabled=True,
        isDataReductionEnabled=False,
        type="thick",
    )


@pytest.fixture
def mock_request(mocker):
    mock = mocker.Mock()
    mock.base_url = "http://testserver"
    mock.url = mocker.Mock()
    mock.url.path = "/api/types/filesystem/instances"
    return mock


@pytest.mark.asyncio
async def test_create_filesystem(filesystem_controller, sample_filesystem_create, mock_request):
    """Test creating a new filesystem."""
    response = await filesystem_controller.create_filesystem(sample_filesystem_create, mock_request)
    assert response.base == "http://testserver/api/types/filesystem/instances"
    assert len(response.entries) == 1

    fs = response.entries[0].content
    assert fs.name == "test_fs"
    assert fs.description == "Test filesystem"
    assert fs.nasServer == "test_nas_server"
    assert fs.pool == "test_pool_id"
    assert fs.size == 1099511627776
    assert fs.isThinEnabled is True
    assert fs.isCompressionEnabled is False
    assert fs.isAdvancedDedupEnabled is False

    assert response.entries[0].links[0].rel == "self"
    assert response.entries[0].links[0].href == f"/{fs.id}"


@pytest.mark.asyncio
async def test_get_filesystem(filesystem_controller, sample_filesystem_create, mock_request):
    """Test retrieving a filesystem by ID."""
    created = await filesystem_controller.create_filesystem(sample_filesystem_create, mock_request)
    fs_id = created.entries[0].content.id

    response = await filesystem_controller.get_filesystem(fs_id, mock_request)
    assert response.base == "http://testserver/api/types/filesystem/instances"
    assert len(response.entries) == 1
    assert response.entries[0].content.id == fs_id
    assert response.entries[0].content.name == "test_fs"


@pytest.mark.asyncio
async def test_get_filesystem_not_found(filesystem_controller, mock_request):
    """Test retrieving a non-existent filesystem."""
    with pytest.raises(HTTPException) as exc_info:
        await filesystem_controller.get_filesystem("non_existent_id", mock_request)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_list_filesystems(filesystem_controller, sample_filesystem_create, mock_request):
    """Test listing all filesystems."""
    await filesystem_controller.create_filesystem(sample_filesystem_create, mock_request)

    response = await filesystem_controller.list_filesystems(mock_request)
    assert response.base == "http://testserver/api/types/filesystem/instances"
    assert len(response.entries) >= 1
    assert all(fs.content.name is not None for fs in response.entries)


@pytest.mark.asyncio
async def test_update_filesystem(filesystem_controller, sample_filesystem_create, mock_request):
    """Test updating a filesystem."""
    created = await filesystem_controller.create_filesystem(sample_filesystem_create, mock_request)
    fs_id = created.entries[0].content.id

    update_data = FilesystemUpdate(
        description="Updated description", isCompressionEnabled=True, size=2199023255552  # 2TB
    )
    response = await filesystem_controller.update_filesystem(fs_id, update_data, mock_request)
    assert response.base == "http://testserver/api/types/filesystem/instances"
    assert len(response.entries) == 1
    assert response.entries[0].content.description == "Updated description"
    assert response.entries[0].content.isCompressionEnabled is True
    assert response.entries[0].content.size == 2199023255552
    # Original values should remain unchanged
    assert response.entries[0].content.name == "test_fs"
    assert response.entries[0].content.pool == "test_pool_id"


@pytest.mark.asyncio
async def test_update_filesystem_decrease_size(filesystem_controller, sample_filesystem_create, mock_request):
    """Test that decreasing filesystem size is not allowed."""
    created = await filesystem_controller.create_filesystem(sample_filesystem_create, mock_request)
    fs_id = created.entries[0].content.id

    update_data = FilesystemUpdate(size=549755813888)  # 512GB
    with pytest.raises(HTTPException) as exc_info:
        await filesystem_controller.update_filesystem(fs_id, update_data, mock_request)
    assert exc_info.value.status_code == 400
    assert "size cannot be decreased" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_delete_filesystem(filesystem_controller, sample_filesystem_create, mock_request):
    """Test deleting a filesystem."""
    created = await filesystem_controller.create_filesystem(sample_filesystem_create, mock_request)
    fs_id = created.entries[0].content.id

    response = await filesystem_controller.delete_filesystem(fs_id, mock_request)
    assert response is None

    # Verify filesystem is deleted
    with pytest.raises(HTTPException) as exc_info:
        await filesystem_controller.get_filesystem(fs_id, mock_request)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_filesystem_with_shares(filesystem_controller, sample_filesystem_create, mock_request):
    """Test that deleting a filesystem with shares is not allowed."""
    created = await filesystem_controller.create_filesystem(sample_filesystem_create, mock_request)
    fs_id = created.entries[0].content.id

    # Add a share
    await filesystem_controller.add_share(fs_id, "test_share", "cifs", mock_request)

    with pytest.raises(HTTPException) as exc_info:
        await filesystem_controller.delete_filesystem(fs_id, mock_request)
    assert exc_info.value.status_code == 400
    assert "active shares" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_add_and_remove_share(filesystem_controller, sample_filesystem_create, mock_request):
    """Test adding and removing shares from a filesystem."""
    created = await filesystem_controller.create_filesystem(sample_filesystem_create, mock_request)
    fs_id = created.entries[0].content.id

    # Add CIFS share
    response = await filesystem_controller.add_share(fs_id, "test_share", "cifs", mock_request)
    assert response.entries[0].content.cifsShares == ["test_share"]
    assert not response.entries[0].content.nfsShares

    # Add NFS share
    response = await filesystem_controller.add_share(fs_id, "test_nfs", "nfs", mock_request)
    assert response.entries[0].content.cifsShares == ["test_share"]
    assert response.entries[0].content.nfsShares == ["test_nfs"]

    # Remove CIFS share
    response = await filesystem_controller.remove_share(fs_id, "test_share", "cifs", mock_request)
    assert not response.entries[0].content.cifsShares
    assert response.entries[0].content.nfsShares == ["test_nfs"]

    # Remove NFS share
    response = await filesystem_controller.remove_share(fs_id, "test_nfs", "nfs", mock_request)
    assert not response.entries[0].content.cifsShares
    assert not response.entries[0].content.nfsShares
