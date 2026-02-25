"""add_import_hash_to_transactions

Revision ID: b3e9f1a2c456
Revises: 8ffc6c2b8a87
Create Date: 2026-02-25 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b3e9f1a2c456"
down_revision: str | Sequence[str] | None = "8ffc6c2b8a87"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Ajout de import_hash (SHA-256 de déduplication) sur la table transactions."""
    op.add_column("transactions", sa.Column("import_hash", sa.String(64), nullable=True))
    op.create_unique_constraint("uq_transactions_import_hash", "transactions", ["import_hash"])


def downgrade() -> None:
    """Suppression de import_hash."""
    op.drop_constraint("uq_transactions_import_hash", "transactions", type_="unique")
    op.drop_column("transactions", "import_hash")
