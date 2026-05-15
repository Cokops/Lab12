import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_create_hotel(client: AsyncClient, db_session: AsyncSession):
    # Создание тестового отеля через API
    hotel_data = {
        "name": "Test Hotel",
        "description": "A test hotel",
        "location": "Test City",
        "rating": 4.5
    }
    response = await client.post("/api/v1/hotels/", json=hotel_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == hotel_data["name"]

@pytest.mark.asyncio
async def test_get_hotels(client: AsyncClient, db_session: AsyncSession):
    response = await client.get("/api/v1/hotels/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_hotel_not_found(client: AsyncClient, db_session: AsyncSession):
    response = await client.get("/api/v1/hotels/99999")
    assert response.status_code == 404