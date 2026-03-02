from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class TransactionFilters(BaseModel):
    """Filtres communs applicables aux transactions (list + export)."""

    account_id: UUID | None = None
    category_id: UUID | None = None
    merchant_id: UUID | None = None
    tag_id: UUID | None = None
    date_from: date | None = None
    date_to: date | None = None
    amount_min: Decimal | None = None
    amount_max: Decimal | None = None


class TransactionListParams(TransactionFilters):
    """Paramètres pour la liste paginée (filtres + pagination cursor-based)."""

    cursor: str | None = None
    page_size: int = Field(50, ge=1, le=200)
