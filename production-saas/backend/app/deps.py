from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User, Membership
from app.core.security import decode_token
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
def current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
 try: uid=decode_token(token)
 except Exception: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
 user=db.get(User,uid)
 if not user or not user.is_active: raise HTTPException(401,"Inactive or missing user")
 return user
def membership(org_id:str,user:User,db:Session):
 m=db.scalar(select(Membership).where(Membership.organization_id==org_id,Membership.user_id==user.id))
 if not m: raise HTTPException(403,"Not a member of this organization")
 return m
def require_role(m:Membership,*roles):
 if m.role not in roles: raise HTTPException(403,"Insufficient role")
