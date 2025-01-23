import logging
from datetime import datetime
from typing import List

from fastapi import HTTPException, Request

from ..core.response_models import ApiResponse, Entry, Link
from ..core.system_info import BasicSystemInfo

logger = logging.getLogger(__name__)


class SystemInfoController:
    """Controller for basic system information"""

    def __init__(self):
        # Mock data - would typically come from a database or service
        self.mock_system_info = BasicSystemInfo(
            id="0",
            model="Unity 450F",
            name="MyStorageSystem",
            softwareVersion="5.2.0",
            softwareFullVersion="5.2.0.0.5.123",
            apiVersion="5.2",
            earliestApiVersion="4.0",
        )

    def _create_response(self, request: Request, entries: List[Entry]) -> ApiResponse:
        """Create a standardized API response"""
        base_url = str(request.base_url)
        current_time = datetime.utcnow()

        return ApiResponse(
            **{
                "@base": f"{base_url}api/types/basicSystemInfo/instances?per_page=2000",
                "updated": current_time,
                "links": [Link(rel="self", href="&page=1")],
                "entries": entries,
            }
        )

    def _create_entry(self, system_info: BasicSystemInfo, base_url: str) -> Entry:
        """Create a standardized entry for system info"""
        return Entry(
            **{
                "@base": f"{base_url}api/instances/basicSystemInfo",
                "content": system_info,
                "links": [Link(rel="self", href=f"/{system_info.id}")],
                "updated": datetime.utcnow(),
            }
        )

    def get_collection(self, request: Request) -> ApiResponse[BasicSystemInfo]:
        """Get all basic system info instances"""
        entry = self._create_entry(self.mock_system_info, str(request.base_url))
        return self._create_response(request, [entry])

    def get_by_id(self, instance_id: str, request: Request) -> ApiResponse[BasicSystemInfo]:
        """Get a specific basic system info instance by ID"""
        logger.info(f"Received request for id: {instance_id}")
        if instance_id != self.mock_system_info.id:
            raise HTTPException(status_code=404, detail="System info not found")

        entry = self._create_entry(self.mock_system_info, str(request.base_url))
        return self._create_response(request, [entry])

    def get_by_name(self, name: str, request: Request) -> ApiResponse[BasicSystemInfo]:
        """Get a specific basic system info instance by name"""
        logger.info(f"Received request for name: {name}")
        print((f"Received request for name: {name}"), flush=True)
        if name != self.mock_system_info.name:
            raise HTTPException(status_code=404, detail=f"System info not found for {name}")

        entry = self._create_entry(self.mock_system_info, str(request.base_url))
        return self._create_response(request, [entry])
