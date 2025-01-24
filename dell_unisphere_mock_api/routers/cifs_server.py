from typing import List

from fastapi import APIRouter, Depends, HTTPException

from dell_unisphere_mock_api.controllers.cifs_server_controller import CIFSServerController
from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.models.cifs_server import CIFSServer, CIFSServerCreate, CIFSServerUpdate

router = APIRouter(prefix="/types/cifsServer", tags=["CIFS Server"])
controller = CIFSServerController()


@router.post("/instances", response_model=ApiResponse)
async def create_cifs_server(cifs_server: CIFSServerCreate, _: str = Depends(get_current_user)):
    new_server = controller.create_cifs_server(cifs_server)
    entry = controller._create_entry(new_server, "https://127.0.0.1:8000")
    return controller._create_api_response([entry], "/types/cifsServer/instances")


@router.get("/instances", response_model=ApiResponse)
async def list_cifs_servers(_: str = Depends(get_current_user)):
    servers = controller.list_cifs_servers()
    entries = [controller._create_entry(server, "https://127.0.0.1:8000") for server in servers]
    return controller._create_api_response(entries, "/types/cifsServer/instances")


@router.get("/instances/{server_id}", response_model=ApiResponse)
async def get_cifs_server(server_id: str, _: str = Depends(get_current_user)):
    server = controller.get_cifs_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="CIFS server not found")
    entry = controller._create_entry(server, "https://127.0.0.1:8000")
    return controller._create_api_response([entry], f"/types/cifsServer/instances/{server_id}")


@router.patch("/instances/{server_id}", response_model=ApiResponse)
async def update_cifs_server(server_id: str, update_data: CIFSServerUpdate, _: str = Depends(get_current_user)):
    updated_server = controller.update_cifs_server(server_id, update_data)
    if not updated_server:
        raise HTTPException(status_code=404, detail="CIFS server not found")
    entry = controller._create_entry(updated_server, "https://127.0.0.1:8000")
    return controller._create_api_response([entry], f"/types/cifsServer/instances/{server_id}")


@router.delete("/instances/{server_id}", response_model=ApiResponse)
async def delete_cifs_server(server_id: str, _: str = Depends(get_current_user)):
    success = controller.delete_cifs_server(server_id)
    if not success:
        raise HTTPException(status_code=404, detail="CIFS server not found")
    return controller._create_api_response([], f"/types/cifsServer/instances/{server_id}")
