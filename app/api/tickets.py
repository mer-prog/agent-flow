from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.ticket import Ticket, TicketStatus
from app.models.user import User, UserRole
from app.schemas.ticket import TicketCreate, TicketList, TicketResponse, TicketUpdate

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.get("", response_model=TicketList)
async def list_tickets(
    skip: int = 0,
    limit: int = 20,
    status: TicketStatus | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    query = select(Ticket)
    # Customers see only their tickets; agents/admins see all
    if user.role == UserRole.customer:
        query = query.where(Ticket.user_id == user.id)
    if status:
        query = query.where(Ticket.status == status)

    total = await db.scalar(select(func.count()).select_from(query.subquery()))

    result = await db.execute(
        query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit)
    )
    items = list(result.scalars().all())

    return {"items": items, "total": total or 0}


@router.post("", response_model=TicketResponse, status_code=201)
async def create_ticket(
    body: TicketCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Ticket:
    ticket = Ticket(
        title=body.title,
        description=body.description,
        priority=body.priority,
        category=body.category,
        conversation_id=body.conversation_id,
        user_id=user.id,
    )
    db.add(ticket)
    await db.flush()
    await db.refresh(ticket)
    return ticket


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Ticket:
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if user.role == UserRole.customer and ticket.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return ticket


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: uuid.UUID,
    body: TicketUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Ticket:
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if user.role == UserRole.customer and ticket.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    update_data = body.model_dump(exclude_unset=True)

    # Customers can only update title and description
    if user.role == UserRole.customer:
        allowed = {"title", "description"}
        update_data = {k: v for k, v in update_data.items() if k in allowed}

    for field, value in update_data.items():
        setattr(ticket, field, value)

    await db.flush()
    await db.refresh(ticket)
    return ticket
