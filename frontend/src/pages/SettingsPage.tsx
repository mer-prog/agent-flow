import { useTranslation } from "react-i18next";

export default function SettingsPage() {
  const { t, i18n } = useTranslation();

  return (
    <div className="space-y-6 max-w-lg">
      <h1 className="text-2xl font-bold">{t("settings.title")}</h1>

      {/* Language */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-3">
        <h3 className="text-sm font-medium text-zinc-300">{t("settings.language")}</h3>
        <div className="flex gap-2">
          {[
            { code: "ja", label: "日本語" },
            { code: "en", label: "English" },
          ].map(({ code, label }) => (
            <button
              key={code}
              onClick={() => i18n.changeLanguage(code)}
              className={`px-4 py-2 text-sm rounded-lg transition-colors ${
                i18n.language === code
                  ? "bg-blue-600 text-white"
                  : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Mode info */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-3">
        <h3 className="text-sm font-medium text-zinc-300">Mode</h3>
        <p className="text-sm text-zinc-400">
          AgentFlow auto-detects mode based on configured API keys.
          In demo mode, keyword-based classifiers and SHA-256 pseudo-embeddings are used.
          In live mode, Claude Haiku 4.5 and OpenAI embeddings are used.
        </p>
      </div>

      {/* API Keys */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-3">
        <h3 className="text-sm font-medium text-zinc-300">{t("settings.apiKeys")}</h3>
        <p className="text-xs text-zinc-500">
          API keys are configured via server environment variables.
          Set ANTHROPIC_API_KEY and OPENAI_API_KEY in .env to enable live mode.
        </p>
      </div>
    </div>
  );
}
