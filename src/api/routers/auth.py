from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from src.db.deps import get_db
from src.schemas.user import UserCreate
from src.core.security import generate_access_token, generate_refresh_token
from src.crud.user import create_user, create_refresh_token

router = APIRouter(prefix="/auth")

@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        with db.begin():
            new_user = create_user(db, user=user)
            if not new_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="email already registered"
                )
            access_token = generate_access_token(
                user_id=new_user.id,
                role=new_user.role
            )
            refresh_token, jti, expires_at = generate_refresh_token(user_id=new_user.id)
            create_refresh_token(db, user_id=new_user.id, token=refresh_token, jti=jti, expires_at=expires_at)
            tokens = {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
        return tokens
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="registration failed due to a server error"
        )