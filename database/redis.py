from redis.asyncio import Redis

from config import db_settings

_redis = Redis(host=db_settings.REDIS_HOST, port=db_settings.REDIS_PORT, db=0)


async def add_jti_to_blacklist(jti: str, ttl_seconds: int) -> None:
    await _redis.set(f"blacklist:{jti}", "1", ex=ttl_seconds)


async def is_jti_blacklisted(jti: str) -> bool:
    return await _redis.exists(f"blacklist:{jti}") > 0


async def hit_rate_limit(key: str, window: int):
    async with _redis.pipeline(transaction=True) as pipe:
        pipe.incr(key)
        pipe.expire(key, window, nx=True)
        pipe.ttl(key)
        count, _, ttl = await pipe.execute()
    return count, ttl


async def close_redis() -> None:
    await _redis.aclose()
