from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.db.deps import get_db

router = APIRouter(prefix="/health")

@router.get("")
def health():
    return {"status": "ok"}

@router.get("/db")
def db_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}