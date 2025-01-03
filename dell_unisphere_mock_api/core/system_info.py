from typing import Optional

from pydantic import BaseModel


class BasicSystemInfo(BaseModel):
    """Model representing basic system information"""

    id: str
    model: str
    name: str
    softwareVersion: str
    softwareFullVersion: str
    apiVersion: str
    earliestApiVersion: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "system-1",
                "model": "Unity 450F",
                "name": "MyStorageSystem",
                "softwareVersion": "5.2.0",
                "softwareFullVersion": "5.2.0.0.5.123",
                "apiVersion": "5.2",
                "earliestApiVersion": "4.0",
            }
        }
