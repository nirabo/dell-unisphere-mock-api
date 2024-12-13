from typing import Dict, List, Optional
from uuid import UUID, uuid4

from dell_unisphere_mock_api.schemas.pool import Pool, PoolCreate, PoolUpdate


class PoolModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.pools: Dict[str, Pool] = {}
        return cls._instance

    def create_pool(self, pool: PoolCreate) -> Pool:
        """Create a new storage pool."""
        pool_id = str(uuid4())
        pool_dict = pool.model_dump()
        pool_dict["id"] = pool_id
        
        new_pool = Pool(**pool_dict)
        self.pools[pool_id] = new_pool
        return new_pool

    def get_pool(self, pool_id: str) -> Optional[Pool]:
        """Get a pool by ID."""
        return self.pools.get(pool_id)

    def get_pool_by_name(self, name: str) -> Optional[Pool]:
        """Get a pool by name."""
        for pool in self.pools.values():
            if pool.name == name:
                return pool
        return None

    def list_pools(self) -> List[Pool]:
        """List all pools."""
        return list(self.pools.values())

    def update_pool(self, pool_id: str, pool_update: PoolUpdate) -> Optional[Pool]:
        """Update a pool."""
        if pool_id not in self.pools:
            return None
        
        current_pool = self.pools[pool_id]
        update_data = pool_update.model_dump(exclude_unset=True)
        
        updated_pool_dict = current_pool.model_dump()
        updated_pool_dict.update(update_data)
        
        updated_pool = Pool(**updated_pool_dict)
        self.pools[pool_id] = updated_pool
        return updated_pool

    def delete_pool(self, pool_id: str) -> bool:
        """Delete a pool by ID."""
        if pool_id in self.pools:
            del self.pools[pool_id]
            return True
        return False
