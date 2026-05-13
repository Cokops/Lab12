from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc
from app.models import Booking, Hotel, Room, Review, Payment
from app.schemas import AnalyticsReport
from datetime import datetime, timedelta
from typing import Dict, Any

async def generate_analytics_report(db: AsyncSession) -> Dict[str, Any]:
    """Генерация аналитического отчёта"""
    
    # Общая статистика
    total_hotels = await db.execute(select(func.count(Hotel.id)))
    total_rooms = await db.execute(select(func.count(Room.id)))
    total_bookings = await db.execute(select(func.count(Booking.id)))
    total_reviews = await db.execute(select(func.count(Review.id)))
    
    # Прибыль за последние 30 дней
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    revenue_30d = await db.execute(
        select(func.sum(Booking.total_price))
        .where(Booking.created_at >= thirty_days_ago)
    )
    
    # Загрузка номеров
    total_rooms_count = total_rooms.scalar() or 0
    if total_rooms_count > 0:
        occupied_rooms = await db.execute(
            select(func.count(Booking.id))
            .where(
                Booking.status == "confirmed",
                Booking.check_in_date <= datetime.utcnow(),
                Booking.check_out_date >= datetime.utcnow()
            )
        )
        occupancy_rate = (occupied_rooms.scalar() or 0) / total_rooms_count
    else:
        occupancy_rate = 0.0
    
    # Топ-5 самых популярных отелей
    top_hotels = await db.execute(
        select(
            Hotel.name,
            func.count(Booking.id).label('booking_count')
        )
        .join(Room)
        .join(Booking)
        .group_by(Hotel.id)
        .order_by(desc('booking_count'))
        .limit(5)
    )
    top_hotels_list = [dict(row) for row in top_hotels.all()]
    
    # Средний рейтинг отелей
    avg_rating = await db.execute(select(func.avg(Hotel.rating)))
    
    # Отчёты по статусам бронирований
    booking_status_stats = await db.execute(
        select(
            Booking.status,
            func.count(Booking.id)
        )
        .group_by(Booking.status)
    )
    status_stats = dict(booking_status_stats.all())
    
    return {
        "total_hotels": total_hotels.scalar() or 0,
        "total_rooms": total_rooms_count,
        "total_bookings": total_bookings.scalar() or 0,
        "total_reviews": total_reviews.scalar() or 0,
        "revenue_30d": revenue_30d.scalar() or 0.0,
        "occupancy_rate": round(occupancy_rate * 100, 2),
        "average_hotel_rating": round(avg_rating.scalar() or 0.0, 2),
        "total_payments": 0,
        "successful_payments": 0,
        "top_hotels_by_bookings": top_hotels_list,
        "booking_status_distribution": status_stats,
        "generated_at": datetime.utcnow().isoformat()
    }