from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.deps import get_db

router = APIRouter(prefix="/health", tags=["v1:Health"])

@router.get("")
async def health():
    return {"status": "ok"}

@router.get("/db")
async def db_health(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status": "ok"}