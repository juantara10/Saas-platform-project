import time

from fastapi import HTTPException, Request
from redis import Redis

from app.core.config import settings


RATE_LIMIT = 120
RATE_LIMIT_WINDOW = 60

try:
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
except Exception:
    redis = None

_local = {}


def enforce_rate_limit(request: Request):
    ident = request.client.host if request.client else "unknown"
    bucket = int(time.time() // RATE_LIMIT_WINDOW)
    key = f"rl:{ident}:{bucket}"

    try:
        if redis is None:
            raise RuntimeError("Redis unavailable")

        n = redis.incr(key)
        redis.expire(key, RATE_LIMIT_WINDOW * 2)
    except Exception:
        now = time.time()
        count, exp = _local.get(key, (0, now + RATE_LIMIT_WINDOW))

        if now > exp:
            count = 0
            exp = now + RATE_LIMIT_WINDOW

        n = count + 1
        _local[key] = (n, exp)

    if n > RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
