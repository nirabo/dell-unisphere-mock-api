from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.response import UnityResponseFormatter
from dell_unisphere_mock_api.models.disk import DiskModel
from dell_unisphere_mock_api.schemas.disk import Disk, DiskCreate, DiskUpdate

router = APIRouter()
disk_model = DiskModel()


@router.post("/types/disk/instances", status_code=status.HTTP_201_CREATED)
async def create_disk(request: Request, disk: DiskCreate, current_user: dict = Depends(get_current_user)):
    """Create a new disk."""
    # Convert pydantic model to dict
    disk_data = disk.model_dump()
    disk_data["health_status"] = "OK"  # Set default health status

    # Validate disk type
    if not disk_model.validate_disk_type(disk.disk_type):
        raise HTTPException(status_code=400, detail="Invalid disk type")

    # Create disk and return
    result = disk_model.create(disk_data)
    disk_obj = Disk(**result["entries"][0]["content"])
    formatter = UnityResponseFormatter(request)
    return await formatter.format_collection([disk_obj])


@router.get("/types/disk/instances")
async def list_disks(request: Request, current_user: dict = Depends(get_current_user)):
    """List all disks."""
    result = disk_model.list()
    disks = [Disk(**entry["content"]) for entry in result["entries"]]
    formatter = UnityResponseFormatter(request)
    return await formatter.format_collection(disks)


@router.get("/types/disk/instances/{disk_id}")
async def get_disk(request: Request, disk_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific disk by ID."""
    result = disk_model.get(disk_id)
    if not result or not result["entries"]:
        raise HTTPException(status_code=404, detail="Disk not found")
    disk = Disk(**result["entries"][0]["content"])
    formatter = UnityResponseFormatter(request)
    return await formatter.format_collection([disk])


@router.patch("/types/disk/instances/{disk_id}")
async def update_disk(request: Request, disk_id: str, disk: DiskUpdate, current_user: dict = Depends(get_current_user)):
    """Update a disk."""
    result = disk_model.update(disk_id, disk.model_dump(exclude_unset=True))
    if not result or not result["entries"]:
        raise HTTPException(status_code=404, detail="Disk not found")
    updated_disk = Disk(**result["entries"][0]["content"])
    formatter = UnityResponseFormatter(request)
    return await formatter.format_collection([updated_disk])


@router.delete("/types/disk/instances/{disk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_disk(disk_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a disk."""
    if not disk_model.delete(disk_id):
        raise HTTPException(status_code=404, detail="Disk not found")


@router.get("/types/disk/instances/byPool/{pool_id}")
async def get_disks_by_pool(request: Request, pool_id: str, current_user: dict = Depends(get_current_user)):
    """Get all disks associated with a specific pool."""
    result = disk_model.get_by_pool(pool_id)
    disks = [Disk(**entry["content"]) for entry in result["entries"]]
    formatter = UnityResponseFormatter(request)
    return await formatter.format_collection(disks)


@router.get("/types/disk/instances/byDiskGroup/{disk_group_id}")
async def get_disks_by_disk_group(request: Request, disk_group_id: str, current_user: dict = Depends(get_current_user)):
    """Get all disks associated with a specific disk group."""
    result = disk_model.get_by_disk_group(disk_group_id)
    disks = [Disk(**entry["content"]) for entry in result["entries"]]
    formatter = UnityResponseFormatter(request)
    return await formatter.format_collection(disks)
