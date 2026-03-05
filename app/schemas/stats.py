from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_conversations: int
    active_conversations: int
    total_tickets: int
    open_tickets: int
    pending_escalations: int
    avg_response_time_ms: float | None
    resolution_rate: float | None


class AgentPerformance(BaseModel):
    agent_type: str
    total_runs: int
    completed_runs: int
    failed_runs: int
    avg_duration_ms: float | None


class AgentPerformanceList(BaseModel):
    items: list[AgentPerformance]
