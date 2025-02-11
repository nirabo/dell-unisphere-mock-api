from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request

from dell_unisphere_mock_api.controllers.nfs_share_controller import NFSShareController
from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.response import UnityResponseFormatter
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.models.nfs_share import NFSShare, NFSShareCreate, NFSShareUpdate

router = APIRouter(prefix="/types/nfsShare", tags=["NFS Share"])
controller = NFSShareController()


@router.post("/instances", response_model=ApiResponse, operation_id="create_nfs_share_instance")
async def create_nfs_share(request: Request, nfs_share: NFSShareCreate, _: str = Depends(get_current_user)):
    response = controller.create_nfs_share(request, nfs_share)
    return response.model_dump(by_alias=True)


@router.get("/instances", response_model=ApiResponse, operation_id="list_nfs_share_instances")
async def list_nfs_shares(request: Request, _: str = Depends(get_current_user)):
    response = controller.list_nfs_shares(request)
    return response.model_dump(by_alias=True)


@router.get("/instances/{share_id}", response_model=ApiResponse, operation_id="get_nfs_share_instance")
async def get_nfs_share(request: Request, share_id: str, _: str = Depends(get_current_user)):
    response = controller.get_nfs_share(request, share_id)
    return response.model_dump(by_alias=True)


@router.put("/instances/{share_id}", response_model=ApiResponse, operation_id="update_nfs_share_instance")
async def update_nfs_share(
    request: Request, share_id: str, update_data: NFSShareUpdate, _: str = Depends(get_current_user)
):
    response = controller.update_nfs_share(request, share_id, update_data)
    return response.model_dump(by_alias=True)


@router.delete("/instances/{share_id}", response_model=ApiResponse, operation_id="delete_nfs_share_instance")
async def delete_nfs_share(request: Request, share_id: str, _: str = Depends(get_current_user)):
    success = controller.delete_nfs_share(request, share_id)
    if not success:
        raise HTTPException(status_code=404, detail="NFS share not found")
    formatter = UnityResponseFormatter(request)
    response = formatter.format_collection([], entry_links={})
    return response.model_dump(by_alias=True)
