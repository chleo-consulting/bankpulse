import io

import pytest
from fastapi.testclient import TestClient

from core.security import create_access_token
from model.models import BankAccount, Transaction, User

# CSV de test minimal (nouveau format : séparateur ";", montants français)
# CSV avec deux transactions strictement identiques (même date, compte, montant, libellé)
DUPLICATE_CSV = b"""\
dateOp;dateVal;label;category;categoryParent;supplierFound;amount;comment;accountNum;accountLabel;accountbalance
2025-05-26;2025-05-26;VIR SEPA LOYER;Logement;Logement;bailleur;-800,00;;DUP_ACC001;Compte courant;1000.00
2025-05-26;2025-05-26;VIR SEPA LOYER;Logement;Logement;bailleur;-800,00;;DUP_ACC001;Compte courant;1000.00
2025-05-26;2025-05-26;CARTE Supermarche;Alimentation;Vie quotidienne;super;-45,00;;DUP_ACC001;Compte courant;1000.00
"""

SIMPLE_CSV = b"""\
dateOp;dateVal;label;category;categoryParent;supplierFound;amount;comment;accountNum;accountLabel;accountbalance
2025-01-15;2025-01-15;CARTE Amazon;Achats;Shopping;amazon;-29,99;;IMPORT_ACC001;Test Import;1500.00
2025-01-16;2025-01-16;VIR Salaire;Revenus;Revenus;employeur;2500,00;;IMPORT_ACC001;Test Import;4000.00
2025-01-17;2025-01-17;CARTE Carrefour;Alimentation;Vie quotidienne;carrefour;-45,50;;IMPORT_ACC002;Autre Compte;800.00
"""


@pytest.fixture
def test_user(db_session) -> User:
    user = User(
        email="import_test@example.com",
        password_hash="hashed",
        first_name="Test",
        last_name="Import",
    )
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


