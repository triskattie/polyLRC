from fastapi import FastAPI
import uvicorn
from src.api.routers import health

app = FastAPI()

app.include_router(health.router)


def main():
    uvicorn.run("main:app", host="0.0.0.0")

if __name__ == "__main__":
    main()