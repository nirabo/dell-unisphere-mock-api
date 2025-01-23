import re
from typing import Any, Dict, List, Optional

from fastapi import Query


class QueryParams:
    def __init__(
        self,
        fields: Optional[str] = Query(None),
        page: int = Query(1, ge=1),
        per_page: int = Query(50, ge=1, le=1000),
        filter: Optional[str] = Query(None),
        orderby: Optional[str] = Query(None),
        groupby: Optional[str] = Query(None),
    ):
        self.fields = fields.split(",") if fields else []
        self.page = page
        self.per_page = per_page
        self.filters = self._parse_filters(filter)
        self.sort = self._parse_sort(orderby)
        self.groupby = groupby.split(",") if groupby else []

    def _parse_filters(self, filter_str: Optional[str]) -> Dict[str, Any]:
        """Parse filter string into structured query filters"""
        filters = {}
        if not filter_str:
            return filters

        # Example filter: "name eq 'test*' and size gt 100"
        # This simplified parser handles basic equality checks
        for condition in re.split(r"\s+and\s+", filter_str, flags=re.IGNORECASE):
            match = re.match(r"(\w+)\s+(eq|ne|gt|lt)\s+(.+)", condition, re.IGNORECASE)
            if match:
                field, op, value = match.groups()
                filters[field] = {"operator": op.upper(), "value": self._parse_value(value)}
        return filters

    def _parse_sort(self, orderby: Optional[str]) -> List[Dict[str, str]]:
        """Parse orderby string into sort directives"""
        if not orderby:
            return []

        sorts = []
        for field in orderby.split(","):
            if " " in field:
                field, direction = field.rsplit(" ", 1)
                sorts.append({"field": field, "direction": direction.upper()})
            else:
                sorts.append({"field": field, "direction": "ASC"})
        return sorts

    def _parse_value(self, value: str):
        """Convert string values to appropriate types"""
        value = value.strip("'\"")
        if value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError:
            return value
