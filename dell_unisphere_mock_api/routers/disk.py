from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.models.disk import DiskModel
from dell_unisphere_mock_api.schemas.disk import Disk, DiskCreate, DiskUpdate

router = APIRouter()
disk_model = DiskModel()


@router.post("/types/disk/instances", response_model=Dict, status_code=status.HTTP_201_CREATED)
async def create_disk(disk: DiskCreate, current_user: dict = Depends(get_current_user)):
    """Create a new disk."""
    # Convert pydantic model to dict
    disk_data = disk.model_dump()
    disk_data["health_status"] = "OK"  # Set default health status

    # Validate disk type
    if not disk_model.validate_disk_type(disk.disk_type):
        raise HTTPException(status_code=400, detail="Invalid disk type")

    # Create disk and return
    return disk_model.create(disk_data)


@router.get("/types/disk/instances", response_model=Dict)
async def list_disks(current_user: dict = Depends(get_current_user)):
    """List all disks."""
    return disk_model.list()


@router.get("/types/disk/instances/{disk_id}", response_model=Dict)
async def get_disk(disk_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific disk by ID."""
    disk = disk_model.get(disk_id)
    if not disk or not disk["entries"]:
        raise HTTPException(status_code=404, detail="Disk not found")
    return disk


@router.patch("/types/disk/instances/{disk_id}", response_model=Dict)
async def update_disk(disk_id: str, disk: DiskUpdate, current_user: dict = Depends(get_current_user)):
    """Update a disk."""
    updated_disk = disk_model.update(disk_id, disk.model_dump(exclude_unset=True))
    if not updated_disk or not updated_disk["entries"]:
        raise HTTPException(status_code=404, detail="Disk not found")
    return updated_disk


@router.delete("/types/disk/instances/{disk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_disk(disk_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a disk."""
    if not disk_model.delete(disk_id):
        raise HTTPException(status_code=404, detail="Disk not found")


@router.get("/types/disk/instances/byPool/{pool_id}", response_model=Dict)
async def get_disks_by_pool(pool_id: str, current_user: dict = Depends(get_current_user)):
    """Get all disks associated with a specific pool."""
    return disk_model.get_by_pool(pool_id)


@router.get("/types/disk/instances/byDiskGroup/{disk_group_id}", response_model=Dict)
async def get_disks_by_disk_group(disk_group_id: str, current_user: dict = Depends(get_current_user)):
    """Get all disks associated with a specific disk group."""
    return disk_model.get_by_disk_group(disk_group_id)
