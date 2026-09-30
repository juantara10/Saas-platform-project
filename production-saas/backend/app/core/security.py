import hashlib, secrets
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from app.core.config import settings
password_hash=PasswordHash.recommended()
def hash_password(p:str)->str: return password_hash.hash(p)
def verify_password(p:str,h:str)->bool: return password_hash.verify(p,h)
def create_access_token(user_id:str)->str:
 exp=datetime.now(timezone.utc)+timedelta(minutes=settings.access_token_minutes)
 return jwt.encode({"sub":user_id,"exp":exp},settings.jwt_secret,algorithm=settings.jwt_algorithm)
def decode_token(token:str)->str:
 return jwt.decode(token,settings.jwt_secret,algorithms=[settings.jwt_algorithm])["sub"]
def new_api_key():
 raw="atlas_"+secrets.token_urlsafe(32); return raw, raw[:14], hashlib.sha256(raw.encode()).hexdigest()
