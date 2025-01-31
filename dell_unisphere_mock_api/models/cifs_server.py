from typing import List, Optional

from pydantic import BaseModel, Field


class CIFSServerBase(BaseModel):
    name: str = Field(..., description="Name of the CIFS server")
    description: Optional[str] = Field(None, description="Description of the CIFS server")
    nas_server_id: str = Field(..., description="ID of the NAS server this CIFS server belongs to")
    domain_name: Optional[str] = Field(None, description="Domain name for Active Directory integration")
    netbios_name: str = Field(..., description="NetBIOS name for the CIFS server")
    workgroup: Optional[str] = Field(None, description="Workgroup name if not domain-joined")
    is_standalone: bool = Field(default=True, description="Whether this is a standalone or domain-joined server")
    is_joined_to_domain: bool = Field(default=False, description="Whether server is joined to a domain")


class CIFSServerCreate(CIFSServerBase):
    pass


class CIFSServerUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    domain_name: Optional[str] = None
    workgroup: Optional[str] = None


class CIFSServer(CIFSServerBase):
    id: str = Field(..., description="Unique identifier for the CIFS server")
    health_state: str = Field(default="OK", description="Health state of the CIFS server")
    state: str = Field(default="READY", description="Operational state of the CIFS server")
