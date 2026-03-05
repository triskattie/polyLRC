from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from src.db.deps import get_db
from src.schemas.user import UserCreate, UserLogin
from src.schemas.auth import TokenResponse, RefreshRequest
from src.core.security import decode_jwt
from src.services.auth_actions import register_user_service, login_user_service, refresh_service
from src.core.errors import EmailAlreadyExists, InvalidLogin, InvalidRefreshToken


router = APIRouter(prefix="/auth", tags=["v1:Authentication"])

@router.post("/register", response_model=TokenResponse)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        async with db.begin():
            access, refresh = await register_user_service(db, email=payload.email, password=payload.password)
        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            token_type="bearer"
        )
    except EmailAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email already registered"
        )



@router.post("/login", response_model=TokenResponse)
async def login_user(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    try:
        async with db.begin():
            access, refresh = await login_user_service(db, email=payload.email, password=payload.password)
        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            token_type="bearer"
        )
    except InvalidLogin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid login details"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:       
        async with db.begin():
            access, refresh = await refresh_service(db=db, refresh_token=payload.refresh_token)
        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            token_type="bearer"
        )
    except InvalidRefreshToken:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid refresh token"
        )