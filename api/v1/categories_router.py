from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.database import get_db
from model.models import Category, User
from schemas.categories import CategoryResponse, CategoryWithChildrenResponse

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryWithChildrenResponse])
def list_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CategoryWithChildrenResponse]:
    """Liste les catégories avec leur hiérarchie (parents + enfants)."""
    parents = (
        db.query(Category)
        .filter(Category.parent_id.is_(None), Category.deleted_at.is_(None))
        .order_by(Category.name)
        .all()
    )
    result = []
    for parent in parents:
        children = (
            db.query(Category)
            .filter(Category.parent_id == parent.id, Category.deleted_at.is_(None))
            .order_by(Category.name)
            .all()
        )
        result.append(
            CategoryWithChildrenResponse(
                id=parent.id,
                name=parent.name,
                icon=parent.icon,
                children=[CategoryResponse.model_validate(c) for c in children],
            )
        )
    return result
