"""Agent utilities shared across all agent nodes."""

from __future__ import annotations


def extract_last_message(state: dict) -> str:
    """Extract the text content of the last message from agent state."""
    messages = state.get("messages", [])
    if not messages:
        return ""
    last = messages[-1]
    return last.content if hasattr(last, "content") else str(last.get("content", ""))
