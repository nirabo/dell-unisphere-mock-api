from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from dell_unisphere_mock_api.controllers.acl_user_controller import ACLUserController
from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.models.acl_user import ACLUser, ACLUserCreate, ACLUserUpdate

router = APIRouter(prefix="/types/aclUser", tags=["ACL User"])
controller = ACLUserController()


@router.post("/instances", response_model=ApiResponse)
async def create_acl_user(user: ACLUserCreate, request: Request, _: str = Depends(get_current_user)):
    return await controller.create_user(request, user)


@router.get("/instances", response_model=ApiResponse)
async def list_acl_users(request: Request, _: str = Depends(get_current_user)):
    return await controller.list_users(request)


@router.get("/instances/{user_id}", response_model=ApiResponse)
async def get_acl_user(user_id: str, request: Request, _: str = Depends(get_current_user)):
    return await controller.get_user(request, user_id)


@router.patch("/instances/{user_id}", response_model=ApiResponse)
async def update_acl_user(
    user_id: str, update_data: ACLUserUpdate, request: Request, _: str = Depends(get_current_user)
):
    return await controller.update_user(request, user_id, update_data)


@router.get("/action/lookupSIDByDomainUser", response_model=ApiResponse)
async def lookup_sid_by_domain_user(
    domain_name: str = Query(..., description="Windows domain name"),
    user_name: str = Query(..., description="User name"),
    request: Request = None,
    _: str = Depends(get_current_user),
):
    return await controller.lookup_sid_by_domain_user(request, domain_name, user_name)
