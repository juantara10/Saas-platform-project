from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api import router
from app.core.config import settings
from app.db import get_db
from app.rate_limit import enforce_rate_limit
from app.observability import setup
app=FastAPI(title=settings.app_name,version="1.0.0",description="Production-grade multi-tenant SaaS API",dependencies=[Depends(enforce_rate_limit)])
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(router)
@app.get("/health",tags=["operations"] )
def health(): return {"status":"ok","service":settings.app_name}
@app.get("/ready",tags=["operations"] )
def ready(db:Session=Depends(get_db)): db.execute(text("SELECT 1")); return {"status":"ready"}
setup(app)
