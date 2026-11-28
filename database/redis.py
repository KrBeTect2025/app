"""
Redis helpers. Redis is a fast in-memory key/value store; here it holds two
kinds of short-lived data that would be wasteful to keep in PostgreSQL:

    blacklist:<jti>   tokens that were logged out (until they would expire)
    ratelimit:<ip>    how many requests an IP made in the current window

Keys get an expiry time, so Redis deletes them by itself when they're stale.
"""

from redis.asyncio import Redis

from config import db_settings

# One shared client for the whole app (it manages a connection pool itself).
# db=0 is Redis's default database number.
_redis = Redis(host=db_settings.REDIS_HOST, port=db_settings.REDIS_PORT, db=0)


async def add_jti_to_blacklist(jti: str, ttl_seconds: int) -> None:
    """Mark a token as logged out.

    A JWT can't be "deleted": it stays valid until it expires. So on logout we
    remember its unique id (jti) and reject it from then on. After ttl_seconds
    the token would be expired anyway, so Redis can forget it.
    """
    await _redis.set(f"blacklist:{jti}", "1", ex=ttl_seconds)


async def is_jti_blacklisted(jti: str) -> bool:
    """True if this token was logged out (see add_jti_to_blacklist)."""
    # exists() returns how many of the given keys exist: 0 or 1 here
    return await _redis.exists(f"blacklist:{jti}") > 0


async def hit_rate_limit(key: str, window: int):
    """Count one request for `key` and return (count, seconds_left_in_window).

    "Fixed window" rate limiting: the first request creates the counter with
    an expiry of `window` seconds; every request adds 1; when the key expires
    the count starts again from 0.
    """
    # A transaction pipeline sends the 3 commands together and runs them as
    # one step, so two requests at the same moment can't mix up the counter.
    async with _redis.pipeline(transaction=True) as pipe:
        pipe.incr(key)  # count += 1 (creates the key with 1 if missing)
        pipe.expire(key, window, nx=True)  # nx: only set expiry if none yet
        pipe.ttl(key)  # seconds until the key expires
        count, _, ttl = await pipe.execute()
    return count, ttl


async def close_redis() -> None:
    """Close the connection pool. Called on server shutdown (main.py)."""
    await _redis.aclose()
