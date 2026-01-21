import redis.asyncio as redis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

class RedisManager:
    def __init__(self):
        self.redis_pool = None
    
    async def connect(self):
        self.redis_pool = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

    async def disconnect(self):
        if self.redis_pool:
            await self.redis_pool.close()

redis_manager = RedisManager()