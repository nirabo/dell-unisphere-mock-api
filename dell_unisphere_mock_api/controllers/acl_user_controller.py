from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from dell_unisphere_mock_api.core.response_models import ApiResponse, Entry, Link
from dell_unisphere_mock_api.models.acl_user import ACLUser, ACLUserCreate, ACLUserUpdate


class ACLUserController:
    def __init__(self):
        self.users: Dict[str, ACLUser] = {}

    def _create_api_response(self, entries: List[Entry], request_path: str) -> ApiResponse:
        """Create standardized API response"""
        base_url = "https://127.0.0.1:8000"
        return ApiResponse(
            **{
                "@base": f"{base_url}/api/types/aclUser/instances",
                "updated": datetime.utcnow(),
                "links": [Link(rel="self", href=f"{base_url}/api/types/aclUser/instances")],
                "entries": entries,
            }
        )

    def _create_entry(self, user: ACLUser, base_url: str) -> Entry:
        """Create standardized entry"""
        return Entry(
            **{
                "@base": "storageObject",
                "content": user,
                "updated": datetime.utcnow(),
                "links": [Link(rel="self", href=f"{base_url}/api/instances/aclUser/{user.id}")],
            }
        )

    def create_user(self, user: ACLUserCreate) -> ACLUser:
        """Create a new ACL user"""
        user_id = str(uuid4())
        new_user = ACLUser(**{**user.dict(), "id": user_id})
        self.users[user_id] = new_user
        return new_user

    def get_user(self, user_id: str) -> Optional[ACLUser]:
        """Get an ACL user by ID"""
        return self.users.get(user_id)

    def list_users(self) -> List[ACLUser]:
        """List all ACL users"""
        return list(self.users.values())

    def update_user(self, user_id: str, update_data: ACLUserUpdate) -> Optional[ACLUser]:
        """Update an ACL user"""
        if user_id not in self.users:
            return None

        user = self.users[user_id]
        update_dict = update_data.dict(exclude_unset=True)
        updated_user = ACLUser(**{**user.dict(), **update_dict})
        self.users[user_id] = updated_user
        return updated_user

    def delete_user(self, user_id: str) -> bool:
        """Delete an ACL user"""
        if user_id not in self.users:
            return False
        del self.users[user_id]
        return True

    def lookup_sid_by_domain_user(self, domain_name: str, user_name: str) -> Optional[Tuple[str, ACLUser]]:
        """Look up a user's SID by domain name and username"""
        for user in self.users.values():
            if user.domain_name.lower() == domain_name.lower() and user.user_name.lower() == user_name.lower():
                return user.sid, user
        return None
