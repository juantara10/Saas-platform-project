import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User, Organization, Membership, ApiKey, AuditLog, Subscription, WebhookEvent
from app.schemas import *
from app.core.security import hash_password, verify_password, create_access_token, new_api_key
from app.core.config import settings
from app.deps import current_user, membership, require_role
from app.services import slugify, audit

router=APIRouter(prefix="/api/v1")

@router.post("/auth/register",response_model=TokenOut,status_code=201)
def register(body:RegisterIn,db:Session=Depends(get_db)):
 if db.scalar(select(User).where(User.email==body.email.lower())): raise HTTPException(409,"Email already registered")
 base=slugify(body.organization_name) or "team"; slug=base; i=1
 while db.scalar(select(Organization).where(Organization.slug==slug)): i+=1; slug=f"{base}-{i}"
 user=User(email=body.email.lower(),password_hash=hash_password(body.password)); org=Organization(name=body.organization_name,slug=slug)
 db.add_all([user,org]); db.flush(); db.add(Membership(user_id=user.id,organization_id=org.id,role="owner")); audit(db,org.id,user.id,"organization.created",{"name":org.name}); db.commit()
 return TokenOut(access_token=create_access_token(user.id))

@router.post("/auth/token",response_model=TokenOut)
def login(form:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
 user=db.scalar(select(User).where(User.email==form.username.lower()))
 if not user or not verify_password(form.password,user.password_hash): raise HTTPException(401,"Invalid email or password")
 return TokenOut(access_token=create_access_token(user.id))

@router.get("/users/me",response_model=UserOut)
def me(user:User=Depends(current_user)): return user

@router.get("/organizations",response_model=list[OrgOut])
def list_orgs(user:User=Depends(current_user),db:Session=Depends(get_db)):
 return list(db.scalars(select(Organization).join(Membership).where(Membership.user_id==user.id)))

@router.post("/organizations",response_model=OrgOut,status_code=201)
def create_org(body:OrgIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
 base=slugify(body.name); slug=base; i=1
 while db.scalar(select(Organization).where(Organization.slug==slug)): i+=1; slug=f"{base}-{i}"
 org=Organization(name=body.name,slug=slug); db.add(org); db.flush(); db.add(Membership(user_id=user.id,organization_id=org.id,role="owner")); audit(db,org.id,user.id,"organization.created"); db.commit(); db.refresh(org); return org

@router.get("/organizations/{org_id}/members",response_model=list[MemberOut])
def members(org_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 membership(org_id,user,db); rows=db.execute(select(Membership,User).join(User,User.id==Membership.user_id).where(Membership.organization_id==org_id)).all(); return [MemberOut(user_id=m.user_id,email=u.email,role=m.role) for m,u in rows]

@router.post("/organizations/{org_id}/members",response_model=MemberOut,status_code=201)
def add_member(org_id:str,body:MemberIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
 m=membership(org_id,user,db); require_role(m,"owner","admin")
 if body.role not in {"admin","member","viewer"}: raise HTTPException(422,"Invalid role")
 target=db.scalar(select(User).where(User.email==body.email.lower()))
 if not target: raise HTTPException(404,"User must register before being invited in this demo")
 if db.scalar(select(Membership).where(Membership.user_id==target.id,Membership.organization_id==org_id)): raise HTTPException(409,"Already a member")
 db.add(Membership(user_id=target.id,organization_id=org_id,role=body.role)); audit(db,org_id,user.id,"member.added",{"user_id":target.id,"role":body.role}); db.commit(); return MemberOut(user_id=target.id,email=target.email,role=body.role)

@router.post("/api-keys",response_model=ApiKeyCreated,status_code=201)
def create_key(body:ApiKeyIn,organization_id:str=Header(alias="X-Organization-ID"),user:User=Depends(current_user),db:Session=Depends(get_db)):
 m=membership(organization_id,user,db); require_role(m,"owner","admin"); raw,prefix,digest=new_api_key(); row=ApiKey(organization_id=organization_id,name=body.name,key_prefix=prefix,key_hash=digest); db.add(row); audit(db,organization_id,user.id,"api_key.created",{"name":body.name,"prefix":prefix}); db.commit(); return ApiKeyCreated(id=row.id,name=row.name,prefix=prefix,api_key=raw)

@router.get("/api-keys")
def list_keys(organization_id:str=Header(alias="X-Organization-ID"),user:User=Depends(current_user),db:Session=Depends(get_db)):
 membership(organization_id,user,db); return [{"id":x.id,"name":x.name,"prefix":x.key_prefix,"created_at":x.created_at} for x in db.scalars(select(ApiKey).where(ApiKey.organization_id==organization_id))]

@router.get("/audit-logs")
def logs(organization_id:str=Header(alias="X-Organization-ID"),user:User=Depends(current_user),db:Session=Depends(get_db)):
 m=membership(organization_id,user,db); require_role(m,"owner","admin"); rows=db.scalars(select(AuditLog).where(AuditLog.organization_id==organization_id).order_by(AuditLog.created_at.desc()).limit(100)); return [{"action":x.action,"metadata":x.metadata_json,"created_at":x.created_at} for x in rows]

@router.post("/billing/checkout")
def checkout(body:CheckoutIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
 m=membership(body.organization_id,user,db); require_role(m,"owner","admin")
 if not settings.stripe_secret_key or not settings.stripe_price_id: raise HTTPException(503,"Stripe is not configured")
 stripe.api_key=settings.stripe_secret_key
 session=stripe.checkout.Session.create(mode="subscription",line_items=[{"price":settings.stripe_price_id,"quantity":1}],success_url=f"{settings.frontend_url}/dashboard?checkout=success",cancel_url=f"{settings.frontend_url}/dashboard?checkout=cancelled",client_reference_id=body.organization_id,customer_email=user.email)
 return {"url":session.url}

@router.post("/billing/portal")
def portal(organization_id:str=Header(alias="X-Organization-ID"),user:User=Depends(current_user),db:Session=Depends(get_db)):
 m=membership(organization_id,user,db); require_role(m,"owner","admin"); sub=db.scalar(select(Subscription).where(Subscription.organization_id==organization_id))
 if not sub or not sub.stripe_customer_id: raise HTTPException(404,"No Stripe customer for organization")
 stripe.api_key=settings.stripe_secret_key; session=stripe.billing_portal.Session.create(customer=sub.stripe_customer_id,return_url=f"{settings.frontend_url}/dashboard"); return {"url":session.url}

@router.post("/webhooks/stripe",include_in_schema=True)
async def stripe_webhook(request:Request,stripe_signature:str=Header(alias="stripe-signature",default=""),db:Session=Depends(get_db)):
 if not settings.stripe_webhook_secret: raise HTTPException(503,"Stripe webhook not configured")
 payload=await request.body()
 try: event=stripe.Webhook.construct_event(payload,stripe_signature,settings.stripe_webhook_secret)
 except Exception as exc: raise HTTPException(400,f"Invalid webhook: {exc}")
 if db.get(WebhookEvent,event["id"]): return {"received":True,"duplicate":True}
 db.add(WebhookEvent(id=event["id"],event_type=event["type"])); obj=event["data"]["object"]
 if event["type"]=="checkout.session.completed" and obj.get("client_reference_id"):
  org_id=obj["client_reference_id"]; sub=db.scalar(select(Subscription).where(Subscription.organization_id==org_id)) or Subscription(organization_id=org_id,status="active"); sub.stripe_customer_id=obj.get("customer"); sub.stripe_subscription_id=obj.get("subscription"); sub.status="active"; db.add(sub); audit(db,org_id,None,"billing.checkout_completed")
 db.commit(); return {"received":True}
