import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../api/client";
import type { Ticket } from "../types";

const STATUS_COLORS: Record<string, string> = {
  open: "bg-yellow-500/20 text-yellow-400",
  in_progress: "bg-blue-500/20 text-blue-400",
  resolved: "bg-green-500/20 text-green-400",
  closed: "bg-zinc-500/20 text-zinc-400",
};

const PRIORITY_COLORS: Record<string, string> = {
  low: "bg-zinc-500/20 text-zinc-400",
  medium: "bg-blue-500/20 text-blue-400",
  high: "bg-orange-500/20 text-orange-400",
  urgent: "bg-red-500/20 text-red-400",
};

export default function TicketsPage() {
  const { t } = useTranslation();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [total, setTotal] = useState(0);
  const [filter, setFilter] = useState<string>("");

  useEffect(() => {
    const params = filter ? `?status=${filter}` : "";
    apiFetch<{ items: Ticket[]; total: number }>(`/tickets${params}`)
      .then((r) => {
        setTickets(r.items);
        setTotal(r.total);
      })
      .catch(() => {});
  }, [filter]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t("tickets.title")}</h1>
        <div className="flex gap-2">
          {["", "open", "in_progress", "resolved", "closed"].map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`px-3 py-1 text-xs rounded-full transition-colors ${
                filter === s
                  ? "bg-blue-600 text-white"
                  : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"
              }`}
            >
              {s ? t(`tickets.status.${s}` as const) : "All"}
            </button>
          ))}
        </div>
      </div>

      <div className="text-sm text-zinc-500">{total} tickets</div>

      <div className="space-y-2">
        {tickets.map((ticket) => (
          <div
            key={ticket.id}
            className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 hover:border-zinc-700 transition-colors"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0">
                <h3 className="font-medium text-zinc-100 truncate">{ticket.title}</h3>
                <p className="text-sm text-zinc-500 mt-1 line-clamp-2">{ticket.description}</p>
              </div>
              <div className="flex gap-2 shrink-0">
                <span className={`px-2 py-0.5 text-xs rounded-full ${STATUS_COLORS[ticket.status] ?? ""}`}>
                  {t(`tickets.status.${ticket.status}` as const)}
                </span>
                <span className={`px-2 py-0.5 text-xs rounded-full ${PRIORITY_COLORS[ticket.priority] ?? ""}`}>
                  {t(`tickets.priority.${ticket.priority}` as const)}
                </span>
              </div>
            </div>
            <div className="text-xs text-zinc-600 mt-2">
              {new Date(ticket.created_at).toLocaleString()}
              {ticket.category && <span className="ml-2">#{ticket.category}</span>}
            </div>
          </div>
        ))}

        {tickets.length === 0 && (
          <p className="text-center text-zinc-500 py-8">No tickets found</p>
        )}
      </div>
    </div>
  );
}
