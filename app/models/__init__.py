from .user import User
from .hotel import Hotel
from .room import Room
from .booking import Booking
from .review import Review
from .payment import Payment

from ..database import Base  # Импортируем Base из database для моделей

# Теперь Base доступен для импорта из app.models
__all__ = ["User", "Hotel", "Room", "Booking", "Review", "Payment", "Base"]