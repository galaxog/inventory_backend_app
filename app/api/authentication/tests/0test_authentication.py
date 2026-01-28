from __future__ import annotations


def test_login_and_refresh_flow(fastapi_client):
    # Register
    r = fastapi_client.post(
        "/api/users/register",
        json={"email": "a@example.com", "password": "Password123!"},
    )
    assert r.status_code == 201, r.text

    # Login
    r = fastapi_client.post(
        "/api/authentication/login",
        json={"email": "a@example.com", "password": "Password123!"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert "access_token" in data and "refresh_token" in data

    # Refresh (rotate)
    refresh = data["refresh_token"]
    r = fastapi_client.post(
        "/api/authentication/refresh", headers={"Authorization": f"Bearer {refresh}"}
    )
    assert r.status_code == 200, r.text
    data2 = r.json()
    assert data2["access_token"] != data["access_token"]
    assert data2["refresh_token"] != refresh

    # Old refresh token should now be revoked
    r = fastapi_client.post(
        "/api/authentication/refresh", headers={"Authorization": f"Bearer {refresh}"}
    )
    assert r.status_code == 401
