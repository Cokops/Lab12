import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.hotel import Hotel as HotelModel
from app.models.user import User
from app.schemas import HotelCreate, HotelUpdate, UserCreate, UserUpdate
from app.services import hotel_service, user_service
from fastapi import HTTPException


class TestHotelService:
    """
    Unit-тесты для функций сервиса hotel_service.
    Эти тесты мокируют сессию БД и тестируют бизнес-логику напрямую.
    """

    @pytest.mark.asyncio
    async def test_get_hotel_success(self):
        """
        Проверяет успешное получение отеля.
        """
        # Мокируем объект отеля
        mock_hotel = AsyncMock(spec=HotelModel)
        mock_hotel.id = 1
        mock_hotel.name = "Test Hotel"
        # Мокируем результат запроса
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_hotel
        # Мокируем сессию БД
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = mock_result
        
        # Вызываем тестируемую функцию
        result = await hotel_service.get_hotel(mock_db, 1)
        
        # Проверяем результат
        assert result.id == mock_hotel.id
        assert result.name == mock_hotel.name
        # Проверяем, что execute был вызван с правильным запросом
        mock_db.execute.assert_called_once()
        assert mock_hotel.id == 1

    @pytest.mark.asyncio
    async def test_get_hotel_not_found(self):
        """
        Проверяет, что get_hotel вызывает HTTPException при отсутствии отеля.
        """
        # Мокируем результат запроса, возвращающий None
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        # Мокируем сессию БД
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = mock_result
        
        # Проверяем, что вызывается исключение
        with pytest.raises(HTTPException) as exc_info:
            await hotel_service.get_hotel(mock_db, 999)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Hotel not found"

    @pytest.mark.asyncio
    async def test_create_hotel_success(self):
        """
        Проверяет успешное создание отеля.
        """
        # Создаем входные данные
        hotel_in = HotelCreate(name="New Hotel", address="New St", city="New City", country="New Country")
        # Мокируем новый объект отеля
        mock_db_hotel = MagicMock(spec=HotelModel, **{
            "id": 1,
            "name": hotel_in.name,
            "rating": 0.0
        })
        # Мокируем сессию
        mock_db = AsyncMock(spec=AsyncSession)
        # Мокируем результат db.refresh
        mock_db.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, 'id', 1))
        
        # Мокируем Hotel так, чтобы он возвращал mock_db_hotel при создании
        with patch('app.models.hotel.Hotel', return_value=mock_db_hotel): # Мокируем модель из app.models
            # Вызываем функцию
            result = await hotel_service.create_hotel(mock_db, hotel_in)
        
        # Проверяем результат
        assert result.name == hotel_in.name
        assert result.id == 1 # ID устанавливается БД
        # Проверяем вызовы методов сессии
        mock_db.add.assert_called_once_with(mock_db_hotel)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_db_hotel)

    @pytest.mark.asyncio
    async def test_update_hotel_success(self):
        """
        Проверяет успешное обновление отеля, включая обновление частичных данных (exclude_unset).
        """
        # Мокируем существующий отель в БД
        mock_db_hotel = MagicMock(spec=HotelModel)
        mock_db_hotel.id = 1
        mock_db_hotel.name = "Old Name"
        mock_db_hotel.address = "Old Address"
        mock_db_hotel.rating = 3.0
        # Мокируем результат запроса
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_db_hotel
        # Мокируем сессию
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = mock_result
        # Мокируем commit и refresh
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Создаем данные для обновления (только имя)
        update_in = HotelUpdate(name="Updated Name")
        
        # Вызываем функцию
        result = await hotel_service.update_hotel(mock_db, 1, update_in)
        
        # Проверяем, что имя изменилось, а другие поля остались прежними
        assert result.name == "Updated Name"
        assert result.address == "Old Address" # Не должно измениться
        assert result.rating == 3.0 # Не должно измениться
        # Проверяем, что атрибуты были установлены
        mock_db_hotel.__setattr__.assert_called_with('name', 'Updated Name')
        # Проверяем вызовы
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_hotel_not_found(self):
        """
        Проверяет, что update_hotel вызывает HTTPException, если отель не найден.
        """
        # Мокируем результат запроса, возвращающий None
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        # Мокируем сессию
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = mock_result
        
        # Данные для обновления
        update_in = HotelUpdate(name="Try Update")
        
        # Проверяем исключение
        with pytest.raises(HTTPException) as exc_info:
            await hotel_service.update_hotel(mock_db, 999, update_in)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Hotel not found"

    @pytest.mark.asyncio
    async def test_delete_hotel_success(self):
        """
        Проверяет успешное удаление отеля.
        """
        # Мокируем существующий отель
        mock_db_hotel = MagicMock(spec=HotelModel)
        # Мокируем результат запроса
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_db_hotel
        # Мокируем сессию
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = mock_result
        # Мокируем delete и commit
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()
        
        # Вызываем функцию
        result = await hotel_service.delete_hotel(mock_db, 1)
        
        # Проверяем результат
        assert result is True
        # Проверяем, что delete и commit были вызваны
        mock_db.delete.assert_called_once_with(mock_db_hotel)
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_hotel_not_found(self):
        """
        Проверяет, что delete_hotel вызывает HTTPException, если отель не найден.
        """
        # Мокируем результат запроса, возвращающий None
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        # Мокируем сессию
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = mock_result
        
        # Проверяем исключение
        with pytest.raises(HTTPException) as exc_info:
            await hotel_service.delete_hotel(mock_db, 999)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Hotel not found"


class TestUserService:
    """
    Unit-тесты для функций сервиса user_service.
    Покрывают создание, проверку email и обновление пользователя.
    """

    @pytest.mark.asyncio
    async def test_create_user_email_exists(self):
        """
        Проверяет, что create_user вызывает HTTPException при попытке регистрации с существующим email.
        """
        # Мокируем существующего пользователя
        mock_existing_user = AsyncMock(spec=User)
        # Мокируем результат запроса
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_existing_user
        # Мокируем сессию
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = mock_result
        
        # Входные данные
        user_in = UserCreate(email="existing@example.com", password="password", full_name="User")
        
        # Проверяем исключение
        with pytest.raises(HTTPException) as exc_info:
            await user_service.create_user(mock_db, user_in)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Email already registered"
        # Проверяем, что хеширование пароля и добавление в сессию не происходили
        mock_db.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_user_change_password(self):
        """
        Проверяет, что при обновлении пользователя с новым паролем, старый пароль хешируется.
        """
        # Мокируем существующего пользователя
        mock_db_user = AsyncMock(spec=User)
        mock_db_user.id = 1
        # Мокируем результат запроса
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_db_user
        # Мокируем сессию
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = mock_result
        # Мокируем commit и refresh
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        # Мокируем хеширование пароля
        with patch('app.services.user_service.get_password_hash', return_value="hashed_new_password") as mock_hash:
            # Создаем данные для обновления с паролем
            update_in = UserUpdate(email="user@example.com", password="new_password", full_name="Updated Name")
            
            # Вызываем функцию
            result = await user_service.update_user(mock_db, 1, update_in)
            
            # Проверяем, что был вызван get_password_hash
            mock_hash.assert_called_once_with("new_password")
            # Проверяем, что в БД установился хешированный пароль, а не исходный
            mock_db_user.__setattr__.assert_any_call("hashed_password", "hashed_new_password")
            mock_db_user.__setattr__.assert_any_call("full_name", "Updated Name")
            # Проверяем, что полное имя изменилось
            mock_db_user.__setattr__.assert_any_call("full_name", "Updated Name")

        # Проверяем результат
        assert result.full_name == "Updated Name"