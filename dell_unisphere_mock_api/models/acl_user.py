from typing import Optional

from pydantic import BaseModel, Field


class ACLUserBase(BaseModel):
    """Base model for ACL User."""

    user_name: str = Field(..., description="Name of the user")
    domain_name: str = Field(..., description="Domain name of the user")
    sid: str = Field(..., description="Security Identifier (SID) of the user")
    is_domain_user: bool = Field(False, description="Whether this is a domain user")
    is_local_user: bool = Field(False, description="Whether this is a local user")


class ACLUserCreate(ACLUserBase):
    """Model for creating a new ACL User."""

    pass


class ACLUserUpdate(BaseModel):
    """Model for updating an ACL User."""

    user_name: Optional[str] = Field(None, description="Name of the user")
    domain_name: Optional[str] = Field(None, description="Domain name of the user")
    sid: Optional[str] = Field(None, description="Security Identifier (SID) of the user")
    is_domain_user: Optional[bool] = Field(None, description="Whether this is a domain user")
    is_local_user: Optional[bool] = Field(None, description="Whether this is a local user")


class ACLUser(ACLUserBase):
    """Model for an ACL User."""

    id: str = Field(..., description="Unique identifier for the ACL User")
