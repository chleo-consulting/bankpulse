import dataclasses
import hashlib
from uuid import UUID

from sqlalchemy.orm import Session

from model.models import AuditLog, BankAccount, Merchant, Transaction
from parsers.base import ParsedTransaction
from parsers.boursorama import BoursoramaCsvParser
from schemas.import_ import AccountImportSummary, ImportResult, SkippedTransaction
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
            skipped: list[SkippedTransaction] = []

            transactions = self._deduplicate_intra_file(parsed_account.transactions)
            for txn in transactions:
                existing = (
                    self.db.query(Transaction)
                    .filter(Transaction.import_hash == txn.import_hash)
                    .first()
                )
                if existing:
                    nb_skipped += 1
                    skipped.append(
                        SkippedTransaction(
                            transaction_date=txn.transaction_date,
                            amount=txn.amount,
                            description=txn.description,
                        )
                    )
                    continue

                savepoint = self.db.begin_nested()
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
                    savepoint.commit()
                    nb_created += 1
                except Exception:
                    savepoint.rollback()
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
                    skipped_transactions=skipped,
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
            skipped: list[SkippedTransaction] = []

            transactions = self._deduplicate_intra_file(parsed_account.transactions)
            for txn in transactions:
                existing = (
                    self.db.query(Transaction)
                    .filter(Transaction.import_hash == txn.import_hash)
                    .first()
                )
                if existing:
                    nb_skipped += 1
                    skipped.append(
                        SkippedTransaction(
                            transaction_date=txn.transaction_date,
                            amount=txn.amount,
                            description=txn.description,
                        )
                    )
                    continue

                savepoint = self.db.begin_nested()
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
                    savepoint.commit()
                    nb_created += 1
                except Exception:
                    savepoint.rollback()
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
                    skipped_transactions=skipped,
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

    @staticmethod
    def _deduplicate_intra_file(
        transactions: list[ParsedTransaction],
    ) -> list[ParsedTransaction]:
        """Détecte les doublons intra-fichier (même import_hash) et rend chaque transaction unique
        en suffixant le libellé.

        1ère occurrence : inchangée.
        2ème occurrence : description + " 1", hash recalculé.
        3ème occurrence : description + " 2", etc.
        """
        seen: dict[str, int] = {}  # original_hash → nb d'occurrences déjà traitées
        result: list[ParsedTransaction] = []
        for txn in transactions:
            key = txn.import_hash
            if key not in seen:
                seen[key] = 0
                result.append(txn)
            else:
                seen[key] += 1
                count = seen[key]
                new_description = f"{txn.description} {count}"
                new_hash = hashlib.sha256(
                    f"{txn.transaction_date.isoformat()}|{txn.account_num}"
                    f"|{txn.amount}|{new_description}".encode()
                ).hexdigest()
                result.append(
                    dataclasses.replace(txn, description=new_description, import_hash=new_hash)
                )
        return result

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
