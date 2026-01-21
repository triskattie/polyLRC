from fastapi import FastAPI
import uvicorn
from src.api.routers import health

app = FastAPI()

app.include_router(health.router)