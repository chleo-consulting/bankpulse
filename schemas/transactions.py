from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from schemas.tags import TagResponse


class TransactionResponse(BaseModel):
    id: UUID
    account_id: UUID
    merchant_id: UUID | None
    category_id: UUID | None
    amount: Decimal
    transaction_date: date
    booking_date: date | None
    description: str | None
    is_pending: bool
    tags: list[TagResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TransactionCategoryUpdate(BaseModel):
    category_id: UUID | None


class CursorTransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    next_cursor: str | None
    page_size: int


class BulkTagRequest(BaseModel):
    transaction_ids: list[UUID]
    tag_ids: list[UUID]


# Compat — conservé pour éviter de casser les imports existants
TransactionListResponse = CursorTransactionListResponse
