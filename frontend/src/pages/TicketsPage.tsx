import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Loader2, Inbox } from "lucide-react";
import { apiFetch } from "../api/client";
import { TICKET_STATUS_COLORS, TICKET_PRIORITY_COLORS } from "../constants/colors";
import type { Ticket } from "../types";

export default function TicketsPage() {
  const { t } = useTranslation();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [total, setTotal] = useState(0);
  const [filter, setFilter] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");
    const params = filter ? `?status=${filter}` : "";
    apiFetch<{ items: Ticket[]; total: number }>(`/tickets${params}`)
      .then((r) => {
        setTickets(r.items);
        setTotal(r.total);
      })
      .catch((e) => setError(e instanceof Error ? e.message : t("common.error")))
      .finally(() => setLoading(false));
  }, [filter, t]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t("tickets.title")}</h1>
        <div className="flex gap-2" role="group" aria-label="Filter by status">
          {["", "open", "in_progress", "resolved", "closed"].map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              aria-pressed={filter === s}
              className={`px-3 py-2 text-xs rounded-full transition-colors min-h-[44px] ${
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

      {error && (
        <div className="text-center py-4 text-red-400" role="alert">{error}</div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-32" role="status">
          <Loader2 className="animate-spin text-zinc-400" size={24} />
          <span className="sr-only">{t("common.loading")}</span>
        </div>
      ) : (
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
                  <span className={`px-2 py-0.5 text-xs rounded-full ${TICKET_STATUS_COLORS[ticket.status] ?? ""}`}>
                    {t(`tickets.status.${ticket.status}` as const)}
                  </span>
                  <span className={`px-2 py-0.5 text-xs rounded-full ${TICKET_PRIORITY_COLORS[ticket.priority] ?? ""}`}>
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

          {tickets.length === 0 && !error && (
            <div className="text-center py-12">
              <Inbox className="mx-auto text-zinc-600 mb-2" size={32} />
              <p className="text-zinc-500">No tickets found</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
