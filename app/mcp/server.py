from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from fastmcp import FastMCP
from sqlalchemy import func, select

from app.database import async_session
from app.models.conversation import Conversation, ConversationStatus
from app.models.escalation import Escalation, EscalationStatus
from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.services.knowledge import search_knowledge_base

mcp = FastMCP("AgentFlow Support Tools")


@mcp.tool()
async def search_knowledge_base_tool(query: str, top_k: int = 5) -> list[dict]:
    """Search the knowledge base for relevant articles using semantic similarity.

    Args:
        query: The search query text.
        top_k: Maximum number of results to return (default: 5).
    """
    async with async_session() as db:
        results = await search_knowledge_base(db, query, top_k)
        return results


@mcp.tool()
async def create_ticket(
    title: str,
    description: str,
    priority: str = "medium",
    category: str = "general",
    user_id: str | None = None,
) -> dict:
    """Create a new support ticket.

    Args:
        title: Short descriptive title for the ticket.
        description: Detailed description of the issue.
        priority: Priority level: low, medium, high, or urgent.
        category: Category: billing, technical, account, shipping, product, feature, or general.
        user_id: UUID of the user creating the ticket (optional).
    """
    async with async_session() as db:
        ticket = Ticket(
            title=title,
            description=description,
            priority=TicketPriority(priority) if priority in TicketPriority.__members__ else TicketPriority.medium,
            category=category,
            user_id=uuid.UUID(user_id) if user_id else uuid.uuid4(),
        )
        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)

        return {
            "ticket_id": str(ticket.id),
            "title": ticket.title,
            "status": ticket.status.value,
            "priority": ticket.priority.value,
            "category": ticket.category,
            "created_at": ticket.created_at.isoformat(),
        }


@mcp.tool()
async def update_ticket(
    ticket_id: str,
    status: str | None = None,
    priority: str | None = None,
    assigned_to: str | None = None,
) -> dict:
    """Update an existing support ticket.

    Args:
        ticket_id: UUID of the ticket to update.
        status: New status: open, in_progress, resolved, or closed.
        priority: New priority: low, medium, high, or urgent.
        assigned_to: UUID of the agent to assign the ticket to.
    """
    async with async_session() as db:
        stmt = select(Ticket).where(Ticket.id == uuid.UUID(ticket_id))
        result = await db.execute(stmt)
        ticket = result.scalar_one_or_none()

        if not ticket:
            return {"error": f"Ticket {ticket_id} not found"}

        if status and status in TicketStatus.__members__:
            ticket.status = TicketStatus(status)
        if priority and priority in TicketPriority.__members__:
            ticket.priority = TicketPriority(priority)
        if assigned_to:
            ticket.assigned_to = uuid.UUID(assigned_to)

        await db.commit()
        await db.refresh(ticket)

        return {
            "ticket_id": str(ticket.id),
            "title": ticket.title,
            "status": ticket.status.value,
            "priority": ticket.priority.value,
            "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
        }


@mcp.tool()
async def get_support_metrics(days: int = 30) -> dict:
    """Get support dashboard metrics and statistics.

    Args:
        days: Number of days to look back for metrics (default: 30).
    """
    async with async_session() as db:
        since = datetime.now(UTC) - timedelta(days=days)

        # Total and active conversations
        total_convos = await db.scalar(
            select(func.count(Conversation.id)).where(Conversation.created_at >= since)
        )
        active_convos = await db.scalar(
            select(func.count(Conversation.id)).where(
                Conversation.status == ConversationStatus.active,
                Conversation.created_at >= since,
            )
        )

        # Ticket stats
        total_tickets = await db.scalar(
            select(func.count(Ticket.id)).where(Ticket.created_at >= since)
        )
        open_tickets = await db.scalar(
            select(func.count(Ticket.id)).where(
                Ticket.status == TicketStatus.open,
                Ticket.created_at >= since,
            )
        )
        resolved_tickets = await db.scalar(
            select(func.count(Ticket.id)).where(
                Ticket.status == TicketStatus.resolved,
                Ticket.created_at >= since,
            )
        )

        # Pending escalations
        pending_escalations = await db.scalar(
            select(func.count(Escalation.id)).where(
                Escalation.status == EscalationStatus.pending,
            )
        )

        resolution_rate = (
            (resolved_tickets / total_tickets * 100) if total_tickets else None
        )

        return {
            "period_days": days,
            "total_conversations": total_convos or 0,
            "active_conversations": active_convos or 0,
            "total_tickets": total_tickets or 0,
            "open_tickets": open_tickets or 0,
            "resolved_tickets": resolved_tickets or 0,
            "pending_escalations": pending_escalations or 0,
            "resolution_rate_pct": round(resolution_rate, 1) if resolution_rate else None,
        }


@mcp.tool()
async def escalate_to_human(conversation_id: str, reason: str) -> dict:
    """Escalate a conversation to a human agent for review.

    Args:
        conversation_id: UUID of the conversation to escalate.
        reason: Reason for the escalation.
    """
    async with async_session() as db:
        escalation = Escalation(
            conversation_id=uuid.UUID(conversation_id),
            reason=reason,
            status=EscalationStatus.pending,
        )
        db.add(escalation)
        await db.commit()
        await db.refresh(escalation)

        return {
            "escalation_id": str(escalation.id),
            "conversation_id": conversation_id,
            "status": escalation.status.value,
            "created_at": escalation.created_at.isoformat(),
        }
