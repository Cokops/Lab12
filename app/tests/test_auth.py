import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User

BASE = "/api/v1/auth"

@pytest.mark.asyncio
async def test_register_user(db_session: AsyncSession, client: AsyncClient):
    response = await client.post(f"{BASE}/register", json={
        "email": "testuser@example.com",
        "password": "password123",
        "full_name": "Test User"
    })
    assert response.status_code == 201, f"Статус: {response.status_code}"
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data

    result = await db_session.execute(select(User).where(User.email == "testuser@example.com"))
    assert result.scalar_one_or_none() is not None

@pytest.mark.asyncio
async def test_register_existing_email(client: AsyncClient):
    await client.post(f"{BASE}/register", json={
        "email": "dup@test.com", "password": "pass123", "full_name": "Dup"
    })
    response = await client.post(f"{BASE}/register", json={
        "email": "dup@test.com", "password": "pass123", "full_name": "Dup2"
    })
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    await client.post(f"{BASE}/register", json={
        "email": "login@test.com", "password": "pass123", "full_name": "Login"
    })
    response = await client.post(f"{BASE}/login", data={
        "username": "login@test.com", "password": "pass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post(f"{BASE}/register", json={
        "email": "wrong@test.com", "password": "pass123", "full_name": "W"
    })
    response = await client.post(f"{BASE}/login", data={
        "username": "wrong@test.com", "password": "WRONG"
    })
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient):
    response = await client.post(f"{BASE}/register", json={
        "email": "short@test.com", "password": "12", "full_name": "S"
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    response = await client.post(f"{BASE}/register", json={
        "email": "notemail", "password": "pass123", "full_name": "B"
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    response = await client.post(f"{BASE}/login", data={
        "username": "no@user.com", "password": "pass123"
    })
    assert response.status_code == 401