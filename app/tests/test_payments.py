import pytest
from httpx import AsyncClient

BASE = "/api/v1/payments"

@pytest.mark.asyncio
async def test_create_payment(client: AsyncClient):
    # Создаём пользователя
    u = await client.post("/api/v1/auth/register", json={
        "email": "paytest@test.com", "password": "pass123", "full_name": "Payer"
    })
    uid = u.json()["id"]

    # Создаём отель
    h = await client.post("/api/v1/hotels/", json={
        "name": "Pay Hotel", "address": "1 St", "city": "City", "country": "RU", "rating": 4.0
    })
    hid = h.json()["id"]

    # Создаём комнату
    r = await client.post("/api/v1/rooms/", json={
        "hotel_id": hid, "room_number": "401", "room_type": "standard",
        "price_per_night": 100.0, "max_occupancy": 2
    })
    rid = r.json()["id"]

    # Создаём бронирование
    b = await client.post("/api/v1/bookings/", json={
        "user_id": uid, "room_id": rid,
        "check_in_date": "2026-08-01T14:00:00",
        "check_out_date": "2026-08-03T12:00:00",
        "total_price": 200.0
    })
    bid = b.json()["id"]

    # Создаём платёж
    response = await client.post(f"{BASE}/", json={
        "booking_id": bid,
        "amount": 200.0,
        "payment_method": "card"
    })
    assert response.status_code in [200, 201]
    data = response.json()
    assert "id" in data
    assert data["amount"] == 200.0
    assert data["payment_method"] == "card"

@pytest.mark.asyncio
async def test_get_payments(client: AsyncClient):
    response = await client.get(f"{BASE}/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_payment_not_found(client: AsyncClient):
    response = await client.get(f"{BASE}/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_payment_negative_amount(client: AsyncClient):
    response = await client.post(f"{BASE}/", json={
        "booking_id": 1,
        "amount": -100.0,
        "payment_method": "card"
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_payment_empty_method(client: AsyncClient):
    response = await client.post(f"{BASE}/", json={
        "booking_id": 1,
        "amount": 100.0,
        "payment_method": ""
    })
    assert response.status_code == 422