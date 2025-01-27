from typing import Optional

from fastapi import HTTPException, Request

from dell_unisphere_mock_api.core.response import UnityResponseFormatter
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.models.filesystem import FilesystemModel
from dell_unisphere_mock_api.schemas.filesystem import FilesystemCreate, FilesystemResponse, FilesystemUpdate


class FilesystemController:
    def __init__(self):
        self.filesystem_model = FilesystemModel()

    async def create_filesystem(self, filesystem_data: FilesystemCreate, request: Request) -> ApiResponse:
        try:
            # Validate NAS server existence (in a real implementation)
            # Validate pool existence and capacity (in a real implementation)

            filesystem = self.filesystem_model.create_filesystem(filesystem_data.model_dump())
            filesystem_response = FilesystemResponse.model_validate(filesystem)
            formatter = UnityResponseFormatter(request)
            return formatter.format_response(
                content=filesystem_response, resource_type="filesystem", resource_id=filesystem_response.id
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_filesystem(self, filesystem_id: str, request: Request) -> ApiResponse:
        filesystem = self.filesystem_model.get_filesystem(filesystem_id)
        if not filesystem:
            raise HTTPException(status_code=404, detail=f"Filesystem {filesystem_id} not found")

        filesystem_response = FilesystemResponse.model_validate(filesystem)
        formatter = UnityResponseFormatter(request)
        return formatter.format_response(
            content=filesystem_response, resource_type="filesystem", resource_id=filesystem_response.id
        )

    async def list_filesystems(self, request: Request) -> ApiResponse:
        filesystems = self.filesystem_model.list_filesystems()
        filesystem_responses = [FilesystemResponse.model_validate(fs) for fs in filesystems]

        formatter = UnityResponseFormatter(request)
        return formatter.format_collection(filesystem_responses)

    async def update_filesystem(
        self, filesystem_id: str, update_data: FilesystemUpdate, request: Request
    ) -> ApiResponse:
        # Validate size increase
        if update_data.size is not None:
            current_fs = self.filesystem_model.get_filesystem(filesystem_id)
            if not current_fs:
                raise HTTPException(status_code=404, detail=f"Filesystem {filesystem_id} not found")
            if update_data.size < current_fs["size"]:
                raise HTTPException(status_code=400, detail="Filesystem size cannot be decreased")

        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}

        filesystem = self.filesystem_model.update_filesystem(filesystem_id, update_dict)
        if not filesystem:
            raise HTTPException(status_code=404, detail=f"Filesystem {filesystem_id} not found")

        filesystem_response = FilesystemResponse.model_validate(filesystem)
        formatter = UnityResponseFormatter(request)
        return formatter.format_response(
            content=filesystem_response, resource_type="filesystem", resource_id=filesystem_response.id
        )

    async def delete_filesystem(self, filesystem_id: str, request: Request) -> Optional[ApiResponse]:
        # Check if filesystem exists
        filesystem = self.filesystem_model.get_filesystem(filesystem_id)
        if not filesystem:
            raise HTTPException(status_code=404, detail=f"Filesystem {filesystem_id} not found")

        # Check if filesystem has any shares
        if filesystem["cifsShares"] or filesystem["nfsShares"]:
            raise HTTPException(status_code=400, detail="Cannot delete filesystem with active shares")

        if self.filesystem_model.delete_filesystem(filesystem_id):
            return None
        raise HTTPException(status_code=500, detail="Failed to delete filesystem")

    async def add_share(self, filesystem_id: str, share_id: str, share_type: str, request: Request) -> ApiResponse:
        if not self.filesystem_model.add_share(filesystem_id, share_id, share_type):
            raise HTTPException(status_code=404, detail=f"Filesystem {filesystem_id} not found")

        filesystem = self.filesystem_model.get_filesystem(filesystem_id)
        filesystem_response = FilesystemResponse.model_validate(filesystem)
        formatter = UnityResponseFormatter(request)
        return formatter.format_response(
            content=filesystem_response, resource_type="filesystem", resource_id=filesystem_response.id
        )

    async def remove_share(self, filesystem_id: str, share_id: str, share_type: str, request: Request) -> ApiResponse:
        if not self.filesystem_model.remove_share(filesystem_id, share_id, share_type):
            raise HTTPException(status_code=404, detail=f"Filesystem {filesystem_id} not found")

        filesystem = self.filesystem_model.get_filesystem(filesystem_id)
        filesystem_response = FilesystemResponse.model_validate(filesystem)
        formatter = UnityResponseFormatter(request)
        return formatter.format_response(
            content=filesystem_response, resource_type="filesystem", resource_id=filesystem_response.id
        )
