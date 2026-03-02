import csv
import hashlib
import io
from datetime import date
from decimal import Decimal, InvalidOperation

from parsers.base import (
    AbstractCsvParser,
    ParsedAccount,
    ParsedData,
    ParsedMerchant,
    ParsedTransaction,
)


class BoursoramaCsvParser(AbstractCsvParser):
    """Parser pour les exports CSV Boursorama (format multi-comptes)."""

    def parse(self, file: bytes | io.IOBase) -> ParsedData:
        if isinstance(file, bytes):
            raw = file
        else:
            raw = file.read()

        text = self._decode(raw)
        reader = csv.DictReader(io.StringIO(text), delimiter=";")

        accounts: dict[str, ParsedAccount] = {}
        balance_by_account: dict[str, Decimal] = {}

        for row in reader:
            account_num = row.get("accountNum", "").strip()
            account_label = row.get("accountLabel", "").strip()
            date_op_str = row.get("dateOp", "").strip()
            date_val_str = row.get("dateVal", "").strip()
            label = row.get("label", "").strip()
            amount_str = (
                row.get("amount", "").strip().replace("\xa0", "").replace(" ", "").replace(",", ".")
            )
            balance_str = row.get("accountbalance", "").strip()
            supplier = row.get("supplierFound", "").strip()

            if not account_num or not date_op_str or not amount_str:
                continue

            try:
                transaction_date = date.fromisoformat(date_op_str)
            except ValueError:
                continue

            booking_date: date | None = None
            if date_val_str:
                try:
                    booking_date = date.fromisoformat(date_val_str)
                except ValueError:
                    pass

            try:
                amount = Decimal(amount_str)
            except InvalidOperation:
                continue

            if balance_str:
                try:
                    balance_by_account[account_num] = Decimal(balance_str)
                except InvalidOperation:
                    pass

            import_hash = hashlib.sha256(
                f"{date_op_str}|{account_num}|{amount_str}|{label}".encode()
            ).hexdigest()

            merchant: ParsedMerchant | None = None
            if supplier:
                merchant = ParsedMerchant(normalized_name=supplier)

            txn = ParsedTransaction(
                account_num=account_num,
                transaction_date=transaction_date,
                booking_date=booking_date,
                description=label,
                amount=amount,
                import_hash=import_hash,
                merchant=merchant,
            )

            if account_num not in accounts:
                accounts[account_num] = ParsedAccount(
                    account_num=account_num,
                    account_label=account_label,
                    balance=None,
                )

            accounts[account_num].transactions.append(txn)

        for account_num, account in accounts.items():
            account.balance = balance_by_account.get(account_num)

        return ParsedData(accounts=list(accounts.values()))

    def _decode(self, raw: bytes) -> str:
        for encoding in ("utf-8-sig", "utf-8", "latin-1"):
            try:
                return raw.decode(encoding)
            except UnicodeDecodeError:
                continue
        return raw.decode("latin-1", errors="replace")
