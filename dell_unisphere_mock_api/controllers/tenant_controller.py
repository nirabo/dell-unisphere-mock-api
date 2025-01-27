from datetime import datetime
from typing import Dict, List
from uuid import uuid4

from fastapi import HTTPException, Request

from dell_unisphere_mock_api.core.response_models import ApiResponse, Entry, Link
from dell_unisphere_mock_api.models.tenant import Tenant, TenantCreate, TenantUpdate


class TenantController:
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self.name_to_id: Dict[str, str] = {}

    def _create_api_response(self, entries: List[Entry], request: Request) -> ApiResponse:
        """Create standardized API response"""
        base_url = str(request.base_url).rstrip("/")
        return ApiResponse(
            **{
                "@base": f"{base_url}/api/types/tenant/instances",
                "updated": datetime.utcnow(),
                "links": [Link(rel="self", href=f"{base_url}/api/types/tenant/instances")],
                "entries": entries,
            }
        )

    def _create_entry(self, tenant: Tenant, request: Request) -> Entry:
        """Create standardized entry"""
        base_url = str(request.base_url).rstrip("/")
        return Entry(
            **{
                "@base": "storageObject",
                "content": tenant,
                "updated": datetime.utcnow(),
                "links": [Link(rel="self", href=f"{base_url}/api/instances/tenant/{tenant.id}")],
            }
        )

    async def create_tenant(self, request: Request, tenant: TenantCreate) -> ApiResponse:
        """Create a new tenant"""
        try:
            tenant_id = str(uuid4())
            new_tenant = Tenant(**{**tenant.model_dump(), "id": tenant_id})
            self.tenants[tenant_id] = new_tenant
            self.name_to_id[new_tenant.name] = tenant_id
            return self._create_api_response([self._create_entry(new_tenant, request)], request)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_tenant(self, request: Request, tenant_id: str) -> ApiResponse:
        """Get a tenant by ID"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return self._create_api_response([self._create_entry(tenant, request)], request)

    async def get_tenant_by_name(self, request: Request, name: str) -> ApiResponse:
        """Get a tenant by name"""
        tenant_id = self.name_to_id.get(name)
        if not tenant_id:
            raise HTTPException(status_code=404, detail="Tenant not found")
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return self._create_api_response([self._create_entry(tenant, request)], request)

    async def list_tenants(self, request: Request) -> ApiResponse:
        """List all tenants"""
        entries = [self._create_entry(tenant, request) for tenant in self.tenants.values()]
        return self._create_api_response(entries, request)

    async def update_tenant(self, request: Request, tenant_id: str, update_data: TenantUpdate) -> ApiResponse:
        """Update a tenant"""
        if tenant_id not in self.tenants:
            raise HTTPException(status_code=404, detail="Tenant not found")

        tenant = self.tenants[tenant_id]
        update_dict = update_data.model_dump(exclude_unset=True)

        # Handle name change in name_to_id mapping
        if "name" in update_dict and update_dict["name"] != tenant.name:
            del self.name_to_id[tenant.name]
            self.name_to_id[update_dict["name"]] = tenant_id

        updated_tenant = Tenant(**{**tenant.model_dump(), **update_dict})
        self.tenants[tenant_id] = updated_tenant
        return self._create_api_response([self._create_entry(updated_tenant, request)], request)

    async def delete_tenant(self, request: Request, tenant_id: str) -> ApiResponse:
        """Delete a tenant"""
        if tenant_id not in self.tenants:
            raise HTTPException(status_code=404, detail="Tenant not found")

        tenant = self.tenants[tenant_id]
        del self.name_to_id[tenant.name]
        del self.tenants[tenant_id]
        return self._create_api_response([], request)
