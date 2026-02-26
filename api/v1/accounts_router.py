from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.database import get_db
from model.models import BankAccount, User
from schemas.accounts import BankAccountCreate, BankAccountResponse, BankAccountUpdate
from schemas.import_ import ImportResult
from services.import_service import ImportService

router = APIRouter(prefix="/accounts", tags=["Accounts"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 Mo


def _get_account_or_404(account_id: UUID, user: User, db: Session) -> BankAccount:
    account = (
        db.query(BankAccount)
        .filter(
            BankAccount.id == account_id,
            BankAccount.user_id == user.id,
            BankAccount.deleted_at.is_(None),
        )
        .first()
    )
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compte introuvable")
    return account


@router.get("", response_model=list[BankAccountResponse])
def list_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[BankAccount]:
    """Liste les comptes bancaires non supprimés de l'utilisateur courant."""
    return (
        db.query(BankAccount)
        .filter(
            BankAccount.user_id == current_user.id,
            BankAccount.deleted_at.is_(None),
        )
        .all()
    )


@router.post("", response_model=BankAccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    body: BankAccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BankAccount:
    """Crée un nouveau compte bancaire pour l'utilisateur courant."""
    account = BankAccount(
        user_id=current_user.id,
        account_name=body.account_name,
        iban=body.iban,
        account_type=body.account_type,
        balance=body.balance,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get("/{account_id}", response_model=BankAccountResponse)
def get_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BankAccount:
    """Retourne un compte bancaire par ID. 404 si inexistant, supprimé ou appartenant à un autre
    utilisateur."""
    return _get_account_or_404(account_id, current_user, db)


@router.patch("/{account_id}", response_model=BankAccountResponse)
def update_account(
    account_id: UUID,
    body: BankAccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BankAccount:
    """Met à jour les champs fournis d'un compte (PATCH sémantique)."""
    account = _get_account_or_404(account_id, current_user, db)

    if body.account_name is not None:
        account.account_name = body.account_name
    if body.iban is not None:
        account.iban = body.iban
    if body.account_type is not None:
        account.account_type = body.account_type
    if body.balance is not None:
        account.balance = body.balance

    account.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Soft-delete d'un compte bancaire."""
    account = _get_account_or_404(account_id, current_user, db)
    account.deleted_at = datetime.now(timezone.utc)
    db.commit()


@router.post("/{account_id}/import", response_model=ImportResult)
async def import_to_account(
    account_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ImportResult:
    """Importe un CSV Boursorama vers un compte spécifique. Déduplique via import_hash."""
    account = _get_account_or_404(account_id, current_user, db)

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fichier vide")
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Fichier trop volumineux (max 10 Mo)",
        )

    service = ImportService(db=db)
    return service.import_to_account(account=account, file_bytes=contents)
