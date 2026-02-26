from datetime import date
from uuid import uuid4

import pytest

from core.security import create_access_token
from model.models import BankAccount, Category, Merchant, RecurringRule, Transaction, User


@pytest.fixture
def test_user(db_session) -> User:
    user = User(email=f"dash_api_{uuid4().hex[:8]}@test.com", password_hash="x")
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_account(db_session, test_user: User) -> BankAccount:
    account = BankAccount(user_id=test_user.id, account_name="Compte Test", balance=1500.00)
    db_session.add(account)
    db_session.flush()
    return account


# --- /summary ---


def test_get_summary_returns_200(client, auth_headers, test_account) -> None:
    response = client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_balance" in data
    assert "expenses" in data
    assert "current" in data["expenses"]
    assert "previous" in data["expenses"]
    assert "delta_pct" in data["expenses"]


def test_summary_requires_auth(client) -> None:
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 401


def test_summary_with_no_data(client, db_session) -> None:
    new_user = User(email=f"empty_{uuid4().hex[:8]}@test.com", password_hash="x")
    db_session.add(new_user)
    db_session.flush()
    headers = {"Authorization": f"Bearer {create_access_token(str(new_user.id))}"}

    response = client.get("/api/v1/dashboard/summary", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert float(data["total_balance"]) == 0.0
    assert float(data["expenses"]["current"]) == 0.0
    assert float(data["expenses"]["previous"]) == 0.0
    assert data["expenses"]["delta_pct"] == 0.0


# --- /categories-breakdown ---


def test_categories_breakdown_filters_by_month(
    client, auth_headers, test_account, db_session
) -> None:
    cat = Category(name="Loisirs")
    db_session.add(cat)
    db_session.flush()
    db_session.add(
        Transaction(
            account_id=test_account.id,
            amount=-50.00,
            transaction_date=date(2025, 3, 1),
            category_id=cat.id,
        )
    )
    db_session.flush()

    response = client.get(
        "/api/v1/dashboard/categories-breakdown?month=2025-03", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["month"] == "2025-03"
    assert len(data["items"]) == 1
    assert data["items"][0]["category_name"] == "Loisirs"
    assert float(data["total_amount"]) == 50.0


def test_categories_breakdown_empty_month(client, auth_headers, test_account) -> None:
    response = client.get(
        "/api/v1/dashboard/categories-breakdown?month=2020-01", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert float(data["total_amount"]) == 0.0


def test_categories_breakdown_invalid_month_format(client, auth_headers) -> None:
    response = client.get(
        "/api/v1/dashboard/categories-breakdown?month=invalid", headers=auth_headers
    )
    assert response.status_code == 422


def test_categories_breakdown_requires_auth(client) -> None:
    response = client.get("/api/v1/dashboard/categories-breakdown")
    assert response.status_code == 401


# --- /top-merchants ---


def test_top_merchants_respects_limit(client, auth_headers, test_account, db_session) -> None:
    merchants = [Merchant(name=f"Boutique{i}") for i in range(5)]
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

    response = client.get(
        "/api/v1/dashboard/top-merchants?month=2025-03&limit=3", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["month"] == "2025-03"
    assert len(data["items"]) == 3


def test_top_merchants_limit_out_of_range(client, auth_headers) -> None:
    response = client.get("/api/v1/dashboard/top-merchants?limit=99", headers=auth_headers)
    assert response.status_code == 422


def test_top_merchants_requires_auth(client) -> None:
    response = client.get("/api/v1/dashboard/top-merchants")
    assert response.status_code == 401


# --- /recurring ---


def test_recurring_returns_200(client, auth_headers) -> None:
    response = client.get("/api/v1/dashboard/recurring", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_recurring_with_data(client, auth_headers, test_account, db_session) -> None:
    merchant = Merchant(name="Spotify")
    db_session.add(merchant)
    db_session.flush()
    db_session.add(
        Transaction(
            account_id=test_account.id,
            merchant_id=merchant.id,
            amount=-9.99,
            transaction_date=date(2025, 3, 1),
        )
    )
    rule = RecurringRule(
        merchant_id=merchant.id,
        expected_amount=-9.99,
        frequency="monthly",
        last_detected=date(2025, 3, 1),
    )
    db_session.add(rule)
    db_session.flush()

    response = client.get("/api/v1/dashboard/recurring", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["merchant_name"] == "Spotify"
    assert data["items"][0]["frequency"] == "monthly"
    assert data["items"][0]["next_expected"] == "2025-04-01"


def test_recurring_requires_auth(client) -> None:
    response = client.get("/api/v1/dashboard/recurring")
    assert response.status_code == 401


# --- isolation utilisateur ---


def test_dashboard_user_isolation(client, db_session) -> None:
    user1 = User(email=f"iso1_{uuid4().hex[:8]}@test.com", password_hash="x")
    user2 = User(email=f"iso2_{uuid4().hex[:8]}@test.com", password_hash="x")
    db_session.add_all([user1, user2])
    db_session.flush()

    acc1 = BankAccount(user_id=user1.id, balance=1500.00)
    acc2 = BankAccount(user_id=user2.id, balance=9999.00)
    db_session.add_all([acc1, acc2])
    db_session.flush()

    headers1 = {"Authorization": f"Bearer {create_access_token(str(user1.id))}"}

    response = client.get("/api/v1/dashboard/summary", headers=headers1)
    assert response.status_code == 200
    data = response.json()
    # user1 voit son solde (1500), pas celui de user2 (9999)
    assert float(data["total_balance"]) == 1500.0
