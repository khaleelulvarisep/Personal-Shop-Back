import pytest
import users.views


pytestmark = pytest.mark.django_db


def test_auth_register(api_client, monkeypatch):
    class DummyAsyncResult:
        id = "test-task-id"

    def fake_apply_async(*args, **kwargs):
        return DummyAsyncResult()

    monkeypatch.setattr(users.views.send_otp_email_task, "apply_async", fake_apply_async)

    payload = {
        "email": "newuser@example.com",
        "first_name": "New",
        "last_name": "User",
        "phone_number": "9999999999",
        "password": "pass12345!",
        "confirm_password": "pass12345!",
    }
    res = api_client.post("/api/auth/register/", payload, format="json")
    assert res.status_code in (200, 201)
    assert res.data["email"] == payload["email"]
    assert "task_id" in res.data


def test_auth_verify_otp_happy_path(api_client, make_user):
    user = make_user(email="otp@example.com", is_active=False, is_verified=False, password="pass12345!")
    user.generate_otp()

    res = api_client.post(
        "/api/auth/verify-otp/",
        {"email": user.email, "otp": user.otp},
        format="json",
    )
    assert res.status_code == 200
    assert "access" in res.data
    assert "refresh" in res.data


def test_auth_login_requires_verified(api_client, make_user):
    user = make_user(email="login-unverified@example.com", is_active=False, is_verified=False, password="pass12345!")

    res = api_client.post(
        "/api/auth/login/",
        {"email": user.email, "password": "pass12345!"},
        format="json",
    )
    assert res.status_code in (401, 403)


def test_auth_login_success(api_client, make_user):
    user = make_user(email="login@example.com", is_active=True, is_verified=True, password="pass12345!")

    res = api_client.post(
        "/api/auth/login/",
        {"email": user.email, "password": "pass12345!"},
        format="json",
    )
    assert res.status_code == 200
    assert "access" in res.data
    assert "refresh" in res.data


def test_auth_token_refresh(api_client, make_user):
    user = make_user(email="refresh@example.com", password="pass12345!")

    login = api_client.post(
        "/api/auth/login/",
        {"email": user.email, "password": "pass12345!"},
        format="json",
    )
    assert login.status_code == 200

    res = api_client.post(
        "/api/auth/token/refresh/",
        {"refresh": login.data["refresh"]},
        format="json",
    )
    assert res.status_code == 200
    assert "access" in res.data

