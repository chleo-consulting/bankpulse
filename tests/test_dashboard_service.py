from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

import services.dashboard_service as svc_module
from model.models import BankAccount, Category, Merchant, RecurringRule, Transaction, User
from services.dashboard_service import DashboardService


@pytest.fixture
def test_user(db_session) -> User:
    user = User(email=f"dash_svc_{uuid4().hex[:8]}@test.com", password_hash="x")
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def test_account(db_session, test_user: User) -> BankAccount:
    account = BankAccount(user_id=test_user.id, account_name="Compte Courant", balance=1000.00)
    db_session.add(account)
    db_session.flush()
    return account


class TestConsolidatedBalance:
    def test_no_accounts_returns_zero(self, db_session, test_user: User) -> None:
        svc = DashboardService(db_session)
        result = svc.get_consolidated_balance(test_user.id)
        assert result == Decimal("0")

    def test_single_account(self, db_session, test_user: User, test_account: BankAccount) -> None:
        svc = DashboardService(db_session)
        result = svc.get_consolidated_balance(test_user.id)
        assert result == Decimal("1000.00")

    def test_multiple_accounts_summed(self, db_session, test_user: User) -> None:
        a1 = BankAccount(user_id=test_user.id, balance=500.00)
        a2 = BankAccount(user_id=test_user.id, balance=750.50)
        db_session.add_all([a1, a2])
        db_session.flush()
        svc = DashboardService(db_session)
        result = svc.get_consolidated_balance(test_user.id)
        assert result == Decimal("1250.50")

    def test_soft_deleted_account_ignored(self, db_session, test_user: User) -> None:
        deleted = BankAccount(user_id=test_user.id, balance=999.00, deleted_at=datetime.now(UTC))
        db_session.add(deleted)
        db_session.flush()
        svc = DashboardService(db_session)
        result = svc.get_consolidated_balance(test_user.id)
        assert result == Decimal("0")


class TestMonthlyExpenses:
    def test_empty_month_returns_zero(
        self, db_session, test_user: User, test_account: BankAccount
    ) -> None:
        svc = DashboardService(db_session)
        result = svc.get_monthly_expenses(test_user.id, "2025-01")
        assert result == Decimal("0")

    def test_only_negative_amounts_counted(
        self, db_session, test_user: User, test_account: BankAccount
    ) -> None:
        db_session.add(
            Transaction(
                account_id=test_account.id, amount=-50.00, transaction_date=date(2025, 3, 1)
            )
        )
        db_session.add(
            Transaction(
                account_id=test_account.id, amount=200.00, transaction_date=date(2025, 3, 15)
            )
        )
        db_session.flush()
        svc = DashboardService(db_session)
        result = svc.get_monthly_expenses(test_user.id, "2025-03")
        assert result == Decimal("50.00")

    def test_other_months_excluded(
        self, db_session, test_user: User, test_account: BankAccount
    ) -> None:
        db_session.add(
            Transaction(
                account_id=test_account.id, amount=-100.00, transaction_date=date(2025, 3, 1)
            )
        )
        db_session.add(
            Transaction(
                account_id=test_account.id, amount=-200.00, transaction_date=date(2025, 4, 1)
            )
        )
        db_session.flush()
        svc = DashboardService(db_session)
        assert svc.get_monthly_expenses(test_user.id, "2025-03") == Decimal("100.00")
        assert svc.get_monthly_expenses(test_user.id, "2025-04") == Decimal("200.00")


