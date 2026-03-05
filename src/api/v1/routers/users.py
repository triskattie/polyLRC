from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.deps import get_db
from src.schemas.user import UserResponse
from src.core.security import oauth2_scheme
from src.services.auth_validation import get_current_user_service
from src.core.errors import InvalidAccessToken


router = APIRouter(prefix="/users", tags=["v1:Users"])

@router.get("/me", response_model=UserResponse)
async def get_me(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        user = await get_current_user_service(db=db, token=token)
        return user
    except InvalidAccessToken:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )