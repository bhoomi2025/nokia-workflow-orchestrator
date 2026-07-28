import { useState } from "react";
import {
  LayoutDashboard,
  Server,
  BookOpen,
  Briefcase,
  Workflow,
  Activity,
  Settings as SettingsIcon,
  ChevronsLeft,
  ChevronsRight,
} from "lucide-react";

const navGroups = [
  {
    label: "Overview",
    items: [{ key: "dashboard", label: "Dashboard", icon: LayoutDashboard }],
  },
  {
    label: "Automation",
    items: [
      { key: "flows", label: "Flows", icon: Workflow },
      { key: "workbooks", label: "Workbooks", icon: BookOpen },
    ],
  },
  {
    label: "Operations",
    items: [
      { key: "inventory", label: "Inventory", icon: Server },
      { key: "jobs", label: "Jobs", icon: Briefcase },
      { key: "executions", label: "Executions", icon: Activity },
    ],
  },
  {
    label: "Workspace",
    items: [{ key: "settings", label: "Settings", icon: SettingsIcon }],
  },
];

function Sidebar({ active, onNavigate }) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`shrink-0 bg-zinc-950 border-r border-zinc-800 flex flex-col transition-all duration-200 ${
        collapsed ? "w-[68px]" : "w-64"
      }`}
    >
      <div className="h-16 flex items-center justify-between px-4 border-b border-zinc-800">
        {!collapsed && (
          <div className="flex items-center gap-2 overflow-hidden">
            <span className="bg-violet-600/15 border border-violet-500/30 text-violet-400 text-[11px] font-bold tracking-wide px-2 py-1 rounded-md shrink-0">
              IA::WFO
            </span>
            <span className="text-zinc-300 text-sm font-medium whitespace-nowrap">Orchestrator</span>
          </div>
        )}
        <button
          onClick={() => setCollapsed((c) => !c)}
          className="text-zinc-500 hover:text-zinc-200 p-1.5 rounded-md hover:bg-zinc-800/60 transition-colors"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronsRight size={16} /> : <ChevronsLeft size={16} />}
        </button>
      </div>

      <nav className="flex-1 py-4 px-3 space-y-6 overflow-y-auto">
        {navGroups.map((group) => (
          <div key={group.label}>
            {!collapsed && (
              <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-600 px-3 mb-2">
                {group.label}
              </p>
            )}
            <div className="space-y-1">
              {group.items.map(({ key, label, icon: Icon }) => {
                const isActive = active === key;
                return (
                  <button
                    key={key}
                    onClick={() => onNavigate(key)}
                    title={collapsed ? label : undefined}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150 relative
                      ${isActive ? "bg-violet-600/10 text-violet-400" : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/60"}
                      ${collapsed ? "justify-center" : ""}`}
                  >
                    {isActive && (
                      <span className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-violet-500 rounded-r-full" />
                    )}
                    <Icon size={18} className="shrink-0" />
                    {!collapsed && <span className="truncate">{label}</span>}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      <div className="px-4 py-4 border-t border-zinc-800">
        {!collapsed ? (
          <p className="text-zinc-600 text-[11px]">Nokia Internship Build · v1.0</p>
        ) : (
          <p className="text-zinc-700 text-[10px] text-center">v1.0</p>
        )}
      </div>
    </aside>
  );
}

export default Sidebar;