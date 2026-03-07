from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime
from src.db.models import Market, MarketOutcome
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from src.schemas.market import MarketUpdate

async def create_market(
    creator_id: UUID, 
    title: str, 
    description: str, 
    open_timestamp: datetime | None,
    closed_timestamp: datetime | None,
    db: AsyncSession
    ):
    market = Market(
        creator_id=creator_id,
        title=title,
        description=description,
        open_timestamp=open_timestamp,
        closed_timestamp=closed_timestamp
    )
    db.add(market)
    await db.flush()
    return market

async def create_outcome(market_id: UUID, name: str, description: str, db: AsyncSession):
    outcome = MarketOutcome(
        market_id=market_id,
        name=name,
        description=description
    )
    db.add(outcome)
    await db.flush()
    return outcome

async def get_market_by_id(market_id: UUID, db: AsyncSession):
    result = await db.execute(select(Market).options(selectinload(Market.outcomes)).where(Market.id == market_id))
    return result.scalar_one_or_none()

async def get_markets(limit: int, offset: int, state: str | None, db: AsyncSession):
    query = select(Market).options(selectinload(Market.outcomes))

    if state:
        query = query.where(Market.state == state)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    result = await db.execute(query.limit(limit).offset(offset))
    markets = result.scalars().all()
    return markets, total

async def patch_market(market_id, payload: MarketUpdate, db: AsyncSession):
    market = await get_market_by_id(market_id=market_id, db=db)

    if payload.title is not None:
        market.title = payload.title
    if payload.description is not None:
        market.description = payload.description
    if payload.open_timestamp is not None and payload.closed_timestamp is not None:
        if payload.open_timestamp >= payload.closed_timestamp:
            raise ValueError("closed timestamp must be after open timestamp")
        market.open_timestamp = payload.open_timestamp
        market.closed_timestamp = payload.closed_timestamp
    elif payload.open_timestamp is not None and payload.closed_timestamp is None:
        if payload.open_timestamp >= market.closed_timestamp:
            raise ValueError("closed timestamp must be after the open timestamp")
        market.open_timestamp = payload.open_timestamp
    elif payload.open_timestamp is None and payload.closed_timestamp is not None:
        if market.open_timestamp >= payload.closed_timestamp:
            raise ValueError("closed timestamp must be after the open timestamp")
        market.closed_timestamp = payload.closed_timestamp
    if payload.outcomes is not None:
        for o in payload.outcomes:
            if o.delete:
                if not o.id:
                    raise ValueError("delete requires outcome id")
                outcome = await db.get(MarketOutcome, o.id)
                if not outcome or outcome.market_id != market_id:
                    raise ValueError("invalid outcome id")
                await db.delete(outcome)
                continue

            if o.id:
                outcome = await db.get(MarketOutcome, o.id)

                if outcome and outcome.market_id == market.id:
                    if o.name is not None:
                        outcome.name = o.name
                    
                    if o.description is not None:
                        outcome.description = o.description
            
            else:
                if not o.name:
                    raise ValueError("outcomes require a name")
                
                new_outcome = MarketOutcome(
                    market_id=market.id,
                    name=o.name,
                    description=o.description
                )
                db.add(new_outcome)
    await db.flush()

    result = await db.execute(select(func.count()).select_from(MarketOutcome).where(MarketOutcome.market_id == market.id))
    count = result.scalar()
    if count < 2:
        raise ValueError("market must have at least two outcomes")
    await db.refresh(market)
    return market