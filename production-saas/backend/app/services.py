import re
from app.models import AuditLog
def slugify(s:str): return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")
def audit(db,org_id,actor_id,action,metadata=None):
 db.add(AuditLog(organization_id=org_id,actor_user_id=actor_id,action=action,metadata_json=metadata or {}))
