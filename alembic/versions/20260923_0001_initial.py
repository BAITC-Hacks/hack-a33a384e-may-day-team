"""Initial Career Quest storage."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260923_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dataset_state",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("dataset_name", sa.String(length=128), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("as_of_date", sa.Date(), nullable=False),
    )
    op.create_table(
        "employees",
        sa.Column("employee_id", sa.String(length=64), primary_key=True),
        sa.Column("source", sa.String(length=16), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
    )
    op.create_table(
        "activity_history",
        sa.Column("record_id", sa.String(length=64), primary_key=True),
        sa.Column("employee_id", sa.String(length=64), sa.ForeignKey("employees.employee_id"), nullable=False),
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("activity_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("completion_pct", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("feedback_rating", sa.Integer(), nullable=True),
        sa.Column("assigned_by", sa.String(length=16), nullable=False),
        sa.Column("source_row", sa.Integer(), nullable=False),
        sa.Column("origin", sa.String(length=16), nullable=False),
        sa.Column("counts_in_replay", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_activity_history_employee_id", "activity_history", ["employee_id"])
    op.create_index("ix_activity_history_event_id", "activity_history", ["event_id"])
    op.create_table(
        "accounts",
        sa.Column("username", sa.String(length=128), primary_key=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("employee_id", sa.String(length=64), sa.ForeignKey("employees.employee_id"), nullable=True),
    )
    op.create_table(
        "sessions",
        sa.Column("token_hash", sa.String(length=64), primary_key=True),
        sa.Column("username", sa.String(length=128), sa.ForeignKey("accounts.username"), nullable=False),
        sa.Column("csrf_token", sa.String(length=128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sessions_username", "sessions", ["username"])
    op.create_table(
        "idempotency_keys",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", sa.String(length=64), sa.ForeignKey("employees.employee_id"), nullable=False),
        sa.Column("idempotency_key", sa.String(length=200), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("record_id", sa.String(length=64), sa.ForeignKey("activity_history.record_id"), nullable=False),
        sa.UniqueConstraint("employee_id", "idempotency_key", name="uq_employee_idempotency"),
    )
    op.create_index("ix_idempotency_keys_employee_id", "idempotency_keys", ["employee_id"])


def downgrade() -> None:
    op.drop_table("idempotency_keys")
    op.drop_table("sessions")
    op.drop_table("accounts")
    op.drop_table("activity_history")
    op.drop_table("employees")
    op.drop_table("dataset_state")
