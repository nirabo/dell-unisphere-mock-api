from datetime import datetime
from typing import Any, Dict, List

from fastapi import Request


class UnityResponseFormatter:
    def __init__(self, request: Request):
        self.base_url = str(request.base_url).rstrip("/")
        self.path = request.url.path

    def format_collection(self, data: List[Any], pagination: dict = None) -> Dict[str, Any]:
        """Format a collection response according to Unity REST API spec."""
        result = {
            "@base": f"{self.base_url}{self.path}",
            "updated": datetime.utcnow().isoformat() + "Z",
            "entries": [{"content": item} for item in data],
            "links": [],
        }

        if pagination:
            result["links"].extend(self._build_pagination_links(pagination))
            result["total"] = pagination.get("total", len(data))

        return result

    def _build_pagination_links(self, pagination: dict) -> List[Dict[str, str]]:
        """Create pagination links according to Unity spec."""
        links = []
        current_page = pagination["page"]
        total_pages = pagination["total_pages"]

        if current_page > 1:
            links.append({"rel": "prev", "href": f"?page={current_page-1}"})
        if current_page < total_pages:
            links.append({"rel": "next", "href": f"?page={current_page+1}"})

        links.append({"rel": "first", "href": "?page=1"})
        links.append({"rel": "last", "href": f"?page={total_pages}"})

        return links
