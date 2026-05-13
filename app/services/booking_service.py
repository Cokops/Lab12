from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import Booking, Room, User
from app.schemas import BookingCreate, BookingUpdate, Booking
from datetime import datetime
from fastapi import HTTPException, status

async def get_booking(db: AsyncSession, booking_id: int) -> Booking:
    result = await db.execute(
        select(Booking)
        .where(Booking.id == booking_id)
        .options(selectinload(Booking.room), selectinload(Booking.user))
    )
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return Booking.model_validate(booking)

async def get_user_bookings(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Booking)
        .where(Booking.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .options(selectinload(Booking.room).selectinload(Room.hotel))
    )
    bookings = result.scalars().all()
    return [Booking.model_validate(booking) for booking in bookings]

async def create_booking(db: AsyncSession, booking_in: BookingCreate, current_user: User):
    # Проверка, что комната существует и доступна
    result = await db.execute(select(Room).where(Room.id == booking_in.room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    
    if not room.is_available:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room is not available")
    
    # Проверка доступности номера на указанные даты
    conflicting_booking = await db.execute(
        select(Booking)
        .where(
            Booking.room_id == booking_in.room_id,
            Booking.status != "cancelled",
            Booking.check_in_date < booking_in.check_out_date,
            Booking.check_out_date > booking_in.check_in_date
        )
    )
    if conflicting_booking.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room is already booked for these dates")
    
    # Расчет общей стоимости
    nights = (booking_in.check_out_date - booking_in.check_in_date).days
    total_price = nights * room.price_per_night
    
    db_booking = Booking(
        user_id=current_user.id,
        room_id=booking_in.room_id,
        check_in_date=booking_in.check_in_date,
        check_out_date=booking_in.check_out_date,
        total_price=total_price,
        special_requests=booking_in.special_requests
    )
    
    db.add(db_booking)
    await db.commit()
    await db.refresh(db_booking)
    return Booking.model_validate(db_booking)

async def update_booking(db: AsyncSession, booking_id: int, booking_in: BookingUpdate):
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    db_booking = result.scalar_one_or_none()
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    update_data = booking_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_booking, key, value)
    
    await db.commit()
    await db.refresh(db_booking)
    return Booking.model_validate(db_booking)

async def cancel_booking(db: AsyncSession, booking_id: int):
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    db_booking = result.scalar_one_or_none()
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    if db_booking.status == "cancelled":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking is already cancelled")
    
    db_booking.status = "cancelled"
    await db.commit()
    await db.refresh(db_booking)
    return Booking.model_validate(db_booking)