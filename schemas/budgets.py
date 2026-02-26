from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BudgetCreate(BaseModel):
    category_id: UUID
    period_type: str = Field(..., pattern="^(monthly|quarterly|yearly)$")
    amount_limit: Decimal = Field(..., gt=0)


class BudgetUpdate(BaseModel):
    period_type: str | None = Field(None, pattern="^(monthly|quarterly|yearly)$")
    amount_limit: Decimal | None = Field(None, gt=0)


class BudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    category_id: UUID
    period_type: str
    amount_limit: Decimal
    created_at: datetime


class BudgetProgressItem(BaseModel):
    budget_id: UUID
    category_id: UUID
    category_name: str
    period_type: str
    limit: Decimal
    spent: Decimal
    pct: float
    alert: str | None  # "over_budget" | "near_limit" | None


class BudgetsProgress(BaseModel):
    month: str | None  # YYYY-MM si fourni, None si mois courant
    items: list[BudgetProgressItem]
