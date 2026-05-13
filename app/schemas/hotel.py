from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class HotelBase(BaseModel):
    name: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    country: str = Field(..., min_length=1)
    description: Optional[str] = None
    rating: float = Field(0.0, ge=0.0, le=5.0)

class HotelCreate(HotelBase):
    pass

class HotelUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)

class HotelInDBBase(HotelBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Hotel(HotelInDBBase):
    pass