from datetime import datetime
from typing import Dict, List
from uuid import uuid4

from fastapi import HTTPException, Request

from dell_unisphere_mock_api.core.response_models import ApiResponse, Entry, Link
from dell_unisphere_mock_api.models.nfs_share import NFSShare, NFSShareCreate, NFSShareUpdate


class NFSShareController:
    def __init__(self):
        self.nfs_shares: Dict[str, NFSShare] = {}

    def _create_api_response(self, entries: List[Entry], request: Request) -> ApiResponse:
        """Create standardized API response"""
        base_url = str(request.base_url).rstrip("/")
        return ApiResponse(
            **{
                "@base": f"{base_url}/api/types/nfsShare/instances",
                "updated": datetime.utcnow(),
                "links": [Link(rel="self", href=f"{base_url}/api/types/nfsShare/instances")],
                "entries": entries,
            }
        )

    def _create_entry(self, nfs_share: NFSShare, request: Request) -> Entry:
        """Create standardized entry"""
        base_url = str(request.base_url).rstrip("/")
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

    async def create_nfs_share(self, request: Request, nfs_share: NFSShareCreate) -> ApiResponse:
        """Create a new NFS share"""
        share_id = str(uuid4())
        new_share = NFSShare(**{**nfs_share.dict(), "id": share_id})
        self.nfs_shares[share_id] = new_share
        return self._create_api_response([self._create_entry(new_share, request)], request)

    async def get_nfs_share(self, request: Request, share_id: str) -> ApiResponse:
        """Get an NFS share by ID"""
        share = self.nfs_shares.get(share_id)
        if not share:
            raise HTTPException(status_code=404, detail=f"NFS share {share_id} not found")
        return self._create_api_response([self._create_entry(share, request)], request)

    async def list_nfs_shares(self, request: Request) -> ApiResponse:
        """List all NFS shares"""
        entries = [self._create_entry(share, request) for share in self.nfs_shares.values()]
        return self._create_api_response(entries, request)

    async def update_nfs_share(self, request: Request, share_id: str, update_data: NFSShareUpdate) -> ApiResponse:
        """Update an NFS share"""
        if share_id not in self.nfs_shares:
            raise HTTPException(status_code=404, detail=f"NFS share {share_id} not found")

        share = self.nfs_shares[share_id]
        updated_data = share.dict()
        updated_data.update(update_data.dict(exclude_unset=True))
        updated_share = NFSShare(**updated_data)
        self.nfs_shares[share_id] = updated_share

        return self._create_api_response([self._create_entry(updated_share, request)], request)

    async def delete_nfs_share(self, request: Request, share_id: str) -> ApiResponse:
        """Delete an NFS share"""
        if share_id not in self.nfs_shares:
            raise HTTPException(status_code=404, detail=f"NFS share {share_id} not found")

        share = self.nfs_shares.pop(share_id)
        return self._create_api_response([self._create_entry(share, request)], request)
