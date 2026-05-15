import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.hotel import Hotel as HotelModel
from app.models.user import User
from app.schemas.hotel import HotelCreate, HotelUpdate
from app.schemas.user import UserCreate, UserUpdate
from app.services import hotel_service, user_service
from fastapi import HTTPException
from datetime import datetime


class TestHotelService:
    """Unit-тесты для hotel_service с реальными assert-ами."""

    @pytest.mark.asyncio
    async def test_get_hotel_success(self):
        mock_hotel = MagicMock(spec=HotelModel)
        mock_hotel.id = 1
        mock_hotel.name = "Test Hotel"
        mock_hotel.address = "Test Address"
        mock_hotel.city = "Test City"
        mock_hotel.country = "Test Country"
        mock_hotel.description = None
        mock_hotel.rating = 0.0
        mock_hotel.created_at = datetime(2023, 1, 1)
        mock_hotel.updated_at = datetime(2023, 1, 1)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_hotel)

        mock_db = MagicMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await hotel_service.get_hotel(mock_db, 1)

        assert result is not None
        assert result.id == 1
        assert result.name == "Test Hotel"
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_hotel_not_found(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)

        mock_db = MagicMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(HTTPException) as exc_info:
            await hotel_service.get_hotel(mock_db, 999)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Hotel not found"

    @pytest.mark.asyncio
    async def test_create_hotel_success(self):
        hotel_in = HotelCreate(
            name="New Hotel", address="New St", city="New City", country="New Country"
        )

        mock_db_hotel = MagicMock(spec=HotelModel)
        mock_db_hotel.id = 1
        mock_db_hotel.name = hotel_in.name
        mock_db_hotel.rating = 0.0

        mock_db = MagicMock(spec=AsyncSession)
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, 'id', 1))

        with patch('app.models.hotel.Hotel', return_value=mock_db_hotel):
            result = await hotel_service.create_hotel(mock_db, hotel_in)

        assert result is not None
        assert result.name == "New Hotel"
        assert result.id == 1
        mock_db.add.assert_called_once_with(mock_db_hotel)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_db_hotel)

    @pytest.mark.asyncio
    async def test_update_hotel_success(self):
        mock_db_hotel = MagicMock(spec=HotelModel)
        mock_db_hotel.id = 1
        mock_db_hotel.name = "Old Name"
        mock_db_hotel.address = "Old Address"
        mock_db_hotel.rating = 3.0

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_db_hotel)

        mock_db = MagicMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        update_in = HotelUpdate(name="Updated Name")

        result = await hotel_service.update_hotel(mock_db, 1, update_in)

        assert result is not None
        assert result.name == "Updated Name"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_hotel_not_found(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)

        mock_db = MagicMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)

        update_in = HotelUpdate(name="Try Update")

        with pytest.raises(HTTPException) as exc_info:
            await hotel_service.update_hotel(mock_db, 999, update_in)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Hotel not found"

    @pytest.mark.asyncio
    async def test_delete_hotel_success(self):
        mock_db_hotel = MagicMock(spec=HotelModel)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_db_hotel)

        mock_db = MagicMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()

        result = await hotel_service.delete_hotel(mock_db, 1)

        assert result is True
        mock_db.delete.assert_called_once_with(mock_db_hotel)
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_hotel_not_found(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)

        mock_db = MagicMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(HTTPException) as exc_info:
            await hotel_service.delete_hotel(mock_db, 999)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Hotel not found"


class TestUserService:
    """Unit-тесты для user_service с реальными assert-ами."""

    @pytest.mark.asyncio
    async def test_create_user_email_exists(self):
        mock_existing_user = MagicMock(spec=User)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_existing_user)

        mock_db = MagicMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)

        user_in = UserCreate(
            email="existing@example.com", password="password", full_name="User"
        )

        with pytest.raises(HTTPException) as exc_info:
            await user_service.create_user(mock_db, user_in)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Email already registered"
        mock_db.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_user_change_password(self):
        mock_db_user = MagicMock(spec=User)
        mock_db_user.id = 1

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_db_user)

        mock_db = MagicMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        update_in = UserUpdate(
            email="user@example.com", password="new_password", full_name="Updated Name"
        )

        with patch('app.services.user_service.get_password_hash', return_value="hashed_new_password") as mock_hash:
            result = await user_service.update_user(mock_db, 1, update_in)

        assert result is not None
        mock_hash.assert_called_once_with("new_password")
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()