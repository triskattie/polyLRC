from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.order import OrderInput
from uuid import UUID
from src.db.models import Order, OrderSide, OrderStatus, Trade, Position
from decimal import Decimal
from sqlalchemy import select

async def create_order(payload: OrderInput, user_id: UUID, db: AsyncSession):
    order = Order(
        user_id=user_id,
        market_id=payload.market_id,
        outcome_id=payload.outcome_id,
        side=payload.side,
        amount=payload.amount,
        price=payload.price,
        remaining=payload.amount
    )
    db.add(order)
    await db.flush()
    return order

async def get_resting_orders(market_id: UUID, outcome_id: UUID, side: OrderSide, price: Decimal, db: AsyncSession):
    if side == OrderSide.BUY:
        other_side = OrderSide.SELL
        price_filter = Order.price <= price
        price_order = Order.price.asc()
    else:
        other_side = OrderSide.BUY
        price_filter = Order.price >= price
        price_order = Order.price.desc()

    result = await db.execute(
        select(Order).where(
            Order.market_id == market_id,
            Order.outcome_id == outcome_id,
            Order.side == other_side,
            Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL]),
            price_filter
        ).order_by(
            price_order, Order.created_at.asc()
        )
    )
    return list(result.scalars().all())

async def create_trade(market_id: UUID, outcome_id: UUID, buy_order_id: UUID, sell_order_id: UUID, amount: Decimal, price: Decimal, db: AsyncSession):
    trade = Trade(
        market_id=market_id,
        outcome_id=outcome_id,
        buy_order_id=buy_order_id,
        sell_order_id=sell_order_id,
        amount=amount,
        price=price
    )
    db.add(trade)
    await db.flush()

async def upsert_position(user_id: UUID, market_id: UUID, outcome_id: UUID, amount: Decimal, db: AsyncSession):
    result = await db.execute(
        select(Position).where(
            Position.user_id == user_id,
            Position.outcome_id == outcome_id
        )
    )
    position = result.scalar_one_or_none()
    if position:
        position.amount += amount
    else:
        position = Position(
            user_id=user_id,
            market_id=market_id,
            outcome_id=outcome_id,
            amount=amount
        )
        db.add(position)