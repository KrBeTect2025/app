"""
Rate limiting middleware: at most LIMIT requests per IP address every
WINDOW seconds. Request number LIMIT + 1 gets "429 Too Many Requests".

A middleware wraps EVERY request: code before `call_next` runs before the
route, code after it runs on the way back out. It's registered in main.py.
The counting itself happens in Redis (database/redis.py: hit_rate_limit).
"""

import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from database.redis import hit_rate_limit
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


LIMIT = 5  # requests allowed...
WINDOW = 60  # ...per this many seconds


async def rate_limiter(request: Request, call_next):
    # Who is calling? (request.client can be None, e.g. in some test clients)
    ip = request.client.host if request.client else "unknown"
    key = f"ratelimit:{ip}"
    try:
        count, ttl = await hit_rate_limit(key, WINDOW)

    except RedisError:
        # "Fail open": if Redis is down, let requests through rather than
        # taking the whole API down with it.
        logger.warning("Redis Unavaialble , skipping rate limit")
        return await call_next(request)

    if count > LIMIT:
        # Stop here: the route never runs
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"},
            headers={
                # Standard header: how many seconds until the client may retry
                "Retry-After": str(max(ttl, 1)),
                "X-RateLimit-Limit": str(LIMIT),
                "X-RateLimit-Remaining": "0",
            },
        )

    # Under the limit: run the route and get its response
    response = await call_next(request)

    # Tell the client how much of its limit is left
    response.headers["X-RateLimit-Limit"] = str(LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(LIMIT - count)
    return response
