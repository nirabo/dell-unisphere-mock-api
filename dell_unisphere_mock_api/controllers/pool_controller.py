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
            if not pool_create.poolSpaceHarvestHighThreshold:
                raise HTTPException(
                    status_code=422, detail="Pool space harvest high threshold must be set when harvesting is enabled"
                )
            if not pool_create.poolSpaceHarvestLowThreshold:
                raise HTTPException(
                    status_code=422, detail="Pool space harvest low threshold must be set when harvesting is enabled"
                )

        if pool_create.isSnapHarvestEnabled:
            if not pool_create.snapSpaceHarvestHighThreshold:
                raise HTTPException(
                    status_code=422,
                    detail="Snap space harvest high threshold must be set when snap harvesting is enabled",
                )
            if not pool_create.snapSpaceHarvestLowThreshold:
                raise HTTPException(
                    status_code=422,
                    detail="Snap space harvest low threshold must be set when snap harvesting is enabled",
                )

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

    def update_pool(self, pool_id: str, update_data: PoolUpdate) -> Optional[Pool]:
        """Update a pool."""
        print(f"Pool controller: Updating pool with ID: {pool_id}")
        # Get existing pool
        current_pool = self.pool_model.get_pool(pool_id)
        if not current_pool:
            print(f"Pool controller: Pool with ID {pool_id} not found")
            return None

        # If name is being changed, check for conflicts
        if update_data.name and update_data.name != current_pool.name:
            existing_pool = self.pool_model.get_pool_by_name(update_data.name)
            if existing_pool:
                raise HTTPException(status_code=422, detail="Pool with this name already exists")

        # Validate harvest settings
        if update_data.isHarvestEnabled is True:
            if not update_data.poolSpaceHarvestHighThreshold and not current_pool.poolSpaceHarvestHighThreshold:
                raise HTTPException(
                    status_code=422, detail="Pool space harvest high threshold must be set when harvesting is enabled"
                )
            if not update_data.poolSpaceHarvestLowThreshold and not current_pool.poolSpaceHarvestLowThreshold:
                raise HTTPException(
                    status_code=422, detail="Pool space harvest low threshold must be set when harvesting is enabled"
                )

        if update_data.isSnapHarvestEnabled is True:
            if not update_data.snapSpaceHarvestHighThreshold and not current_pool.snapSpaceHarvestHighThreshold:
                raise HTTPException(
                    status_code=422,
                    detail="Snap space harvest high threshold must be set when snap harvesting is enabled",
                )
            if not update_data.snapSpaceHarvestLowThreshold and not current_pool.snapSpaceHarvestLowThreshold:
                raise HTTPException(
                    status_code=422,
                    detail="Snap space harvest low threshold must be set when snap harvesting is enabled",
                )

        print(f"Pool controller: Updated pool: {update_data}")
        return self.pool_model.update_pool(pool_id, update_data)

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
