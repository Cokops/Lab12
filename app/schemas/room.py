from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class RoomBase(BaseModel):
    hotel_id: int
    room_number: str = Field(..., min_length=1)
    room_type: str = Field(..., min_length=1)
    price_per_night: float = Field(..., gt=0)
    description: Optional[str] = None
    max_occupancy: int = Field(..., gt=0)
    is_available: bool = True

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    room_number: Optional[str] = None
    room_type: Optional[str] = None
    price_per_night: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    max_occupancy: Optional[int] = Field(None, gt=0)
    is_available: Optional[bool] = None

class RoomInDBBase(RoomBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Room(RoomInDBBase):
    pass