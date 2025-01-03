from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import HTTPException

from dell_unisphere_mock_api.models.pool import PoolModel
from dell_unisphere_mock_api.schemas.pool import (
    HarvestStateEnum,
    Pool,
    PoolAutoConfigurationResponse,
    PoolCreate,
    PoolUpdate,
    RaidTypeEnum,
    StorageConfiguration,
)


class PoolController:
    def __init__(self):
        self.pool_model = PoolModel()

    def create_pool(self, pool_create: PoolCreate) -> Pool:
        """Create a new storage pool."""
        print(f"Pool controller: Creating pool with name: {pool_create.name}")
        # Check if pool with same name exists
        existing_pool = self.pool_model.get_pool_by_name(pool_create.name)
        if existing_pool:
            raise HTTPException(status_code=422, detail=f"Pool with name '{pool_create.name}' already exists")

        # Validate harvest settings
        if pool_create.isHarvestEnabled:
            if pool_create.poolSpaceHarvestHighThreshold is None:
                raise HTTPException(
                    status_code=422, detail="Pool space harvest high threshold must be set when harvesting is enabled"
                )
            if pool_create.poolSpaceHarvestLowThreshold is None:
                raise HTTPException(
                    status_code=422, detail="Pool space harvest low threshold must be set when harvesting is enabled"
                )
            if (
                pool_create.poolSpaceHarvestLowThreshold is not None
                and pool_create.poolSpaceHarvestHighThreshold is not None
                and pool_create.poolSpaceHarvestLowThreshold >= pool_create.poolSpaceHarvestHighThreshold
            ):
                raise HTTPException(status_code=422, detail="Low threshold must be less than high threshold")

        if pool_create.isSnapHarvestEnabled:
            if pool_create.snapSpaceHarvestHighThreshold is None:
                raise HTTPException(
                    status_code=422,
                    detail="Snap space harvest high threshold must be set when snap harvesting is enabled",
                )
            if pool_create.snapSpaceHarvestLowThreshold is None:
                raise HTTPException(
                    status_code=422,
                    detail="Snap space harvest low threshold must be set when snap harvesting is enabled",
                )
            if (
                pool_create.snapSpaceHarvestLowThreshold is not None
                and pool_create.snapSpaceHarvestHighThreshold is not None
                and pool_create.snapSpaceHarvestLowThreshold >= pool_create.snapSpaceHarvestHighThreshold
            ):
                raise HTTPException(status_code=422, detail="Low threshold must be less than high threshold")

        # Create the pool
        pool_dict = pool_create.model_dump()
        pool_id = f"pool_{uuid4().hex}"
        print(f"Pool controller: Generated pool ID: {pool_id}")
        pool_dict.update(
            {
                "id": pool_id,
                "creationTime": datetime.utcnow(),
                "sizeFree": pool_create.sizeTotal,
                "sizeUsed": 0,
                "sizePreallocated": 0,
                "sizeSubscribed": pool_create.sizeTotal,
                "harvestState": HarvestStateEnum.IDLE,
                "isEmpty": True,
                "hasDataReductionEnabledLuns": False,
                "hasDataReductionEnabledFs": False,
                "dataReductionSizeSaved": 0,
                "dataReductionPercent": 0,
                "dataReductionRatio": 1.0,
                "flashPercentage": 100,
                "metadataSizeSubscribed": 0,
                "snapSizeSubscribed": 0,
                "nonBaseSizeSubscribed": 0,
                "metadataSizeUsed": 0,
                "snapSizeUsed": 0,
                "nonBaseSizeUsed": 0,
                "isAllFlash": True,
                "tiers": [],
                "poolFastVP": None,
                "type": "dynamic",
                "rebalanceProgress": None,
            }
        )
        print(f"Pool controller: Pool data before creation: {pool_dict}")
        pool = Pool(**pool_dict)
        print(f"Pool controller: Created pool instance: {pool}")
        result = self.pool_model.create_pool(pool)
        print(f"Pool controller: Pool creation result: {result}")
        return result

    def get_pool(self, pool_id: str) -> Optional[Pool]:
        """Get a pool by ID."""
        print(f"Pool controller: Looking for pool with ID: {pool_id}")
        pool = self.pool_model.get_pool(pool_id)
        print(f"Pool controller: Found pool: {pool}")
        return pool

    def get_pool_by_name(self, name: str) -> Optional[Pool]:
        """Get a pool by name."""
        print(f"Pool controller: Looking for pool with name: {name}")
        pool = self.pool_model.get_pool_by_name(name)
        print(f"Pool controller: Found pool: {pool}")
        return pool

    def list_pools(self) -> List[Pool]:
        """List all pools."""
        print("Pool controller: Listing all pools")
        pools = self.pool_model.list_pools()
        print(f"Pool controller: Listed pools: {pools}")
        return pools

    def update_pool(self, pool_id: str, pool_update: PoolUpdate) -> Optional[Pool]:
        """Update a pool."""
        print(f"Pool controller: Updating pool with ID: {pool_id}")
        print(f"Pool controller: Update data: {pool_update.model_dump()}")

        # Get existing pool
        pool = self.pool_model.get_pool(pool_id)
        if not pool:
            print(f"Pool controller: Pool not found with ID: {pool_id}")
            raise HTTPException(status_code=404, detail=f"Pool with ID '{pool_id}' not found")

        # Validate harvest settings
        if pool_update.isHarvestEnabled is True:  # Only validate if explicitly set to True
            if pool_update.poolSpaceHarvestHighThreshold is None and pool.poolSpaceHarvestHighThreshold is None:
                print("Pool controller: Pool space harvest high threshold must be set when enabling harvesting")
                raise HTTPException(
                    status_code=422, detail="Pool space harvest high threshold must be set when harvesting is enabled"
                )
            if pool_update.poolSpaceHarvestLowThreshold is None and pool.poolSpaceHarvestLowThreshold is None:
                print("Pool controller: Pool space harvest low threshold must be set when enabling harvesting")
                raise HTTPException(
                    status_code=422, detail="Pool space harvest low threshold must be set when harvesting is enabled"
                )

            # Check thresholds if either is being updated
            high_threshold = (
                pool_update.poolSpaceHarvestHighThreshold
                if pool_update.poolSpaceHarvestHighThreshold is not None
                else pool.poolSpaceHarvestHighThreshold
            )
            low_threshold = (
                pool_update.poolSpaceHarvestLowThreshold
                if pool_update.poolSpaceHarvestLowThreshold is not None
                else pool.poolSpaceHarvestLowThreshold
            )

            if high_threshold is not None and low_threshold is not None and low_threshold >= high_threshold:
                print("Pool controller: Low threshold must be less than high threshold")
                raise HTTPException(status_code=422, detail="Low threshold must be less than high threshold")

        if pool_update.isSnapHarvestEnabled is True:  # Only validate if explicitly set to True
            if pool_update.snapSpaceHarvestHighThreshold is None and pool.snapSpaceHarvestHighThreshold is None:
                print("Pool controller: Snap space harvest high threshold must be set when enabling snap harvesting")
                raise HTTPException(
                    status_code=422,
                    detail="Snap space harvest high threshold must be set when snap harvesting is enabled",
                )
            if pool_update.snapSpaceHarvestLowThreshold is None and pool.snapSpaceHarvestLowThreshold is None:
                print("Pool controller: Snap space harvest low threshold must be set when enabling snap harvesting")
                raise HTTPException(
                    status_code=422,
                    detail="Snap space harvest low threshold must be set when snap harvesting is enabled",
                )

            # Check thresholds if either is being updated
            high_threshold = (
                pool_update.snapSpaceHarvestHighThreshold
                if pool_update.snapSpaceHarvestHighThreshold is not None
                else pool.snapSpaceHarvestHighThreshold
            )
            low_threshold = (
                pool_update.snapSpaceHarvestLowThreshold
                if pool_update.snapSpaceHarvestLowThreshold is not None
                else pool.snapSpaceHarvestLowThreshold
            )

            if high_threshold is not None and low_threshold is not None and low_threshold >= high_threshold:
                print("Pool controller: Low threshold must be less than high threshold")
                raise HTTPException(status_code=422, detail="Low threshold must be less than high threshold")

        # Update the pool
        print(f"Pool controller: Updating pool with data: {pool_update.model_dump()}")
        result = self.pool_model.update_pool(pool_id, pool_update)
        print(f"Pool controller: Update result: {result}")
        return result

    def delete_pool(self, pool_id: str) -> bool:
        """Delete a pool."""
        print(f"Pool controller: Deleting pool with ID: {pool_id}")
        return self.pool_model.delete_pool(pool_id)

    def delete_pool_by_name(self, name: str) -> bool:
        """Delete a pool by name."""
        print(f"Pool controller: Deleting pool with name: {name}")
        pool = self.pool_model.get_pool_by_name(name)
        if not pool:
            print(f"Pool controller: Pool with name {name} not found")
            return False
        return self.pool_model.delete_pool(pool.id)

    def recommend_auto_configuration(self) -> List[PoolAutoConfigurationResponse]:
        """
        Generate recommended pool configurations based on available drives.
        In this mock implementation, we'll return some sample configurations.
        In a real system, this would analyze the actual available drives.
        """
        print("Pool controller: Recommending auto configurations")
        recommendations = []

        # Sample recommendation for SSD drives
        ssd_config = PoolAutoConfigurationResponse(
            name="recommended_ssd_pool",
            description="Recommended pool configuration for SSD drives",
            storageConfiguration=StorageConfiguration(
                raidType=RaidTypeEnum.RAID5, diskGroup="dg_ssd", diskCount=5, stripeWidth=5  # 4+1 RAID5
            ),
            maxSizeLimit=10995116277760,  # 10TB
            maxDiskNumberLimit=16,
            isFastCacheEnabled=False,  # Not needed for all-flash
            isDiskTechnologyMixed=False,
            isRPMMixed=False,
        )
        recommendations.append(ssd_config)

        # Sample recommendation for SAS drives
        sas_config = PoolAutoConfigurationResponse(
            name="recommended_sas_pool",
            description="Recommended pool configuration for SAS drives",
            storageConfiguration=StorageConfiguration(
                raidType=RaidTypeEnum.RAID6, diskGroup="dg_sas", diskCount=8, stripeWidth=8  # 6+2 RAID6
            ),
            maxSizeLimit=21990232555520,  # 20TB
            maxDiskNumberLimit=24,
            isFastCacheEnabled=True,  # Enable FAST Cache for HDD
            isDiskTechnologyMixed=False,
            isRPMMixed=False,
        )
        recommendations.append(sas_config)

        print(f"Pool controller: Recommended configurations: {recommendations}")
        return recommendations
