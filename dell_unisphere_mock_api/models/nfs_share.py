from typing import List, Optional

from pydantic import BaseModel, Field


class NFSShareBase(BaseModel):
    name: str = Field(..., description="Name of the NFS share")
    description: str = Field(..., description="Description of the NFS share")
    filesystem_id: str = Field(..., description="ID of the filesystem this share belongs to")
    path: str = Field(..., description="Path to the shared directory")
    default_access: str = Field(..., description="Default access level for the share")
    root_squash_enabled: bool = Field(..., description="Whether root squashing is enabled")
    anonymous_uid: int = Field(..., description="UID for anonymous access")
    anonymous_gid: int = Field(..., description="GID for anonymous access")
    is_read_only: bool = Field(..., description="Whether the share is read-only")
    min_security: str = Field(..., description="Minimum security level for NFS clients")
    no_access_hosts: List[str] = Field(..., description="List of hosts that are denied access")
    read_only_hosts: List[str] = Field(..., description="List of hosts with read-only access")
    read_write_hosts: List[str] = Field(..., description="List of hosts with read-write access")
    root_access_hosts: List[str] = Field(..., description="List of hosts with root access")


class NFSShareCreate(NFSShareBase):
    pass


class NFSShareUpdate(BaseModel):
    description: Optional[str] = None
    default_access: Optional[str] = None
    root_squash_enabled: Optional[bool] = None
    anonymous_uid: Optional[int] = None
    anonymous_gid: Optional[int] = None
    is_read_only: Optional[bool] = None
    min_security: Optional[str] = None
    no_access_hosts: Optional[List[str]] = None
    read_only_hosts: Optional[List[str]] = None
    read_write_hosts: Optional[List[str]] = None
    root_access_hosts: Optional[List[str]] = None


class NFSShare(NFSShareBase):
    id: str = Field(..., description="Unique identifier for the NFS share")
    state: str = Field(default="READY", description="Operational state of the NFS share")
    export_paths: List[str] = Field(default_factory=list, description="List of export paths")
