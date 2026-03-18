from src.schemas.order import OrderInput
from src.crud.market import get_market_by_id
from src.core.errors import MarketNotFound, MarketNotOpen, InsufficientFunds, OrderNotFound, OrderAccessDenied, OutcomeNotInMarket
from src.db.models import MarketState, OrderSide, Order, TransactionType, OrderStatus
from src.crud.wallet import get_balance, get_wallet_by_user, create_transaction
from src.crud.order import get_resting_orders, upsert_position, create_trade, create_order, get_order_by_id
from decimal import Decimal
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

async def create_order_service(payload: OrderInput, user_id: UUID, db: AsyncSession):
    market = await get_market_by_id(market_id=payload.market_id, db=db)
    if not market:
        raise MarketNotFound()
    if market.state != MarketState.OPEN:
        raise MarketNotOpen()
    if payload.outcome_id not in [o.id for o in market.outcomes]:
        raise OutcomeNotInMarket()

    wallet = await get_wallet_by_user(user_id=user_id, db=db)
    balance = await get_balance(wallet_id=wallet.id, db=db)

    if payload.side == OrderSide.BUY:
        collateral = payload.amount * payload.price
    else:
        collateral = payload.amount * (Decimal("1") - payload.price)

    if (balance or Decimal("0")) < collateral:
        raise InsufficientFunds()

    await create_transaction(
        db=db,
        wallet_id=wallet.id,
        amount=-collateral,
        type=TransactionType.TRADE,
        related_market_id=payload.market_id
    )

    order = await create_order(payload=payload, user_id=user_id, db=db)
    await _matching_engine(order=order, db=db)
    return order


async def _matching_engine(order: Order, db: AsyncSession):
    makers = await get_resting_orders(
        market_id=order.market_id,
        outcome_id=order.outcome_id,
        side=order.side,
        price=order.price,
        db=db
    )
    incoming_wallet = await get_wallet_by_user(user_id=order.user_id, db=db)

    for maker in makers:
        if order.remaining <= 0:
            break

        maker_wallet = await get_wallet_by_user(user_id=maker.user_id, db=db)
        fill_amount = min(order.remaining, maker.remaining)
        trade_value = maker.price * fill_amount

        if order.side == OrderSide.BUY:
            buy_order_id = order.id
            sell_order_id = maker.id
            refund = (order.price - maker.price) * fill_amount
            if refund > 0:
                await create_transaction(db=db, wallet_id=incoming_wallet.id, amount=refund, type=TransactionType.TRADE, related_market_id=order.market_id)
            await create_transaction(db=db, wallet_id=maker_wallet.id, amount=trade_value, type=TransactionType.TRADE, related_market_id=order.market_id)
            await upsert_position(user_id=order.user_id, market_id=order.market_id, outcome_id=order.outcome_id, amount=fill_amount, db=db)
            await upsert_position(user_id=maker.user_id, market_id=order.market_id, outcome_id=order.outcome_id, amount=-fill_amount, db=db)
        else:
            buy_order_id = maker.id
            sell_order_id = order.id
            await create_transaction(db=db, wallet_id=incoming_wallet.id, amount=trade_value, type=TransactionType.TRADE, related_market_id=order.market_id)
            await upsert_position(user_id=maker.user_id, market_id=order.market_id, outcome_id=order.outcome_id, amount=fill_amount, db=db)
            await upsert_position(user_id=order.user_id, market_id=order.market_id, outcome_id=order.outcome_id, amount=-fill_amount, db=db)

        await create_trade(
            market_id=order.market_id,
            outcome_id=order.outcome_id,
            buy_order_id=buy_order_id,
            sell_order_id=sell_order_id,
            amount=fill_amount,
            price=maker.price,
            db=db
        )

        order.remaining -= fill_amount
        maker.remaining -= fill_amount
        _update_status(order)
        _update_status(maker)

    await db.flush()


def _update_status(order: Order):
    if order.remaining <= 0:
        order.status = OrderStatus.FILLED
    elif order.remaining < order.amount:
        order.status = OrderStatus.PARTIAL

async def get_order_service(order_id: UUID, user_id: UUID, db: AsyncSession):
    order = await get_order_by_id(order_id=order_id, db=db)
    if not order:
        raise OrderNotFound()
    if order.user_id != user_id:
        raise OrderAccessDenied()
    return order