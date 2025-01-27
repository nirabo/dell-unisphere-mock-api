from datetime import datetime

import pytest
from fastapi import Request
from fastapi.testclient import TestClient

from dell_unisphere_mock_api.core.response import UnityResponseFormatter
from dell_unisphere_mock_api.core.response_models import ApiResponse, Entry, Link


def test_format_collection_matches_api_response_model(test_client: TestClient):
    # Create a test request
    scope = {
        "type": "http",
        "headers": [],
        "method": "GET",
        "scheme": "http",
        "server": ("testserver", 80),
        "path": "/api/types/test",
    }
    request = Request(scope=scope)

    # Create test data
    test_data = [{"id": 1, "name": "test1"}, {"id": 2, "name": "test2"}]
    formatter = UnityResponseFormatter(request)

    # Format the response
    formatted_response = formatter.format_collection(test_data)

    # Validate using ApiResponse model
    try:
        api_response = ApiResponse[dict].parse_obj(formatted_response)
        assert api_response.base == "http://testserver/api/types/test"
        assert len(api_response.entries) == 2
        assert isinstance(api_response.updated, datetime)
        assert isinstance(api_response.links, list)

        # Validate entries
        for entry, test_item in zip(api_response.entries, test_data):
            assert entry.content == test_item

    except Exception as e:
        pytest.fail(f"Failed to validate response against ApiResponse model: {str(e)}")


def test_pagination_links(test_client: TestClient):
    scope = {
        "type": "http",
        "headers": [],
        "method": "GET",
        "scheme": "http",
        "server": ("testserver", 80),
        "path": "/api/types/test",
    }
    request = Request(scope=scope)

    test_data = [{"id": i} for i in range(1, 6)]  # 5 items
    pagination = {"page": 2, "total_pages": 3, "total": 15}

    formatter = UnityResponseFormatter(request)
    formatted_response = formatter.format_collection(test_data, pagination)

    # Validate using ApiResponse model
    api_response = ApiResponse[dict].parse_obj(formatted_response)

    # Check pagination links
    link_rels = {link.rel: link.href for link in api_response.links}
    assert "prev" in link_rels
    assert "next" in link_rels
    assert "first" in link_rels
    assert "last" in link_rels

    assert link_rels["prev"] == "?page=1"
    assert link_rels["next"] == "?page=3"
    assert link_rels["first"] == "?page=1"
    assert link_rels["last"] == "?page=3"

    # Check total
    assert formatted_response["total"] == 15
