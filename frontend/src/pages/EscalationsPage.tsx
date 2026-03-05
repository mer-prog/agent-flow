import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Check, X } from "lucide-react";
import { apiFetch } from "../api/client";
import type { Escalation } from "../types";

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-yellow-500/20 text-yellow-400",
  approved: "bg-green-500/20 text-green-400",
  rejected: "bg-red-500/20 text-red-400",
  completed: "bg-blue-500/20 text-blue-400",
};

export default function EscalationsPage() {
  const { t } = useTranslation();
  const [escalations, setEscalations] = useState<Escalation[]>([]);
  const [filter, setFilter] = useState<string>("pending");

  const load = () => {
    const params = filter ? `?status=${filter}` : "";
    apiFetch<{ items: Escalation[]; total: number }>(`/escalations${params}`)
      .then((r) => setEscalations(r.items))
      .catch(() => {});
  };

  useEffect(load, [filter]);

  const handleReview = async (id: string, action: "approve" | "reject") => {
    await apiFetch(`/escalations/${id}/review`, {
      method: "POST",
      body: JSON.stringify({ action }),
    });
    load();
  };

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">{t("escalations.title")}</h1>

      <div className="flex gap-2">
        {["pending", "approved", "rejected", ""].map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`px-3 py-1 text-xs rounded-full ${
              filter === s ? "bg-blue-600 text-white" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"
            }`}
          >
            {s ? t(`escalations.status.${s}` as const) : "All"}
          </button>
        ))}
      </div>

      <div className="space-y-2">
        {escalations.map((esc) => (
          <div key={esc.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0">
                <p className="text-sm text-zinc-200">{esc.reason}</p>
                {esc.sentiment_score != null && (
                  <p className="text-xs text-zinc-500 mt-1">
                    Sentiment: {(esc.sentiment_score * 100).toFixed(0)}%
                  </p>
                )}
                <p className="text-xs text-zinc-600 mt-1">
                  {new Date(esc.created_at).toLocaleString()}
                </p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className={`px-2 py-0.5 text-xs rounded-full ${STATUS_COLORS[esc.status] ?? ""}`}>
                  {t(`escalations.status.${esc.status}` as const)}
                </span>
                {esc.status === "pending" && (
                  <>
                    <button
                      onClick={() => handleReview(esc.id, "approve")}
                      className="p-1.5 bg-green-600 hover:bg-green-700 rounded-lg text-white"
                      title={t("escalations.approve")}
                    >
                      <Check size={14} />
                    </button>
                    <button
                      onClick={() => handleReview(esc.id, "reject")}
                      className="p-1.5 bg-red-600 hover:bg-red-700 rounded-lg text-white"
                      title={t("escalations.reject")}
                    >
                      <X size={14} />
                    </button>
                  </>
                )}
              </div>
            </div>
            {esc.notes && (
              <p className="text-xs text-zinc-500 mt-2 border-t border-zinc-800 pt-2">{esc.notes}</p>
            )}
          </div>
        ))}

        {escalations.length === 0 && (
          <p className="text-center text-zinc-500 py-8">No escalations found</p>
        )}
      </div>
    </div>
  );
}
