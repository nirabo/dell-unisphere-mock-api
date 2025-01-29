import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class StorageResourceResponse(BaseModel):
    """Storage resource response model"""

    id: str = Field(description="Unique identifier of the storage resource")
    name: str = Field(description="Name of the storage resource")
    description: Optional[str] = Field(None, description="Description of the storage resource")
    health: str = Field(default="OK", description="Health status of the storage resource")
    type: str = Field(description="Type of storage resource (e.g., 'lun', 'filesystem')")
    sizeTotal: int = Field(description="Total size of the storage resource in bytes")
    sizeUsed: int = Field(default=0, description="Used size of the storage resource in bytes")
    sizeAllocated: int = Field(description="Allocated size of the storage resource in bytes")
    isThinEnabled: bool = Field(default=True, description="Whether thin provisioning is enabled")
    thinStatus: str = Field(default="True", description="Thin provisioning status")
    metadataSize: int = Field(default=0, description="Size of metadata in bytes")
    metadataSizeAllocated: int = Field(default=0, description="Allocated size of metadata in bytes")
    snapCount: int = Field(default=0, description="Number of snapshots")
    snapSize: int = Field(default=0, description="Total size of snapshots in bytes")
    snapSizeAllocated: int = Field(default=0, description="Allocated size of snapshots in bytes")
    hostAccess: List[dict] = Field(default_factory=list, description="List of host access configurations")
    perTierSizeUsed: Dict[str, int] = Field(default_factory=dict, description="Size used per storage tier")
    created: datetime = Field(description="Creation timestamp")
    modified: datetime = Field(description="Last modification timestamp")
    esxFilesystemMajorVersion: Optional[str] = Field(
        None, description="ESX filesystem major version for VMware resources"
    )


