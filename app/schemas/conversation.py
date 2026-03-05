import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.conversation import ConversationStatus
from app.models.message import MessageRole


class MessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: MessageRole
    content: str
    metadata_: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str | None
    status: ConversationStatus
    metadata_: dict | None = None
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class ConversationDetail(ConversationResponse):
    messages: list[MessageResponse] = []


class ConversationUpdate(BaseModel):
    title: str | None = None
    status: ConversationStatus | None = None


class ConversationList(BaseModel):
    items: list[ConversationResponse]
    total: int
