"""add_category_rules_and_seed

Revision ID: c7d8e3f1a234
Revises: b3e9f1a2c456
Create Date: 2026-02-25 12:00:00.000000

"""

from collections.abc import Sequence
from datetime import datetime

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c7d8e3f1a234"
down_revision: str | Sequence[str] | None = "b3e9f1a2c456"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# ── UUID fixes catégories parents ────────────────────────────────────────────
CAT_ALIMENTATION = "a1000000-0000-0000-0000-000000000001"
CAT_TRANSPORT = "a1000000-0000-0000-0000-000000000002"
CAT_LOGEMENT = "a1000000-0000-0000-0000-000000000003"
CAT_LOISIRS = "a1000000-0000-0000-0000-000000000004"
CAT_SANTE = "a1000000-0000-0000-0000-000000000005"
CAT_SHOPPING = "a1000000-0000-0000-0000-000000000006"
CAT_SERVICES = "a1000000-0000-0000-0000-000000000007"
CAT_REVENUS = "a1000000-0000-0000-0000-000000000008"

# ── UUID fixes catégories enfants ────────────────────────────────────────────
CAT_SUPERMARCHE = "c1000000-0000-0000-0000-000000000001"
CAT_RESTAURANT = "c1000000-0000-0000-0000-000000000002"
CAT_FAST_FOOD = "c1000000-0000-0000-0000-000000000003"
CAT_ESSENCE = "c1000000-0000-0000-0000-000000000004"
CAT_TC = "c1000000-0000-0000-0000-000000000005"
CAT_TAXI = "c1000000-0000-0000-0000-000000000006"
CAT_LOYER = "c1000000-0000-0000-0000-000000000007"
CAT_CHARGES = "c1000000-0000-0000-0000-000000000008"
CAT_SPORT = "c1000000-0000-0000-0000-000000000009"
CAT_STREAMING = "c1000000-0000-0000-0000-000000000010"
CAT_CINEMA = "c1000000-0000-0000-0000-000000000011"
CAT_MEDECIN = "c1000000-0000-0000-0000-000000000012"
CAT_PHARMACIE = "c1000000-0000-0000-0000-000000000013"
CAT_VETEMENTS = "c1000000-0000-0000-0000-000000000014"
CAT_HIGH_TECH = "c1000000-0000-0000-0000-000000000015"
CAT_TELEPHONIE = "c1000000-0000-0000-0000-000000000016"
CAT_ASSURANCES = "c1000000-0000-0000-0000-000000000017"
CAT_BANQUE = "c1000000-0000-0000-0000-000000000018"
CAT_SALAIRE = "c1000000-0000-0000-0000-000000000019"
CAT_REMBOURS = "c1000000-0000-0000-0000-000000000020"

SEED_TS = datetime(2026, 2, 25, 12, 0, 0)


