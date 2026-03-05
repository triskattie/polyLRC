from fastapi import APIRouter, Depends, HTTPException, status
from src.core.dependencies import get_current_user
from src.db.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.wallets import wallet_service, faucet_service
from src.core.errors import WalletNotFound
from src.schemas.wallet import WalletResponse

router = APIRouter(prefix="/wallet", tags=["v1:Wallets"])

@router.get("", response_model=WalletResponse)
async def wallet_endpoint(user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        wallet_id, balance = await wallet_service(user_id=user.user_id, db=db)
        return WalletResponse(
            wallet_id=wallet_id,
            balance=balance
        )
    except WalletNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="wallet not found"
        )

@router.post("/faucet", response_model=WalletResponse)
async def faucet_endpoint(user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        async with db.begin():
            wallet_id, balance = await faucet_service(user_id=user.user_id, db=db)
        return WalletResponse(
            wallet_id=wallet_id,
            balance=balance
        )
    except WalletNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="wallet not found"
        )