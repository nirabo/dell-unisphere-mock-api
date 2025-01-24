"""Schema definitions for CIFS Server resources."""

from typing import Optional

from pydantic import BaseModel, Field


class CIFSServerSchema(BaseModel):
    """Base schema for CIFS Server."""

    id: str = Field(..., description="Unique identifier for the CIFS server")
    name: str = Field(..., description="Name of the CIFS server")
    description: Optional[str] = Field(None, description="Description of the CIFS server")
    nas_server_id: str = Field(..., description="ID of the NAS server this CIFS server belongs to")
    domain_name: Optional[str] = Field(None, description="Domain name for Active Directory integration")
    netbios_name: str = Field(..., description="NetBIOS name for the CIFS server")
    workgroup: Optional[str] = Field(None, description="Workgroup name if not domain-joined")
    is_standalone: bool = Field(default=True, description="Whether this is a standalone or domain-joined server")
    is_joined_to_domain: bool = Field(default=False, description="Whether server is joined to a domain")
    health_state: str = Field(default="OK", description="Health state of the CIFS server")
    state: str = Field(default="READY", description="Operational state of the CIFS server")

    class Config:
        """Pydantic model configuration."""

        schema_extra = {
            "example": {
                "id": "CIFSServer_1",
                "name": "FileShare01",
                "description": "Primary file sharing server",
                "nas_server_id": "nas_1",
                "netbios_name": "FILESHARE01",
                "domain_name": "example.com",
                "workgroup": None,
                "is_standalone": False,
                "is_joined_to_domain": True,
                "health_state": "OK",
                "state": "READY",
            }
        }
