import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User

AUTH = "/api/v1/auth/register"
BASE = "/api/v1/users"

@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession, client: AsyncClient):
    response = await client.post(f"{BASE}/", json={
        "email": "testuser@example.com",
        "password": "password123",
        "full_name": "Test User"
    })
    assert response.status_code in [200, 201], f"Статус: {response.status_code}"
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data

    result = await db_session.execute(
        select(User).where(User.email == "testuser@example.com")
    )
    assert result.scalar_one_or_none() is not None

@pytest.mark.asyncio
async def test_get_user(client: AsyncClient):
    r = await client.post(f"{BASE}/", json={
        "email": "getuser@example.com",
        "password": "password123",
        "full_name": "Get User"
    })
    uid = r.json()["id"]

    response = await client.get(f"{BASE}/{uid}")
    assert response.status_code == 200
    assert response.json()["id"] == uid

@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient):
    response = await client.get(f"{BASE}/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_user(client: AsyncClient):
    r = await client.post(f"{BASE}/", json={
        "email": "updateuser@example.com",
        "password": "password123",
        "full_name": "Old Name"
    })
    uid = r.json()["id"]

    response = await client.put(f"{BASE}/{uid}", json={
        "full_name": "Updated Name",
        "phone": "+1234567890"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"

@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient):
    r = await client.post(f"{BASE}/", json={
        "email": "deleteuser@example.com",
        "password": "password123",
        "full_name": "Delete Me"
    })
    uid = r.json()["id"]

    response = await client.delete(f"{BASE}/{uid}")
    assert response.status_code == 200

    check = await client.get(f"{BASE}/{uid}")
    assert check.status_code == 404

@pytest.mark.asyncio
async def test_get_users_list(client: AsyncClient):
    await client.post(f"{BASE}/", json={
        "email": "list1@example.com", "password": "pass123", "full_name": "U1"
    })
    await client.post(f"{BASE}/", json={
        "email": "list2@example.com", "password": "pass123", "full_name": "U2"
    })

    response = await client.get(f"{BASE}/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_create_user_invalid_email(client: AsyncClient):
    response = await client.post(f"{BASE}/", json={
        "email": "notanemail",
        "password": "password123",
        "full_name": "Bad Email"
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_user_short_password(client: AsyncClient):
    response = await client.post(f"{BASE}/", json={
        "email": "short@test.com",
        "password": "12",
        "full_name": "Short Pass"
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_user_empty_name(client: AsyncClient):
    response = await client.post(f"{BASE}/", json={
        "email": "empty@test.com",
        "password": "password123",
        "full_name": ""
    })
    assert response.status_code == 422