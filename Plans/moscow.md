# MoSCoW Structure PolyLRC

## Must haves
### Infrastructure
- FastAPI backend
- PostgreSQL
- Alembic migrations
- Redis (caching)
- Docker + docker-compose
- Env based config
- Health check endpoint

### Users
- User registration
- Login
- JWT access + refresh tokens
- Password hashing (bcrypt)
- >GET /users/me 
- Role system

### Wallet
- Wallet model
- Wallet transactions (ledger)
- No balance column
- Faucet on registration
- Atomic transactions
- Rate-limited faucet

### Markets
- Create market
- Market states (PRE, OPEN, CLOSED, RESOLUTION)
- Outcomes
- Open/Close timestamps
- Immutable markets once OPEN

### Orders & Matching engine
- Only limit orders
- Buy / Sell
- One outcome per order
- Price-time priority
- Partial fills
- Full database transaction per match

### Market resolution & Settlement
- Admin resolves market
- Winning outcome pays out
- Losing positions cleared
- Trading locked after resolution

### Frontend (minimal)
- Login / Register
- Market list
- Market detail
- Order placement
- Wallet balance
- Order book view

### Deployment (basic)
- Public deployment with special key
- HTTPS
- Logs visible
- Basic ratelimiting


## Should haves
### Backend
- Admin UI
- Audit logs for admin actions
- Input validation everywhere
- Simple analytics

### Frontend
- Charts
- Better order book
- Loading / empty states
- Error handling UX


## Could haves
### Features
- Trade history per user
- User profiles
- Market categories / tags
- Market search
- Pagination everywhere
- UI theming
- Notifications


## Won't haves
- Real money
- Realtime updates (webSockets)
- Market orders
- Automated market makers
- Multi-currency wallets
- Mobile app
- Social features
- Comments / chat
- Refactors for cleanliness


## FINAL CHECKLIST
**Can a user do these steps?**
1. Register
2. Get tokens
3. Open a market
4. Place a trade
5. Match another user
6. Resolve the market
7. See wallet change
