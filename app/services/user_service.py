from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User 
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User
from fastapi import HTTPException, status
from app.core.security import get_password_hash

async def get_user(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return User.model_validate(user)

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(User)
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()
    return [User.model_validate(user) for user in users]

async def create_user(db: AsyncSession, user_in: UserCreate):
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
    
    return User.model_validate(db_user)


async def update_user(db: AsyncSession, user_id: int, user_in: UserUpdate):
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    await db.commit()
    await db.refresh(db_user)
    return User.model_validate(db_user)


async def delete_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.delete(db_user)
    await db.commit()
    return True