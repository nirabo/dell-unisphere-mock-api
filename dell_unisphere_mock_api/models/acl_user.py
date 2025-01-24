from typing import Optional

from pydantic import BaseModel, Field


class ACLUserBase(BaseModel):
    """Base model for ACL User."""

    sid: str = Field(..., description="Windows user id")
    domain_name: str = Field(..., description="Windows domain name")
    user_name: str = Field(..., description="User name")


class ACLUserCreate(ACLUserBase):
    pass


class ACLUserUpdate(BaseModel):
    sid: Optional[str] = None
    domain_name: Optional[str] = None
    user_name: Optional[str] = None


class ACLUser(ACLUserBase):
    """Model for ACL User instance."""

    id: str = Field(..., description="Unique instance id")
