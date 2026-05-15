from fastapi import FastAPI
from fastapi import FastAPI
from app.api.api_v1 import api_router
from app.core.config import settings
from app.database import engine, Base  # Импортируем engine и Base из database
from app.models import user, hotel, room, booking, payment, review  # Импортируем все модели для создания таблиц

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Создание таблиц при запуске приложения (в реальном проекте используйте Alembic)
# Base.metadata.create_all(bind=engine)  # Удалено: синхронный вызов на async engine невозможен

# Подключаем маршруты
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to Hotel Booking API"}
