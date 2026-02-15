"""
Tests for authentication endpoints.
Uses shared conftest.py fixtures (SQLite, no PostGIS).
"""
def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert data["is_active"] is True
    assert data["notifications_processions"] is True
    assert data["notifications_restrictions"] is True


def test_register_duplicate_email(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "anotherpassword"},
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login_success(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "somepassword"},
    )
    assert response.status_code == 401


def test_refresh_token(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_get_current_user(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    access_token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_get_current_user_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403


def test_refresh_token_for_deleted_user_returns_401(client, db):
    client.post(
        "/api/v1/auth/register",
        json={"email": "to-delete@example.com", "password": "testpassword123"},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "to-delete@example.com", "password": "testpassword123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    from app.models.models import User

    user = db.query(User).filter(User.email == "to-delete@example.com").first()
    db.delete(user)
    db.commit()

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "User not found"


def test_refresh_token_for_inactive_user_returns_403(client, db):
    client.post(
        "/api/v1/auth/register",
        json={"email": "inactive@example.com", "password": "testpassword123"},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "inactive@example.com", "password": "testpassword123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    from app.models.models import User

    user = db.query(User).filter(User.email == "inactive@example.com").first()
    user.is_active = False
    db.commit()

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Inactive user"


def test_notification_settings_get_and_patch(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "prefs@example.com", "password": "testpassword123"},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "prefs@example.com", "password": "testpassword123"},
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    get_response = client.get("/api/v1/auth/me/notifications", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json() == {
        "notifications_processions": True,
        "notifications_restrictions": True,
    }

    patch_response = client.patch(
        "/api/v1/auth/me/notifications",
        headers=headers,
        json={"notifications_restrictions": False},
    )
    assert patch_response.status_code == 200
    assert patch_response.json() == {
        "notifications_processions": True,
        "notifications_restrictions": False,
    }


def test_notification_settings_patch_requires_payload(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "prefs2@example.com", "password": "testpassword123"},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "prefs2@example.com", "password": "testpassword123"},
    )
    access_token = login_response.json()["access_token"]

    response = client.patch(
        "/api/v1/auth/me/notifications",
        headers={"Authorization": f"Bearer {access_token}"},
        json={},
    )
    assert response.status_code == 422
