from typing import List

from pydantic import BaseModel


class User:
    # Placeholder for user resource
    pass


class Role:
    # Placeholder for role resource
    pass


class LoginSessionInfo(BaseModel):
    id: str
    domain: str
    user: User
    roles: List[Role]
    idleTimeout: int
    isPasswordChangeRequired: bool
