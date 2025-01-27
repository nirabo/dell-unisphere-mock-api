from datetime import datetime
from typing import List

from fastapi import HTTPException, Request

from dell_unisphere_mock_api.core.response_models import ApiResponse, Entry, Link
from dell_unisphere_mock_api.models.nas_server import NasServerModel
from dell_unisphere_mock_api.schemas.nas_server import NasServerCreate, NasServerResponse, NasServerUpdate


class NasServerController:
    def __init__(self):
        self.nas_server_model = NasServerModel()

    def _create_api_response(self, entries: List[Entry], request: Request) -> ApiResponse:
        """Create standardized API response"""
        base_url = str(request.base_url).rstrip("/")
        return ApiResponse(
            **{
                "@base": f"{base_url}/api/types/nasServer/instances",
                "updated": datetime.utcnow(),
                "links": [Link(rel="self", href=f"{base_url}/api/types/nasServer/instances")],
                "entries": entries,
            }
        )

    def _create_entry(self, nas_server: NasServerResponse, request: Request) -> Entry:
        """Create standardized entry"""
        base_url = str(request.base_url).rstrip("/")
        return Entry(
            **{
                "@base": "storageObject",
                "content": nas_server,
                "updated": datetime.utcnow(),
                "links": [
                    Link(rel="self", href=f"{base_url}/api/instances/nasServer/{nas_server.id}"),
                    Link(rel="pool", href=f"{base_url}/api/instances/pool/{nas_server.pool}"),
                ],
            }
        )

    async def create_nas_server(self, request: Request, nas_server_data: NasServerCreate) -> ApiResponse:
        try:
            nas_server = self.nas_server_model.create_nas_server(nas_server_data.model_dump())
            response = NasServerResponse.model_validate(nas_server)
            return self._create_api_response([self._create_entry(response, request)], request)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_nas_server(self, request: Request, nas_server_id: str) -> ApiResponse:
        nas_server = self.nas_server_model.get_nas_server(nas_server_id)
        if not nas_server:
            raise HTTPException(status_code=404, detail="NAS server not found")
        response = NasServerResponse.model_validate(nas_server)
        return self._create_api_response([self._create_entry(response, request)], request)

    async def list_nas_servers(self, request: Request) -> ApiResponse:
        nas_servers = self.nas_server_model.list_nas_servers()
        responses = [NasServerResponse.model_validate(server) for server in nas_servers]
        entries = [self._create_entry(response, request) for response in responses]
        return self._create_api_response(entries, request)

    async def update_nas_server(
        self, request: Request, nas_server_id: str, update_data: NasServerUpdate
    ) -> ApiResponse:
        nas_server = self.nas_server_model.update_nas_server(nas_server_id, update_data.model_dump(exclude_unset=True))
        if not nas_server:
            raise HTTPException(status_code=404, detail="NAS server not found")
        response = NasServerResponse.model_validate(nas_server)
        return self._create_api_response([self._create_entry(response, request)], request)

    async def delete_nas_server(self, request: Request, nas_server_id: str) -> ApiResponse:
        if not self.nas_server_model.delete_nas_server(nas_server_id):
            raise HTTPException(status_code=404, detail="NAS server not found")
        return self._create_api_response([], request)
