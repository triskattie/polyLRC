## Phase 1 - skeleton
### Backend  
Deliverables
- Repo
- .env config
- FastAPI app runs
- PostgreSQL connection
- Alembic works
- Redis connection
- Health check endpoint

Tasks
- Create base FastAPI app
- SQLAlchemy session setup
- Alembic init + first migrations
- Redis client
- Dockerfile + docker-compose

## Phase 2 - authentication & users
### Backend
Models
- > users
- > refresh_tokens

Features
- Register
- Login
- JWT issuance
- Password hashing
- Role system

Endpoints
- POST /auth/register
- POST /auth/login
- POST /auth/refresh
- GET /users/me

Security
- Password hashing with bcrypt
- Temporary access tokens
- Refresh token rotation

## Phase 3 - Wallets
### Backend
Models
- > wallets
- > wallet_transactions

Features
- Faucet on registration
- Get wallet balance
- Credit + debit helper functions

Rules
- No balance column
- Balance = sum of all transactions

Endpoints
- GET /wallet
- POST /wallet/faucet