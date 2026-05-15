from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env"
    )
    
    PROJECT_NAME: str = "Hotel Booking API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database - используем SQLite, так как asyncpg не установился на Python 3.14
    DATABASE_URL: str = "sqlite+aiosqlite:///./test_hotel_booking.db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-here-use-env-var-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


# Создаём экземпляр настроек (ОБЯЗАТЕЛЬНО для импорта!)
@lru_cache()
def get_settings():
    return Settings()

# Экспортируем экземпляр settings, чтобы можно было импортировать напрямую
settings = get_settings()