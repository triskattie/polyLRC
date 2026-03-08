import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from src.db.base import Base
from src.db.deps import get_db
from src.main import app
from unittest.mock import AsyncMock, MagicMock


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(db_engine):
    factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False
    )
    async with factory() as session:
        yield session

@pytest_asyncio.fixture
async def client(db_session, mock_redis):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
def mock_redis(monkeypatch):
    mock = MagicMock()
    mock.store_access_token = AsyncMock()
    mock.is_access_token = AsyncMock(return_value=True)
    mock.claim_faucet = AsyncMock(return_value=True)
    mock.connect = AsyncMock()
    mock.disconnect = AsyncMock()
    monkeypatch.setattr("src.services.auth_actions.redis_manager", mock)
    monkeypatch.setattr("src.services.auth_validation.redis_manager", mock)
    monkeypatch.setattr("src.services.wallets.redis_manager", mock)
    return mock