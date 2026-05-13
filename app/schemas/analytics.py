from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional

class AnalyticsReport(BaseModel):
    total_hotels: int
    total_rooms: int
    total_bookings: int
    total_reviews: int
    revenue_30d: float
    occupancy_rate: float  # в процентах
    average_hotel_rating: float
    total_payments: int
    successful_payments: int
    top_hotels_by_bookings: List[Dict[str, Any]]
    booking_status_distribution: Dict[str, int]
    generated_at: str

    class Config:
        from_attributes = True