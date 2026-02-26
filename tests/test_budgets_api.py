from datetime import date
from uuid import uuid4

import pytest

from core.security import create_access_token
from model.models import BankAccount, Budget, Category, Transaction, User

# --- Fixtures locales ---


@pytest.fixture
def test_user(db_session) -> User:
    user = User(email=f"budget_{uuid4().hex[:8]}@test.com", password_hash="x")
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_category(db_session) -> Category:
    cat = Category(name="Alimentation_budget")
    db_session.add(cat)
    db_session.flush()
    return cat


@pytest.fixture
def test_account(db_session, test_user: User) -> BankAccount:
    account = BankAccount(user_id=test_user.id, account_name="Compte Budget", balance=2000.00)
    db_session.add(account)
    db_session.flush()
    return account


@pytest.fixture
def test_budget(db_session, test_user: User, test_category: Category) -> Budget:
    budget = Budget(
        user_id=test_user.id,
        category_id=test_category.id,
        period_type="monthly",
        amount_limit=500.00,
    )
    db_session.add(budget)
    db_session.flush()
    return budget


# --- POST /budgets ---


def test_create_budget_returns_201(client, auth_headers, test_category) -> None:
    response = client.post(
        "/api/v1/budgets",
        json={
            "category_id": str(test_category.id),
            "period_type": "monthly",
            "amount_limit": "500.00",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["period_type"] == "monthly"
    assert float(data["amount_limit"]) == 500.0
    assert "id" in data


def test_create_budget_quarterly(client, auth_headers, test_category) -> None:
    response = client.post(
        "/api/v1/budgets",
        json={
            "category_id": str(test_category.id),
            "period_type": "quarterly",
            "amount_limit": "1500.00",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["period_type"] == "quarterly"


def test_create_budget_yearly(client, auth_headers, test_category) -> None:
    response = client.post(
        "/api/v1/budgets",
        json={
            "category_id": str(test_category.id),
            "period_type": "yearly",
            "amount_limit": "6000.00",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["period_type"] == "yearly"


def test_create_budget_invalid_period_type(client, auth_headers, test_category) -> None:
    response = client.post(
        "/api/v1/budgets",
        json={
            "category_id": str(test_category.id),
            "period_type": "weekly",
            "amount_limit": "100.00",
        },
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_create_budget_negative_limit(client, auth_headers, test_category) -> None:
    response = client.post(
        "/api/v1/budgets",
        json={
            "category_id": str(test_category.id),
            "period_type": "monthly",
            "amount_limit": "-10.00",
        },
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_create_budget_unknown_category(client, auth_headers) -> None:
    response = client.post(
        "/api/v1/budgets",
        json={
            "category_id": str(uuid4()),
            "period_type": "monthly",
            "amount_limit": "200.00",
        },
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_create_budget_requires_auth(client, test_category) -> None:
    response = client.post(
        "/api/v1/budgets",
        json={
            "category_id": str(test_category.id),
            "period_type": "monthly",
            "amount_limit": "500.00",
        },
    )
    assert response.status_code == 401


# --- GET /budgets ---


def test_list_budgets_returns_200(client, auth_headers, test_budget) -> None:
    response = client.get("/api/v1/budgets", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(item["id"] == str(test_budget.id) for item in data)


def test_list_budgets_empty_for_new_user(client, db_session) -> None:
    new_user = User(email=f"nobudget_{uuid4().hex[:8]}@test.com", password_hash="x")
    db_session.add(new_user)
    db_session.flush()
    headers = {"Authorization": f"Bearer {create_access_token(str(new_user.id))}"}
    response = client.get("/api/v1/budgets", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_list_budgets_requires_auth(client) -> None:
    response = client.get("/api/v1/budgets")
    assert response.status_code == 401


# --- GET /budgets/{id} ---


def test_get_budget_by_id(client, auth_headers, test_budget) -> None:
    response = client.get(f"/api/v1/budgets/{test_budget.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_budget.id)
    assert data["period_type"] == "monthly"
    assert float(data["amount_limit"]) == 500.0


def test_get_budget_not_found(client, auth_headers) -> None:
    response = client.get(f"/api/v1/budgets/{uuid4()}", headers=auth_headers)
    assert response.status_code == 404


def test_get_budget_user_isolation(client, db_session, test_category) -> None:
    """Un utilisateur ne peut pas accéder aux budgets d'un autre."""
    other_user = User(email=f"other_{uuid4().hex[:8]}@test.com", password_hash="x")
    db_session.add(other_user)
    db_session.flush()
    budget = Budget(
        user_id=other_user.id,
        category_id=test_category.id,
        period_type="monthly",
        amount_limit=300.00,
    )
    db_session.add(budget)
    db_session.flush()

    # Connecté en tant qu'un autre utilisateur
    attacker = User(email=f"attacker_{uuid4().hex[:8]}@test.com", password_hash="x")
    db_session.add(attacker)
    db_session.flush()
    headers = {"Authorization": f"Bearer {create_access_token(str(attacker.id))}"}

    response = client.get(f"/api/v1/budgets/{budget.id}", headers=headers)
    assert response.status_code == 404


# --- PATCH /budgets/{id} ---


def test_update_budget_amount_limit(client, auth_headers, test_budget) -> None:
    response = client.patch(
        f"/api/v1/budgets/{test_budget.id}",
        json={"amount_limit": "750.00"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert float(response.json()["amount_limit"]) == 750.0


def test_update_budget_period_type(client, auth_headers, test_budget) -> None:
    response = client.patch(
        f"/api/v1/budgets/{test_budget.id}",
        json={"period_type": "quarterly"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["period_type"] == "quarterly"


def test_update_budget_not_found(client, auth_headers) -> None:
    response = client.patch(
        f"/api/v1/budgets/{uuid4()}",
        json={"amount_limit": "100.00"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_update_budget_invalid_period_type(client, auth_headers, test_budget) -> None:
    response = client.patch(
        f"/api/v1/budgets/{test_budget.id}",
        json={"period_type": "bimonthly"},
        headers=auth_headers,
    )
    assert response.status_code == 422


# --- DELETE /budgets/{id} ---


def test_delete_budget_returns_204(client, auth_headers, test_budget) -> None:
    response = client.delete(f"/api/v1/budgets/{test_budget.id}", headers=auth_headers)
    assert response.status_code == 204


def test_delete_budget_soft_deletes(client, auth_headers, test_budget, db_session) -> None:
    client.delete(f"/api/v1/budgets/{test_budget.id}", headers=auth_headers)
    db_session.expire(test_budget)
    db_session.refresh(test_budget)
    assert test_budget.deleted_at is not None


def test_delete_budget_not_visible_after_deletion(client, auth_headers, test_budget) -> None:
    client.delete(f"/api/v1/budgets/{test_budget.id}", headers=auth_headers)
    response = client.get(f"/api/v1/budgets/{test_budget.id}", headers=auth_headers)
    assert response.status_code == 404


def test_delete_budget_not_found(client, auth_headers) -> None:
    response = client.delete(f"/api/v1/budgets/{uuid4()}", headers=auth_headers)
    assert response.status_code == 404


# --- GET /budgets/progress ---


def test_get_progress_empty(client, auth_headers) -> None:
    response = client.get("/api/v1/budgets/progress", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["month"] is None


def test_get_progress_with_month_param(client, auth_headers) -> None:
    response = client.get("/api/v1/budgets/progress?month=2025-03", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["month"] == "2025-03"


def test_get_progress_invalid_month_format(client, auth_headers) -> None:
    response = client.get("/api/v1/budgets/progress?month=march-2025", headers=auth_headers)
    assert response.status_code == 422


def test_get_progress_no_spending(client, auth_headers, test_budget, test_account) -> None:
    """Budget sans transaction : spent=0, pct=0, alert=None."""
    response = client.get("/api/v1/budgets/progress?month=2025-01", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) >= 1
    budget_item = next(i for i in items if i["budget_id"] == str(test_budget.id))
    assert float(budget_item["spent"]) == 0.0
    assert budget_item["pct"] == 0.0
    assert budget_item["alert"] is None


def test_get_progress_near_limit(
    client, auth_headers, test_budget, test_account, test_category, db_session
) -> None:
    """Dépenses > 80% du budget → alert='near_limit'."""
    # 420 / 500 = 84% → near_limit
    db_session.add(
        Transaction(
            account_id=test_account.id,
            amount=-420.00,
            transaction_date=date(2025, 6, 15),
            category_id=test_category.id,
        )
    )
    db_session.flush()

    response = client.get("/api/v1/budgets/progress?month=2025-06", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()["items"]
    budget_item = next(i for i in items if i["budget_id"] == str(test_budget.id))
    assert float(budget_item["spent"]) == 420.0
    assert budget_item["alert"] == "near_limit"


def test_get_progress_over_budget(
    client, auth_headers, test_budget, test_account, test_category, db_session
) -> None:
    """Dépenses > budget → alert='over_budget'."""
    # 600 / 500 = 120% → over_budget
    db_session.add(
        Transaction(
            account_id=test_account.id,
            amount=-600.00,
            transaction_date=date(2025, 7, 10),
            category_id=test_category.id,
        )
    )
    db_session.flush()

    response = client.get("/api/v1/budgets/progress?month=2025-07", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()["items"]
    budget_item = next(i for i in items if i["budget_id"] == str(test_budget.id))
    assert float(budget_item["spent"]) == 600.0
    assert float(budget_item["pct"]) == 120.0
    assert budget_item["alert"] == "over_budget"


def test_get_progress_under_limit(
    client, auth_headers, test_budget, test_account, test_category, db_session
) -> None:
    """Dépenses < 80% du budget → alert=None."""
    # 200 / 500 = 40% → aucune alerte
    db_session.add(
        Transaction(
            account_id=test_account.id,
            amount=-200.00,
            transaction_date=date(2025, 8, 5),
            category_id=test_category.id,
        )
    )
    db_session.flush()

    response = client.get("/api/v1/budgets/progress?month=2025-08", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()["items"]
    budget_item = next(i for i in items if i["budget_id"] == str(test_budget.id))
    assert float(budget_item["spent"]) == 200.0
    assert budget_item["alert"] is None


def test_get_progress_ignores_income(
    client, auth_headers, test_budget, test_account, test_category, db_session
) -> None:
    """Les transactions positives (revenus) ne comptent pas dans les dépenses."""
    db_session.add(
        Transaction(
            account_id=test_account.id,
            amount=300.00,  # revenu
            transaction_date=date(2025, 9, 1),
            category_id=test_category.id,
        )
    )
    db_session.flush()

    response = client.get("/api/v1/budgets/progress?month=2025-09", headers=auth_headers)
    items = response.json()["items"]
    budget_item = next(i for i in items if i["budget_id"] == str(test_budget.id))
    assert float(budget_item["spent"]) == 0.0


def test_get_progress_requires_auth(client) -> None:
    response = client.get("/api/v1/budgets/progress")
    assert response.status_code == 401


def test_get_progress_quarterly(client, db_session, test_category) -> None:
    """Budget trimestriel : agrège sur 3 mois."""
    user = User(email=f"quarterly_{uuid4().hex[:8]}@test.com", password_hash="x")
    db_session.add(user)
    db_session.flush()
    account = BankAccount(user_id=user.id, balance=5000.00)
    db_session.add(account)
    db_session.flush()
    budget = Budget(
        user_id=user.id,
        category_id=test_category.id,
        period_type="quarterly",
        amount_limit=1500.00,
    )
    db_session.add(budget)
    db_session.flush()
    # Transactions dans Q1 2025 (jan, fév, mars)
    for d in [date(2025, 1, 10), date(2025, 2, 15), date(2025, 3, 20)]:
        db_session.add(
            Transaction(
                account_id=account.id,
                amount=-400.00,
                transaction_date=d,
                category_id=test_category.id,
            )
        )
    db_session.flush()

    headers = {"Authorization": f"Bearer {create_access_token(str(user.id))}"}
    # month=2025-02 → Q1 (jan-mars)
    response = client.get("/api/v1/budgets/progress?month=2025-02", headers=headers)
    assert response.status_code == 200
    items = response.json()["items"]
    budget_item = items[0]
    assert float(budget_item["spent"]) == 1200.0  # 3 x 400
    assert budget_item["alert"] == "near_limit"  # 1200/1500 = 80%


def test_get_progress_yearly(client, db_session, test_category) -> None:
    """Budget annuel : agrège sur 12 mois."""
    user = User(email=f"yearly_{uuid4().hex[:8]}@test.com", password_hash="x")
    db_session.add(user)
    db_session.flush()
    account = BankAccount(user_id=user.id, balance=10000.00)
    db_session.add(account)
    db_session.flush()
    budget = Budget(
        user_id=user.id,
        category_id=test_category.id,
        period_type="yearly",
        amount_limit=5000.00,
    )
    db_session.add(budget)
    db_session.flush()
    # 6 transactions x 1000€ dans 2024
    for month in range(1, 7):
        db_session.add(
            Transaction(
                account_id=account.id,
                amount=-1000.00,
                transaction_date=date(2024, month, 15),
                category_id=test_category.id,
            )
        )
    db_session.flush()

    headers = {"Authorization": f"Bearer {create_access_token(str(user.id))}"}
    response = client.get("/api/v1/budgets/progress?month=2024-06", headers=headers)
    assert response.status_code == 200
    items = response.json()["items"]
    budget_item = items[0]
    assert float(budget_item["spent"]) == 6000.0
    assert budget_item["alert"] == "over_budget"
