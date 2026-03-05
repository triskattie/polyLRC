from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.wallet import get_wallet_by_user, get_balance, create_transaction
from src.core.errors import WalletNotFound, FaucetCooldown
from src.schemas.wallet import WalletResponse
from uuid import UUID
import os
from decimal import Decimal
from src.db.redis import redis_manager

FAUCET_AMOUNT = os.getenv("FAUCET_AMOUNT")

async def wallet_service(user_id: str, db: AsyncSession):
    wallet = await get_wallet_by_user(user_id=UUID(user_id), db=db)
    if not wallet:
        raise WalletNotFound()
    balance = await get_balance(wallet_id=wallet.id, db=db)
    return wallet.id, balance

async def faucet_service(user_id: str, db: AsyncSession):
    wallet = await get_wallet_by_user(user_id=UUID(user_id), db=db)
    if not wallet:
        raise WalletNotFound()
    if not await redis_manager.claim_faucet(user_id=wallet.user_id):
        raise FaucetCooldown()
    transaction = await create_transaction(wallet_id=wallet.id, amount=Decimal(FAUCET_AMOUNT), type="FAUCET", db=db)
    balance = await get_balance(wallet_id=wallet.id, db=db)
    return wallet.id, balance