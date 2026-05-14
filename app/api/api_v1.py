from fastapi import APIRouter

from app.api.v1 import (
    admin_router,
    auth_router,
    bookings_router,
    hotels_router,
    payments_router,
    reviews_router,
    rooms_router,
    users_router
)

api_router = APIRouter()

# Подключаем роутеры
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(hotels_router, prefix="/hotels", tags=["hotels"])
api_router.include_router(rooms_router, prefix="/rooms", tags=["rooms"])
api_router.include_router(bookings_router, prefix="/bookings", tags=["bookings"])
api_router.include_router(reviews_router, prefix="/reviews", tags=["reviews"])
api_router.include_router(payments_router, prefix="/payments", tags=["payments"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])