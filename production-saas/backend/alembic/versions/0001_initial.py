"""initial schema"""
from alembic import op
import sqlalchemy as sa
revision="0001"; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
 op.create_table("users",sa.Column("id",sa.String(36),primary_key=True),sa.Column("email",sa.String(320),nullable=False,unique=True),sa.Column("password_hash",sa.String(255),nullable=False),sa.Column("is_active",sa.Boolean(),nullable=False,server_default=sa.true()),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
 op.create_table("organizations",sa.Column("id",sa.String(36),primary_key=True),sa.Column("name",sa.String(120),nullable=False),sa.Column("slug",sa.String(120),nullable=False,unique=True),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
 op.create_table("memberships",sa.Column("id",sa.String(36),primary_key=True),sa.Column("user_id",sa.String(36),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),sa.Column("organization_id",sa.String(36),sa.ForeignKey("organizations.id",ondelete="CASCADE"),nullable=False),sa.Column("role",sa.String(20),nullable=False),sa.UniqueConstraint("user_id","organization_id"))
 op.create_table("subscriptions",sa.Column("id",sa.String(36),primary_key=True),sa.Column("organization_id",sa.String(36),sa.ForeignKey("organizations.id",ondelete="CASCADE"),nullable=False,unique=True),sa.Column("stripe_customer_id",sa.String(120)),sa.Column("stripe_subscription_id",sa.String(120)),sa.Column("status",sa.String(40),nullable=False),sa.Column("price_id",sa.String(120)))
 op.create_table("api_keys",sa.Column("id",sa.String(36),primary_key=True),sa.Column("organization_id",sa.String(36),sa.ForeignKey("organizations.id",ondelete="CASCADE"),nullable=False),sa.Column("name",sa.String(100),nullable=False),sa.Column("key_prefix",sa.String(20),nullable=False),sa.Column("key_hash",sa.String(64),nullable=False,unique=True),sa.Column("last_used_at",sa.DateTime(timezone=True)),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
 op.create_table("audit_logs",sa.Column("id",sa.String(36),primary_key=True),sa.Column("organization_id",sa.String(36),sa.ForeignKey("organizations.id",ondelete="CASCADE"),nullable=False),sa.Column("actor_user_id",sa.String(36),sa.ForeignKey("users.id",ondelete="SET NULL")),sa.Column("action",sa.String(120),nullable=False),sa.Column("metadata_json",sa.JSON(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
 op.create_table("webhook_events",sa.Column("id",sa.String(120),primary_key=True),sa.Column("event_type",sa.String(120),nullable=False),sa.Column("processed_at",sa.DateTime(timezone=True),nullable=False))
def downgrade():
 for t in ["webhook_events","audit_logs","api_keys","subscriptions","memberships","organizations","users"]: op.drop_table(t)
