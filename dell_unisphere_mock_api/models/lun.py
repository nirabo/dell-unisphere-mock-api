import logging
import random
from typing import Dict, List, Optional
from uuid import uuid4

from dell_unisphere_mock_api.schemas.lun import LUN, LUNCreate, LUNHealth, LUNUpdate


class LUNModel:
    """Model for managing LUNs (Logical Unit Numbers)."""

    _instance = None
    luns: Dict[str, LUN]  # Class-level type annotation

    def __new__(cls) -> "LUNModel":
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.luns = {}  # Initialize in __new__
        return cls._instance

    def __init__(self) -> None:
        """Initialize the LUN model."""
        # No initialization needed as it's handled in __new__
        pass

    def _generate_wwn(self) -> str:
        """Generate a random World Wide Name for a LUN."""
        prefix = "60060160372045"
        suffix = "".join([random.choice("0123456789ABCDEF") for _ in range(18)])
        return f"{prefix}{suffix}"

    def _create_default_health(self) -> LUNHealth:
        """Create a default health status for a new LUN."""
        return LUNHealth(
            value=5,
            descriptionIds=["ALRT_COMPONENT_OK"],
            descriptions=["The component is operating normally."],
        )

    def create_lun(self, lun_create: LUNCreate) -> LUN:
        """Create a new LUN."""
        logging.debug(f"LUN model: Creating LUN with name: {lun_create.name}")
        lun_dict = lun_create.model_dump()
        logging.debug(f"LUN model: Initial LUN data: {lun_dict}")

        # Generate new ID
        lun_id = str(len(self.luns) + 1)
        lun_dict["id"] = lun_id
        lun_dict["pool_id"] = str(lun_dict["pool_id"])  # Ensure pool_id is string
        lun_dict["wwn"] = self._generate_wwn()
        lun_dict["health"] = self._create_default_health()
        lun_dict["currentNode"] = lun_dict.get("defaultNode", 0)
        lun_dict["sizeAllocated"] = 0  # Initially no space allocated for thin provisioning

        # Create LUN object
        lun = LUN(**lun_dict)
        logging.debug(f"LUN model: Created LUN object: {lun}")

        # Store in dictionary
        self.luns[lun_id] = lun
        logging.debug(f"LUN model: Stored LUN with ID {lun_id}")

        return lun

    def get_lun(self, lun_id: str) -> Optional[LUN]:
        """Get a LUN by ID."""
        logging.debug(f"LUN model: Getting LUN with ID: {lun_id}")
        return self.luns.get(lun_id)

    def get_lun_by_name(self, name: str) -> Optional[LUN]:
        """Get a LUN by name."""
        logging.debug(f"LUN model: Getting LUN with name: {name}")
        for lun in self.luns.values():
            if lun.name == name:
                return lun
        return None

    def list_luns(self) -> List[LUN]:
        """List all LUNs."""
        logging.debug("LUN model: Listing all LUNs")
        return list(self.luns.values())

    def get_luns_by_pool(self, pool_id: str) -> List[LUN]:
        """Get all LUNs in a pool."""
        logging.debug(f"LUN model: Getting LUNs in pool with ID: {pool_id}")
        return [lun for lun in self.luns.values() if str(lun.pool_id) == str(pool_id)]

    def update_lun(self, lun_id: str, lun_update: LUNUpdate) -> Optional[LUN]:
        """Update a LUN."""
        logging.debug(f"LUN model: Updating LUN with ID: {lun_id}")
        if lun_id not in self.luns:
            return None

        current_lun = self.luns[lun_id]
        update_data = lun_update.model_dump(exclude_unset=True)

        # Update fields
        updated_dict = current_lun.model_dump()
        updated_dict.update(update_data)

        # Create new LUN object with updated data
        updated_lun = LUN(**updated_dict)
        self.luns[lun_id] = updated_lun

        return updated_lun

    def delete_lun(self, lun_id: str) -> bool:
        """Delete a LUN."""
        logging.debug(f"LUN model: Deleting LUN with ID: {lun_id}")
        if lun_id in self.luns:
            del self.luns[lun_id]
            return True
        return False

    def delete_lun_by_name(self, name: str) -> bool:
        """Delete a LUN by name."""
        lun = self.get_lun_by_name(name)
        if lun:
            return self.delete_lun(lun.id)
        return False
