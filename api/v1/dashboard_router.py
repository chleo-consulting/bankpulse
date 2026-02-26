from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.database import get_db
from model.models import User
from schemas.dashboard import (
    CategoriesBreakdown,
    CategoryBreakdownItem,
    DashboardSummary,
    MonthlySummary,
    RecurringSubscription,
    RecurringSubscriptions,
    TopMerchantItem,
    TopMerchants,
)
from services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardSummary:
    """Solde consolidé + comparaison des dépenses mois courant vs précédent."""
    svc = DashboardService(db)
    balance = svc.get_consolidated_balance(current_user.id)
    comparison = svc.get_monthly_comparison(current_user.id)
    return DashboardSummary(
        total_balance=balance,
        expenses=MonthlySummary(**comparison),
    )


@router.get("/categories-breakdown", response_model=CategoriesBreakdown)
def get_categories_breakdown(
    month: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CategoriesBreakdown:
    """Répartition des dépenses par catégorie pour le mois demandé (défaut : mois courant)."""
    svc = DashboardService(db)
    effective_month = month or date.today().strftime("%Y-%m")
    items = svc.get_categories_breakdown(current_user.id, effective_month)
    total = sum((item["amount"] for item in items), Decimal("0"))
    return CategoriesBreakdown(
        month=effective_month,
        items=[CategoryBreakdownItem(**item) for item in items],
        total_amount=total,
    )


@router.get("/top-merchants", response_model=TopMerchants)
def get_top_merchants(
    month: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TopMerchants:
    """Top N marchands par montant dépensé pour le mois demandé (défaut : mois courant)."""
    svc = DashboardService(db)
    effective_month = month or date.today().strftime("%Y-%m")
    items = svc.get_top_merchants(current_user.id, effective_month, limit)
    return TopMerchants(
        month=effective_month,
        items=[TopMerchantItem(**item) for item in items],
    )


@router.get("/recurring", response_model=RecurringSubscriptions)
def get_recurring_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecurringSubscriptions:
    """Liste des abonnements récurrents détectés pour l'utilisateur."""
    svc = DashboardService(db)
    items = svc.get_recurring_subscriptions(current_user.id)
    return RecurringSubscriptions(
        items=[RecurringSubscription(**item) for item in items],
    )
