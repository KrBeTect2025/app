import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError

from ..database.redis import hit_rate_limit

logger = logging.getLogger(__name__)


LIMIT = 5
WINDOW = 60


async def rate_limiter(request: Request, call_next):
    ip = request.client.host if request.client else "unknown"
    key = f"ratelimit:{ip}"
    try:
        count, ttl = await hit_rate_limit(key, WINDOW)

    except RedisError:
        logger.warning("Redis Unavaialble , skipping rate limit")
        return await call_next(request)

    if count > LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"},
            headers={
                "Retry-After": str(max(ttl, 1)),
                "X-RateLimit-Limit": str(LIMIT),
                "X-RateLimit-Remaining": "0",
            },
        )

    response = await call_next(request)

    response.headers["X-RateLimit-Limit"] = str(LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(LIMIT - count)
    return response
