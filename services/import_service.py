from uuid import UUID

from sqlalchemy.orm import Session

from model.models import AuditLog, BankAccount, Merchant, Transaction
from parsers.boursorama import BoursoramaCsvParser
from schemas.import_ import AccountImportSummary, ImportResult
from services.categorization_service import CategorizationService


class ImportService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def import_boursorama(self, user_id: UUID, file_bytes: bytes) -> ImportResult:
        parser = BoursoramaCsvParser()
        parsed = parser.parse(file_bytes)

        summaries: list[AccountImportSummary] = []
        cat_service = CategorizationService(db=self.db)

        for parsed_account in parsed.accounts:
            account = (
                self.db.query(BankAccount)
                .filter(
                    BankAccount.user_id == user_id,
                    BankAccount.iban == parsed_account.account_num,
                    BankAccount.deleted_at.is_(None),
                )
                .first()
            )

            if account is None:
                account = BankAccount(
                    user_id=user_id,
                    iban=parsed_account.account_num,
                    account_name=parsed_account.account_label,
                )
                self.db.add(account)
                self.db.flush()

            nb_created = 0
            nb_skipped = 0
            nb_errors = 0

            for txn in parsed_account.transactions:
                existing = (
                    self.db.query(Transaction)
                    .filter(Transaction.import_hash == txn.import_hash)
                    .first()
                )
                if existing:
                    nb_skipped += 1
                    continue

                try:
                    merchant_id = None
                    if txn.merchant:
                        merchant = self._upsert_merchant(txn.merchant.normalized_name)
                        merchant_id = merchant.id

                    new_txn = Transaction(
                        account_id=account.id,
                        merchant_id=merchant_id,
                        amount=txn.amount,
                        transaction_date=txn.transaction_date,
                        booking_date=txn.booking_date,
                        description=txn.description,
                        import_hash=txn.import_hash,
                    )
                    self.db.add(new_txn)
                    if merchant_id:
                        cat_service.categorize_transaction(new_txn)
                    nb_created += 1
                except Exception:
                    nb_errors += 1

            balance_updated = False
            if parsed_account.balance is not None:
                account.balance = float(parsed_account.balance)
                balance_updated = True

            self.db.flush()

            audit = AuditLog(
                user_id=user_id,
                entity_type="bank_account",
                entity_id=account.id,
                action="IMPORT",
                new_values={
                    "source": "boursorama",
                    "nb_created": nb_created,
                    "nb_skipped": nb_skipped,
                    "nb_errors": nb_errors,
                },
            )
            self.db.add(audit)

            summaries.append(
                AccountImportSummary(
                    account_num=parsed_account.account_num,
                    account_label=parsed_account.account_label,
                    nb_created=nb_created,
                    nb_skipped=nb_skipped,
                    nb_errors=nb_errors,
                    balance_updated=balance_updated,
                )
            )

        self.db.commit()

        return ImportResult(
            accounts=summaries,
            total_created=sum(s.nb_created for s in summaries),
            total_skipped=sum(s.nb_skipped for s in summaries),
            total_errors=sum(s.nb_errors for s in summaries),
        )

    def import_to_account(self, account: BankAccount, file_bytes: bytes) -> ImportResult:
        """Importe un CSV Boursorama vers un compte spécifique.

        Priorité à l'IBAN matchant dans le CSV ; si aucun ne correspond, tous les comptes du CSV
        sont importés vers ce compte. La déduplication par import_hash s'applique.
        """
        parser = BoursoramaCsvParser()
        parsed = parser.parse(file_bytes)

        matching = [pa for pa in parsed.accounts if pa.account_num == account.iban]
        accounts_to_process = matching if matching else parsed.accounts

        summaries: list[AccountImportSummary] = []
        total_created, total_skipped, total_errors = 0, 0, 0
        last_balance = None
        cat_service = CategorizationService(db=self.db)

        for parsed_account in accounts_to_process:
            if parsed_account.balance is not None:
                last_balance = parsed_account.balance

            nb_created, nb_skipped, nb_errors = 0, 0, 0

            for txn in parsed_account.transactions:
                existing = (
                    self.db.query(Transaction)
                    .filter(Transaction.import_hash == txn.import_hash)
                    .first()
                )
                if existing:
                    nb_skipped += 1
                    continue

                try:
                    merchant_id = None
                    if txn.merchant:
                        merchant = self._upsert_merchant(txn.merchant.normalized_name)
                        merchant_id = merchant.id

                    new_txn = Transaction(
                        account_id=account.id,
                        merchant_id=merchant_id,
                        amount=txn.amount,
                        transaction_date=txn.transaction_date,
                        booking_date=txn.booking_date,
                        description=txn.description,
                        import_hash=txn.import_hash,
                    )
                    self.db.add(new_txn)
                    if merchant_id:
                        cat_service.categorize_transaction(new_txn)
                    nb_created += 1
                except Exception:
                    nb_errors += 1

            total_created += nb_created
            total_skipped += nb_skipped
            total_errors += nb_errors

            summaries.append(
                AccountImportSummary(
                    account_num=parsed_account.account_num,
                    account_label=parsed_account.account_label,
                    nb_created=nb_created,
                    nb_skipped=nb_skipped,
                    nb_errors=nb_errors,
                    balance_updated=parsed_account.balance is not None,
                )
            )

        if last_balance is not None:
            account.balance = float(last_balance)

        self.db.flush()

        audit = AuditLog(
            user_id=account.user_id,
            entity_type="bank_account",
            entity_id=account.id,
            action="IMPORT",
            new_values={
                "source": "boursorama",
                "nb_created": total_created,
                "nb_skipped": total_skipped,
                "nb_errors": total_errors,
            },
        )
        self.db.add(audit)
        self.db.commit()

        return ImportResult(
            accounts=summaries,
            total_created=total_created,
            total_skipped=total_skipped,
            total_errors=total_errors,
        )

    def _upsert_merchant(self, normalized_name: str) -> Merchant:
        merchant = (
            self.db.query(Merchant)
            .filter(
                Merchant.normalized_name == normalized_name,
                Merchant.deleted_at.is_(None),
            )
            .first()
        )
        if merchant is None:
            merchant = Merchant(name=normalized_name, normalized_name=normalized_name)
            self.db.add(merchant)
            self.db.flush()
        return merchant
