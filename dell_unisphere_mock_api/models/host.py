from typing import Dict, List, Optional

from dell_unisphere_mock_api.schemas.host import Host, HostCreate, HostUpdate


class HostModel:
    def __init__(self):
        self.hosts: Dict[str, Host] = {}

    def create_host(self, host: HostCreate) -> Host:
        """Create a new host."""
        host_id = f"host_{len(self.hosts) + 1}"
        new_host = Host(
            id=host_id,
            name=host.name,
            description=host.description,
            type=host.type,
            os_type=host.os_type,
            initiators=host.initiators or [],
            host_group=host.host_group,
        )
        self.hosts[host_id] = new_host
        return new_host

    def get_host(self, host_id: str) -> Optional[Host]:
        """Get a host by ID."""
        return self.hosts.get(host_id)

    def get_host_by_name(self, name: str) -> Optional[Host]:
        """Get a host by name."""
        for host in self.hosts.values():
            if host.name == name:
                return host
        return None

    def list_hosts(self) -> List[Host]:
        """List all hosts."""
        return list(self.hosts.values())

    def update_host(self, host_id: str, host_update: HostUpdate) -> Optional[Host]:
        """Update a host."""
        if host_id not in self.hosts:
            return None

        host = self.hosts[host_id]
        update_data = host_update.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(host, field, value)

        return host

    def delete_host(self, host_id: str) -> bool:
        """Delete a host."""
        if host_id not in self.hosts:
            return False
        del self.hosts[host_id]
        return True

    def add_initiator(self, host_id: str, initiator: str) -> bool:
        """Add an initiator to a host."""
        host = self.get_host(host_id)
        if not host:
            return False
        if initiator not in host.initiators:
            host.initiators.append(initiator)
        return True

    def remove_initiator(self, host_id: str, initiator: str) -> bool:
        """Remove an initiator from a host."""
        host = self.get_host(host_id)
        if not host:
            return False
        if initiator in host.initiators:
            host.initiators.remove(initiator)
        return True

    def add_storage_access(self, host_id: str, storage_id: str) -> bool:
        """Add storage access to a host."""
        host = self.get_host(host_id)
        if not host:
            return False
        if storage_id not in host.storage_access:
            host.storage_access.append(storage_id)
        return True

    def remove_storage_access(self, host_id: str, storage_id: str) -> bool:
        """Remove storage access from a host."""
        host = self.get_host(host_id)
        if not host:
            return False
        if storage_id in host.storage_access:
            host.storage_access.remove(storage_id)
        return True
