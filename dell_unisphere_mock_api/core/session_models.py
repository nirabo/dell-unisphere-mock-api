from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class UserInfo(BaseModel):
    id: str
    name: str


class Role(BaseModel):
    id: str
    name: str


class LoginSessionInfo(BaseModel):
    id: str
    domain: str
    user: UserInfo
    roles: List[Role]
    idleTimeout: int = Field(default=3600, description="Session timeout in seconds")
    isPasswordChangeRequired: bool = False


class LogoutRequest(BaseModel):
    localCleanupOnly: Optional[bool] = Field(default=False, description="If true, only log out current session")


class LogoutResponse(BaseModel):
    logoutOK: str = "true"
