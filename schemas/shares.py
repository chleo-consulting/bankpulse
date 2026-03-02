from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class AccountShareInviteRequest(BaseModel):
    email: EmailStr


class AccountShareResponse(BaseModel):
    """Vue propriétaire — détail d'un partage."""

    id: UUID
    account_id: UUID
    account_name: str | None
    invitee_email: str
    invitee_user_id: UUID | None
    status: str
    created_at: datetime
    expires_at: datetime
    responded_at: datetime | None


class ReceivedInvitationResponse(BaseModel):
    """Vue invité — invitation reçue."""

    id: UUID
    account_id: UUID
    account_name: str | None
    owner_email: str
    owner_name: str | None
    status: str
    expires_at: datetime
    created_at: datetime
