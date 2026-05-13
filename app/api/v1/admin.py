from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import AnalyticsReport
from app.services.analytics_service import generate_analytics_report
from app.core.security import get_current_admin
from app.models import User

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/analytics", response_model=AnalyticsReport)
async def admin_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Панель аналитики для администратора"""
    return await generate_analytics_report(db)