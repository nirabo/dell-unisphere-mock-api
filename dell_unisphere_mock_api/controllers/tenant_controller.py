from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from dell_unisphere_mock_api.core.response_models import ApiResponse, Entry, Link
from dell_unisphere_mock_api.models.tenant import Tenant, TenantCreate, TenantUpdate


class TenantController:
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self.name_to_id: Dict[str, str] = {}

    def _create_api_response(self, entries: List[Entry], request_path: str) -> ApiResponse:
        """Create standardized API response"""
        base_url = "https://127.0.0.1:8000"
        return ApiResponse(
            **{
                "@base": f"{base_url}/api/types/tenant/instances",
                "updated": datetime.utcnow(),
                "links": [Link(rel="self", href=f"{base_url}/api/types/tenant/instances")],
                "entries": entries,
            }
        )

    def _create_entry(self, tenant: Tenant, base_url: str) -> Entry:
        """Create standardized entry"""
        return Entry(
            **{
                "@base": "storageObject",
                "content": tenant,
                "updated": datetime.utcnow(),
                "links": [Link(rel="self", href=f"{base_url}/api/instances/tenant/{tenant.id}")],
            }
        )

    def create_tenant(self, tenant: TenantCreate) -> Tenant:
        """Create a new tenant"""
        tenant_id = str(uuid4())
        new_tenant = Tenant(**{**tenant.dict(), "id": tenant_id})
        self.tenants[tenant_id] = new_tenant
        self.name_to_id[new_tenant.name] = tenant_id
        return new_tenant

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get a tenant by ID"""
        return self.tenants.get(tenant_id)

    def get_tenant_by_name(self, name: str) -> Optional[Tenant]:
        """Get a tenant by name"""
        tenant_id = self.name_to_id.get(name)
        return self.tenants.get(tenant_id) if tenant_id else None

    def list_tenants(self) -> List[Tenant]:
        """List all tenants"""
        return list(self.tenants.values())

    def update_tenant(self, tenant_id: str, update_data: TenantUpdate) -> Optional[Tenant]:
        """Update a tenant"""
        if tenant_id not in self.tenants:
            return None

        tenant = self.tenants[tenant_id]
        update_dict = update_data.dict(exclude_unset=True)

        # Handle name change in name_to_id mapping
        if "name" in update_dict and update_dict["name"] != tenant.name:
            del self.name_to_id[tenant.name]
            self.name_to_id[update_dict["name"]] = tenant_id

        updated_tenant = Tenant(**{**tenant.dict(), **update_dict})
        self.tenants[tenant_id] = updated_tenant
        return updated_tenant

    def delete_tenant(self, tenant_id: str) -> bool:
        """Delete a tenant"""
        if tenant_id not in self.tenants:
            return False

        tenant = self.tenants[tenant_id]
        del self.name_to_id[tenant.name]
        del self.tenants[tenant_id]
        return True
