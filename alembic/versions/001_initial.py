"""Initial migration with all tables and pgvector

Revision ID: 001
Revises:
Create Date: 2026-03-05

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create enum types idempotently with raw SQL
    op.execute("DO $$ BEGIN CREATE TYPE userrole AS ENUM ('admin', 'agent', 'customer'); EXCEPTION WHEN duplicate_object THEN null; END $$")
    op.execute("DO $$ BEGIN CREATE TYPE conversationstatus AS ENUM ('active', 'closed', 'archived'); EXCEPTION WHEN duplicate_object THEN null; END $$")
    op.execute("DO $$ BEGIN CREATE TYPE messagerole AS ENUM ('user', 'assistant', 'system'); EXCEPTION WHEN duplicate_object THEN null; END $$")
    op.execute("DO $$ BEGIN CREATE TYPE ticketstatus AS ENUM ('open', 'in_progress', 'resolved', 'closed'); EXCEPTION WHEN duplicate_object THEN null; END $$")
    op.execute("DO $$ BEGIN CREATE TYPE ticketpriority AS ENUM ('low', 'medium', 'high', 'urgent'); EXCEPTION WHEN duplicate_object THEN null; END $$")
    op.execute("DO $$ BEGIN CREATE TYPE escalationstatus AS ENUM ('pending', 'approved', 'rejected', 'completed'); EXCEPTION WHEN duplicate_object THEN null; END $$")
    op.execute("DO $$ BEGIN CREATE TYPE agenttype AS ENUM ('router', 'faq', 'ticket', 'escalation', 'chitchat', 'formatter'); EXCEPTION WHEN duplicate_object THEN null; END $$")
    op.execute("DO $$ BEGIN CREATE TYPE agentrunstatus AS ENUM ('started', 'completed', 'failed'); EXCEPTION WHEN duplicate_object THEN null; END $$")

    # Reference enums with create_type=False (already created above)
    userrole = sa.Enum("admin", "agent", "customer", name="userrole", create_type=False)
    conversationstatus = sa.Enum("active", "closed", "archived", name="conversationstatus", create_type=False)
    messagerole = sa.Enum("user", "assistant", "system", name="messagerole", create_type=False)
    ticketstatus = sa.Enum("open", "in_progress", "resolved", "closed", name="ticketstatus", create_type=False)
    ticketpriority = sa.Enum("low", "medium", "high", "urgent", name="ticketpriority", create_type=False)
    escalationstatus = sa.Enum("pending", "approved", "rejected", "completed", name="escalationstatus", create_type=False)
    agenttype = sa.Enum("router", "faq", "ticket", "escalation", "chitchat", "formatter", name="agenttype", create_type=False)
    agentrunstatus = sa.Enum("started", "completed", "failed", name="agentrunstatus", create_type=False)

    # users
    op.create_table(
        "users",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", userrole, nullable=False, server_default="customer"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )

    # conversations
    op.create_table(
        "conversations",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255)),
        sa.Column("status", conversationstatus, nullable=False, server_default="active"),
        sa.Column("metadata", sa.dialects.postgresql.JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )

    # messages
    op.create_table(
        "messages",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("role", messagerole, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("metadata", sa.dialects.postgresql.JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # tickets
    op.create_table(
        "tickets",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id")),
        sa.Column("user_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("status", ticketstatus, nullable=False, server_default="open"),
        sa.Column("priority", ticketpriority, nullable=False, server_default="medium"),
        sa.Column("category", sa.String(100)),
        sa.Column("assigned_to", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )

    # escalations
    op.create_table(
        "escalations",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("ticket_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("tickets.id")),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("sentiment_score", sa.Float),
        sa.Column("status", escalationstatus, nullable=False, server_default="pending"),
        sa.Column("reviewed_by", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )

    # kb_articles
    op.create_table(
        "kb_articles",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("category", sa.String(100)),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )

    # kb_chunks
    op.create_table(
        "kb_chunks",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("article_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("kb_articles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("embedding", Vector(1536)),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # agent_runs
    op.create_table(
        "agent_runs",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("agent_type", agenttype, nullable=False),
        sa.Column("input_data", sa.dialects.postgresql.JSONB, nullable=False),
        sa.Column("output_data", sa.dialects.postgresql.JSONB),
        sa.Column("duration_ms", sa.Integer),
        sa.Column("status", agentrunstatus, nullable=False, server_default="started"),
        sa.Column("error_message", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("agent_runs")
    op.drop_table("kb_chunks")
    op.drop_table("kb_articles")
    op.drop_table("escalations")
    op.drop_table("tickets")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("users")

    for name in [
        "agentrunstatus", "agenttype", "escalationstatus",
        "ticketpriority", "ticketstatus", "messagerole",
        "conversationstatus", "userrole",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {name}")

    op.execute("DROP EXTENSION IF EXISTS vector")
