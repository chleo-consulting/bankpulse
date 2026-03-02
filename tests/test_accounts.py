import io
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from core.security import create_access_token
from model.models import BankAccount, Transaction, User

# CSV minimal pour l'import ciblé (compte ACC_TEST_001) - nouveau format séparateur ";"
IMPORT_CSV = b"""\
dateOp;dateVal;label;category;categoryParent;supplierFound;amount;comment;accountNum;accountLabel;accountbalance
2025-03-01;2025-03-01;CARTE Test;Achats;Shopping;test_merchant;-10,00;;ACC_TEST_001;Compte Test;500.00
2025-03-02;2025-03-02;VIR Salaire;Revenus;Revenus;employeur;1000,00;;ACC_TEST_001;Compte Test;1500.00
"""

LARGE_FILE = b"x" * (10 * 1024 * 1024 + 1)  # 10 Mo + 1 octet


@pytest.fixture
def test_user(db_session) -> User:
    user = User(
        email=f"accounts_{uuid4().hex[:8]}@example.com",
        password_hash="hashed",
        first_name="Test",
        last_name="Accounts",
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
        email=f"other_{uuid4().hex[:8]}@example.com",
        password_hash="hashed",
        first_name="Other",
        last_name="User",
    )
    db_session.add(user)
    db_session.flush()
    return user


def _create_account(client: TestClient, auth_headers: dict, **kwargs) -> dict:
    payload = {"account_name": "Mon Compte", **kwargs}
    response = client.post("/api/v1/accounts", json=payload, headers=auth_headers)
    return response.json()


