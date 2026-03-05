from __future__ import annotations

import re
import time
import uuid

from app.agents.state import AgentState
from app.config import settings


def _extract_ticket_demo(text: str) -> dict:
    """Keyword-based ticket field extraction for demo mode."""
    lower = text.lower()

    # Priority detection
    priority = "medium"
    if any(w in lower for w in ("urgent", "critical", "emergency", "asap")):
        priority = "urgent"
    elif any(w in lower for w in ("high", "important", "serious")):
        priority = "high"
    elif any(w in lower for w in ("low", "minor", "small")):
        priority = "low"

    # Category detection
    category = "general"
    for cat in ("billing", "technical", "account", "shipping", "product", "feature"):
        if cat in lower:
            category = cat
            break

    # Title: first sentence or first 80 chars
    title = text.split(".")[0][:80] if "." in text else text[:80]

    return {
        "title": title.strip(),
        "description": text,
        "priority": priority,
        "category": category,
    }


async def _extract_ticket_live(text: str) -> dict:
    """LLM-based ticket field extraction using Claude Haiku."""
    from app.agents.llm import get_llm

    llm = get_llm()

    resp = await llm.ainvoke(
        [
            {
                "role": "system",
                "content": (
                    "Extract ticket fields from the user message. Reply in this exact format:\n"
                    "title: <short descriptive title>\n"
                    "priority: <low|medium|high|urgent>\n"
                    "category: <billing|technical|account|shipping|product|feature|general>"
                ),
            },
            {"role": "user", "content": text},
        ]
    )

    result = {"title": text[:80], "description": text, "priority": "medium", "category": "general"}
    for line in resp.content.strip().split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip().lower()
            val = val.strip()
            if key in result:
                result[key] = val

    return result


async def ticket_agent(state: AgentState) -> dict:
    """Ticket Agent: creates support tickets from conversation."""
    start = time.time()

    messages = state.get("messages", [])
    last_msg = ""
    if messages:
        last = messages[-1]
        last_msg = last.content if hasattr(last, "content") else str(last.get("content", ""))

    if settings.is_live_mode:
        ticket_data = await _extract_ticket_live(last_msg)
    else:
        ticket_data = _extract_ticket_demo(last_msg)

    ticket_id = str(uuid.uuid4())
    duration = int((time.time() - start) * 1000)

    response = (
        f"I've created a support ticket for you.\n\n"
        f"**Ticket #{ticket_id[:8]}**\n"
        f"- **Title**: {ticket_data['title']}\n"
        f"- **Priority**: {ticket_data['priority']}\n"
        f"- **Category**: {ticket_data['category']}\n\n"
        f"Our team will review it shortly."
    )

    return {
        "response": response,
        "ticket_id": ticket_id,
        "context": {
            **state.get("context", {}),
            "ticket_data": ticket_data,
        },
        "agent_trace": state.get("agent_trace", [])
        + [
            {
                "agent": "ticket",
                "duration_ms": duration,
                "ticket_id": ticket_id,
            }
        ],
    }
