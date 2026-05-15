import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from httpx import AsyncClient, ASGITransport
from app.core.config import Settings

# Тестовые настройки с in-memory SQLite
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

class TestSettings(Settings):
    DATABASE_URL: str = TEST_DATABASE_URL

test_settings = TestSettings()

# Создание асинхронного движка для тестов
engine = create_async_engine(
    test_settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Асинхронная сессия для тестов
TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Зависимость для получения тестовой сессии БД
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

# Переопределение зависимости get_db в приложении
app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(scope="session")
async def test_db():
    """Создает и удаляет базу данных для тестов."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield TestingSessionLocal
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def db_session(test_db):
    """Создает новую сессию для каждого теста с откатом изменений."""
    async with test_db() as session:
        async with session.begin():
            try:
                yield session
            finally:
                await session.rollback()

@pytest_asyncio.fixture(scope="function")
async def client():
    """Фикстура AsyncClient для тестирования API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

@pytest_asyncio.fixture
async def test_user(db_session):
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        role="user"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def auth_headers(client, test_user):
    response = await client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "password123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}