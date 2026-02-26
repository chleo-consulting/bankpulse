from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.database import get_db
from model.models import Category, User
from schemas.budgets import BudgetCreate, BudgetResponse, BudgetsProgress, BudgetUpdate
from services.budget_service import BudgetService

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(
    body: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BudgetResponse:
    """Crée un nouveau budget par catégorie et période."""
    category = db.get(Category, body.category_id)
    if category is None or category.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catégorie introuvable")
    svc = BudgetService(db)
    budget = svc.create(current_user.id, body.category_id, body.period_type, body.amount_limit)
    return BudgetResponse.model_validate(budget)


@router.get("", response_model=list[BudgetResponse])
def list_budgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[BudgetResponse]:
    """Liste tous les budgets actifs de l'utilisateur courant."""
    svc = BudgetService(db)
    budgets = svc.list_budgets(current_user.id)
    return [BudgetResponse.model_validate(b) for b in budgets]


# IMPORTANT : /progress doit être déclaré avant /{budget_id} pour éviter
# que FastAPI essaie de convertir "progress" en UUID.
@router.get("/progress", response_model=BudgetsProgress)
def get_budgets_progress(
    month: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BudgetsProgress:
    """Progression temps réel de tous les budgets (dépensé, %, alerte)."""
    svc = BudgetService(db)
    items = svc.get_progress(current_user.id, month)
    from schemas.budgets import BudgetProgressItem

    return BudgetsProgress(
        month=month,
        items=[BudgetProgressItem(**item) for item in items],
    )


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(
    budget_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BudgetResponse:
    """Détail d'un budget."""
    svc = BudgetService(db)
    budget = svc.get_by_id(budget_id, current_user.id)
    if budget is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget introuvable")
    return BudgetResponse.model_validate(budget)


@router.patch("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: UUID,
    body: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BudgetResponse:
    """Modifie la limite ou la période d'un budget."""
    svc = BudgetService(db)
    budget = svc.get_by_id(budget_id, current_user.id)
    if budget is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget introuvable")
    updated = svc.update(budget, body.period_type, body.amount_limit)
    return BudgetResponse.model_validate(updated)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Supprime (soft delete) un budget."""
    svc = BudgetService(db)
    budget = svc.get_by_id(budget_id, current_user.id)
    if budget is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget introuvable")
    svc.delete(budget)
