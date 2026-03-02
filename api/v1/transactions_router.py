import base64
import csv
import io
import json
from collections.abc import Generator
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.database import get_db
from model.models import (
    AuditLog,
    BankAccount,
    Category,
    Merchant,
    Tag,
    Transaction,
    User,
    transaction_tags,
)
from schemas.transaction_filters import TransactionFilters, TransactionListParams
from schemas.transactions import (
    BulkTagRequest,
    CursorTransactionListResponse,
    TransactionCategoryUpdate,
    TransactionResponse,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def _filters_dep(
    account_id: UUID | None = Query(None),
    category_id: UUID | None = Query(None),
    merchant_id: UUID | None = Query(None),
    tag_id: UUID | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    amount_min: Decimal | None = Query(None),
    amount_max: Decimal | None = Query(None),
) -> TransactionFilters:
    """Dépendance FastAPI : construit un TransactionFilters depuis les query params."""
    return TransactionFilters(
        account_id=account_id,
        category_id=category_id,
        merchant_id=merchant_id,
        tag_id=tag_id,
        date_from=date_from,
        date_to=date_to,
        amount_min=amount_min,
        amount_max=amount_max,
    )


def _list_params_dep(
    filters: TransactionFilters = Depends(_filters_dep),
    cursor: str | None = Query(None),
    page_size: int = Query(50, ge=1, le=200),
) -> TransactionListParams:
    """Dépendance FastAPI : construit un TransactionListParams depuis les query params."""
    return TransactionListParams(
        **filters.model_dump(),
        cursor=cursor,
        page_size=page_size,
    )


def _encode_cursor(txn: Transaction) -> str:
    payload = {"date": txn.transaction_date.isoformat(), "id": str(txn.id)}
    return base64.b64encode(json.dumps(payload).encode()).decode()


def _decode_cursor(cursor: str) -> tuple[date, UUID]:
    try:
        payload = json.loads(base64.b64decode(cursor).decode())
        return date.fromisoformat(payload["date"]), UUID(payload["id"])
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cursor invalide"
        ) from exc


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


def _build_base_query(db: Session, user: User):
    """Construit la requête de base filtrée par utilisateur."""
    user_account_ids = select(BankAccount.id).where(
        BankAccount.user_id == user.id,
        BankAccount.deleted_at.is_(None),
    )
    return db.query(Transaction).filter(Transaction.account_id.in_(user_account_ids))


def _apply_filters(query, filters: TransactionFilters):
    """Applique les filtres communs TransactionFilters à une requête transaction."""
    if filters.account_id:
        query = query.filter(Transaction.account_id == filters.account_id)
    if filters.category_id:
        query = query.filter(Transaction.category_id == filters.category_id)
    if filters.merchant_id:
        query = query.filter(Transaction.merchant_id == filters.merchant_id)
    if filters.tag_id:
        tagged_ids = select(transaction_tags.c.transaction_id).where(
            transaction_tags.c.tag_id == filters.tag_id
        )
        query = query.filter(Transaction.id.in_(tagged_ids))
    if filters.date_from:
        query = query.filter(Transaction.transaction_date >= filters.date_from)
    if filters.date_to:
        query = query.filter(Transaction.transaction_date <= filters.date_to)
    if filters.amount_min is not None:
        query = query.filter(Transaction.amount >= filters.amount_min)
    if filters.amount_max is not None:
        query = query.filter(Transaction.amount <= filters.amount_max)
    return query


def _generate_jsonl(
    db: Session, user: User, filters: TransactionFilters
) -> Generator[str, None, None]:
    """Génère les transactions en JSON Lines, page par page (mémoire O(1))."""
    cursor_val: str | None = None
    page_size = 100
    while True:
        query = _apply_filters(_build_base_query(db, user), filters)
        query = query.order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
        if cursor_val:
            cursor_date, cursor_id = _decode_cursor(cursor_val)
            query = query.filter(
                or_(
                    Transaction.transaction_date < cursor_date,
                    (Transaction.transaction_date == cursor_date) & (Transaction.id < cursor_id),
                )
            )
        results = query.limit(page_size).all()
        if not results:
            break
        for txn in results:
            yield TransactionResponse.model_validate(txn).model_dump_json() + "\n"
        if len(results) < page_size:
            break
        cursor_val = _encode_cursor(results[-1])


