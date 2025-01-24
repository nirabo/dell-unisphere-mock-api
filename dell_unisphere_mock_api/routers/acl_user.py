from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from dell_unisphere_mock_api.controllers.acl_user_controller import ACLUserController
from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.models.acl_user import ACLUser, ACLUserCreate, ACLUserUpdate

router = APIRouter(prefix="/types/aclUser", tags=["ACL User"])
controller = ACLUserController()


@router.post("/instances", response_model=ApiResponse)
async def create_acl_user(user: ACLUserCreate, _: str = Depends(get_current_user)):
    new_user = controller.create_user(user)
    entry = controller._create_entry(new_user, "https://127.0.0.1:8000")
    return controller._create_api_response([entry], "/types/aclUser/instances")


@router.get("/instances", response_model=ApiResponse)
async def list_acl_users(_: str = Depends(get_current_user)):
    users = controller.list_users()
    entries = [controller._create_entry(user, "https://127.0.0.1:8000") for user in users]
    return controller._create_api_response(entries, "/types/aclUser/instances")


@router.get("/instances/{user_id}", response_model=ApiResponse)
async def get_acl_user(user_id: str, _: str = Depends(get_current_user)):
    user = controller.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="ACL user not found")
    entry = controller._create_entry(user, "https://127.0.0.1:8000")
    return controller._create_api_response([entry], f"/types/aclUser/instances/{user_id}")


@router.patch("/instances/{user_id}", response_model=ApiResponse)
async def update_acl_user(user_id: str, update_data: ACLUserUpdate, _: str = Depends(get_current_user)):
    updated_user = controller.update_user(user_id, update_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="ACL user not found")
    entry = controller._create_entry(updated_user, "https://127.0.0.1:8000")
    return controller._create_api_response([entry], f"/types/aclUser/instances/{user_id}")


@router.get("/action/lookupSIDByDomainUser", response_model=ApiResponse)
async def lookup_sid_by_domain_user(
    domain_name: str = Query(..., description="Windows domain name"),
    user_name: str = Query(..., description="User name"),
    _: str = Depends(get_current_user),
):
    result = controller.lookup_sid_by_domain_user(domain_name, user_name)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    sid, user = result
    entry = controller._create_entry(user, "https://127.0.0.1:8000")
    return controller._create_api_response([entry], "/types/aclUser/action/lookupSIDByDomainUser")
