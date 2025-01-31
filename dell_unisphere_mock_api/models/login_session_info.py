from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    """User resource model"""

    id: str
    name: str
    role: str = "admin"
    password_change_required: bool = False
    domain: str = "Local"

    model_config = ConfigDict(
        populate_by_name=True, json_schema_extra={"json_encoders": {datetime: lambda v: v.isoformat()}}
    )


class Role(BaseModel):
    """Role resource model"""

    id: str
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True, json_schema_extra={"json_encoders": {datetime: lambda v: v.isoformat()}}
    )


class LoginSessionInfo(BaseModel):
    """Login session information model"""

    id: str
    domain: str
    user: User
    roles: List[Role]
    idleTimeout: int
    isPasswordChangeRequired: bool
    last_activity: datetime

    model_config = ConfigDict(
        populate_by_name=True, json_schema_extra={"json_encoders": {datetime: lambda v: v.isoformat()}}
    )
