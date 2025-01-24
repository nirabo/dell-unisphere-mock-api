from typing import List, Optional

from pydantic import BaseModel, Field, conint, validator


class Host(BaseModel):
    """Model for host associated with a tenant."""

    id: str = Field(..., description="Host identifier")
    name: str = Field(..., description="Host name")


class TenantBase(BaseModel):
    """Base model for Tenant."""

    name: str = Field(..., description="User-specified name of the tenant")
    uuid: Optional[str] = Field(None, description="UUID of the tenant")
    vlans: List[conint(ge=1, le=4094)] = Field(..., description="VLAN IDs assigned to the tenant")

    @validator("vlans")
    def validate_vlans(cls, v):
        if len(v) > 32:
            raise ValueError("Maximum of 32 VLANs allowed per tenant")
        return v


class TenantCreate(TenantBase):
    """Model for creating a tenant."""

    pass


class TenantUpdate(BaseModel):
    """Model for updating a tenant."""

    name: Optional[str] = Field(None, description="New tenant name")
    vlans: Optional[List[conint(ge=1, le=4094)]] = Field(None, description="List of VLAN IDs to set")

    @validator("vlans")
    def validate_vlans(cls, v):
        if v is not None and len(v) > 32:
            raise ValueError("Maximum of 32 VLANs allowed per tenant")
        return v


class Tenant(TenantBase):
    """Model for Tenant instance."""

    id: str = Field(..., description="Unique identifier of the tenant instance")
    hosts: List[Host] = Field(default=[], description="The hosts associated with the tenant")
