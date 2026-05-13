from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import Room, RoomCreate, RoomUpdate
from app.services.room_service import get_room, get_rooms_by_hotel, create_room, update_room, delete_room

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.get("", response_model=list[Room])
async def read_rooms(
    hotel_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Получить список номеров (всех или по отелю)"""
    if hotel_id:
        return await get_rooms_by_hotel(db, hotel_id, skip=skip, limit=limit)
    result = await db.execute(
        select(Room)
        .offset(skip)
        .limit(limit)
        .options(selectinload(Room.hotel))
    )
    rooms = result.scalars().all()
    return [Room.model_validate(room) for room in rooms]

@router.get("/{room_id}", response_model=Room)
async def read_room(room_id: int, db: AsyncSession = Depends(get_db)):
    """Получить номер по ID"""
    return await get_room(db, room_id)

@router.post("", response_model=Room, status_code=status.HTTP_201_CREATED)
async def create_room_endpoint(
    room_in: RoomCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать новый номер"""
    return await create_room(db, room_in)

@router.put("/{room_id}", response_model=Room)
async def update_room_endpoint(
    room_id: int,
    room_in: RoomUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить номер"""
    return await update_room(db, room_id, room_in)

@router.delete("/{room_id}", response_model=bool)
async def delete_room_endpoint(room_id: int, db: AsyncSession = Depends(get_db)):
    """Удалить номер"""
    return await delete_room(db, room_id)