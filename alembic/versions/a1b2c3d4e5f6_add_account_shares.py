"""add_account_shares

Revision ID: a1b2c3d4e5f6
Revises: 11ad90472e66
Create Date: 2026-03-02 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "11ad90472e66"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "account_shares",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("account_id", sa.UUID(), nullable=False),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("invitee_email", sa.String(length=255), nullable=False),
        sa.Column("invitee_user_id", sa.UUID(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("responded_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "status IN ('pending','accepted','rejected','revoked')",
            name="ck_account_shares_status",
        ),
        sa.ForeignKeyConstraint(["account_id"], ["bank_accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["invitee_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(
        "idx_account_shares_token_hash", "account_shares", ["token_hash"], unique=False
    )
    op.create_index(
        "idx_account_shares_invitee_email", "account_shares", ["invitee_email"], unique=False
    )
    op.create_index(
        "idx_account_shares_account_id", "account_shares", ["account_id"], unique=False
    )
    op.create_index(
        "idx_account_shares_invitee_user_id",
        "account_shares",
        ["invitee_user_id"],
        unique=False,
    )
    # Index partiel PostgreSQL : une seule invitation pending par (account_id, invitee_email)
    op.create_index(
        "idx_account_shares_unique_pending",
        "account_shares",
        ["account_id", "invitee_email"],
        unique=True,
        postgresql_where=sa.text("status = 'pending'"),
    )


def downgrade() -> None:
    op.drop_index("idx_account_shares_unique_pending", table_name="account_shares")
    op.drop_index("idx_account_shares_invitee_user_id", table_name="account_shares")
    op.drop_index("idx_account_shares_account_id", table_name="account_shares")
    op.drop_index("idx_account_shares_invitee_email", table_name="account_shares")
    op.drop_index("idx_account_shares_token_hash", table_name="account_shares")
    op.drop_table("account_shares")
