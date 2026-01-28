from __future__ import annotations


def test_register_user(fastapi_client):
    r = fastapi_client.post(
        "/api/users/register",
        json={"email": "user@example.com", "password": "Password123!"},
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["email"] == "user@example.com"
    assert "id" in data
