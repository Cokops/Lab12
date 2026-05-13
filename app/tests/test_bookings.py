from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine
from app.models import Base, User, Booking, Room, Hotel
from app.schemas import BookingCreate
from app.core.security import get_password_hash
from datetime import datetime, date, timedelta
import pytest
import asyncio

client = TestClient(app)

class TestBookingAPI:
    @pytest.fixture(autouse=True)
    def setup_db(self):
        # Создаем таблицы для тестов
        Base.metadata.create_all(bind=engine)
        yield
        # Очищаем базу данных после тестов
        Base.metadata.drop_all(bind=engine)
    
    @pytest.fixture
    def db_session(self):
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    @pytest.fixture
    async def create_test_user(self, db_session):
        # Создаем тестового пользователя
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password"),
            full_name="Test User",
            role="user"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user
    
    @pytest.fixture
    async def create_test_hotel(self, db_session):
        # Создаем тестовый отель
        hotel = Hotel(
            name="Test Hotel",
            description="Test Description",
            location="Test Location",
            rating=4.5
        )
        db_session.add(hotel)
        await db_session.commit()
        await db_session.refresh(hotel)
        return hotel
    
    @pytest.fixture
    async def create_test_room(self, db_session, create_test_hotel):
        # Создаем тестовую комнату
        room = Room(
            hotel_id=create_test_hotel.id,
            room_number="101",
            room_type="standart",
            price_per_night=100,
            is_available=True
        )
        db_session.add(room)
        await db_session.commit()
        await db_session.refresh(room)
        return room
    
    @pytest.fixture
    async def create_test_booking(self, db_session, create_test_user, create_test_room):
        # Создаем тестовое бронирование
        booking_date = date.today()
        check_in = booking_date + timedelta(days=1)
        check_out = booking_date + timedelta(days=3)
        
        booking = Booking(
            user_id=create_test_user.id,
            room_id=create_test_room.id,
            check_in_date=check_in,
            check_out_date=check_out,
            total_price=200,
            status="confirmed"
        )
        db_session.add(booking)
        await db_session.commit()
        await db_session.refresh(booking)
        return booking
    
    @pytest.mark.asyncio
    async def test_create_booking(self, create_test_user, create_test_room):
        # Тест создания бронирования
        booking_date = date.today()
        check_in = booking_date + timedelta(days=1)
        check_out = booking_date + timedelta(days=3)
        
        response = client.post(
            "/api/v1/bookings/",
            json={
                "room_id": create_test_room.id,
                "check_in_date": check_in.isoformat(),
                "check_out_date": check_out.isoformat(),
                "special_requests": "Early check-in"
            },
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["room_id"] == create_test_room.id
        assert data["user_id"] == create_test_user.id
        assert data["total_price"] == 200
        assert data["status"] == "confirmed"
    
    @pytest.mark.asyncio
    async def test_create_booking_room_not_found(self):
        # Тест создания бронирования с несуществующей комнатой
        booking_date = date.today()
        check_in = booking_date + timedelta(days=1)
        check_out = booking_date + timedelta(days=3)
        
        response = client.post(
            "/api/v1/bookings/",
            json={
                "room_id": 999,
                "check_in_date": check_in.isoformat(),
                "check_out_date": check_out.isoformat()
            },
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Room not found"
    
    @pytest.mark.asyncio
    async def test_create_booking_room_not_available(self, create_test_user, create_test_room, db_session):
        # Тест создания бронирования для недоступной комнаты
        create_test_room.is_available = False
        await db_session.commit()
        
        booking_date = date.today()
        check_in = booking_date + timedelta(days=1)
        check_out = booking_date + timedelta(days=3)
        
        response = client.post(
            "/api/v1/bookings/",
            json={
                "room_id": create_test_room.id,
                "check_in_date": check_in.isoformat(),
                "check_out_date": check_out.isoformat()
            },
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Room is not available"
    
    @pytest.mark.asyncio
    async def test_create_booking_room_conflict(self, create_test_user, create_test_room, create_test_booking):
        # Тест создания бронирования с конфликтом по датам
        booking_date = date.today()
        check_in = create_test_booking.check_in_date + timedelta(days=1)  # Пересечение дат
        check_out = create_test_booking.check_out_date + timedelta(days=1)
        
        response = client.post(
            "/api/v1/bookings/",
            json={
                "room_id": create_test_room.id,
                "check_in_date": check_in.isoformat(),
                "check_out_date": check_out.isoformat()
            },
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Room is already booked for these dates"
    
    @pytest.mark.asyncio
    async def test_get_booking(self, create_test_booking):
        # Тест получения бронирования по ID
        response = client.get(
            f"/api/v1/bookings/{create_test_booking.id}",
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == create_test_booking.id
        assert data["user_id"] == create_test_booking.user_id
        assert data["room_id"] == create_test_booking.room_id
    
    @pytest.mark.asyncio
    async def test_get_booking_not_found(self):
        # Тест получения несуществующего бронирования
        response = client.get(
            "/api/v1/bookings/999",
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Booking not found"
    
    @pytest.mark.asyncio
    async def test_get_user_bookings(self, create_test_user, create_test_booking):
        # Тест получения бронирований пользователя
        response = client.get(
            "/api/v1/bookings/user/",
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == create_test_booking.id
    
    @pytest.mark.asyncio
    async def test_update_booking(self, create_test_booking):
        # Тест обновления бронирования
        response = client.put(
            f"/api/v1/bookings/{create_test_booking.id}",
            json={"special_requests": "Late check-out"},
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["special_requests"] == "Late check-out"
    
    @pytest.mark.asyncio
    async def test_update_booking_not_found(self):
        # Тест обновления несуществующего бронирования
        response = client.put(
            "/api/v1/bookings/999",
            json={"special_requests": "Late check-out"},
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Booking not found"
    
    @pytest.mark.asyncio
    async def test_cancel_booking(self, create_test_booking):
        # Тест отмены бронирования
        response = client.post(
            f"/api/v1/bookings/{create_test_booking.id}/cancel",
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
    
    @pytest.mark.asyncio
    async def test_cancel_booking_already_cancelled(self, create_test_booking, db_session):
        # Тест отмены уже отмененного бронирования
        create_test_booking.status = "cancelled"
        await db_session.commit()
        
        response = client.post(
            f"/api/v1/bookings/{create_test_booking.id}/cancel",
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Booking is already cancelled"