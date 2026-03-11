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
- Token storge in redis

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
- Rate limited faucet

Rules
- No balance column
- Balance = sum of all transactions

Endpoints
- GET /wallet
- POST /wallet/faucet

## Phase 4 - Market creation
### Backend
Models
- > markets
- > market_outcomes

Features
- Create market
- Different market states
- Market description with markdown, saved as plain text
- Open / close timestamps

Rules
- Only OPEN markets accept orders
- No editing except during PRE

Endpoints
- GET /markets
- GET /markets/{id}
- POST /markets
- PATCH /markets/{id}

## Phase 5 - Orders, trading engine and testing
### Backend
Testing
- Pytest for testing
- SQLite database in-memory for test isolation
- Mocked Redis
- Fixtures - db_engine, db_session, client, mock_redis, registered_user, user_tokens, auth_headers, admin_user, admin_headers, open_market
- Marks - integration, slow

Models
- > orders
- > trades
- > positions

Order types
- Only limit orders
- Buy / sell
- One outcome per order

Matching engine
- Price-time priority
- Partial fills
- Single process

Flow
1. Valid market is OPEN
2. Validate outcome belongs to market
3. Check buyer balance covers cost (BUY only)
4. Insert incoming order
5. Fetch best opposing order (price-time priority)
6. For each maker: fill, write trade, update wallet, update position
7. Update order statuses
8. Commit transaction

Endpoints
- POST /orders
- GET /markets/{id}/orderbook
- GET /orders/{id}

## Phase 6 - Market resolution
### Backend
Models 
- > winning_outcome_id added to markets (nullable ForeignKey)

Features
- Admin seeds initial liquidity per market
- Admin resolves market
- Payout calculation
- Wallet settlement

Rules
- Only admin can resolve
- Each winning position pays 1*amount
- All positions cleared after settlement

Flow
1. Validate admin
2. Validate market is OPEN or CLOSED
3. Validate outcome belongs to market
4. Transition market to RESOLVED and set winning_outcome_id
5. Query all winning positions
6. Give every winner's wallet by position amount
7. Delete all positions for market

Endpoints
- POST /markets/{id}/resolve
- POST /markets/{id}/seed

## Phase 7 - Frontend core
### Frontend
Pages
- Landing
- Register/login
- Market list
- Market detail
- Wallet page

Features
- Auth flow
- Place orders
- View orderbook
- View trades
- Charts