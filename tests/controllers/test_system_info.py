import pytest
from fastapi import HTTPException

from dell_unisphere_mock_api.controllers.system_info import SystemInfoController
from dell_unisphere_mock_api.core.system_info import BasicSystemInfo


@pytest.fixture
def mock_request():
    class MockRequest:
        def __init__(self):
            self.base_url = "http://testserver"
            self.path = "/api/types/basicSystemInfo/instances"
            self.url = type("URL", (), {"path": "/api/types/basicSystemInfo/instances"})()

    return MockRequest()


@pytest.fixture
def system_info_controller():
    return SystemInfoController()


def test_get_collection(system_info_controller, mock_request):
    """Test getting all system info instances."""
    response = system_info_controller.get_collection(mock_request)
    assert response.base == "http://testserver/api/types/basicSystemInfo/instances"
    assert len(response.entries) == 1
    assert isinstance(response.entries[0].content, BasicSystemInfo)
    assert response.entries[0].content.id == "0"
    assert response.entries[0].content.model == "Unity 450F"
    assert response.entries[0].links[0].rel == "self"
    assert response.entries[0].links[0].href == "/0"


def test_get_by_id_found(system_info_controller, mock_request):
    """Test getting system info by existing ID."""
    response = system_info_controller.get_by_id("0", mock_request)
    assert response.base == "http://testserver/api/types/basicSystemInfo/instances"
    assert len(response.entries) == 1
    assert isinstance(response.entries[0].content, BasicSystemInfo)
    assert response.entries[0].content.id == "0"
    assert response.entries[0].content.model == "Unity 450F"
    assert response.entries[0].links[0].rel == "self"
    assert response.entries[0].links[0].href == "/0"


def test_get_by_id_not_found(system_info_controller, mock_request):
    """Test getting system info by non-existent ID."""
    with pytest.raises(HTTPException) as exc:
        system_info_controller.get_by_id("999", mock_request)
    assert exc.value.status_code == 404
    assert exc.value.detail == "System info not found"


def test_get_by_name_found(system_info_controller, mock_request):
    """Test getting system info by existing name."""
    response = system_info_controller.get_by_name("MyStorageSystem", mock_request)
    assert response.base == "http://testserver/api/types/basicSystemInfo/instances"
    assert len(response.entries) == 1
    assert isinstance(response.entries[0].content, BasicSystemInfo)
    assert response.entries[0].content.id == "0"
    assert response.entries[0].content.name == "MyStorageSystem"
    assert response.entries[0].links[0].rel == "self"
    assert response.entries[0].links[0].href == "/0"


def test_get_by_name_not_found(system_info_controller, mock_request):
    """Test getting system info by non-existent name."""
    with pytest.raises(HTTPException) as exc:
        system_info_controller.get_by_name("NonExistentSystem", mock_request)
    assert exc.value.status_code == 404
    assert exc.value.detail == "System info not found for NonExistentSystem"
