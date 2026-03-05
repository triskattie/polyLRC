from src.schemas.market import MarketCreation, MarketCreationResponse
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.user import get_user_by_uuid
from src.crud.market import create_market, create_outcome
from src.core.errors import MissingPermission
from datetime import datetime, timezone

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