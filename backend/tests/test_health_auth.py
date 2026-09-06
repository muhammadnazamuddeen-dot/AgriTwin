"""Tests for health check and authentication endpoints."""

import pytest


def test_health_check(client):
    """Test that the system health check returns status ok."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_docs_available(client):
    """Test that OpenAPI interactive documentation is reachable."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_user_registration_and_login_flow(client):
    """Test end-to-end user registration, duplicate rejection, login, and profile fetching."""
    user_payload = {
        "name": "Chaudhry Tariq Gujjar",
        "email": "tariq.gujjar@agritwin.pk",
        "phone": "+923001234567",
        "password": "StrongSecretPassword123!",
    }

    # 1. Register new user
    reg_response = client.post("/api/v1/auth/register", json=user_payload)
    assert reg_response.status_code == 201
    user_data = reg_response.json()
    assert user_data["email"] == user_payload["email"]
    assert user_data["name"] == user_payload["name"]
    assert "id" in user_data

    # 2. Reject duplicate registration with same email
    dup_response = client.post("/api/v1/auth/register", json=user_payload)
    assert dup_response.status_code == 400
    assert "already registered" in dup_response.json()["detail"].lower()

    # 3. Reject invalid login credentials
    bad_login = client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": "WrongPassword!"},
    )
    assert bad_login.status_code == 401

    # 4. Successful login and token issuance
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["user"]["email"] == user_payload["email"]

    # 5. Access /auth/me with Bearer token
    token = token_data["access_token"]
    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == user_payload["email"]
    assert me_data["name"] == user_payload["name"]

    # 6. Access /auth/me with agri_session cookie directly (no Bearer header)
    assert "agri_session" in login_response.cookies
    cookie_me_response = client.get("/api/v1/auth/me")
    assert cookie_me_response.status_code == 200
    assert cookie_me_response.json()["email"] == user_payload["email"]

    # 7. Logout clears cookie
    logout_res = client.post("/api/v1/auth/logout")
    assert logout_res.status_code == 200


def test_registration_empty_phone_and_case_insensitive_login(client):
    """Test registration with empty phone string converts to NULL and login is case-insensitive."""
    user1 = {
        "name": "User One",
        "email": "User.One@AgriTwin.PK ",
        "phone": " ",
        "password": "Password123!",
    }
    user2 = {
        "name": "User Two",
        "email": "USER.TWO@AGRITWIN.PK",
        "phone": "",
        "password": "Password123!",
    }

    # 1. First user registration with empty phone
    res1 = client.post("/api/v1/auth/register", json=user1)
    assert res1.status_code == 201
    assert res1.json()["email"] == "user.one@agritwin.pk"
    assert res1.json()["phone"] is None

    # 2. Second user registration with empty phone (must NOT trigger UNIQUE constraint error)
    res2 = client.post("/api/v1/auth/register", json=user2)
    assert res2.status_code == 201
    assert res2.json()["email"] == "user.two@agritwin.pk"
    assert res2.json()["phone"] is None

    # 3. Login with uppercase & padded email
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": " USER.ONE@AGRITWIN.PK ", "password": "Password123!"},
    )
    assert login_res.status_code == 200
    assert login_res.json()["user"]["email"] == "user.one@agritwin.pk"