class TestCreateAccount:
    def test_create_account_returns_201(self, client: TestClient, auth_headers: dict) -> None:
        response = client.post(
            "/api/v1/accounts",
            json={"account_name": "Compte Courant", "iban": "FR7612345678901234567890123"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["account_name"] == "Compte Courant"
        assert data["iban"] == "FR7612345678901234567890123"
        assert "id" in data
        assert "user_id" in data


class TestListAccounts:
    def test_list_accounts_empty(self, client: TestClient, auth_headers: dict) -> None:
        response = client.get("/api/v1/accounts", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_list_accounts_returns_own_only(
        self, client: TestClient, auth_headers: dict, another_user: User, db_session
    ) -> None:
        # Compte de l'autre utilisateur créé directement en DB
        other_account = BankAccount(user_id=another_user.id, account_name="Compte Autre")
        db_session.add(other_account)
        db_session.flush()

        # Compte de l'utilisateur courant via API
        _create_account(client, auth_headers, account_name="Mon Compte")

        response = client.get("/api/v1/accounts", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["account_name"] == "Mon Compte"


class TestGetAccount:
    def test_get_account_returns_200(self, client: TestClient, auth_headers: dict) -> None:
        created = _create_account(client, auth_headers, account_name="Compte Épargne")
        account_id = created["id"]

        response = client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == account_id

    def test_get_account_404_other_user(
        self, client: TestClient, auth_headers: dict, another_user: User, db_session
    ) -> None:
        other_account = BankAccount(user_id=another_user.id, account_name="Compte Autre")
        db_session.add(other_account)
        db_session.flush()

        response = client.get(f"/api/v1/accounts/{other_account.id}", headers=auth_headers)
        assert response.status_code == 404


class TestPatchAccount:
    def test_patch_account_updates_fields(self, client: TestClient, auth_headers: dict) -> None:
        created = _create_account(client, auth_headers, account_name="Ancien Nom")
        account_id = created["id"]
        old_updated_at = created["updated_at"]

        response = client.patch(
            f"/api/v1/accounts/{account_id}",
            json={"account_name": "Nouveau Nom"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["account_name"] == "Nouveau Nom"
        assert data["updated_at"] != old_updated_at

    def test_patch_account_partial_update(self, client: TestClient, auth_headers: dict) -> None:
        created = _create_account(client, auth_headers, account_name="Compte", iban="FR1234567890")
        account_id = created["id"]

        response = client.patch(
            f"/api/v1/accounts/{account_id}",
            json={"account_name": "Nom Mis à Jour"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["account_name"] == "Nom Mis à Jour"
        assert data["iban"] == "FR1234567890"  # inchangé


class TestDeleteAccount:
    def test_delete_account_returns_204(self, client: TestClient, auth_headers: dict) -> None:
        created = _create_account(client, auth_headers)
        account_id = created["id"]

        response = client.delete(f"/api/v1/accounts/{account_id}", headers=auth_headers)
        assert response.status_code == 204

    def test_deleted_account_not_listed(self, client: TestClient, auth_headers: dict) -> None:
        created = _create_account(client, auth_headers)
        account_id = created["id"]

        client.delete(f"/api/v1/accounts/{account_id}", headers=auth_headers)

        response = client.get("/api/v1/accounts", headers=auth_headers)
        assert response.status_code == 200
        ids = [a["id"] for a in response.json()]
        assert account_id not in ids

    def test_delete_then_get_404(self, client: TestClient, auth_headers: dict) -> None:
        created = _create_account(client, auth_headers)
        account_id = created["id"]

        client.delete(f"/api/v1/accounts/{account_id}", headers=auth_headers)

        response = client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
        assert response.status_code == 404


class TestUnauthenticated:
    def test_unauthenticated_list_returns_401(self, client: TestClient) -> None:
        assert client.get("/api/v1/accounts").status_code == 401

    def test_unauthenticated_create_returns_401(self, client: TestClient) -> None:
        assert client.post("/api/v1/accounts", json={}).status_code == 401

    def test_unauthenticated_get_returns_401(self, client: TestClient) -> None:
        assert client.get(f"/api/v1/accounts/{uuid4()}").status_code == 401

    def test_unauthenticated_patch_returns_401(self, client: TestClient) -> None:
        assert client.patch(f"/api/v1/accounts/{uuid4()}", json={}).status_code == 401

    def test_unauthenticated_delete_returns_401(self, client: TestClient) -> None:
        assert client.delete(f"/api/v1/accounts/{uuid4()}").status_code == 401

    def test_unauthenticated_import_returns_401(self, client: TestClient) -> None:
        response = client.post(
            f"/api/v1/accounts/{uuid4()}/import",
            files={"file": ("test.csv", io.BytesIO(b"data"), "text/csv")},
        )
        assert response.status_code == 401


class TestImportToAccount:
    def test_import_to_account_returns_200(self, client: TestClient, auth_headers: dict) -> None:
        created = _create_account(client, auth_headers, iban="ACC_TEST_001")
        account_id = created["id"]

        response = client.post(
            f"/api/v1/accounts/{account_id}/import",
            files={"file": ("test.csv", io.BytesIO(IMPORT_CSV), "text/csv")},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_created" in data
        assert "total_skipped" in data
        assert "total_errors" in data

    def test_import_to_account_creates_transactions(
        self, client: TestClient, auth_headers: dict, db_session
    ) -> None:
        created = _create_account(client, auth_headers, iban="ACC_TEST_001")
        account_id = created["id"]

        response = client.post(
            f"/api/v1/accounts/{account_id}/import",
            files={"file": ("test.csv", io.BytesIO(IMPORT_CSV), "text/csv")},
            headers=auth_headers,
        )
        data = response.json()
        assert data["total_created"] == 2

        transactions = (
            db_session.query(Transaction).filter(Transaction.account_id == UUID(account_id)).all()
        )
        assert len(transactions) == 2

    def test_import_to_account_wrong_user_404(
        self, client: TestClient, auth_headers: dict, another_user: User, db_session
    ) -> None:
        other_account = BankAccount(user_id=another_user.id, account_name="Compte Autre")
        db_session.add(other_account)
        db_session.flush()

        response = client.post(
            f"/api/v1/accounts/{other_account.id}/import",
            files={"file": ("test.csv", io.BytesIO(IMPORT_CSV), "text/csv")},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_import_to_account_file_too_large_413(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        created = _create_account(client, auth_headers)
        account_id = created["id"]

        response = client.post(
            f"/api/v1/accounts/{account_id}/import",
            files={"file": ("large.csv", io.BytesIO(LARGE_FILE), "text/csv")},
            headers=auth_headers,
        )
        assert response.status_code == 413
