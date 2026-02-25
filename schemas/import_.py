from pydantic import BaseModel


class AccountImportSummary(BaseModel):
    account_num: str
    account_label: str
    nb_created: int
    nb_skipped: int
    nb_errors: int
    balance_updated: bool


class ImportResult(BaseModel):
    accounts: list[AccountImportSummary]
    total_created: int
    total_skipped: int
    total_errors: int
