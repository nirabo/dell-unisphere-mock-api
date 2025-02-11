from typing import Any, Dict, List, Optional, TypeVar

from fastapi import Request
from pydantic import BaseModel

from dell_unisphere_mock_api.core.response_models import ApiResponse, Entry, Link

T = TypeVar("T", bound=BaseModel)

class UnityResponseFormatter:
    """Formatter for Unity API responses."""

    def __init__(self, request: Request):
        self.request = request

    async def format_collection(
        self,
        items: List[T],
        entry_links: Optional[Dict[int, List[Dict[str, str]]]] = None,
    ) -> ApiResponse[T]:
        """Format a collection of items into a Unity API response."""
        entries = []
        base = str(self.request.base_url)[:-1] + self.request.url.path

        for i, item in enumerate(items):
            links = []
            if entry_links and i in entry_links:
                for link_data in entry_links[i]:
                    links.append(Link(rel=link_data["rel"], href=link_data["href"]))

            entry = Entry[T](
                base=base, 
                content=item, 
                links=links
            )
            entries.append(entry)

        return ApiResponse[T](
            base=base,
            links=[],
            entries=entries,
            total=len(items),
            metadata=None
        )

    async def format_item(
        self,
        item: T,
        links: Optional[List[Dict[str, str]]] = None,
    ) -> ApiResponse[T]:
        """Format a single item into a Unity API response."""
        base = str(self.request.base_url)[:-1] + self.request.url.path
        entry_links = []
        if links:
            for link_data in links:
                entry_links.append(Link(rel=link_data["rel"], href=link_data["href"]))

        entry = Entry[T](
            base=base, 
            content=item, 
            links=entry_links
        )
        
        return ApiResponse[T](
            base=base,
            links=[],
            entries=[entry],
            total=1,
            metadata=None
        )
