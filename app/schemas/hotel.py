from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class HotelBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    country: str = Field(..., min_length=1)
    description: Optional[str] = None
    rating: float = Field(0.0, ge=0.0, le=5.0)

class HotelCreate(HotelBase):
    pass

class HotelUpdate(BaseModel):
    """Схема для частичного обновления отеля"""
    model_config = ConfigDict(from_attributes=True)
    
    name: Optional[str] = Field(None, min_length=1)
    address: Optional[str] = Field(None, min_length=1)
    city: Optional[str] = Field(None, min_length=1)
    country: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)

class HotelInDBBase(HotelBase):
    id: int
    created_at: datetime
    updated_at: datetime

class Hotel(HotelInDBBase):
    pass