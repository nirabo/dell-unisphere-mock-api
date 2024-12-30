import pytest

from dell_unisphere_mock_api.schemas.host import Host, HostCreate, HostTypeEnum, HostUpdate


def test_host_type_enum_values():
    """Test that HostTypeEnum has the correct values"""
    assert HostTypeEnum.WINDOWS == "Windows"
    assert HostTypeEnum.LINUX == "Linux"
    assert HostTypeEnum.VMWARE == "VMware"
    assert HostTypeEnum.OTHER == "Other"


def test_host_create_schema():
    """Test HostCreate schema validation"""
    # Valid data
    valid_data = {"name": "test-host", "type": HostTypeEnum.LINUX, "description": "Test host"}
    host = HostCreate(**valid_data)
    assert host.name == "test-host"
    assert host.type == HostTypeEnum.LINUX
    assert host.description == "Test host"

    # Test missing required fields
    with pytest.raises(ValueError):
        HostCreate(name="test-host")


def test_host_update_schema():
    """Test HostUpdate schema validation"""
    # Valid data
    valid_data = {"description": "Updated description", "os_type": "CentOS 8"}
    host = HostUpdate(**valid_data)
    assert host.description == "Updated description"
    assert host.os_type == "CentOS 8"

    # Test empty update
    empty_update = {}
    host = HostUpdate(**empty_update)
    assert host.description is None
    assert host.os_type is None


def test_host_schema():
    """Test Host schema validation"""
    # Valid data
    valid_data = {
        "id": "host-123",
        "name": "test-host",
        "type": HostTypeEnum.LINUX,
        "description": "Test host",
        "initiators": ["iqn.1994-05.com.redhat:2bfbc0884dc4"],
        "health": "OK",
    }
    host = Host(**valid_data)
    assert host.id == "host-123"
    assert host.name == "test-host"
    assert host.type == HostTypeEnum.LINUX
    assert host.description == "Test host"
    assert host.initiators == ["iqn.1994-05.com.redhat:2bfbc0884dc4"]
    assert host.health == "OK"

    # Test missing required fields
    with pytest.raises(ValueError):
        Host(id="host-123")


def test_host_schema_config():
    """Test Host schema configuration"""
    # Test schema example
    example = Host.model_config["json_schema_extra"]["example"]
    assert example["id"] == "host_1"
    assert example["name"] == "test_host"
    assert example["type"] == "Linux"
    assert example["description"] == "Test host"
    assert example["initiators"] == ["iqn.1994-05.com.redhat:2bfbc0884dc4"]
