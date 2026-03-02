import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from core.config import settings
from model.models import AccountShare, BankAccount, User
from services.email_service import EmailService


class AccountShareService:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Helpers privés
    # ------------------------------------------------------------------

    def _now_utc(self) -> datetime:
        return datetime.now(UTC)

    def _generate_token(self) -> tuple[str, str]:
        """Retourne (raw_token, token_hash)."""
        raw = secrets.token_urlsafe(32)
        hashed = hashlib.sha256(raw.encode()).hexdigest()
        return raw, hashed

    def _is_expired(self, expires_at: datetime) -> bool:
        now = self._now_utc()
        return expires_at.replace(tzinfo=None) < now.replace(tzinfo=None)

    # ------------------------------------------------------------------
    # Méthodes publiques
    # ------------------------------------------------------------------

    def invite(
        self,
        account_id: UUID,
        owner_id: UUID,
        invitee_email: str,
    ) -> tuple[AccountShare, str]:
        """Crée un AccountShare et envoie l'email d'invitation.

        Retourne (share, raw_token).
        Lève ValueError si auto-invitation, doublon pending ou compte introuvable.
        """
        account = self.db.execute(
            select(BankAccount).where(
                BankAccount.id == account_id,
                BankAccount.user_id == owner_id,
                BankAccount.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if account is None:
            raise ValueError("Compte introuvable")

        owner = self.db.get(User, owner_id)
        if owner is None:
            raise ValueError("Propriétaire introuvable")

        if invitee_email.lower() == owner.email.lower():
            raise ValueError("Vous ne pouvez pas vous inviter vous-même")

        existing = self.db.execute(
            select(AccountShare).where(
                AccountShare.account_id == account_id,
                AccountShare.invitee_email == invitee_email,
                AccountShare.status == "pending",
            )
        ).scalar_one_or_none()
        if existing is not None:
            raise ValueError("Une invitation est déjà en attente pour cet email")

        raw_token, token_hash = self._generate_token()
        expires_at = self._now_utc() + timedelta(days=settings.SHARE_INVITATION_EXPIRE_DAYS)

        share = AccountShare(
            account_id=account_id,
            owner_id=owner_id,
            invitee_email=invitee_email,
            status="pending",
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(share)
        self.db.flush()

        invitation_url = f"{settings.FRONTEND_URL}/invitations/{raw_token}"
        owner_name = f"{owner.first_name or ''} {owner.last_name or ''}".strip() or owner.email
        try:
            EmailService().send_account_share_invitation(
                to_email=invitee_email,
                inviter_name=owner_name,
                account_name=account.account_name or "Compte sans nom",
                invitation_url=invitation_url,
            )
        except Exception:
            pass  # L'email ne bloque pas la création de l'invitation

        self.db.commit()
        self.db.refresh(share)
        return share, raw_token

    def accept_by_token(self, token: str) -> AccountShare:
        """Accepte une invitation via le token en clair reçu par email.

        Résout invitee_user_id si un utilisateur avec cet email existe.
        Lève ValueError si token invalide, expiré ou non-pending.
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        share = self.db.execute(
            select(AccountShare).where(AccountShare.token_hash == token_hash)
        ).scalar_one_or_none()

        if share is None:
            raise ValueError("Token invalide")
        if share.status != "pending":
            raise ValueError("Cette invitation a déjà été traitée")
        if self._is_expired(share.expires_at):
            raise ValueError("Ce lien d'invitation a expiré")

        invitee = self.db.execute(
            select(User).where(
                User.email == share.invitee_email,
                User.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

        share.status = "accepted"
        share.responded_at = self._now_utc()
        if invitee is not None:
            share.invitee_user_id = invitee.id

        self.db.commit()
        self.db.refresh(share)
        return share

    def accept_by_id(self, share_id: UUID, user: User) -> AccountShare:
        """Accepte une invitation via son ID (flow UI authentifié).

        Vérifie que user.email correspond à share.invitee_email.
        """
        share = self._get_share_for_invitee(share_id, user)

        if share.status != "pending":
            raise ValueError("Cette invitation a déjà été traitée")
        if self._is_expired(share.expires_at):
            raise ValueError("Cette invitation a expiré")

        share.status = "accepted"
        share.invitee_user_id = user.id
        share.responded_at = self._now_utc()

        self.db.commit()
        self.db.refresh(share)
        return share

    def reject(self, share_id: UUID, user: User) -> AccountShare:
        """Refuse une invitation via son ID."""
        share = self._get_share_for_invitee(share_id, user)

        if share.status != "pending":
            raise ValueError("Cette invitation a déjà été traitée")

        share.status = "rejected"
        share.responded_at = self._now_utc()

        self.db.commit()
        self.db.refresh(share)
        return share

    def revoke(self, account_id: UUID, share_id: UUID, owner_id: UUID) -> AccountShare:
        """Révoque un partage actif. Seul le propriétaire du compte peut révoquer."""
        share = self.db.execute(
            select(AccountShare).where(
                AccountShare.id == share_id,
                AccountShare.account_id == account_id,
                AccountShare.owner_id == owner_id,
            )
        ).scalar_one_or_none()

        if share is None:
            raise ValueError("Partage introuvable")
        if share.status in ("rejected", "revoked"):
            raise ValueError("Ce partage ne peut plus être révoqué")

        share.status = "revoked"
        share.responded_at = self._now_utc()

        self.db.commit()
        self.db.refresh(share)
        return share

    def list_received_invitations(self, user: User) -> list[AccountShare]:
        """Liste les invitations pending reçues.

        Cherche par invitee_user_id OU invitee_email pour couvrir les invitations
        créées avant l'inscription de l'utilisateur.
        """
        now = self._now_utc()
        return list(
            self.db.execute(
                select(AccountShare)
                .where(
                    or_(
                        AccountShare.invitee_user_id == user.id,
                        AccountShare.invitee_email == user.email,
                    ),
                    AccountShare.status == "pending",
                    AccountShare.expires_at > now,
                )
                .order_by(AccountShare.created_at.desc())
            )
            .scalars()
            .all()
        )

    def list_account_shares(self, account_id: UUID, owner_id: UUID) -> list[AccountShare]:
        """Liste les partages actifs (pending + accepted) d'un compte."""
        return list(
            self.db.execute(
                select(AccountShare)
                .where(
                    AccountShare.account_id == account_id,
                    AccountShare.owner_id == owner_id,
                    AccountShare.status.in_(["pending", "accepted"]),
                )
                .order_by(AccountShare.created_at.desc())
            )
            .scalars()
            .all()
        )

    # ------------------------------------------------------------------
    # Helpers privés supplémentaires
    # ------------------------------------------------------------------

    def _get_share_for_invitee(self, share_id: UUID, user: User) -> AccountShare:
        """Récupère un share et vérifie que l'user est bien l'invité."""
        share = self.db.execute(
            select(AccountShare).where(AccountShare.id == share_id)
        ).scalar_one_or_none()

        if share is None:
            raise LookupError("Invitation introuvable")
        if share.invitee_email.lower() != user.email.lower():
            raise PermissionError("Vous n'êtes pas le destinataire de cette invitation")
        return share
