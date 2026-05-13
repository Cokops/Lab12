from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import Room, Hotel, Booking
from app.schemas import RoomCreate, RoomUpdate, Room
from fastapi import HTTPException, status

async def get_room(db: AsyncSession, room_id: int) -> Room:
    result = await db.execute(
        select(Room)
        .where(Room.id == room_id)
        .options(selectinload(Room.hotel))
    )
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return Room.model_validate(room)

async def get_rooms_by_hotel(db: AsyncSession, hotel_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Room)
        .where(Room.hotel_id == hotel_id)
        .offset(skip)
        .limit(limit)
    )
    rooms = result.scalars().all()
    return [Room.model_validate(room) for room in rooms]

async def create_room(db: AsyncSession, room_in: RoomCreate):
    # Проверка существования отеля
    result = await db.execute(select(Hotel).where(Hotel.id == room_in.hotel_id))
    hotel = result.scalar_one_or_none()
    if not hotel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    
    db_room = Room(**room_in.model_dump())
    db.add(db_room)
    await db.commit()
    await db.refresh(db_room)
    return Room.model_validate(db_room)

async def update_room(db: AsyncSession, room_id: int, room_in: RoomUpdate):
    result = await db.execute(select(Room).where(Room.id == room_id))
    db_room = result.scalar_one_or_none()
    if not db_room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    
    update_data = room_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_room, key, value)
    
    await db.commit()
    await db.refresh(db_room)
    return Room.model_validate(db_room)

async def delete_room(db: AsyncSession, room_id: int):
    result = await db.execute(select(Room).where(Room.id == room_id))
    db_room = result.scalar_one_or_none()
    if not db_room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    await db.delete(db_room)
    await db.commit()
    return True