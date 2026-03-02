import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
from core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from model.models import AuditLog, PasswordResetToken, User
from schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)
from services.email_service import EmailService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> User:
    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        first_name=body.first_name,
        last_name=body.last_name,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte avec cet email existe déjà",
        ) from None
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == body.email, User.deleted_at.is_(None)).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )

    log = AuditLog(
        user_id=user.id,
        entity_type="user",
        entity_id=user.id,
        action="LOGIN",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        new_values={"email": user.email},
    )
    db.add(log)
    db.commit()

    user_id = str(user.id)
    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest) -> TokenResponse:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token invalide ou expiré",
    )
    try:
        payload = decode_token(body.refresh_token)
    except JWTError:
        raise credentials_error from None

    if payload.get("type") != "refresh":
        raise credentials_error

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise credentials_error

    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout() -> None:
    """Invalide le refresh token côté client (stateless MVP)."""
    return None


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)) -> MessageResponse:
    """Demande de réinitialisation de mot de passe. Répond toujours 200."""
    _generic_message = MessageResponse(
        message="Si cet email est associé à un compte, un lien de réinitialisation a été envoyé."
    )

    user = db.query(User).filter(User.email == body.email, User.deleted_at.is_(None)).first()
    if not user:
        return _generic_message

    # Invalider les tokens précédents non utilisés
    now = _now_utc()
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used_at.is_(None),
    ).update({"used_at": now})

    # Générer un token sécurisé et stocker son hash SHA-256
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = now + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)

    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(reset_token)

    log = AuditLog(
        user_id=user.id,
        entity_type="user",
        entity_id=user.id,
        action="FORGOT_PASSWORD_REQUEST",
        new_values={"email": user.email},
    )
    db.add(log)
    db.commit()

    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"
    try:
        EmailService().send_password_reset(user.email, reset_url)
    except Exception:
        pass  # Ne pas révéler l'échec d'envoi à l'appelant

    return _generic_message


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)) -> MessageResponse:
    """Réinitialise le mot de passe via un token valide."""
    invalid_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Token invalide ou expiré",
    )

    token_hash = hashlib.sha256(body.token.encode()).hexdigest()
    now = _now_utc()

    reset_token = (
        db.query(PasswordResetToken).filter(PasswordResetToken.token_hash == token_hash).first()
    )

    if reset_token is None:
        raise invalid_error
    if reset_token.used_at is not None:
        raise invalid_error
    if reset_token.expires_at.replace(tzinfo=None) < now.replace(tzinfo=None):
        raise invalid_error

    user = db.query(User).filter(User.id == reset_token.user_id, User.deleted_at.is_(None)).first()
    if user is None:
        raise invalid_error

    user.password_hash = hash_password(body.new_password)
    reset_token.used_at = now

    log = AuditLog(
        user_id=user.id,
        entity_type="user",
        entity_id=user.id,
        action="PASSWORD_RESET",
    )
    db.add(log)
    db.commit()

    return MessageResponse(message="Mot de passe réinitialisé avec succès.")


def _now_utc() -> datetime:
    return datetime.now(UTC)
