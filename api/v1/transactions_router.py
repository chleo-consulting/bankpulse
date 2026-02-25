from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.database import get_db
from model.models import AuditLog, BankAccount, Category, Transaction, User
from schemas.transactions import (
    TransactionCategoryUpdate,
    TransactionListResponse,
    TransactionResponse,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def _get_transaction_or_404(transaction_id: UUID, user: User, db: Session) -> Transaction:
    user_account_ids = select(BankAccount.id).where(
        BankAccount.user_id == user.id,
        BankAccount.deleted_at.is_(None),
    )
    txn = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.account_id.in_(user_account_ids),
        )
        .first()
    )
    if not txn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction introuvable")
    return txn


@router.get("", response_model=TransactionListResponse)
def list_transactions(
    account_id: UUID | None = Query(None),
    category_id: UUID | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    amount_min: Decimal | None = Query(None),
    amount_max: Decimal | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionListResponse:
    """Liste les transactions de l'utilisateur avec filtres et pagination."""
    user_account_ids = select(BankAccount.id).where(
        BankAccount.user_id == current_user.id,
        BankAccount.deleted_at.is_(None),
    )
    query = db.query(Transaction).filter(Transaction.account_id.in_(user_account_ids))

    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if date_from:
        query = query.filter(Transaction.transaction_date >= date_from)
    if date_to:
        query = query.filter(Transaction.transaction_date <= date_to)
    if amount_min is not None:
        query = query.filter(Transaction.amount >= amount_min)
    if amount_max is not None:
        query = query.filter(Transaction.amount <= amount_max)

    total = query.count()
    items = (
        query.order_by(Transaction.transaction_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return TransactionListResponse(items=items, total=total, page=page, page_size=page_size)


@router.patch("/{transaction_id}/category", response_model=TransactionResponse)
def update_transaction_category(
    transaction_id: UUID,
    body: TransactionCategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Transaction:
    """Met à jour la catégorie d'une transaction (re-catégorisation manuelle)."""
    txn = _get_transaction_or_404(transaction_id, current_user, db)
    old_category_id = str(txn.category_id) if txn.category_id else None

    if body.category_id is not None:
        cat = (
            db.query(Category)
            .filter(Category.id == body.category_id, Category.deleted_at.is_(None))
            .first()
        )
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Catégorie introuvable"
            )

    txn.category_id = body.category_id
    txn.updated_at = datetime.utcnow()

    audit = AuditLog(
        user_id=current_user.id,
        entity_type="transaction",
        entity_id=txn.id,
        action="UPDATE",
        old_values={"category_id": old_category_id},
        new_values={"category_id": str(body.category_id) if body.category_id else None},
    )
    db.add(audit)
    db.commit()
    db.refresh(txn)
    return txn
