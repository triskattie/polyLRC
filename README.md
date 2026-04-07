# PolyLRC

[![Python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

PolyLRC is a prediction market project with a FastAPI backend and a Next.js frontend.
It includes JWT auth, wallets with a faucet, binary markets, an orderbook, limit orders, matching, and admin resolution.

## Current status

Implemented in backend:
- Auth with access + refresh token rotation
- Users endpoint for current profile
- Wallet balance and wallet transaction history
- Market lifecycle (PRE -> OPEN -> CLOSED -> RESOLVED)
- Market seeding and orderbook views
- Limit orders with price-time priority matching
- Market resolution and payout settlement

Implemented in frontend:
- Landing page
- Login/Register
- Market list and market detail/trading page
- Admin market create/edit/seed pages
- Admin market resolve page
- Docs page
- Feedback page
- Dashboard page

## Tech stack

- Backend: FastAPI, SQLAlchemy (async), Alembic, PostgreSQL, Redis
- Frontend: Next.js (App Router), React Query, Axios
- Testing: pytest, pytest-asyncio, httpx, aiosqlite
- Infra: Docker Compose (api + postgres + redis)

## Repository layout

```text
.
├── src/                  # FastAPI application
│   ├── api/v1/routers/   # Route handlers
│   ├── services/         # Business logic
│   ├── crud/             # Data access
│   ├── schemas/          # Pydantic models
│   └── db/               # SQLAlchemy models/session/redis
├── alembic/              # Database migrations
├── frontend/             # Next.js app
└── tests/                # Backend tests
```

## Environment variables

Create a root `.env` file for backend and Docker services:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=polylrc

# Keep this in sync with docker-compose service names
DATABASE_URL=postgresql://postgres:postgres@db:5432/polylrc
REDIS_URL=redis://redis:6379/0

ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
JWT_ALGORITHM=HS256
SECRET_KEY=replace-with-a-random-64-byte-hex

FAUCET_AMOUNT=10
FAUCET_COOLDOWN_MINUTES=1
```

Generate a secure `SECRET_KEY`:

```bash
openssl rand -hex 64
```

Create a frontend env file at `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Quick start with Docker Compose

1. Start services:

```bash
docker compose up -d --build
```

2. Run migrations:

```bash
docker compose exec -w /app api alembic upgrade head
```

3. Open:

- API docs: http://localhost:8000/docs
- API base: http://localhost:8000/v1

Frontend runs separately (see below), unless you add it to compose.

## Local development (without Docker)

### Backend

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run API:

```bash
uvicorn src.main:app --reload
```

4. Apply migrations when needed:

```bash
alembic upgrade head
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend dev server: http://localhost:3000

## API endpoints

All API routes are prefixed with `/v1`.

Health:
- `GET /v1/health`
- `GET /v1/health/db`

Auth:
- `POST /v1/auth/register`
- `POST /v1/auth/login`
- `POST /v1/auth/refresh`

Users:
- `GET /v1/users/me`

Wallet:
- `GET /v1/wallet`
- `POST /v1/wallet/faucet`
- `GET /v1/wallet/transactions`

Markets:
- `POST /v1/markets`
- `GET /v1/markets`
- `GET /v1/markets/{market_id}`
- `PATCH /v1/markets/{market_id}`
- `GET /v1/markets/{market_id}/orderbook/{outcome_id}`
- `POST /v1/markets/{market_id}/seed`
- `POST /v1/markets/{market_id}/resolve`

Orders:
- `POST /v1/orders`
- `GET /v1/orders/{order_id}`

Utility route:
- `GET /hit` (Redis-backed counter)

## Testing

Install test dependencies:

```bash
pip install -r requirements-test.txt
```

Run all tests:

```bash
pytest -v
```

Run integration-only tests:

```bash
pytest -m integration -v
```

Notes:
- Tests use in-memory SQLite and mocked Redis.
- They do not require PostgreSQL or Redis containers.

## License

MIT. See [LICENSE](LICENSE).