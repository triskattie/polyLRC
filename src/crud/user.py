from src.db.models import User, RefreshToken
from src.core.security import get_password_hash, generate_refresh_token, hash_token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
from sqlalchemy import select


async def create_user(db: AsyncSession, email: str, password: str):
    try:
        hashed_password = get_password_hash(password)
        obj = User(
            email=email.lower(),
            password_hash=hashed_password
        )
        db.add(obj)
        await db.flush()
        return obj
    except IntegrityError:
        return None

async def create_refresh_token(db: AsyncSession, user_id: uuid.UUID, token: str, jti: uuid.UUID, expires_at: datetime):
    db_token = RefreshToken(id=jti, user_id=user_id, token_hash=hash_token(token), expires_at=expires_at)
    db.add(db_token)
    await db.flush()
    return db_token

async def get_user_by_email(db: AsyncSession, email):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_uuid(db: AsyncSession, user_id: uuid.UUID):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def get_refresh_token_by_hash(db: AsyncSession, refresh_token_hash):
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == refresh_token_hash))
    return result.scalar_one_or_none()

async def revoke_refresh_token(db: AsyncSession, token: RefreshToken):
    token.revoked = True
    await db.flush()
