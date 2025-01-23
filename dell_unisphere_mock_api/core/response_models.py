from datetime import datetime
from typing import Generic, List, Optional, TypeVar

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

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class ApiResponse(BaseModel, Generic[T]):
    base: str = Field(alias="@base")
    updated: datetime
    links: List[Link]
    entries: List[Entry[T]]

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}
