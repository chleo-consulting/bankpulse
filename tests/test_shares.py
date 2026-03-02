import hashlib
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from core.security import create_access_token, hash_password
from model.models import AccountShare, BankAccount, User

# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------


def _make_user(db_session, email: str = "alice@example.com") -> User:
    u = User(email=email, password_hash=hash_password("Secret123!"))
    db_session.add(u)
    db_session.flush()
    return u


def _make_account(db_session, user: User, name: str = "Compte Courant") -> BankAccount:
    a = BankAccount(user_id=user.id, account_name=name, iban="FR7630006000011234567890189")
    db_session.add(a)
    db_session.flush()
    return a


def _auth_headers(user: User) -> dict:
    token = create_access_token(str(user.id))
    return {"Authorization": f"Bearer {token}"}


def _make_share(
    db_session,
    account: BankAccount,
    owner: User,
    invitee_email: str,
    status: str = "pending",
    days_offset: int = 7,
    invitee_user: User | None = None,
) -> tuple[AccountShare, str]:
    raw_token = "raw-test-token-" + str(uuid4())
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    share = AccountShare(
        account_id=account.id,
        owner_id=owner.id,
        invitee_email=invitee_email,
        invitee_user_id=invitee_user.id if invitee_user else None,
        status=status,
        token_hash=token_hash,
        expires_at=datetime.now(UTC) + timedelta(days=days_offset),
    )
    db_session.add(share)
    db_session.flush()
    return share, raw_token


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def owner(db_session) -> User:
    return _make_user(db_session, "owner@example.com")


@pytest.fixture
def invitee(db_session) -> User:
    return _make_user(db_session, "invitee@example.com")


@pytest.fixture
def owner_account(db_session, owner) -> BankAccount:
    return _make_account(db_session, owner)


@pytest.fixture
def owner_headers(owner) -> dict:
    return _auth_headers(owner)


@pytest.fixture
def invitee_headers(invitee) -> dict:
    return _auth_headers(invitee)


# ---------------------------------------------------------------------------
# POST /accounts/{account_id}/invite
# ---------------------------------------------------------------------------


class TestInvite:
    def test_invite_creates_share_returns_201(
        self, client: TestClient, owner_account: BankAccount, owner_headers: dict
    ):
        with patch("services.account_share_service.EmailService") as mock_cls:
            mock_cls.return_value.send_account_share_invitation = MagicMock()
            resp = client.post(
                f"/api/v1/accounts/{owner_account.id}/invite",
                json={"email": "bob@example.com"},
                headers=owner_headers,
            )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "pending"
        assert data["invitee_email"] == "bob@example.com"
        assert data["account_id"] == str(owner_account.id)

    def test_invite_sends_email(
        self, client: TestClient, owner_account: BankAccount, owner_headers: dict
    ):
        with patch("services.account_share_service.EmailService") as mock_cls:
            mock_instance = MagicMock()
            mock_cls.return_value = mock_instance
            client.post(
                f"/api/v1/accounts/{owner_account.id}/invite",
                json={"email": "bob2@example.com"},
                headers=owner_headers,
            )
        mock_instance.send_account_share_invitation.assert_called_once()

    def test_invite_unauthenticated_returns_401(
        self, client: TestClient, owner_account: BankAccount
    ):
        resp = client.post(
            f"/api/v1/accounts/{owner_account.id}/invite",
            json={"email": "bob@example.com"},
        )
        assert resp.status_code == 401

    def test_invite_wrong_owner_returns_404(
        self, client: TestClient, owner_account: BankAccount, invitee_headers: dict
    ):
        with patch("services.account_share_service.EmailService"):
            resp = client.post(
                f"/api/v1/accounts/{owner_account.id}/invite",
                json={"email": "bob@example.com"},
                headers=invitee_headers,
            )
        assert resp.status_code == 404

    def test_invite_nonexistent_account_returns_404(self, client: TestClient, owner_headers: dict):
        with patch("services.account_share_service.EmailService"):
            resp = client.post(
                f"/api/v1/accounts/{uuid4()}/invite",
                json={"email": "bob@example.com"},
                headers=owner_headers,
            )
        assert resp.status_code == 404

    def test_invite_self_returns_400(
        self, client: TestClient, owner_account: BankAccount, owner: User, owner_headers: dict
    ):
        with patch("services.account_share_service.EmailService"):
            resp = client.post(
                f"/api/v1/accounts/{owner_account.id}/invite",
                json={"email": owner.email},
                headers=owner_headers,
            )
        assert resp.status_code == 400

    def test_invite_duplicate_pending_returns_409(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        owner_headers: dict,
    ):
        _make_share(db_session, owner_account, owner, "bob@example.com", status="pending")
        with patch("services.account_share_service.EmailService"):
            resp = client.post(
                f"/api/v1/accounts/{owner_account.id}/invite",
                json={"email": "bob@example.com"},
                headers=owner_headers,
            )
        assert resp.status_code == 409

    def test_invite_email_failure_does_not_rollback(
        self, client: TestClient, owner_account: BankAccount, owner_headers: dict
    ):
        with patch("services.account_share_service.EmailService") as mock_cls:
            mock_cls.return_value.send_account_share_invitation.side_effect = Exception(
                "SMTP error"
            )
            resp = client.post(
                f"/api/v1/accounts/{owner_account.id}/invite",
                json={"email": "bob3@example.com"},
                headers=owner_headers,
            )
        # L'invitation est quand même créée
        assert resp.status_code == 201


