export interface User {
  id: string;
  email: string;
  full_name: string;
  role: "admin" | "agent" | "customer";
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  title: string | null;
  status: "active" | "closed" | "archived";
  created_at: string;
  updated_at: string | null;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  metadata_: Record<string, unknown> | null;
  created_at: string;
}

export interface Ticket {
  id: string;
  conversation_id: string | null;
  user_id: string;
  title: string;
  description: string;
  status: "open" | "in_progress" | "resolved" | "closed";
  priority: "low" | "medium" | "high" | "urgent";
  category: string | null;
  assigned_to: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface Escalation {
  id: string;
  conversation_id: string;
  ticket_id: string | null;
  reason: string;
  sentiment_score: number | null;
  status: "pending" | "approved" | "rejected" | "completed";
  reviewed_by: string | null;
  reviewed_at: string | null;
  notes: string | null;
  created_at: string;
}

export interface KBArticle {
  id: string;
  title: string;
  content: string;
  category: string | null;
  is_published: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface DashboardStats {
  total_conversations: number;
  active_conversations: number;
  total_tickets: number;
  open_tickets: number;
  pending_escalations: number;
  avg_response_time_ms: number | null;
  resolution_rate: number | null;
}

export interface AgentPerformance {
  agent_type: string;
  total_runs: number;
  completed_runs: number;
  failed_runs: number;
  avg_duration_ms: number | null;
}
