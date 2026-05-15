from fastapi import APIRouter
from app.api.v1 import (
    auth,
    hotels,
    rooms,
    bookings,
    reviews,
    payments,
    admin,
    users
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(hotels.router, prefix="/hotels", tags=["hotels"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])