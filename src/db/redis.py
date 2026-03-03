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

    async def store_access_token(self, jti: str, user_id: str, expires_minutes: int):
        key = f"access:{jti}"
        await self.redis_pool.setex(key, expires_minutes * 60, str(user_id))

    async def revoke_access_token(self, jti: str):
        key = f"access:{jti}"
        await self.redis_pool.delete(key)

    async def is_access_token(self, jti: str):
        key = f"access:{jti}"
        return await self.redis_pool.exists(key) > 0

redis_manager = RedisManager()