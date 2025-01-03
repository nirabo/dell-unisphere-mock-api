import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from ..schemas.pool import Pool, PoolCreate, PoolUpdate

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PoolModel:
    """In-memory model for managing pool instances."""

    _instance: "PoolModel" = None
    pools: Dict[str, Pool]  # Class-level type annotation

    def __new__(cls) -> "PoolModel":
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.pools = {}  # Initialize in __new__
        return cls._instance

    def __init__(self) -> None:
        """Initialize the pool model."""
        if not hasattr(self, "initialized"):
            # No initialization needed as it's handled in __new__
            self.initialized = True

    def create_pool(self, pool: Pool) -> Pool:
        """
        Create a new pool instance.

        Args:
            pool: Pool instance to store.

        Returns:
            The created pool instance.
        """
        logger.debug(f"Creating pool with ID: {pool.id}")
        logger.debug(f"Pool data: {pool.model_dump()}")

        # Store the pool
        self.pools[pool.id] = pool
        logger.debug(f"Stored pool. Available pools: {list(self.pools.keys())}")
        return pool

    def get_pool(self, pool_id: str) -> Optional[Pool]:
        """
        Retrieve a pool by its ID.

        Args:
            pool_id: The ID of the pool to retrieve.

        Returns:
            The pool instance if found, otherwise None.
        """
        logger.debug(f"Looking for pool with ID: {pool_id}")
        logger.debug(f"Available pool IDs: {list(self.pools.keys())}")
        pool = self.pools.get(pool_id)
        logger.debug(f"Found pool: {pool}")
        return pool

    def list_pools(self) -> List[Pool]:
        """
        List all pools.

        Returns:
            A list of all pool instances.
        """
        return list(self.pools.values())

    def update_pool(self, pool_id: str, pool_update: PoolUpdate) -> Optional[Pool]:
        """Update a pool by its ID."""
        logger.debug(f"Updating pool with ID: {pool_id}")
        pool = self.pools.get(pool_id)
        if pool:
            # Update the pool with the provided data
            update_dict = {k: v for k, v in pool_update.model_dump().items() if v is not None}
            logger.debug(f"Applying updates: {update_dict}")

            # Create a new pool instance with updated data
            updated_data = pool.model_dump()
            updated_data.update(update_dict)
            updated_pool = Pool(**updated_data)

            # Store the updated pool
            self.pools[pool_id] = updated_pool
            logger.debug(f"Updated pool: {updated_pool}")
            return updated_pool
        logger.debug(f"Pool with ID {pool_id} not found")
        return None

    def delete_pool(self, pool_id: str) -> bool:
        """
        Delete a pool instance.

        Args:
            pool_id: The ID of the pool to delete.

        Returns:
            True if the pool was deleted, False if it was not found.
        """
        logger.debug(f"Deleting pool with ID: {pool_id}")
        if pool_id in self.pools:
            del self.pools[pool_id]
            logger.debug(f"Deleted pool with ID: {pool_id}")
            return True
        logger.debug(f"Pool with ID {pool_id} not found")
        return False

    def get_pool_by_name(self, name: str) -> Optional[Pool]:
        """
        Retrieve a pool by its name.

        Args:
            name: The name of the pool to retrieve.

        Returns:
            The pool instance if found, otherwise None.
        """
        logger.debug(f"Looking for pool with name: {name}")
        for pool in self.pools.values():
            if pool.name == name:
                logger.debug(f"Found pool with name: {name}")
                return pool
        logger.debug(f"Pool with name {name} not found")
        return None
