from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime
from src.db.models import Market, MarketOutcome

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