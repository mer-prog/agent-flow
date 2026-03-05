import { FormEvent, useState } from "react";
import { useTranslation } from "react-i18next";

interface Props {
  onLogin: (email: string, password: string) => Promise<void>;
  onRegister: (email: string, password: string, fullName: string) => Promise<void>;
}

export default function LoginPage({ onLogin, onRegister }: Props) {
  const { t } = useTranslation();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (isRegister) {
        await onRegister(email, password, fullName);
      } else {
        await onLogin(email, password);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-zinc-100">{t("app.title")}</h1>
          <p className="text-zinc-500 mt-1">{t("app.subtitle")}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 bg-zinc-900 p-6 rounded-xl border border-zinc-800">
          <h2 className="text-lg font-semibold text-zinc-100">
            {isRegister ? t("auth.register") : t("auth.login")}
          </h2>

          {error && (
            <div className="text-sm text-red-400 bg-red-400/10 p-2 rounded" role="alert">{error}</div>
          )}

          {isRegister && (
            <div>
              <label htmlFor="fullName" className="block text-xs text-zinc-400 mb-1">{t("auth.fullName")}</label>
              <input
                id="fullName"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                className="w-full px-3 py-2.5 bg-zinc-800 border border-zinc-700 rounded-lg text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-blue-500 min-h-[44px]"
              />
            </div>
          )}

          <div>
            <label htmlFor="email" className="block text-xs text-zinc-400 mb-1">{t("auth.email")}</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-3 py-2.5 bg-zinc-800 border border-zinc-700 rounded-lg text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-blue-500 min-h-[44px]"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-xs text-zinc-400 mb-1">{t("auth.password")}</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-3 py-2.5 bg-zinc-800 border border-zinc-700 rounded-lg text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-blue-500 min-h-[44px]"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-700 text-white rounded-lg font-medium transition-colors min-h-[44px]"
          >
            {loading ? t("common.loading") : isRegister ? t("auth.registerButton") : t("auth.loginButton")}
          </button>

          <button
            type="button"
            onClick={() => setIsRegister(!isRegister)}
            className="w-full text-sm text-zinc-400 hover:text-zinc-200 py-2"
          >
            {isRegister ? t("auth.hasAccount") : t("auth.noAccount")}
          </button>
        </form>
      </div>
    </div>
  );
}
