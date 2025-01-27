from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, Request

from dell_unisphere_mock_api.core.response import UnityResponseFormatter
from dell_unisphere_mock_api.core.response_models import ApiResponse
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

    def create_pool(self, pool_create: PoolCreate, request: Request) -> ApiResponse[Pool]:
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

        pool_dict = pool_create.model_dump()
        pool_id = str(uuid4())
        print(f"Pool controller: Generated pool ID: {pool_id}")
        pool_dict.update(
            {
                "id": pool_id,
                "creationTime": datetime.now(timezone.utc),
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

        formatter = UnityResponseFormatter(request)
        return formatter.format_collection([result], entry_links={0: [{"rel": "self", "href": f"/{pool_id}"}]})

    def get_pool(self, pool_id: str, request: Request) -> ApiResponse[Pool]:
        """Get a pool by ID."""
        print(f"Pool controller: Looking for pool with ID: {pool_id}")
        pool = self.pool_model.get_pool(pool_id)
        if not pool:
            raise HTTPException(status_code=404, detail=f"Pool with ID '{pool_id}' not found")

        formatter = UnityResponseFormatter(request)
        return formatter.format_collection([pool], entry_links={0: [{"rel": "self", "href": f"/{pool_id}"}]})

    def get_pool_by_name(self, name: str, request: Request) -> ApiResponse[Pool]:
        """Get a pool by name."""
        print(f"Pool controller: Looking for pool with name: {name}")
        pool = self.pool_model.get_pool_by_name(name)
        if not pool:
            raise HTTPException(status_code=404, detail=f"Pool with name '{name}' not found")

        formatter = UnityResponseFormatter(request)
        return formatter.format_collection([pool], entry_links={0: [{"rel": "self", "href": f"/{pool.id}"}]})

    def list_pools(self, request: Request) -> ApiResponse[Pool]:
        """List all pools."""
        print("Pool controller: Listing all pools")
        pools = self.pool_model.list_pools()
        formatter = UnityResponseFormatter(request)
        entry_links = {i: [{"rel": "self", "href": f"/{pool.id}"}] for i, pool in enumerate(pools)}
        return formatter.format_collection(pools, entry_links=entry_links)

    def update_pool(self, pool_id: str, pool_update: PoolUpdate, request: Request) -> ApiResponse[Pool]:
        """Update a pool."""
        print(f"Pool controller: Updating pool with ID: {pool_id}")
        pool = self.pool_model.get_pool(pool_id)
        if not pool:
            raise HTTPException(status_code=404, detail=f"Pool with ID '{pool_id}' not found")

        # Validate harvest settings if being updated
        if pool_update.isHarvestEnabled is not None and pool_update.isHarvestEnabled:
            if (
                pool_update.poolSpaceHarvestHighThreshold is not None
                and pool_update.poolSpaceHarvestLowThreshold is not None
                and pool_update.poolSpaceHarvestLowThreshold >= pool_update.poolSpaceHarvestHighThreshold
            ):
                raise HTTPException(status_code=422, detail="Low threshold must be less than high threshold")

        if pool_update.isSnapHarvestEnabled is not None and pool_update.isSnapHarvestEnabled:
            if (
                pool_update.snapSpaceHarvestHighThreshold is not None
                and pool_update.snapSpaceHarvestLowThreshold is not None
                and pool_update.snapSpaceHarvestLowThreshold >= pool_update.snapSpaceHarvestHighThreshold
            ):
                raise HTTPException(status_code=422, detail="Low threshold must be less than high threshold")

        # Update the pool
        updated_pool = self.pool_model.update_pool(pool_id, pool_update)

        formatter = UnityResponseFormatter(request)
        return formatter.format_collection([updated_pool], entry_links={0: [{"rel": "self", "href": f"/{pool_id}"}]})

    def delete_pool(self, pool_id: str, request: Request) -> ApiResponse[None]:
        """Delete a pool."""
        print(f"Pool controller: Deleting pool with ID: {pool_id}")
        pool = self.pool_model.get_pool(pool_id)
        if not pool:
            raise HTTPException(status_code=404, detail=f"Pool with ID '{pool_id}' not found")

        self.pool_model.delete_pool(pool_id)
        formatter = UnityResponseFormatter(request)
        return formatter.format_collection([], entry_links={})

    def delete_pool_by_name(self, name: str, request: Request) -> ApiResponse[None]:
        """Delete a pool by name."""
        print(f"Pool controller: Deleting pool with name: {name}")
        pool = self.pool_model.get_pool_by_name(name)
        if not pool:
            raise HTTPException(status_code=404, detail=f"Pool with name '{name}' not found")

        self.pool_model.delete_pool(pool.id)
        formatter = UnityResponseFormatter(request)
        return formatter.format_collection([], entry_links={})

    def recommend_auto_configuration(self, request: Request) -> ApiResponse[PoolAutoConfigurationResponse]:
        """
        Generate recommended pool configurations based on available drives.
        In this mock implementation, we'll return a sample configuration.
        In a real system, this would analyze the actual available drives.
        """
        # Sample configuration
        storage_config = StorageConfiguration(
            raidType=RaidTypeEnum.RAID5,
            stripeWidth=5,
            diskCount=5,
            diskGroup="dg_ssd",
        )

        config = PoolAutoConfigurationResponse(
            name="Recommended Pool Configuration",
            description="Auto-generated pool configuration based on available drives",
            storageConfiguration=storage_config,
            maxSizeLimit=109951162777600,  # 100TB
            maxDiskNumberLimit=180,  # Maximum number of disks allowed in a pool
        )

        formatter = UnityResponseFormatter(request)
        return formatter.format_collection([config], entry_links={0: [{"rel": "self", "href": "/auto_config"}]})
