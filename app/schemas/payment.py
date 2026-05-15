from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    booking_id: int
    amount: float = Field(..., gt=0)
    payment_method: str = Field(..., min_length=1)
    status: PaymentStatus = PaymentStatus.PENDING

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    """Схема для частичного обновления платежа"""
    model_config = ConfigDict(from_attributes=True)
    
    amount: Optional[float] = Field(None, gt=0)
    payment_method: Optional[str] = None
    status: Optional[PaymentStatus] = None

class PaymentInDBBase(PaymentBase):
    id: int
    transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class Payment(PaymentInDBBase):
    pass