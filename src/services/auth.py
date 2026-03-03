from sqlalchemy.orm import Session
from src.crud.user import create_user, create_refresh_token, get_user_by_email, get_user_by_uuid, get_refresh_token_by_hash
from src.core.security import generate_access_token, generate_refresh_token, check_password, decode_jwt, hash_token
from src.core.errors import EmailAlreadyExists, InvalidLogin, InvalidRefreshToken
from datetime import datetime, timezone
from uuid import UUID

def register_user_service(db: Session, email: str, password: str):
    new_user = create_user(db, email=email, password=password)
    if not new_user:
        raise EmailAlreadyExists()
    access_token = generate_access_token(
        user_id=new_user.id,
        role=new_user.role
    )
    refresh_token, jti, expires_at = generate_refresh_token(user_id=new_user.id)
    create_refresh_token(db, user_id=new_user.id, token=refresh_token, jti=jti, expires_at=expires_at)
    return access_token, refresh_token

def login_user_service(db: Session, email: str, password: str):
    db_user = get_user_by_email(db, email.lower())
    if not db_user:
        raise InvalidLogin()
    
    if not check_password(password, db_user.password_hash):
        raise InvalidLogin()

    access_token = generate_access_token(
        user_id=db_user.id,
        role=db_user.role
    )
    refresh_token, jti, expires_at = generate_refresh_token(user_id=db_user.id)
    create_refresh_token(db, db_user.id, token=refresh_token, jti=jti, expires_at=expires_at)
    return access_token, refresh_token

def refresh_service(db: Session, refresh_token: str):
    try:
        payload = decode_jwt(refresh_token)
    except JWTError:
        raise InvalidRefreshToken()

    if payload.get("type") != "refresh":
        raise InvalidRefreshToken()

    token_hash = hash_token(refresh_token)
    db_token = get_refresh_token_by_hash(db=db, refresh_token_hash=token_hash)

    if not db_token:
        raise InvalidRefreshToken()

    now = datetime.utcnow()
    if db_token.revoked:
        raise InvalidRefreshToken()

    if db_token.expires_at <= now:
        raise InvalidRefreshToken()

    if UUID(payload["sub"]) != db_token.user_id:
        raise InvalidRefreshToken()

    # Start the token cycle
    db_token.revoked = True
    user = get_user_by_uuid(db, user_id=UUID(payload["sub"]))
    if not user:
        raise InvalidRefreshToken()
    user_id = user.id
    new_access = generate_access_token(user_id=db_token.user_id, role=user.role)
    refresh_token, jti, expires_at = generate_refresh_token(user_id=user_id)
    create_refresh_token(db, user_id=user_id, token=refresh_token, jti=jti, expires_at=expires_at)
    return new_access, refresh_token