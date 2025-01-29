from datetime import datetime, timezone
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.response import UnityResponseFormatter
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.models.storage_resource import StorageResourceModel, StorageResourceResponse

router = APIRouter()
storage_resource_model = StorageResourceModel()


@router.post("/types/storageResource/instances", response_model=ApiResponse[StorageResourceResponse], status_code=201)
async def create_storage_resource(
    resource_data: dict, request: Request, response: Response, current_user: dict = Depends(get_current_user)
) -> ApiResponse[StorageResourceResponse]:
    """Create a new storage resource instance."""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create storage resources")

    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"

    resource = storage_resource_model.create_storage_resource(resource_data)
    formatter = UnityResponseFormatter(request)
    return await formatter.format_collection([resource])


@router.get("/types/storageResource/instances", response_model=ApiResponse[StorageResourceResponse])
async def list_storage_resources(
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user),
) -> ApiResponse[StorageResourceResponse]:
    """List all storage resource instances."""
    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"

    resources = storage_resource_model.list_storage_resources()
    formatter = UnityResponseFormatter(request)
    return await formatter.format_collection(resources)


@router.get("/instances/storageResource/{resource_id}", response_model=ApiResponse[StorageResourceResponse])
async def get_storage_resource(
    resource_id: str, request: Request, response: Response, current_user: dict = Depends(get_current_user)
) -> ApiResponse[StorageResourceResponse]:
    """Get a specific storage resource instance by ID."""
    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"

    resource = storage_resource_model.get_storage_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Storage resource not found")

    formatter = UnityResponseFormatter(request)
    return await formatter.format_collection([resource])


@router.patch("/instances/storageResource/{resource_id}", response_model=ApiResponse[StorageResourceResponse])
async def update_storage_resource(
    resource_id: str,
    update_data: dict,
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user),
) -> ApiResponse[StorageResourceResponse]:
    """Update a specific storage resource instance."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update storage resources")

    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"

    resource = storage_resource_model.update_storage_resource(resource_id, update_data)
    if not resource:
        raise HTTPException(status_code=404, detail="Storage resource not found")

    formatter = UnityResponseFormatter(request)
    return await formatter.format_collection([resource])


@router.delete("/instances/storageResource/{resource_id}", response_model=ApiResponse[StorageResourceResponse])
async def delete_storage_resource(
    resource_id: str, request: Request, response: Response, current_user: dict = Depends(get_current_user)
) -> ApiResponse[StorageResourceResponse]:
    """Delete a specific storage resource instance."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete storage resources")

    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"

    resource = storage_resource_model.delete_storage_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Storage resource not found")

    formatter = UnityResponseFormatter(request)
    return await formatter.format_collection([resource])


@router.post(
    "/instances/storageResource/{resource_id}/action/modifyHostAccess",
    response_model=ApiResponse[StorageResourceResponse],
)
async def modify_host_access(
    resource_id: str,
    host_access: dict,
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user),
) -> ApiResponse[StorageResourceResponse]:
    """Modify host access for a storage resource."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to modify host access")

    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"

    resource = storage_resource_model.modify_host_access(resource_id, host_access)
    if not resource:
        raise HTTPException(status_code=404, detail="Storage resource not found")

    formatter = UnityResponseFormatter(request)
    return await formatter.format_collection([resource])


@router.post("/types/storageResource/action/createLun", response_model=ApiResponse[StorageResourceResponse])
async def create_lun(
    lun_data: dict, request: Request, response: Response, current_user: dict = Depends(get_current_user)
) -> ApiResponse[StorageResourceResponse]:
    """Create a new LUN storage resource."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create LUNs")

    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"

    resource = storage_resource_model.create_lun(lun_data)
    formatter = UnityResponseFormatter(request)
    return await formatter.format_collection([resource])


@router.post(
    "/instances/storageResource/{resource_id}/action/modifyLun", response_model=ApiResponse[StorageResourceResponse]
)
async def modify_lun(
    resource_id: str,
    lun_data: dict,
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user),
) -> ApiResponse[StorageResourceResponse]:
    """Modify an existing LUN storage resource."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to modify LUNs")

    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"

    resource = storage_resource_model.modify_lun(resource_id, lun_data)
    if not resource:
        raise HTTPException(status_code=404, detail="Storage resource not found")

    formatter = UnityResponseFormatter(request)
    return await formatter.format_collection([resource])


@router.post(
    "/instances/storageResource/{resource_id}/action/expand", response_model=ApiResponse[StorageResourceResponse]
)
async def expand_lun(
    resource_id: str,
    expand_data: dict,
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user),
) -> ApiResponse[StorageResourceResponse]:
    """Expand an existing LUN storage resource."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to expand LUNs")

    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"

    resource = storage_resource_model.expand_lun(resource_id, expand_data)
    if not resource:
        raise HTTPException(status_code=404, detail="Storage resource not found")

    formatter = UnityResponseFormatter(request)
    return await formatter.format_collection([resource])


@router.post(
    "/instances/storageResource/{resource_id}/action/delete", response_model=ApiResponse[StorageResourceResponse]
)
async def delete_storage_resource_action(
    resource_id: str, request: Request, response: Response, current_user: dict = Depends(get_current_user)
) -> ApiResponse[StorageResourceResponse]:
    """Delete a storage resource via action endpoint."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete storage resources")

    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"

    resource = storage_resource_model.delete_storage_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Storage resource not found")

    formatter = UnityResponseFormatter(request)
    return await formatter.format_collection([resource])
