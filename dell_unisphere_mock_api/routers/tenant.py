from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from dell_unisphere_mock_api.controllers.tenant_controller import TenantController
from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.models.tenant import TenantCreate, TenantUpdate

router = APIRouter(prefix="/types/tenant", tags=["Tenant"])
controller = TenantController()


@router.post("/instances", response_model=ApiResponse, status_code=201)
async def create_tenant(tenant: TenantCreate, _: str = Depends(get_current_user)):
    new_tenant = controller.create_tenant(tenant)
    entry = controller._create_entry(new_tenant, "https://127.0.0.1:8000")
    return controller._create_api_response([entry], "/types/tenant/instances")


@router.get("/instances", response_model=ApiResponse)
async def list_tenants(_: str = Depends(get_current_user)):
    tenants = controller.list_tenants()
    entries = [controller._create_entry(tenant, "https://127.0.0.1:8000") for tenant in tenants]
    return controller._create_api_response(entries, "/types/tenant/instances")


@router.get("/instances/{tenant_id}", response_model=ApiResponse)
async def get_tenant(
    tenant_id: str = Path(..., description="Unique identifier of the tenant instance"),
    _: str = Depends(get_current_user),
):
    tenant = controller.get_tenant(tenant_id)
    if not tenant:
        error_response = controller._create_api_response([], f"/types/tenant/instances/{tenant_id}")
        error_response["error"] = {"messages": ["Tenant not found"], "httpStatusCode": 404}
        raise HTTPException(status_code=404, detail=error_response)
    entry = controller._create_entry(tenant, "https://127.0.0.1:8000")
    return controller._create_api_response([entry], f"/types/tenant/instances/{tenant_id}")


@router.get("/instances/name:{tenant_name}", response_model=ApiResponse)
async def get_tenant_by_name(
    tenant_name: str = Path(..., description="Name of the tenant instance"),
    _: str = Depends(get_current_user),
):
    tenant = controller.get_tenant_by_name(tenant_name)
    if not tenant:
        error_response = controller._create_api_response([], f"/types/tenant/instances/name:{tenant_name}")
        error_response["error"] = {"messages": ["Tenant not found"], "httpStatusCode": 404}
        raise HTTPException(status_code=404, detail=error_response)
    entry = controller._create_entry(tenant, "https://127.0.0.1:8000")
    return controller._create_api_response([entry], f"/types/tenant/instances/name:{tenant_name}")


@router.post("/instances/{tenant_id}/action/modify", status_code=204)
async def modify_tenant(
    tenant_id: str = Path(..., description="Unique identifier of the tenant instance"),
    update_data: TenantUpdate = None,
    _: str = Depends(get_current_user),
):
    updated_tenant = controller.update_tenant(tenant_id, update_data)
    if not updated_tenant:
        error_response = controller._create_api_response([], f"/types/tenant/instances/{tenant_id}/action/modify")
        error_response["error"] = {"messages": ["Tenant not found"], "httpStatusCode": 404}
        raise HTTPException(status_code=404, detail=error_response)
    return None


@router.post("/instances/name:{tenant_name}/action/modify", status_code=204)
async def modify_tenant_by_name(
    tenant_name: str = Path(..., description="Name of the tenant instance"),
    update_data: TenantUpdate = None,
    _: str = Depends(get_current_user),
):
    tenant = controller.get_tenant_by_name(tenant_name)
    if not tenant:
        error_response = controller._create_api_response(
            [], f"/types/tenant/instances/name:{tenant_name}/action/modify"
        )
        error_response["error"] = {"messages": ["Tenant not found"], "httpStatusCode": 404}
        raise HTTPException(status_code=404, detail=error_response)
    updated_tenant = controller.update_tenant(tenant.id, update_data)
    if not updated_tenant:
        error_response = controller._create_api_response(
            [], f"/types/tenant/instances/name:{tenant_name}/action/modify"
        )
        error_response["error"] = {"messages": ["Failed to update tenant"], "httpStatusCode": 404}
        raise HTTPException(status_code=404, detail=error_response)
    return None


@router.delete("/instances/{tenant_id}", status_code=200)
async def delete_tenant(
    tenant_id: str = Path(..., description="Unique identifier of the tenant instance"),
    _: str = Depends(get_current_user),
):
    success = controller.delete_tenant(tenant_id)
    if not success:
        error_response = controller._create_api_response([], f"/types/tenant/instances/{tenant_id}")
        error_response["error"] = {"messages": ["Tenant not found"], "httpStatusCode": 404}
        raise HTTPException(status_code=404, detail=error_response)
    return controller._create_api_response([], f"/types/tenant/instances/{tenant_id}")


@router.delete("/instances/name:{tenant_name}", status_code=200)
async def delete_tenant_by_name(
    tenant_name: str = Path(..., description="Name of the tenant instance"),
    _: str = Depends(get_current_user),
):
    tenant = controller.get_tenant_by_name(tenant_name)
    if not tenant:
        error_response = controller._create_api_response([], f"/types/tenant/instances/name:{tenant_name}")
        error_response["error"] = {"messages": ["Tenant not found"], "httpStatusCode": 404}
        raise HTTPException(status_code=404, detail=error_response)
    success = controller.delete_tenant(tenant.id)
    if not success:
        error_response = controller._create_api_response([], f"/types/tenant/instances/name:{tenant_name}")
        error_response["error"] = {"messages": ["Failed to delete tenant"], "httpStatusCode": 404}
        raise HTTPException(status_code=404, detail=error_response)
    return controller._create_api_response([], f"/types/tenant/instances/name:{tenant_name}")
