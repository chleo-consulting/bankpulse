import io
from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from core.security import create_access_token
from model.models import AuditLog, BankAccount, Transaction, User

# CSV avec une transaction CARREFOUR pour tester l'auto-catégorisation
IMPORT_CSV_CARREFOUR = b"""\
"dateOp","dateVal","label","category","categoryParent","amount","comment","accountNum","accountLabel","accountbalance","CB","supplierFound"
"2025-03-01","2025-03-01","CARTE CARREFOUR CITY","Alimentation","Vie quotidienne",-50.00,"","AUTOCATEG_ACC_001","Compte Test",500.00,"CB","carrefour"
"""


@pytest.fixture
def test_user(db_session) -> User:
    user = User(
        email=f"txn_{uuid4().hex[:8]}@example.com",
        password_hash="hashed",
    )
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def another_user(db_session) -> User:
    user = User(
        email=f"other_txn_{uuid4().hex[:8]}@example.com",
        password_hash="hashed",
    )
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def test_account(db_session, test_user: User) -> BankAccount:
    account = BankAccount(user_id=test_user.id, account_name="Compte Test")
    db_session.add(account)
    db_session.flush()
    return account


@pytest.fixture
def test_transactions(db_session, test_account: BankAccount) -> list[Transaction]:
    txns = [
        Transaction(
            account_id=test_account.id,
            amount=-50.00,
            transaction_date=date(2025, 3, 1),
        ),
        Transaction(
            account_id=test_account.id,
            amount=1000.00,
            transaction_date=date(2025, 3, 2),
        ),
        Transaction(
            account_id=test_account.id,
            amount=-20.00,
            transaction_date=date(2025, 3, 3),
        ),
    ]
    db_session.add_all(txns)
    db_session.flush()
    return txns


