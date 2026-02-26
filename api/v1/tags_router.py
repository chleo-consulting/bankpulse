from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.database import get_db
from model.models import Tag, User
from schemas.tags import TagCreate, TagResponse

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("", response_model=list[TagResponse])
def list_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Tag]:
    """Liste tous les tags disponibles."""
    return db.query(Tag).filter(Tag.deleted_at.is_(None)).order_by(Tag.name).all()


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    body: TagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Tag:
    """Crée un nouveau tag (retourne 409 si le nom existe déjà)."""
    existing = db.query(Tag).filter(Tag.name == body.name, Tag.deleted_at.is_(None)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un tag avec ce nom existe déjà",
        )
    tag = Tag(name=body.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag
