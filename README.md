# PolyLRC

[![Python](https://img.shields.io/badge/python-3.13--slim-blue)](https://www.python.org/)  
[![FastAPI](https://img.shields.io/pypi/v/fastapi?color=%2334D058&label=FastAPI)](https://fastapi.tiangolo.com/)  
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

Minimal prediction market platform built with **FastAPI**, **PostgreSQL**, and **Redis** for a computer science final project.  
Phases 1–4 are implemented: user authentication, wallet management, and market creation.

---

## Roadmap
- [x] Phase 1 - Infrastructure (FastAPI, PostgreSQL, Redis, Alembic, health check)
- [x] Phase 2 - Authentication (register, login, JWT access + refresh tokens, bcrypt)
- [x] Phase 3 - Wallets (ledger-based balance, faucet, rate limiting)
- [x] Phase 4 - Markets (create, list, get, patch, state machine, outcomes)
- [ ] Phase 5 - Orders & matching engine (limit orders, price-time priority, partial fills)
- [ ] Phase 6 - Resolution & settlement (admin resolves, winning outcome pays out)
- [ ] Phase 7 - Frontend (login, market list, order placement, wallet balance, order book)

---

## Features Implemented

### 1. User Management
- User registration and login
- JWT-based authentication (access + refresh tokens)
- Password hashing using bcrypt
- Role-based system (admin / user)
- `/users/me` endpoint for retrieving authenticated user profile

### 2. Wallets
- Wallet model with transaction registry
- Faucet on registration (initial credit)
- Credit and debit helper functions
- Balance calculated dynamically (no balance column)

### 3. Markets
- Market creation with multiple outcomes
- Market states: `PRE`, `OPEN`, `CLOSED`, `RESOLUTION`
- Open/close timestamps
- Markets only mutable if `PRE`
- Market listing and detail endpoints
- Market descriptions in Markdown (stored as plain text)

### 4. Infrastructure
- FastAPI backend
- PostgreSQL database
- Alembic migrations for schema versioning
- Redis caching
- Docker + docker-compose support
- Environment-based configuration
- Health check endpoints (`GET /health`, `GET /health/db`)

---

## Getting started

### Requirements
This project supports both Docker and Podman.
- Docker & docker-compose, or
- Podman & podman-compose (used in development on Fedora Silverblue)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/triskattie/polyLRC.git
cd polyLRC
```

2. Create a .env file:
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=polylrc
DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/polylrc
REDIS_URL=redis://redis:6379/0

ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
SECRET_KEY=generate-a-512-bit-random-key
JWT_ALGORITHM=HS256

FAUCET_AMOUNT=10
FAUCET_COOLDOWN_MINUTES=1
```
Generate a secure SECRET_KEY:
```bash
openssl rand -hex 64
```
3. Build and start:
```bash
# Docker
docker-compose up -d --build
# Podman
podman compose up -d --build
```

4. Apply database migrations:
```bash
# Docker
docker-compose exec -w /app api alembic upgrade head
# Podman
podman compose exec -w /app api alembic upgrade head
```
5. Access API documentation at http://localhost:8000/docs

---

## Testing

The test suite uses pytest with SQLite in-memory, no extra containers needed.

Install test dependencies:
```bash
# Docker
docker-compose exec -w /app api pip install -r requirements-test.txt
# Podman
podman compose exec -w /app api pip install -r requirements-test.txt
```

Run every test:
```bash
# Docker
docker-compose exec -w /app api pytest -v
# Podman
podman compose exec -w /app api pytest -v
```

Run only integration tests:
```bash
podman compose exec -w /app api pytest -m integration -v
```

---

## Project structure
```text
src
├── api
│   ├── __init__.py
│   └── v1
│       ├── __init__.py
│       └── routers
│           ├── auth.py
│           ├── health.py
│           ├── __init__.py
│           ├── markets.py
│           ├── users.py
│           └── wallets.py
├── core
│   ├── dependencies.py
│   ├── errors.py
│   ├── __init__.py
│   └── security.py
├── crud
│   ├── __init__.py
│   ├── market.py
│   ├── user.py
│   └── wallet.py
├── db
│   ├── base.py
│   ├── deps.py
│   ├── __init__.py
│   ├── models.py
│   ├── redis.py
│   └── session.py
├── __init__.py
├── main.py
├── schemas
│   ├── auth.py
│   ├── __init__.py
│   ├── market.py
│   ├── user.py
│   └── wallet.py
└── services
    ├── auth_actions.py
    ├── auth_validation.py
    ├── __init__.py
    ├── markets.py
    └── wallets.py
```

## Implemented API endpoints
### Authentication
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`

### Users
- `GET /users/me`

### Wallets
- `GET /wallet`
- `POST /wallet/faucet`

### Markets
- `POST /markets`
- `GET /markets`
- `GET /markets/{market_id}`
- `PATCH /markets/{market_id}`

## Contributing
This project is currently not open to contributions.