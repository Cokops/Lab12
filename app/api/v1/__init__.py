from .admin import router as admin_router
from .auth import router as auth_router
from .bookings import router as bookings_router
from .hotels import router as hotels_router
from .payments import router as payments_router
from .reviews import router as reviews_router
from .rooms import router as rooms_router
from .users import router as users_router

__all__ = [
    "admin_router",
    "auth_router",
    "bookings_router",
    "hotels_router",
    "payments_router",
    "reviews_router",
    "rooms_router",
    "users_router"
]