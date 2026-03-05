import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { Loader2 } from "lucide-react";
import { apiFetch } from "../api/client";
import type { DashboardStats, AgentPerformance } from "../types";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"];

export default function DashboardPage() {
  const { t } = useTranslation();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [agents, setAgents] = useState<AgentPerformance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    Promise.all([
      apiFetch<DashboardStats>("/stats"),
      apiFetch<{ items: AgentPerformance[] }>("/stats/agent-performance"),
    ])
      .then(([s, a]) => {
        setStats(s);
        setAgents(a.items);
      })
      .catch((e) => setError(e instanceof Error ? e.message : t("common.error")))
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, [t]);

  const kpiCards = useMemo(
    () =>
      stats
        ? [
            { label: t("dashboard.totalConversations"), value: stats.total_conversations },
            { label: t("dashboard.activeConversations"), value: stats.active_conversations },
            { label: t("dashboard.openTickets"), value: stats.open_tickets },
            { label: t("dashboard.pendingEscalations"), value: stats.pending_escalations },
            { label: t("dashboard.resolutionRate"), value: stats.resolution_rate != null ? `${stats.resolution_rate}%` : "—" },
            { label: t("dashboard.avgResponseTime"), value: stats.avg_response_time_ms != null ? `${Math.round(stats.avg_response_time_ms)}ms` : "—" },
          ]
        : [],
    [stats, t],
  );

  const pieData = useMemo(
    () => agents.filter((a) => a.total_runs > 0).map((a) => ({ name: a.agent_type, value: a.total_runs })),
    [agents],
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" role="status">
        <Loader2 className="animate-spin text-zinc-400" size={32} />
        <span className="sr-only">{t("common.loading")}</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12" role="alert">
        <p className="text-red-400">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">{t("nav.dashboard")}</h1>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {kpiCards.map((card) => (
          <div key={card.label} className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
            <p className="text-xs text-zinc-500 mb-1">{card.label}</p>
            <p className="text-2xl font-bold text-zinc-100">{card.value}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <h3 className="text-sm font-medium text-zinc-400 mb-4">Agent Performance</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={agents}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
              <XAxis dataKey="agent_type" stroke="#71717a" fontSize={12} />
              <YAxis stroke="#71717a" fontSize={12} />
              <Tooltip
                contentStyle={{ backgroundColor: "#18181b", border: "1px solid #27272a", borderRadius: "8px" }}
                labelStyle={{ color: "#a1a1aa" }}
              />
              <Bar dataKey="completed_runs" fill="#3b82f6" name="Completed" radius={[4, 4, 0, 0]} />
              <Bar dataKey="failed_runs" fill="#ef4444" name="Failed" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <h3 className="text-sm font-medium text-zinc-400 mb-4">Agent Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} dataKey="value" label>
                {pieData.map((entry) => (
                  <Cell key={entry.name} fill={COLORS[pieData.indexOf(entry) % COLORS.length]!} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: "#18181b", border: "1px solid #27272a", borderRadius: "8px" }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
