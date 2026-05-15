import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_create_payment(client: AsyncClient, db_session: AsyncSession):
    # Тестовая логика
    pass

@pytest.mark.asyncio
async def test_get_payment(client: AsyncClient, db_session: AsyncSession):
    pass