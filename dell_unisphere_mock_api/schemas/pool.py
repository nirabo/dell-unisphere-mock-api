from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, validator


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


class HarvestStateEnum(str, Enum):
    IDLE = "IDLE"
    HARVESTING = "HARVESTING"
    PAUSED = "PAUSED"
    ERROR = "ERROR"


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
    poolSpaceHarvestHighThreshold: Optional[float] = Field(
        None, ge=0.0, le=100.0, description="High threshold percentage (0-100)"
    )
    poolSpaceHarvestLowThreshold: Optional[float] = Field(
        None, ge=0.0, le=100.0, description="Low threshold percentage (0-100)"
    )
    snapSpaceHarvestHighThreshold: Optional[float] = Field(
        None, ge=0.0, le=100.0, description="High threshold percentage (0-100)"
    )
    snapSpaceHarvestLowThreshold: Optional[float] = Field(
        None, ge=0.0, le=100.0, description="Low threshold percentage (0-100)"
    )
    isHarvestEnabled: bool = False
    isSnapHarvestEnabled: bool = False
    isFASTCacheEnabled: bool = False
    isFASTVpScheduleEnabled: bool = False
    type: str = "dynamic"

    @classmethod
    def model_validator(cls, values):
        if values.get("isHarvestEnabled"):
            if values.get("poolSpaceHarvestHighThreshold") is None:
                raise ValueError("Pool space harvest high threshold must be set when harvesting is enabled")
            if values.get("poolSpaceHarvestLowThreshold") is None:
                raise ValueError("Pool space harvest low threshold must be set when harvesting is enabled")
            if (
                values.get("poolSpaceHarvestLowThreshold") is not None
                and values.get("poolSpaceHarvestHighThreshold") is not None
                and values.get("poolSpaceHarvestLowThreshold") >= values.get("poolSpaceHarvestHighThreshold")
            ):
                raise ValueError("Low threshold must be less than high threshold")

        if values.get("isSnapHarvestEnabled"):
            if values.get("snapSpaceHarvestHighThreshold") is None:
                raise ValueError("Snap space harvest high threshold must be set when snap harvesting is enabled")
            if values.get("snapSpaceHarvestLowThreshold") is None:
                raise ValueError("Snap space harvest low threshold must be set when snap harvesting is enabled")
            if (
                values.get("snapSpaceHarvestLowThreshold") is not None
                and values.get("snapSpaceHarvestHighThreshold") is not None
                and values.get("snapSpaceHarvestLowThreshold") >= values.get("snapSpaceHarvestHighThreshold")
            ):
                raise ValueError("Low threshold must be less than high threshold")
        return values


class PoolUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=85)
    description: Optional[str] = Field(None, max_length=170)
    alertThreshold: Optional[int] = Field(None, ge=50, le=84)
    poolSpaceHarvestHighThreshold: Optional[float] = Field(None, ge=0.0, le=100.0)
    poolSpaceHarvestLowThreshold: Optional[float] = Field(None, ge=0.0, le=100.0)
    snapSpaceHarvestHighThreshold: Optional[float] = Field(None, ge=0.0, le=100.0)
    snapSpaceHarvestLowThreshold: Optional[float] = Field(None, ge=0.0, le=100.0)
    isHarvestEnabled: Optional[bool] = None
    isSnapHarvestEnabled: Optional[bool] = None
    isFASTCacheEnabled: Optional[bool] = None
    isFASTVpScheduleEnabled: Optional[bool] = None

    @classmethod
    def model_validator(cls, values):
        if values.get("isHarvestEnabled"):
            if values.get("poolSpaceHarvestHighThreshold") is None:
                raise ValueError("Pool space harvest high threshold must be set when harvesting is enabled")
            if values.get("poolSpaceHarvestLowThreshold") is None:
                raise ValueError("Pool space harvest low threshold must be set when harvesting is enabled")
            if (
                values.get("poolSpaceHarvestLowThreshold") is not None
                and values.get("poolSpaceHarvestHighThreshold") is not None
                and values.get("poolSpaceHarvestLowThreshold") >= values.get("poolSpaceHarvestHighThreshold")
            ):
                raise ValueError("Low threshold must be less than high threshold")

        if values.get("isSnapHarvestEnabled"):
            if values.get("snapSpaceHarvestHighThreshold") is None:
                raise ValueError("Snap space harvest high threshold must be set when snap harvesting is enabled")
            if values.get("snapSpaceHarvestLowThreshold") is None:
                raise ValueError("Snap space harvest low threshold must be set when snap harvesting is enabled")
            if (
                values.get("snapSpaceHarvestLowThreshold") is not None
                and values.get("snapSpaceHarvestHighThreshold") is not None
                and values.get("snapSpaceHarvestLowThreshold") >= values.get("snapSpaceHarvestHighThreshold")
            ):
                raise ValueError("Low threshold must be less than high threshold")
        return values


