import pytest


pytestmark = pytest.mark.django_db


def test_delivery_login_invalid_credentials(api_client):
    res = api_client.post(
        "/api/delivery/login/",
        {"username": "nope@example.com", "password": "bad"},
        format="json",
    )
    assert res.status_code == 401


def test_delivery_login_rejects_non_delivery(api_client, make_user):
    user = make_user(email="customer1@example.com", role="customer", password="pass12345!")
    res = api_client.post(
        "/api/delivery/login/",
        {"username": user.email, "password": "pass12345!"},
        format="json",
    )
    assert res.status_code == 403


def test_delivery_login_success(api_client, make_user):
    user = make_user(email="driver1@example.com", role="delivery", password="pass12345!")
    res = api_client.post(
        "/api/delivery/login/",
        {"username": user.email, "password": "pass12345!"},
        format="json",
    )
    assert res.status_code == 200
    assert "access" in res.data
    assert "refresh" in res.data
    assert res.data["user"]["email"] == user.email

