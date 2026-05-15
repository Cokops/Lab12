import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta

@pytest.mark.asyncio
async def test_create_booking(client: AsyncClient, db_session: AsyncSession):
    # Здесь нужна тестовая логика с использованием client и db_session
    # Пример:
    # response = await client.post("/api/v1/bookings/", json={...})
    # assert response.status_code == 200
    pass

@pytest.mark.asyncio
async def test_get_booking(client: AsyncClient, db_session: AsyncSession):
    pass

@pytest.mark.asyncio
async def test_cancel_booking(client: AsyncClient, db_session: AsyncSession):
    pass