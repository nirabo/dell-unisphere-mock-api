from pydantic import BaseModel, ConfigDict


class BasicSystemInfo(BaseModel):
    """Model representing basic system information"""

    id: str
    model: str
    name: str
    softwareVersion: str
    softwareFullVersion: str
    apiVersion: str
    earliestApiVersion: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "0",
                "model": "Unity 450F",
                "name": "MyStorageSystem",
                "softwareVersion": "5.2.0",
                "softwareFullVersion": "5.2.0.0.0.0",
                "apiVersion": "5.2",
                "earliestApiVersion": "5.0",
            }
        }
    )
