from pydantic import BaseModel, Field, ConfigDict, model_validator
from datetime import datetime, timezone
from typing import Optional
from enum import Enum

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"

class BookingBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    user_id: int
    room_id: int
    check_in_date: datetime = Field(..., description="Дата заезда")
    check_out_date: datetime = Field(..., description="Дата выезда")
    total_price: float = Field(..., gt=0, description="Общая стоимость")
    status: BookingStatus = Field(BookingStatus.PENDING, description="Статус бронирования")
    special_requests: Optional[str] = Field(None, description="Особые пожелания")

    @model_validator(mode='after')
    def validate_dates(self):
        # Проверка что дата выезда после даты заезда
        if self.check_out_date <= self.check_in_date:
            raise ValueError('Check-out date must be after check-in date')
        
        # Проверка что дата заезда в будущем (используем timezone-aware)
        now = datetime.now(timezone.utc)
        if self.check_in_date.replace(tzinfo=timezone.utc) < now:
            raise ValueError('Check-in date must be in the future')
        
        return self

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    """Схема для частичного обновления бронирования"""
    model_config = ConfigDict(from_attributes=True)
    
    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None
    total_price: Optional[float] = Field(None, gt=0)
    status: Optional[BookingStatus] = None
    special_requests: Optional[str] = None

    @model_validator(mode='after')
    def validate_dates(self):
        # Проверяем даты только если обе указаны
        if self.check_in_date and self.check_out_date:
            if self.check_out_date <= self.check_in_date:
                raise ValueError('Check-out date must be after check-in date')
        return self

class BookingInDBBase(BookingBase):
    id: int
    created_at: datetime
    updated_at: datetime

class Booking(BookingInDBBase):
    pass

class BookingResponse(Booking):
    """Расширенный ответ с дополнительной информацией"""
    user_email: Optional[str] = None
    room_number: Optional[str] = None
    hotel_name: Optional[str] = None