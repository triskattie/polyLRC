from jose import JWTError
from uuid import UUID
from src.core.security import decode_jwt
from src.crud.user import get_user_by_uuid
from src.db.redis import redis_manager
from src.core.errors import InvalidAccessToken
from src.schemas.user import UserResponse


async def get_current_user_service(db, token: str):
    try:
        payload = decode_jwt(token)
    except JWTError:
        raise InvalidAccessToken()

    if payload.get("type") != "access":
        raise InvalidAccessToken()

    jti = payload.get("jti")
    user_id = payload.get("sub")

    if not jti or not user_id:
        raise InvalidAccessToken()

    token_exists = await redis_manager.is_access_token(jti=jti)
    if not token_exists:
        raise InvalidAccessToken()

    user = await get_user_by_uuid(db, UUID(user_id))
    if not user:
        raise InvalidAccessToken()

    user_response = UserResponse(
        user_id=user.id,
        email=user.email,
        role=user.role,
        created_at=user.created_at
    )

    return user_response