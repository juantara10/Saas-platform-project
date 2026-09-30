from sqlalchemy import select
from app.db import SessionLocal
from app.models import User, Organization, Membership
from app.core.security import hash_password
from app.services import audit
def main():
 db=SessionLocal()
 try:
  if db.scalar(select(User).where(User.email=="demo@example.com")): print("Demo user already exists"); return
  u=User(email="demo@example.com",password_hash=hash_password("DemoPassword123!")); o=Organization(name="Acme Demo",slug="acme-demo"); db.add_all([u,o]); db.flush(); db.add(Membership(user_id=u.id,organization_id=o.id,role="owner")); audit(db,o.id,u.id,"seed.created"); db.commit(); print("Created demo@example.com / DemoPassword123!")
 finally: db.close()
if __name__=="__main__": main()
