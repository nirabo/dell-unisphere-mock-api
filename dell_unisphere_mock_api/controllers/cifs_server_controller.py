import logging
from uuid import uuid4

from fastapi import HTTPException, Request

from dell_unisphere_mock_api.core.response import UnityResponseFormatter
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.models.cifs_server import CIFSServer, CIFSServerCreate, CIFSServerUpdate

logger = logging.getLogger(__name__)


class CIFSServerController:
    """Controller for managing CIFS servers."""

    def __init__(self):
        self.servers: dict[str, CIFSServer] = {}

    async def create_cifs_server(self, request: Request, server_data: CIFSServerCreate) -> ApiResponse[CIFSServer]:
        """Create a new CIFS server."""
        server_id = str(uuid4())
        server = CIFSServer(
            id=server_id,
            name=server_data.name,
            description=server_data.description,
            domain_name=server_data.domain_name,
            netbios_name=server_data.netbios_name,
            workgroup=server_data.workgroup,
            is_standalone=server_data.is_standalone,
            nas_server_id=server_data.nas_server_id,
        )

        self.servers[server_id] = server
        formatter = UnityResponseFormatter(request)
        return await formatter.format_collection([server], entry_links={0: [{"rel": "self", "href": f"/{server_id}"}]})

    async def get_cifs_server(self, request: Request, server_id: str) -> ApiResponse[CIFSServer]:
        """Get a CIFS server by ID."""
        server = self.servers.get(server_id)
        if not server:
            raise HTTPException(status_code=404, detail=f"CIFS server with ID '{server_id}' not found")

        formatter = UnityResponseFormatter(request)
        return await formatter.format_collection([server], entry_links={0: [{"rel": "self", "href": f"/{server_id}"}]})

    async def list_cifs_servers(self, request: Request) -> ApiResponse[CIFSServer]:
        """List all CIFS servers."""
        servers = list(self.servers.values())
        formatter = UnityResponseFormatter(request)
        entry_links = {i: [{"rel": "self", "href": f"/{server.id}"}] for i, server in enumerate(servers)}
        return await formatter.format_collection(servers, entry_links=entry_links)

    async def update_cifs_server(
        self, request: Request, server_id: str, server_data: CIFSServerUpdate
    ) -> ApiResponse[CIFSServer]:
        """Update a CIFS server."""
        server = self.servers.get(server_id)
        if not server:
            raise HTTPException(status_code=404, detail=f"CIFS server with ID '{server_id}' not found")

        # Update only provided fields
        update_data = server_data.model_dump(exclude_unset=True)
        logger.info(f"Updating server {server_id} with data: {update_data}")
        logger.info(f"Current server state: {server.model_dump()}")

        server_dict = server.model_dump()
        server_dict.update(update_data)
        logger.info(f"Updated server dict: {server_dict}")

        updated_server = CIFSServer(**server_dict)
        self.servers[server_id] = updated_server  # Update the server in the dictionary
        logger.info(f"Final server state: {self.servers[server_id].model_dump()}")

        formatter = UnityResponseFormatter(request)
        return await formatter.format_collection(
            [updated_server], entry_links={0: [{"rel": "self", "href": f"/{server_id}"}]}
        )

    async def delete_cifs_server(self, request: Request, server_id: str) -> ApiResponse[None]:
        """Delete a CIFS server."""
        if server_id not in self.servers:
            raise HTTPException(status_code=404, detail=f"CIFS server with ID '{server_id}' not found")

        del self.servers[server_id]
        formatter = UnityResponseFormatter(request)
        return await formatter.format_collection([], entry_links={})
