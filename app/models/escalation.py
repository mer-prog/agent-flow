import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EscalationStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    completed = "completed"


class Escalation(Base):
    __tablename__ = "escalations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False
    )
    ticket_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tickets.id")
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment_score: Mapped[float | None] = mapped_column(Float)
    status: Mapped[EscalationStatus] = mapped_column(
        Enum(EscalationStatus, name="escalationstatus", create_constraint=False, native_enum=True, create_type=False),
        nullable=False,
        default=EscalationStatus.pending,
    )
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    conversation: Mapped["Conversation"] = relationship()  # noqa: F821
    ticket: Mapped["Ticket | None"] = relationship()  # noqa: F821
    reviewer: Mapped["User | None"] = relationship(foreign_keys=[reviewed_by])  # noqa: F821
