from fastapi import APIRouter

from dell_unisphere_mock_api.controllers.system_info import SystemInfoController

router = APIRouter()
controller = SystemInfoController()


@router.get("/types/basicSystemInfo/instances")
async def get_basic_system_info_collection():
    return controller.get_collection()


@router.get("/instances/basicSystemInfo/{id}")
async def get_basic_system_info_by_id(id: str):
    return controller.get_by_id(id)


@router.get("/instances/basicSystemInfo/name/{name}")
async def get_basic_system_info_by_name(name: str):
    # Remove URL encoding from the name parameter
    return controller.get_by_name(name)
