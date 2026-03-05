import uuid

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: uuid.UUID | None = None


class ChatEvent(BaseModel):
    event: str  # "token", "agent_start", "agent_end", "done", "error"
    data: str
    agent: str | None = None
    conversation_id: uuid.UUID | None = None
