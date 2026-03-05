import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.ticket import TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=10000)
    priority: TicketPriority = TicketPriority.medium
    category: str | None = Field(default=None, max_length=100)
    conversation_id: uuid.UUID | None = None


class TicketUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1, max_length=10000)
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    category: str | None = Field(default=None, max_length=100)
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
