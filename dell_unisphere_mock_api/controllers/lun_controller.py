from typing import List, Optional

from fastapi import HTTPException

from dell_unisphere_mock_api.controllers.pool_controller import PoolController
from dell_unisphere_mock_api.models.lun import LUNModel
from dell_unisphere_mock_api.schemas.lun import LUN, LUNCreate, LUNUpdate


class LUNController:
    def __init__(self):
        self.lun_model = LUNModel()
        self.pool_controller = PoolController()

    def create_lun(self, lun_create: LUNCreate) -> LUN:
        """Create a new LUN."""
        print(f"LUN controller: Creating LUN with pool_id: {lun_create.pool_id}")
        # Validate pool exists and has enough space
        print(f"LUN controller: Looking for pool with ID: {lun_create.pool_id}")
        pool = self.pool_controller.get_pool(str(lun_create.pool_id))
        print(f"LUN controller: Found pool: {pool}")
        if not pool:
            print(f"LUN controller: Pool not found with ID: {lun_create.pool_id}")
            raise HTTPException(status_code=404, detail=f"Pool not found with ID: {lun_create.pool_id}")

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
        return result

    def get_lun(self, lun_id: str) -> Optional[LUN]:
        """Get a LUN by ID."""
        print(f"LUN controller: Looking for LUN with ID: {lun_id}")
        lun = self.lun_model.get_lun(lun_id)
        if not lun:
            print(f"LUN controller: LUN not found with ID: {lun_id}")
            raise HTTPException(status_code=404, detail=f"LUN with ID '{lun_id}' not found")
        print(f"LUN controller: Found LUN: {lun}")
        return lun

    def get_lun_by_name(self, name: str) -> Optional[LUN]:
        """Get a LUN by name."""
        print(f"LUN controller: Looking for LUN with name: {name}")
        lun = self.lun_model.get_lun_by_name(name)
        if not lun:
            print(f"LUN controller: LUN not found with name: {name}")
            raise HTTPException(status_code=404, detail=f"LUN with name '{name}' not found")
        print(f"LUN controller: Found LUN: {lun}")
        return lun

    def list_luns(self) -> List[LUN]:
        """List all LUNs."""
        print("LUN controller: Listing all LUNs")
        result = self.lun_model.list_luns()
        print(f"LUN controller: Listed LUNs: {result}")
        return result

    def get_luns_by_pool(self, pool_id: str) -> List[LUN]:
        """Get all LUNs in a pool."""
        print(f"LUN controller: Getting LUNs in pool with ID: {pool_id}")
        result = self.lun_model.get_luns_by_pool(pool_id)
        print(f"LUN controller: Got LUNs in pool: {result}")
        return result

    def update_lun(self, lun_id: str, lun_update: LUNUpdate) -> Optional[LUN]:
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
        return result

    def delete_lun(self, lun_id: str) -> bool:
        """Delete a LUN."""
        print(f"LUN controller: Deleting LUN with ID: {lun_id}")
        if not self.lun_model.delete_lun(lun_id):
            print(f"LUN controller: LUN not found with ID: {lun_id}")
            raise HTTPException(status_code=404, detail=f"LUN with ID '{lun_id}' not found")
        print(f"LUN controller: Deleted LUN with ID: {lun_id}")
        return True
