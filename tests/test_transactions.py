import io
from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from core.security import create_access_token
from model.models import AuditLog, BankAccount, Merchant, Tag, Transaction, User

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
            description="CARREFOUR CITY",
        ),
        Transaction(
            account_id=test_account.id,
            amount=1000.00,
            transaction_date=date(2025, 3, 2),
            description="Virement reçu",
        ),
        Transaction(
            account_id=test_account.id,
            amount=-20.00,
            transaction_date=date(2025, 3, 3),
            description="NETFLIX ABONNEMENT",
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
        assert "next_cursor" in data
        assert "page_size" in data
        assert len(data["items"]) == 3

    def test_list_cursor_pagination(
        self, client: TestClient, auth_headers: dict, test_transactions
    ) -> None:
        # Page 1 : 2 items
        r1 = client.get("/api/v1/transactions?page_size=2", headers=auth_headers)
        assert r1.status_code == 200
        data1 = r1.json()
        assert len(data1["items"]) == 2
        assert data1["next_cursor"] is not None

        # Page 2 via cursor
        r2 = client.get(
            f"/api/v1/transactions?page_size=2&cursor={data1['next_cursor']}",
            headers=auth_headers,
        )
        assert r2.status_code == 200
        data2 = r2.json()
        assert len(data2["items"]) == 1
        assert data2["next_cursor"] is None

        # Pas de doublon entre les deux pages
        ids1 = {i["id"] for i in data1["items"]}
        ids2 = {i["id"] for i in data2["items"]}
        assert ids1.isdisjoint(ids2)

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
        assert len(data["items"]) == 3

    def test_list_filter_by_date(
        self, client: TestClient, auth_headers: dict, test_transactions
    ) -> None:
        response = client.get(
            "/api/v1/transactions?date_from=2025-03-02&date_to=2025-03-02",
            headers=auth_headers,
        )
        data = response.json()
        assert len(data["items"]) == 1
        assert float(data["items"][0]["amount"]) == 1000.00

    def test_list_filter_by_amount_min(
        self, client: TestClient, auth_headers: dict, test_transactions
    ) -> None:
        response = client.get(
            "/api/v1/transactions?amount_min=0",
            headers=auth_headers,
        )
        data = response.json()
        assert len(data["items"]) == 1  # Seul 1000.00 est >= 0

    def test_list_filter_by_amount_max(
        self, client: TestClient, auth_headers: dict, test_transactions
    ) -> None:
        response = client.get(
            "/api/v1/transactions?amount_max=-25",
            headers=auth_headers,
        )
        data = response.json()
        assert len(data["items"]) == 1  # Seul -50.00 est <= -25

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
        assert len(data["items"]) == 1
        assert data["items"][0]["category_id"] == str(cat_id)

    def test_list_filter_by_merchant(
        self,
        client: TestClient,
        auth_headers: dict,
        test_account: BankAccount,
        db_session,
    ) -> None:
        merchant = Merchant(name="Netflix", normalized_name="netflix")
        db_session.add(merchant)
        db_session.flush()
        txn = Transaction(
            account_id=test_account.id,
            amount=-14.99,
            transaction_date=date(2025, 3, 15),
            merchant_id=merchant.id,
        )
        db_session.add(txn)
        db_session.flush()

        response = client.get(
            f"/api/v1/transactions?merchant_id={merchant.id}",
            headers=auth_headers,
        )
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["merchant_id"] == str(merchant.id)

    def test_list_filter_by_tag(
        self,
        client: TestClient,
        auth_headers: dict,
        test_account: BankAccount,
        db_session,
        test_transactions,
    ) -> None:
        tag = Tag(name=f"tag_filter_{uuid4().hex[:6]}")
        db_session.add(tag)
        db_session.flush()
        # Attacher le tag à la première transaction
        test_transactions[0].tags.append(tag)
        db_session.flush()

        response = client.get(
            f"/api/v1/transactions?tag_id={tag.id}",
            headers=auth_headers,
        )
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == str(test_transactions[0].id)

    def test_list_items_include_tags(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session,
        test_transactions,
    ) -> None:
        tag = Tag(name=f"tag_include_{uuid4().hex[:6]}")
        db_session.add(tag)
        db_session.flush()
        test_transactions[0].tags.append(tag)
        db_session.flush()

        response = client.get("/api/v1/transactions", headers=auth_headers)
        data = response.json()
        tagged = next(i for i in data["items"] if i["id"] == str(test_transactions[0].id))
        assert len(tagged["tags"]) == 1
        assert tagged["tags"][0]["name"] == tag.name

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
        assert len(data["items"]) == 3  # Seulement les 3 transactions du test_user

    def test_list_invalid_cursor_returns_400(self, client: TestClient, auth_headers: dict) -> None:
        response = client.get("/api/v1/transactions?cursor=invalid", headers=auth_headers)
        assert response.status_code == 400


class TestSearchTransactions:
    def test_search_by_description(
        self, client: TestClient, auth_headers: dict, test_transactions
    ) -> None:
        response = client.get("/api/v1/transactions/search?q=NETFLIX", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert "NETFLIX" in data["items"][0]["description"]

    def test_search_by_merchant_name(
        self,
        client: TestClient,
        auth_headers: dict,
        test_account: BankAccount,
        db_session,
    ) -> None:
        merchant = Merchant(name="Spotify", normalized_name="spotify")
        db_session.add(merchant)
        db_session.flush()
        txn = Transaction(
            account_id=test_account.id,
            amount=-9.99,
            transaction_date=date(2025, 3, 20),
            merchant_id=merchant.id,
            description="Paiement CB",
        )
        db_session.add(txn)
        db_session.flush()

        response = client.get("/api/v1/transactions/search?q=spotify", headers=auth_headers)
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["merchant_id"] == str(merchant.id)

    def test_search_case_insensitive(
        self, client: TestClient, auth_headers: dict, test_transactions
    ) -> None:
        response = client.get("/api/v1/transactions/search?q=carrefour", headers=auth_headers)
        data = response.json()
        assert len(data["items"]) == 1

    def test_search_no_results(
        self, client: TestClient, auth_headers: dict, test_transactions
    ) -> None:
        response = client.get("/api/v1/transactions/search?q=zzznoresult", headers=auth_headers)
        data = response.json()
        assert len(data["items"]) == 0
        assert data["next_cursor"] is None

    def test_search_requires_auth(self, client: TestClient) -> None:
        response = client.get("/api/v1/transactions/search?q=test")
        assert response.status_code == 401

    def test_search_cursor_pagination(
        self, client: TestClient, auth_headers: dict, test_transactions
    ) -> None:
        # Tous les 3 contiennent au moins une lettre commune — chercher "e" (virement, netflix...)
        r1 = client.get("/api/v1/transactions/search?q=e&page_size=2", headers=auth_headers)
        data1 = r1.json()
        if data1["next_cursor"]:
            r2 = client.get(
                f"/api/v1/transactions/search?q=e&page_size=2&cursor={data1['next_cursor']}",
                headers=auth_headers,
            )
            assert r2.status_code == 200


class TestBulkTag:
    def test_bulk_tag_returns_204(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session,
        test_transactions,
    ) -> None:
        tag = Tag(name=f"bulk_{uuid4().hex[:6]}")
        db_session.add(tag)
        db_session.flush()

        payload = {
            "transaction_ids": [str(test_transactions[0].id), str(test_transactions[1].id)],
            "tag_ids": [str(tag.id)],
        }
        response = client.post("/api/v1/transactions/bulk-tag", json=payload, headers=auth_headers)
        assert response.status_code == 204

    def test_bulk_tag_attaches_tags(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session,
        test_transactions,
    ) -> None:
        tag = Tag(name=f"attach_{uuid4().hex[:6]}")
        db_session.add(tag)
        db_session.flush()

        payload = {
            "transaction_ids": [str(test_transactions[0].id)],
            "tag_ids": [str(tag.id)],
        }
        client.post("/api/v1/transactions/bulk-tag", json=payload, headers=auth_headers)

        db_session.expire_all()
        txn = db_session.get(Transaction, test_transactions[0].id)
        assert any(t.id == tag.id for t in txn.tags)

    def test_bulk_tag_idempotent(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session,
        test_transactions,
    ) -> None:
        tag = Tag(name=f"idem_{uuid4().hex[:6]}")
        db_session.add(tag)
        db_session.flush()
        payload = {
            "transaction_ids": [str(test_transactions[0].id)],
            "tag_ids": [str(tag.id)],
        }
        client.post("/api/v1/transactions/bulk-tag", json=payload, headers=auth_headers)
        # Deuxième appel identique — ne doit pas lever d'erreur
        response = client.post("/api/v1/transactions/bulk-tag", json=payload, headers=auth_headers)
        assert response.status_code == 204

    def test_bulk_tag_404_unknown_tag(
        self,
        client: TestClient,
        auth_headers: dict,
        test_transactions,
    ) -> None:
        payload = {
            "transaction_ids": [str(test_transactions[0].id)],
            "tag_ids": [str(uuid4())],
        }
        response = client.post("/api/v1/transactions/bulk-tag", json=payload, headers=auth_headers)
        assert response.status_code == 404

    def test_bulk_tag_404_foreign_transaction(
        self,
        client: TestClient,
        auth_headers: dict,
        another_user: User,
        db_session,
    ) -> None:
        other_account = BankAccount(user_id=another_user.id, account_name="Autre")
        db_session.add(other_account)
        db_session.flush()
        other_txn = Transaction(
            account_id=other_account.id,
            amount=-10.00,
            transaction_date=date(2025, 3, 1),
        )
        tag = Tag(name=f"foreign_{uuid4().hex[:6]}")
        db_session.add_all([other_txn, tag])
        db_session.flush()

        payload = {
            "transaction_ids": [str(other_txn.id)],
            "tag_ids": [str(tag.id)],
        }
        response = client.post("/api/v1/transactions/bulk-tag", json=payload, headers=auth_headers)
        assert response.status_code == 404

    def test_bulk_tag_requires_auth(self, client: TestClient, test_transactions) -> None:
        response = client.post(
            "/api/v1/transactions/bulk-tag",
            json={"transaction_ids": [], "tag_ids": []},
        )
        assert response.status_code == 401


class TestExportTransactions:
    def test_export_csv_returns_200(
        self, client: TestClient, auth_headers: dict, test_transactions
    ) -> None:
        response = client.get("/api/v1/transactions/export?format=csv", headers=auth_headers)
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

    def test_export_csv_columns(
        self, client: TestClient, auth_headers: dict, test_transactions
    ) -> None:
        response = client.get("/api/v1/transactions/export?format=csv", headers=auth_headers)
        lines = response.text.strip().split("\n")
        header = lines[0]
        assert "date" in header
        assert "description" in header
        assert "montant" in header
        assert "categorie" in header
        assert "tags" in header

    def test_export_csv_row_count(
        self, client: TestClient, auth_headers: dict, test_transactions
    ) -> None:
        response = client.get("/api/v1/transactions/export?format=csv", headers=auth_headers)
        lines = [line for line in response.text.strip().split("\n") if line]
        # 1 header + 3 transactions
        assert len(lines) == 4

    def test_export_csv_includes_tags(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session,
        test_transactions,
    ) -> None:
        tag = Tag(name=f"export_tag_{uuid4().hex[:6]}")
        db_session.add(tag)
        db_session.flush()
        test_transactions[0].tags.append(tag)
        db_session.flush()

        response = client.get("/api/v1/transactions/export?format=csv", headers=auth_headers)
        assert tag.name in response.text

    def test_export_invalid_format_returns_400(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        response = client.get("/api/v1/transactions/export?format=json", headers=auth_headers)
        assert response.status_code == 400

    def test_export_requires_auth(self, client: TestClient) -> None:
        response = client.get("/api/v1/transactions/export?format=csv")
        assert response.status_code == 401

    def test_export_respects_filters(
        self, client: TestClient, auth_headers: dict, test_transactions
    ) -> None:
        response = client.get(
            "/api/v1/transactions/export?format=csv&date_from=2025-03-02&date_to=2025-03-02",
            headers=auth_headers,
        )
        lines = [line for line in response.text.strip().split("\n") if line]
        # 1 header + 1 transaction
        assert len(lines) == 2


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
