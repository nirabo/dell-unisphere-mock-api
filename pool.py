from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# Enums
class RaidTypeEnum(str, Enum):
    RAID0 = "RAID0"
    RAID1 = "RAID1"
    RAID5 = "RAID5"
    RAID6 = "RAID6"
    RAID10 = "RAID10"
    MIXED = "MIXED"


class FastVPStatusEnum(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"


class FastVPRelocationRateEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TierTypeEnum(str, Enum):
    FLASH = "FLASH"
    SAS = "SAS"
    NL_SAS = "NL_SAS"


class DiskTechnologyEnum(str, Enum):
    FLASH = "FLASH"
    SAS = "SAS"
    NL_SAS = "NL_SAS"


class RaidStripeWidthEnum(str, Enum):
    STRIPE_2 = "2"
    STRIPE_4 = "4"
    STRIPE_8 = "8"
    STRIPE_16 = "16"


class StoragePoolTypeEnum(str, Enum):
    DYNAMIC = "DYNAMIC"
    TRADITIONAL = "TRADITIONAL"


# Nested Models
class PoolConfiguration(BaseModel):
    name: str
    description: Optional[str] = None
    alertThreshold: Optional[int] = Field(None, ge=50, le=84)
    poolSpaceHarvestHighThreshold: Optional[float] = None
    poolSpaceHarvestLowThreshold: Optional[float] = None
    snapSpaceHarvestHighThreshold: Optional[float] = None
    snapSpaceHarvestLowThreshold: Optional[float] = None
    isFastCacheEnabled: Optional[bool] = None
    isFASTVpScheduleEnabled: Optional[bool] = None
    isDiskTechnologyMixed: Optional[bool] = None
    maxSizeLimit: Optional[int] = None
    maxDiskNumberLimit: Optional[int] = None
    isMaxSizeLimitExceeded: Optional[bool] = None
    isMaxDiskNumberLimitExceeded: Optional[bool] = None
    isRPMMixed: Optional[bool] = None


class PoolFASTVP(BaseModel):
    status: FastVPStatusEnum
    relocationRate: FastVPRelocationRateEnum
    isScheduleEnabled: bool
    relocationDurationEstimate: Optional[datetime] = None
    sizeMovingDown: Optional[int] = None
    sizeMovingUp: Optional[int] = None
    sizeMovingWithin: Optional[int] = None
    percentComplete: Optional[int] = None
    dataRelocated: Optional[int] = None
    lastStartTime: Optional[datetime] = None
    lastEndTime: Optional[datetime] = None


class PoolRaidStripeWidthInfo(BaseModel):
    rpm: Optional[int] = None
    stripeWidth: RaidStripeWidthEnum
    driveTechnology: DiskTechnologyEnum
    driveCount: int
    parityDrives: int


class PoolTier(BaseModel):
    tierType: TierTypeEnum
    stripeWidth: RaidStripeWidthEnum
    raidType: RaidTypeEnum
    sizeTotal: int
    sizeUsed: int
    sizeFree: int
    sizeMovingDown: Optional[int] = None
    sizeMovingUp: Optional[int] = None
    sizeMovingWithin: Optional[int] = None
    name: str
    poolUnits: List[Dict] = []
    diskCount: int
    spareDriveCount: Optional[int] = None
    raidStripeWidthInfo: Optional[List[PoolRaidStripeWidthInfo]] = None


# Main Pool Model
class Pool(BaseModel):
    id: str
    health: Optional[Dict] = None
    name: str
    description: Optional[str] = None
    raidType: RaidTypeEnum
    sizeFree: int
    sizeTotal: int
    sizeUsed: int
    sizePreallocated: int
    dataReductionSizeSaved: Optional[int] = None
    dataReductionPercent: Optional[int] = None
    dataReductionRatio: Optional[float] = None
    flashPercentage: Optional[int] = None
    sizeSubscribed: int
    alertThreshold: Optional[int] = Field(None, ge=50, le=84)
    hasDataReductionEnabledLuns: Optional[bool] = None
    hasDataReductionEnabledFs: Optional[bool] = None
    isFASTCacheEnabled: Optional[bool] = None
    creationTime: datetime
    isEmpty: bool
    poolFastVP: Optional[PoolFASTVP] = None
    tiers: List[PoolTier] = []
    isHarvestEnabled: Optional[bool] = None
    harvestState: Optional[str] = None
    isSnapHarvestEnabled: Optional[bool] = None
    poolSpaceHarvestHighThreshold: Optional[float] = None
    poolSpaceHarvestLowThreshold: Optional[float] = None
    snapSpaceHarvestHighThreshold: Optional[float] = None
    snapSpaceHarvestLowThreshold: Optional[float] = None
    metadataSizeSubscribed: Optional[int] = None
    snapSizeSubscribed: Optional[int] = None
    nonBaseSizeSubscribed: Optional[int] = None
    metadataSizeUsed: Optional[int] = None
    snapSizeUsed: Optional[int] = None
    nonBaseSizeUsed: Optional[int] = None
    rebalanceProgress: Optional[int] = None
    type: StoragePoolTypeEnum
    isAllFlash: bool

    class Config:
        json_schema_extra = {
            "example": {
                "id": "pool_123",
                "name": "TestPool",
                "raidType": "RAID5",
                "sizeFree": 1000000000,
                "sizeTotal": 2000000000,
                "sizeUsed": 500000000,
                "sizePreallocated": 500000000,
                "sizeSubscribed": 1500000000,
                "creationTime": "2023-10-01T12:00:00Z",
                "isEmpty": False,
                "type": "DYNAMIC",
                "isAllFlash": True,
                "tiers": [
                    {
                        "tierType": "FLASH",
                        "stripeWidth": "4",
                        "raidType": "RAID5",
                        "sizeTotal": 1000000000,
                        "sizeUsed": 500000000,
                        "sizeFree": 500000000,
                        "name": "FlashTier",
                        "diskCount": 10,
                        "spareDriveCount": 2,
                    }
                ],
            }
        }
