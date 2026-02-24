from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from core.database import get_db

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/db")
async def health_db(db: Session = Depends(get_db)) -> dict:
    try:
        db.execute(text("SELECT 1"))
        return {"database": "ok"}
    except Exception:
        return {"database": "error"}
