from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path

from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.models.nas_server import NasServerModel
from dell_unisphere_mock_api.schemas.nas_server import (
    NasServerCreate,
    NasServerResponse,
    NasServerUpdate,
    PingRequest,
    TracerouteRequest,
    UserMapping,
)

router = APIRouter()
nas_server_model = NasServerModel()


# Helper function to get NAS server or raise 404
async def get_nas_server_or_404(identifier: str) -> dict:
    nas_server = nas_server_model.get_nas_server(identifier)
    if not nas_server:
        raise HTTPException(status_code=404, detail="NAS server not found")
    return nas_server


# Basic CRUD Operations
@router.post("/types/nasServer/instances", response_model=NasServerResponse)
async def create_nas_server(nas_server_data: NasServerCreate, current_user: dict = Depends(get_current_user)) -> dict:
    """Create a new NAS server instance."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create NAS servers")
    return nas_server_model.create_nas_server(nas_server_data.model_dump())


@router.get("/types/nasServer/instances", response_model=List[NasServerResponse])
async def list_nas_servers(
    current_user: dict = Depends(get_current_user),
) -> List[dict]:
    """List all NAS server instances."""
    return nas_server_model.list_nas_servers()


@router.get("/instances/nasServer/{nas_id}", response_model=NasServerResponse)
async def get_nas_server_by_id(
    nas_id: str = Path(..., description="NAS server ID"), current_user: dict = Depends(get_current_user)
) -> dict:
    """Get a specific NAS server instance by ID."""
    return await get_nas_server_or_404(nas_id)


@router.get("/types/nasServer/instances/name:{name}", response_model=NasServerResponse)
async def get_nas_server_by_name(
    name: str = Path(..., description="NAS server name"), current_user: dict = Depends(get_current_user)
) -> dict:
    """Get a specific NAS server instance by name."""
    return await get_nas_server_or_404(name)


@router.patch("/types/nasServer/instances/{nas_id}", response_model=NasServerResponse)
async def update_nas_server(
    nas_id: str,
    update_data: NasServerUpdate,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Update a specific NAS server instance."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update NAS servers")
    return await get_nas_server_or_404(nas_id)


@router.delete("/types/nasServer/instances/{nas_id}")
async def delete_nas_server_by_id(
    nas_id: str = Path(..., description="NAS server ID"), current_user: dict = Depends(get_current_user)
) -> dict:
    """Delete a specific NAS server instance by ID."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete NAS servers")
    if nas_server_model.delete_nas_server(nas_id):
        return {"message": "NAS server deleted successfully"}
    raise HTTPException(status_code=404, detail="NAS server not found")


# TODO: Fix FastAPI routing conflict for name-based deletion
# @router.delete("/types/nasServer/instances/name:{name}")
# async def delete_nas_server_by_name(
#     name: str = Path(..., description="NAS server name"), current_user: dict = Depends(get_current_user)
# ) -> dict:
#     """Delete a specific NAS server instance by name."""
#     if current_user["role"] != "admin":
#         raise HTTPException(status_code=403, detail="Not authorized to delete NAS servers")
#     nas_server = await get_nas_server_or_404(name)
#     if nas_server_model.delete_nas_server(name):
#         return {"message": "NAS server deleted successfully"}
#     raise HTTPException(status_code=404, detail="NAS server not found")


# User Mapping Operations
@router.post("/instances/nasServer/{nas_id}/action/generateUserMappingsReport")
async def generate_user_mappings_report(
    nas_id: str = Path(..., description="NAS server ID"), current_user: dict = Depends(get_current_user)
) -> dict:
    """Generate a user mappings report for a NAS server."""
    await get_nas_server_or_404(nas_id)
    report = nas_server_model.generate_user_mappings_report(nas_id)
    if not report:
        raise HTTPException(status_code=500, detail="Failed to generate user mappings report")
    return report


@router.post("/instances/nasServer/{nas_id}/action/updateUserMappings")
async def update_user_mappings(
    nas_id: str, mapping_data: UserMapping, current_user: dict = Depends(get_current_user)
) -> dict:
    """Update user mappings for a NAS server."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update user mappings")
    await get_nas_server_or_404(nas_id)
    result = nas_server_model.update_user_mappings(nas_id, mapping_data.model_dump())
    if not result:
        raise HTTPException(status_code=500, detail="Failed to update user mappings")
    return result


# Configuration Management
@router.post("/instances/nasServer/{nas_id}/action/refreshConfiguration")
async def refresh_configuration(
    nas_id: str = Path(..., description="NAS server ID"), current_user: dict = Depends(get_current_user)
) -> dict:
    """Refresh the configuration of a NAS server."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to refresh configuration")
    result = nas_server_model.refresh_configuration(nas_id)
    if not result:
        raise HTTPException(status_code=404, detail="NAS server not found")
    return result


# Network Diagnostics
@router.post("/instances/nasServer/{nas_id}/action/ping")
async def ping_from_nas(nas_id: str, request: PingRequest, current_user: dict = Depends(get_current_user)) -> dict:
    """Perform ping from a NAS server."""
    await get_nas_server_or_404(nas_id)
    return nas_server_model.ping(nas_id, request.address, request.count, request.timeout, request.size)


@router.post("/instances/nasServer/name:{name}/action/ping")
async def ping_from_nas_by_name(
    name: str, request: PingRequest, current_user: dict = Depends(get_current_user)
) -> dict:
    """Perform ping from a NAS server (specified by name)."""
    await get_nas_server_or_404(name)
    return nas_server_model.ping(name, request.address, request.count, request.timeout, request.size)


@router.post("/instances/nasServer/{nas_id}/action/traceroute")
async def traceroute_from_nas(
    nas_id: str, request: TracerouteRequest, current_user: dict = Depends(get_current_user)
) -> dict:
    """Perform traceroute from a NAS server."""
    await get_nas_server_or_404(nas_id)
    return nas_server_model.traceroute(nas_id, request.address, request.timeout, request.max_hops)


@router.post("/instances/nasServer/name:{name}/action/traceroute")
async def traceroute_from_nas_by_name(
    name: str, request: TracerouteRequest, current_user: dict = Depends(get_current_user)
) -> dict:
    """Perform traceroute from a NAS server (specified by name)."""
    await get_nas_server_or_404(name)
    return nas_server_model.traceroute(name, request.address, request.timeout, request.max_hops)
