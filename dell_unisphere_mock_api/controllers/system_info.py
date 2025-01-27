import logging

from fastapi import HTTPException, Request

from ..core.response import UnityResponseFormatter
from ..core.response_models import ApiResponse
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

    def get_collection(self, request: Request) -> ApiResponse[BasicSystemInfo]:
        """Get all basic system info instances"""
        formatter = UnityResponseFormatter(request)
        return formatter.format_collection([self.mock_system_info], entry_links={0: [{"rel": "self", "href": "/0"}]})

    def get_by_id(self, instance_id: str, request: Request) -> ApiResponse[BasicSystemInfo]:
        """Get a specific basic system info instance by ID"""
        logger.info(f"Received request for id: {instance_id}")
        if instance_id != self.mock_system_info.id:
            raise HTTPException(status_code=404, detail="System info not found")

        formatter = UnityResponseFormatter(request)
        return formatter.format_collection(
            [self.mock_system_info], entry_links={0: [{"rel": "self", "href": f"/{instance_id}"}]}
        )

    def get_by_name(self, name: str, request: Request) -> ApiResponse[BasicSystemInfo]:
        """Get a specific basic system info instance by name"""
        logger.info(f"Received request for name: {name}")
        print((f"Received request for name: {name}"), flush=True)
        if name != self.mock_system_info.name:
            raise HTTPException(status_code=404, detail=f"System info not found for {name}")

        formatter = UnityResponseFormatter(request)
        return formatter.format_collection([self.mock_system_info], entry_links={0: [{"rel": "self", "href": "/0"}]})
