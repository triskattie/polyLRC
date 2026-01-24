from src.db.models import User, RefreshToken
from src.schemas.user import UserCreate
from src.core.security import get_password_hash, generate_refresh_token, hash_token
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime


def create_user(db: Session, user: UserCreate):
    try:
        hashed_password = get_password_hash(user.password)
        obj = User(
            email=user.email.lower(),
            password_hash=hashed_password
        )
        db.add(obj)
        db.flush()
        return obj
    except IntegrityError:
        return None

def create_refresh_token(db: Session, user_id: uuid.UUID, token: str, jti: uuid.UUID, expires_at: datetime):
    db_token = RefreshToken(id=jti, user_id=user_id, token_hash=hash_token(token), expires_at=expires_at)
    db.add(db_token)
    return db_token