"""Schema definitions for NFS Share resources."""

from typing import List, Optional

from pydantic import BaseModel, Field


class NFSShareSchema(BaseModel):
    """Base schema for NFS Share."""

    id: str = Field(..., description="Unique identifier for the NFS share")
    name: str = Field(..., description="Name of the NFS share")
    description: Optional[str] = Field(None, description="Description of the NFS share")
    filesystem_id: str = Field(..., description="ID of the filesystem this share belongs to")
    path: str = Field(..., description="Path to the shared directory")
    default_access: str = Field(default="NO_ACCESS", description="Default access level for the share")
    root_squash_enabled: bool = Field(default=True, description="Whether root squashing is enabled")
    anonymous_uid: int = Field(default=65534, description="UID for anonymous access")
    anonymous_gid: int = Field(default=65534, description="GID for anonymous access")
    is_read_only: bool = Field(default=False, description="Whether the share is read-only")
    state: str = Field(default="READY", description="Operational state of the NFS share")
    export_paths: List[str] = Field(default_factory=list, description="List of export paths")

    class Config:
        """Pydantic model configuration."""

        schema_extra = {
            "example": {
                "id": "NFSShare_1",
                "name": "project_data",
                "description": "Project data share",
                "filesystem_id": "fs_1",
                "path": "/exports/project_data",
                "default_access": "READ_ONLY",
                "root_squash_enabled": True,
                "anonymous_uid": 65534,
                "anonymous_gid": 65534,
                "is_read_only": True,
                "state": "READY",
                "export_paths": ["/exports/project_data"],
            }
        }
