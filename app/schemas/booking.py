from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Optional
from enum import Enum

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"

class BookingBase(BaseModel):
    user_id: int
    room_id: int
    check_in_date: datetime = Field(..., gt=datetime.utcnow())
    check_out_date: datetime
    total_price: float = Field(..., gt=0)
    status: BookingStatus = BookingStatus.PENDING
    special_requests: Optional[str] = None

    @model_validator(mode='after')
    def validate_dates(self):
        if self.check_out_date <= self.check_in_date:
            raise ValueError('Check-out date must be after check-in date')
        return self

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None
    total_price: Optional[float] = Field(None, gt=0)
    status: Optional[BookingStatus] = None
    special_requests: Optional[str] = None

class BookingInDBBase(BookingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Booking(BookingInDBBase):
    pass