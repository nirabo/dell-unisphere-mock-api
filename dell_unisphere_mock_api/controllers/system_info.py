import logging
from typing import List

from fastapi import HTTPException

from ..core.system_info import BasicSystemInfo

logger = logging.getLogger(__name__)


class SystemInfoController:
    """Controller for basic system information"""

    def __init__(self):
        # Mock data - would typically come from a database or service
        self.mock_system_info = BasicSystemInfo(
            id="system-1",
            model="Unity 450F",
            name="MyStorageSystem",
            softwareVersion="5.2.0",
            softwareFullVersion="5.2.0.0.5.123",
            apiVersion="5.2",
            earliestApiVersion="4.0",
        )

    def get_collection(self) -> List[BasicSystemInfo]:
        """Get all basic system info instances"""
        return [self.mock_system_info]

    def get_by_id(self, instance_id: str) -> BasicSystemInfo:
        """Get a specific basic system info instance by ID"""
        logger.info(f"Received request for id: {id}")
        if instance_id != self.mock_system_info.id:
            raise HTTPException(status_code=404, detail="System info not foundtest")
        return self.mock_system_info

    def get_by_name(self, name: str) -> BasicSystemInfo:
        """Get a specific basic system info instance by name"""
        # Direct comparison of the name
        logger.info(f"Received request for name: {name}")
        print((f"Received request for name: {name}"), flush=True)
        if name != self.mock_system_info.name:
            raise HTTPException(status_code=404, detail=f"System info not found for {name}")
        return self.mock_system_info
