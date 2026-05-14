from fastapi import FastAPI
from app.api.api_v1 import api_router
from app.core.config import settings
from app.database import engine, Base  # Импортируем engine и Base из database

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Подключаем маршруты
app.include_router(api_router, prefix=settings.API_V1_STR)




@app.get("/")
def read_root():
    return {"message": "Welcome to Hotel Booking API"}
