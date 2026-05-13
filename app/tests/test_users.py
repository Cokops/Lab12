import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UserCreate, UserUpdate
from app.models import User

@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession, client: AsyncClient):
    user_data = {
        "email": "testuser@example.com",
        "password": "password123",
        "full_name": "Test User"
    }
    response = await client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert data["role"] == "user"
    assert data["is_active"] is True

    # Проверка, что пользователь сохранен в БД
    result = await db_session.execute(
        db_session.query(User).filter(User.email == user_data["email"])
    )
    db_user = result.scalar_one_or_none()
    assert db_user is not None

@pytest.mark.asyncio
async def test_get_user(db_session: AsyncSession, client: AsyncClient):
    # Сначала создаем пользователя
    user_data = {
        "email": "getuser@example.com",
        "password": "password123",
        "full_name": "Get User"
    }
    response = await client.post("/api/v1/users/", json=user_data)
    user_id = response.json()["id"]

    # Получаем пользователя по ID
    response = await client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]

@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession, client: AsyncClient):
    # Сначала создаем пользователя
    user_data = {
        "email": "updateuser@example.com",
        "password": "password123",
        "full_name": "Update User"
    }
    response = await client.post("/api/v1/users/", json=user_data)
    user_id = response.json()["id"]

    # Обновляем пользователя
    update_data = {
        "full_name": "Updated Name",
        "phone": "+1234567890"
    }
    response = await client.put(f"/api/v1/users/{user_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["full_name"] == update_data["full_name"]
    assert data["phone"] == update_data["phone"]

@pytest.mark.asyncio
async def test_delete_user(db_session: AsyncSession, client: AsyncClient):
    # Сначала создаем пользователя
    user_data = {
        "email": "deleteuser@example.com",
        "password": "password123",
        "full_name": "Delete User"
    }
    response = await client.post("/api/v1/users/", json=user_data)
    user_id = response.json()["id"]

    # Удаляем пользователя
    response = await client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 200

    # Проверяем, что пользователя больше нет
    response = await client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_users_list(db_session: AsyncSession, client: AsyncClient):
    # Создаем несколько пользователей
    users_data = [
        {"email": "user1@example.com", "password": "password123", "full_name": "User One"},
        {"email": "user2@example.com", "password": "password123", "full_name": "User Two"}
    ]
    
    for user_data in users_data:
        await client.post("/api/v1/users/", json=user_data)
    
    # Получаем список пользователей
    response = await client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    
    # Проверяем, что все созданные пользователи присутствуют
    emails = [user["email"] for user in data]
    for user_data in users_data:
        assert user_data["email"] in emails