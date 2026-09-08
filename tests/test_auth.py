import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_full_lifecycle(client: AsyncClient):
    uid = uuid.uuid4().hex[:8]
    username = f"user_{uid}"
    email = f"user_{uid}@example.com"
    password = "SuperSecurePassword123!"

    # 1. Successful registration
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert reg_res.status_code == 201, reg_res.text
    user_data = reg_res.json()
    assert user_data["username"] == username
    assert user_data["email"] == email
    assert user_data["level"] == 1
    assert user_data["xp"] == 0
    assert user_data["financial_instinct"] == 0.0
    assert "password_hash" not in user_data

    # 2. Duplicate email
    dup_res = await client.post(
        "/api/v1/auth/register",
        json={"username": f"another_{uid}", "email": email, "password": password},
    )
    assert dup_res.status_code == 409
    assert "Email already registered" in dup_res.json()["detail"]

    # 3. Duplicate username
    dup_uname = await client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"diff_{uid}@example.com", "password": password},
    )
    assert dup_uname.status_code == 409
    assert "Username already taken" in dup_uname.json()["detail"]

    # 4. Invalid email format
    invalid_email = await client.post(
        "/api/v1/auth/register",
        json={"username": f"invalid_{uid}", "email": "not-an-email", "password": password},
    )
    assert invalid_email.status_code == 422

    # 5. Weak / short password
    short_pw = await client.post(
        "/api/v1/auth/register",
        json={"username": f"short_{uid}", "email": f"short_{uid}@example.com", "password": "123"},
    )
    assert short_pw.status_code == 422

    # 6. Login with incorrect password
    bad_login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "WrongPassword!"},
    )
    assert bad_login.status_code == 401

    # 7. Successful login
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    access_token = token_data["access_token"]

    # 8. /auth/me with valid JWT
    me_res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == email
    assert me_data["username"] == username

    # 9. /auth/me with invalid JWT
    bad_jwt = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.jwt.token"},
    )
    assert bad_jwt.status_code == 401

    # 10. /auth/me without header
    no_jwt = await client.get("/api/v1/auth/me")
    assert no_jwt.status_code == 401
