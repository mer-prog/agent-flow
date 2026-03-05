from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.escalation import Escalation, EscalationStatus
from app.models.user import User, UserRole
from app.schemas.escalation import EscalationList, EscalationResponse, EscalationReview

router = APIRouter(prefix="/api/escalations", tags=["escalations"])


@router.get("", response_model=EscalationList)
async def list_escalations(
    skip: int = 0,
    limit: int = 20,
    status: EscalationStatus | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if user.role == UserRole.customer:
        raise HTTPException(status_code=403, detail="Access denied")

    query = select(Escalation)
    if status:
        query = query.where(Escalation.status == status)

    total = await db.scalar(select(func.count()).select_from(query.subquery()))

    result = await db.execute(
        query.order_by(Escalation.created_at.desc()).offset(skip).limit(limit)
    )
    items = list(result.scalars().all())

    return {"items": items, "total": total or 0}


@router.get("/{escalation_id}", response_model=EscalationResponse)
async def get_escalation(
    escalation_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Escalation:
    if user.role == UserRole.customer:
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(select(Escalation).where(Escalation.id == escalation_id))
    escalation = result.scalar_one_or_none()
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")
    return escalation


@router.post("/{escalation_id}/review", response_model=EscalationResponse)
async def review_escalation(
    escalation_id: uuid.UUID,
    body: EscalationReview,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Escalation:
    if user.role == UserRole.customer:
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(select(Escalation).where(Escalation.id == escalation_id))
    escalation = result.scalar_one_or_none()
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")

    if escalation.status != EscalationStatus.pending:
        raise HTTPException(status_code=400, detail="Escalation already reviewed")

    if body.action == "approve":
        escalation.status = EscalationStatus.approved
    elif body.action == "reject":
        escalation.status = EscalationStatus.rejected
    else:
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")

    escalation.reviewed_by = user.id
    escalation.reviewed_at = datetime.now(UTC)
    escalation.notes = body.notes

    await db.flush()
    await db.refresh(escalation)
    return escalation
