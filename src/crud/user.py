from src.db.models import User, RefreshToken
from src.core.security import get_password_hash, generate_refresh_token, hash_token
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime


def create_user(db: Session, email: str, password: str):
    try:
        hashed_password = get_password_hash(password)
        obj = User(
            email=email.lower(),
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

def get_user_by_email(db: Session, email):
    return db.query(User).filter(User.email == email).first()

def get_user_by_uuid(db: Session, user_id: uuid.UUID):
    return db.query(User).filter(User.id == user_id).first()

def get_refresh_token_by_hash(db: Session, refresh_token_hash):
    return db.query(RefreshToken).filter(RefreshToken.token_hash == refresh_token_hash).first()

def revoke_refresh_token(db: Session, token: RefreshToken):
    token.revoked = True
