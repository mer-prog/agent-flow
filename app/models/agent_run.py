import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AgentType(str, enum.Enum):
    router = "router"
    faq = "faq"
    ticket = "ticket"
    escalation = "escalation"
    chitchat = "chitchat"
    formatter = "formatter"


class AgentRunStatus(str, enum.Enum):
    started = "started"
    completed = "completed"
    failed = "failed"


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True
    )
    agent_type: Mapped[AgentType] = mapped_column(
        Enum(AgentType, name="agenttype", create_constraint=False, native_enum=True, create_type=False), nullable=False
    )
    input_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    output_data: Mapped[dict | None] = mapped_column(JSONB)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[AgentRunStatus] = mapped_column(
        Enum(AgentRunStatus, name="agentrunstatus", create_constraint=False, native_enum=True, create_type=False),
        nullable=False,
        default=AgentRunStatus.started,
    )
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="agent_runs")  # noqa: F821
