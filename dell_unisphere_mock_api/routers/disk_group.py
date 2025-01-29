from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.response import UnityResponseFormatter
from dell_unisphere_mock_api.models.disk_group import DiskGroupModel
from dell_unisphere_mock_api.schemas.disk_group import DiskGroup, DiskGroupCreate, DiskGroupUpdate

router = APIRouter()
disk_group_model = DiskGroupModel()


@router.post(
    "/types/diskGroup/instances",
    status_code=status.HTTP_201_CREATED,
)
async def create_disk_group(
    request: Request, disk_group: DiskGroupCreate, current_user: dict = Depends(get_current_user)
):
    """Create a new disk group."""
    # Validate RAID configuration
    if not disk_group_model.validate_raid_config(
        disk_group.raid_type, disk_group.stripe_width, len(disk_group.disk_ids)
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid RAID configuration for the given stripe width and number of disks",
        )
    result = disk_group_model.create(disk_group.model_dump())
    formatter = UnityResponseFormatter(request)
    return formatter.format_collection([result["entries"][0]["content"]])


@router.get("/types/diskGroup/instances")
async def list_disk_groups(request: Request, current_user: dict = Depends(get_current_user)):
    """List all disk groups."""
    result = disk_group_model.list()
    formatter = UnityResponseFormatter(request)
    return formatter.format_collection([entry["content"] for entry in result["entries"]])


@router.get("/types/diskGroup/instances/{disk_group_id}")
async def get_disk_group(request: Request, disk_group_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific disk group by ID."""
    result = disk_group_model.get(disk_group_id)
    if not result["entries"]:
        raise HTTPException(status_code=404, detail="Disk group not found")
    formatter = UnityResponseFormatter(request)
    return formatter.format_collection([result["entries"][0]["content"]])


@router.patch("/types/diskGroup/instances/{disk_group_id}")
async def update_disk_group(
    request: Request,
    disk_group_id: str,
    disk_group: DiskGroupUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update a disk group."""
    result = disk_group_model.update(disk_group_id, disk_group.model_dump(exclude_unset=True))
    if not result["entries"]:
        raise HTTPException(status_code=404, detail="Disk group not found")
    formatter = UnityResponseFormatter(request)
    return formatter.format_collection([result["entries"][0]["content"]])


@router.delete("/types/diskGroup/instances/{disk_group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_disk_group(disk_group_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a disk group."""
    if not disk_group_model.delete(disk_group_id):
        raise HTTPException(status_code=404, detail="Disk group not found")
