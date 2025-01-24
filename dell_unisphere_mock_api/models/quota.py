from typing import Optional

from pydantic import BaseModel, Field


class QuotaConfigBase(BaseModel):
    filesystem_id: str = Field(..., description="ID of the filesystem this quota config belongs to")
    is_user_quotas_enabled: bool = Field(default=False, description="Whether user quotas are enabled")
    is_tree_quotas_enabled: bool = Field(default=False, description="Whether tree quotas are enabled")
    default_hard_limit: int = Field(default=0, description="Default hard limit in bytes")
    default_soft_limit: Optional[int] = Field(None, description="Default soft limit in bytes")
    description: Optional[str] = Field(None, description="Description of the quota config")


class QuotaConfigCreate(QuotaConfigBase):
    pass


class QuotaConfigUpdate(BaseModel):
    is_user_quotas_enabled: Optional[bool] = None
    is_tree_quotas_enabled: Optional[bool] = None
    default_hard_limit: Optional[int] = None
    default_soft_limit: Optional[int] = None
    description: Optional[str] = None


class QuotaConfig(QuotaConfigBase):
    id: str = Field(..., description="Unique identifier for the quota config")
    state: str = Field(default="READY", description="Operational state of the quota config")


class TreeQuotaBase(BaseModel):
    filesystem_id: str = Field(..., description="ID of the filesystem this tree quota belongs to")
    path: str = Field(..., description="Path to the directory")
    hard_limit: int = Field(default=0, description="Hard limit in bytes")
    soft_limit: Optional[int] = Field(None, description="Soft limit in bytes")
    used_capacity: int = Field(default=0, description="Used capacity in bytes")
    description: Optional[str] = Field(None, description="Description of the tree quota")


class TreeQuotaCreate(TreeQuotaBase):
    pass


class TreeQuotaUpdate(BaseModel):
    hard_limit: Optional[int] = None
    soft_limit: Optional[int] = None
    description: Optional[str] = None


class TreeQuota(TreeQuotaBase):
    id: str = Field(..., description="Unique identifier for the tree quota")
    state: str = Field(default="OK", description="Health state of the tree quota")


class UserQuotaBase(BaseModel):
    filesystem_id: str = Field(..., description="ID of the filesystem this user quota belongs to")
    uid: int = Field(..., description="User ID")
    hard_limit: int = Field(default=0, description="Hard limit in bytes")
    soft_limit: Optional[int] = Field(None, description="Soft limit in bytes")
    used_capacity: int = Field(default=0, description="Used capacity in bytes")
    description: Optional[str] = Field(None, description="Description of the user quota")


class UserQuotaCreate(UserQuotaBase):
    pass


class UserQuotaUpdate(BaseModel):
    hard_limit: Optional[int] = None
    soft_limit: Optional[int] = None
    description: Optional[str] = None


class UserQuota(UserQuotaBase):
    id: str = Field(..., description="Unique identifier for the user quota")
    state: str = Field(default="OK", description="Health state of the user quota")
