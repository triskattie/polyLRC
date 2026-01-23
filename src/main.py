from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api.routers import routers
from src.db.redis import redis_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    yield
    await redis_manager.disconnect()

app = FastAPI(lifespan=lifespan)

@app.get("/hit")
async def root():
    hits = await redis_manager.redis_pool.incr("hits")
    return {"message": f"This page has been viewed {hits} times"}

for router in routers:
    app.include_router(router)