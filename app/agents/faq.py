from __future__ import annotations

import time

from app.agents.state import AgentState
from app.config import settings

_FAQ_TEMPLATES: dict[str, str] = {
    "price": "Our plans start at $9.99/month for Basic, $29.99/month for Pro, and $99.99/month for Enterprise. All plans include a 14-day free trial.",
    "shipping": "We offer free standard shipping on orders over $50. Express shipping is available for $12.99. Orders are typically delivered within 3-5 business days.",
    "return": "We accept returns within 30 days of purchase. Items must be in original condition. Refunds are processed within 5-7 business days after we receive the item.",
    "support": "Our support team is available 24/7 via chat, email (support@example.com), or phone (1-800-EXAMPLE). Premium support with dedicated agents is available on Enterprise plans.",
    "feature": "Key features include: real-time analytics, custom dashboards, API access, team collaboration tools, and automated reporting. Enterprise plans also include SSO and audit logs.",
    "policy": "Our privacy policy ensures your data is encrypted at rest and in transit. We are SOC 2 Type II certified and GDPR compliant. We never sell your data to third parties.",
}


def _generate_demo_answer(query: str, kb_results: list[dict]) -> str:
    """Generate a template-based answer for demo mode."""
    lower = query.lower()

    # Check KB results first
    if kb_results:
        top = kb_results[0]
        return f"Based on our knowledge base:\n\n**{top['article_title']}**\n\n{top['content']}"

    # Fall back to templates
    for keyword, template in _FAQ_TEMPLATES.items():
        if keyword in lower:
            return template

    return "I'd be happy to help you with that question. Could you provide more details so I can give you the most accurate information?"


async def _generate_live_answer(query: str, kb_results: list[dict]) -> str:
    """Generate an LLM-powered answer using Claude Haiku + RAG context."""
    from app.agents.llm import get_llm

    llm = get_llm()

    context = "\n\n".join(
        f"[{r['article_title']}]: {r['content']}" for r in kb_results
    ) if kb_results else "No relevant knowledge base articles found."

    resp = await llm.ainvoke(
        [
            {
                "role": "system",
                "content": (
                    "You are a helpful customer support agent. Answer the user's question "
                    "using the provided knowledge base context. Be concise and friendly. "
                    "If the context doesn't contain relevant information, provide a general "
                    "helpful response.\n\n"
                    f"Knowledge Base Context:\n{context}"
                ),
            },
            {"role": "user", "content": query},
        ]
    )

    return resp.content


async def faq_agent(state: AgentState) -> dict:
    """FAQ Agent: RAG-powered question answering."""
    start = time.time()

    messages = state.get("messages", [])
    last_msg = ""
    if messages:
        last = messages[-1]
        last_msg = last.content if hasattr(last, "content") else str(last.get("content", ""))

    kb_results = state.get("kb_results", [])

    if settings.is_live_mode:
        response = await _generate_live_answer(last_msg, kb_results)
    else:
        response = _generate_demo_answer(last_msg, kb_results)

    duration = int((time.time() - start) * 1000)

    return {
        "response": response,
        "agent_trace": state.get("agent_trace", [])
        + [
            {
                "agent": "faq",
                "duration_ms": duration,
                "kb_results_count": len(kb_results),
            }
        ],
    }
