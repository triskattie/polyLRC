import bcrypt
from jose import jwt
from datetime import datetime, timedelta, timezone
import uuid
import os
import hashlib

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET_KEY = os.getenv("SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

def get_password_hash(password): 
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

def generate_access_token(user_id: uuid.UUID, role: str):
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "iat": datetime.now(tz=timezone.utc),
        "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def generate_refresh_token(user_id: uuid.UUID, token_id: uuid.UUID | None = None):
    jti = token_id or uuid.uuid4()

    expires_at = (datetime.now(tz=timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    payload = {
        "sub": str(user_id),
        "jti": str(jti),
        "type": "refresh",
        "iat": datetime.now(tz=timezone.utc),
        "exp": expires_at,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token, jti, expires_at

def decode_jwt(token):
    return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM],)

def hash_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()

def check_password(password, password_hash):
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

def refresh_token_valid(refresh_token):
    refresh_token_hash = hash_token(refresh_token)
