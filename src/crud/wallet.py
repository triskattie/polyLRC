from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import Wallet, WalletTransaction
from uuid import UUID
from sqlalchemy import select, func

async def get_wallet_by_user(user_id: UUID, db: AsyncSession):
    result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    return result.scalar_one_or_none()

async def get_balance(wallet_id: UUID, db: AsyncSession):
    result = await db.execute(select(func.sum(WalletTransaction.amount)).where(WalletTransaction.wallet_id == wallet_id))
    return result.scalar_one()

async def create_wallet(user_id: UUID, db: AsyncSession):
    wallet = Wallet(user_id=user_id)
    db.add(wallet)
    await db.flush()