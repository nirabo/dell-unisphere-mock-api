from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request

from dell_unisphere_mock_api.controllers.filesystem_controller import FilesystemController
from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.schemas.filesystem import FilesystemCreate, FilesystemUpdate

router = APIRouter()
filesystem_controller = FilesystemController()


@router.post("/types/filesystem/instances")
def create_filesystem(
    filesystem_data: FilesystemCreate,
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> ApiResponse:
    """
    Create a new filesystem instance.
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create filesystems")

    return filesystem_controller.create_filesystem(filesystem_data, request)


@router.get("/types/filesystem/instances")
def list_filesystems(
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> ApiResponse:
    """
    List all filesystem instances.
    """
    return filesystem_controller.list_filesystems(request)


@router.get("/instances/filesystem/{filesystem_id}")
def get_filesystem(
    filesystem_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> ApiResponse:
    """
    Get a specific filesystem instance by ID.
    """
    return filesystem_controller.get_filesystem(filesystem_id, request)


@router.patch("/types/filesystem/instances/{filesystem_id}")
def update_filesystem(
    filesystem_id: str,
    update_data: FilesystemUpdate,
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> ApiResponse:
    """
    Update a specific filesystem instance.
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update filesystems")

    return filesystem_controller.update_filesystem(filesystem_id, update_data, request)


@router.delete("/types/filesystem/instances/{filesystem_id}")
def delete_filesystem(
    filesystem_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> ApiResponse:
    """
    Delete a specific filesystem instance.
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete filesystems")

    return filesystem_controller.delete_filesystem(filesystem_id, request)
