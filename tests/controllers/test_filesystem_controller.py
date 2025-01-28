import pytest
import pytest_asyncio
from fastapi import HTTPException

from dell_unisphere_mock_api.controllers.filesystem_controller import FilesystemController
from dell_unisphere_mock_api.schemas.filesystem import FilesystemCreate, FilesystemTypeEnum, FilesystemUpdate


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
    response = await filesystem_controller.create_filesystem(
        request=mock_request, filesystem_data=sample_filesystem_create
    )
    assert response.base == "http://testserver/api/types/filesystem/instances"
    assert len(response.entries) == 1

    fs = response.entries[0].content
    assert fs.name == "test_fs"
    assert fs.description == "Test filesystem"
    assert fs.nasServer == "test_nas_server"
    assert fs.pool == "test_pool_id"
    assert fs.size == 1099511627776
    assert fs.isThinEnabled is True
    assert fs.isDataReductionEnabled is False
    assert fs.type == FilesystemTypeEnum.FileSystem
    assert fs.health == "OK"
    assert fs.sizeAllocated == 1024 * 1024 * 1024  # 1GB cap for thin provisioned
    assert fs.sizeUsed == 0
    assert fs.cifsShares == []
    assert fs.nfsShares == []
    assert fs.created is not None
    assert fs.modified is not None

    assert response.entries[0].links[0].rel == "self"
    assert response.entries[0].links[0].href == f"/{fs.id}"


@pytest.mark.asyncio
async def test_get_filesystem(filesystem_controller, sample_filesystem_create, mock_request):
    """Test retrieving a filesystem by ID."""
    created = await filesystem_controller.create_filesystem(
        request=mock_request, filesystem_data=sample_filesystem_create
    )
    fs_id = created.entries[0].content.id

    response = await filesystem_controller.get_filesystem(request=mock_request, filesystem_id=fs_id)
    assert response.base == "http://testserver/api/types/filesystem/instances"
    assert len(response.entries) == 1
    assert response.entries[0].content.id == fs_id
    assert response.entries[0].content.name == "test_fs"
    assert response.entries[0].content.description == "Test filesystem"
    assert response.entries[0].content.nasServer == "test_nas_server"
    assert response.entries[0].content.pool == "test_pool_id"


@pytest.mark.asyncio
async def test_get_filesystem_not_found(filesystem_controller, mock_request):
    """Test retrieving a non-existent filesystem."""
    with pytest.raises(HTTPException) as exc_info:
        await filesystem_controller.get_filesystem(request=mock_request, filesystem_id="non_existent_id")
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_list_filesystems(filesystem_controller, sample_filesystem_create, mock_request):
    """Test listing all filesystems."""
    created = await filesystem_controller.create_filesystem(
        request=mock_request, filesystem_data=sample_filesystem_create
    )
    fs_id = created.entries[0].content.id

    response = await filesystem_controller.list_filesystems(request=mock_request)
    assert response.base == "http://testserver/api/types/filesystem/instances"
    assert len(response.entries) == 1
    assert response.entries[0].content.id == fs_id
    assert response.entries[0].content.name == "test_fs"
    assert response.entries[0].content.description == "Test filesystem"
    assert response.entries[0].content.nasServer == "test_nas_server"
    assert response.entries[0].content.pool == "test_pool_id"


@pytest.mark.asyncio
async def test_update_filesystem(filesystem_controller, sample_filesystem_create, mock_request):
    """Test updating a filesystem."""
    created = await filesystem_controller.create_filesystem(
        request=mock_request, filesystem_data=sample_filesystem_create
    )
    fs_id = created.entries[0].content.id
    old_allocated = created.entries[0].content.sizeAllocated

    update_data = FilesystemUpdate(
        description="Updated description", isDataReductionEnabled=True, size=2199023255552  # 2TB
    )
    response = await filesystem_controller.update_filesystem(
        request=mock_request, filesystem_id=fs_id, update_data=update_data
    )
    assert response.base == "http://testserver/api/types/filesystem/instances"
    assert len(response.entries) == 1

    updated_fs = response.entries[0].content
    assert updated_fs.description == "Updated description"
    assert updated_fs.isDataReductionEnabled is True
    assert updated_fs.size == 2199023255552
    assert updated_fs.sizeAllocated > old_allocated  # Should increase by 10% of the size increase
    assert updated_fs.name == "test_fs"  # Should remain unchanged
    assert updated_fs.nasServer == "test_nas_server"  # Should remain unchanged
    assert updated_fs.pool == "test_pool_id"  # Should remain unchanged


