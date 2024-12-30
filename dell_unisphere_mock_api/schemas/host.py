from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class HostTypeEnum(str, Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"
    VMWARE = "VMware"
    OTHER = "Other"


class HostCreate(BaseModel):
    name: str
    description: Optional[str] = None
    type: HostTypeEnum
    os_type: Optional[str] = None
    initiators: Optional[List[str]] = None
    host_group: Optional[str] = None


class HostUpdate(BaseModel):
    description: Optional[str] = None
    os_type: Optional[str] = None
    initiators: Optional[List[str]] = None
    host_group: Optional[str] = None


class Host(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    type: HostTypeEnum
    os_type: Optional[str] = None
    initiators: List[str] = []
    host_group: Optional[str] = None
    health: str = "OK"
    storage_access: List[str] = []

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "host_1",
                "name": "test_host",
                "description": "Test host",
                "type": "Linux",
                "os_type": "CentOS 7",
                "initiators": ["iqn.1994-05.com.redhat:2bfbc0884dc4"],
                "host_group": "group_1",
                "health": "OK",
                "storage_access": ["lun_1", "lun_2"],
            }
        }
    )
