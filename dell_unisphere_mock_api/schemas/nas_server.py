from enum import Enum
from ipaddress import IPv4Address, IPv6Address
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress


class NasServerProtocolEnum(str, Enum):
    NFSv3 = "NFSv3"
    NFSv4 = "NFSv4"
    CIFS = "CIFS"
    Multiprotocol = "Multiprotocol"


class NasServerHealthEnum(str, Enum):
    OK = "OK"
    WARNING = "WARNING"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class NetworkInterfaceTypeEnum(str, Enum):
    PRODUCTION = "Production"
    BACKUP = "Backup"
    MANAGEMENT = "Management"


class AuthenticationTypeEnum(str, Enum):
    NONE = "None"
    KERBEROS = "Kerberos"
    NTLMV2 = "NTLMv2"


class DnsConfig(BaseModel):
    domain: str
    addresses: List[IPvAnyAddress]
    search_domains: Optional[List[str]] = Field(default_factory=list)


class NetworkInterface(BaseModel):
    id: str
    name: str
    ip_address: IPvAnyAddress
    netmask: IPvAnyAddress
    gateway: Optional[IPvAnyAddress]
    interface_type: NetworkInterfaceTypeEnum
    vlan_id: Optional[int] = None


class UserMapping(BaseModel):
    unix_enabled: bool = False
    windows_enabled: bool = False
    ldap_enabled: bool = False
    ldap_server: Optional[str] = None
    ldap_base_dn: Optional[str] = None
    kerberos_enabled: bool = False
    kerberos_realm: Optional[str] = None


class NasServerBase(BaseModel):
    name: str = Field(..., description="User-specified NAS server name")
    description: Optional[str] = Field(None, description="User-specified NAS server description")
    homeSP: str = Field(..., description="Storage Processor (SP) that owns the NAS server")
    pool: str = Field(..., description="Storage pool that contains the NAS server")
    isReplicationDestination: bool = Field(False, description="Indicates whether this is a replication destination")
    currentSP: Optional[str] = Field(None, description="SP currently running the NAS server")
    defaultUnixUser: Optional[str] = Field(None, description="Default Unix user for NFS access")
    defaultWindowsUser: Optional[str] = Field(None, description="Default Windows user for CIFS access")
    currentUnixDirectory: Optional[str] = Field(None, description="Current Unix directory service being used")
    isMultiProtocolEnabled: bool = Field(False, description="Indicates whether multi-protocol sharing is enabled")

    # New fields
    dns_config: Optional[DnsConfig] = None
    network_interfaces: List[NetworkInterface] = Field(default_factory=list)
    user_mapping: Optional[UserMapping] = None
    authentication_type: AuthenticationTypeEnum = Field(default=AuthenticationTypeEnum.NONE)
    replication_status: Optional[str] = None
    configuration_status: Optional[str] = None
    network_status: Optional[str] = None


class NasServerCreate(NasServerBase):
    pass


class NasServerUpdate(BaseModel):
    description: Optional[str] = None
    defaultUnixUser: Optional[str] = None
    defaultWindowsUser: Optional[str] = None
    isMultiProtocolEnabled: Optional[bool] = None
    dns_config: Optional[DnsConfig] = None
    network_interfaces: Optional[List[NetworkInterface]] = None
    user_mapping: Optional[UserMapping] = None
    authentication_type: Optional[AuthenticationTypeEnum] = None


class NasServerResponse(NasServerBase):
    id: str = Field(..., description="Unique identifier of the NAS server")
    health: NasServerHealthEnum = Field(..., description="Health status of the NAS server")
    protocols: List[NasServerProtocolEnum] = Field(..., description="List of protocols enabled on the NAS server")
    fileInterfaces: List[str] = Field([], description="List of file interfaces associated with the NAS server")
    fileSystemCount: int = Field(0, description="Number of file systems hosted by the NAS server")
    model_config = ConfigDict(
        from_attributes=True, json_encoders={IPvAnyAddress: str, IPv4Address: str, IPv6Address: str}
    )


# Network diagnostic schemas
class PingRequest(BaseModel):
    address: IPvAnyAddress
    count: Optional[int] = Field(default=4, ge=1, le=20)
    timeout: Optional[int] = Field(default=5, ge=1, le=60)
    size: Optional[int] = Field(default=32, ge=32, le=65500)


class TracerouteRequest(BaseModel):
    address: IPvAnyAddress
    timeout: Optional[int] = Field(default=5, ge=1, le=60)
    max_hops: Optional[int] = Field(default=30, ge=1, le=255)
