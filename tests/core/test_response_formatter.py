from datetime import datetime, timezone
from typing import List, Optional

import pytest
from fastapi import HTTPException, Request
from pydantic import BaseModel

from dell_unisphere_mock_api.core.response import UnityResponseFormatter
from dell_unisphere_mock_api.core.response_models import ApiResponse, ErrorDetail


class TestModel(BaseModel):
    id: int
    name: str
    tags: Optional[List[str]] = None


@pytest.fixture
def mock_request():
    class MockRequest:
        def __init__(self):
            self.base_url = "http://testserver"
            self.path = "/test"
            self.url = type("URL", (), {"path": "/test"})()

    return MockRequest()


def test_format_collection_single_item(mock_request):
    """Test formatting a single item into a collection response."""
    formatter = UnityResponseFormatter(mock_request)
    test_data = TestModel(id=1, name="test")

    response = formatter.format_collection([test_data])

    assert response.base == "http://testserver/test"
    assert len(response.entries) == 1
    assert response.entries[0].content == test_data
    assert isinstance(response.entries[0].updated, datetime)
    assert response.entries[0].links == []


def test_format_collection_multiple_items(mock_request):
    """Test formatting multiple items into a collection response."""
    formatter = UnityResponseFormatter(mock_request)
    test_data = [TestModel(id=1, name="test1"), TestModel(id=2, name="test2", tags=["tag1", "tag2"])]

    response = formatter.format_collection(test_data)

    assert response.base == "http://testserver/test"
    assert len(response.entries) == 2
    assert response.entries[0].content == test_data[0]
    assert response.entries[1].content == test_data[1]
    assert isinstance(response.entries[0].updated, datetime)
    assert isinstance(response.entries[1].updated, datetime)
    assert response.entries[0].links == []
    assert response.entries[1].links == []


def test_format_collection_with_pagination(mock_request):
    """Test formatting a collection response with pagination."""
    formatter = UnityResponseFormatter(mock_request)
    test_data = [TestModel(id=i, name=f"test{i}") for i in range(1, 4)]
    pagination = {"page": 2, "total_pages": 3, "total": 10}

    response = formatter.format_collection(test_data, pagination)

    assert response.base == "http://testserver/test"
    assert len(response.entries) == 3
    assert len(response.links) == 2  # prev and next links

    # Verify pagination links
    prev_link = next((link for link in response.links if link.rel == "previous"), None)
    next_link = next((link for link in response.links if link.rel == "next"), None)

    assert prev_link is not None
    assert next_link is not None
    assert prev_link.href == "http://testserver/test?page=1"
    assert next_link.href == "http://testserver/test?page=3"


def test_format_error_http_exception(mock_request):
    """Test formatting an HTTP exception into an error response."""
    formatter = UnityResponseFormatter(mock_request)
    error = HTTPException(status_code=404, detail="Resource not found")

    response = formatter.format_error(error)

    assert isinstance(response, ErrorDetail)
    assert response.error_code == 404
    assert response.http_status_code == 404
    assert response.messages == ["Resource not found"]
    assert isinstance(response.created, datetime)
    assert response.error_messages is None


def test_format_error_with_custom_code(mock_request):
    """Test formatting an error with a custom error code."""
    formatter = UnityResponseFormatter(mock_request)
    error = HTTPException(status_code=400, detail="Bad request")

    response = formatter.format_error(error, error_code=12345)

    assert response.error_code == 12345
    assert response.http_status_code == 400
    assert response.messages == ["Bad request"]


def test_format_error_with_error_messages(mock_request):
    """Test formatting an error with additional error messages."""
    formatter = UnityResponseFormatter(mock_request)
    error = HTTPException(status_code=500, detail="Internal server error")
    error_messages = [
        {"code": "ERR001", "message": "Database connection failed"},
        {"code": "ERR002", "message": "Retry limit exceeded"},
    ]

    response = formatter.format_error(error, error_messages=error_messages)

    assert response.error_code == 500
    assert response.http_status_code == 500
    assert response.messages == ["Internal server error"]
    assert response.error_messages == error_messages


def test_format_error_generic_exception(mock_request):
    """Test formatting a generic exception into an error response."""
    formatter = UnityResponseFormatter(mock_request)
    error = ValueError("Invalid value")

    response = formatter.format_error(error)

    assert response.error_code == 500
    assert response.http_status_code == 500
    assert response.messages == ["Invalid value"]
    assert isinstance(response.created, datetime)
    assert response.error_messages is None
