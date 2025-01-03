from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class RaidTypeEnum(str, Enum):
    RAID0 = "RAID0"
    RAID1 = "RAID1"
    RAID5 = "RAID5"
    RAID6 = "RAID6"
    RAID10 = "RAID10"
    MIXED = "MIXED"


class TierTypeEnum(str, Enum):
    EXTREME_PERFORMANCE = "EXTREME_PERFORMANCE"
    PERFORMANCE = "PERFORMANCE"
    CAPACITY = "CAPACITY"


class FastVPStatusEnum(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"


class FastVPRelocationRateEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class PoolRaidStripeWidthInfo(BaseModel):
    rpm: int = Field(..., description="Revolutions Per Minute (RPMs)")
    stripeWidth: int = Field(..., description="RAID stripe width")
    driveTechnology: str = Field(..., description="Drive technology")
    driveCount: int = Field(..., description="Number of physical drives")
    parityDrives: int = Field(..., description="Number of parity drives")


class PoolTier(BaseModel):
    tierType: TierTypeEnum
    stripeWidth: int
    raidType: RaidTypeEnum
    sizeTotal: int
    sizeUsed: int
    sizeFree: int
    sizeMovingDown: int
    sizeMovingUp: int
    sizeMovingWithin: int
    name: str
    poolUnits: List[str]
    diskCount: int
    spareDriveCount: int
    raidStripeWidthInfo: List[PoolRaidStripeWidthInfo]


class PoolFASTVP(BaseModel):
    status: FastVPStatusEnum
    relocationRate: FastVPRelocationRateEnum
    isScheduleEnabled: bool
    relocationDurationEstimate: Optional[datetime]
    sizeMovingDown: int
    sizeMovingUp: int
    sizeMovingWithin: int
    percentComplete: int
    type: str
    dataRelocated: int
    lastStartTime: Optional[datetime]
    lastEndTime: Optional[datetime]


class PoolConfiguration(BaseModel):
    name: str
    description: Optional[str]
    storageConfiguration: dict
    alertThreshold: int
    poolSpaceHarvestHighThreshold: float
    poolSpaceHarvestLowThreshold: float
    snapSpaceHarvestHighThreshold: float
    snapSpaceHarvestLowThreshold: float
    isFastCacheEnabled: bool
    isFASTVpScheduleEnabled: bool
    isDiskTechnologyMixed: bool
    maxSizeLimit: int
    maxDiskNumberLimit: int
    isMaxSizeLimitExceeded: bool
    isMaxDiskNumberLimitExceeded: bool
    isRPMMixed: bool


class PoolCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=85)
    description: Optional[str] = Field(None, max_length=170)
    raidType: RaidTypeEnum
    sizeTotal: int
    alertThreshold: int = Field(50, ge=50, le=84)
    poolSpaceHarvestHighThreshold: Optional[float]
    poolSpaceHarvestLowThreshold: Optional[float]
    snapSpaceHarvestHighThreshold: Optional[float]
    snapSpaceHarvestLowThreshold: Optional[float]
    isHarvestEnabled: bool = False
    isSnapHarvestEnabled: bool = False
    isFASTCacheEnabled: bool = False
    isFASTVpScheduleEnabled: bool = False
    type: str = "dynamic"


class PoolUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=85)
    description: Optional[str] = Field(None, max_length=170)
    alertThreshold: Optional[int] = Field(None, ge=50, le=84)
    poolSpaceHarvestHighThreshold: Optional[float]
    poolSpaceHarvestLowThreshold: Optional[float]
    snapSpaceHarvestHighThreshold: Optional[float]
    snapSpaceHarvestLowThreshold: Optional[float]
    isHarvestEnabled: Optional[bool]
    isSnapHarvestEnabled: Optional[bool]
    isFASTCacheEnabled: Optional[bool]
    isFASTVpScheduleEnabled: Optional[bool]


class Pool(BaseModel):
    id: str
    name: str
    description: Optional[str]
    raidType: RaidTypeEnum
    sizeTotal: int
    sizeFree: int
    sizeUsed: int
    sizePreallocated: int
    dataReductionSizeSaved: int
    dataReductionPercent: int
    dataReductionRatio: float
    flashPercentage: int
    sizeSubscribed: int
    alertThreshold: int
    hasDataReductionEnabledLuns: bool
    hasDataReductionEnabledFs: bool
    isFASTCacheEnabled: bool
    creationTime: datetime
    isEmpty: bool
    poolFastVP: Optional[PoolFASTVP]
    tiers: List[PoolTier]
    isHarvestEnabled: bool
    harvestState: Optional[str]
    isSnapHarvestEnabled: bool
    poolSpaceHarvestHighThreshold: Optional[float]
    poolSpaceHarvestLowThreshold: Optional[float]
    snapSpaceHarvestHighThreshold: Optional[float]
    snapSpaceHarvestLowThreshold: Optional[float]
    metadataSizeSubscribed: int
    snapSizeSubscribed: int
    nonBaseSizeSubscribed: int
    metadataSizeUsed: int
    snapSizeUsed: int
    nonBaseSizeUsed: int
    rebalanceProgress: Optional[int]
    type: str
    isAllFlash: bool

    class Config:
        json_schema_extra = {
            "example": {
                "id": "pool_123",
                "name": "PerformancePool",
                "description": "High performance storage pool",
                "raidType": "RAID5",
                "sizeTotal": 1000000000000,
                "sizeFree": 800000000000,
                "sizeUsed": 200000000000,
                "sizePreallocated": 0,
                "dataReductionSizeSaved": 0,
                "dataReductionPercent": 0,
                "dataReductionRatio": 1.0,
                "flashPercentage": 100,
                "sizeSubscribed": 1000000000000,
                "alertThreshold": 50,
                "hasDataReductionEnabledLuns": False,
                "hasDataReductionEnabledFs": False,
                "isFASTCacheEnabled": False,
                "creationTime": "2025-01-03T12:00:00Z",
                "isEmpty": False,
                "tiers": [],
                "isHarvestEnabled": False,
                "isSnapHarvestEnabled": False,
                "metadataSizeSubscribed": 0,
                "snapSizeSubscribed": 0,
                "nonBaseSizeSubscribed": 0,
                "metadataSizeUsed": 0,
                "snapSizeUsed": 0,
                "nonBaseSizeUsed": 0,
                "type": "dynamic",
                "isAllFlash": True,
            }
        }
