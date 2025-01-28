from typing import Dict, List, Optional, Union

from dell_unisphere_mock_api.schemas.disk import Disk, DiskTierEnum, DiskTypeEnum


class DiskModel:
    def __init__(self):
        self.disks: Dict[str, Disk] = {}
        self.disk_counter = 0

    def _format_response(self, disk: Disk) -> Dict:
        """Helper method to format disk response consistently."""
        return {
            "entries": [
                {
                    "content": {
                        "id": disk.id,
                        "name": disk.name or "",
                        "description": disk.description or "",
                        "disk_type": disk.disk_type,
                        "tier_type": disk.tier_type,
                        "size": disk.size,
                        "disk_technology": disk.disk_technology or "",
                        "rpm": disk.rpm,
                        "slot_number": disk.slot_number,
                        "pool_id": disk.pool_id or "",
                        "disk_group_id": disk.disk_group_id or "",
                        "firmware_version": disk.firmware_version or "",
                        "health_status": disk.health_status or "OK",
                    }
                }
            ]
        }

    def create(self, disk: Dict) -> Dict:
        """Create a new disk."""
        self.disk_counter += 1
        disk_id = str(self.disk_counter)

        # Set default values for required fields
        if "tier_type" not in disk:
            disk_type = disk.get("disk_type", DiskTypeEnum.SAS)
            if disk_type == DiskTypeEnum.SAS:
                disk["tier_type"] = DiskTierEnum.PERFORMANCE
            elif disk_type == DiskTypeEnum.NL_SAS:
                disk["tier_type"] = DiskTierEnum.CAPACITY
            else:
                disk["tier_type"] = DiskTierEnum.EXTREME_PERFORMANCE

        disk_obj = Disk(id=disk_id, **disk)
        self.disks[disk_id] = disk_obj
        return self._format_response(disk_obj)

    def get(self, disk_id: str) -> Optional[Dict]:
        """Get a disk by ID."""
        if disk_id not in self.disks:
            return {"entries": []}
        return self._format_response(self.disks[disk_id])

    def list(self) -> Dict:
        """List all disks."""
        return {"entries": [self._format_response(disk)["entries"][0] for disk in self.disks.values()]}

    def update(self, disk_id: str, disk_update: Dict) -> Optional[Dict]:
        """Update a disk."""
        if disk_id in self.disks:
            current_disk = self.disks[disk_id]
            for key, value in disk_update.items():
                if hasattr(current_disk, key):
                    setattr(current_disk, key, value)
            return self._format_response(current_disk)
        return {"entries": []}

    def delete(self, disk_id: str) -> bool:
        """Delete a disk."""
        if disk_id in self.disks:
            del self.disks[disk_id]
            return True
        return False

    def get_by_pool(self, pool_id: str) -> Dict:
        """Get all disks associated with a specific pool."""
        matching_disks = [disk for disk in self.disks.values() if disk.pool_id == pool_id]
        return {
            "entries": [
                {
                    "content": {
                        "id": disk.id,
                        "name": disk.name or "",
                        "description": disk.description or "",
                        "disk_type": disk.disk_type,
                        "tier_type": disk.tier_type,
                        "size": disk.size,
                        "disk_technology": disk.disk_technology or "",
                        "rpm": disk.rpm,
                        "slot_number": disk.slot_number,
                        "pool_id": disk.pool_id or "",
                        "disk_group_id": disk.disk_group_id or "",
                        "firmware_version": disk.firmware_version or "",
                        "health_status": disk.health_status or "OK",
                    }
                }
                for disk in matching_disks
            ]
        }

    def get_by_disk_group(self, disk_group_id: str) -> Dict:
        """Get all disks associated with a specific disk group."""
        matching_disks = [disk for disk in self.disks.values() if disk.disk_group_id == disk_group_id]
        return {
            "entries": [
                {
                    "content": {
                        "id": disk.id,
                        "name": disk.name or "",
                        "description": disk.description or "",
                        "disk_type": disk.disk_type,
                        "tier_type": disk.tier_type,
                        "size": disk.size,
                        "disk_technology": disk.disk_technology or "",
                        "rpm": disk.rpm,
                        "slot_number": disk.slot_number,
                        "pool_id": disk.pool_id or "",
                        "disk_group_id": disk.disk_group_id or "",
                        "firmware_version": disk.firmware_version or "",
                        "health_status": disk.health_status or "OK",
                    }
                }
                for disk in matching_disks
            ]
        }

    def validate_disk_type(self, disk_type: str) -> bool:
        """Validate disk type and set appropriate tier type."""
        return disk_type in DiskTypeEnum.__members__
