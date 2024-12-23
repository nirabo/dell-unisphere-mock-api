from enum import Enum
from pydantic import BaseModel
from typing import Optional, List

class PoolUnitTypeEnum(str, Enum):
    VIRTUAL_DISK = "Virtual_Disk"
    RAID_GROUP = "RAID_Group"

class PoolUnitOpStatusEnum(str, Enum):
    UNKNOWN = "Unknown"
    OK = "OK"
    DEGRADED = "Degraded"
    ERROR = "Error"
    NOT_READY = "Not_Ready"
    OFFLINE = "Offline"

class PoolUnitBase(BaseModel):
    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    health: PoolUnitOpStatusEnum = PoolUnitOpStatusEnum.OK
    type: PoolUnitTypeEnum
    size_total: int
    size_used: int
    size_free: int
    raid_type: Optional[str] = None
    disk_group: Optional[str] = None

class PoolUnitCreate(PoolUnitBase):
    pass

class PoolUnitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class PoolUnit(PoolUnitBase):
    class Config:
        orm_mode = True