class TestMonthlyComparison:
    def _mock_today(self, monkeypatch, fake_today: date) -> None:
        mock_date = MagicMock(wraps=date)
        mock_date.today.return_value = fake_today
        monkeypatch.setattr(svc_module, "date", mock_date)

    def test_delta_positive_when_more_spending(
        self, db_session, test_user: User, test_account: BankAccount, monkeypatch
    ) -> None:
        # Mars: -100, Avril: -200 → delta = +100%
        db_session.add(
            Transaction(
                account_id=test_account.id, amount=-100.00, transaction_date=date(2025, 3, 10)
            )
        )
        db_session.add(
            Transaction(
                account_id=test_account.id, amount=-200.00, transaction_date=date(2025, 4, 10)
            )
        )
        db_session.flush()
        self._mock_today(monkeypatch, date(2025, 4, 15))

        svc = DashboardService(db_session)
        result = svc.get_monthly_comparison(test_user.id)

        assert result["current"] == Decimal("200.00")
        assert result["previous"] == Decimal("100.00")
        assert result["delta_pct"] == 100.0

    def test_delta_negative_when_less_spending(
        self, db_session, test_user: User, test_account: BankAccount, monkeypatch
    ) -> None:
        # Mars: -200, Avril: -100 → delta = -50%
        db_session.add(
            Transaction(
                account_id=test_account.id, amount=-200.00, transaction_date=date(2025, 3, 10)
            )
        )
        db_session.add(
            Transaction(
                account_id=test_account.id, amount=-100.00, transaction_date=date(2025, 4, 10)
            )
        )
        db_session.flush()
        self._mock_today(monkeypatch, date(2025, 4, 15))

        svc = DashboardService(db_session)
        result = svc.get_monthly_comparison(test_user.id)
        assert result["delta_pct"] == -50.0

    def test_delta_zero_when_no_previous_month(
        self, db_session, test_user: User, test_account: BankAccount, monkeypatch
    ) -> None:
        db_session.add(
            Transaction(
                account_id=test_account.id, amount=-150.00, transaction_date=date(2025, 4, 10)
            )
        )
        db_session.flush()
        self._mock_today(monkeypatch, date(2025, 4, 15))

        svc = DashboardService(db_session)
        result = svc.get_monthly_comparison(test_user.id)
        assert result["previous"] == Decimal("0")
        assert result["delta_pct"] == 0.0


class TestCategoriesBreakdown:
    def test_basic_breakdown(self, db_session, test_user: User, test_account: BankAccount) -> None:
        cat = Category(name="Alimentation")
        db_session.add(cat)
        db_session.flush()
        db_session.add(
            Transaction(
                account_id=test_account.id,
                amount=-100.00,
                transaction_date=date(2025, 3, 1),
                category_id=cat.id,
            )
        )
        db_session.flush()
        svc = DashboardService(db_session)
        result = svc.get_categories_breakdown(test_user.id, "2025-03")

        assert len(result) == 1
        assert result[0]["category_name"] == "Alimentation"
        assert result[0]["amount"] == Decimal("100.00")
        assert result[0]["percentage"] == 100.0
        assert result[0]["transaction_count"] == 1
        assert result[0]["parent_category_name"] is None

    def test_sorted_by_amount_descending(
        self, db_session, test_user: User, test_account: BankAccount
    ) -> None:
        cat1 = Category(name="Transport")
        cat2 = Category(name="Courses")
        db_session.add_all([cat1, cat2])
        db_session.flush()
        db_session.add(
            Transaction(
                account_id=test_account.id,
                amount=-50.00,
                transaction_date=date(2025, 3, 1),
                category_id=cat1.id,
            )
        )
        db_session.add(
            Transaction(
                account_id=test_account.id,
                amount=-300.00,
                transaction_date=date(2025, 3, 1),
                category_id=cat2.id,
            )
        )
        db_session.flush()
        svc = DashboardService(db_session)
        result = svc.get_categories_breakdown(test_user.id, "2025-03")

        assert len(result) == 2
        assert result[0]["category_name"] == "Courses"  # dépense la plus élevée en premier
        assert result[0]["amount"] == Decimal("300.00")
        assert result[1]["amount"] == Decimal("50.00")
        # Pourcentages : 300/350 ≈ 85.71, 50/350 ≈ 14.29
        assert result[0]["percentage"] == round(300 / 350 * 100, 2)
        assert result[1]["percentage"] == round(50 / 350 * 100, 2)

    def test_uncategorized_transactions_excluded(
        self, db_session, test_user: User, test_account: BankAccount
    ) -> None:
        db_session.add(
            Transaction(
                account_id=test_account.id,
                amount=-75.00,
                transaction_date=date(2025, 3, 1),
                category_id=None,
            )
        )
        db_session.flush()
        svc = DashboardService(db_session)
        result = svc.get_categories_breakdown(test_user.id, "2025-03")
        assert result == []


