import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Review

BASE = "/api/v1/reviews"
AUTH = "/api/v1/auth/register"
HOTELS = "/api/v1/hotels"

@pytest.mark.asyncio
async def test_create_review(client: AsyncClient):
    # Создаём пользователя
    u = await client.post(AUTH, json={
        "email": "rev1@test.com", "password": "pass123", "full_name": "Rev1"
    })
    uid = u.json()["id"]

    # Создаём отель
    h = await client.post(f"{HOTELS}/", json={
        "name": "Review Hotel", "address": "1 St", "city": "City", "country": "RU", "rating": 4.0
    })
    hid = h.json()["id"]

    # Создаём отзыв
    response = await client.post(f"{BASE}/", json={
        "user_id": uid,
        "hotel_id": hid,
        "rating": 4.5,
        "comment": "Great hotel!"
    })
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["rating"] == 4.5
    assert data["comment"] == "Great hotel!"
    assert "id" in data

@pytest.mark.asyncio
async def test_get_reviews(client: AsyncClient):
    response = await client.get(f"{BASE}/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_review_not_found(client: AsyncClient):
    response = await client.get(f"{BASE}/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_review_invalid_rating_low(client: AsyncClient):
    u = await client.post(AUTH, json={
        "email": "rev2@test.com", "password": "pass123", "full_name": "Rev2"
    })
    uid = u.json()["id"]
    h = await client.post(f"{HOTELS}/", json={
        "name": "H2", "address": "A", "city": "C", "country": "R", "rating": 3.0
    })
    hid = h.json()["id"]

    response = await client.post(f"{BASE}/", json={
        "user_id": uid, "hotel_id": hid, "rating": 0.5, "comment": "Too low"
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_review_invalid_rating_high(client: AsyncClient):
    u = await client.post(AUTH, json={
        "email": "rev3@test.com", "password": "pass123", "full_name": "Rev3"
    })
    uid = u.json()["id"]
    h = await client.post(f"{HOTELS}/", json={
        "name": "H3", "address": "A", "city": "C", "country": "R", "rating": 3.0
    })
    hid = h.json()["id"]

    response = await client.post(f"{BASE}/", json={
        "user_id": uid, "hotel_id": hid, "rating": 5.5, "comment": "Too high"
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_review_negative_rating(client: AsyncClient):
    response = await client.post(f"{BASE}/", json={
        "user_id": 1, "hotel_id": 1, "rating": -1.0, "comment": "Negative"
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_update_review(client: AsyncClient):
    u = await client.post(AUTH, json={
        "email": "rev4@test.com", "password": "pass123", "full_name": "Rev4"
    })
    uid = u.json()["id"]
    h = await client.post(f"{HOTELS}/", json={
        "name": "H4", "address": "A", "city": "C", "country": "R", "rating": 3.0
    })
    hid = h.json()["id"]

    r = await client.post(f"{BASE}/", json={
        "user_id": uid, "hotel_id": hid, "rating": 3.0, "comment": "Old"
    })
    rid = r.json()["id"]

    response = await client.put(f"{BASE}/{rid}", json={
        "rating": 5.0, "comment": "Updated!"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 5.0
    assert data["comment"] == "Updated!"

@pytest.mark.asyncio
async def test_delete_review(client: AsyncClient):
    u = await client.post(AUTH, json={
        "email": "rev5@test.com", "password": "pass123", "full_name": "Rev5"
    })
    uid = u.json()["id"]
    h = await client.post(f"{HOTELS}/", json={
        "name": "H5", "address": "A", "city": "C", "country": "R", "rating": 3.0
    })
    hid = h.json()["id"]

    r = await client.post(f"{BASE}/", json={
        "user_id": uid, "hotel_id": hid, "rating": 4.0, "comment": "Delete me"
    })
    rid = r.json()["id"]

    response = await client.delete(f"{BASE}/{rid}")
    assert response.status_code == 200

    check = await client.get(f"{BASE}/{rid}")
    assert check.status_code == 404