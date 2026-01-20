from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class HealthCheck(BaseModel):
    status: str = "OK"

@app.get("/health")
async def healthcheck():
    return HealthCheck(status="OK")


def main():
    uvicorn.run("main:app", host="0.0.0.0")

if __name__ == "__main__":
    main()