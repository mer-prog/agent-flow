from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.agent_run import AgentRun, AgentRunStatus
from app.models.conversation import Conversation, ConversationStatus
from app.models.escalation import Escalation, EscalationStatus
from app.models.ticket import Ticket, TicketStatus
from app.models.user import User
from app.schemas.stats import AgentPerformance, AgentPerformanceList, DashboardStats

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=DashboardStats)
async def dashboard_stats(
    days: int = 30,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    since = datetime.now(UTC) - timedelta(days=days)

    total_convos = await db.scalar(
        select(func.count(Conversation.id)).where(Conversation.created_at >= since)
    ) or 0
    active_convos = await db.scalar(
        select(func.count(Conversation.id)).where(
            Conversation.status == ConversationStatus.active,
            Conversation.created_at >= since,
        )
    ) or 0
    total_tickets = await db.scalar(
        select(func.count(Ticket.id)).where(Ticket.created_at >= since)
    ) or 0
    open_tickets = await db.scalar(
        select(func.count(Ticket.id)).where(
            Ticket.status == TicketStatus.open, Ticket.created_at >= since
        )
    ) or 0
    pending_esc = await db.scalar(
        select(func.count(Escalation.id)).where(Escalation.status == EscalationStatus.pending)
    ) or 0
    avg_duration = await db.scalar(
        select(func.avg(AgentRun.duration_ms)).where(AgentRun.created_at >= since)
    )

    resolved = await db.scalar(
        select(func.count(Ticket.id)).where(
            Ticket.status == TicketStatus.resolved, Ticket.created_at >= since
        )
    ) or 0
    resolution_rate = (resolved / total_tickets * 100) if total_tickets else None

    return {
        "total_conversations": total_convos,
        "active_conversations": active_convos,
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "pending_escalations": pending_esc,
        "avg_response_time_ms": float(avg_duration) if avg_duration else None,
        "resolution_rate": round(resolution_rate, 1) if resolution_rate else None,
    }


@router.get("/agent-performance", response_model=AgentPerformanceList)
async def agent_performance(
    days: int = 30,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    since = datetime.now(UTC) - timedelta(days=days)

    result = await db.execute(
        select(
            AgentRun.agent_type,
            func.count(AgentRun.id).label("total"),
            func.count(AgentRun.id).filter(AgentRun.status == AgentRunStatus.completed).label("completed"),
            func.count(AgentRun.id).filter(AgentRun.status == AgentRunStatus.failed).label("failed"),
            func.avg(AgentRun.duration_ms).label("avg_duration"),
        )
        .where(AgentRun.created_at >= since)
        .group_by(AgentRun.agent_type)
    )

    items = [
        {
            "agent_type": row.agent_type.value if hasattr(row.agent_type, "value") else row.agent_type,
            "total_runs": row.total,
            "completed_runs": row.completed,
            "failed_runs": row.failed,
            "avg_duration_ms": float(row.avg_duration) if row.avg_duration else None,
        }
        for row in result.all()
    ]

    return {"items": items}
