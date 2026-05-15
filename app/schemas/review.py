from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class ReviewBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    user_id: int
    hotel_id: int
    rating: float = Field(..., ge=1.0, le=5.0)
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    """Схема для частичного обновления отзыва"""
    model_config = ConfigDict(from_attributes=True)
    
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    comment: Optional[str] = None

class ReviewInDBBase(ReviewBase):
    id: int
    created_at: datetime
    updated_at: datetime

class Review(ReviewInDBBase):
    pass