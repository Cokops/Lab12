import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UserCreate
from app.models import User

@pytest.mark.asyncio
async def test_register_user(db_session: AsyncSession, client: AsyncClient):
    user_data = {
        "email": "testuser@example.com",
        "password": "password123",
        "full_name": "Test User"
    }
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data

    # Проверка, что пользователь сохранен в БД
    result = await db_session.execute(
        db_session.query(User).filter(User.email == user_data["email"])
    )
    db_user = result.scalar_one_or_none()
    assert db_user is not None

@pytest.mark.asyncio
async def test_register_existing_email(db_session: AsyncSession, client: AsyncClient):
    user_data = {
        "email": "existing@example.com",
        "password": "password123",
        "full_name": "Existing User"
    }
    # Сначала зарегистрируем пользователя
    await client.post("/api/v1/auth/register", json=user_data)

    # Попытка зарегистрировать с тем же email
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    # Сначала зарегистрируем пользователя
    user_data = {
        "email": "loginuser@example.com",
        "password": "password123",
        "full_name": "Login User"
    }
    await client.post("/api/v1/auth/register", json=user_data)

    # Попытка входа с правильными данными
    response = await client.post(
        "/api/v1/auth/login",
        data={"email": user_data["email"], "password": user_data["password"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_incorrect_password(client: AsyncClient):
    user_data = {
        "email": "wrongpass@example.com",
        "password": "password123",
        "full_name": "Wrong Pass User"
    }
    await client.post("/api/v1/auth/register", json=user_data)

    # Попытка входа с неправильным паролем
    response = await client.post(
        "/api/v1/auth/login",
        data={"email": user_data["email"], "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]