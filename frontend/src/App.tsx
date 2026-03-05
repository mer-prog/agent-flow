import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./hooks/useAuth";
import Layout from "./components/Layout";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import ChatPage from "./pages/ChatPage";
import TicketsPage from "./pages/TicketsPage";
import EscalationsPage from "./pages/EscalationsPage";
import KnowledgePage from "./pages/KnowledgePage";
import AgentFlowPage from "./pages/AgentFlowPage";
import SettingsPage from "./pages/SettingsPage";

export default function App() {
  const { user, loading, login, register, logout } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-zinc-950 text-zinc-400">
        Loading...
      </div>
    );
  }

  if (!user) {
    return <LoginPage onLogin={login} onRegister={register} />;
  }

  return (
    <Layout onLogout={logout}>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/tickets" element={<TicketsPage />} />
        <Route path="/escalations" element={<EscalationsPage />} />
        <Route path="/knowledge" element={<KnowledgePage />} />
        <Route path="/agent-flow" element={<AgentFlowPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
