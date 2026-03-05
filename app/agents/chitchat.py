from __future__ import annotations

import time

from app.agents.state import AgentState
from app.config import settings

_DEMO_RESPONSES: dict[str, str] = {
    "hello": "Hello! Welcome to AgentFlow support. How can I help you today?",
    "hi": "Hi there! How can I assist you today?",
    "thanks": "You're welcome! Is there anything else I can help you with?",
    "bye": "Goodbye! Feel free to reach out anytime you need help.",
    "good": "Glad to hear that! Is there anything else I can do for you?",
}

_DEFAULT_RESPONSE = (
    "Thanks for reaching out! I'm here to help with any questions about our products, "
    "services, or support. What can I assist you with?"
)


def _respond_demo(text: str) -> str:
    """Template-based conversational response for demo mode."""
    lower = text.lower().strip()
    for keyword, response in _DEMO_RESPONSES.items():
        if keyword in lower:
            return response
    return _DEFAULT_RESPONSE


async def _respond_live(messages: list[dict]) -> str:
    """LLM-powered conversational response using Claude Haiku."""
    from langchain_anthropic import ChatAnthropic

    llm = ChatAnthropic(
        model="claude-haiku-4-5-20241022",
        api_key=settings.ANTHROPIC_API_KEY,
        max_tokens=300,
    )

    last_msg = messages[-1]["content"] if messages else ""

    resp = await llm.ainvoke(
        [
            {
                "role": "system",
                "content": (
                    "You are a friendly customer support agent for AgentFlow. "
                    "Have a natural, helpful conversation. Be concise and warm."
                ),
            },
            {"role": "user", "content": last_msg},
        ]
    )

    return resp.content


async def chitchat_agent(state: AgentState) -> dict:
    """Chitchat Agent: general conversational responses."""
    start = time.time()

    messages = state.get("messages", [])
    last_msg = ""
    if messages:
        last = messages[-1]
        last_msg = last.content if hasattr(last, "content") else str(last.get("content", ""))

    if settings.is_live_mode:
        response = await _respond_live([{"content": last_msg}])
    else:
        response = _respond_demo(last_msg)

    duration = int((time.time() - start) * 1000)

    return {
        "response": response,
        "agent_trace": state.get("agent_trace", [])
        + [{"agent": "chitchat", "duration_ms": duration}],
    }
