from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from ..schemas.pool import Pool, PoolCreate, PoolUpdate


class PoolModel:
    """In-memory model for managing pool instances."""

    def __init__(self):
        self.pools: Dict[str, Pool] = {}

    def create_pool(self, pool_data: PoolCreate) -> Pool:
        """
        Create a new pool instance.

        Args:
            pool_data: Data for creating the pool.

        Returns:
            The created pool instance.
        """
        # Generate a unique ID for the pool
        pool_id = f"pool_{uuid4().hex}"
        created_time = datetime.utcnow()

        # Create default values for calculated fields
        default_values = {
            "id": pool_id,
            "creationTime": created_time,
            "sizeFree": pool_data.sizeTotal,
            "sizeUsed": 0,
            "sizePreallocated": 0,
            "dataReductionSizeSaved": 0,
            "dataReductionPercent": 0,
            "dataReductionRatio": 1.0,
            "flashPercentage": 100 if pool_data.type == "dynamic" else 0,
            "sizeSubscribed": pool_data.sizeTotal,
            "hasDataReductionEnabledLuns": False,
            "hasDataReductionEnabledFs": False,
            "isEmpty": True,
            "tiers": [],
            "harvestState": None,
            "metadataSizeSubscribed": 0,
            "snapSizeSubscribed": 0,
            "nonBaseSizeSubscribed": 0,
            "metadataSizeUsed": 0,
            "snapSizeUsed": 0,
            "nonBaseSizeUsed": 0,
            "rebalanceProgress": None,
            "isAllFlash": True if pool_data.type == "dynamic" else False,
            "poolFastVP": None,
        }

        # Create the pool instance
        pool = Pool(**{**default_values, **pool_data.dict()})

        # Store the pool
        self.pools[pool_id] = pool
        return pool

    def get_pool(self, pool_id: str) -> Optional[Pool]:
        """
        Retrieve a pool by its ID.

        Args:
            pool_id: The ID of the pool to retrieve.

        Returns:
            The pool instance if found, otherwise None.
        """
        return self.pools.get(pool_id)

    def list_pools(self) -> List[Pool]:
        """
        List all pools.

        Returns:
            A list of all pool instances.
        """
        return list(self.pools.values())

    def update_pool(self, pool_id: str, update_data: PoolUpdate) -> Optional[Pool]:
        """
        Update a pool instance.

        Args:
            pool_id: The ID of the pool to update.
            update_data: Data to update the pool with.

        Returns:
            The updated pool instance if found, otherwise None.
        """
        pool = self.pools.get(pool_id)
        if pool:
            # Update the pool with the provided data
            update_dict = update_data.dict(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(pool, key, value)
            self.pools[pool_id] = pool
        return pool

    def delete_pool(self, pool_id: str) -> bool:
        """
        Delete a pool instance.

        Args:
            pool_id: The ID of the pool to delete.

        Returns:
            True if the pool was deleted, False if it was not found.
        """
        if pool_id in self.pools:
            del self.pools[pool_id]
            return True
        return False

    def get_pool_by_name(self, name: str) -> Optional[Pool]:
        """
        Retrieve a pool by its name.

        Args:
            name: The name of the pool to retrieve.

        Returns:
            The pool instance if found, otherwise None.
        """
        for pool in self.pools.values():
            if pool.name == name:
                return pool
        return None
