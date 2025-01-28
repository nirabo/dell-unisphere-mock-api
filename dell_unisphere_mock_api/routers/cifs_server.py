from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request

from dell_unisphere_mock_api.controllers.cifs_server_controller import CIFSServerController
from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.models.cifs_server import CIFSServer, CIFSServerCreate, CIFSServerUpdate

router = APIRouter(prefix="/types/cifsServer", tags=["CIFS Server"])
controller = CIFSServerController()


@router.post("/instances", response_model=ApiResponse)
async def create_cifs_server(request: Request, cifs_server: CIFSServerCreate, _: str = Depends(get_current_user)):
    return controller.create_cifs_server(request, cifs_server)


@router.get("/instances", response_model=ApiResponse)
async def list_cifs_servers(request: Request, _: str = Depends(get_current_user)):
    return controller.list_cifs_servers(request)


@router.get("/instances/{server_id}", response_model=ApiResponse)
async def get_cifs_server(request: Request, server_id: str, _: str = Depends(get_current_user)):
    return controller.get_cifs_server(request, server_id)


@router.patch("/instances/{server_id}", response_model=ApiResponse)
async def update_cifs_server(
    request: Request, server_id: str, update_data: CIFSServerUpdate, _: str = Depends(get_current_user)
):
    return controller.update_cifs_server(request, server_id, update_data)


@router.delete("/instances/{server_id}", response_model=ApiResponse)
async def delete_cifs_server(request: Request, server_id: str, _: str = Depends(get_current_user)):
    return controller.delete_cifs_server(request, server_id)
