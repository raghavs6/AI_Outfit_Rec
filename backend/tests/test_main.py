import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"ok": True}


def test_create_guest_user_v1_returns_uuid_and_timestamp():
    res = client.post("/v1/users/guest")
    assert res.status_code == 200
    data = res.json()
    assert "user_id" in data
    assert "created_at" in data
    assert len(data["user_id"]) == 36  # UUID format


def test_create_guest_user_v1_unique_ids():
    res1 = client.post("/v1/users/guest")
    res2 = client.post("/v1/users/guest")
    assert res1.json()["user_id"] != res2.json()["user_id"]


def test_cors_header_present_for_allowed_origin():
    res = client.options(
        "/v1/users/guest",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert res.headers.get("access-control-allow-origin") == "http://localhost:5173"
