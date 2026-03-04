from fastapi import APIRouter, Depends, HTTPException, status
from src.core.dependencies import get_current_user
from src.db.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.wallets import wallet_service
from src.core.errors import WalletNotFound

router = APIRouter(prefix="/wallet")

@router.get("")
async def wallet_endpoint(user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        async with db.begin():
            return wallet_service(user_id=user.user_id, db=db)
    except WalletNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="wallet not found"
        )