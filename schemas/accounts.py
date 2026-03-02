from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class BankAccountCreate(BaseModel):
    account_name: str | None = None
    iban: str | None = None
    account_type: str | None = None
    balance: Decimal = Decimal("0.00")


class BankAccountUpdate(BaseModel):
    account_name: str | None = None
    iban: str | None = None
    account_type: str | None = None
    balance: Decimal | None = None


class BankAccountResponse(BaseModel):
    id: UUID
    user_id: UUID
    account_name: str | None
    iban: str | None
    account_type: str | None
    balance: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BankAccountListResponse(BankAccountResponse):
    """Réponse étendue pour GET /accounts — inclut les informations de partage."""

    is_shared: bool = False
    shared_by_email: str | None = None
    shared_by_name: str | None = None

    model_config = {"from_attributes": False}
