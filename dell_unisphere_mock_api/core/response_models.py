from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Link(BaseModel):
    rel: str
    href: str


class Entry(BaseModel, Generic[T]):
    base: str = Field(alias="@base")
    content: T
    links: List[Link]
    updated: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class ApiResponse(BaseModel, Generic[T]):
    base: str = Field(alias="@base")
    updated: datetime
    links: List[Link]
    entries: List[Entry[T]]
    total: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class ErrorDetail(BaseModel):
    """Detailed error information following Unity API error format."""

    error_code: int = Field(alias="errorCode")
    http_status_code: int = Field(alias="httpStatusCode")
    messages: List[str]
    created: datetime
    error_messages: Optional[List[Dict[str, Any]]] = Field(default=None, alias="errorMessages")

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}
