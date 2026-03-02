from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class SkippedTransaction(BaseModel):
    transaction_date: date
    amount: Decimal
    description: str


class AccountImportSummary(BaseModel):
    account_num: str
    account_label: str
    nb_created: int
    nb_skipped: int
    nb_errors: int
    balance_updated: bool
    skipped_transactions: list[SkippedTransaction] = []


class ImportResult(BaseModel):
    accounts: list[AccountImportSummary]
    total_created: int
    total_skipped: int
    total_errors: int