class Pool(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    raidType: RaidTypeEnum
    sizeTotal: int
    sizeFree: int = 0
    sizeUsed: int = 0
    sizePreallocated: int = 0
    dataReductionSizeSaved: int = 0
    dataReductionPercent: int = 0
    dataReductionRatio: float = 1.0
    flashPercentage: int = 100
    sizeSubscribed: int = Field(0, description="Size of space requested by storage resources")
    alertThreshold: int = Field(50, ge=50, le=84)
    hasDataReductionEnabledLuns: bool = False
    hasDataReductionEnabledFs: bool = False
    isFASTCacheEnabled: bool = False
    creationTime: datetime
    isEmpty: bool = True
    poolFastVP: Optional[PoolFASTVP] = None
    tiers: List[PoolTier] = Field(default_factory=list)
    isHarvestEnabled: bool = False
    harvestState: Optional[HarvestStateEnum] = HarvestStateEnum.IDLE
    isSnapHarvestEnabled: bool = False
    poolSpaceHarvestHighThreshold: Optional[float] = Field(None, ge=0.0, le=100.0)
    poolSpaceHarvestLowThreshold: Optional[float] = Field(None, ge=0.0, le=100.0)
    snapSpaceHarvestHighThreshold: Optional[float] = Field(None, ge=0.0, le=100.0)
    snapSpaceHarvestLowThreshold: Optional[float] = Field(None, ge=0.0, le=100.0)
    metadataSizeSubscribed: int = 0
    snapSizeSubscribed: int = 0
    nonBaseSizeSubscribed: int = 0
    metadataSizeUsed: int = 0
    snapSizeUsed: int = 0
    nonBaseSizeUsed: int = 0
    rebalanceProgress: Optional[int] = None
    type: str = "dynamic"
    isAllFlash: bool = True

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


class StorageConfiguration(BaseModel):
    raidType: RaidTypeEnum
    diskGroup: str
    diskCount: int
    stripeWidth: int


class PoolAutoConfigurationResponse(BaseModel):
    name: str
    description: str
    storageConfiguration: StorageConfiguration
    alertThreshold: int = Field(50, ge=50, le=84)
    poolSpaceHarvestHighThreshold: float = Field(85.0, ge=0.0, le=100.0)
    poolSpaceHarvestLowThreshold: float = Field(75.0, ge=0.0, le=100.0)
    snapSpaceHarvestHighThreshold: float = Field(85.0, ge=0.0, le=100.0)
    snapSpaceHarvestLowThreshold: float = Field(75.0, ge=0.0, le=100.0)
    isFastCacheEnabled: bool = False
    isFASTVpScheduleEnabled: bool = False
    isDiskTechnologyMixed: bool = False
    maxSizeLimit: int
    maxDiskNumberLimit: int
    isMaxSizeLimitExceeded: bool = False
    isMaxDiskNumberLimitExceeded: bool = False
    isRPMMixed: bool = False
