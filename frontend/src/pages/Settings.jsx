import { useState } from "react";
import {
  Settings as SettingsIcon,
  User,
  LogOut,
  Moon,
  RefreshCw,
  Layers,
  Code2,
  Server,
  Database,
  ShieldCheck,
} from "lucide-react";

const techStack = [
  { label: "React", icon: Code2 },
  { label: "Vite", icon: Layers },
  { label: "Tailwind CSS", icon: Layers },
  { label: "React Flow", icon: Layers },
  { label: "FastAPI", icon: Server },
  { label: "PostgreSQL", icon: Database },
  { label: "JWT Auth", icon: ShieldCheck },
];

function Toggle({ checked, onChange }) {
  return (
    <button
      onClick={onChange}
      className={`w-10 h-5.5 rounded-full transition-colors relative shrink-0 ${checked ? "bg-violet-600" : "bg-zinc-700"}`}
      style={{ height: 22, width: 40 }}
    >
      <span
        className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${checked ? "translate-x-[19px]" : "translate-x-0.5"}`}
      />
    </button>
  );
}

function Section({ icon: Icon, title, description, children }) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 shadow-sm">
      <div className="flex items-start gap-3 mb-5">
        <div className="w-9 h-9 rounded-lg bg-violet-600/15 border border-violet-500/30 flex items-center justify-center shrink-0">
          <Icon size={16} className="text-violet-400" />
        </div>
        <div>
          <h2 className="text-zinc-100 font-semibold text-sm">{title}</h2>
          {description && <p className="text-zinc-500 text-xs mt-0.5">{description}</p>}
        </div>
      </div>
      {children}
    </div>
  );
}

// Preferences below are visual only — there's no backend endpoint yet to persist them.
// Kept as local UI state so the toggles are interactive without pretending to save anything.
function Settings({ onLogout }) {
  const [darkMode, setDarkMode] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30);

  return (
    <div className="p-8 space-y-6 bg-zinc-950 min-h-full max-w-3xl">
      <div>
        <h1 className="text-zinc-100 text-xl font-bold flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-violet-600/15 border border-violet-500/30 flex items-center justify-center">
            <SettingsIcon size={16} className="text-violet-400" />
          </div>
          Settings
        </h1>
        <p className="text-zinc-500 text-sm mt-1 ml-11">Manage your account and workspace preferences</p>
      </div>

      {/* Account */}
      <Section icon={User} title="Account" description="Your session on this Workflow Orchestrator instance">
        <div className="flex items-center justify-between py-2">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-violet-600/20 border border-violet-500/30 flex items-center justify-center">
              <User size={16} className="text-violet-400" />
            </div>
            <div>
              <p className="text-zinc-200 text-sm font-medium">Signed in</p>
              <p className="text-zinc-500 text-xs">Session active on this device</p>
            </div>
          </div>
          <button
            onClick={onLogout}
            className="flex items-center gap-1.5 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-200 text-sm px-4 py-2 rounded-lg transition-colors"
          >
            <LogOut size={14} /> Sign out
          </button>
        </div>
      </Section>

      {/* Preferences */}
      <Section icon={Moon} title="Appearance & Preferences" description="Visual only for now — not yet wired to a backend setting">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-zinc-200 text-sm">Dark mode</p>
              <p className="text-zinc-500 text-xs">This app is dark-themed by design</p>
            </div>
            <Toggle checked={darkMode} onChange={() => setDarkMode((d) => !d)} />
          </div>

          <div className="h-px bg-zinc-800" />

          <div className="flex items-center justify-between">
            <div>
              <p className="text-zinc-200 text-sm">Auto-refresh dashboard</p>
              <p className="text-zinc-500 text-xs">Periodically reload job & flow data</p>
            </div>
            <Toggle checked={autoRefresh} onChange={() => setAutoRefresh((a) => !a)} />
          </div>

          <div className="h-px bg-zinc-800" />

          <div className="flex items-center justify-between">
            <div>
              <p className="text-zinc-200 text-sm">Refresh interval</p>
              <p className="text-zinc-500 text-xs">How often to auto-refresh (seconds)</p>
            </div>
            <div className="flex items-center gap-2">
              <RefreshCw size={13} className="text-zinc-500" />
              <input
                type="number"
                min={5}
                max={300}
                value={refreshInterval}
                onChange={(e) => setRefreshInterval(e.target.value)}
                disabled={!autoRefresh}
                className="w-16 bg-zinc-950 border border-zinc-700 rounded-lg px-2 py-1 text-sm text-zinc-100 text-center disabled:opacity-40 focus:outline-none focus:border-violet-500"
              />
            </div>
          </div>
        </div>
      </Section>

      {/* About */}
      <Section icon={Layers} title="About this build" description="Nokia Workflow Orchestrator — internship project">
        <div className="flex flex-wrap gap-2">
          {techStack.map(({ label, icon: Icon }) => (
            <span
              key={label}
              className="flex items-center gap-1.5 bg-zinc-800/60 border border-zinc-700 text-zinc-300 text-xs px-3 py-1.5 rounded-lg"
            >
              <Icon size={12} className="text-violet-400" />
              {label}
            </span>
          ))}
        </div>
      </Section>
    </div>
  );
}

export default Settings;