from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.dependencies import get_current_user
from src.db.deps import get_db
from src.schemas.market import MarketCreation, MarketCreationResponse, MarketId, MarketResponse, MarketsPageResponse, MarketUpdate, OrderBookResponse, ResolveMarketInput
from src.services.markets import market_creation_service, market_by_id_service, markets_service, patch_market_service, get_orderbook_service, resolve_market_service
from src.core.errors import MissingPermission, MarketNotFound, MarketOpen, InvalidStateTransition, OutcomeNotInMarket
from uuid import UUID
from src.db.models import MarketState

router = APIRouter(prefix="/markets", tags=["v1:Markets"])

@router.post("", response_model=MarketCreationResponse)
async def market_creation_endpoint(payload: MarketCreation, user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        result = await market_creation_service(payload=payload, creator_id=user.user_id, db=db)
        await db.commit()
        return result
    except MissingPermission:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not authorized to create markets"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("", response_model=MarketsPageResponse)
async def markets_endpoint(limit: int = Query(20, gt=0, le=100), offset: int = Query(0, ge=0), state: MarketState | None = None, user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await markets_service(limit=limit, offset=offset, state=state, db=db)
    return result

@router.get("/{market_id}", response_model=MarketResponse)
async def market_by_id_endpoint(market_id: UUID, user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        result = await market_by_id_service(market_id=market_id, db=db)
        return result
    except MarketNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="market was not found"
        )

@router.patch("/{market_id}", response_model=MarketResponse)
async def patch_market_endpoint(market_id: UUID, payload: MarketUpdate, user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        market = await patch_market_service(market_id=market_id, payload=payload, user_id=user.user_id, db=db)
        await db.commit()
        return market
    except MissingPermission:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not authorized to modify markets"
        )
    except MarketNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="market was not found"
        )
    except InvalidStateTransition:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="invalid state transition"
        )
    except MarketOpen:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="can't modify markets after opening"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{market_id}/orderbook/{outcome_id}", response_model=OrderBookResponse)
async def get_orderbook(market_id: UUID, outcome_id: UUID, user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        response = await get_orderbook_service(market_id=market_id, outcome_id=outcome_id, db=db)
        return response
    except MarketNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="market was not found"
        )
    except OutcomeNotInMarket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="outcome not in market"
        )

@router.post("/{market_id}/resolve", response_model=MarketResponse)
async def resolve_market_endpoint(market_id: UUID, payload: ResolveMarketInput, user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        market = await resolve_market_service(market_id=market_id, winning_outcome_id=payload.winning_outcome_id, user_id=user.user_id, db=db)
        await db.commit()
        return market
    except MissingPermission:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not authorized to resolve markets"
        )
    except MarketNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="market was not found"
        )
    except InvalidStateTransition:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="invalid state transition"
        )
    except OutcomeNotInMarket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="outcome not in market"
        )