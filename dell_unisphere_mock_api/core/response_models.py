from datetime import datetime, timezone
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T", bound=BaseModel)

# Base configuration for all response models
base_config = ConfigDict(
    populate_by_name=True,
    json_schema_extra={"json_encoders": {datetime: lambda v: v.isoformat()}}
)

class Link(BaseModel):
    """Link model for HATEOAS (Hypermedia as the Engine of Application State)"""
    rel: str
    href: str
    model_config = base_config

class Entry(BaseModel, Generic[T]):
    """Entry model for Unity API responses."""
    base: str = Field(alias="@base")
    content: T
    links: List[Link] = []
    updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Optional[Dict[str, Any]] = None
    model_config = base_config

class ApiResponse(BaseModel, Generic[T]):
    """Base response model for Unity API."""
    base: str = Field(alias="@base")
    updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    links: List[Link]
    entries: List[Entry[T]]
    total: int
    metadata: Optional[Dict[str, Any]] = None
    model_config = base_config

class ErrorDetail(BaseModel):
    """Error detail model for Unity API error responses."""
    error_code: int = Field(alias="errorCode")
    http_status_code: int = Field(alias="httpStatusCode")
    messages: List[str]
    created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_config = base_config

def create_error_response(
    error_code: int,
    http_status_code: int,
    messages: List[str],
) -> ErrorDetail:
    """Centralized error response creation."""
    return ErrorDetail(
        error_code=error_code,
        http_status_code=http_status_code,
        messages=messages
    )
