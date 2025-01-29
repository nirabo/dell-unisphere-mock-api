from typing import List, Optional

from fastapi import HTTPException, Request

from dell_unisphere_mock_api.core.response import UnityResponseFormatter
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.models.pool import PoolModel
from dell_unisphere_mock_api.schemas.pool import Pool, PoolAutoConfigurationResponse, PoolCreate, PoolUpdate


class PoolController:
    """Controller for managing storage pools."""

    def __init__(self):
        """Initialize the pool controller."""
        self.pool_model = PoolModel()

    async def create_pool(self, pool_create: PoolCreate, request: Request) -> ApiResponse[Pool]:
        """Create a new storage pool."""
        print(f"Pool controller: Creating pool with name: {pool_create.name}")
        # Check if pool with same name exists
        existing_pool = self.pool_model.get_pool_by_name(pool_create.name)
        if existing_pool:
            raise HTTPException(status_code=409, detail=f"Pool with name '{pool_create.name}' already exists")

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
                    status_code=422, detail="Snap space harvest high threshold must be set when harvesting is enabled"
                )
            if pool_create.snapSpaceHarvestLowThreshold is None:
                raise HTTPException(
                    status_code=422, detail="Snap space harvest low threshold must be set when harvesting is enabled"
                )
            if (
                pool_create.snapSpaceHarvestLowThreshold is not None
                and pool_create.snapSpaceHarvestHighThreshold is not None
                and pool_create.snapSpaceHarvestLowThreshold >= pool_create.snapSpaceHarvestHighThreshold
            ):
                raise HTTPException(status_code=422, detail="Low threshold must be less than high threshold")

        # Create the pool
        pool = self.pool_model.create_pool(pool_create)
        print(f"Pool controller: Created pool: {pool}")

        # Format response
        formatter = UnityResponseFormatter(request)
        return await formatter.format_item(pool)

    async def get_pool(self, pool_id: str, request: Request) -> ApiResponse[Pool]:
        """Get a pool by ID."""
        print(f"Pool controller: Getting pool with ID: {pool_id}")
        # Get the pool
        pool = self.pool_model.get_pool(pool_id)
        if not pool:
            raise HTTPException(status_code=404, detail=f"Pool with ID '{pool_id}' not found")
        print(f"Pool controller: Found pool: {pool}")

        # Format response
        formatter = UnityResponseFormatter(request)
        return await formatter.format_item(pool)

    async def get_pool_by_name(self, name: str, request: Request) -> ApiResponse[Pool]:
        """Get a pool by name."""
        print(f"Pool controller: Getting pool with name: {name}")
        # Get the pool
        pool = self.pool_model.get_pool_by_name(name)
        if not pool:
            raise HTTPException(status_code=404, detail=f"Pool with name '{name}' not found")
        print(f"Pool controller: Found pool: {pool}")

        # Format response
        formatter = UnityResponseFormatter(request)
        return await formatter.format_item(pool)

    async def list_pools(
        self,
        request: Request,
        compact: Optional[bool] = None,
        fields: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        orderby: Optional[str] = None,
    ) -> ApiResponse[List[Pool]]:
        """List all pools with filtering and pagination."""
        print("Pool controller: Listing pools")
        # Get pools from model
        pools = list(self.pool_model.list_pools())  # Convert to list to ensure it's not a tuple

        # Create entry links for each pool
        entry_links = {}
        if pools:
            entry_links = {i: [{"rel": "self", "href": f"/instances/pool/{pool.id}"}] for i, pool in enumerate(pools)}

        # Format response
        formatter = UnityResponseFormatter(request)
        return await formatter.format_collection(pools, entry_links=entry_links)

    async def update_pool(self, pool_id: str, pool_update: PoolUpdate, request: Request) -> ApiResponse[Pool]:
        """Update a pool."""
        print(f"Pool controller: Updating pool with ID: {pool_id}")
        # Update the pool
        pool = self.pool_model.update_pool(pool_id, pool_update)
        if not pool:
            raise HTTPException(status_code=404, detail=f"Pool with ID '{pool_id}' not found")
        print(f"Pool controller: Updated pool: {pool}")

        # Format response
        formatter = UnityResponseFormatter(request)
        return await formatter.format_item(pool)

    async def delete_pool(self, pool_id: str, request: Request) -> None:
        """Delete a pool."""
        print(f"Pool controller: Deleting pool with ID: {pool_id}")
        success = self.pool_model.delete_pool(pool_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Pool with ID '{pool_id}' not found")
        print(f"Pool controller: Deleted pool with ID: {pool_id}")

    async def delete_pool_by_name(self, name: str, request: Request) -> None:
        """Delete a pool by name."""
        print(f"Pool controller: Deleting pool with name: {name}")
        success = self.pool_model.delete_pool_by_name(name)
        if not success:
            raise HTTPException(status_code=404, detail=f"Pool with name '{name}' not found")
        print(f"Pool controller: Deleted pool with name: {name}")

    async def recommend_auto_configuration(self, request: Request) -> ApiResponse[List[PoolAutoConfigurationResponse]]:
        """Get recommended pool configurations."""
        print("Pool controller: Getting recommended pool configurations")
        # Get recommendations
        configs = self.pool_model.recommend_auto_configuration()
        print(f"Pool controller: Found {len(configs)} recommendations")

        # Format response
        formatter = UnityResponseFormatter(request)
        return await formatter.format_collection(configs)