@pytest.mark.asyncio
async def test_update_filesystem_decrease_size(filesystem_controller, sample_filesystem_create, mock_request):
    """Test that decreasing filesystem size is not allowed."""
    created = await filesystem_controller.create_filesystem(
        request=mock_request, filesystem_data=sample_filesystem_create
    )
    fs_id = created.entries[0].content.id

    update_data = FilesystemUpdate(size=549755813888)  # 0.5TB
    with pytest.raises(HTTPException) as exc_info:
        await filesystem_controller.update_filesystem(
            request=mock_request, filesystem_id=fs_id, update_data=update_data
        )
    assert exc_info.value.status_code == 400
    assert "size cannot be decreased" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_delete_filesystem(filesystem_controller, sample_filesystem_create, mock_request):
    """Test deleting a filesystem."""
    created = await filesystem_controller.create_filesystem(
        request=mock_request, filesystem_data=sample_filesystem_create
    )
    fs_id = created.entries[0].content.id

    # Delete should succeed
    response = await filesystem_controller.delete_filesystem(request=mock_request, filesystem_id=fs_id)
    assert response is None

    # Get should fail
    with pytest.raises(HTTPException) as exc_info:
        await filesystem_controller.get_filesystem(request=mock_request, filesystem_id=fs_id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_filesystem_with_shares(filesystem_controller, sample_filesystem_create, mock_request):
    """Test that deleting a filesystem with shares is not allowed."""
    created = await filesystem_controller.create_filesystem(
        request=mock_request, filesystem_data=sample_filesystem_create
    )
    fs_id = created.entries[0].content.id

    # Add a share
    await filesystem_controller.add_share(
        request=mock_request, filesystem_id=fs_id, share_id="share1", share_type="CIFS"
    )

    # Delete should fail
    with pytest.raises(HTTPException) as exc_info:
        await filesystem_controller.delete_filesystem(request=mock_request, filesystem_id=fs_id)
    assert exc_info.value.status_code == 400
    assert "active shares" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_add_and_remove_share(filesystem_controller, sample_filesystem_create, mock_request):
    """Test adding and removing shares from a filesystem."""
    created = await filesystem_controller.create_filesystem(
        request=mock_request, filesystem_data=sample_filesystem_create
    )
    fs_id = created.entries[0].content.id

    # Add CIFS share
    response = await filesystem_controller.add_share(
        request=mock_request, filesystem_id=fs_id, share_id="cifs1", share_type="CIFS"
    )
    assert "cifs1" in response.entries[0].content.cifsShares
    assert len(response.entries[0].content.nfsShares) == 0

    # Add NFS share
    response = await filesystem_controller.add_share(
        request=mock_request, filesystem_id=fs_id, share_id="nfs1", share_type="NFS"
    )
    assert "cifs1" in response.entries[0].content.cifsShares
    assert "nfs1" in response.entries[0].content.nfsShares

    # Remove CIFS share
    response = await filesystem_controller.remove_share(
        request=mock_request, filesystem_id=fs_id, share_id="cifs1", share_type="CIFS"
    )
    assert len(response.entries[0].content.cifsShares) == 0
    assert "nfs1" in response.entries[0].content.nfsShares

    # Remove NFS share
    response = await filesystem_controller.remove_share(
        request=mock_request, filesystem_id=fs_id, share_id="nfs1", share_type="NFS"
    )
    assert len(response.entries[0].content.cifsShares) == 0
    assert len(response.entries[0].content.nfsShares) == 0
