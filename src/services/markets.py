from src.schemas.market import MarketCreation, MarketCreationResponse, MarketResponse, MarketOutcomeResponse, MarketUpdate, OrderBookResponse, OrderBookEntry
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.user import get_user_by_uuid
from src.crud.market import create_market, create_outcome, get_market_by_id, get_markets, patch_market, get_market_orderbook
from src.core.errors import MissingPermission, MarketNotFound, MarketOpen, OutcomeNotInMarket
from datetime import datetime, timezone
from src.db.models import MarketState, TransactionType
from src.crud.order import get_winning_positions, delete_positions_for_market
from src.crud.wallet import get_wallet_by_user, create_transaction

async def market_creation_service(payload: MarketCreation, creator_id: UUID, db: AsyncSession):
    creator = await get_user_by_uuid(db=db, user_id=creator_id)
    if creator.role != "admin":
        raise MissingPermission()

    if not payload.title.strip():
        raise ValueError("title can't be empty")

    if len(payload.outcomes) < 2:
        raise ValueError("market must have at least two outcomes")

    names = [outcome.name.lower() for outcome in payload.outcomes]
    if len(names) != len(set(names)):
        raise ValueError("duplicate outcome names")
    
    for outcome in payload.outcomes:
        if not outcome.name.strip():
            raise ValueError("outcome name must not be empty")

    if payload.open_timestamp and payload.closed_timestamp:
        if payload.closed_timestamp <= payload.open_timestamp:
            raise ValueError("closed timestamp must be after open timestamp")

    if payload.open_timestamp and payload.open_timestamp <= datetime.now(timezone.utc):
        raise ValueError("open timestamp can't be in the past")


    market = await create_market(creator_id=creator_id, title=payload.title, description=payload.description, open_timestamp=payload.open_timestamp, closed_timestamp=payload.closed_timestamp, db=db)
    outcomes = []
    for outcm in payload.outcomes:
        outcome = await create_outcome(market_id=market.id, name=outcm.name, description=outcm.description, db=db)
        outcomes.append(outcome.id)
    
    return MarketCreationResponse(
        market_id=market.id,
        outcome_ids=outcomes
    )

async def markets_service(limit: int, offset: int, state: str | None, db: AsyncSession):
    markets, total = await get_markets(limit=limit, offset=offset, state=state, db=db)
    return {
        "markets": markets,
        "total": total,
        "limit": limit,
        "offset": offset
    }

async def market_by_id_service(market_id: UUID, db: AsyncSession):
    market = await get_market_by_id(market_id=market_id, db=db)
    if not market:
        raise MarketNotFound()

    outcomes_responses = [MarketOutcomeResponse(
        id=o.id,
        name=o.name,
        description=o.description
    ) for o in market.outcomes]

    return MarketResponse(
        id=market.id,
        title=market.title,
        description=market.description,
        state=market.state,
        open_timestamp=market.open_timestamp,
        closed_timestamp=market.closed_timestamp,
        created_at=market.created_at,
        updated_at=market.updated_at,
        outcomes=outcomes_responses
    )

async def patch_market_service(market_id: UUID, payload: MarketUpdate, user_id: UUID, db: AsyncSession):
    user = await get_user_by_uuid(db=db, user_id=user_id)
    if user.role != "admin":
        raise MissingPermission()
    market = await get_market_by_id(market_id=market_id, db=db)
    if not market:
        raise MarketNotFound()
    if payload.state:
        valid_transitions = {
            MarketState.PRE: MarketState.OPEN,
            MarketState.OPEN: MarketState.CLOSED,
            MarketState.CLOSED: MarketState.RESOLVED,
        }
        if valid_transitions.get(market.state) != payload.state:
            raise InvalidStateTransition()
        market.state = payload.state
    else:
        if market.state != MarketState.PRE:
            raise MarketOpen()
    new_market = await patch_market(market_id=market_id, payload=payload, db=db)
    await db.refresh(new_market)
    outcomes_responses = [MarketOutcomeResponse(
        id=o.id,
        name=o.name,
        description=o.description
    ) for o in new_market.outcomes]

    return MarketResponse(
        id=new_market.id,
        title=new_market.title,
        description=new_market.description,
        state=new_market.state,
        open_timestamp=new_market.open_timestamp,
        closed_timestamp=new_market.closed_timestamp,
        created_at=new_market.created_at,
        updated_at=new_market.updated_at,
        outcomes=outcomes_responses
    )

async def get_orderbook_service(market_id: UUID, outcome_id: UUID, db: AsyncSession):
    market = await get_market_by_id(market_id=market_id, db=db)
    if not market:
        raise MarketNotFound()
    
    if outcome_id not in [o.id for o in market.outcomes]:
        raise OutcomeNotInMarket()

    bids, asks = await get_market_orderbook(market_id=market_id, outcome_id=outcome_id, db=db)
    return OrderBookResponse(
        market_id=market_id,
        outcome_id=outcome_id,
        bids=[OrderBookEntry(price=row.price, remaining=row.remaining) for row in bids],
        asks=[OrderBookEntry(price=row.price, remaining=row.remaining) for row in asks],
    )

async def resolve_market_service(market_id: UUID, winning_outcome_id: UUID, user_id: UUID, db: AsyncSession):
    user = await get_user_by_uuid(db=db, user_id=user_id)
    if user.role != "admin":
        raise MissingPermission()
    market = await get_market_by_id(market_id=market_id, db=db)
    if not market:
        raise MarketNotFound()
    if market.state not in [MarketState.OPEN, MarketState.CLOSED]:
        raise InvalidStateTransition()
    if winning_outcome_id not in [o.id for o in market.outcomes]:
        raise OutcomeNotInMarket()
    market.state = MarketState.RESOLVED
    market.winning_outcome_id = winning_outcome_id
    winning_positions = await get_winning_positions(winning_outcome_id=winning_outcome_id, db=db)
    for p in winning_positions:
        wallet = await get_wallet_by_user(user_id=p.user_id, db=db)
        await create_transaction(db=db, wallet_id=wallet.id, amount=p.amount, type=TransactionType.PAYOUT, related_market_id=market_id)
    await delete_positions_for_market(market_id=market_id, db=db)
    await db.refresh(market)

    outcomes_responses = [MarketOutcomeResponse(
        id=o.id,
        name=o.name,
        description=o.description
    ) for o in market.outcomes]

    return MarketResponse(
        id=market.id,
        winning_outcome_id=market.winning_outcome_id,
        title=market.title,
        description=market.description,
        state=market.state,
        open_timestamp=market.open_timestamp,
        closed_timestamp=market.closed_timestamp,
        created_at=market.created_at,
        updated_at=market.updated_at,
        outcomes=outcomes_responses
    )