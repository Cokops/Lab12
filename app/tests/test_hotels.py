import pytest
from httpx import AsyncClient

BASE = "/api/v1/hotels"

@pytest.mark.asyncio
async def test_create_hotel(client: AsyncClient):
    response = await client.post(f"{BASE}/", json={
        "name": "Test Hotel",
        "address": "123 St",
        "city": "City",
        "country": "RU",
        "description": "Nice",
        "rating": 4.0
    })
    assert response.status_code in [200, 201], f"Статус: {response.status_code}"
    data = response.json()
    assert data["name"] == "Test Hotel"
    assert "id" in data

@pytest.mark.asyncio
async def test_get_hotels(client: AsyncClient):
    response = await client.get(f"{BASE}/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_hotel_not_found(client: AsyncClient):
    response = await client.get(f"{BASE}/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_hotel_invalid_rating(client: AsyncClient):
    response = await client.post(f"{BASE}/", json={
        "name": "Bad", "address": "A", "city": "C", "country": "R", "rating": 6.0
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_hotel_empty_name(client: AsyncClient):
    response = await client.post(f"{BASE}/", json={
        "name": "", "address": "A", "city": "C", "country": "R", "rating": 3.0
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_hotel_negative_rating(client: AsyncClient):
    response = await client.post(f"{BASE}/", json={
        "name": "Neg", "address": "A", "city": "C", "country": "R", "rating": -1.0
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_update_hotel(client: AsyncClient):
    r = await client.post(f"{BASE}/", json={
        "name": "Old", "address": "Old St", "city": "Old City", "country": "RU", "rating": 3.0
    })
    assert r.status_code in [200, 201]
    hid = r.json()["id"]

    response = await client.put(f"{BASE}/{hid}", json={"name": "New", "rating": 5.0})
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_hotel(client: AsyncClient):
    r = await client.post(f"{BASE}/", json={
        "name": "Del", "address": "D St", "city": "C", "country": "RU", "rating": 2.0
    })
    assert r.status_code in [200, 201]
    hid = r.json()["id"]

    response = await client.delete(f"{BASE}/{hid}")
    assert response.status_code == 200

    check = await client.get(f"{BASE}/{hid}")
    assert check.status_code == 404