from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
 app_name:str="Atlas SaaS"
 environment:str="development"
 database_url:str="sqlite:///./atlas.db"
 redis_url:str="redis://localhost:6379/0"
 jwt_secret:str="development-only-secret-change-me"
 jwt_algorithm:str="HS256"
 access_token_minutes:int=30
 cors_origins:str="http://localhost:3000"
 stripe_secret_key:str=""
 stripe_webhook_secret:str=""
 stripe_price_id:str=""
 frontend_url:str="http://localhost:3000"
 otel_exporter_otlp_endpoint:str=""
 model_config=SettingsConfigDict(env_file="../.env",extra="ignore")
 @property
 def cors_list(self): return [x.strip() for x in self.cors_origins.split(",") if x.strip()]
@lru_cache
def get_settings(): return Settings()
settings=get_settings()
