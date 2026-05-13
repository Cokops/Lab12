import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import ReviewCreate, ReviewUpdate
from app.models import Review, User, Hotel

@pytest.mark.asyncio
async def test_create_review(db_session: AsyncSession, client: AsyncClient):
    # Сначала создаем пользователя и отель
    user_response = await client.post(
        "/api/v1/users/",
        json={"email": "user@example.com", "password": "password123", "full_name": "Test User"}
    )
    user_id = user_response.json()["id"]
    
    hotel_response = await client.post(
        "/api/v1/hotels/",
        json={
            "name": "Test Hotel",
            "description": "A nice test hotel",
            "address": "123 Test St",
            "stars": 4,
            "amenities": ["WiFi", "Parking"]
        }
    )
    hotel_id = hotel_response.json()["id"]

    # Создаем отзыв
    review_data = {
        "user_id": user_id,
        "hotel_id": hotel_id,
        "rating": 4.5,
        "comment": "Great hotel!"
    }
    response = await client.post("/api/v1/reviews/", json=review_data)
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == user_id
    assert data["hotel_id"] == hotel_id
    assert data["rating"] == 4.5
    assert data["comment"] == "Great hotel!"
    assert "id" in data

    # Проверка, что отзыв сохранен в БД
    result = await db_session.execute(
        db_session.query(Review).filter(Review.id == data["id"])
    )
    db_review = result.scalar_one_or_none()
    assert db_review is not None

@pytest.mark.asyncio
async def test_get_review(db_session: AsyncSession, client: AsyncClient):
    # Сначала создаем отзыв
    user_response = await client.post(
        "/api/v1/users/",
        json={"email": "user2@example.com", "password": "password123", "full_name": "Test User 2"}
    )
    user_id = user_response.json()["id"]
    
    hotel_response = await client.post(
        "/api/v1/hotels/",
        json={
            "name": "Test Hotel 2",
            "description": "Another test hotel",
            "address": "456 Test St",
            "stars": 5,
            "amenities": ["WiFi", "Spa", "Gym"]
        }
    )
    hotel_id = hotel_response.json()["id"]

    review_data = {
        "user_id": user_id,
        "hotel_id": hotel_id,
        "rating": 5.0,
        "comment": "Excellent service!"
    }
    response = await client.post("/api/v1/reviews/", json=review_data)
    review_id = response.json()["id"]

    # Получаем отзыв по ID
    response = await client.get(f"/api/v1/reviews/{review_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == review_id
    assert data["user_id"] == user_id
    assert data["hotel_id"] == hotel_id
    assert data["rating"] == 5.0
    assert data["comment"] == "Excellent service!"

@pytest.mark.asyncio
async def test_update_review(db_session: AsyncSession, client: AsyncClient):
    # Сначала создаем отзыв
    user_response = await client.post(
        "/api/v1/users/",
        json={"email": "user3@example.com", "password": "password123", "full_name": "Test User 3"}
    )
    user_id = user_response.json()["id"]
    
    hotel_response = await client.post(
        "/api/v1/hotels/",
        json={
            "name": "Test Hotel 3",
            "description": "Third test hotel",
            "address": "789 Test St",
            "stars": 3,
            "amenities": ["WiFi"]
        }
    )
    hotel_id = hotel_response.json()["id"]

    review_data = {
        "user_id": user_id,
        "hotel_id": hotel_id,
        "rating": 3.0,
        "comment": "Good hotel"
    }
    response = await client.post("/api/v1/reviews/", json=review_data)
    review_id = response.json()["id"]

    # Обновляем отзыв
    update_data = {
        "rating": 4.0,
        "comment": "Very good hotel!"
    }
    response = await client.put(f"/api/v1/reviews/{review_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == review_id
    assert data["rating"] == 4.0
    assert data["comment"] == "Very good hotel!"

@pytest.mark.asyncio
async def test_delete_review(db_session: AsyncSession, client: AsyncClient):
    # Сначала создаем отзыв
    user_response = await client.post(
        "/api/v1/users/",
        json={"email": "user4@example.com", "password": "password123", "full_name": "Test User 4"}
    )
    user_id = user_response.json()["id"]
    
    hotel_response = await client.post(
        "/api/v1/hotels/",
        json={
            "name": "Test Hotel 4",
            "description": "Fourth test hotel",
            "address": "101 Test St",
            "stars": 4,
            "amenities": ["WiFi", "Parking", "Pool"]
        }
    )
    hotel_id = hotel_response.json()["id"]

    review_data = {
        "user_id": user_id,
        "hotel_id": hotel_id,
        "rating": 4.0,
        "comment": "Nice place"
    }
    response = await client.post("/api/v1/reviews/", json=review_data)
    review_id = response.json()["id"]

    # Удаляем отзыв
    response = await client.delete(f"/api/v1/reviews/{review_id}")
    assert response.status_code == 200

    # Проверяем, что отзыва больше нет
    response = await client.get(f"/api/v1/reviews/{review_id}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_reviews_list(db_session: AsyncSession, client: AsyncClient):
    # Создаем несколько отзывов
    user_response = await client.post(
        "/api/v1/users/",
        json={"email": "user5@example.com", "password": "password123", "full_name": "Test User 5"}
    )
    user_id = user_response.json()["id"]
    
    hotel_response = await client.post(
        "/api/v1/hotels/",
        json={
            "name": "Test Hotel 5",
            "description": "Fifth test hotel",
            "address": "202 Test St",
            "stars": 5,
            "amenities": ["WiFi", "Spa", "Gym", "Pool", "Restaurant"]
        }
    )
    hotel_id = hotel_response.json()["id"]

    reviews_data = [
        {"user_id": user_id, "hotel_id": hotel_id, "rating": 4.5, "comment": "Great experience"},
        {"user_id": user_id, "hotel_id": hotel_id, "rating": 5.0, "comment": "Excellent service"}
    ]
    
    for review_data in reviews_data:
        await client.post("/api/v1/reviews/", json=review_data)
    
    # Получаем список отзывов
    response = await client.get("/api/v1/reviews/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    
    # Проверяем, что все созданные отзывы присутствуют
    ratings = [review["rating"] for review in data]
    for review_data in reviews_data:
        assert review_data["rating"] in ratings

@pytest.mark.asyncio
async def test_create_review_invalid_rating(db_session: AsyncSession, client: AsyncClient):
    # Сначала создаем пользователя и отель
    user_response = await client.post(
        "/api/v1/users/",
        json={"email": "user6@example.com", "password": "password123", "full_name": "Test User 6"}
    )
    user_id = user_response.json()["id"]
    
    hotel_response = await client.post(
        "/api/v1/hotels/",
        json={
            "name": "Test Hotel 6",
            "description": "Sixth test hotel",
            "address": "303 Test St",
            "stars": 4,
            "amenities": ["WiFi", "Parking"]
        }
    )
    hotel_id = hotel_response.json()["id"]

    # Пытаемся создать отзыв с рейтингом меньше 1.0
    review_data = {
        "user_id": user_id,
        "hotel_id": hotel_id,
        "rating": 0.5,
        "comment": "Rating too low"
    }
    response = await client.post("/api/v1/reviews/", json=review_data)
    assert response.status_code == 422
    
    # Пытаемся создать отзыв с рейтингом больше 5.0
    review_data["rating"] = 5.5
    response = await client.post("/api/v1/reviews/", json=review_data)
    assert response.status_code == 422