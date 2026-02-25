from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


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
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TransactionCategoryUpdate(BaseModel):
    category_id: UUID | None


class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
    page: int
    page_size: int