class TestListTransactions:
    def test_list_returns_200(
        self, client: TestClient, auth_headers: dict, test_transactions
    ) -> None:
        response = client.get("/api/v1/transactions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert data["total"] == 3

    def test_list_filter_by_account(
        self,
        client: TestClient,
        auth_headers: dict,
        test_account: BankAccount,
        test_transactions,
    ) -> None:
        response = client.get(
            f"/api/v1/transactions?account_id={test_account.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3

    def test_list_filter_by_date(
        self, client: TestClient, auth_headers: dict, test_transactions
    ) -> None:
        response = client.get(
            "/api/v1/transactions?date_from=2025-03-02&date_to=2025-03-02",
            headers=auth_headers,
        )
        data = response.json()
        assert data["total"] == 1
        assert float(data["items"][0]["amount"]) == 1000.00

    def test_list_filter_by_amount_min(
        self, client: TestClient, auth_headers: dict, test_transactions
    ) -> None:
        response = client.get(
            "/api/v1/transactions?amount_min=0",
            headers=auth_headers,
        )
        data = response.json()
        assert data["total"] == 1  # Seul 1000.00 est >= 0

    def test_list_filter_by_amount_max(
        self, client: TestClient, auth_headers: dict, test_transactions
    ) -> None:
        response = client.get(
            "/api/v1/transactions?amount_max=-25",
            headers=auth_headers,
        )
        data = response.json()
        assert data["total"] == 1  # Seul -50.00 est <= -25

    def test_list_filter_by_category(
        self,
        client: TestClient,
        auth_headers: dict,
        test_account: BankAccount,
        db_session,
        seed_categories,
    ) -> None:
        cat_id = seed_categories["supermarche"].id
        txn = Transaction(
            account_id=test_account.id,
            amount=-30.00,
            transaction_date=date(2025, 3, 10),
            category_id=cat_id,
        )
        db_session.add(txn)
        db_session.flush()

        response = client.get(
            f"/api/v1/transactions?category_id={cat_id}",
            headers=auth_headers,
        )
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["category_id"] == str(cat_id)

    def test_list_pagination(
        self, client: TestClient, auth_headers: dict, test_transactions
    ) -> None:
        response = client.get(
            "/api/v1/transactions?page=1&page_size=2",
            headers=auth_headers,
        )
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 2

    def test_list_requires_auth(self, client: TestClient) -> None:
        response = client.get("/api/v1/transactions")
        assert response.status_code == 401

    def test_list_isolation_between_users(
        self,
        client: TestClient,
        auth_headers: dict,
        another_user: User,
        db_session,
        test_transactions,
    ) -> None:
        other_account = BankAccount(user_id=another_user.id, account_name="Autre")
        db_session.add(other_account)
        db_session.flush()
        other_txn = Transaction(
            account_id=other_account.id,
            amount=-100.00,
            transaction_date=date(2025, 3, 1),
        )
        db_session.add(other_txn)
        db_session.flush()

        response = client.get("/api/v1/transactions", headers=auth_headers)
        data = response.json()
        txn_ids = [t["id"] for t in data["items"]]
        assert str(other_txn.id) not in txn_ids
        assert data["total"] == 3  # Seulement les 3 transactions du test_user


class TestPatchTransactionCategory:
    def test_patch_category_returns_200(
        self,
        client: TestClient,
        auth_headers: dict,
        test_transactions,
        seed_categories,
    ) -> None:
        txn_id = test_transactions[0].id
        cat_id = seed_categories["supermarche"].id

        response = client.patch(
            f"/api/v1/transactions/{txn_id}/category",
            json={"category_id": str(cat_id)},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["category_id"] == str(cat_id)

    def test_patch_category_creates_audit_log(
        self,
        client: TestClient,
        auth_headers: dict,
        test_transactions,
        seed_categories,
        db_session,
    ) -> None:
        txn_id = test_transactions[0].id
        cat_id = seed_categories["supermarche"].id

        client.patch(
            f"/api/v1/transactions/{txn_id}/category",
            json={"category_id": str(cat_id)},
            headers=auth_headers,
        )
        audit = (
            db_session.query(AuditLog)
            .filter(AuditLog.entity_id == txn_id, AuditLog.action == "UPDATE")
            .first()
        )
        assert audit is not None
        assert audit.new_values["category_id"] == str(cat_id)

    def test_patch_category_null_uncategorizes(
        self,
        client: TestClient,
        auth_headers: dict,
        test_account: BankAccount,
        db_session,
        seed_categories,
    ) -> None:
        cat_id = seed_categories["supermarche"].id
        txn = Transaction(
            account_id=test_account.id,
            amount=-30.00,
            transaction_date=date(2025, 3, 10),
            category_id=cat_id,
        )
        db_session.add(txn)
        db_session.flush()

        response = client.patch(
            f"/api/v1/transactions/{txn.id}/category",
            json={"category_id": None},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["category_id"] is None

    def test_patch_category_404_unknown_transaction(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        response = client.patch(
            f"/api/v1/transactions/{uuid4()}/category",
            json={"category_id": None},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_patch_category_404_invalid_category(
        self, client: TestClient, auth_headers: dict, test_transactions
    ) -> None:
        txn_id = test_transactions[0].id
        response = client.patch(
            f"/api/v1/transactions/{txn_id}/category",
            json={"category_id": str(uuid4())},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_patch_category_requires_auth(self, client: TestClient, test_transactions) -> None:
        txn_id = test_transactions[0].id
        response = client.patch(
            f"/api/v1/transactions/{txn_id}/category",
            json={"category_id": None},
        )
        assert response.status_code == 401


class TestAutoCategorizationOnImport:
    def test_import_auto_categorizes_matching_transaction(
        self, client: TestClient, auth_headers: dict, db_session, seed_rules
    ) -> None:
        """Une transaction avec merchant 'carrefour' doit être catégorisée en Supermarché."""
        response = client.post(
            "/api/v1/import/boursorama",
            files={"file": ("test.csv", io.BytesIO(IMPORT_CSV_CARREFOUR), "text/csv")},
            headers=auth_headers,
        )
        assert response.status_code == 200

        # La règle CARREFOUR → Supermarché doit avoir été appliquée
        txns = db_session.query(Transaction).all()
        carrefour_txns = [t for t in txns if t.description and "CARREFOUR" in t.description.upper()]
        assert len(carrefour_txns) >= 1
        assert carrefour_txns[0].category_id == seed_rules[0].category_id
