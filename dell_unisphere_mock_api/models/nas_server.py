import random
import uuid
from datetime import datetime, timezone
from ipaddress import IPv4Address, IPv6Address
from typing import Dict, List, Optional, Union


class NasServerModel:
    def __init__(self):
        self.nas_servers: Dict[str, dict] = {}
        self._name_to_id: Dict[str, str] = {}

    def create_nas_server(self, nas_server_data: dict) -> dict:
        nas_server_id = str(uuid.uuid4())
        # Convert IP addresses to strings if they exist
        if nas_server_data.get("dns_config") and nas_server_data["dns_config"].get("addresses"):
            nas_server_data["dns_config"]["addresses"] = [
                str(addr) for addr in nas_server_data["dns_config"]["addresses"]
            ]

        if nas_server_data.get("network_interfaces"):
            for iface in nas_server_data["network_interfaces"]:
                if "ip_address" in iface:
                    iface["ip_address"] = str(iface["ip_address"])
                if "netmask" in iface:
                    iface["netmask"] = str(iface["netmask"])
                if "gateway" in iface:
                    iface["gateway"] = str(iface["gateway"])

        nas_server = {
            **nas_server_data,
            "id": nas_server_id,
            "health": "OK",
            "protocols": ["NFSv3"] if not nas_server_data.get("isMultiProtocolEnabled") else ["NFSv3", "CIFS"],
            "fileInterfaces": [],
            "fileSystemCount": 0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "configuration_status": "OK",
            "network_status": "OK",
            "replication_status": None,
        }
        self.nas_servers[nas_server_id] = nas_server
        self._name_to_id[nas_server["name"]] = nas_server_id
        return nas_server

    def get_nas_server(self, identifier: str) -> Optional[dict]:
        # Try to get by ID first
        if identifier in self.nas_servers:
            return self.nas_servers[identifier]
        # Then try by name
        nas_id = self._name_to_id.get(identifier)
        return self.nas_servers.get(nas_id) if nas_id else None

    def list_nas_servers(self) -> List[dict]:
        return list(self.nas_servers.values())

    def update_nas_server(self, nas_server_id: str, update_data: dict) -> Optional[dict]:
        nas_server = self.get_nas_server(nas_server_id)
        if not nas_server:
            return None

        for key, value in update_data.items():
            if value is not None:
                nas_server[key] = value

                # Update protocols if multiprotocol setting changes
                if key == "isMultiProtocolEnabled":
                    nas_server["protocols"] = ["NFSv3", "CIFS"] if value else ["NFSv3"]

                # Update name mapping if name changes
                if key == "name":
                    old_name = nas_server["name"]
                    del self._name_to_id[old_name]
                    self._name_to_id[value] = nas_server_id

        nas_server["updated_at"] = datetime.now(timezone.utc)
        return nas_server

    def delete_nas_server(self, identifier: str) -> bool:
        nas_server = self.get_nas_server(identifier)
        if not nas_server:
            return False

        nas_id = nas_server["id"]
        if nas_id in self.nas_servers:
            del self.nas_servers[nas_id]
            if nas_server["name"] in self._name_to_id:
                del self._name_to_id[nas_server["name"]]
            return True
        return False

    def generate_user_mappings_report(self, nas_server_id: str) -> Optional[dict]:
        nas_server = self.get_nas_server(nas_server_id)
        if not nas_server:
            return None

        return {
            "id": str(uuid.uuid4()),
            "nas_server_id": nas_server_id,
            "timestamp": datetime.now(timezone.utc),
            "mappings": {
                "unix_users": ["root", "admin", "user1"],
                "windows_users": ["Administrator", "Guest", "User1"],
                "conflicts": [],
                "unmapped_users": [],
            },
        }

    def update_user_mappings(self, nas_server_id: str, mapping_data: dict) -> Optional[dict]:
        nas_server = self.get_nas_server(nas_server_id)
        if not nas_server:
            return None

        nas_server["user_mapping"] = mapping_data
        nas_server["updated_at"] = datetime.now(timezone.utc)
        return nas_server

    def refresh_configuration(self, nas_server_id: str) -> Optional[dict]:
        nas_server = self.get_nas_server(nas_server_id)
        if not nas_server:
            return None

        nas_server["configuration_status"] = "OK"
        nas_server["updated_at"] = datetime.now(timezone.utc)
        return nas_server

    def ping(
        self,
        nas_server_id: str,
        address: Union[IPv4Address, IPv6Address],
        count: int = 4,
        timeout: int = 5,
        size: int = 32,
    ) -> dict:
        nas_server = self.get_nas_server(nas_server_id)
        if not nas_server:
            return {"error": "NAS server not found"}

        # Simulate ping results
        results = []
        for i in range(count):
            latency = random.uniform(0.1, 50.0)
            results.append({"sequence": i + 1, "bytes": size, "time_ms": round(latency, 2), "ttl": 64})

        return {
            "address": str(address),
            "packets_transmitted": count,
            "packets_received": count,
            "packet_loss": 0,
            "min_latency": min(r["time_ms"] for r in results),
            "avg_latency": sum(r["time_ms"] for r in results) / len(results),
            "max_latency": max(r["time_ms"] for r in results),
            "results": results,
        }

    def traceroute(
        self, nas_server_id: str, address: Union[IPv4Address, IPv6Address], timeout: int = 5, max_hops: int = 30
    ) -> dict:
        nas_server = self.get_nas_server(nas_server_id)
        if not nas_server:
            return {"error": "NAS server not found"}

        # Simulate traceroute results
        hops = []
        for i in range(random.randint(3, max_hops)):
            latency = random.uniform(0.1, 100.0)
            hops.append(
                {
                    "hop": i + 1,
                    "host": f"router-{i+1}.example.com",
                    "ip": f"10.0.{i}.1",
                    "latency_ms": round(latency, 2),
                }
            )

        return {"destination": str(address), "max_hops": max_hops, "timeout": timeout, "hops": hops}
