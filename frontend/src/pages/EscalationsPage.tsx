import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Check, X, Loader2, Inbox } from "lucide-react";
import { apiFetch } from "../api/client";
import { ESCALATION_STATUS_COLORS } from "../constants/colors";
import type { Escalation } from "../types";

export default function EscalationsPage() {
  const { t } = useTranslation();
  const [escalations, setEscalations] = useState<Escalation[]>([]);
  const [filter, setFilter] = useState<string>("pending");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = () => {
    setLoading(true);
    setError("");
    const params = filter ? `?status=${filter}` : "";
    apiFetch<{ items: Escalation[]; total: number }>(`/escalations${params}`)
      .then((r) => setEscalations(r.items))
      .catch((e) => setError(e instanceof Error ? e.message : t("common.error")))
      .finally(() => setLoading(false));
  };

  useEffect(load, [filter, t]);

  const handleReview = async (id: string, action: "approve" | "reject") => {
    try {
      await apiFetch(`/escalations/${id}/review`, {
        method: "POST",
        body: JSON.stringify({ action }),
      });
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : t("common.error"));
    }
  };

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">{t("escalations.title")}</h1>

      <div className="flex gap-2" role="group" aria-label="Filter by status">
        {["pending", "approved", "rejected", ""].map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            aria-pressed={filter === s}
            className={`px-3 py-2 text-xs rounded-full min-h-[44px] ${
              filter === s ? "bg-blue-600 text-white" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"
            }`}
          >
            {s ? t(`escalations.status.${s}` as const) : "All"}
          </button>
        ))}
      </div>

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
                  <span className={`px-2 py-0.5 text-xs rounded-full ${ESCALATION_STATUS_COLORS[esc.status] ?? ""}`}>
                    {t(`escalations.status.${esc.status}` as const)}
                  </span>
                  {esc.status === "pending" && (
                    <>
                      <button
                        onClick={() => handleReview(esc.id, "approve")}
                        className="p-2.5 bg-green-600 hover:bg-green-700 rounded-lg text-white min-w-[44px] min-h-[44px] flex items-center justify-center"
                        aria-label={t("escalations.approve")}
                      >
                        <Check size={16} />
                      </button>
                      <button
                        onClick={() => handleReview(esc.id, "reject")}
                        className="p-2.5 bg-red-600 hover:bg-red-700 rounded-lg text-white min-w-[44px] min-h-[44px] flex items-center justify-center"
                        aria-label={t("escalations.reject")}
                      >
                        <X size={16} />
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

          {escalations.length === 0 && !error && (
            <div className="text-center py-12">
              <Inbox className="mx-auto text-zinc-600 mb-2" size={32} />
              <p className="text-zinc-500">No escalations found</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
