from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.dependencies import get_current_user
from src.db.deps import get_db
from src.schemas.market import MarketCreation, MarketCreationResponse, MarketId, MarketResponse
from src.services.markets import market_creation_service, market_by_id_service
from src.core.errors import MissingPermission, MarketNotFound
from uuid import UUID

router = APIRouter(prefix="/markets", tags=["v1:Markets"])

@router.post("", response_model=MarketCreationResponse)
async def market_creation_endpoint(payload: MarketCreation, user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        async with db.begin():
            result = await market_creation_service(payload=payload, creator_id=user.user_id, db=db)
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