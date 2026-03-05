from __future__ import annotations

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list[dict], add_messages]
    intent: str | None
    confidence: float
    user_id: str
    conversation_id: str
    context: dict
    response: str | None
    agent_trace: list[dict]
    require_human_review: bool
    ticket_id: str | None
    kb_results: list[dict]