@router.get("/search", response_model=CursorTransactionListResponse)
def search_transactions(
    q: str = Query(..., min_length=1),
    cursor: str | None = Query(None),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CursorTransactionListResponse:
    """Recherche full-text sur description et nom du marchand."""
    query = (
        _build_base_query(db, current_user)
        .outerjoin(Merchant, Transaction.merchant_id == Merchant.id)
        .filter(
            or_(
                Transaction.description.ilike(f"%{q}%"),
                Merchant.name.ilike(f"%{q}%"),
            )
        )
    )
    query = query.order_by(Transaction.transaction_date.desc(), Transaction.id.desc())

    if cursor:
        cursor_date, cursor_id = _decode_cursor(cursor)
        query = query.filter(
            or_(
                Transaction.transaction_date < cursor_date,
                (Transaction.transaction_date == cursor_date) & (Transaction.id < cursor_id),
            )
        )

    results = query.limit(page_size + 1).all()
    has_next = len(results) > page_size
    items = results[:page_size]
    next_cursor = _encode_cursor(items[-1]) if has_next and items else None
    return CursorTransactionListResponse(items=items, next_cursor=next_cursor, page_size=page_size)


@router.get("/export")
def export_transactions(
    format: str = Query("csv"),
    filters: TransactionFilters = Depends(_filters_dep),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Exporte les transactions filtrées en CSV ou JSON Lines (format=csv|jsonl)."""
    if format == "jsonl":
        return StreamingResponse(
            _generate_jsonl(db, current_user, filters),
            media_type="application/jsonl",
            headers={"Content-Disposition": "attachment; filename=transactions.jsonl"},
        )

    if format != "csv":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format non supporté. Valeurs acceptées : csv, jsonl",
        )

    query = _apply_filters(_build_base_query(db, current_user), filters)
    transactions = query.order_by(Transaction.transaction_date.desc()).all()

    cat_ids = {t.category_id for t in transactions if t.category_id}
    cats = {c.id: c.name for c in db.query(Category).filter(Category.id.in_(cat_ids)).all()}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "description", "montant", "categorie", "tags"])

    for txn in transactions:
        tag_names = ",".join(t.name for t in txn.tags)
        cat_name = cats.get(txn.category_id, "") if txn.category_id else ""
        writer.writerow(
            [
                txn.transaction_date.isoformat(),
                txn.description or "",
                str(txn.amount),
                cat_name,
                tag_names,
            ]
        )

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )


@router.get("", response_model=CursorTransactionListResponse)
def list_transactions(
    params: TransactionListParams = Depends(_list_params_dep),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CursorTransactionListResponse:
    """Liste les transactions avec pagination cursor-based et filtres multicritères."""
    query = _apply_filters(_build_base_query(db, current_user), params)
    query = query.order_by(Transaction.transaction_date.desc(), Transaction.id.desc())

    if params.cursor:
        cursor_date, cursor_id = _decode_cursor(params.cursor)
        query = query.filter(
            or_(
                Transaction.transaction_date < cursor_date,
                (Transaction.transaction_date == cursor_date) & (Transaction.id < cursor_id),
            )
        )

    results = query.limit(params.page_size + 1).all()
    has_next = len(results) > params.page_size
    items = results[: params.page_size]
    next_cursor = _encode_cursor(items[-1]) if has_next and items else None
    return CursorTransactionListResponse(
        items=items, next_cursor=next_cursor, page_size=params.page_size
    )


@router.post("/bulk-tag", status_code=status.HTTP_204_NO_CONTENT)
def bulk_tag_transactions(
    body: BulkTagRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Attache des tags à plusieurs transactions en une seule opération."""
    if not body.transaction_ids or not body.tag_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="transaction_ids et tag_ids ne peuvent pas être vides",
        )

    user_account_ids = select(BankAccount.id).where(
        BankAccount.user_id == current_user.id,
        BankAccount.deleted_at.is_(None),
    )
    # Vérifier que tous les tags existent
    tags = db.query(Tag).filter(Tag.id.in_(body.tag_ids), Tag.deleted_at.is_(None)).all()
    if len(tags) != len(body.tag_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Un ou plusieurs tags introuvables"
        )

    # Charger les transactions de l'utilisateur
    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.id.in_(body.transaction_ids),
            Transaction.account_id.in_(user_account_ids),
        )
        .all()
    )
    if len(transactions) != len(body.transaction_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Une ou plusieurs transactions introuvables",
        )

    for txn in transactions:
        existing_tag_ids = {t.id for t in txn.tags}
        for tag in tags:
            if tag.id not in existing_tag_ids:
                txn.tags.append(tag)

    db.commit()


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
    txn.updated_at = datetime.now(UTC)

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