def upgrade() -> None:
    """Crée la table category_rules et insère le seed catégories + règles RegExp."""
    # ── 1. Table category_rules ───────────────────────────────────────────────
    op.create_table(
        "category_rules",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("category_id", sa.UUID(), nullable=False),
        sa.Column("merchant_pattern", sa.String(255), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── 2. Seed catégories ────────────────────────────────────────────────────
    categories_tbl = sa.table(
        "categories",
        sa.column("id", sa.String),
        sa.column("name", sa.String),
        sa.column("parent_id", sa.String),
        sa.column("icon", sa.String),
        sa.column("created_at", sa.DateTime),
    )

    op.bulk_insert(
        categories_tbl,
        [
            # Parents
            {
                "id": CAT_ALIMENTATION,
                "name": "Alimentation",
                "parent_id": None,
                "icon": None,
                "created_at": SEED_TS,
            },
            {
                "id": CAT_TRANSPORT,
                "name": "Transport",
                "parent_id": None,
                "icon": None,
                "created_at": SEED_TS,
            },
            {
                "id": CAT_LOGEMENT,
                "name": "Logement",
                "parent_id": None,
                "icon": None,
                "created_at": SEED_TS,
            },
            {
                "id": CAT_LOISIRS,
                "name": "Loisirs & Culture",
                "parent_id": None,
                "icon": None,
                "created_at": SEED_TS,
            },
            {
                "id": CAT_SANTE,
                "name": "Sante",
                "parent_id": None,
                "icon": None,
                "created_at": SEED_TS,
            },
            {
                "id": CAT_SHOPPING,
                "name": "Shopping",
                "parent_id": None,
                "icon": None,
                "created_at": SEED_TS,
            },
            {
                "id": CAT_SERVICES,
                "name": "Services & Abonnements",
                "parent_id": None,
                "icon": None,
                "created_at": SEED_TS,
            },
            {
                "id": CAT_REVENUS,
                "name": "Revenus",
                "parent_id": None,
                "icon": None,
                "created_at": SEED_TS,
            },
            # Enfants — Alimentation
            {
                "id": CAT_SUPERMARCHE,
                "name": "Supermarche",
                "parent_id": CAT_ALIMENTATION,
                "icon": None,
                "created_at": SEED_TS,
            },
            {
                "id": CAT_RESTAURANT,
                "name": "Restaurant",
                "parent_id": CAT_ALIMENTATION,
                "icon": None,
                "created_at": SEED_TS,
            },
            {
                "id": CAT_FAST_FOOD,
                "name": "Fast food",
                "parent_id": CAT_ALIMENTATION,
                "icon": None,
                "created_at": SEED_TS,
            },
            # Enfants — Transport
            {
                "id": CAT_ESSENCE,
                "name": "Essence",
                "parent_id": CAT_TRANSPORT,
                "icon": None,
                "created_at": SEED_TS,
            },
            {
                "id": CAT_TC,
                "name": "Transports en commun",
                "parent_id": CAT_TRANSPORT,
                "icon": None,
                "created_at": SEED_TS,
            },
            {
                "id": CAT_TAXI,
                "name": "Taxi & VTC",
                "parent_id": CAT_TRANSPORT,
                "icon": None,
                "created_at": SEED_TS,
            },
            # Enfants — Logement
            {
                "id": CAT_LOYER,
                "name": "Loyer",
                "parent_id": CAT_LOGEMENT,
                "icon": None,
                "created_at": SEED_TS,
            },
            {
                "id": CAT_CHARGES,
                "name": "Charges",
                "parent_id": CAT_LOGEMENT,
                "icon": None,
                "created_at": SEED_TS,
            },
            # Enfants — Loisirs
            {
                "id": CAT_SPORT,
                "name": "Sport & Fitness",
                "parent_id": CAT_LOISIRS,
                "icon": None,
                "created_at": SEED_TS,
            },
            {
                "id": CAT_STREAMING,
                "name": "Streaming & Jeux",
                "parent_id": CAT_LOISIRS,
                "icon": None,
                "created_at": SEED_TS,
            },
            {
                "id": CAT_CINEMA,
                "name": "Cinema",
                "parent_id": CAT_LOISIRS,
                "icon": None,
                "created_at": SEED_TS,
            },
            # Enfants — Sante
            {
                "id": CAT_MEDECIN,
                "name": "Medecin",
                "parent_id": CAT_SANTE,
                "icon": None,
                "created_at": SEED_TS,
            },
            {
                "id": CAT_PHARMACIE,
                "name": "Pharmacie",
                "parent_id": CAT_SANTE,
                "icon": None,
                "created_at": SEED_TS,
            },
            # Enfants — Shopping
            {
                "id": CAT_VETEMENTS,
                "name": "Vetements",
                "parent_id": CAT_SHOPPING,
                "icon": None,
                "created_at": SEED_TS,
            },
            {
                "id": CAT_HIGH_TECH,
                "name": "High-tech",
                "parent_id": CAT_SHOPPING,
                "icon": None,
                "created_at": SEED_TS,
            },
            # Enfants — Services
            {
                "id": CAT_TELEPHONIE,
                "name": "Telephonie",
                "parent_id": CAT_SERVICES,
                "icon": None,
                "created_at": SEED_TS,
            },
            {
                "id": CAT_ASSURANCES,
                "name": "Assurances",
                "parent_id": CAT_SERVICES,
                "icon": None,
                "created_at": SEED_TS,
            },
            {
                "id": CAT_BANQUE,
                "name": "Banque & Frais",
                "parent_id": CAT_SERVICES,
                "icon": None,
                "created_at": SEED_TS,
            },
            # Enfants — Revenus
            {
                "id": CAT_SALAIRE,
                "name": "Salaire",
                "parent_id": CAT_REVENUS,
                "icon": None,
                "created_at": SEED_TS,
            },
            {
                "id": CAT_REMBOURS,
                "name": "Remboursements",
                "parent_id": CAT_REVENUS,
                "icon": None,
                "created_at": SEED_TS,
            },
        ],
    )

    # ── 3. Seed règles RegExp ─────────────────────────────────────────────────
    rules_tbl = sa.table(
        "category_rules",
        sa.column("id", sa.String),
        sa.column("category_id", sa.String),
        sa.column("merchant_pattern", sa.String),
        sa.column("priority", sa.Integer),
        sa.column("created_at", sa.DateTime),
    )

    op.bulk_insert(
        rules_tbl,
        [
            {
                "id": "d1000000-0000-0000-0000-000000000001",
                "category_id": CAT_SUPERMARCHE,
                "merchant_pattern": (
                    r"(?i)CARREFOUR|LECLERC|LIDL|ALDI|INTERMARCHE|SUPER U|MONOPRIX|CASINO"
                ),
                "priority": 10,
                "created_at": SEED_TS,
            },
            {
                "id": "d1000000-0000-0000-0000-000000000002",
                "category_id": CAT_FAST_FOOD,
                "merchant_pattern": r"(?i)MCDONALDS|BURGER KING|KFC|SUBWAY|QUICK|DOMINOS",
                "priority": 10,
                "created_at": SEED_TS,
            },
            {
                "id": "d1000000-0000-0000-0000-000000000003",
                "category_id": CAT_ESSENCE,
                "merchant_pattern": r"(?i)TOTAL|BP|SHELL|ESSO|AVIA",
                "priority": 10,
                "created_at": SEED_TS,
            },
            {
                "id": "d1000000-0000-0000-0000-000000000004",
                "category_id": CAT_TC,
                "merchant_pattern": r"(?i)SNCF|RATP|TRANSILIEN|OUIGO|TER ",
                "priority": 10,
                "created_at": SEED_TS,
            },
            {
                "id": "d1000000-0000-0000-0000-000000000005",
                "category_id": CAT_TAXI,
                "merchant_pattern": r"(?i)UBER|BOLT|HEETCH|BLABLACAR",
                "priority": 9,
                "created_at": SEED_TS,
            },
            {
                "id": "d1000000-0000-0000-0000-000000000006",
                "category_id": CAT_STREAMING,
                "merchant_pattern": r"(?i)NETFLIX|SPOTIFY|DEEZER|CANAL\+|AMAZON PRIME|DISNEY",
                "priority": 10,
                "created_at": SEED_TS,
            },
            {
                "id": "d1000000-0000-0000-0000-000000000007",
                "category_id": CAT_PHARMACIE,
                "merchant_pattern": r"(?i)PHARMACIE|PHARMA|APOTHEQUE",
                "priority": 10,
                "created_at": SEED_TS,
            },
        ],
    )


def downgrade() -> None:
    """Supprime le seed et la table category_rules."""
    conn = op.get_bind()

    parent_ids = [
        CAT_ALIMENTATION,
        CAT_TRANSPORT,
        CAT_LOGEMENT,
        CAT_LOISIRS,
        CAT_SANTE,
        CAT_SHOPPING,
        CAT_SERVICES,
        CAT_REVENUS,
    ]

    categories_tbl = sa.table(
        "categories", sa.column("id", sa.String), sa.column("parent_id", sa.String)
    )
    category_rules_tbl = sa.table("category_rules", sa.column("id", sa.String))

    conn.execute(sa.delete(category_rules_tbl))
    conn.execute(sa.delete(categories_tbl).where(categories_tbl.c.parent_id.in_(parent_ids)))
    conn.execute(sa.delete(categories_tbl).where(categories_tbl.c.id.in_(parent_ids)))

    op.drop_table("category_rules")
