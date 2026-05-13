from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from app.models import Review, Hotel, User
from app.schemas import ReviewCreate, ReviewUpdate, Review
from fastapi import HTTPException, status

async def get_review(db: AsyncSession, review_id: int) -> Review:
    result = await db.execute(
        select(Review)
        .where(Review.id == review_id)
        .options(selectinload(Review.hotel), selectinload(Review.user))
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return Review.model_validate(review)

async def get_reviews_by_hotel(db: AsyncSession, hotel_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Review)
        .where(Review.hotel_id == hotel_id)
        .offset(skip)
        .limit(limit)
        .options(selectinload(Review.user))
    )
    reviews = result.scalars().all()
    return [Review.model_validate(review) for review in reviews]

async def get_user_reviews(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Review)
        .where(Review.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .options(selectinload(Review.hotel))
    )
    reviews = result.scalars().all()
    return [Review.model_validate(review) for review in reviews]

async def create_review(db: AsyncSession, review_in: ReviewCreate, current_user: User):
    # Проверка, что отель существует
    result = await db.execute(select(Hotel).where(Hotel.id == review_in.hotel_id))
    hotel = result.scalar_one_or_none()
    if not hotel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    
    # Проверка, что пользователь бронировал этот отель
    result = await db.execute(
        select(Review)
        .where(
            Review.user_id == current_user.id,
            Review.hotel_id == review_in.hotel_id
        )
    )
    existing_review = result.scalar_one_or_none()
    if existing_review:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already reviewed this hotel")
    
    db_review = Review(
        user_id=current_user.id,
        hotel_id=review_in.hotel_id,
        rating=review_in.rating,
        comment=review_in.comment
    )
    
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    
    # Обновление среднего рейтинга отеля
    await update_hotel_rating(db, review_in.hotel_id)
    
    return Review.model_validate(db_review)

async def update_review(db: AsyncSession, review_id: int, review_in: ReviewUpdate, current_user: User):
    result = await db.execute(select(Review).where(Review.id == review_id))
    db_review = result.scalar_one_or_none()
    if not db_review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    if db_review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    update_data = review_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_review, key, value)
    
    await db.commit()
    await db.refresh(db_review)
    
    # Обновление среднего рейтинга отеля
    await update_hotel_rating(db, db_review.hotel_id)
    
    return Review.model_validate(db_review)

async def delete_review(db: AsyncSession, review_id: int, current_user: User):
    result = await db.execute(select(Review).where(Review.id == review_id))
    db_review = result.scalar_one_or_none()
    if not db_review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    if db_review.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    hotel_id = db_review.hotel_id
    await db.delete(db_review)
    await db.commit()
    
    # Обновление среднего рейтинга отеля
    await update_hotel_rating(db, hotel_id)
    
    return True

async def update_hotel_rating(db: AsyncSession, hotel_id: int):
    # Расчет среднего рейтинга для отеля
    result = await db.execute(
        select(func.avg(Review.rating))
        .where(Review.hotel_id == hotel_id)
    )
    avg_rating = result.scalar() or 0.0
    
    # Обновление рейтинга отеля
    result = await db.execute(select(Hotel).where(Hotel.id == hotel_id))
    hotel = result.scalar_one_or_none()
    if hotel:
        hotel.rating = round(avg_rating, 1)
        await db.commit()
        await db.refresh(hotel)