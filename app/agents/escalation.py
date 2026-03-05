from __future__ import annotations

import time

from app.agents.state import AgentState
from app.config import settings

_NEGATIVE_WORDS = {
    "angry", "furious", "frustrated", "unacceptable", "terrible", "worst",
    "hate", "disgusted", "awful", "horrible", "useless", "incompetent",
    "ridiculous", "pathetic", "disappointed", "outraged", "livid",
}


def _analyze_sentiment_demo(text: str) -> float:
    """Keyword-based sentiment analysis for demo mode. Returns 0.0 (negative) to 1.0 (positive)."""
    lower = text.lower()
    words = set(lower.split())
    negative_count = len(words & _NEGATIVE_WORDS)

    if negative_count >= 3:
        return 0.1
    elif negative_count >= 2:
        return 0.25
    elif negative_count >= 1:
        return 0.4
    return 0.6


async def _analyze_sentiment_live(text: str) -> float:
    """LLM-based sentiment analysis using Claude Haiku."""
    from langchain_anthropic import ChatAnthropic

    llm = ChatAnthropic(
        model="claude-haiku-4-5-20241022",
        api_key=settings.ANTHROPIC_API_KEY,
        max_tokens=50,
    )

    resp = await llm.ainvoke(
        [
            {
                "role": "system",
                "content": (
                    "Analyze the sentiment of this customer message. "
                    "Reply with ONLY a number between 0.0 (very negative) and 1.0 (very positive)."
                ),
            },
            {"role": "user", "content": text},
        ]
    )

    try:
        return max(0.0, min(1.0, float(resp.content.strip())))
    except ValueError:
        return 0.5


async def escalation_agent(state: AgentState) -> dict:
    """Escalation Agent: sentiment analysis + human-in-the-loop."""
    start = time.time()

    messages = state.get("messages", [])
    last_msg = ""
    if messages:
        last = messages[-1]
        last_msg = last.content if hasattr(last, "content") else str(last.get("content", ""))

    if settings.is_live_mode:
        sentiment = await _analyze_sentiment_live(last_msg)
    else:
        sentiment = _analyze_sentiment_demo(last_msg)

    duration = int((time.time() - start) * 1000)

    response = (
        "I understand your concern and I want to make sure you get the help you need. "
        "I'm escalating this to a human agent who will be able to assist you directly.\n\n"
        f"**Sentiment Score**: {sentiment:.2f}\n"
        "A support agent will review this shortly."
    )

    return {
        "response": response,
        "require_human_review": True,
        "context": {
            **state.get("context", {}),
            "sentiment_score": sentiment,
            "escalation_reason": last_msg[:200],
        },
        "agent_trace": state.get("agent_trace", [])
        + [
            {
                "agent": "escalation",
                "duration_ms": duration,
                "sentiment_score": sentiment,
            }
        ],
    }
