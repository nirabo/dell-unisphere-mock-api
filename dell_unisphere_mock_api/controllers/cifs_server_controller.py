from datetime import datetime
from typing import Dict, List
from uuid import uuid4

from fastapi import HTTPException, Request

from dell_unisphere_mock_api.core.response_models import ApiResponse, Entry, Link
from dell_unisphere_mock_api.models.cifs_server import CIFSServer, CIFSServerCreate, CIFSServerUpdate


class CIFSServerController:
    def __init__(self):
        self.cifs_servers: Dict[str, CIFSServer] = {}

    def _create_api_response(self, entries: List[Entry], request: Request) -> ApiResponse:
        """Create standardized API response"""
        base_url = str(request.base_url).rstrip("/")
        return ApiResponse(
            **{
                "@base": f"{base_url}/api/types/cifsServer/instances",
                "updated": datetime.utcnow(),
                "links": [Link(rel="self", href=f"{base_url}/api/types/cifsServer/instances")],
                "entries": entries,
            }
        )

    def _create_entry(self, cifs_server: CIFSServer, request: Request) -> Entry:
        """Create standardized entry"""
        base_url = str(request.base_url).rstrip("/")
        return Entry(
            **{
                "@base": "storageObject",
                "content": cifs_server,
                "updated": datetime.utcnow(),
                "links": [
                    Link(rel="self", href=f"{base_url}/api/instances/cifsServer/{cifs_server.id}"),
                    Link(rel="nasServer", href=f"{base_url}/api/instances/nasServer/{cifs_server.nas_server_id}"),
                ],
            }
        )

    async def create_cifs_server(self, request: Request, cifs_server: CIFSServerCreate) -> ApiResponse:
        """Create a new CIFS server"""
        try:
            server_id = str(uuid4())
            new_server = CIFSServer(**{**cifs_server.model_dump(), "id": server_id})
            self.cifs_servers[server_id] = new_server
            return self._create_api_response([self._create_entry(new_server, request)], request)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_cifs_server(self, request: Request, server_id: str) -> ApiResponse:
        """Get a CIFS server by ID"""
        server = self.cifs_servers.get(server_id)
        if not server:
            raise HTTPException(status_code=404, detail="CIFS server not found")
        return self._create_api_response([self._create_entry(server, request)], request)

    async def list_cifs_servers(self, request: Request) -> ApiResponse:
        """List all CIFS servers"""
        entries = [self._create_entry(server, request) for server in self.cifs_servers.values()]
        return self._create_api_response(entries, request)

    async def update_cifs_server(self, request: Request, server_id: str, update_data: CIFSServerUpdate) -> ApiResponse:
        """Update a CIFS server"""
        if server_id not in self.cifs_servers:
            raise HTTPException(status_code=404, detail="CIFS server not found")

        server = self.cifs_servers[server_id]
        update_dict = update_data.model_dump(exclude_unset=True)
        updated_server = CIFSServer(**{**server.model_dump(), **update_dict})
        self.cifs_servers[server_id] = updated_server
        return self._create_api_response([self._create_entry(updated_server, request)], request)

    async def delete_cifs_server(self, request: Request, server_id: str) -> ApiResponse:
        """Delete a CIFS server"""
        if server_id not in self.cifs_servers:
            raise HTTPException(status_code=404, detail="CIFS server not found")
        del self.cifs_servers[server_id]
        return self._create_api_response([], request)
