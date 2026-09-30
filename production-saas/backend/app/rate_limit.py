import time
from fastapi import HTTPException, Request
from redis import Redis
from app.core.config import settings
try: redis=Redis.from_url(settings.redis_url,decode_responses=True)
except Exception: redis=None
_local={}
def enforce_rate_limit(request:Request,limit=120,window=60):
 ident=request.client.host if request.client else "unknown"; bucket=int(time.time()//window); key=f"rl:{ident}:{bucket}"
 try:
  n=redis.incr(key); redis.expire(key,window+2)
 except Exception:
  now=time.time(); count,exp=_local.get(key,(0,now+window)); n=count+1; _local[key]=(n,exp)
 if n>limit: raise HTTPException(429,"Rate limit exceeded")
