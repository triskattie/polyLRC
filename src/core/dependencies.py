from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.deps import get_db
from src.core.security import oauth2_scheme
from src.services.auth_validation import get_current_user_service
from src.core.errors import InvalidAccessToken
from src.db.session import SessionLocal


async def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    try:
        async with SessionLocal() as db:
            return await get_current_user_service(db, token)
    except InvalidAccessToken:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )