from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.agents.graph import agent_graph
from app.api.deps import get_current_user, get_db
from app.models.conversation import Conversation, ConversationStatus
from app.models.message import Message, MessageRole
from app.models.user import User
from app.schemas.chat import ChatRequest
from app.schemas.conversation import ConversationDetail, MessageResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
async def chat(
    body: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    # Get or create conversation
    if body.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == body.conversation_id,
                Conversation.user_id == user.id,
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(user_id=user.id, title=body.message[:50])
        db.add(conversation)
        await db.flush()

    # Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        role=MessageRole.user,
        content=body.message,
    )
    db.add(user_msg)
    await db.flush()

    conversation_id = conversation.id

    async def event_stream():  # type: ignore[no-untyped-def]
        yield _sse("conversation_id", str(conversation_id))

        # Run agent graph
        state = {
            "messages": [{"role": "user", "content": body.message}],
            "intent": None,
            "confidence": 0.0,
            "user_id": str(user.id),
            "conversation_id": str(conversation_id),
            "context": {},
            "response": None,
            "agent_trace": [],
            "require_human_review": False,
            "ticket_id": None,
            "kb_results": [],
        }

        result = await agent_graph.ainvoke(state)

        # Stream agent trace events
        for trace in result.get("agent_trace", []):
            yield _sse("agent_trace", json.dumps(trace))

        # Stream response
        response_text = result.get("response", "")
        if response_text:
            # Stream in chunks for SSE effect
            words = response_text.split(" ")
            for i in range(0, len(words), 3):
                chunk = " ".join(words[i : i + 3])
                yield _sse("token", chunk + " ")

        yield _sse("done", "")

        # Save assistant message (in a new session since the outer one may be committed)
        async with (await _get_session()) as save_db:
            assistant_msg = Message(
                conversation_id=conversation_id,
                role=MessageRole.assistant,
                content=response_text,
                metadata_={"intent": result.get("intent"), "agent_trace": result.get("agent_trace", [])},
            )
            save_db.add(assistant_msg)
            await save_db.commit()

    return StreamingResponse(event_stream(), media_type="text/event-stream")


async def _get_session():  # type: ignore[no-untyped-def]
    from app.database import async_session
    return async_session()


def _sse(event: str, data: str) -> str:
    return f"event: {event}\ndata: {data}\n\n"


@router.get("/{conversation_id}/history", response_model=list[MessageResponse])
async def get_history(
    conversation_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Message]:
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    return list(result.scalars().all())
