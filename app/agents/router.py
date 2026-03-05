from __future__ import annotations

import re
import time
import uuid

from app.agents.state import AgentState
from app.config import settings

# Demo mode keyword patterns
_INTENT_PATTERNS: dict[str, list[str]] = {
    "ticket": [
        r"\b(create|open|submit|file|new)\b.*(ticket|issue|request|bug|problem)",
        r"\b(ticket|issue|request|bug)\b.*(create|open|submit|file)",
        r"\b(report|reporting)\b.*(issue|bug|problem)",
    ],
    "escalation": [
        r"\b(escalat|speak|talk|connect)\b.*(human|agent|person|manager|supervisor)",
        r"\b(angry|furious|frustrated|unacceptable|terrible|worst|hate|disgusted)\b",
        r"\b(demand|insist|require)\b.*(refund|compensation|manager)",
    ],
    "faq": [
        r"\b(how|what|when|where|why|can i|do you|is there|tell me)\b",
        r"\b(help|guide|explain|info|information|documentation)\b",
        r"\b(price|pricing|cost|plan|feature|support|policy|return|refund|shipping)\b",
    ],
}


def _classify_demo(text: str) -> tuple[str, float]:
    """Keyword-based intent classification for demo mode."""
    lower = text.lower()

    for intent, patterns in _INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, lower):
                return intent, 0.85

    return "chitchat", 0.7


async def _classify_live(messages: list[dict]) -> tuple[str, float]:
    """LLM-based intent classification using Claude Haiku."""
    from app.agents.llm import get_llm

    llm = get_llm()

    last_message = messages[-1]["content"] if messages else ""
    resp = await llm.ainvoke(
        [
            {
                "role": "system",
                "content": (
                    "Classify the user's intent into exactly one category: "
                    "faq, ticket, escalation, or chitchat. "
                    "Reply with ONLY the category name followed by a confidence score 0-1. "
                    "Format: category|score"
                ),
            },
            {"role": "user", "content": last_message},
        ]
    )

    text = resp.content.strip()
    parts = text.split("|")
    intent = parts[0].strip().lower()
    confidence = float(parts[1].strip()) if len(parts) > 1 else 0.8

    if intent not in ("faq", "ticket", "escalation", "chitchat"):
        intent = "chitchat"
        confidence = 0.5

    return intent, confidence


async def router_agent(state: AgentState) -> dict:
    """Router Agent: classifies user intent."""
    start = time.time()

    messages = state.get("messages", [])
    last_msg = ""
    if messages:
        last = messages[-1]
        last_msg = last.content if hasattr(last, "content") else str(last.get("content", ""))

    if settings.is_live_mode:
        intent, confidence = await _classify_live(
            [{"content": last_msg}]
        )
    else:
        intent, confidence = _classify_demo(last_msg)

    duration = int((time.time() - start) * 1000)

    return {
        "intent": intent,
        "confidence": confidence,
        "agent_trace": [
            {
                "agent": "router",
                "intent": intent,
                "confidence": confidence,
                "duration_ms": duration,
            }
        ],
    }
