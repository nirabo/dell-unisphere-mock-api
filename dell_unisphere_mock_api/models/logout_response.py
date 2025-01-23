from pydantic import BaseModel


class LogoutResult(BaseModel):
    logoutOK: str = "true"


class LogoutResponse(BaseModel):
    result: LogoutResult = LogoutResult()
