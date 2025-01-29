from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T", bound=BaseModel)


class Link(BaseModel):
    """Link model for HATEOAS (Hypermedia as the Engine of Application State)"""

    rel: str
    href: str


class Entry(BaseModel, Generic[T]):
    """Entry model for Unity API responses."""

    base: str = Field(alias="@base")
    content: T
    links: List[Link] = []
    updated: datetime
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(populate_by_name=True, json_encoders={datetime: lambda v: v.isoformat()})


class ApiResponse(BaseModel, Generic[T]):
    """Base response model for Unity API."""

    base: str = Field(alias="@base")
    updated: datetime
    links: List[Link]
    entries: List[Entry[T]]
    total: int
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(populate_by_name=True, json_encoders={datetime: lambda v: v.isoformat()})


class ErrorDetail(BaseModel):
    """Error detail model for Unity API error responses."""

    error_code: int = Field(alias="errorCode")
    http_status_code: int = Field(alias="httpStatusCode")
    messages: List[str]
    created: datetime = Field(default_factory=lambda: datetime.now())

    model_config = ConfigDict(populate_by_name=True, json_encoders={datetime: lambda v: v.isoformat()})
