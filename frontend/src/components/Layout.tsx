import { Link, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  LayoutDashboard,
  MessageSquare,
  Ticket,
  AlertTriangle,
  BookOpen,
  GitBranch,
  Settings,
  LogOut,
} from "lucide-react";

interface LayoutProps {
  children: React.ReactNode;
  onLogout: () => void;
}

const navItems = [
  { path: "/", icon: LayoutDashboard, key: "dashboard" },
  { path: "/chat", icon: MessageSquare, key: "chat" },
  { path: "/tickets", icon: Ticket, key: "tickets" },
  { path: "/escalations", icon: AlertTriangle, key: "escalations" },
  { path: "/knowledge", icon: BookOpen, key: "knowledge" },
  { path: "/agent-flow", icon: GitBranch, key: "agentFlow" },
  { path: "/settings", icon: Settings, key: "settings" },
] as const;

export default function Layout({ children, onLogout }: LayoutProps) {
  const { t } = useTranslation();
  const location = useLocation();

  return (
    <div className="flex h-screen bg-zinc-950">
      {/* Sidebar */}
      <nav className="hidden md:flex w-60 flex-col border-r border-zinc-800 bg-zinc-900" aria-label="Main navigation">
        <div className="p-4 border-b border-zinc-800">
          <h1 className="text-lg font-bold text-zinc-100">{t("app.title")}</h1>
          <p className="text-xs text-zinc-500">{t("app.subtitle")}</p>
        </div>

        <div className="flex-1 py-2 space-y-0.5">
          {navItems.map(({ path, icon: Icon, key }) => {
            const active = location.pathname === path;
            return (
              <Link
                key={path}
                to={path}
                className={`flex items-center gap-3 mx-2 px-3 py-2.5 rounded-lg text-sm transition-colors min-h-[44px] ${
                  active
                    ? "bg-zinc-800 text-zinc-100"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
                }`}
              >
                <Icon size={18} />
                {t(`nav.${key}`)}
              </Link>
            );
          })}
        </div>

        <button
          onClick={onLogout}
          className="flex items-center gap-3 mx-2 mb-4 px-3 py-2.5 rounded-lg text-sm text-zinc-400 hover:text-red-400 hover:bg-zinc-800/50 transition-colors min-h-[44px]"
        >
          <LogOut size={18} />
          {t("nav.logout")}
        </button>
      </nav>

      {/* Mobile header */}
      <div className="flex flex-col flex-1 min-w-0">
        <header className="md:hidden flex items-center justify-between p-3 border-b border-zinc-800 bg-zinc-900">
          <h1 className="text-lg font-bold">{t("app.title")}</h1>
          <nav className="flex gap-1" aria-label="Mobile navigation">
            {navItems.slice(0, 4).map(({ path, icon: Icon, key }) => {
              const active = location.pathname === path;
              return (
                <Link
                  key={path}
                  to={path}
                  aria-label={t(`nav.${key}`)}
                  className={`p-2.5 rounded-lg min-w-[44px] min-h-[44px] flex items-center justify-center ${active ? "bg-zinc-800" : "text-zinc-400"}`}
                >
                  <Icon size={18} />
                </Link>
              );
            })}
          </nav>
        </header>

        <main className="flex-1 overflow-auto p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}
