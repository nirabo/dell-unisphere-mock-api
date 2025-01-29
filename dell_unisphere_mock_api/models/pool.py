import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from dell_unisphere_mock_api.schemas.pool import (
    HarvestStateEnum,
    Pool,
    PoolAutoConfigurationResponse,
    PoolCreate,
    PoolUpdate,
    RaidTypeEnum,
    StorageConfiguration,
)


class PoolModel:
    """Model for managing storage pools."""

    _instance = None
    pools: Dict[str, Pool] = {}  # Initialize as class variable

    def __new__(cls) -> "PoolModel":
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the pool model."""
        # No initialization needed as it's handled in __new__
        pass

    def create_pool(self, pool_create: PoolCreate) -> Pool:
        """Create a new storage pool."""
        logging.debug(f"Pool model: Creating pool with name: {pool_create.name}")
        pool_dict = pool_create.model_dump()
        logging.debug(f"Pool model: Initial pool data: {pool_dict}")

        # Generate new ID
        pool_id = str(len(self.pools) + 1)
        pool_dict["id"] = pool_id

        # Set default values
        pool_dict["health"] = {
            "value": 5,
            "descriptionIds": ["ALRT_COMPONENT_OK"],
            "descriptions": ["The component is operating normally."],
        }
        pool_dict["sizeFree"] = pool_dict["sizeTotal"]
        pool_dict["sizeUsed"] = 0
        pool_dict["sizePreallocated"] = 0
        pool_dict["dataReductionSizeSaved"] = 0
        pool_dict["dataReductionPercent"] = 0
        pool_dict["dataReductionRatio"] = 1.0
        pool_dict["flashPercentage"] = 100
        pool_dict["sizeSubscribed"] = 0
        pool_dict["alertThreshold"] = pool_dict.get("alertThreshold", 70)
        pool_dict["hasDataReductionEnabledLuns"] = False
        pool_dict["hasDataReductionEnabledFs"] = False
        pool_dict["isFASTCacheEnabled"] = pool_dict.get("isFASTCacheEnabled", False)
        pool_dict["creationTime"] = datetime.now(timezone.utc)
        pool_dict["modificationTime"] = datetime.now(timezone.utc)
        pool_dict["isEmpty"] = True
        pool_dict["poolFastVP"] = None
        pool_dict["tiers"] = []
        pool_dict["isHarvestEnabled"] = pool_dict.get("isHarvestEnabled", False)
        pool_dict["harvestState"] = HarvestStateEnum.IDLE
        pool_dict["isSnapHarvestEnabled"] = pool_dict.get("isSnapHarvestEnabled", False)
        pool_dict["poolSpaceHarvestHighThreshold"] = pool_dict.get("poolSpaceHarvestHighThreshold", None)
        pool_dict["poolSpaceHarvestLowThreshold"] = pool_dict.get("poolSpaceHarvestLowThreshold", None)
        pool_dict["snapSpaceHarvestHighThreshold"] = pool_dict.get("snapSpaceHarvestHighThreshold", None)
        pool_dict["snapSpaceHarvestLowThreshold"] = pool_dict.get("snapSpaceHarvestLowThreshold", None)
        pool_dict["metadataSizeSubscribed"] = 0
        pool_dict["snapSizeSubscribed"] = 0
        pool_dict["nonBaseSizeSubscribed"] = 0
        pool_dict["metadataSizeUsed"] = 0
        pool_dict["snapSizeUsed"] = 0
        pool_dict["nonBaseSizeUsed"] = 0
        pool_dict["rebalanceProgress"] = None
        pool_dict["type"] = pool_dict.get("type", "dynamic")
        pool_dict["isAllFlash"] = True

        # Create pool object
        pool = Pool(**pool_dict)
        logging.debug(f"Pool model: Created pool object: {pool}")

        # Store in dictionary
        self.pools[pool_id] = pool
        logging.debug(f"Pool model: Stored pool with ID {pool_id}")

        return pool

    def get_pool(self, pool_id: str) -> Optional[Pool]:
        """Get a pool by ID."""
        logging.debug(f"Pool model: Getting pool with ID: {pool_id}")
        return self.pools.get(pool_id)

    def get_pool_by_name(self, name: str) -> Optional[Pool]:
        """Get a pool by name."""
        logging.debug(f"Pool model: Getting pool with name: {name}")
        for pool in self.pools.values():
            if pool.name == name:
                return pool
        return None

    def list_pools(self) -> List[Pool]:
        """List all pools."""
        logging.debug("Pool model: Listing pools")
        # Convert to list and ensure all items are Pool objects
        pools = []
        for pool_data in self.pools.values():
            if isinstance(pool_data, dict):
                pools.append(Pool(**pool_data))
            else:
                pools.append(pool_data)
        return pools

    def update_pool(self, pool_id: str, pool_update: PoolUpdate) -> Optional[Pool]:
        """Update a pool."""
        logging.debug(f"Pool model: Updating pool with ID: {pool_id}")
        pool = self.pools.get(pool_id)
        if not pool:
            return None

        # Update fields
        update_dict = pool_update.model_dump(exclude_unset=True)
        pool_dict = pool.model_dump()
        pool_dict.update(update_dict)
        pool_dict["modificationTime"] = datetime.now(timezone.utc)

        # Create updated pool object
        updated_pool = Pool(**pool_dict)
        logging.debug(f"Pool model: Updated pool object: {updated_pool}")

        # Store in dictionary
        self.pools[pool_id] = updated_pool
        logging.debug(f"Pool model: Stored updated pool with ID {pool_id}")

        return updated_pool

    def delete_pool(self, pool_id: str) -> bool:
        """Delete a pool."""
        logging.debug(f"Pool model: Deleting pool with ID: {pool_id}")
        if pool_id in self.pools:
            del self.pools[pool_id]
            logging.debug(f"Pool model: Deleted pool with ID {pool_id}")
            return True
        return False

    def delete_pool_by_name(self, name: str) -> bool:
        """Delete a pool by name."""
        logging.debug(f"Pool model: Deleting pool with name: {name}")
        for pool_id, pool in self.pools.items():
            if pool.name == name:
                del self.pools[pool_id]
                logging.debug(f"Pool model: Deleted pool with ID {pool_id}")
                return True
        return False

    def recommend_auto_configuration(self) -> List[PoolAutoConfigurationResponse]:
        """Get recommended pool configurations based on available drives."""
        logging.debug("Pool model: Getting recommended pool configurations")

        # Example configurations
        configs = [
            PoolAutoConfigurationResponse(
                name="Recommended Pool 1",
                description="High Performance SSD Pool",
                storageConfiguration=StorageConfiguration(
                    raidType=RaidTypeEnum.RAID5,
                    diskGroup="SAS_FLASH_4",
                    diskCount=5,
                    stripeWidth=4,
                ),
                maxSizeLimit=10995116277760,  # 10TB
                maxDiskNumberLimit=16,
            ),
            PoolAutoConfigurationResponse(
                name="Recommended Pool 2",
                description="Capacity Optimized Pool",
                storageConfiguration=StorageConfiguration(
                    raidType=RaidTypeEnum.RAID6,
                    diskGroup="SAS_FLASH_4",
                    diskCount=8,
                    stripeWidth=6,
                ),
                maxSizeLimit=21990232555520,  # 20TB
                maxDiskNumberLimit=24,
            ),
        ]

        logging.debug(f"Pool model: Found {len(configs)} recommended configurations")
        return configs
