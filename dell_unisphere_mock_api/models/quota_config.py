from typing import Optional

from pydantic import BaseModel, Field


class QuotaConfigBase(BaseModel):
    filesystem_id: str = Field(..., description="ID of the filesystem this quota config belongs to")
    is_user_quotas_enabled: bool = Field(default=False, description="Whether user quotas are enabled")
    is_tree_quotas_enabled: bool = Field(default=False, description="Whether tree quotas are enabled")
    default_hard_limit: Optional[int] = Field(None, description="Default hard limit in bytes")
    default_soft_limit: Optional[int] = Field(None, description="Default soft limit in bytes")
    grace_period: int = Field(default=604800, description="Grace period in seconds (default 7 days)")


class QuotaConfigCreate(QuotaConfigBase):
    pass


class QuotaConfigUpdate(BaseModel):
    is_user_quotas_enabled: Optional[bool] = None
    is_tree_quotas_enabled: Optional[bool] = None
    default_hard_limit: Optional[int] = None
    default_soft_limit: Optional[int] = None
    grace_period: Optional[int] = None


class QuotaConfig(QuotaConfigBase):
    id: str = Field(..., description="Unique identifier for the quota configuration")
    state: str = Field(default="READY", description="Operational state of the quota configuration")
