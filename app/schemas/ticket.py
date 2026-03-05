import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.ticket import TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    title: str
    description: str
    priority: TicketPriority = TicketPriority.medium
    category: str | None = None
    conversation_id: uuid.UUID | None = None


class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    category: str | None = None
    assigned_to: uuid.UUID | None = None


class TicketResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID | None
    user_id: uuid.UUID
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    category: str | None
    assigned_to: uuid.UUID | None
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class TicketList(BaseModel):
    items: list[TicketResponse]
    total: int
