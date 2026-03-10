from fastapi import APIRouter, Depends, HTTPException, status
from src.schemas.order import OrderInput, OrderResponse
from src.core.dependencies import get_current_user
from src.db.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.orders import create_order_service, get_order_service
from src.core.errors import MarketNotFound, MarketNotOpen, OrderNotFound, OrderAccessDenied, OutcomeNotInMarket
from uuid import UUID

router = APIRouter(prefix="/orders", tags=["v1:Orders"])

@router.post("", response_model=OrderResponse)
async def create_order_endpoint(payload: OrderInput, user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        order = await create_order_service(payload=payload, user_id=user.user_id, db=db)
        await db.commit()
        await db.refresh(order)
        return order
    except MarketNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="market not found"
        )
    except MarketNotOpen:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="market is not open to orders"
        )
    except OutcomeNotInMarket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="outcome not in market"
        )

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_endpoint(order_id: UUID, user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        order = await get_order_service(order_id=order_id, user_id=user.user_id, db=db)
        return order
    except OrderNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="order not found"
        )
    except OrderAccessDenied:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="access denied"
        )