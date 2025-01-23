from fastapi import APIRouter, Request

from dell_unisphere_mock_api.controllers.system_info import SystemInfoController

router = APIRouter(prefix="")
controller = SystemInfoController()


@router.get("/types/basicSystemInfo/instances")
async def get_basic_system_info_collection(request: Request):
    """Get all basic system info instances"""
    return controller.get_collection(request)


@router.get("/instances/basicSystemInfo/{id}")
async def get_basic_system_info_by_id(id: str, request: Request):
    """Get basic system info by ID"""
    return controller.get_by_id(id, request)


@router.get("/instances/basicSystemInfo/name:{name}")
async def get_basic_system_info_by_name(name: str, request: Request):
    """Get basic system info by name"""
    return controller.get_by_name(name, request)