class TestTopMerchants:
    def test_limit_respected(self, db_session, test_user: User, test_account: BankAccount) -> None:
        merchants = [Merchant(name=f"Shop{i}") for i in range(4)]
        db_session.add_all(merchants)
        db_session.flush()
        for m in merchants:
            db_session.add(
                Transaction(
                    account_id=test_account.id,
                    merchant_id=m.id,
                    amount=-10.00,
                    transaction_date=date(2025, 3, 1),
                )
            )
        db_session.flush()
        svc = DashboardService(db_session)
        result = svc.get_top_merchants(test_user.id, "2025-03", limit=2)
        assert len(result) == 2

    def test_excludes_transactions_without_merchant(
        self, db_session, test_user: User, test_account: BankAccount
    ) -> None:
        db_session.add(
            Transaction(
                account_id=test_account.id,
                amount=-100.00,
                transaction_date=date(2025, 3, 1),
                merchant_id=None,
            )
        )
        db_session.flush()
        svc = DashboardService(db_session)
        result = svc.get_top_merchants(test_user.id, "2025-03")
        assert result == []


class TestRecurringSubscriptions:
    def _make_rule(
        self,
        db_session,
        test_account: BankAccount,
        name: str,
        frequency: str,
        last_detected: date | None,
        expected_amount: float | None = None,
    ) -> RecurringRule:
        merchant = Merchant(name=name)
        db_session.add(merchant)
        db_session.flush()
        db_session.add(
            Transaction(
                account_id=test_account.id,
                merchant_id=merchant.id,
                amount=-10.00,
                transaction_date=date(2025, 3, 1),
            )
        )
        rule = RecurringRule(
            merchant_id=merchant.id,
            expected_amount=expected_amount,
            frequency=frequency,
            last_detected=last_detected,
        )
        db_session.add(rule)
        db_session.flush()
        return rule

    def test_monthly_next_expected(
        self, db_session, test_user: User, test_account: BankAccount
    ) -> None:
        self._make_rule(db_session, test_account, "Netflix", "monthly", date(2025, 3, 1), -15.00)
        svc = DashboardService(db_session)
        result = svc.get_recurring_subscriptions(test_user.id)

        assert len(result) == 1
        assert result[0]["merchant_name"] == "Netflix"
        assert result[0]["frequency"] == "monthly"
        assert result[0]["next_expected"] == date(2025, 4, 1)
        assert result[0]["expected_amount"] == Decimal("15.00")

    def test_yearly_next_expected(
        self, db_session, test_user: User, test_account: BankAccount
    ) -> None:
        self._make_rule(
            db_session, test_account, "Amazon Prime", "yearly", date(2025, 3, 1), -99.00
        )
        svc = DashboardService(db_session)
        result = svc.get_recurring_subscriptions(test_user.id)

        assert len(result) == 1
        assert result[0]["next_expected"] == date(2026, 3, 1)

    def test_no_last_detected_gives_null_next(
        self, db_session, test_user: User, test_account: BankAccount
    ) -> None:
        self._make_rule(db_session, test_account, "Gym", "monthly", None)
        svc = DashboardService(db_session)
        result = svc.get_recurring_subscriptions(test_user.id)

        assert len(result) == 1
        assert result[0]["next_expected"] is None