class TestImportBoursoramaEndpoint:
    def test_import_returns_200(self, client: TestClient, auth_headers: dict) -> None:
        response = client.post(
            "/api/v1/import/boursorama",
            files={"file": ("test.csv", io.BytesIO(SIMPLE_CSV), "text/csv")},
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_import_creates_accounts(
        self, client: TestClient, auth_headers: dict, db_session
    ) -> None:
        client.post(
            "/api/v1/import/boursorama",
            files={"file": ("test.csv", io.BytesIO(SIMPLE_CSV), "text/csv")},
            headers=auth_headers,
        )
        accounts = db_session.query(BankAccount).all()
        account_ibans = {a.iban for a in accounts}
        assert "IMPORT_ACC001" in account_ibans
        assert "IMPORT_ACC002" in account_ibans

    def test_import_result_structure(self, client: TestClient, auth_headers: dict) -> None:
        response = client.post(
            "/api/v1/import/boursorama",
            files={"file": ("test.csv", io.BytesIO(SIMPLE_CSV), "text/csv")},
            headers=auth_headers,
        )
        data = response.json()
        assert "accounts" in data
        assert "total_created" in data
        assert "total_skipped" in data
        assert "total_errors" in data
        assert len(data["accounts"]) == 2

    def test_import_counts_transactions(self, client: TestClient, auth_headers: dict) -> None:
        response = client.post(
            "/api/v1/import/boursorama",
            files={"file": ("test.csv", io.BytesIO(SIMPLE_CSV), "text/csv")},
            headers=auth_headers,
        )
        data = response.json()
        assert data["total_created"] == 3
        assert data["total_skipped"] == 0
        assert data["total_errors"] == 0

    def test_import_deduplication(self, client: TestClient, auth_headers: dict) -> None:
        # Premier import
        client.post(
            "/api/v1/import/boursorama",
            files={"file": ("test.csv", io.BytesIO(SIMPLE_CSV), "text/csv")},
            headers=auth_headers,
        )
        # Deuxième import du même fichier
        response = client.post(
            "/api/v1/import/boursorama",
            files={"file": ("test.csv", io.BytesIO(SIMPLE_CSV), "text/csv")},
            headers=auth_headers,
        )
        data = response.json()
        assert data["total_created"] == 0
        assert data["total_skipped"] == 3

    def test_import_requires_auth(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/import/boursorama",
            files={"file": ("test.csv", io.BytesIO(SIMPLE_CSV), "text/csv")},
        )
        assert response.status_code == 401

    def test_import_empty_file_returns_400(self, client: TestClient, auth_headers: dict) -> None:
        response = client.post(
            "/api/v1/import/boursorama",
            files={"file": ("empty.csv", io.BytesIO(b""), "text/csv")},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_import_idempotent_account_creation(
        self, client: TestClient, auth_headers: dict, db_session
    ) -> None:
        """Deux imports du même fichier ne doivent pas créer deux fois les comptes."""
        client.post(
            "/api/v1/import/boursorama",
            files={"file": ("test.csv", io.BytesIO(SIMPLE_CSV), "text/csv")},
            headers=auth_headers,
        )
        client.post(
            "/api/v1/import/boursorama",
            files={"file": ("test.csv", io.BytesIO(SIMPLE_CSV), "text/csv")},
            headers=auth_headers,
        )
        acc001_count = (
            db_session.query(BankAccount).filter(BankAccount.iban == "IMPORT_ACC001").count()
        )
        assert acc001_count == 1

    def test_import_balance_updated(
        self, client: TestClient, auth_headers: dict, db_session
    ) -> None:
        client.post(
            "/api/v1/import/boursorama",
            files={"file": ("test.csv", io.BytesIO(SIMPLE_CSV), "text/csv")},
            headers=auth_headers,
        )
        account = db_session.query(BankAccount).filter(BankAccount.iban == "IMPORT_ACC001").first()
        assert account is not None
        assert float(account.balance) == 4000.00

    def test_import_transactions_have_import_hash(
        self, client: TestClient, auth_headers: dict, db_session
    ) -> None:
        client.post(
            "/api/v1/import/boursorama",
            files={"file": ("test.csv", io.BytesIO(SIMPLE_CSV), "text/csv")},
            headers=auth_headers,
        )
        transactions = db_session.query(Transaction).all()
        for txn in transactions:
            assert txn.import_hash is not None
            assert len(txn.import_hash) == 64

    def test_intrafile_duplicates_are_all_created(
        self, client: TestClient, auth_headers: dict, db_session
    ) -> None:
        """Deux transactions identiques dans le même CSV doivent être toutes deux importées."""
        response = client.post(
            "/api/v1/import/boursorama",
            files={"file": ("dup.csv", io.BytesIO(DUPLICATE_CSV), "text/csv")},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        # 2 transactions identiques + 1 unique = 3 créées, 0 ignorées
        assert data["total_created"] == 3
        assert data["total_skipped"] == 0
        # Vérification en base : 3 transactions avec des hashs distincts
        transactions = (
            db_session.query(Transaction)
            .join(Transaction.account)
            .filter(Transaction.account.has(iban="DUP_ACC001"))
            .all()
        )
        assert len(transactions) == 3
        hashes = {txn.import_hash for txn in transactions}
        assert len(hashes) == 3  # tous les hashs sont distincts
        # La 2ème occurrence doit avoir le libellé suffixé
        descriptions = sorted(txn.description for txn in transactions)
        assert "VIR SEPA LOYER" in descriptions
        assert "VIR SEPA LOYER 1" in descriptions

    def test_intrafile_duplicates_reimport_skips_all(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        """Ré-importer le même CSV avec doublons intra-fichier doit tout ignorer."""
        # 1er import
        client.post(
            "/api/v1/import/boursorama",
            files={"file": ("dup.csv", io.BytesIO(DUPLICATE_CSV), "text/csv")},
            headers=auth_headers,
        )
        # 2e import du même fichier
        response = client.post(
            "/api/v1/import/boursorama",
            files={"file": ("dup.csv", io.BytesIO(DUPLICATE_CSV), "text/csv")},
            headers=auth_headers,
        )
        data = response.json()
        assert data["total_created"] == 0
        assert data["total_skipped"] == 3
