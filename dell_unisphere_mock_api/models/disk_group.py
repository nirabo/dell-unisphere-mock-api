from typing import Dict, List, Optional, Union

from dell_unisphere_mock_api.schemas.disk_group import RaidStripeWidthEnum, RaidTypeEnum


class DiskGroupModel:
    def __init__(self):
        self.disk_groups: Dict[str, dict] = {}
        self.next_id = 1

    def _format_disk_group_content(self, disk_group: dict) -> dict:
        """Helper method to format disk group content consistently."""
        return {
            "id": disk_group["id"],
            "name": disk_group.get("name", ""),
            "description": disk_group.get("description", ""),
            "raid_type": disk_group["raid_type"],
            "stripe_width": disk_group["stripe_width"],
            "disk_ids": disk_group.get("disk_ids", []),
            "pool_id": disk_group.get("pool_id", ""),
            "state": disk_group.get("state", "OK"),
        }

    def _format_response(self, disk_group: Optional[Union[dict, List[dict]]]) -> dict:
        """Helper method to format response consistently."""
        if disk_group is None:
            return {"entries": []}

        if isinstance(disk_group, list):
            entries = [{"content": self._format_disk_group_content(dg)} for dg in disk_group]
        else:
            entries = [{"content": self._format_disk_group_content(disk_group)}]

        return {"entries": entries}

    def create(self, disk_group: dict) -> dict:
        """Create a new disk group."""
        disk_group_id = str(self.next_id)
        self.next_id += 1

        disk_group["id"] = disk_group_id
        disk_group["state"] = "OK"
        self.disk_groups[disk_group_id] = disk_group
        return self._format_response(disk_group)

    def get(self, disk_group_id: str) -> dict:
        """Get a disk group by ID."""
        disk_group = self.disk_groups.get(disk_group_id)
        if not disk_group:
            return {"entries": []}
        return self._format_response(disk_group)

    def list(self) -> dict:
        """List all disk groups."""
        return self._format_response(list(self.disk_groups.values()))

    def update(self, disk_group_id: str, disk_group_update: dict) -> dict:
        """Update a disk group."""
        if disk_group_id in self.disk_groups:
            current_disk_group = self.disk_groups[disk_group_id]
            for key, value in disk_group_update.items():
                if value is not None:
                    current_disk_group[key] = value
            return self._format_response(current_disk_group)
        return {"entries": []}

    def delete(self, disk_group_id: str) -> bool:
        """Delete a disk group."""
        if disk_group_id in self.disk_groups:
            del self.disk_groups[disk_group_id]
            return True
        return False

    def validate_raid_config(self, raid_type: str, stripe_width: int, disk_count: int) -> bool:
        """Validate RAID configuration based on stripe width and disk count."""
        valid_configs = {
            "RAID5": {5: 5, 9: 9, 13: 13},  # stripe_width: required_disks
            "RAID6": {6: 6, 8: 8, 10: 10, 12: 12, 14: 14, 16: 16},
            "RAID10": {2: 2, 4: 4, 6: 6, 8: 8, 10: 10, 12: 12},
        }

        if raid_type not in valid_configs:
            return False

        if stripe_width not in valid_configs[raid_type]:
            return False

        return disk_count >= valid_configs[raid_type][stripe_width]
