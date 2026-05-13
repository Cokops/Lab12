from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User
from app.schemas import UserCreate, UserInDB
from app.core.security import get_password_hash, verify_password
from fastapi import HTTPException, status

async def register_user(db: AsyncSession, user_in: UserCreate) -> UserInDB:
    # Проверка на существующего пользователя
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Хеширование пароля
    hashed_password = get_password_hash(user_in.password)
    
    # Создание пользователя
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        phone=user_in.phone
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return UserInDB.model_validate(db_user)

async def authenticate_user(db: AsyncSession, email: str, password: str) -> UserInDB:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return UserInDB.model_validate(user)