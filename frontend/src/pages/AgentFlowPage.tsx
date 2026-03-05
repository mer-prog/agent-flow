import { useTranslation } from "react-i18next";

const AGENTS = [
  { id: "router", label: "Router", color: "#3b82f6", x: 250, y: 40 },
  { id: "faq", label: "FAQ", color: "#10b981", x: 80, y: 160 },
  { id: "ticket", label: "Ticket", color: "#f59e0b", x: 200, y: 160 },
  { id: "escalation", label: "Escalation", color: "#ef4444", x: 320, y: 160 },
  { id: "chitchat", label: "Chitchat", color: "#8b5cf6", x: 440, y: 160 },
  { id: "formatter", label: "Formatter", color: "#6b7280", x: 250, y: 280 },
];

const EDGES = [
  { from: "router", to: "faq" },
  { from: "router", to: "ticket" },
  { from: "router", to: "escalation" },
  { from: "router", to: "chitchat" },
  { from: "faq", to: "formatter" },
  { from: "ticket", to: "formatter" },
  { from: "escalation", to: "formatter" },
  { from: "chitchat", to: "formatter" },
];

export default function AgentFlowPage() {
  const { t } = useTranslation();

  const getAgent = (id: string) => AGENTS.find((a) => a.id === id)!;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">{t("nav.agentFlow")}</h1>

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 overflow-auto">
        <svg viewBox="0 0 560 360" className="w-full max-w-2xl mx-auto" role="img" aria-labelledby="agent-flow-title agent-flow-desc">
          <title id="agent-flow-title">Agent Flow Diagram</title>
          <desc id="agent-flow-desc">Multi-agent graph: messages flow from Router to FAQ, Ticket, Escalation, or Chitchat agents, then to Formatter</desc>
          {/* START → Router */}
          <line x1="280" y1="10" x2="280" y2="35" stroke="#404040" strokeWidth="2" markerEnd="url(#arrow)" />
          <text x="280" y="8" textAnchor="middle" fill="#71717a" fontSize="10">START</text>

          {/* Edges */}
          {EDGES.map(({ from, to }) => {
            const a = getAgent(from);
            const b = getAgent(to);
            return (
              <line
                key={`${from}-${to}`}
                x1={a.x + 35}
                y1={a.y + 30}
                x2={b.x + 35}
                y2={b.y}
                stroke="#404040"
                strokeWidth="1.5"
                markerEnd="url(#arrow)"
              />
            );
          })}

          {/* Formatter → END */}
          <line x1="285" y1="310" x2="285" y2="340" stroke="#404040" strokeWidth="2" markerEnd="url(#arrow)" />
          <text x="285" y="355" textAnchor="middle" fill="#71717a" fontSize="10">END</text>

          {/* Agent nodes */}
          {AGENTS.map((agent) => (
            <g key={agent.id}>
              <rect
                x={agent.x}
                y={agent.y}
                width="70"
                height="30"
                rx="8"
                fill={agent.color + "20"}
                stroke={agent.color}
                strokeWidth="1.5"
              />
              <text
                x={agent.x + 35}
                y={agent.y + 19}
                textAnchor="middle"
                fill={agent.color}
                fontSize="11"
                fontWeight="600"
              >
                {agent.label}
              </text>
            </g>
          ))}

          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#404040" />
            </marker>
          </defs>
        </svg>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {AGENTS.map((agent) => (
          <div key={agent.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-3">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: agent.color }} />
              <span className="text-sm font-medium text-zinc-200">{agent.label}</span>
            </div>
            <p className="text-xs text-zinc-500 mt-1">
              {agent.id === "router" && "Intent classification"}
              {agent.id === "faq" && "RAG knowledge search"}
              {agent.id === "ticket" && "Ticket creation"}
              {agent.id === "escalation" && "Human-in-the-loop"}
              {agent.id === "chitchat" && "General conversation"}
              {agent.id === "formatter" && "Response formatting"}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
