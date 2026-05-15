import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_create_booking(client: AsyncClient):
    # Создаём пользователя
    u = await client.post("/api/v1/auth/register", json={
        "email": "book1@test.com", "password": "pass123", "full_name": "Booker"
    })
    assert u.status_code in [200, 201]
    uid = u.json()["id"]

    # Создаём отель
    h = await client.post("/api/v1/hotels/", json={
        "name": "Booking Hotel", "address": "1 St", "city": "City", "country": "RU", "rating": 4.0
    })
    assert h.status_code in [200, 201]
    hid = h.json()["id"]

    # Создаём комнату
    r = await client.post("/api/v1/rooms/", json={
        "hotel_id": hid, "room_number": "201", "room_type": "lux",
        "price_per_night": 150.0, "max_occupancy": 3
    })
    assert r.status_code in [200, 201]
    rid = r.json()["id"]

    # Создаём бронирование
    response = await client.post("/api/v1/bookings/", json={
        "user_id": uid,
        "room_id": rid,
        "check_in_date": "2026-07-01T14:00:00",
        "check_out_date": "2026-07-05T12:00:00",
        "total_price": 600.0
    })
    assert response.status_code in [200, 201]
    data = response.json()
    assert "id" in data
    assert data["user_id"] == uid
    assert data["room_id"] == rid

@pytest.mark.asyncio
async def test_get_bookings(client: AsyncClient):
    response = await client.get("/api/v1/bookings/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_booking_not_found(client: AsyncClient):
    response = await client.get("/api/v1/bookings/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_booking_invalid_dates(client: AsyncClient):
    u = await client.post("/api/v1/auth/register", json={
        "email": "book2@test.com", "password": "pass123", "full_name": "B2"
    })
    uid = u.json()["id"]

    h = await client.post("/api/v1/hotels/", json={
        "name": "Date Hotel", "address": "2 St", "city": "City", "country": "RU", "rating": 3.0
    })
    hid = h.json()["id"]

    r = await client.post("/api/v1/rooms/", json={
        "hotel_id": hid, "room_number": "301", "room_type": "standard",
        "price_per_night": 100.0, "max_occupancy": 2
    })
    rid = r.json()["id"]

    # check_out раньше check_in
    response = await client.post("/api/v1/bookings/", json={
        "user_id": uid,
        "room_id": rid,
        "check_in_date": "2026-08-01T14:00:00",
        "check_out_date": "2026-07-01T12:00:00",
        "total_price": 100.0
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_booking_negative_price(client: AsyncClient):
    response = await client.post("/api/v1/bookings/", json={
        "user_id": 1, "room_id": 1,
        "check_in_date": "2026-09-01T14:00:00",
        "check_out_date": "2026-09-05T12:00:00",
        "total_price": -100.0
    })
    assert response.status_code == 422