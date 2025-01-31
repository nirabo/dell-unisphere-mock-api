"""Schema definitions for Quota resources."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class QuotaConfigSchema(BaseModel):
    """Base schema for Quota Configuration."""

    id: str = Field(..., description="Unique identifier for the quota configuration")
    filesystem_id: str = Field(..., description="ID of the filesystem this quota config belongs to")
    is_user_quotas_enabled: bool = Field(default=False, description="Whether user quotas are enabled")
    is_tree_quotas_enabled: bool = Field(default=False, description="Whether tree quotas are enabled")
    default_hard_limit: Optional[int] = Field(None, description="Default hard limit in bytes")
    default_soft_limit: Optional[int] = Field(None, description="Default soft limit in bytes")
    grace_period: int = Field(default=604800, description="Grace period in seconds (default 7 days)")
    state: str = Field(default="READY", description="Operational state of the quota configuration")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "QuotaConfig_1",
                "filesystem_id": "fs_1",
                "is_user_quotas_enabled": True,
                "is_tree_quotas_enabled": True,
                "default_hard_limit": 1073741824,  # 1GB
                "default_soft_limit": 858993459,  # 800MB
                "grace_period": 604800,
                "state": "READY",
            }
        }
    )


class TreeQuotaSchema(BaseModel):
    """Base schema for Tree Quota."""

    id: str = Field(..., description="Unique identifier for the tree quota")
    filesystem_id: str = Field(..., description="ID of the filesystem this tree quota belongs to")
    path: str = Field(..., description="Path to the directory where quota is applied")
    description: Optional[str] = Field(None, description="Description of the tree quota")
    hard_limit: Optional[int] = Field(None, description="Hard limit in bytes")
    soft_limit: Optional[int] = Field(None, description="Soft limit in bytes")
    remaining_grace_period: Optional[int] = Field(None, description="Remaining grace period in seconds")
    state: str = Field(default="OK", description="State of the tree quota")
    size_used: int = Field(default=0, description="Current size used in bytes")
    percent_used: float = Field(default=0.0, description="Percentage of quota used")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "TreeQuota_1",
                "filesystem_id": "fs_1",
                "path": "/shared/projects",
                "description": "Project directory quota",
                "hard_limit": 5368709120,  # 5GB
                "soft_limit": 4294967296,  # 4GB
                "remaining_grace_period": 345600,
                "state": "OK",
                "size_used": 2147483648,  # 2GB
                "percent_used": 40.0,
            }
        }
    )


class UserQuotaSchema(BaseModel):
    """Base schema for User Quota."""

    id: str = Field(..., description="Unique identifier for the user quota")
    filesystem_id: str = Field(..., description="ID of the filesystem this user quota belongs to")
    uid: int = Field(..., description="User ID the quota applies to")
    hard_limit: Optional[int] = Field(None, description="Hard limit in bytes")
    soft_limit: Optional[int] = Field(None, description="Soft limit in bytes")
    remaining_grace_period: Optional[int] = Field(None, description="Remaining grace period in seconds")
    state: str = Field(default="OK", description="State of the user quota")
    size_used: int = Field(default=0, description="Current size used in bytes")
    percent_used: float = Field(default=0.0, description="Percentage of quota used")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "UserQuota_1",
                "filesystem_id": "fs_1",
                "uid": 1000,
                "hard_limit": 2147483648,  # 2GB
                "soft_limit": 1610612736,  # 1.5GB
                "remaining_grace_period": 172800,
                "state": "OK",
                "size_used": 1073741824,  # 1GB
                "percent_used": 50.0,
            }
        }
    )
