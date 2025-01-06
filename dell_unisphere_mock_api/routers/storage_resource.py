from datetime import datetime, timezone
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException

from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.models.storage_resource import StorageResourceModel

router = APIRouter()
storage_resource_model = StorageResourceModel()


@router.post("/types/storageResource/instances", status_code=201)
async def create_storage_resource(resource_data: dict, current_user: dict = Depends(get_current_user)) -> dict:
    """Create a new storage resource instance."""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create storage resources")

    return storage_resource_model.create_storage_resource(resource_data)


@router.get("/types/storageResource/instances")
async def list_storage_resources(
    current_user: dict = Depends(get_current_user),
) -> List[dict]:
    """List all storage resource instances."""
    return storage_resource_model.list_storage_resources()


@router.get("/types/storageResource/instances/{resource_id}")
async def get_storage_resource(resource_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    """Get a specific storage resource instance by ID."""
    resource = storage_resource_model.get_storage_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Storage resource not found")
    return resource


@router.patch("/types/storageResource/instances/{resource_id}")
async def update_storage_resource(
    resource_id: str, update_data: dict, current_user: dict = Depends(get_current_user)
) -> dict:
    """Update a specific storage resource instance."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update storage resources")

    resource = storage_resource_model.update_storage_resource(resource_id, update_data)
    if not resource:
        raise HTTPException(status_code=404, detail="Storage resource not found")
    return resource


@router.delete("/types/storageResource/instances/{resource_id}")
async def delete_storage_resource(resource_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    """Delete a specific storage resource instance."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete storage resources")

    success = storage_resource_model.delete_storage_resource(resource_id)
    if not success:
        raise HTTPException(status_code=404, detail="Storage resource not found")
    return {"message": "Storage resource deleted successfully"}


@router.post("/types/storageResource/instances/{resource_id}/action/modifyHostAccess")
async def modify_host_access(
    resource_id: str, host_access: dict, current_user: dict = Depends(get_current_user)
) -> dict:
    """Modify host access for a storage resource."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to modify host access")

    # Get the resource first to check it exists
    resource = storage_resource_model.get_storage_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Storage resource not found")

    # Update host access
    success = storage_resource_model.update_host_access(
        resource_id=resource_id,
        host_id=host_access["host"],
        access_type=host_access["accessType"],
    )

    if not success:
        raise HTTPException(status_code=400, detail="Failed to update host access")

    return storage_resource_model.get_storage_resource(resource_id)


@router.post("/types/storageResource/action/createLun")
async def create_lun(lun_data: dict, current_user: dict = Depends(get_current_user)) -> dict:
    """Create a new LUN storage resource."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create LUNs")

    # Validate required fields
    if "name" not in lun_data or "lunParameters" not in lun_data:
        raise HTTPException(status_code=400, detail="Missing required fields: name and lunParameters")

    if "pool" not in lun_data["lunParameters"] or "size" not in lun_data["lunParameters"]:
        raise HTTPException(status_code=400, detail="Missing required lunParameters: pool and size")

    # Create LUN with type "lun"
    lun_data["type"] = "lun"
    lun_data["sizeTotal"] = int(lun_data["lunParameters"]["size"])  # Set the size from lunParameters
    resource = storage_resource_model.create_storage_resource(lun_data)

    return {
        "@base": "https://unisphere/api/types/storageResource/action/createLun",
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "links": [{"rel": "self", "href": f"/{resource['id']}"}],
        "content": {"storageResource": {"id": resource["id"]}},
    }


@router.post("/types/storageResource/{resource_id}/action/modifyLun")
async def modify_lun(resource_id: str, lun_data: dict, current_user: dict = Depends(get_current_user)) -> dict:
    """Modify an existing LUN storage resource."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to modify LUNs")

    resource = storage_resource_model.get_storage_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Storage resource not found")

    if resource["type"] != "lun":
        raise HTTPException(status_code=400, detail="Storage resource is not a LUN")

    # Update LUN properties
    update_data = {}
    if "description" in lun_data:
        update_data["description"] = lun_data["description"]
    if "lunParameters" in lun_data and "size" in lun_data["lunParameters"]:
        update_data["sizeTotal"] = lun_data["lunParameters"]["size"]

    storage_resource_model.update_storage_resource(resource_id, update_data)
    return {"status": "success"}


@router.post("/types/storageResource/{resource_id}/action/expandLun")
async def expand_lun(resource_id: str, expand_data: dict, current_user: dict = Depends(get_current_user)) -> dict:
    """Expand an existing LUN storage resource."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to expand LUNs")

    resource = storage_resource_model.get_storage_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Storage resource not found")

    if resource["type"] != "lun":
        raise HTTPException(status_code=400, detail="Storage resource is not a LUN")

    if "size" not in expand_data:
        raise HTTPException(status_code=400, detail="Missing required field: size")

    # Ensure new size is larger than current size
    try:
        current_size = int(resource["sizeTotal"])  # Ensure we have integers
        new_size = int(expand_data["size"])
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid size value")

    if new_size <= current_size:
        raise HTTPException(
            status_code=400, detail=f"New size ({new_size}) must be larger than current size ({current_size})"
        )

    # Update the LUN size
    storage_resource_model.update_storage_resource(resource_id, {"sizeTotal": new_size})
    return {"status": "success"}


@router.post("/types/storageResource/{resource_id}/action/delete")
async def delete_storage_resource_action(resource_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    """Delete a storage resource via action endpoint."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete storage resources")

    success = storage_resource_model.delete_storage_resource(resource_id)
    if not success:
        raise HTTPException(status_code=404, detail="Storage resource not found")
    return {"status": "success"}
