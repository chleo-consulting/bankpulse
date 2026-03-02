from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.database import get_db
from model.models import AccountShare, BankAccount, User
from schemas.auth import MessageResponse
from schemas.shares import (
    AccountShareInviteRequest,
    AccountShareResponse,
    ReceivedInvitationResponse,
)
from services.account_share_service import AccountShareService

router = APIRouter(tags=["Shares"])


def _share_to_response(share: AccountShare) -> AccountShareResponse:
    return AccountShareResponse(
        id=share.id,
        account_id=share.account_id,
        account_name=share.account.account_name if share.account else None,
        invitee_email=share.invitee_email,
        invitee_user_id=share.invitee_user_id,
        status=share.status,
        created_at=share.created_at,
        expires_at=share.expires_at,
        responded_at=share.responded_at,
    )


def _share_to_received_response(share: AccountShare) -> ReceivedInvitationResponse:
    owner = share.owner
    owner_name = None
    if owner:
        owner_name = f"{owner.first_name or ''} {owner.last_name or ''}".strip() or None
    return ReceivedInvitationResponse(
        id=share.id,
        account_id=share.account_id,
        account_name=share.account.account_name if share.account else None,
        owner_email=owner.email if owner else "",
        owner_name=owner_name,
        status=share.status,
        expires_at=share.expires_at,
        created_at=share.created_at,
    )


# ---------------------------------------------------------------------------
# Routes propriétaire
# ---------------------------------------------------------------------------


@router.post(
    "/accounts/{account_id}/invite",
    response_model=AccountShareResponse,
    status_code=status.HTTP_201_CREATED,
)
def invite_user(
    account_id: UUID,
    body: AccountShareInviteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountShareResponse:
    """Invite un utilisateur (par email) à accéder à un compte."""
    service = AccountShareService(db=db)
    try:
        share, _ = service.invite(
            account_id=account_id,
            owner_id=current_user.id,
            invitee_email=body.email,
        )
    except ValueError as exc:
        msg = str(exc)
        if "introuvable" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        if "déjà en attente" in msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    # Charger les relations pour la réponse
    db.refresh(share, attribute_names=["account", "owner"])
    return _share_to_response(share)


@router.get("/accounts/{account_id}/shares", response_model=list[AccountShareResponse])
def list_shares(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AccountShareResponse]:
    """Liste les partages actifs (pending + accepted) d'un compte."""
    # Vérifier que le compte appartient bien à l'utilisateur courant
    account = (
        db.query(BankAccount)
        .filter(
            BankAccount.id == account_id,
            BankAccount.user_id == current_user.id,
            BankAccount.deleted_at.is_(None),
        )
        .first()
    )
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compte introuvable")

    service = AccountShareService(db=db)
    shares = service.list_account_shares(account_id=account_id, owner_id=current_user.id)
    for s in shares:
        db.refresh(s, attribute_names=["account", "owner"])
    return [_share_to_response(s) for s in shares]


@router.delete(
    "/accounts/{account_id}/shares/{share_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def revoke_share(
    account_id: UUID,
    share_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Révoque un partage (propriétaire uniquement)."""
    service = AccountShareService(db=db)
    try:
        service.revoke(account_id=account_id, share_id=share_id, owner_id=current_user.id)
    except ValueError as exc:
        msg = str(exc)
        if "introuvable" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


# ---------------------------------------------------------------------------
# Routes invité
# ---------------------------------------------------------------------------


@router.get("/invitations", response_model=list[ReceivedInvitationResponse])
def list_invitations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ReceivedInvitationResponse]:
    """Liste les invitations pending reçues par l'utilisateur courant."""
    service = AccountShareService(db=db)
    shares = service.list_received_invitations(user=current_user)
    for s in shares:
        db.refresh(s, attribute_names=["account", "owner"])
    return [_share_to_received_response(s) for s in shares]


@router.post("/invitations/accept/{token}", response_model=MessageResponse)
def accept_by_token(
    token: str,
    db: Session = Depends(get_db),
) -> MessageResponse:
    """Accepte une invitation via le lien reçu par email (sans authentification requise)."""
    service = AccountShareService(db=db)
    try:
        service.accept_by_token(token=token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return MessageResponse(message="Invitation acceptée avec succès.")


@router.post("/invitations/{share_id}/accept", response_model=AccountShareResponse)
def accept_by_id(
    share_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountShareResponse:
    """Accepte une invitation via son ID (flow UI authentifié)."""
    service = AccountShareService(db=db)
    try:
        share = service.accept_by_id(share_id=share_id, user=current_user)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    db.refresh(share, attribute_names=["account", "owner"])
    return _share_to_response(share)


@router.post("/invitations/{share_id}/reject", response_model=MessageResponse)
def reject_invitation(
    share_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    """Refuse une invitation."""
    service = AccountShareService(db=db)
    try:
        service.reject(share_id=share_id, user=current_user)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return MessageResponse(message="Invitation refusée.")
