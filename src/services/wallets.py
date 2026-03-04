from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.wallet import get_wallet_by_user, get_balance
from src.core.errors import WalletNotFound
from src.schemas.wallet import WalletResponse

async def wallet_service(user_id: str, db: AsyncSession):
    wallet = get_wallet_by_user(user_id=UUID(user_id), db=db)
    if not wallet:
        raise WalletNotFound()
    balance = get_balance(wallet_id=wallet.id, db=db)
    return WalletResponse(
        user_id=user_id,
        balance=balance
    )
