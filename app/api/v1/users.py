from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import User, UserCreate, UserUpdate
from app.services import get_user, get_users, create_user, update_user, delete_user
from app.core.security import get_current_active_user, get_current_admin
from app.models import User as UserModel

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=list[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin)
):
    """Получить список пользователей (только для администраторов)"""
    return await get_users(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Получить пользователя по ID"""
    user = await get_user(db, user_id)
    if user.id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return user

@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin)
):
    """Создать нового пользователя (только для администраторов)"""
    return await create_user(db, user_in)


@router.put("/{user_id}", response_model=User)
async def update_user_endpoint(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Обновить пользователя"""
    user = await get_user(db, user_id)
    if user.id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await update_user(db, user_id, user_in)

@router.delete("/{user_id}", response_model=bool)
async def delete_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin)
):
    """Удалить пользователя (только для администраторов)"""
    user = await get_user(db, user_id)
    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself")
    return await delete_user(db, user_id)