from typing import List, Optional

from pydantic import BaseModel, Field


class NFSShareBase(BaseModel):
    name: str = Field(..., description="Name of the NFS share")
    description: Optional[str] = Field(None, description="Description of the NFS share")
    filesystem_id: str = Field(..., description="ID of the filesystem this share belongs to")
    path: str = Field(..., description="Path to the shared directory")
    default_access: str = Field(default="NO_ACCESS", description="Default access level for the share")
    root_squash_enabled: bool = Field(default=True, description="Whether root squashing is enabled")
    anonymous_uid: int = Field(default=65534, description="UID for anonymous access")
    anonymous_gid: int = Field(default=65534, description="GID for anonymous access")
    is_read_only: bool = Field(default=False, description="Whether the share is read-only")


class NFSShareCreate(NFSShareBase):
    pass


class NFSShareUpdate(BaseModel):
    description: Optional[str] = None
    default_access: Optional[str] = None
    root_squash_enabled: Optional[bool] = None
    anonymous_uid: Optional[int] = None
    anonymous_gid: Optional[int] = None
    is_read_only: Optional[bool] = None


class NFSShare(NFSShareBase):
    id: str = Field(..., description="Unique identifier for the NFS share")
    state: str = Field(default="READY", description="Operational state of the NFS share")
    export_paths: List[str] = Field(default_factory=list, description="List of export paths")
