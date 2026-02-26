from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from dateutil.relativedelta import relativedelta
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from model.models import BankAccount, Budget, Category, Transaction


class BudgetService:
    def __init__(self, db: Session) -> None:
        self.db = db

    # --- helpers ---

    def _user_account_ids_subq(self, user_id: UUID):
        return select(BankAccount.id).where(
            BankAccount.user_id == user_id,
            BankAccount.deleted_at.is_(None),
        )

    def _period_range(self, period_type: str, month_str: str | None) -> tuple[date, date]:
        """Calcule (start, end) selon period_type et le mois de référence."""
        if month_str:
            year, month = int(month_str[:4]), int(month_str[5:7])
            ref = date(year, month, 1)
        else:
            today = date.today()
            ref = date(today.year, today.month, 1)

        if period_type == "monthly":
            start = ref
            end = ref + relativedelta(months=1)
        elif period_type == "quarterly":
            q = (ref.month - 1) // 3
            start = date(ref.year, q * 3 + 1, 1)
            end = start + relativedelta(months=3)
        else:  # yearly
            start = date(ref.year, 1, 1)
            end = date(ref.year + 1, 1, 1)

        return start, end

    def _compute_spent(self, user_id: UUID, category_id: UUID, start: date, end: date) -> Decimal:
        """Somme des dépenses (montant < 0) sur une catégorie et une période."""
        user_account_ids = self._user_account_ids_subq(user_id)
        result = self.db.execute(
            select(func.sum(Transaction.amount)).where(
                Transaction.account_id.in_(user_account_ids),
                Transaction.category_id == category_id,
                Transaction.amount < 0,
                Transaction.transaction_date >= start,
                Transaction.transaction_date < end,
            )
        ).scalar()
        return abs(Decimal(str(result))) if result is not None else Decimal("0")

    def _compute_alert(self, spent: Decimal, limit: Decimal) -> str | None:
        if limit <= 0:
            return None
        if spent > limit:
            return "over_budget"
        if spent >= limit * Decimal("0.8"):
            return "near_limit"
        return None

    # --- CRUD ---

    def create(
        self,
        user_id: UUID,
        category_id: UUID,
        period_type: str,
        amount_limit: Decimal,
    ) -> Budget:
        budget = Budget(
            user_id=user_id,
            category_id=category_id,
            period_type=period_type,
            amount_limit=amount_limit,
        )
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def list_budgets(self, user_id: UUID) -> list[Budget]:
        return list(
            self.db.execute(
                select(Budget)
                .where(Budget.user_id == user_id, Budget.deleted_at.is_(None))
                .order_by(Budget.created_at)
            )
            .scalars()
            .all()
        )

    def get_by_id(self, budget_id: UUID, user_id: UUID) -> Budget | None:
        return self.db.execute(
            select(Budget).where(
                Budget.id == budget_id,
                Budget.user_id == user_id,
                Budget.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

    def update(
        self,
        budget: Budget,
        period_type: str | None,
        amount_limit: Decimal | None,
    ) -> Budget:
        if period_type is not None:
            budget.period_type = period_type
        if amount_limit is not None:
            budget.amount_limit = amount_limit
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def delete(self, budget: Budget) -> None:
        budget.deleted_at = datetime.now(timezone.utc)
        self.db.commit()

    # --- Progression ---

    def get_progress(self, user_id: UUID, month_str: str | None) -> list[dict]:
        """Retourne la progression temps réel pour tous les budgets actifs de l'utilisateur."""
        budgets = self.list_budgets(user_id)
        items = []
        for budget in budgets:
            category = self.db.get(Category, budget.category_id)
            category_name = category.name if category else "Inconnue"

            start, end = self._period_range(budget.period_type, month_str)
            spent = self._compute_spent(user_id, budget.category_id, start, end)
            limit = Decimal(str(budget.amount_limit))
            pct = float(spent / limit * 100) if limit > 0 else 0.0
            alert = self._compute_alert(spent, limit)

            items.append(
                {
                    "budget_id": budget.id,
                    "category_id": budget.category_id,
                    "category_name": category_name,
                    "period_type": budget.period_type,
                    "limit": limit,
                    "spent": spent,
                    "pct": round(pct, 2),
                    "alert": alert,
                }
            )
        return items
