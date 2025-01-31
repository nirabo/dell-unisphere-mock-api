import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from dell_unisphere_mock_api.schemas.storage_resource import (
    StorageResourceCreate,
    StorageResourceResponse,
    StorageResourceUpdate,
)


class StorageResourceModel:
    def __init__(self):
        self.storage_resources: Dict[str, dict] = {}

    def create_storage_resource(self, resource_data: dict | StorageResourceCreate) -> StorageResourceResponse:
        resource_id = str(uuid.uuid4())

        # Convert to dict if it's a Pydantic model
        if not isinstance(resource_data, dict):
            resource_data = resource_data.model_dump()

        # Initialize size-related fields based on type
        size_total = resource_data.get("sizeTotal", 0)
        is_thin = resource_data.get("isThinEnabled", True)

        # Calculate initial allocated size
        size_allocated = size_total // 10 if is_thin else size_total
        size_used = 0  # Initially no space is used

        # Create base resource with required fields
        resource = StorageResourceResponse(
            id=resource_id,
            name=resource_data.get("name"),
            description=resource_data.get("description"),
            type=resource_data.get("type", "LUN"),
            pool=resource_data.get("pool", "default_pool"),
            sizeTotal=size_total,
            sizeUsed=size_used,
            sizeAllocated=size_allocated,
            isThinEnabled=is_thin,
            isCompressionEnabled=resource_data.get("isCompressionEnabled", False),
            isAdvancedDedupEnabled=resource_data.get("isAdvancedDedupEnabled", False),
            health="OK",
            thinStatus="True" if is_thin else "False",
            metadataSize=0,
            metadataSizeAllocated=0,
            snapCount=0,
            snapSize=0,
            snapSizeAllocated=0,
            hostAccess=[],
            perTierSizeUsed={},
            created=datetime.now(timezone.utc),
            modified=datetime.now(timezone.utc),
            tieringPolicy=resource_data.get("tieringPolicy"),
            relocationPolicy=resource_data.get("relocationPolicy"),
        )

        # Add VMware-specific fields if applicable
        if resource.type in ["VMwareFS", "VVolDatastoreFS"]:
            resource.esxFilesystemMajorVersion = "6"

        self.storage_resources[resource_id] = resource.model_dump()
        return resource

    def update_storage_resource(
        self, resource_id: str, update_data: dict | StorageResourceUpdate
    ) -> Optional[StorageResourceResponse]:
        if resource_id not in self.storage_resources:
            return None

        # Convert to dict if it's a Pydantic model
        if not isinstance(update_data, dict):
            update_data = update_data.model_dump(exclude_unset=True)

        # Get current resource data
        current_data = self.storage_resources[resource_id]

        # Update the fields
        current_data.update(update_data)
        current_data["modified"] = datetime.now(timezone.utc)

        # Create updated resource
        resource = StorageResourceResponse(**current_data)
        self.storage_resources[resource_id] = resource.model_dump()
        return resource

    def get_storage_resource(self, resource_id: str) -> Optional[StorageResourceResponse]:
        resource = self.storage_resources.get(resource_id)
        if not resource:
            return None
        return StorageResourceResponse(**resource)

    def list_storage_resources(self, resource_type: Optional[str] = None) -> List[StorageResourceResponse]:
        resources = []
        for resource in self.storage_resources.values():
            if not resource_type or resource.get("type") == resource_type:
                resources.append(StorageResourceResponse(**resource))
        return resources

    def delete_storage_resource(self, resource_id: str) -> bool:
        if resource_id not in self.storage_resources:
            return False
        del self.storage_resources[resource_id]
        return True

    def add_host_access(self, resource_id: str, host_id: str, access_type: str) -> bool:
        if resource_id not in self.storage_resources:
            return False

        resource = self.storage_resources[resource_id]
        host_access = resource.get("hostAccess", [])
        host_access.append({"host": host_id, "accessType": access_type})
        resource["hostAccess"] = host_access
        resource["modified"] = datetime.now(timezone.utc).isoformat()
        return True

    def update_host_access(self, resource_id: str, host_id: str, access_type: str) -> bool:
        if resource_id not in self.storage_resources:
            return False

        resource = self.storage_resources[resource_id]
        host_access = resource.get("hostAccess", [])
        for access in host_access:
            if access["host"] == host_id:
                access["accessType"] = access_type
                resource["modified"] = datetime.now(timezone.utc).isoformat()
                return True
        return False

    def remove_host_access(self, resource_id: str, host_id: str) -> bool:
        if resource_id not in self.storage_resources:
            return False

        resource = self.storage_resources[resource_id]
        host_access = resource.get("hostAccess", [])
        for i, access in enumerate(host_access):
            if access["host"] == host_id:
                del host_access[i]
                resource["modified"] = datetime.now(timezone.utc).isoformat()
                return True
        return False

    def manage_host_access(
        self, resource_id: str, host_access: List[Dict[str, str]]
    ) -> Optional[StorageResourceResponse]:
        if resource_id not in self.storage_resources:
            return None

        resource = self.storage_resources[resource_id]
        resource["hostAccess"] = host_access
        resource["modified"] = datetime.now(timezone.utc).isoformat()
        return StorageResourceResponse(**resource)

    def create_lun(self, lun_data: StorageResourceCreate) -> StorageResourceResponse:
        # Validate required fields
        if (
            not lun_data.name
            or not lun_data.lunParameters
            or not lun_data.lunParameters.pool
            or not lun_data.lunParameters.size
        ):
            raise ValueError("Missing required fields: name, lunParameters, pool, and size")

        # Create LUN with type "lun"
        lun_data.type = "lun"
        lun_data.sizeTotal = int(lun_data.lunParameters.size)

        return self.create_storage_resource(lun_data)

    def modify_lun(self, resource_id: str, lun_data: StorageResourceUpdate) -> Optional[StorageResourceResponse]:
        resource = self.get_storage_resource(resource_id)
        if not resource:
            return None

        if resource.type != "lun":
            raise ValueError("Storage resource is not a LUN")

        update_data = {}
        if lun_data.description:
            update_data["description"] = lun_data.description
        if lun_data.lunParameters and lun_data.lunParameters.size:
            update_data["sizeTotal"] = lun_data.lunParameters.size

        return self.update_storage_resource(resource_id, update_data)

    def expand_lun(self, resource_id: str, expand_data: StorageResourceUpdate) -> Optional[StorageResourceResponse]:
        resource = self.get_storage_resource(resource_id)
        if not resource:
            return None

        if resource.type != "lun":
            raise ValueError("Storage resource is not a LUN")

        if not expand_data.size:
            raise ValueError("Missing required field: size")

        new_size = int(expand_data.size)
        if new_size <= resource.sizeTotal:
            raise ValueError(f"New size ({new_size}) must be larger than current size ({resource.sizeTotal})")

        return self.update_storage_resource(resource_id, expand_data)
