from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.hotel import Hotel  # Импорт из models, не из schemas!
from app.schemas.hotel import HotelCreate, HotelUpdate


async def get_hotel(db: AsyncSession, hotel_id: int):
    result = await db.execute(select(Hotel).where(Hotel.id == hotel_id))
    hotel = result.scalar_one_or_none()
    if hotel is None:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel


async def create_hotel(db: AsyncSession, hotel_in: HotelCreate):
    hotel_data = hotel_in.model_dump()
    db_hotel = Hotel(**hotel_data)
    db.add(db_hotel)
    await db.commit()
    await db.refresh(db_hotel)
    return db_hotel


async def update_hotel(db: AsyncSession, hotel_id: int, hotel_in: HotelUpdate):
    result = await db.execute(select(Hotel).where(Hotel.id == hotel_id))
    db_hotel = result.scalar_one_or_none()
    if db_hotel is None:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    update_data = hotel_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_hotel, key, value)
    
    await db.commit()
    await db.refresh(db_hotel)
    return db_hotel


async def delete_hotel(db: AsyncSession, hotel_id: int):
    result = await db.execute(select(Hotel).where(Hotel.id == hotel_id))
    db_hotel = result.scalar_one_or_none()
    if db_hotel is None:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    await db.delete(db_hotel)
    await db.commit()
    return True