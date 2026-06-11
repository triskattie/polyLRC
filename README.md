# PolyLRC

[![Python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

PolyLRC is a prediction market project with a FastAPI backend and a Next.js frontend.
It includes JWT auth, wallets with a faucet, binary markets, an orderbook, limit orders, matching, and admin resolution.

## Tech stack

- Backend:
  - FastAPI because it's one of the [fastest](https://fastapi.tiangolo.com/benchmarks/) frameworks 
  - Asynchronous SQLAlchemy because it pairs well into FastAPI
  - Alembic for strong type checking
  - PostgreSQL because of the ACID compliance required for market systems
  - Redis for simple caching
- Frontend: 
  - Next.js App Router for server-side components and streaming
  - React Query for automatic caching, deduplication and mutations
  - Axios for a centralized API configuration and the interceptors
- Testing:
  - pytest(-asyncio) because it's the most popular testing framework
  - httpx for direct communication with the FastAPI app and the asynchronous functionality
  - aiosqlite for an in-memory database and asynchronous due to the choice of async SQLAlchemy
- Infra: 
  - Docker Compose for simple startup of the API, PostgreSQL and Redis
  
Notes: 
Tests use mocked Redis and the aiosqlite in-memory database so there are no additional containers required.

## Repository layout

```text
.
├── src/                  # FastAPI application
│   ├── main.py           # App entry point
│   ├── api/v1/routers/   # Route handlers
│   ├── services/         # Business logic
│   ├── crud/             # Data access
│   ├── core/             # Config, dependencies, security
│   ├── schemas/          # Pydantic models
│   └── db/               # SQLAlchemy models/session/redis
├── alembic/              # Database migrations
├── frontend/             # Next.js app
└── tests/                # Backend tests
```

## License

MIT. See [LICENSE](LICENSE).