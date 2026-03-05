from __future__ import annotations

import time

from app.agents.state import AgentState


async def response_formatter(state: AgentState) -> dict:
    """Response Formatter: formats the final response with metadata."""
    start = time.time()

    response = state.get("response", "")
    intent = state.get("intent", "unknown")
    confidence = state.get("confidence", 0.0)
    require_review = state.get("require_human_review", False)

    # Build metadata footer
    meta_parts = [f"Intent: {intent} ({confidence:.0%})"]
    if state.get("ticket_id"):
        meta_parts.append(f"Ticket: {state['ticket_id'][:8]}")
    if require_review:
        meta_parts.append("Status: Pending human review")

    duration = int((time.time() - start) * 1000)

    return {
        "response": response,
        "context": {
            **state.get("context", {}),
            "formatted": True,
            "meta": " | ".join(meta_parts),
        },
        "agent_trace": state.get("agent_trace", [])
        + [{"agent": "formatter", "duration_ms": duration}],
    }
