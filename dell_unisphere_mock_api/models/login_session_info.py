from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    """User resource model"""

    id: str
    name: str
    role: str = "admin"
    password_change_required: bool = False
    domain: str = "Local"


class Role(BaseModel):
    """Role resource model"""

    id: str
    name: str
    description: Optional[str] = None


class LoginSessionInfo(BaseModel):
    """Login session information model"""

    id: str
    domain: str
    user: User
    roles: List[Role]
    idleTimeout: int = Field(default=3600, description="Session timeout in seconds")
    isPasswordChangeRequired: bool = Field(default=False, description="Whether password change is required")
    last_activity: datetime = Field(default_factory=datetime.utcnow)
