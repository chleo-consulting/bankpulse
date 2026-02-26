from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class MonthlySummary(BaseModel):
    current: Decimal
    previous: Decimal
    delta_pct: float


class DashboardSummary(BaseModel):
    total_balance: Decimal
    expenses: MonthlySummary


class CategoryBreakdownItem(BaseModel):
    category_id: UUID
    category_name: str
    parent_category_name: str | None
    amount: Decimal
    percentage: float
    transaction_count: int


class CategoriesBreakdown(BaseModel):
    month: str  # YYYY-MM
    items: list[CategoryBreakdownItem]
    total_amount: Decimal


class TopMerchantItem(BaseModel):
    merchant_id: UUID
    merchant_name: str
    amount: Decimal
    transaction_count: int


class TopMerchants(BaseModel):
    month: str
    items: list[TopMerchantItem]


class RecurringSubscription(BaseModel):
    recurring_rule_id: UUID
    merchant_id: UUID
    merchant_name: str
    expected_amount: Decimal | None
    frequency: str
    last_detected: date | None
    next_expected: date | None


class RecurringSubscriptions(BaseModel):
    items: list[RecurringSubscription]
