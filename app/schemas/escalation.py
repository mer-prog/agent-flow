import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.escalation import EscalationStatus


class EscalationResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    ticket_id: uuid.UUID | None
    reason: str
    sentiment_score: float | None
    status: EscalationStatus
    reviewed_by: uuid.UUID | None
    reviewed_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class EscalationReview(BaseModel):
    action: str  # "approve" or "reject"
    notes: str | None = None


class EscalationList(BaseModel):
    items: list[EscalationResponse]
    total: int
