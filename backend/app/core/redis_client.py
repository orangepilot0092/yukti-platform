import os
import redis.asyncio as aioredis

# Enterprise-grade Redis client with explicit high-concurrency pooling
redis_client = aioredis.from_url(
    os.getenv("REDIS_URL", "redis://redis:6379"),
    encoding="utf-8",
    decode_responses=True,
    max_connections=5000,
    socket_keepalive=True,
    socket_keepalive_options={},
    retry_on_timeout=True
)
