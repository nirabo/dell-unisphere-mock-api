from typing import List

from fastapi import APIRouter, Depends, HTTPException

from dell_unisphere_mock_api.controllers.quota_controller import QuotaController
from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.models.quota_config import QuotaConfig, QuotaConfigCreate, QuotaConfigUpdate
from dell_unisphere_mock_api.models.tree_quota import TreeQuota, TreeQuotaCreate, TreeQuotaUpdate
from dell_unisphere_mock_api.models.user_quota import UserQuota, UserQuotaCreate, UserQuotaUpdate

router = APIRouter(prefix="/types", tags=["Quota Management"])
controller = QuotaController()


# Quota Config endpoints
@router.post("/quotaConfig/instances", response_model=ApiResponse)
async def create_quota_config(config: QuotaConfigCreate, _: str = Depends(get_current_user)):
    new_config = controller.create_quota_config(config)
    entry = controller._create_entry(new_config, "https://127.0.0.1:8000", "quotaConfig")
    return controller._create_api_response([entry], "/types/quotaConfig/instances", "quotaConfig")


@router.get("/quotaConfig/instances/{config_id}", response_model=ApiResponse)
async def get_quota_config(config_id: str, _: str = Depends(get_current_user)):
    config = controller.get_quota_config(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Quota configuration not found")
    entry = controller._create_entry(config, "https://127.0.0.1:8000", "quotaConfig")
    return controller._create_api_response([entry], f"/types/quotaConfig/instances/{config_id}", "quotaConfig")


@router.patch("/quotaConfig/instances/{config_id}", response_model=ApiResponse)
async def update_quota_config(config_id: str, update_data: QuotaConfigUpdate, _: str = Depends(get_current_user)):
    updated_config = controller.update_quota_config(config_id, update_data)
    if not updated_config:
        raise HTTPException(status_code=404, detail="Quota configuration not found")
    entry = controller._create_entry(updated_config, "https://127.0.0.1:8000", "quotaConfig")
    return controller._create_api_response([entry], f"/types/quotaConfig/instances/{config_id}", "quotaConfig")


# Tree Quota endpoints
@router.post("/treeQuota/instances", response_model=ApiResponse)
async def create_tree_quota(quota: TreeQuotaCreate, _: str = Depends(get_current_user)):
    new_quota = controller.create_tree_quota(quota)
    entry = controller._create_entry(new_quota, "https://127.0.0.1:8000", "treeQuota")
    return controller._create_api_response([entry], "/types/treeQuota/instances", "treeQuota")


@router.get("/treeQuota/instances/{quota_id}", response_model=ApiResponse)
async def get_tree_quota(quota_id: str, _: str = Depends(get_current_user)):
    quota = controller.get_tree_quota(quota_id)
    if not quota:
        raise HTTPException(status_code=404, detail="Tree quota not found")
    entry = controller._create_entry(quota, "https://127.0.0.1:8000", "treeQuota")
    return controller._create_api_response([entry], f"/types/treeQuota/instances/{quota_id}", "treeQuota")


@router.patch("/treeQuota/instances/{quota_id}", response_model=ApiResponse)
async def update_tree_quota(quota_id: str, update_data: TreeQuotaUpdate, _: str = Depends(get_current_user)):
    updated_quota = controller.update_tree_quota(quota_id, update_data)
    if not updated_quota:
        raise HTTPException(status_code=404, detail="Tree quota not found")
    entry = controller._create_entry(updated_quota, "https://127.0.0.1:8000", "treeQuota")
    return controller._create_api_response([entry], f"/types/treeQuota/instances/{quota_id}", "treeQuota")


@router.delete("/treeQuota/instances/{quota_id}", response_model=ApiResponse)
async def delete_tree_quota(quota_id: str, _: str = Depends(get_current_user)):
    success = controller.delete_tree_quota(quota_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tree quota not found")
    return controller._create_api_response([], f"/types/treeQuota/instances/{quota_id}", "treeQuota")


# User Quota endpoints
@router.post("/userQuota/instances", response_model=ApiResponse)
async def create_user_quota(quota: UserQuotaCreate, _: str = Depends(get_current_user)):
    new_quota = controller.create_user_quota(quota)
    entry = controller._create_entry(new_quota, "https://127.0.0.1:8000", "userQuota")
    return controller._create_api_response([entry], "/types/userQuota/instances", "userQuota")


@router.get("/userQuota/instances/{quota_id}", response_model=ApiResponse)
async def get_user_quota(quota_id: str, _: str = Depends(get_current_user)):
    quota = controller.get_user_quota(quota_id)
    if not quota:
        raise HTTPException(status_code=404, detail="User quota not found")
    entry = controller._create_entry(quota, "https://127.0.0.1:8000", "userQuota")
    return controller._create_api_response([entry], f"/types/userQuota/instances/{quota_id}", "userQuota")


@router.patch("/userQuota/instances/{quota_id}", response_model=ApiResponse)
async def update_user_quota(quota_id: str, update_data: UserQuotaUpdate, _: str = Depends(get_current_user)):
    updated_quota = controller.update_user_quota(quota_id, update_data)
    if not updated_quota:
        raise HTTPException(status_code=404, detail="User quota not found")
    entry = controller._create_entry(updated_quota, "https://127.0.0.1:8000", "userQuota")
    return controller._create_api_response([entry], f"/types/userQuota/instances/{quota_id}", "userQuota")


@router.delete("/userQuota/instances/{quota_id}", response_model=ApiResponse)
async def delete_user_quota(quota_id: str, _: str = Depends(get_current_user)):
    success = controller.delete_user_quota(quota_id)
    if not success:
        raise HTTPException(status_code=404, detail="User quota not found")
    return controller._create_api_response([], f"/types/userQuota/instances/{quota_id}", "userQuota")
