from redis.asyncio import Redis

from config import db_settings

_token_blacklist = Redis(host=db_settings.REDIS_HOST, port=db_settings.REDIS_PORT, db=0)


async def add_jti_to_blacklist(jti: str, ttl_seconds: int) -> None:
    await _token_blacklist.set(f"blacklist:{jti}", "1", ex=ttl_seconds)


async def is_jti_blacklisted(jti: str) -> bool:
    return await _token_blacklist.exists(f"blacklist:{jti}") > 0
