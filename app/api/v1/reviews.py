from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import Review, ReviewCreate, ReviewUpdate
from app.services.review_service import get_review, get_reviews_by_hotel, get_user_reviews, create_review, update_review, delete_review
from app.core.security import get_current_active_user
from app.models import User

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.get("", response_model=list[Review])
async def read_reviews(
    hotel_id: int = None,
    user_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Получить отзывы (по отелю, пользователю или все)"""
    if hotel_id:
        return await get_reviews_by_hotel(db, hotel_id, skip=skip, limit=limit)
    if user_id:
        return await get_user_reviews(db, user_id, skip=skip, limit=limit)
    result = await db.execute(
        select(Review)
        .offset(skip)
        .limit(limit)
        .options(selectinload(Review.user), selectinload(Review.hotel))
    )
    reviews = result.scalars().all()
    return [Review.model_validate(review) for review in reviews]

@router.get("/{review_id}", response_model=Review)
async def read_review(review_id: int, db: AsyncSession = Depends(get_db)):
    """Получить отзыв по ID"""
    return await get_review(db, review_id)

@router.post("", response_model=Review, status_code=status.HTTP_201_CREATED)
async def create_review_endpoint(
    review_in: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создать новый отзыв"""
    return await create_review(db, review_in, current_user)

@router.put("/{review_id}", response_model=Review)
async def update_review_endpoint(
    review_id: int,
    review_in: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновить отзыв"""
    review = await get_review(db, review_id)
    if review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await update_review(db, review_id, review_in, current_user)

@router.delete("/{review_id}", response_model=bool)
async def delete_review_endpoint(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Удалить отзыв"""
    review = await get_review(db, review_id)
    if review.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await delete_review(db, review_id, current_user)