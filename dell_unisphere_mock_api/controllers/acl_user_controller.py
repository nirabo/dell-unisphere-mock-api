from datetime import datetime
from typing import Dict, List
from uuid import uuid4

from fastapi import HTTPException, Request

from dell_unisphere_mock_api.core.response_models import ApiResponse, Entry, Link
from dell_unisphere_mock_api.models.acl_user import ACLUser, ACLUserCreate, ACLUserUpdate


class ACLUserController:
    def __init__(self):
        self.users: Dict[str, ACLUser] = {}

    def _create_api_response(self, entries: List[Entry], request: Request) -> ApiResponse:
        """Create standardized API response"""
        base_url = str(request.base_url).rstrip("/")
        return ApiResponse(
            **{
                "@base": f"{base_url}/api/types/aclUser/instances",
                "updated": datetime.utcnow(),
                "links": [Link(rel="self", href=f"{base_url}/api/types/aclUser/instances")],
                "entries": entries,
            }
        )

    def _create_entry(self, user: ACLUser, request: Request) -> Entry:
        """Create standardized entry"""
        base_url = str(request.base_url).rstrip("/")
        return Entry(
            **{
                "@base": "storageObject",
                "content": user,
                "updated": datetime.utcnow(),
                "links": [Link(rel="self", href=f"{base_url}/api/instances/aclUser/{user.id}")],
            }
        )

    async def create_user(self, request: Request, user: ACLUserCreate) -> ApiResponse:
        """Create a new ACL user"""
        try:
            user_id = str(uuid4())
            new_user = ACLUser(**{**user.model_dump(), "id": user_id})
            self.users[user_id] = new_user
            return self._create_api_response([self._create_entry(new_user, request)], request)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_user(self, request: Request, user_id: str) -> ApiResponse:
        """Get an ACL user by ID"""
        user = self.users.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="ACL user not found")
        return self._create_api_response([self._create_entry(user, request)], request)

    async def list_users(self, request: Request) -> ApiResponse:
        """List all ACL users"""
        entries = [self._create_entry(user, request) for user in self.users.values()]
        return self._create_api_response(entries, request)

    async def update_user(self, request: Request, user_id: str, update_data: ACLUserUpdate) -> ApiResponse:
        """Update an ACL user"""
        if user_id not in self.users:
            raise HTTPException(status_code=404, detail="ACL user not found")

        user = self.users[user_id]
        update_dict = update_data.model_dump(exclude_unset=True)
        updated_user = ACLUser(**{**user.model_dump(), **update_dict})
        self.users[user_id] = updated_user
        return self._create_api_response([self._create_entry(updated_user, request)], request)

    async def delete_user(self, request: Request, user_id: str) -> ApiResponse:
        """Delete an ACL user"""
        if user_id not in self.users:
            raise HTTPException(status_code=404, detail="ACL user not found")
        del self.users[user_id]
        return self._create_api_response([], request)

    async def lookup_sid_by_domain_user(self, request: Request, domain_name: str, user_name: str) -> ApiResponse:
        """Look up a user's SID by domain name and username"""
        for user in self.users.values():
            if user.domain_name.lower() == domain_name.lower() and user.user_name.lower() == user_name.lower():
                return self._create_api_response([self._create_entry(user, request)], request)
        raise HTTPException(status_code=404, detail="ACL user not found")
