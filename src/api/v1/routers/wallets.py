from fastapi import APIRouter, Depends, HTTPException, status
from src.core.dependencies import get_current_user
from src.db.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.wallets import wallet_service, faucet_service
from src.core.errors import WalletNotFound

router = APIRouter(prefix="/wallet", tags=["v1:Wallets"])

@router.get("")
async def wallet_endpoint(user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        return await wallet_service(user_id=user.user_id, db=db)
    except WalletNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="wallet not found"
        )

@router.post("/faucet")
async def faucet_endpoint(user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        async with db.begin():
            transaction = await faucet_service(user_id=user.user_id, db=db)
        return transaction.id
    except WalletNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="wallet not found"
        )