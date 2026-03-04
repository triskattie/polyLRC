from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.wallet import get_wallet_by_user, get_balance, create_transaction
from src.core.errors import WalletNotFound
from src.schemas.wallet import WalletResponse
from uuid import UUID
import os
from decimal import Decimal

FAUCET_AMOUNT = os.getenv("FAUCET_AMOUNT")

async def wallet_service(user_id: str, db: AsyncSession):
    wallet = await get_wallet_by_user(user_id=UUID(user_id), db=db)
    if not wallet:
        raise WalletNotFound()
    balance = await get_balance(wallet_id=wallet.id, db=db)
    return WalletResponse(
        user_id=user_id,
        balance=balance
    )

async def faucet_service(user_id: str, db: AsyncSession):
    wallet = await get_wallet_by_user(user_id=UUID(user_id), db=db)
    if not wallet:
        raise WalletNotFound()
    transaction = await create_transaction(wallet_id=wallet.id, amount=Decimal(FAUCET_AMOUNT), type="FAUCET", db=db)
    return transaction