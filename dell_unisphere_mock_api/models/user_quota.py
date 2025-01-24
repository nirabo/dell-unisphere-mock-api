from typing import Optional

from pydantic import BaseModel, Field


class UserQuotaBase(BaseModel):
    filesystem_id: str = Field(..., description="ID of the filesystem this user quota belongs to")
    uid: int = Field(..., description="User ID the quota applies to")
    hard_limit: Optional[int] = Field(None, description="Hard limit in bytes")
    soft_limit: Optional[int] = Field(None, description="Soft limit in bytes")


class UserQuotaCreate(UserQuotaBase):
    pass


class UserQuotaUpdate(BaseModel):
    hard_limit: Optional[int] = None
    soft_limit: Optional[int] = None


class UserQuota(UserQuotaBase):
    id: str = Field(..., description="Unique identifier for the user quota")
    remaining_grace_period: Optional[int] = Field(None, description="Remaining grace period in seconds")
    state: str = Field(default="OK", description="State of the user quota")
    size_used: int = Field(default=0, description="Current size used in bytes")
    percent_used: float = Field(default=0.0, description="Percentage of quota used")
