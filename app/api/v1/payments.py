from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import Payment, PaymentCreate, PaymentUpdate
from app.services.payment_service import get_payment, get_payments_by_booking, create_payment, update_payment, delete_payment
from app.core.security import get_current_active_user
from app.models import User

router = APIRouter(prefix="/payments", tags=["payments"])

@router.get("", response_model=list[Payment])
async def read_payments(
    booking_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Получить платежи (по бронированию или все)"""
    if booking_id:
        return await get_payments_by_booking(db, booking_id, skip=skip, limit=limit)
    result = await db.execute(
        select(Payment)
        .offset(skip)
        .limit(limit)
        .options(selectinload(Payment.booking))
    )
    payments = result.scalars().all()
    return [Payment.model_validate(payment) for payment in payments]

@router.get("/{payment_id}", response_model=Payment)
async def read_payment(payment_id: int, db: AsyncSession = Depends(get_db)):
    """Получить платеж по ID"""
    return await get_payment(db, payment_id)

@router.post("", response_model=Payment, status_code=status.HTTP_201_CREATED)
async def create_payment_endpoint(
    payment_in: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создать новый платеж"""
    return await create_payment(db, payment_in, current_user)

@router.put("/{payment_id}", response_model=Payment)
async def update_payment_endpoint(
    payment_id: int,
    payment_in: PaymentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновить платеж"""
    payment = await get_payment(db, payment_id)
    if payment.booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await update_payment(db, payment_id, payment_in)

@router.delete("/{payment_id}", response_model=bool)
async def delete_payment_endpoint(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Удалить платеж"""
    payment = await get_payment(db, payment_id)
    if payment.booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await delete_payment(db, payment_id)