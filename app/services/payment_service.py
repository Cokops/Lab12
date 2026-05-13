from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Payment, Booking
from app.schemas import PaymentCreate, PaymentUpdate, Payment
from fastapi import HTTPException, status

async def get_payment(db: AsyncSession, payment_id: int) -> Payment:
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return Payment.model_validate(payment)

async def get_payments_by_booking(db: AsyncSession, booking_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Payment)
        .where(Payment.booking_id == booking_id)
        .offset(skip)
        .limit(limit)
    )
    payments = result.scalars().all()
    return [Payment.model_validate(payment) for payment in payments]

async def create_payment(db: AsyncSession, payment_in: PaymentCreate, current_user: User):
    # Проверка, что бронирование существует и принадлежит пользователю
    result = await db.execute(select(Booking).where(Booking.id == payment_in.booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    db_payment = Payment(
        booking_id=payment_in.booking_id,
        amount=payment_in.amount,
        payment_method=payment_in.payment_method,
        status=payment_in.status
    )
    
    db.add(db_payment)
    await db.commit()
    await db.refresh(db_payment)
    return Payment.model_validate(db_payment)

async def update_payment(db: AsyncSession, payment_id: int, payment_in: PaymentUpdate):
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    db_payment = result.scalar_one_or_none()
    if not db_payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    
    update_data = payment_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_payment, key, value)
    
    await db.commit()
    await db.refresh(db_payment)
    return Payment.model_validate(db_payment)

async def delete_payment(db: AsyncSession, payment_id: int):
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    db_payment = result.scalar_one_or_none()
    if not db_payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    await db.delete(db_payment)
    await db.commit()
    return True