class StorageResourceModel:
    def __init__(self):
        self.storage_resources: Dict[str, dict] = {}

    def create_storage_resource(self, resource_data: dict) -> StorageResourceResponse:
        resource_id = str(uuid.uuid4())

        # Initialize size-related fields based on type
        size_total = resource_data.get("sizeTotal", 0)
        is_thin = resource_data.get("isThinEnabled", True)

        # Calculate initial allocated size
        size_allocated = size_total // 10 if is_thin else size_total

        resource = StorageResourceResponse(
            id=resource_id,
            name=resource_data.get("name"),
            description=resource_data.get("description"),
            type=resource_data.get("type", "lun"),
            sizeTotal=size_total,
            sizeAllocated=size_allocated,
            isThinEnabled=is_thin,
            created=datetime.now(timezone.utc),
            modified=datetime.now(timezone.utc),
            **{k: v for k, v in resource_data.items() if k not in ["id", "created", "modified"]},
        )

        # Add VMware-specific fields if applicable
        if resource.type in ["VMwareFS", "VVolDatastoreFS"]:
            resource.esxFilesystemMajorVersion = "6"

        self.storage_resources[resource_id] = resource.dict()
        return resource

    def get_storage_resource(self, resource_id: str) -> Optional[StorageResourceResponse]:
        resource = self.storage_resources.get(resource_id)
        return StorageResourceResponse(**resource) if resource else None

    def list_storage_resources(self, resource_type: Optional[str] = None) -> List[StorageResourceResponse]:
        resources = []
        for resource in self.storage_resources.values():
            if not resource_type or resource.get("type") == resource_type:
                resources.append(StorageResourceResponse(**resource))
        return resources

    def update_storage_resource(self, resource_id: str, update_data: dict) -> Optional[StorageResourceResponse]:
        if resource_id not in self.storage_resources:
            return None

        resource = self.storage_resources[resource_id]

        # Handle compression and deduplication updates
        if "isCompressionEnabled" in update_data:
            # In a real implementation, this would trigger compression
            pass

        if "isAdvancedDedupEnabled" in update_data:
            # In a real implementation, this would trigger deduplication
            pass

        # Update fields
        for key, value in update_data.items():
            if value is not None:
                resource[key] = value

        resource["modified"] = datetime.now(timezone.utc).isoformat()
        return StorageResourceResponse(**resource)

    def delete_storage_resource(self, resource_id: str) -> bool:
        if resource_id not in self.storage_resources:
            return False
        del self.storage_resources[resource_id]
        return True

    def add_host_access(self, resource_id: str, host_id: str, access_type: str) -> bool:
        if resource_id not in self.storage_resources:
            return False

        resource = self.storage_resources[resource_id]
        # Check if host already has access
        for access in resource["hostAccess"]:
            if access["host"] == host_id:
                access["accessType"] = access_type
                return True

        # Add new host access
        resource["hostAccess"].append({"host": host_id, "accessType": access_type})
        return True

    def remove_host_access(self, resource_id: str, host_id: str) -> bool:
        if resource_id not in self.storage_resources:
            return False

        resource = self.storage_resources[resource_id]
        resource["hostAccess"] = [access for access in resource["hostAccess"] if access["host"] != host_id]
        return True

    def update_host_access(self, resource_id: str, host_id: str, access_type: str) -> bool:
        if resource_id not in self.storage_resources:
            return False

        resource = self.storage_resources[resource_id]
        # Check if host already has access
        for access in resource["hostAccess"]:
            if access["host"] == host_id:
                access["accessType"] = access_type
                return True

        return False

    def update_usage_stats(self, resource_id: str, size_used: int, tier_usage: dict) -> bool:
        if resource_id not in self.storage_resources:
            return False

        resource = self.storage_resources[resource_id]
        resource["sizeUsed"] = size_used
        resource["perTierSizeUsed"] = tier_usage

        # Update allocated size for thin provisioning
        if resource["isThinEnabled"]:
            resource["sizeAllocated"] = max(
                size_used + (1024 * 1024 * 1024),  # Add 1GB buffer
                resource["sizeAllocated"],
            )

        return True

    def modify_host_access(self, resource_id: str, host_access: dict) -> Optional[StorageResourceResponse]:
        if resource_id not in self.storage_resources:
            return None

        resource = self.storage_resources[resource_id]
        host_accesses = resource.get("hostAccess", [])

        # Update or add host access
        updated = False
        for access in host_accesses:
            if access["host"] == host_access["host"]:
                access["accessType"] = host_access["accessType"]
                updated = True
                break

        if not updated:
            host_accesses.append(host_access)

        resource["hostAccess"] = host_accesses
        resource["modified"] = datetime.now(timezone.utc).isoformat()

        return StorageResourceResponse(**resource)

    def create_lun(self, lun_data: dict) -> StorageResourceResponse:
        # Validate required fields
        if "name" not in lun_data or "lunParameters" not in lun_data:
            raise ValueError("Missing required fields: name and lunParameters")

        if "pool" not in lun_data["lunParameters"] or "size" not in lun_data["lunParameters"]:
            raise ValueError("Missing required lunParameters: pool and size")

        # Create LUN with type "lun"
        lun_data["type"] = "lun"
        lun_data["sizeTotal"] = int(lun_data["lunParameters"]["size"])

        return self.create_storage_resource(lun_data)

    def modify_lun(self, resource_id: str, lun_data: dict) -> Optional[StorageResourceResponse]:
        resource = self.get_storage_resource(resource_id)
        if not resource:
            return None

        if resource.type != "lun":
            raise ValueError("Storage resource is not a LUN")

        update_data = {}
        if "description" in lun_data:
            update_data["description"] = lun_data["description"]
        if "lunParameters" in lun_data and "size" in lun_data["lunParameters"]:
            update_data["sizeTotal"] = lun_data["lunParameters"]["size"]

        return self.update_storage_resource(resource_id, update_data)

    def expand_lun(self, resource_id: str, expand_data: dict) -> Optional[StorageResourceResponse]:
        resource = self.get_storage_resource(resource_id)
        if not resource:
            return None

        if resource.type != "lun":
            raise ValueError("Storage resource is not a LUN")

        if "size" not in expand_data:
            raise ValueError("Missing required field: size")

        new_size = int(expand_data["size"])
        if new_size <= resource.sizeTotal:
            raise ValueError(f"New size ({new_size}) must be larger than current size ({resource.sizeTotal})")

        return self.update_storage_resource(resource_id, {"sizeTotal": new_size})
