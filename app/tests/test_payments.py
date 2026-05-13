from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine
from app.models import Base, User, Booking, Payment
from app.schemas import PaymentCreate
from app.core.security import get_password_hash
from datetime import datetime, date
import pytest
import asyncio

client = TestClient(app)

class TestPaymentAPI:
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
    async def create_test_booking(self, db_session, create_test_user):
        # Создаем тестовое бронирование
        booking = Booking(
            user_id=create_test_user.id,
            room_id=1,
            check_in_date=date.today(),
            check_out_date=date.today() + timedelta(days=2),
            total_price=200,
            status="confirmed"
        )
        db_session.add(booking)
        await db_session.commit()
        await db_session.refresh(booking)
        return booking
    
    @pytest.fixture
    async def create_test_payment(self, db_session, create_test_booking):
        # Создаем тестовый платеж
        payment = Payment(
            booking_id=create_test_booking.id,
            amount=create_test_booking.total_price,
            payment_method="card",
            status="completed"
        )
        db_session.add(payment)
        await db_session.commit()
        await db_session.refresh(payment)
        return payment
    
    @pytest.mark.asyncio
    async def test_create_payment(self, create_test_booking):
        # Тест создания платежа
        response = client.post(
            "/api/v1/payments/",
            json={
                "booking_id": create_test_booking.id,
                "amount": 200.0,
                "payment_method": "card",
                "status": "completed"
            },
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["booking_id"] == create_test_booking.id
        assert data["amount"] == 200.0
        assert data["payment_method"] == "card"
        assert data["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_create_payment_booking_not_found(self):
        # Тест создания платежа для несуществующего бронирования
        response = client.post(
            "/api/v1/payments/",
            json={
                "booking_id": 999,
                "amount": 200.0,
                "payment_method": "card",
                "status": "completed"
            },
            headers={"Authorization": f"Bearer test_token"}
}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Booking not found"
    
    @pytest.mark.asyncio
    async def test_create_payment_for_other_user_booking(self, db_session):
        # Тест создания платежа для бронирования другого пользователя
        # Создаем другого пользователя
        other_user = User(
            email="other@example.com",
            hashed_password=get_password_hash("password"),
            full_name="Other User",
            role="user"
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)
        
        # Создаем бронирование для другого пользователя
        other_booking = Booking(
            user_id=other_user.id,
            room_id=1,
            check_in_date=date.today(),
            check_out_date=date.today() + timedelta(days=2),
            total_price=200,
            status="confirmed"
        )
        db_session.add(other_booking)
        await db_session.commit()
        await db_session.refresh(other_booking)
        
        # Пытаемся создать платеж для чужого бронирования
        response = client.post(
            "/api/v1/payments/",
            json={
                "booking_id": other_booking.id,
                "amount": 200.0,
                "payment_method": "card",
                "status": "completed"
            },
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 403
        assert response.json()["detail"] == "Not enough permissions"
    
    @pytest.mark.asyncio
    async def test_get_payment(self, create_test_payment):
        # Тест получения платежа по ID
        response = client.get(
            f"/api/v1/payments/{create_test_payment.id}",
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == create_test_payment.id
        assert data["booking_id"] == create_test_payment.booking_id
    
    @pytest.mark.asyncio
    async def test_get_payment_not_found(self):
        # Тест получения несуществующего платежа
        response = client.get(
            "/api/v1/payments/999",
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Payment not found"
    
    @pytest.mark.asyncio
    async def test_get_payments_by_booking(self, create_test_booking, create_test_payment):
        # Тест получения платежей по бронированию
        response = client.get(
            f"/api/v1/payments/booking/{create_test_booking.id}",
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == create_test_payment.id
    
    @pytest.mark.asyncio
    async def test_get_payments_by_booking_no_payments(self, create_test_booking):
        # Тест получения платежей по бронированию без платежей
        response = client.get(
            f"/api/v1/payments/booking/{create_test_booking.id}",
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    @pytest.mark.asyncio
    async def test_update_payment(self, create_test_payment):
        # Тест обновления платежа
        response = client.put(
            f"/api/v1/payments/{create_test_payment.id}",
            json={"status": "refunded"},
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "refunded"
    
    @pytest.mark.asyncio
    async def test_update_payment_not_found(self):
        # Тест обновления несуществующего платежа
        response = client.put(
            "/api/v1/payments/999",
            json={"status": "refunded"},
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Payment not found"
    
    @pytest.mark.asyncio
    async def test_delete_payment(self, create_test_payment):
        # Тест удаления платежа
        response = client.delete(
            f"/api/v1/payments/{create_test_payment.id}",
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 200
        assert response.json() is True
    
    @pytest.mark.asyncio
    async def test_delete_payment_not_found(self):
        # Тест удаления несуществующего платежа
        response = client.delete(
            "/api/v1/payments/999",
            headers={"Authorization": f"Bearer test_token"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Payment not found"