import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { Send, Plus, Loader2 } from "lucide-react";
import { apiFetch } from "../api/client";
import { useSSE } from "../hooks/useSSE";
import type { Conversation, Message } from "../types";

export default function ChatPage() {
  const { t } = useTranslation();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loadingConvos, setLoadingConvos] = useState(true);
  const [error, setError] = useState("");
  const messagesEnd = useRef<HTMLDivElement>(null);
  const { events, isStreaming, stream } = useSSE();

  // Load conversations
  useEffect(() => {
    apiFetch<{ items: Conversation[] }>("/conversations")
      .then((r) => setConversations(r.items))
      .catch((e) => setError(e instanceof Error ? e.message : t("common.error")))
      .finally(() => setLoadingConvos(false));
  }, [t]);

  // Load messages when conversation changes
  useEffect(() => {
    if (activeId) {
      apiFetch<Message[]>(`/chat/${activeId}/history`)
        .then(setMessages)
        .catch((e) => setError(e instanceof Error ? e.message : t("common.error")));
    } else {
      setMessages([]);
    }
  }, [activeId, t]);

  // Build streaming response from SSE events
  const streamingText = useMemo(() => {
    return events
      .filter((e) => e.event === "token")
      .map((e) => e.data)
      .join("");
  }, [events]);

  // Update conversation ID from SSE
  useEffect(() => {
    const convEvent = events.find((e) => e.event === "conversation_id");
    if (convEvent && !activeId) {
      setActiveId(convEvent.data);
    }
  }, [events, activeId]);

  // Auto-scroll
  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingText]);

  const handleSend = useCallback(async () => {
    if (!input.trim() || isStreaming) return;
    const text = input;
    setInput("");
    setError("");

    // Optimistic add
    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), conversation_id: activeId ?? "", role: "user", content: text, metadata_: null, created_at: new Date().toISOString() },
    ]);

    try {
      await stream("/api/chat", { message: text, conversation_id: activeId });

      // Reload conversation list and messages
      const [msgs, convos] = await Promise.all([
        activeId ? apiFetch<Message[]>(`/chat/${activeId}/history`) : Promise.resolve([]),
        apiFetch<{ items: Conversation[] }>("/conversations"),
      ]);
      if (activeId) setMessages(msgs);
      setConversations(convos.items);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("common.error"));
    }
  }, [input, isStreaming, activeId, stream, t]);

  return (
    <div className="flex h-[calc(100vh-5rem)] md:h-[calc(100vh-3rem)] gap-4">
      {/* Conversation sidebar */}
      <div className="hidden md:flex w-56 flex-col border-r border-zinc-800 pr-3 space-y-1">
        <button
          onClick={() => setActiveId(null)}
          className="flex items-center gap-2 px-3 py-2 text-sm text-blue-400 hover:bg-zinc-800/50 rounded-lg min-h-[44px]"
        >
          <Plus size={16} /> {t("chat.newConversation")}
        </button>
        {loadingConvos && (
          <div className="flex justify-center py-4" role="status">
            <Loader2 className="animate-spin text-zinc-500" size={16} />
            <span className="sr-only">{t("common.loading")}</span>
          </div>
        )}
        {conversations.map((c) => (
          <button
            key={c.id}
            onClick={() => setActiveId(c.id)}
            className={`text-left px-3 py-2 text-sm rounded-lg truncate min-h-[44px] ${
              activeId === c.id ? "bg-zinc-800 text-zinc-100" : "text-zinc-400 hover:bg-zinc-800/50"
            }`}
          >
            {c.title || "New conversation"}
          </button>
        ))}
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {error && (
          <div className="text-sm text-red-400 bg-red-400/10 p-2 rounded mb-2" role="alert">{error}</div>
        )}
        <div className="flex-1 overflow-auto space-y-3 pb-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] px-4 py-2 rounded-2xl text-sm whitespace-pre-wrap ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-zinc-800 text-zinc-200"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}

          {streamingText && (
            <div className="flex justify-start" aria-live="polite">
              <div className="max-w-[80%] px-4 py-2 rounded-2xl text-sm bg-zinc-800 text-zinc-200 whitespace-pre-wrap">
                {streamingText}
                <span className="animate-pulse">|</span>
              </div>
            </div>
          )}
          <div ref={messagesEnd} />
        </div>

        {/* Input */}
        <div className="flex gap-2 pt-2 border-t border-zinc-800">
          <label className="sr-only" htmlFor="chat-input">{t("chat.placeholder")}</label>
          <input
            id="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            placeholder={t("chat.placeholder")}
            disabled={isStreaming}
            className="flex-1 px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-xl text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-blue-500 min-h-[44px]"
          />
          <button
            onClick={handleSend}
            disabled={isStreaming || !input.trim()}
            aria-label={t("chat.send")}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-700 text-white rounded-xl transition-colors min-h-[44px]"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
