from uuid import uuid4

from fastapi import HTTPException, Request

from dell_unisphere_mock_api.core.response import UnityResponseFormatter
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.models.nfs_share import NFSShare, NFSShareCreate, NFSShareUpdate


class NFSShareController:
    """Controller for managing NFS shares."""

    def __init__(self):
        self.shares: dict[str, NFSShare] = {}

    def create_nfs_share(self, request: Request, share_data: NFSShareCreate) -> ApiResponse[NFSShare]:
        """Create a new NFS share."""
        share_id = str(uuid4())
        share = NFSShare(
            id=share_id,
            name=share_data.name,
            path=share_data.path,
            description=share_data.description,
            filesystem_id=share_data.filesystem_id,
            default_access=share_data.default_access,
            root_squash_enabled=share_data.root_squash_enabled,
            anonymous_uid=share_data.anonymous_uid,
            anonymous_gid=share_data.anonymous_gid,
            is_read_only=share_data.is_read_only,
            min_security=share_data.min_security,
            no_access_hosts=share_data.no_access_hosts,
            read_only_hosts=share_data.read_only_hosts,
            read_write_hosts=share_data.read_write_hosts,
            root_access_hosts=share_data.root_access_hosts,
        )

        self.shares[share_id] = share
        formatter = UnityResponseFormatter(request)
        return formatter.format_collection([share], entry_links={0: [{"rel": "self", "href": f"/{share_id}"}]})

    def get_nfs_share(self, request: Request, share_id: str) -> ApiResponse[NFSShare]:
        """Get an NFS share by ID."""
        share = self.shares.get(share_id)
        if not share:
            raise HTTPException(status_code=404, detail=f"NFS share with ID '{share_id}' not found")

        formatter = UnityResponseFormatter(request)
        return formatter.format_collection([share], entry_links={0: [{"rel": "self", "href": f"/{share_id}"}]})

    def list_nfs_shares(self, request: Request) -> ApiResponse[NFSShare]:
        """List all NFS shares."""
        shares = list(self.shares.values())
        formatter = UnityResponseFormatter(request)
        entry_links = {i: [{"rel": "self", "href": f"/{share.id}"}] for i, share in enumerate(shares)}
        return formatter.format_collection(shares, entry_links=entry_links)

    def update_nfs_share(self, request: Request, share_id: str, share_data: NFSShareUpdate) -> ApiResponse[NFSShare]:
        """Update an NFS share."""
        share = self.shares.get(share_id)
        if not share:
            raise HTTPException(status_code=404, detail=f"NFS share with ID '{share_id}' not found")

        # Update share fields
        update_data = share_data.model_dump(exclude_unset=True)
        share_dict = share.model_dump()
        share_dict.update(update_data)
        updated_share = NFSShare(**share_dict)
        self.shares[share_id] = updated_share

        formatter = UnityResponseFormatter(request)
        return formatter.format_collection([updated_share], entry_links={0: [{"rel": "self", "href": f"/{share_id}"}]})

    def delete_nfs_share(self, request: Request, share_id: str) -> bool:
        """Delete an NFS share."""
        if share_id not in self.shares:
            raise HTTPException(status_code=404, detail=f"NFS share with ID '{share_id}' not found")

        del self.shares[share_id]
        return True
