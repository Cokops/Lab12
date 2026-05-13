from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    PROJECT_NAME: str = "Hotel Booking API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database - используем SQLite, так как asyncpg не установился на Python 3.14
    DATABASE_URL: str = "sqlite+aiosqlite:///./hotel_booking.db"
    
    # JWT
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        case_sensitive = True
        env_file = ".env"


# Создаём экземпляр настроек (ОБЯЗАТЕЛЬНО для импорта!)
@lru_cache()
def get_settings():
    return Settings()

# Экспортируем экземпляр settings, чтобы можно было импортировать напрямую
settings = get_settings()