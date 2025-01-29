from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from dell_unisphere_mock_api.controllers.lun_controller import LUNController
from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.schemas.lun import LUN, LUNCreate, LUNUpdate

router = APIRouter()

lun_controller = LUNController()


@router.post("/types/lun/instances", status_code=201)
async def create_lun(request: Request, lun: LUNCreate, _: dict = Depends(get_current_user)) -> ApiResponse[LUN]:
    """Create a new LUN."""
    return await lun_controller.create_lun(lun, request)


@router.get("/instances/lun/name:{name}")
async def get_lun_by_name(request: Request, name: str, _: dict = Depends(get_current_user)) -> ApiResponse[LUN]:
    """Get a LUN by name."""
    return await lun_controller.get_lun_by_name(name, request)


@router.get("/instances/lun/{lun_id}")
async def get_lun(request: Request, lun_id: str, _: dict = Depends(get_current_user)) -> ApiResponse[LUN]:
    """Get a LUN by ID."""
    return await lun_controller.get_lun(lun_id, request)


@router.get("/types/lun/instances")
async def list_luns(request: Request, _: dict = Depends(get_current_user)) -> ApiResponse[List[LUN]]:
    """List all LUNs."""
    return await lun_controller.list_luns(request)


@router.patch("/instances/lun/{lun_id}")
async def modify_lun(
    request: Request, lun_id: str, lun_update: LUNUpdate, _: dict = Depends(get_current_user)
) -> ApiResponse[LUN]:
    """Modify a LUN."""
    return await lun_controller.update_lun(lun_id, lun_update, request)


@router.delete("/instances/lun/name:{name}", status_code=204)
async def delete_lun_by_name(request: Request, name: str, _: dict = Depends(get_current_user)):
    """Delete a LUN by name."""
    await lun_controller.delete_lun_by_name(name, request)
    return Response(status_code=204)


@router.delete("/instances/lun/{lun_id}", status_code=204)
async def delete_lun(request: Request, lun_id: str, _: dict = Depends(get_current_user)):
    """Delete a LUN."""
    await lun_controller.delete_lun(lun_id, request)
    return Response(status_code=204)


@router.get("/types/lun/instances/byPool/{pool_id}")
async def get_luns_by_pool(
    request: Request, pool_id: str, _: dict = Depends(get_current_user)
) -> ApiResponse[List[LUN]]:
    """Get all LUNs in a pool."""
    return await lun_controller.get_luns_by_pool(pool_id, request)
