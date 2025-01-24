from datetime import datetime
from typing import Dict, List, Optional, Union
from uuid import uuid4

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

    def _create_api_response(self, entries: List[Entry], request_path: str, resource_type: str) -> ApiResponse:
        """Create standardized API response"""
        base_url = "https://127.0.0.1:8000"  # This should come from configuration
        return ApiResponse(
            **{
                "@base": f"{base_url}/api/types/{resource_type}/instances",
                "updated": datetime.utcnow(),
                "links": [Link(rel="self", href=f"{base_url}/api/types/{resource_type}/instances")],
                "entries": entries,
            }
        )

    def _create_entry(
        self, resource: Union[QuotaConfig, TreeQuota, UserQuota], base_url: str, resource_type: str
    ) -> Entry:
        """Create standardized entry"""
        return Entry(
            **{
                "@base": "storageObject",
                "content": resource,
                "updated": datetime.utcnow(),
                "links": [
                    Link(rel="self", href=f"{base_url}/api/instances/{resource_type}/{resource.id}"),
                    Link(rel="filesystem", href=f"{base_url}/api/instances/filesystem/{resource.filesystem_id}"),
                ],
            }
        )

    # Quota Config methods
    def create_quota_config(self, config: QuotaConfigCreate) -> QuotaConfig:
        """Create a new quota configuration"""
        config_id = str(uuid4())
        new_config = QuotaConfig(**{**config.dict(), "id": config_id})
        self.quota_configs[config_id] = new_config
        return new_config

    def get_quota_config(self, config_id: str) -> Optional[QuotaConfig]:
        """Get a quota configuration by ID"""
        return self.quota_configs.get(config_id)

    def list_quota_configs(self) -> List[QuotaConfig]:
        """List all quota configurations"""
        return list(self.quota_configs.values())

    def update_quota_config(self, config_id: str, update_data: QuotaConfigUpdate) -> Optional[QuotaConfig]:
        """Update a quota configuration"""
        if config_id not in self.quota_configs:
            return None

        config = self.quota_configs[config_id]
        update_dict = update_data.dict(exclude_unset=True)
        updated_config = QuotaConfig(**{**config.dict(), **update_dict})
        self.quota_configs[config_id] = updated_config
        return updated_config

    def delete_quota_config(self, config_id: str) -> bool:
        """Delete a quota configuration"""
        if config_id not in self.quota_configs:
            return False
        del self.quota_configs[config_id]
        return True

    # Tree Quota methods
    def create_tree_quota(self, quota: TreeQuotaCreate) -> TreeQuota:
        """Create a new tree quota"""
        quota_id = str(uuid4())
        new_quota = TreeQuota(**{**quota.dict(), "id": quota_id})
        self.tree_quotas[quota_id] = new_quota
        return new_quota

    def get_tree_quota(self, quota_id: str) -> Optional[TreeQuota]:
        """Get a tree quota by ID"""
        return self.tree_quotas.get(quota_id)

    def list_tree_quotas(self) -> List[TreeQuota]:
        """List all tree quotas"""
        return list(self.tree_quotas.values())

    def update_tree_quota(self, quota_id: str, update_data: TreeQuotaUpdate) -> Optional[TreeQuota]:
        """Update a tree quota"""
        if quota_id not in self.tree_quotas:
            return None

        quota = self.tree_quotas[quota_id]
        update_dict = update_data.dict(exclude_unset=True)
        updated_quota = TreeQuota(**{**quota.dict(), **update_dict})
        self.tree_quotas[quota_id] = updated_quota
        return updated_quota

    def delete_tree_quota(self, quota_id: str) -> bool:
        """Delete a tree quota"""
        if quota_id not in self.tree_quotas:
            return False
        del self.tree_quotas[quota_id]
        return True

    # User Quota methods
    def create_user_quota(self, quota: UserQuotaCreate) -> UserQuota:
        """Create a new user quota"""
        quota_id = str(uuid4())
        new_quota = UserQuota(**{**quota.dict(), "id": quota_id})
        self.user_quotas[quota_id] = new_quota
        return new_quota

    def get_user_quota(self, quota_id: str) -> Optional[UserQuota]:
        """Get a user quota by ID"""
        return self.user_quotas.get(quota_id)

    def list_user_quotas(self) -> List[UserQuota]:
        """List all user quotas"""
        return list(self.user_quotas.values())

    def update_user_quota(self, quota_id: str, update_data: UserQuotaUpdate) -> Optional[UserQuota]:
        """Update a user quota"""
        if quota_id not in self.user_quotas:
            return None

        quota = self.user_quotas[quota_id]
        update_dict = update_data.dict(exclude_unset=True)
        updated_quota = UserQuota(**{**quota.dict(), **update_dict})
        self.user_quotas[quota_id] = updated_quota
        return updated_quota

    def delete_user_quota(self, quota_id: str) -> bool:
        """Delete a user quota"""
        if quota_id not in self.user_quotas:
            return False
        del self.user_quotas[quota_id]
        return True
