import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from order.models import Order


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture()
def make_user(db):
    def _make_user(
        *,
        email: str,
        password: str = "pass12345",
        role: str = "customer",
        is_active: bool = True,
        is_verified: bool = True,
        first_name: str = "Test",
        last_name: str = "User",
    ) -> User:
        return User.objects.create_user(
            email=email,
            password=password,
            role=role,
            is_active=is_active,
            is_verified=is_verified,
            first_name=first_name,
            last_name=last_name,
        )

    return _make_user


@pytest.fixture()
def auth_header():
    def _auth_header(user: User) -> str:
        refresh = RefreshToken.for_user(user)
        return f"Bearer {refresh.access_token}"

    return _auth_header


@pytest.fixture()
def make_order(db, make_user):
    def _make_order(
        *,
        customer: User | None = None,
        status: str = "pending",
        delivery_partner: User | None = None,
        latitude: float = 12.9716,
        longitude: float = 77.5946,
    ) -> Order:
        if customer is None:
            customer = make_user(email="customer@example.com")

        return Order.objects.create(
            customer=customer,
            delivery_partner=delivery_partner,
            items_text="Milk, bread",
            note="",
            budget="100.00",
            urgency="2_hours",
            phone_number="9999999999",
            address_text="Test address",
            latitude=latitude,
            longitude=longitude,
            status=status,
        )

    return _make_order

