from typing import List

from fastapi import APIRouter, Depends, HTTPException

from dell_unisphere_mock_api.controllers.nfs_share_controller import NFSShareController
from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.models.nfs_share import NFSShare, NFSShareCreate, NFSShareUpdate

router = APIRouter(prefix="/types/nfsShare", tags=["NFS Share"])
controller = NFSShareController()


@router.post("/instances", response_model=ApiResponse)
async def create_nfs_share(nfs_share: NFSShareCreate, _: str = Depends(get_current_user)):
    new_share = controller.create_nfs_share(nfs_share)
    entry = controller._create_entry(new_share, "https://127.0.0.1:8000")
    return controller._create_api_response([entry], "/types/nfsShare/instances")


@router.get("/instances", response_model=ApiResponse)
async def list_nfs_shares(_: str = Depends(get_current_user)):
    shares = controller.list_nfs_shares()
    entries = [controller._create_entry(share, "https://127.0.0.1:8000") for share in shares]
    return controller._create_api_response(entries, "/types/nfsShare/instances")


@router.get("/instances/{share_id}", response_model=ApiResponse)
async def get_nfs_share(share_id: str, _: str = Depends(get_current_user)):
    share = controller.get_nfs_share(share_id)
    if not share:
        raise HTTPException(status_code=404, detail="NFS share not found")
    entry = controller._create_entry(share, "https://127.0.0.1:8000")
    return controller._create_api_response([entry], f"/types/nfsShare/instances/{share_id}")


@router.patch("/instances/{share_id}", response_model=ApiResponse)
async def update_nfs_share(share_id: str, update_data: NFSShareUpdate, _: str = Depends(get_current_user)):
    updated_share = controller.update_nfs_share(share_id, update_data)
    if not updated_share:
        raise HTTPException(status_code=404, detail="NFS share not found")
    entry = controller._create_entry(updated_share, "https://127.0.0.1:8000")
    return controller._create_api_response([entry], f"/types/nfsShare/instances/{share_id}")


@router.delete("/instances/{share_id}", response_model=ApiResponse)
async def delete_nfs_share(share_id: str, _: str = Depends(get_current_user)):
    success = controller.delete_nfs_share(share_id)
    if not success:
        raise HTTPException(status_code=404, detail="NFS share not found")
    return controller._create_api_response([], f"/types/nfsShare/instances/{share_id}")
