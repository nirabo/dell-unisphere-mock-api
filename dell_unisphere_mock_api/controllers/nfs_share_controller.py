from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from dell_unisphere_mock_api.core.response_models import ApiResponse, Entry, Link
from dell_unisphere_mock_api.models.nfs_share import NFSShare, NFSShareCreate, NFSShareUpdate


class NFSShareController:
    def __init__(self):
        self.nfs_shares: Dict[str, NFSShare] = {}

    def _create_api_response(self, entries: List[Entry], request_path: str) -> ApiResponse:
        """Create standardized API response"""
        base_url = "https://127.0.0.1:8000"  # This should come from configuration
        return ApiResponse(
            **{
                "@base": f"{base_url}/api/types/nfsShare/instances",
                "updated": datetime.utcnow(),
                "links": [Link(rel="self", href=f"{base_url}/api/types/nfsShare/instances")],
                "entries": entries,
            }
        )

    def _create_entry(self, nfs_share: NFSShare, base_url: str) -> Entry:
        """Create standardized entry"""
        return Entry(
            **{
                "@base": "storageObject",
                "content": nfs_share,
                "updated": datetime.utcnow(),
                "links": [
                    Link(rel="self", href=f"{base_url}/api/instances/nfsShare/{nfs_share.id}"),
                    Link(rel="filesystem", href=f"{base_url}/api/instances/filesystem/{nfs_share.filesystem_id}"),
                ],
            }
        )

    def create_nfs_share(self, nfs_share: NFSShareCreate) -> NFSShare:
        """Create a new NFS share"""
        share_id = str(uuid4())
        new_share = NFSShare(**{**nfs_share.dict(), "id": share_id})
        self.nfs_shares[share_id] = new_share
        return new_share

    def get_nfs_share(self, share_id: str) -> Optional[NFSShare]:
        """Get an NFS share by ID"""
        return self.nfs_shares.get(share_id)

    def list_nfs_shares(self) -> List[NFSShare]:
        """List all NFS shares"""
        return list(self.nfs_shares.values())

    def update_nfs_share(self, share_id: str, update_data: NFSShareUpdate) -> Optional[NFSShare]:
        """Update an NFS share"""
        if share_id not in self.nfs_shares:
            return None

        share = self.nfs_shares[share_id]
        update_dict = update_data.dict(exclude_unset=True)
        updated_share = NFSShare(**{**share.dict(), **update_dict})
        self.nfs_shares[share_id] = updated_share
        return updated_share

    def delete_nfs_share(self, share_id: str) -> bool:
        """Delete an NFS share"""
        if share_id not in self.nfs_shares:
            return False
        del self.nfs_shares[share_id]
        return True
