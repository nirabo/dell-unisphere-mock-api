from uuid import uuid4

from fastapi import HTTPException, Request

from dell_unisphere_mock_api.core.response import UnityResponseFormatter
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.models.acl_user import ACLUser, ACLUserCreate, ACLUserUpdate


class ACLUserController:
    """Controller for managing ACL users."""

    def __init__(self):
        self.users: dict[str, ACLUser] = {}

    def create_user(self, request: Request, user_data: ACLUserCreate) -> ApiResponse[ACLUser]:
        """Create a new ACL user."""
        user_id = str(uuid4())
        user = ACLUser(
            id=user_id,
            user_name=user_data.user_name,
            domain_name=user_data.domain_name,
            sid=user_data.sid,
            is_domain_user=user_data.is_domain_user,
            is_local_user=user_data.is_local_user,
        )

        self.users[user_id] = user
        formatter = UnityResponseFormatter(request)
        return formatter.format_collection([user], entry_links={0: [{"rel": "self", "href": f"/{user_id}"}]})

    def get_user(self, request: Request, user_id: str) -> ApiResponse[ACLUser]:
        """Get an ACL user by ID."""
        user = self.users.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"ACL user with ID '{user_id}' not found")

        formatter = UnityResponseFormatter(request)
        return formatter.format_collection([user], entry_links={0: [{"rel": "self", "href": f"/{user_id}"}]})

    def list_users(self, request: Request) -> ApiResponse[ACLUser]:
        """List all ACL users."""
        users = list(self.users.values())
        formatter = UnityResponseFormatter(request)
        entry_links = {i: [{"rel": "self", "href": f"/{user.id}"}] for i, user in enumerate(users)}
        return formatter.format_collection(users, entry_links=entry_links)

    def update_user(self, request: Request, user_id: str, user_data: ACLUserUpdate) -> ApiResponse[ACLUser]:
        """Update an ACL user."""
        user = self.users.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"ACL user with ID '{user_id}' not found")

        # Update user fields
        update_data = user_data.model_dump(exclude_unset=True)
        user_dict = user.model_dump()
        user_dict.update(update_data)
        updated_user = ACLUser(**user_dict)
        self.users[user_id] = updated_user

        formatter = UnityResponseFormatter(request)
        return formatter.format_collection([updated_user], entry_links={0: [{"rel": "self", "href": f"/{user_id}"}]})

    def delete_user(self, request: Request, user_id: str) -> ApiResponse[None]:
        """Delete an ACL user."""
        if user_id not in self.users:
            raise HTTPException(status_code=404, detail=f"ACL user with ID '{user_id}' not found")

        del self.users[user_id]
        formatter = UnityResponseFormatter(request)
        return formatter.format_collection([], entry_links={})

    def lookup_sid_by_domain_user(self, request: Request, domain: str, username: str) -> ApiResponse[ACLUser]:
        """Look up an ACL user by domain and username."""
        for user in self.users.values():
            if user.domain_name == domain and user.user_name == username:
                formatter = UnityResponseFormatter(request)
                return formatter.format_collection([user], entry_links={0: [{"rel": "self", "href": f"/{user.id}"}]})

        raise HTTPException(status_code=404, detail=f"No user found for domain '{domain}' and username '{username}'")
