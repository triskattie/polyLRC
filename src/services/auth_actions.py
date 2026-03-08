from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.user import create_user, create_refresh_token, get_user_by_email, get_user_by_uuid, get_refresh_token_by_hash
from src.core.security import generate_access_token, generate_refresh_token, check_password, decode_jwt, hash_token
from src.core.errors import EmailAlreadyExists, InvalidLogin, InvalidRefreshToken
from datetime import datetime, timezone
from uuid import UUID
from src.db.redis import redis_manager
import os
from src.crud.wallet import create_wallet
from jose import JWTError


ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

async def register_user_service(db: AsyncSession, email: str, password: str):
    new_user = await create_user(db, email=email, password=password)
    if not new_user:
        raise EmailAlreadyExists()

    await create_wallet(user_id=new_user.id, db=db)
    
    access_token, a_jti = generate_access_token(
        user_id=new_user.id,
        role=new_user.role
    )
    await redis_manager.store_access_token(jti=a_jti, user_id=new_user.id, expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token, jti, expires_at = generate_refresh_token(user_id=new_user.id)
    await create_refresh_token(db, user_id=new_user.id, token=refresh_token, jti=jti, expires_at=expires_at)
    return access_token, refresh_token

async def login_user_service(db: AsyncSession, email: str, password: str):
    db_user = await get_user_by_email(db, email.lower())
    if not db_user:
        raise InvalidLogin()
    
    if not check_password(password, db_user.password_hash):
        raise InvalidLogin()

    access_token, a_jti = generate_access_token(
        user_id=db_user.id,
        role=db_user.role
    )
    await redis_manager.store_access_token(jti=a_jti, user_id=db_user.id, expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token, jti, expires_at = generate_refresh_token(user_id=db_user.id)
    await create_refresh_token(db, db_user.id, token=refresh_token, jti=jti, expires_at=expires_at)
    return access_token, refresh_token

async def refresh_service(db: AsyncSession, refresh_token: str):
    try:
        payload = decode_jwt(refresh_token)
    except JWTError:
        raise InvalidRefreshToken()

    if payload.get("type") != "refresh":
        raise InvalidRefreshToken()

    token_hash = hash_token(refresh_token)
    db_token = await get_refresh_token_by_hash(db=db, refresh_token_hash=token_hash)

    if not db_token:
        raise InvalidRefreshToken()

    now = datetime.now(tz=timezone.utc)
    if db_token.revoked:
        raise InvalidRefreshToken()

    expires_at = db_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= now:
        raise InvalidRefreshToken()

    if UUID(payload["sub"]) != db_token.user_id:
        raise InvalidRefreshToken()

    # Start the token cycle
    db_token.revoked = True
    user = await get_user_by_uuid(db, user_id=UUID(payload["sub"]))
    if not user:
        raise InvalidRefreshToken()
    user_id = user.id
    new_access, a_jti = generate_access_token(user_id=db_token.user_id, role=user.role)
    await redis_manager.store_access_token(jti=a_jti, user_id=user_id, expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token, jti, expires_at = generate_refresh_token(user_id=user_id)
    await create_refresh_token(db, user_id=user_id, token=refresh_token, jti=jti, expires_at=expires_at)
    return new_access, refresh_token