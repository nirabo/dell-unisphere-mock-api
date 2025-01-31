from fastapi import HTTPException, Request

from dell_unisphere_mock_api.controllers.pool_controller import PoolController
from dell_unisphere_mock_api.core.response import UnityResponseFormatter
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.models.lun import LUNModel
from dell_unisphere_mock_api.schemas.lun import LUN, LUNCreate, LUNUpdate


class LUNController:
    def __init__(self):
        self.lun_model = LUNModel()
        self.pool_controller = PoolController()

    async def create_lun(self, lun_create: LUNCreate, request: Request) -> ApiResponse[LUN]:
        """Create a new LUN."""
        print(f"LUN controller: Creating LUN with pool_id: {lun_create.pool_id}")
        # Validate pool exists and has enough space
        print(f"LUN controller: Looking for pool with ID: {lun_create.pool_id}")
        pool_response = await self.pool_controller.get_pool(str(lun_create.pool_id), request)
        print(f"LUN controller: Found pool: {pool_response}")
        if not pool_response.entries:
            print(f"LUN controller: Pool not found with ID: {lun_create.pool_id}")
            raise HTTPException(status_code=404, detail=f"Pool not found with ID: {lun_create.pool_id}")

        pool = pool_response.entries[0].content
        if pool.sizeFree < lun_create.size:
            print(
                f"LUN controller: Pool {pool.id} does not have enough free space. "
                f"Required: {lun_create.size}, Available: {pool.sizeFree}"
            )
            raise HTTPException(status_code=400, detail="Pool does not have enough free space")

        # Check if LUN with same name exists
        print(f"LUN controller: Checking if LUN with name {lun_create.name} exists")
        existing_lun = self.lun_model.get_lun_by_name(lun_create.name)
        if existing_lun:
            print(f"LUN controller: LUN with name {lun_create.name} already exists")
            raise HTTPException(status_code=409, detail="LUN with this name already exists")

        # Create the LUN
        print(f"LUN controller: Creating LUN with data: {lun_create.model_dump()}")
        result = self.lun_model.create_lun(lun_create)
        print(f"LUN controller: Created LUN: {result}")

        formatter = UnityResponseFormatter(request)
        return await formatter.format_collection([result], entry_links={0: [{"rel": "self", "href": f"/{result.id}"}]})

    async def get_lun(self, lun_id: str, request: Request) -> ApiResponse[LUN]:
        """Get a LUN by ID."""
        print(f"LUN controller: Looking for LUN with ID: {lun_id}")
        lun = self.lun_model.get_lun(lun_id)
        if not lun:
            print(f"LUN controller: LUN not found with ID: {lun_id}")
            raise HTTPException(status_code=404, detail=f"LUN with ID '{lun_id}' not found")
        print(f"LUN controller: Found LUN: {lun}")

        formatter = UnityResponseFormatter(request)
        return await formatter.format_collection([lun], entry_links={0: [{"rel": "self", "href": f"/{lun_id}"}]})

    async def get_lun_by_name(self, name: str, request: Request) -> ApiResponse[LUN]:
        """Get a LUN by name."""
        print(f"LUN controller: Looking for LUN with name: {name}")
        lun = self.lun_model.get_lun_by_name(name)
        if not lun:
            print(f"LUN controller: LUN not found with name: {name}")
            raise HTTPException(status_code=404, detail=f"LUN with name '{name}' not found")
        print(f"LUN controller: Found LUN: {lun}")

        formatter = UnityResponseFormatter(request)
        return await formatter.format_collection([lun], entry_links={0: [{"rel": "self", "href": f"/{lun.id}"}]})

    async def list_luns(self, request: Request) -> ApiResponse[LUN]:
        """List all LUNs."""
        print("LUN controller: Listing all LUNs")
        luns = self.lun_model.list_luns()
        print(f"LUN controller: Listed LUNs: {luns}")

        formatter = UnityResponseFormatter(request)
        entry_links = {i: [{"rel": "self", "href": f"/{lun.id}"}] for i, lun in enumerate(luns)}
        return await formatter.format_collection(luns, entry_links=entry_links)

    async def get_luns_by_pool(self, pool_id: str, request: Request) -> ApiResponse[LUN]:
        """Get all LUNs in a pool."""
        print(f"LUN controller: Getting LUNs in pool with ID: {pool_id}")
        luns = self.lun_model.get_luns_by_pool(pool_id)
        print(f"LUN controller: Got LUNs in pool: {luns}")

        formatter = UnityResponseFormatter(request)
        entry_links = {i: [{"rel": "self", "href": f"/{lun.id}"}] for i, lun in enumerate(luns)}
        return await formatter.format_collection(luns, entry_links=entry_links)

    async def update_lun(self, lun_id: str, lun_update: LUNUpdate, request: Request) -> ApiResponse[LUN]:
        """Update a LUN."""
        print(f"LUN controller: Updating LUN with ID: {lun_id}")
        # Get existing LUN
        current_lun = self.lun_model.get_lun(lun_id)
        if not current_lun:
            print(f"LUN controller: LUN not found with ID: {lun_id}")
            raise HTTPException(status_code=404, detail=f"LUN with ID '{lun_id}' not found")
        print(f"LUN controller: Found LUN: {current_lun}")

        # If name is being changed, check for conflicts
        if lun_update.name and lun_update.name != current_lun.name:
            existing_lun = self.lun_model.get_lun_by_name(lun_update.name)
            if existing_lun:
                print(f"LUN controller: LUN with name {lun_update.name} already exists")
                raise HTTPException(status_code=409, detail="LUN with this name already exists")

        print(f"LUN controller: Updating LUN with data: {lun_update.model_dump()}")
        result = self.lun_model.update_lun(lun_id, lun_update)
        print(f"LUN controller: Updated LUN: {result}")

        formatter = UnityResponseFormatter(request)
        return await formatter.format_collection([result], entry_links={0: [{"rel": "self", "href": f"/{lun_id}"}]})

    async def delete_lun(self, lun_id: str, request: Request) -> ApiResponse[None]:
        """Delete a LUN."""
        print(f"LUN controller: Deleting LUN with ID: {lun_id}")
        if not self.lun_model.delete_lun(lun_id):
            print(f"LUN controller: LUN not found with ID: {lun_id}")
            raise HTTPException(status_code=404, detail=f"LUN with ID '{lun_id}' not found")
        print(f"LUN controller: Deleted LUN with ID: {lun_id}")

        formatter = UnityResponseFormatter(request)
        return await formatter.format_collection([], entry_links={})
