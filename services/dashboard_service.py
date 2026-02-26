from datetime import date
from decimal import Decimal
from uuid import UUID

from dateutil.relativedelta import relativedelta
from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from model.models import BankAccount, Category, Merchant, RecurringRule, Transaction


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _user_account_ids(self, user_id: UUID):
        """Sous-requête réutilisable : IDs des comptes actifs de l'utilisateur."""
        return select(BankAccount.id).where(
            BankAccount.user_id == user_id,
            BankAccount.deleted_at.is_(None),
        )

    def _get_month_range(self, month_str: str) -> tuple[date, date]:
        """Retourne (start_date inclusive, end_date exclusive) pour un mois YYYY-MM."""
        year, month = int(month_str[:4]), int(month_str[5:7])
        start_date = date(year, month, 1)
        end_date = start_date + relativedelta(months=1)
        return start_date, end_date

    def get_consolidated_balance(self, user_id: UUID) -> Decimal:
        """Somme des soldes de tous les comptes actifs de l'utilisateur."""
        result = (
            self.db.query(func.sum(BankAccount.balance))
            .filter(
                BankAccount.user_id == user_id,
                BankAccount.deleted_at.is_(None),
            )
            .scalar()
        )
        return Decimal(str(result)) if result is not None else Decimal("0")

    def get_monthly_expenses(self, user_id: UUID, month_str: str) -> Decimal:
        """Somme des dépenses (amount < 0) du mois, retournée en valeur absolue."""
        start_date, end_date = self._get_month_range(month_str)
        user_account_ids = self._user_account_ids(user_id)
        result = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.account_id.in_(user_account_ids),
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date < end_date,
                Transaction.amount < 0,
            )
            .scalar()
        )
        if result is None:
            return Decimal("0")
        return abs(Decimal(str(result)))

    def get_monthly_comparison(self, user_id: UUID) -> dict:
        """Comparaison des dépenses mois courant vs mois précédent."""
        today = date.today()
        current_month = today.strftime("%Y-%m")
        previous_month = (today - relativedelta(months=1)).strftime("%Y-%m")

        current = self.get_monthly_expenses(user_id, current_month)
        previous = self.get_monthly_expenses(user_id, previous_month)

        if previous == Decimal("0"):
            delta_pct = 0.0
        else:
            delta_pct = round(float((current - previous) / previous * 100), 2)

        return {
            "current": current,
            "previous": previous,
            "delta_pct": delta_pct,
        }

    def get_categories_breakdown(self, user_id: UUID, month_str: str | None = None) -> list[dict]:
        """Répartition des dépenses par catégorie pour un mois donné."""
        if month_str is None:
            month_str = date.today().strftime("%Y-%m")

        start_date, end_date = self._get_month_range(month_str)
        user_account_ids = self._user_account_ids(user_id)

        ParentCategory = aliased(Category)

        rows = (
            self.db.query(
                Category.id.label("category_id"),
                Category.name.label("category_name"),
                ParentCategory.name.label("parent_category_name"),
                func.sum(Transaction.amount).label("amount"),
                func.count(Transaction.id).label("transaction_count"),
            )
            .join(Transaction, Transaction.category_id == Category.id)
            .outerjoin(ParentCategory, Category.parent_id == ParentCategory.id)
            .filter(
                Transaction.account_id.in_(user_account_ids),
                Transaction.amount < 0,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date < end_date,
            )
            .group_by(Category.id, Category.name, ParentCategory.name)
            .order_by(func.sum(Transaction.amount).asc())  # plus négatif = dépense la plus élevée
            .limit(10)
            .all()
        )

        total_amount = sum(abs(Decimal(str(row.amount))) for row in rows)

        result = []
        for row in rows:
            cat_amount = abs(Decimal(str(row.amount)))
            pct = round(float(cat_amount / total_amount * 100), 2) if total_amount > 0 else 0.0
            result.append(
                {
                    "category_id": row.category_id,
                    "category_name": row.category_name,
                    "parent_category_name": row.parent_category_name,
                    "amount": cat_amount,
                    "percentage": pct,
                    "transaction_count": row.transaction_count,
                }
            )

        return result

    def get_top_merchants(
        self, user_id: UUID, month_str: str | None = None, limit: int = 5
    ) -> list[dict]:
        """Top marchands par montant dépensé pour un mois donné."""
        if month_str is None:
            month_str = date.today().strftime("%Y-%m")

        start_date, end_date = self._get_month_range(month_str)
        user_account_ids = self._user_account_ids(user_id)

        rows = (
            self.db.query(
                Merchant.id.label("merchant_id"),
                Merchant.name.label("merchant_name"),
                func.sum(Transaction.amount).label("amount"),
                func.count(Transaction.id).label("transaction_count"),
            )
            .join(Transaction, Transaction.merchant_id == Merchant.id)
            .filter(
                Transaction.account_id.in_(user_account_ids),
                Transaction.merchant_id.is_not(None),
                Transaction.amount < 0,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date < end_date,
            )
            .group_by(Merchant.id, Merchant.name)
            .order_by(func.sum(Transaction.amount).asc())
            .limit(limit)
            .all()
        )

        return [
            {
                "merchant_id": row.merchant_id,
                "merchant_name": row.merchant_name,
                "amount": abs(Decimal(str(row.amount))),
                "transaction_count": row.transaction_count,
            }
            for row in rows
        ]

    def get_recurring_subscriptions(self, user_id: UUID) -> list[dict]:
        """Abonnements récurrents liés aux transactions de l'utilisateur."""
        user_account_ids = self._user_account_ids(user_id)

        user_merchant_ids = (
            select(Transaction.merchant_id)
            .where(
                Transaction.account_id.in_(user_account_ids),
                Transaction.merchant_id.is_not(None),
            )
            .distinct()
        )

        rows = (
            self.db.query(RecurringRule, Merchant)
            .join(Merchant, RecurringRule.merchant_id == Merchant.id)
            .filter(
                RecurringRule.merchant_id.in_(user_merchant_ids),
                RecurringRule.deleted_at.is_(None),
            )
            .order_by(RecurringRule.last_detected.asc())
            .all()
        )

        result = []
        for rule, merchant in rows:
            if rule.last_detected is not None:
                if rule.frequency == "monthly":
                    next_expected = rule.last_detected + relativedelta(months=1)
                else:  # yearly
                    next_expected = rule.last_detected + relativedelta(years=1)
            else:
                next_expected = None

            result.append(
                {
                    "recurring_rule_id": rule.id,
                    "merchant_id": merchant.id,
                    "merchant_name": merchant.name,
                    "expected_amount": (
                        abs(Decimal(str(rule.expected_amount)))
                        if rule.expected_amount is not None
                        else None
                    ),
                    "frequency": rule.frequency,
                    "last_detected": rule.last_detected,
                    "next_expected": next_expected,
                }
            )

        return result