# ---------------------------------------------------------------------------
# GET /accounts/{account_id}/shares
# ---------------------------------------------------------------------------


class TestListShares:
    def test_list_shares_returns_pending_and_accepted(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        owner_headers: dict,
    ):
        _make_share(db_session, owner_account, owner, "a@example.com", "pending")
        _make_share(db_session, owner_account, owner, "b@example.com", "accepted")
        resp = client.get(f"/api/v1/accounts/{owner_account.id}/shares", headers=owner_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_list_shares_excludes_rejected_revoked(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        owner_headers: dict,
    ):
        _make_share(db_session, owner_account, owner, "c@example.com", "rejected")
        _make_share(db_session, owner_account, owner, "d@example.com", "revoked")
        resp = client.get(f"/api/v1/accounts/{owner_account.id}/shares", headers=owner_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 0

    def test_list_shares_other_owner_returns_404(
        self,
        client: TestClient,
        owner_account: BankAccount,
        invitee_headers: dict,
    ):
        resp = client.get(f"/api/v1/accounts/{owner_account.id}/shares", headers=invitee_headers)
        assert resp.status_code == 404

    def test_list_shares_unauthenticated_returns_401(
        self, client: TestClient, owner_account: BankAccount
    ):
        resp = client.get(f"/api/v1/accounts/{owner_account.id}/shares")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# DELETE /accounts/{account_id}/shares/{share_id}
# ---------------------------------------------------------------------------


class TestRevokeShare:
    def test_revoke_returns_204(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        owner_headers: dict,
    ):
        share, _ = _make_share(db_session, owner_account, owner, "x@example.com", "pending")
        resp = client.delete(
            f"/api/v1/accounts/{owner_account.id}/shares/{share.id}",
            headers=owner_headers,
        )
        assert resp.status_code == 204

    def test_revoke_sets_status_revoked(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        owner_headers: dict,
    ):
        share, _ = _make_share(db_session, owner_account, owner, "y@example.com", "accepted")
        client.delete(
            f"/api/v1/accounts/{owner_account.id}/shares/{share.id}",
            headers=owner_headers,
        )
        db_session.refresh(share)
        assert share.status == "revoked"

    def test_revoke_nonexistent_returns_404(
        self, client: TestClient, owner_account: BankAccount, owner_headers: dict
    ):
        resp = client.delete(
            f"/api/v1/accounts/{owner_account.id}/shares/{uuid4()}",
            headers=owner_headers,
        )
        assert resp.status_code == 404

    def test_revoke_other_owner_returns_404(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        invitee_headers: dict,
    ):
        share, _ = _make_share(db_session, owner_account, owner, "z@example.com", "pending")
        resp = client.delete(
            f"/api/v1/accounts/{owner_account.id}/shares/{share.id}",
            headers=invitee_headers,
        )
        assert resp.status_code == 404

    def test_revoke_already_revoked_returns_400(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        owner_headers: dict,
    ):
        share, _ = _make_share(db_session, owner_account, owner, "w@example.com", "revoked")
        resp = client.delete(
            f"/api/v1/accounts/{owner_account.id}/shares/{share.id}",
            headers=owner_headers,
        )
        assert resp.status_code == 400

    def test_revoke_unauthenticated_returns_401(
        self, client: TestClient, owner_account: BankAccount
    ):
        resp = client.delete(f"/api/v1/accounts/{owner_account.id}/shares/{uuid4()}")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /invitations/accept/{token} (sans auth)
# ---------------------------------------------------------------------------


class TestAcceptByToken:
    def test_accept_by_token_valid_returns_200(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
    ):
        share, raw_token = _make_share(
            db_session, owner_account, owner, "tok@example.com", "pending"
        )
        resp = client.post(f"/api/v1/invitations/accept/{raw_token}")
        assert resp.status_code == 200
        assert resp.json()["message"] == "Invitation acceptée avec succès."

    def test_accept_by_token_sets_status_accepted(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
    ):
        share, raw_token = _make_share(
            db_session, owner_account, owner, "tok2@example.com", "pending"
        )
        client.post(f"/api/v1/invitations/accept/{raw_token}")
        db_session.refresh(share)
        assert share.status == "accepted"
        assert share.responded_at is not None

    def test_accept_by_token_resolves_invitee_user_id(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        invitee: User,
    ):
        share, raw_token = _make_share(db_session, owner_account, owner, invitee.email, "pending")
        client.post(f"/api/v1/invitations/accept/{raw_token}")
        db_session.refresh(share)
        assert share.invitee_user_id == invitee.id

    def test_accept_by_token_unknown_user_no_user_id(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
    ):
        share, raw_token = _make_share(
            db_session, owner_account, owner, "unknown@example.com", "pending"
        )
        client.post(f"/api/v1/invitations/accept/{raw_token}")
        db_session.refresh(share)
        assert share.status == "accepted"
        assert share.invitee_user_id is None

    def test_accept_by_token_invalid_returns_400(self, client: TestClient):
        resp = client.post("/api/v1/invitations/accept/bad-token-xyz")
        assert resp.status_code == 400

    def test_accept_by_token_expired_returns_400(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
    ):
        share, raw_token = _make_share(
            db_session, owner_account, owner, "exp@example.com", "pending", days_offset=-1
        )
        resp = client.post(f"/api/v1/invitations/accept/{raw_token}")
        assert resp.status_code == 400

    def test_accept_by_token_already_accepted_returns_400(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
    ):
        share, raw_token = _make_share(
            db_session, owner_account, owner, "done@example.com", "accepted"
        )
        resp = client.post(f"/api/v1/invitations/accept/{raw_token}")
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# POST /invitations/{share_id}/accept (UI authentifié)
# ---------------------------------------------------------------------------


class TestAcceptById:
    def test_accept_by_id_returns_200(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        invitee: User,
        invitee_headers: dict,
    ):
        share, _ = _make_share(db_session, owner_account, owner, invitee.email, "pending")
        resp = client.post(f"/api/v1/invitations/{share.id}/accept", headers=invitee_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "accepted"

    def test_accept_by_id_sets_invitee_user_id(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        invitee: User,
        invitee_headers: dict,
    ):
        share, _ = _make_share(db_session, owner_account, owner, invitee.email, "pending")
        client.post(f"/api/v1/invitations/{share.id}/accept", headers=invitee_headers)
        db_session.refresh(share)
        assert share.invitee_user_id == invitee.id

    def test_accept_by_id_wrong_email_returns_403(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        owner_headers: dict,
    ):
        # owner tente d'accepter une invitation destinée à quelqu'un d'autre
        share, _ = _make_share(db_session, owner_account, owner, "other@example.com", "pending")
        resp = client.post(f"/api/v1/invitations/{share.id}/accept", headers=owner_headers)
        assert resp.status_code == 403

    def test_accept_by_id_already_accepted_returns_400(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        invitee: User,
        invitee_headers: dict,
    ):
        share, _ = _make_share(db_session, owner_account, owner, invitee.email, "accepted")
        resp = client.post(f"/api/v1/invitations/{share.id}/accept", headers=invitee_headers)
        assert resp.status_code == 400

    def test_accept_by_id_expired_returns_400(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        invitee: User,
        invitee_headers: dict,
    ):
        share, _ = _make_share(
            db_session, owner_account, owner, invitee.email, "pending", days_offset=-1
        )
        resp = client.post(f"/api/v1/invitations/{share.id}/accept", headers=invitee_headers)
        assert resp.status_code == 400

    def test_accept_by_id_unauthenticated_returns_401(
        self, client: TestClient, db_session, owner_account: BankAccount, owner: User
    ):
        share, _ = _make_share(db_session, owner_account, owner, "z@example.com", "pending")
        resp = client.post(f"/api/v1/invitations/{share.id}/accept")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /invitations/{share_id}/reject
# ---------------------------------------------------------------------------


class TestRejectInvitation:
    def test_reject_returns_200(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        invitee: User,
        invitee_headers: dict,
    ):
        share, _ = _make_share(db_session, owner_account, owner, invitee.email, "pending")
        resp = client.post(f"/api/v1/invitations/{share.id}/reject", headers=invitee_headers)
        assert resp.status_code == 200

    def test_reject_sets_status_rejected(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        invitee: User,
        invitee_headers: dict,
    ):
        share, _ = _make_share(db_session, owner_account, owner, invitee.email, "pending")
        client.post(f"/api/v1/invitations/{share.id}/reject", headers=invitee_headers)
        db_session.refresh(share)
        assert share.status == "rejected"

    def test_reject_wrong_email_returns_403(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        owner_headers: dict,
    ):
        share, _ = _make_share(db_session, owner_account, owner, "other@example.com", "pending")
        resp = client.post(f"/api/v1/invitations/{share.id}/reject", headers=owner_headers)
        assert resp.status_code == 403

    def test_reject_already_rejected_returns_400(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        invitee: User,
        invitee_headers: dict,
    ):
        share, _ = _make_share(db_session, owner_account, owner, invitee.email, "rejected")
        resp = client.post(f"/api/v1/invitations/{share.id}/reject", headers=invitee_headers)
        assert resp.status_code == 400

    def test_reject_unauthenticated_returns_401(
        self, client: TestClient, db_session, owner_account: BankAccount, owner: User
    ):
        share, _ = _make_share(db_session, owner_account, owner, "z2@example.com", "pending")
        resp = client.post(f"/api/v1/invitations/{share.id}/reject")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /invitations
# ---------------------------------------------------------------------------


class TestListInvitations:
    def test_list_invitations_returns_pending(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        invitee: User,
        invitee_headers: dict,
    ):
        _make_share(db_session, owner_account, owner, invitee.email, "pending")
        resp = client.get("/api/v1/invitations", headers=invitee_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_invitations_returns_by_email_match(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        invitee: User,
        invitee_headers: dict,
    ):
        # L'invitation a été créée avant l'inscription → invitee_user_id=None
        share, _ = _make_share(
            db_session, owner_account, owner, invitee.email, "pending", invitee_user=None
        )
        resp = client.get("/api/v1/invitations", headers=invitee_headers)
        assert resp.status_code == 200
        # Doit apparaître grâce au match par email
        assert any(i["id"] == str(share.id) for i in resp.json())

    def test_list_invitations_excludes_expired(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        invitee: User,
        invitee_headers: dict,
    ):
        _make_share(db_session, owner_account, owner, invitee.email, "pending", days_offset=-1)
        resp = client.get("/api/v1/invitations", headers=invitee_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 0

    def test_list_invitations_excludes_accepted(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        invitee: User,
        invitee_headers: dict,
    ):
        _make_share(db_session, owner_account, owner, invitee.email, "accepted")
        resp = client.get("/api/v1/invitations", headers=invitee_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 0

    def test_list_invitations_unauthenticated_returns_401(self, client: TestClient):
        resp = client.get("/api/v1/invitations")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /accounts — extension partage
# ---------------------------------------------------------------------------


class TestListAccountsShared:
    def test_list_accounts_includes_shared_accounts(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        invitee: User,
        invitee_headers: dict,
    ):
        _make_share(
            db_session, owner_account, owner, invitee.email, "accepted", invitee_user=invitee
        )
        resp = client.get("/api/v1/accounts", headers=invitee_headers)
        assert resp.status_code == 200
        ids = [a["id"] for a in resp.json()]
        assert str(owner_account.id) in ids

    def test_list_accounts_shared_has_is_shared_true(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        invitee: User,
        invitee_headers: dict,
    ):
        _make_share(
            db_session, owner_account, owner, invitee.email, "accepted", invitee_user=invitee
        )
        resp = client.get("/api/v1/accounts", headers=invitee_headers)
        shared = next(a for a in resp.json() if a["id"] == str(owner_account.id))
        assert shared["is_shared"] is True
        assert shared["shared_by_email"] == owner.email

    def test_list_accounts_own_accounts_have_is_shared_false(
        self,
        client: TestClient,
        db_session,
        owner: User,
        owner_headers: dict,
        owner_account: BankAccount,
    ):
        resp = client.get("/api/v1/accounts", headers=owner_headers)
        assert resp.status_code == 200
        own = next(a for a in resp.json() if a["id"] == str(owner_account.id))
        assert own["is_shared"] is False

    def test_list_accounts_rejected_share_not_included(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        invitee: User,
        invitee_headers: dict,
    ):
        _make_share(
            db_session, owner_account, owner, invitee.email, "rejected", invitee_user=invitee
        )
        resp = client.get("/api/v1/accounts", headers=invitee_headers)
        ids = [a["id"] for a in resp.json()]
        assert str(owner_account.id) not in ids

    def test_list_accounts_revoked_share_not_included(
        self,
        client: TestClient,
        db_session,
        owner_account: BankAccount,
        owner: User,
        invitee: User,
        invitee_headers: dict,
    ):
        _make_share(
            db_session, owner_account, owner, invitee.email, "revoked", invitee_user=invitee
        )
        resp = client.get("/api/v1/accounts", headers=invitee_headers)
        ids = [a["id"] for a in resp.json()]
        assert str(owner_account.id) not in ids
