from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import Booking, BookingCreate, BookingUpdate
from app.services.booking_service import get_booking, get_user_bookings, create_booking, update_booking, cancel_booking
from app.core.security import get_current_active_user
from app.models import User

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.get("", response_model=list[Booking])
async def read_user_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """Получить все бронирования текущего пользователя"""
    return await get_user_bookings(db, current_user.id, skip=skip, limit=limit)

@router.get("/{booking_id}", response_model=Booking)
async def read_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить бронирование по ID"""
    booking = await get_booking(db, booking_id)
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return booking

@router.post("", response_model=Booking, status_code=status.HTTP_201_CREATED)
async def create_booking_endpoint(
    booking_in: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создать новое бронирование"""
    return await create_booking(db, booking_in, current_user)

@router.put("/{booking_id}", response_model=Booking)
async def update_booking_endpoint(
    booking_id: int,
    booking_in: BookingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновить бронирование"""
    booking = await get_booking(db, booking_id)
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await update_booking(db, booking_id, booking_in)

@router.delete("/{booking_id}", response_model=Booking)
async def cancel_booking_endpoint(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Отменить бронирование"""
    booking = await get_booking(db, booking_id)
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await cancel_booking(db, booking_id)