from datetime import datetime
from typing import Dict, List, Union
from uuid import uuid4

from fastapi import HTTPException

from dell_unisphere_mock_api.core.response_models import ApiResponse, Entry, Link
from dell_unisphere_mock_api.models.quota import (
    QuotaConfig,
    QuotaConfigCreate,
    QuotaConfigUpdate,
    TreeQuota,
    TreeQuotaCreate,
    TreeQuotaUpdate,
    UserQuota,
    UserQuotaCreate,
    UserQuotaUpdate,
)


class QuotaController:
    def __init__(self):
        self.quota_configs: Dict[str, QuotaConfig] = {}
        self.tree_quotas: Dict[str, TreeQuota] = {}
        self.user_quotas: Dict[str, UserQuota] = {}

    def _create_api_response(self, entries: List[Entry], request) -> ApiResponse:
        """Create standardized API response"""
        return ApiResponse(
            **{
                "@base": f"{request.base_url}{request.url.path}",
                "updated": datetime.utcnow(),
                "links": [Link(rel="self", href=request.url.path)],
                "entries": entries,
            }
        )

    def _create_entry(self, resource: Union[QuotaConfig, TreeQuota, UserQuota], request, resource_type: str) -> Entry:
        """Create standardized entry"""
        return Entry(
            **{
                "@base": "storageObject",
                "content": resource,
                "updated": datetime.utcnow(),
                "links": [
                    Link(rel="self", href=f"/{resource.id}"),
                    Link(rel="filesystem", href=f"/api/instances/filesystem/{resource.filesystem_id}"),
                ],
            }
        )

    # Quota Config methods
    def create_quota_config(self, config: QuotaConfigCreate, request) -> ApiResponse:
        """Create a new quota configuration"""
        config_id = str(uuid4())
        new_config = QuotaConfig(**{**config.dict(), "id": config_id})
        self.quota_configs[config_id] = new_config
        return self._create_api_response([self._create_entry(new_config, request, "quota_config")], request)

    def get_quota_config(self, config_id: str, request) -> ApiResponse:
        """Get a quota configuration by ID"""
        config = self.quota_configs.get(config_id)
        if not config:
            raise HTTPException(status_code=404, detail=f"Quota config {config_id} not found")
        return self._create_api_response([self._create_entry(config, request, "quota_config")], request)

    def list_quota_configs(self, request) -> ApiResponse:
        """List all quota configurations"""
        entries = [self._create_entry(config, request, "quota_config") for config in self.quota_configs.values()]
        return self._create_api_response(entries, request)

    def update_quota_config(self, config_id: str, update_data: QuotaConfigUpdate, request) -> ApiResponse:
        """Update a quota configuration"""
        if config_id not in self.quota_configs:
            raise HTTPException(status_code=404, detail=f"Quota config {config_id} not found")

        config = self.quota_configs[config_id]
        update_dict = update_data.dict(exclude_unset=True)
        updated_config = QuotaConfig(**{**config.dict(), **update_dict})
        self.quota_configs[config_id] = updated_config
        return self._create_api_response([self._create_entry(updated_config, request, "quota_config")], request)

    def delete_quota_config(self, config_id: str, request) -> None:
        """Delete a quota configuration"""
        if config_id not in self.quota_configs:
            raise HTTPException(status_code=404, detail=f"Quota config {config_id} not found")
        del self.quota_configs[config_id]

    # Tree Quota methods
    def create_tree_quota(self, quota: TreeQuotaCreate, request) -> ApiResponse:
        """Create a new tree quota"""
        quota_id = str(uuid4())
        new_quota = TreeQuota(**{**quota.dict(), "id": quota_id})
        self.tree_quotas[quota_id] = new_quota
        return self._create_api_response([self._create_entry(new_quota, request, "tree_quota")], request)

    def get_tree_quota(self, quota_id: str, request) -> ApiResponse:
        """Get a tree quota by ID"""
        quota = self.tree_quotas.get(quota_id)
        if not quota:
            raise HTTPException(status_code=404, detail=f"Tree quota {quota_id} not found")
        return self._create_api_response([self._create_entry(quota, request, "tree_quota")], request)

    def list_tree_quotas(self, request) -> ApiResponse:
        """List all tree quotas"""
        entries = [self._create_entry(quota, request, "tree_quota") for quota in self.tree_quotas.values()]
        return self._create_api_response(entries, request)

    def update_tree_quota(self, quota_id: str, update_data: TreeQuotaUpdate, request) -> ApiResponse:
        """Update a tree quota"""
        if quota_id not in self.tree_quotas:
            raise HTTPException(status_code=404, detail=f"Tree quota {quota_id} not found")

        quota = self.tree_quotas[quota_id]
        update_dict = update_data.dict(exclude_unset=True)
        updated_quota = TreeQuota(**{**quota.dict(), **update_dict})
        self.tree_quotas[quota_id] = updated_quota
        return self._create_api_response([self._create_entry(updated_quota, request, "tree_quota")], request)

    def delete_tree_quota(self, quota_id: str, request) -> None:
        """Delete a tree quota"""
        if quota_id not in self.tree_quotas:
            raise HTTPException(status_code=404, detail=f"Tree quota {quota_id} not found")
        del self.tree_quotas[quota_id]

    # User Quota methods
    def create_user_quota(self, quota: UserQuotaCreate, request) -> ApiResponse:
        """Create a new user quota"""
        quota_id = str(uuid4())
        new_quota = UserQuota(**{**quota.dict(), "id": quota_id})
        self.user_quotas[quota_id] = new_quota
        return self._create_api_response([self._create_entry(new_quota, request, "user_quota")], request)

    def get_user_quota(self, quota_id: str, request) -> ApiResponse:
        """Get a user quota by ID"""
        quota = self.user_quotas.get(quota_id)
        if not quota:
            raise HTTPException(status_code=404, detail=f"User quota {quota_id} not found")
        return self._create_api_response([self._create_entry(quota, request, "user_quota")], request)

    def list_user_quotas(self, request) -> ApiResponse:
        """List all user quotas"""
        entries = [self._create_entry(quota, request, "user_quota") for quota in self.user_quotas.values()]
        return self._create_api_response(entries, request)

    def update_user_quota(self, quota_id: str, update_data: UserQuotaUpdate, request) -> ApiResponse:
        """Update a user quota"""
        if quota_id not in self.user_quotas:
            raise HTTPException(status_code=404, detail=f"User quota {quota_id} not found")

        quota = self.user_quotas[quota_id]
        update_dict = update_data.dict(exclude_unset=True)
        updated_quota = UserQuota(**{**quota.dict(), **update_dict})
        self.user_quotas[quota_id] = updated_quota
        return self._create_api_response([self._create_entry(updated_quota, request, "user_quota")], request)

    def delete_user_quota(self, quota_id: str, request) -> None:
        """Delete a user quota"""
        if quota_id not in self.user_quotas:
            raise HTTPException(status_code=404, detail=f"User quota {quota_id} not found")
        del self.user_quotas[quota_id]
