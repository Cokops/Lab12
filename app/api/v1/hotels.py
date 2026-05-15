from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.hotel import Hotel, HotelCreate, HotelUpdate
from app.services.hotel_service import get_hotel, get_hotels, create_hotel, update_hotel, delete_hotel

router = APIRouter(prefix="/hotels", tags=["hotels"])

@router.get("", response_model=list[Hotel])
async def read_hotels(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Получить список отелей"""
    return await get_hotels(db, skip=skip, limit=limit)

@router.get("/{hotel_id}", response_model=Hotel)
async def read_hotel(hotel_id: int, db: AsyncSession = Depends(get_db)):
    """Получить отель по ID"""
    return await get_hotel(db, hotel_id)

@router.post("", response_model=Hotel, status_code=status.HTTP_201_CREATED)
async def create_hotel_endpoint(
    hotel_in: HotelCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать новый отель"""
    return await create_hotel(db, hotel_in)

@router.put("/{hotel_id}", response_model=Hotel)
async def update_hotel_endpoint(
    hotel_id: int,
    hotel_in: HotelUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить отель"""
    return await update_hotel(db, hotel_id, hotel_in)

@router.delete("/{hotel_id}", response_model=bool)
async def delete_hotel_endpoint(hotel_id: int, db: AsyncSession = Depends(get_db)):
    """Удалить отель"""
    return await delete_hotel(db, hotel_id)