from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.database import get_db
from model.models import User
from schemas.import_ import ImportResult
from services.import_service import ImportService

router = APIRouter(prefix="/import", tags=["Import"])


@router.post("/boursorama", response_model=ImportResult, status_code=status.HTTP_200_OK)
async def import_boursorama(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ImportResult:
    """Importe un export CSV Boursorama (multi-comptes). Crée les comptes manquants et déduplique
    les transactions via import_hash."""
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fichier vide")

    service = ImportService(db=db)
    return service.import_boursorama(user_id=current_user.id, file_bytes=contents)
