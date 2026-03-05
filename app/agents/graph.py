from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.agents.chitchat import chitchat_agent
from app.agents.escalation import escalation_agent
from app.agents.faq import faq_agent
from app.agents.formatter import response_formatter
from app.agents.router import router_agent
from app.agents.state import AgentState
from app.agents.ticket import ticket_agent


def route_by_intent(state: AgentState) -> str:
    """Route to the appropriate agent based on classified intent."""
    match state.get("intent"):
        case "faq":
            return "faq_agent"
        case "ticket":
            return "ticket_agent"
        case "escalation":
            return "escalation_agent"
        case _:
            return "chitchat_agent"


def build_graph() -> StateGraph:
    """Build the multi-agent LangGraph state graph."""
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("router", router_agent)
    graph.add_node("faq_agent", faq_agent)
    graph.add_node("ticket_agent", ticket_agent)
    graph.add_node("escalation_agent", escalation_agent)
    graph.add_node("chitchat_agent", chitchat_agent)
    graph.add_node("formatter", response_formatter)

    # Entry point
    graph.set_entry_point("router")

    # Conditional routing from router
    graph.add_conditional_edges(
        "router",
        route_by_intent,
        {
            "faq_agent": "faq_agent",
            "ticket_agent": "ticket_agent",
            "escalation_agent": "escalation_agent",
            "chitchat_agent": "chitchat_agent",
        },
    )

    # All agents connect to formatter
    graph.add_edge("faq_agent", "formatter")
    graph.add_edge("ticket_agent", "formatter")
    graph.add_edge("escalation_agent", "formatter")
    graph.add_edge("chitchat_agent", "formatter")

    # Formatter → END
    graph.add_edge("formatter", END)

    return graph


# Compiled graph instance
agent_graph = build_graph().compile()
