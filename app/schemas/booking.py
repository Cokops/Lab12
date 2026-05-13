from pydantic import BaseModel, Field
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

    class Config:
        @staticmethod
        def validate_dates(booking: 'BookingBase'):
            if booking.check_out_date <= booking.check_in_date:
                raise ValueError('Check-out date must be after check-in date')
            return booking

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