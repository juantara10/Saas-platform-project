import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base
def uid(): return str(uuid.uuid4())
def now(): return datetime.now(timezone.utc)
class User(Base):
 __tablename__="users"
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 email:Mapped[str]=mapped_column(String(320),unique=True,index=True)
 password_hash:Mapped[str]=mapped_column(String(255))
 is_active:Mapped[bool]=mapped_column(Boolean,default=True)
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Organization(Base):
 __tablename__="organizations"
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 name:Mapped[str]=mapped_column(String(120))
 slug:Mapped[str]=mapped_column(String(120),unique=True,index=True)
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Membership(Base):
 __tablename__="memberships"; __table_args__=(UniqueConstraint("user_id","organization_id"),)
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 user_id:Mapped[str]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),index=True)
 organization_id:Mapped[str]=mapped_column(ForeignKey("organizations.id",ondelete="CASCADE"),index=True)
 role:Mapped[str]=mapped_column(String(20),default="member")
class Subscription(Base):
 __tablename__="subscriptions"
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 organization_id:Mapped[str]=mapped_column(ForeignKey("organizations.id",ondelete="CASCADE"),unique=True,index=True)
 stripe_customer_id:Mapped[str|None]=mapped_column(String(120),nullable=True)
 stripe_subscription_id:Mapped[str|None]=mapped_column(String(120),nullable=True)
 status:Mapped[str]=mapped_column(String(40),default="inactive")
 price_id:Mapped[str|None]=mapped_column(String(120),nullable=True)
class ApiKey(Base):
 __tablename__="api_keys"
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 organization_id:Mapped[str]=mapped_column(ForeignKey("organizations.id",ondelete="CASCADE"),index=True)
 name:Mapped[str]=mapped_column(String(100))
 key_prefix:Mapped[str]=mapped_column(String(20))
 key_hash:Mapped[str]=mapped_column(String(64),unique=True,index=True)
 last_used_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class AuditLog(Base):
 __tablename__="audit_logs"
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 organization_id:Mapped[str]=mapped_column(ForeignKey("organizations.id",ondelete="CASCADE"),index=True)
 actor_user_id:Mapped[str|None]=mapped_column(ForeignKey("users.id",ondelete="SET NULL"),nullable=True)
 action:Mapped[str]=mapped_column(String(120),index=True)
 metadata_json:Mapped[dict]=mapped_column(JSON,default=dict)
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,index=True)
class WebhookEvent(Base):
 __tablename__="webhook_events"
 id:Mapped[str]=mapped_column(String(120),primary_key=True)
 event_type:Mapped[str]=mapped_column(String(120))
 processed_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
