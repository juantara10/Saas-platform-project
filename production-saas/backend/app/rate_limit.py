import time

from fastapi import HTTPException, Request
from redis import Redis

from app.core.config import settings

try:
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
except Exception:
    redis = None

_local = {}


def enforce_rate_limit(request: Request, limit: int = 120, window: int = 60):
    # CORS preflight requests must pass through without rate limiting.
    if request.method == "OPTIONS":
        return

    ident = request.client.host if request.client else "unknown"
    bucket = int(time.time() // window)
    key = f"rl:{ident}:{bucket}"

    try:
        if redis is None:
            raise RuntimeError("Redis unavailable")

        n = redis.incr(key)
        redis.expire(key, window + 2)

    except Exception:
        now = time.time()
        count, exp = _local.get(key, (0, now + window))

        if now >= exp:
            count = 0
            exp = now + window

        n = count + 1
        _local[key] = (n, exp)

    if n > limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
