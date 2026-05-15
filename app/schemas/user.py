from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1)
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    """Схема для обновления - все поля опциональны"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1)
    phone: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)

class UserInDBBase(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str