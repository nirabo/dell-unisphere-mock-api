from typing import Optional

from pydantic import BaseModel, Field


class TreeQuotaBase(BaseModel):
    filesystem_id: str = Field(..., description="ID of the filesystem this tree quota belongs to")
    path: str = Field(..., description="Path to the directory where quota is applied")
    description: Optional[str] = Field(None, description="Description of the tree quota")
    hard_limit: Optional[int] = Field(None, description="Hard limit in bytes")
    soft_limit: Optional[int] = Field(None, description="Soft limit in bytes")


class TreeQuotaCreate(TreeQuotaBase):
    pass


class TreeQuotaUpdate(BaseModel):
    description: Optional[str] = None
    hard_limit: Optional[int] = None
    soft_limit: Optional[int] = None


class TreeQuota(TreeQuotaBase):
    id: str = Field(..., description="Unique identifier for the tree quota")
    remaining_grace_period: Optional[int] = Field(None, description="Remaining grace period in seconds")
    state: str = Field(default="OK", description="State of the tree quota")
    size_used: int = Field(default=0, description="Current size used in bytes")
    percent_used: float = Field(default=0.0, description="Percentage of quota used")
