from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from dell_unisphere_mock_api.controllers.filesystem_controller import FilesystemController
from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.schemas.filesystem import FilesystemCreate, FilesystemResponse, FilesystemUpdate

router = APIRouter()
filesystem_controller = FilesystemController()


@router.post("/types/filesystem/instances", response_model=ApiResponse[FilesystemResponse])
async def create_filesystem(
    filesystem_data: FilesystemCreate,
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user),
) -> ApiResponse[FilesystemResponse]:
    """
    Create a new filesystem instance.
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create filesystems")

    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"
    return await filesystem_controller.create_filesystem(request, filesystem_data)


@router.get("/types/filesystem/instances", response_model=ApiResponse[FilesystemResponse])
async def list_filesystems(
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user),
) -> ApiResponse[FilesystemResponse]:
    """
    List all filesystem instances.
    """
    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"
    return await filesystem_controller.list_filesystems(request)


@router.get("/instances/filesystem/{filesystem_id}", response_model=ApiResponse[FilesystemResponse])
async def get_filesystem(
    filesystem_id: str,
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user),
) -> ApiResponse[FilesystemResponse]:
    """
    Get a specific filesystem instance by ID.
    """
    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"
    return await filesystem_controller.get_filesystem(request, filesystem_id)


@router.delete("/instances/filesystem/{filesystem_id}", response_model=ApiResponse[FilesystemResponse])
async def delete_filesystem(
    filesystem_id: str,
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user),
) -> ApiResponse[FilesystemResponse]:
    """
    Delete a specific filesystem instance.
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete filesystems")

    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"
    return await filesystem_controller.delete_filesystem(request, filesystem_id)


@router.patch("/instances/filesystem/{filesystem_id}", response_model=ApiResponse[FilesystemResponse])
async def update_filesystem(
    filesystem_id: str,
    update_data: FilesystemUpdate,
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user),
) -> ApiResponse[FilesystemResponse]:
    """
    Update a specific filesystem instance.
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update filesystems")

    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"
    return await filesystem_controller.update_filesystem(request, filesystem_id, update_data)
