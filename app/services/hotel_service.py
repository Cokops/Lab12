from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import Hotel, Room, Review
from app.schemas import HotelCreate, HotelUpdate, Hotel
from fastapi import HTTPException, status

async def get_hotel(db: AsyncSession, hotel_id: int) -> Hotel:
    result = await db.execute(
        select(Hotel)
        .where(Hotel.id == hotel_id)
        .options(selectinload(Hotel.rooms), selectinload(Hotel.reviews))
    )
    hotel = result.scalar_one_or_none()
    if not hotel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    return Hotel.model_validate(hotel)

async def get_hotels(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Hotel)
        .offset(skip)
        .limit(limit)
    )
    hotels = result.scalars().all()
    return [Hotel.model_validate(hotel) for hotel in hotels]

async def create_hotel(db: AsyncSession, hotel_in: HotelCreate):
    db_hotel = Hotel(**hotel_in.model_dump())
    db.add(db_hotel)
    await db.commit()
    await db.refresh(db_hotel)
    return Hotel.model_validate(db_hotel)

async def update_hotel(db: AsyncSession, hotel_id: int, hotel_in: HotelUpdate):
    result = await db.execute(select(Hotel).where(Hotel.id == hotel_id))
    db_hotel = result.scalar_one_or_none()
    if not db_hotel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    
    update_data = hotel_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_hotel, key, value)
    
    await db.commit()
    await db.refresh(db_hotel)
    return Hotel.model_validate(db_hotel)

async def delete_hotel(db: AsyncSession, hotel_id: int):
    result = await db.execute(select(Hotel).where(Hotel.id == hotel_id))
    db_hotel = result.scalar_one_or_none()
    if not db_hotel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    await db.delete(db_hotel)
    await db.commit()
    return True