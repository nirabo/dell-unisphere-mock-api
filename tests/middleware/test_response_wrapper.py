import logging
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.testclient import TestClient

from dell_unisphere_mock_api.middleware.response_wrapper import ResponseWrapperMiddleware

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_response_wrapper_middleware():
    app = FastAPI()
    app.add_middleware(ResponseWrapperMiddleware)

    @app.get("/test/json")
    async def get_json():
        return {"message": "test"}

    @app.get("/test/list")
    async def get_list():
        return [{"id": 1}, {"id": 2}]

    @app.get("/test/text")
    async def get_text():
        return PlainTextResponse("test")

    @app.get("/test/already-wrapped")
    async def get_wrapped():
        return JSONResponse(
            {
                "@base": "http://test",
                "updated": datetime.now(timezone.utc).isoformat() + "Z",
                "entries": [{"content": {"message": "test"}}],
                "links": [],
            }
        )

    @app.get("/test/error")
    async def get_error():
        raise HTTPException(status_code=404, detail="Resource not found")

    @app.get("/test/unexpected-error")
    async def get_unexpected_error():
        raise ValueError("Something went wrong")

    client = TestClient(app)

    # Test JSON object response
    response = client.get("/test/json")
    assert response.status_code == 200
    data = response.json()
    logger.debug(f"JSON response data: {data}")
    assert "@base" in data
    assert "entries" in data
    assert len(data["entries"]) == 1
    assert data["entries"][0]["content"]["message"] == "test"

    # Test JSON list response
    response = client.get("/test/list")
    assert response.status_code == 200
    data = response.json()
    logger.debug(f"List response data: {data}")
    assert "@base" in data
    assert "entries" in data
    assert len(data["entries"]) == 2
    assert data["entries"][0]["content"]["id"] == 1
    assert data["entries"][1]["content"]["id"] == 2

    # Test non-JSON response
    response = client.get("/test/text")
    assert response.status_code == 200
    assert response.text == "test"

    # Test already wrapped response
    response = client.get("/test/already-wrapped")
    assert response.status_code == 200
    data = response.json()
    logger.debug(f"Already wrapped response data: {data}")
    assert data["@base"] == "http://test"
    assert len(data["entries"]) == 1
    assert data["entries"][0]["content"]["message"] == "test"

    # Test HTTP error response
    response = client.get("/test/error")
    assert response.status_code == 404
    data = response.json()
    assert "errorCode" in data
    assert data["errorCode"] == 404
    assert data["httpStatusCode"] == 404
    assert "Resource not found" in data["messages"]
    assert "created" in data

    # Test unexpected error response
    response = client.get("/test/unexpected-error")
    assert response.status_code == 500
    data = response.json()
    assert "errorCode" in data
    assert data["errorCode"] == 500
    assert data["httpStatusCode"] == 500
    assert "Something went wrong" in data["messages"]
    assert "created" in data
