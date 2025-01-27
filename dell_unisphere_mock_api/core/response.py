from datetime import datetime, timezone
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from fastapi import HTTPException, Request, status

from .response_models import ApiResponse, Entry, ErrorDetail, Link

T = TypeVar("T")


class UnityResponseFormatter(Generic[T]):
    def __init__(self, request: Request):
        self.base_url = str(request.base_url).rstrip("/")
        self.path = request.url.path

    def format_collection(
        self,
        data: List[T],
        pagination: Optional[dict] = None,
        entry_links: Optional[Dict[int, List[Link]]] = None,
        entry_metadata: Optional[Dict[int, Dict[str, Any]]] = None,
        response_metadata: Optional[Dict[str, Any]] = None,
    ) -> ApiResponse[T]:
        """Format a collection response according to Unity REST API spec.

        Args:
            data: List of items to include in the response
            pagination: Optional pagination information (page, total_pages, total)
            entry_links: Optional dict mapping entry index to list of links for that entry
            entry_metadata: Optional dict mapping entry index to metadata for that entry
            response_metadata: Optional metadata to include in the response
        """
        base = f"{self.base_url}{self.path}"
        current_time = datetime.now(timezone.utc)

        # Create Entry objects for each item
        entries = []
        for idx, item in enumerate(data):
            entry_links_list = entry_links.get(idx, []) if entry_links else []
            entry_metadata_dict = entry_metadata.get(idx) if entry_metadata else None

            entries.append(
                Entry[T](
                    base=base, content=item, links=entry_links_list, updated=current_time, metadata=entry_metadata_dict
                )
            )

        # Build response links
        links = []
        if pagination:
            links.extend(self._build_pagination_links(pagination))

        # Create the full response
        response = ApiResponse[T](
            base=base,
            updated=current_time,
            entries=entries,
            links=links,
            total=pagination.get("total", len(data)) if pagination else len(data),
            metadata=response_metadata,
        )

        return response

    def format_error(
        self,
        error: Union[HTTPException, Exception],
        error_code: Optional[int] = None,
        error_messages: Optional[List[Dict[str, Any]]] = None,
    ) -> ErrorDetail:
        """Format an error response according to Unity REST API spec."""
        if isinstance(error, HTTPException):
            status_code = error.status_code
            messages = [error.detail]
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            messages = [str(error)]

        if error_code is None:
            error_code = status_code

        return ErrorDetail(
            errorCode=error_code,
            httpStatusCode=status_code,
            messages=messages,
            created=datetime.now(timezone.utc),
            errorMessages=error_messages,
        )

    def _build_pagination_links(self, pagination: dict) -> List[Link]:
        """Create pagination links according to Unity spec."""
        links = []
        current_page = pagination["page"]
        total_pages = pagination["total_pages"]

        if current_page > 1:
            links.append(Link(rel="previous", href=f"{self.base_url}{self.path}?page={current_page - 1}"))

        if current_page < total_pages:
            links.append(Link(rel="next", href=f"{self.base_url}{self.path}?page={current_page + 1}"))

        return links

    def format_response(
        self,
        content: T,
        resource_type: str,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ApiResponse[T]:
        """Format a single resource response according to Unity REST API spec.

        Args:
            content: The resource content
            resource_type: Type of the resource (e.g., 'filesystem', 'lun')
            resource_id: Optional ID of the resource
            metadata: Optional metadata to include in the response
        """
        base = f"{self.base_url}{self.path}"
        current_time = datetime.now(timezone.utc)

        # Create links for the resource
        links = []
        if resource_id:
            links.append(Link(rel="self", href=f"/{resource_id}"))

        # Create the entry
        entry = Entry[T](base=base, content=content, links=links, updated=current_time, metadata=metadata)

        # Create the full response
        response = ApiResponse[T](base=base, updated=current_time, entries=[entry], links=[], total=1, metadata=None)

        return response
