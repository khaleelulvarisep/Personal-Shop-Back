import pytest

pytestmark = pytest.mark.django_db

def test_orders_create_requires_auth(api_client):
    res = api_client.post(
        "/api/orders/create/",
        {
            "items_text": "Milk",
            "budget": "100.00",
            "phone_number": "9999999999",
            "address_text": "A",
            "latitude": 12.97,
            "longitude": 77.59,
            "urgency": "2_hours",
        },
        format="json",
    )
    assert res.status_code == 401


def test_orders_create_success(api_client, make_user, auth_header):
    user = make_user(email="order-customer@example.com", password="pass12345!")
    api_client.credentials(HTTP_AUTHORIZATION=auth_header(user))

    res = api_client.post(
        "/api/orders/create/",
        {
            "items_text": "Milk",
            "budget": "100.00",
            "phone_number": "9999999999",
            "address_text": "A",
            "latitude": 12.97,
            "longitude": 77.59,
            "urgency": "2_hours",
        },
        format="json",
    )
    assert res.status_code == 201
    assert res.data["message"] == "Order created successfully"
    assert "data" in res.data


def test_orders_my_orders_requires_auth(api_client):
    res = api_client.get("/api/orders/my-orders/")
    assert res.status_code == 401


def test_orders_my_orders_success(api_client, make_user, auth_header, make_order):
    user = make_user(email="myorders@example.com", password="pass12345!")
    make_order(customer=user)
    api_client.credentials(HTTP_AUTHORIZATION=auth_header(user))

    res = api_client.get("/api/orders/my-orders/")
    assert res.status_code == 200
    assert res.data["message"] == "Orders fetched successfully"
    assert isinstance(res.data["data"], list)


def test_orders_all_orders_lists_pending(api_client, make_user, make_order):
    customer = make_user(email="pending@example.com", password="pass12345!")
    make_order(customer=customer, status="pending")
    make_order(customer=customer, status="accepted")

    res = api_client.get("/api/orders/orders/")
    assert res.status_code == 200
    assert all(order["status"] == "pending" for order in res.data)


def test_orders_nearby_orders_requires_location(api_client):
    res = api_client.get("/api/orders/nearby-orders/")
    assert res.status_code == 400


def test_orders_nearby_orders_success(api_client, make_user, make_order):
    customer = make_user(email="nearby@example.com", password="pass12345!")
    make_order(customer=customer, status="pending", latitude=12.9716, longitude=77.5946)

    res = api_client.get("/api/orders/nearby-orders/?lat=12.9716&lng=77.5946")
    assert res.status_code == 200
    assert isinstance(res.data, list)


def test_orders_order_detail_404(api_client):
    res = api_client.get("/api/orders/order/999999/")
    assert res.status_code == 404


def test_orders_order_detail_success(api_client, make_user, make_order):
    customer = make_user(email="detail@example.com", password="pass12345!")
    order = make_order(customer=customer)
    res = api_client.get(f"/api/orders/order/{order.id}/")
    assert res.status_code == 200
    assert res.data["id"] == order.id


def test_orders_accept_requires_auth(api_client, make_user, make_order):
    customer = make_user(email="accept-customer@example.com", password="pass12345!")
    order = make_order(customer=customer)
    res = api_client.post(f"/api/orders/accept/{order.id}/", {}, format="json")
    assert res.status_code == 401


def test_orders_accept_success(api_client, make_user, auth_header, make_order):
    customer = make_user(email="accept2-customer@example.com", password="pass12345!")
    driver = make_user(email="accept-driver@example.com", role="delivery", password="pass12345!")
    order = make_order(customer=customer, status="pending")

    api_client.credentials(HTTP_AUTHORIZATION=auth_header(driver))
    res = api_client.post(f"/api/orders/accept/{order.id}/", {}, format="json")
    assert res.status_code == 200
    assert res.data["message"] == "Order accepted successfully"


def test_orders_driver_orders_lists_assigned(api_client, make_user, auth_header, make_order):
    driver = make_user(email="driver-orders@example.com", role="delivery", password="pass12345!")
    customer = make_user(email="driver-orders-customer@example.com", password="pass12345!")

    make_order(customer=customer, status="accepted", delivery_partner=driver)
    make_order(customer=customer, status="delivered", delivery_partner=driver)

    api_client.credentials(HTTP_AUTHORIZATION=auth_header(driver))
    res = api_client.get("/api/orders/driver/orders/")
    assert res.status_code == 200
    assert all(order["status"] != "delivered" for order in res.data)


