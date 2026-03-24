from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api.v1 import router as v1router
from src.db.redis import redis_manager
from fastapi.middleware.cors import CORSMiddleware

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

app.include_router(v1router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.2.36:3000", "https://polylrc.triskattie.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)