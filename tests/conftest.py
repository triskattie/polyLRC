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

@pytest.fixture
async def registered_user(client):
    email = "example@gmail.com"
    password = "s3curepassword!"
    response = await client.post(
        "/v1/auth/register",
        json={"email": email, "password": password}
    )
    assert response.status_code == 200
    return response.json(), email, password

@pytest.fixture
async def user_tokens(registered_user):
    tokens, _, _ = registered_user
    return tokens

@pytest.fixture
async def auth_headers(user_tokens):
    return {"Authorization": f"Bearer {user_tokens['access_token']}"}

@pytest.fixture
async def admin_user(client, db_session):
    email = "admin@example.com"
    password = "4dminp4ssword"
    response = await client.post(
        "/v1/auth/register",
        json={"email": email, "password": password}
    )
    assert response.status_code == 200
    from sqlalchemy import text
    await db_session.execute(
        text("UPDATE users SET role = 'admin' WHERE email = :e"),
        {"e": email}
    )
    await db_session.commit()

    login_response = await client.post(
        "/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert login_response.status_code == 200
    return login_response.json(), email, password

@pytest.fixture
async def admin_headers(admin_user):
    tokens, _, _ = admin_user
    return {"Authorization": f"Bearer {tokens['access_token']}"}

@pytest.fixture
async def open_market(client, admin_headers):
    VALID_MARKET = {
        "title": "Will these tests fail?",
        "description": "A simple yes or no valid_market.",
        "outcomes": [
            {"name": "Yes", "description": "The tests fail"},
            {"name": "No", "description": "The tests succeed"}
        ]
    }
    response = await client.post("/v1/markets", json=VALID_MARKET, headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    market_id = body["market_id"]

    patch = await client.patch(
        f"/v1/markets/{market_id}",
        json={"state": "OPEN"},
        headers=admin_headers
    )
    assert patch.status_code == 200

    return market_id, body["outcome_ids"]