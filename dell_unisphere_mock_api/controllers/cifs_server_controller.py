from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from dell_unisphere_mock_api.core.response_models import ApiResponse, Entry, Link
from dell_unisphere_mock_api.models.cifs_server import CIFSServer, CIFSServerCreate, CIFSServerUpdate


class CIFSServerController:
    def __init__(self):
        self.cifs_servers: Dict[str, CIFSServer] = {}

    def _create_api_response(self, entries: List[Entry], request_path: str) -> ApiResponse:
        """Create standardized API response"""
        base_url = "https://127.0.0.1:8000"  # This should come from configuration
        return ApiResponse(
            **{
                "@base": f"{base_url}/api/types/cifsServer/instances",
                "updated": datetime.utcnow(),
                "links": [Link(rel="self", href=f"{base_url}/api/types/cifsServer/instances")],
                "entries": entries,
            }
        )

    def _create_entry(self, cifs_server: CIFSServer, base_url: str) -> Entry:
        """Create standardized entry"""
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

    def create_cifs_server(self, cifs_server: CIFSServerCreate) -> CIFSServer:
        """Create a new CIFS server"""
        server_id = str(uuid4())
        new_server = CIFSServer(**{**cifs_server.dict(), "id": server_id})
        self.cifs_servers[server_id] = new_server
        return new_server

    def get_cifs_server(self, server_id: str) -> Optional[CIFSServer]:
        """Get a CIFS server by ID"""
        return self.cifs_servers.get(server_id)

    def list_cifs_servers(self) -> List[CIFSServer]:
        """List all CIFS servers"""
        return list(self.cifs_servers.values())

    def update_cifs_server(self, server_id: str, update_data: CIFSServerUpdate) -> Optional[CIFSServer]:
        """Update a CIFS server"""
        if server_id not in self.cifs_servers:
            return None

        server = self.cifs_servers[server_id]
        update_dict = update_data.dict(exclude_unset=True)
        updated_server = CIFSServer(**{**server.dict(), **update_dict})
        self.cifs_servers[server_id] = updated_server
        return updated_server

    def delete_cifs_server(self, server_id: str) -> bool:
        """Delete a CIFS server"""
        if server_id not in self.cifs_servers:
            return False
        del self.cifs_servers[server_id]
        return True
