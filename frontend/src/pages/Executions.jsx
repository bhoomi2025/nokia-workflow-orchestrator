import { useState, useEffect, useCallback } from "react";
import { Activity, RefreshCw, ChevronDown, ChevronRight, Clock, CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { apiFetch } from "../api";

function Badge({ status }) {
  const s = (status || "queued").toLowerCase();
  const styles = {
    success: "bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-500/20",
    failed: "bg-rose-500/10 text-rose-400 ring-1 ring-rose-500/20",
    running: "bg-amber-500/10 text-amber-400 ring-1 ring-amber-500/20",
    queued: "bg-amber-500/10 text-amber-400 ring-1 ring-amber-500/20",
  };
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs uppercase font-medium ${styles[s] || styles.queued}`}>
      {s}
    </span>
  );
}

function fmtTime(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString([], {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", second: "2-digit",
  });
}

function computeDuration(start, end) {
  if (!start || !end) return "—";
  const ms = new Date(end) - new Date(start);
  if (ms < 0) return "—";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

function StatusTimeline({ status }) {
  const s = (status || "queued").toLowerCase();
  const steps = [
    { key: "queued", label: "Queued" },
    { key: "running", label: "Running" },
    { key: "done", label: s === "failed" ? "Failed" : "Success" },
  ];
  const activeIndex = s === "queued" ? 0 : s === "running" ? 1 : 2;

  return (
    <div className="flex items-center gap-2">
      {steps.map((step, idx) => {
        const isPast = idx < activeIndex;
        const isCurrent = idx === activeIndex;
        const isFailedFinal = idx === 2 && s === "failed";
        let dotColor = "bg-zinc-700";
        if (isPast) dotColor = "bg-violet-500";
        if (isCurrent && !isFailedFinal) dotColor = s === "success" ? "bg-emerald-400" : "bg-amber-400";
        if (isCurrent && isFailedFinal) dotColor = "bg-rose-400";

        return (
          <div key={step.key} className="flex items-center gap-2">
            <div className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${dotColor}`} />
              <span className="text-xs text-zinc-400">{step.label}</span>
            </div>
            {idx < steps.length - 1 && <span className="w-6 h-px bg-zinc-700" />}
          </div>
        );
      })}
    </div>
  );
}

function ExecutionRow({ job, expanded, onToggle }) {
  const duration = computeDuration(job.started_at, job.finished_at);

  return (
    <div className="border-t border-zinc-800">
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-4 px-5 py-3 text-left hover:bg-zinc-800/40 transition-colors"
      >
        {expanded ? <ChevronDown size={15} className="text-zinc-500 shrink-0" /> : <ChevronRight size={15} className="text-zinc-500 shrink-0" />}
        <span className="text-zinc-300 text-sm w-16 shrink-0">#{job.id}</span>
        <span className="text-zinc-200 text-sm w-28 shrink-0">WB-{job.workbook_id}</span>
        <span className="text-zinc-400 text-sm w-28 shrink-0">INV-{job.inventory_id}</span>
        <span className="shrink-0"><Badge status={job.status} /></span>
        <span className="text-zinc-500 text-xs w-16 shrink-0 ml-auto flex items-center gap-1">
          <Clock size={11} /> {duration}
        </span>
      </button>

      {expanded && (
        <div className="px-5 pb-4 pl-14 bg-zinc-950/60">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-zinc-600 text-[11px] uppercase tracking-wide">Started</p>
              <p className="text-zinc-300 text-sm mt-0.5">{fmtTime(job.started_at)}</p>
            </div>
            <div>
              <p className="text-zinc-600 text-[11px] uppercase tracking-wide">Finished</p>
              <p className="text-zinc-300 text-sm mt-0.5">{fmtTime(job.finished_at)}</p>
            </div>
          </div>
          <p className="text-zinc-600 text-[11px] uppercase tracking-wide mb-2">Execution stages</p>
          <StatusTimeline status={job.status} />
        </div>
      )}
    </div>
  );
}

function Executions({ token }) {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    const { data } = await apiFetch("/jobs/", token);
    setJobs(Array.isArray(data) ? data : []);
    setLoading(false);
  }, [token]);

  useEffect(() => { load(); }, [load]);

  const sorted = [...jobs].sort((a, b) => b.id - a.id);
  const successCount = jobs.filter((j) => j.status === "success").length;
  const failedCount = jobs.filter((j) => j.status === "failed").length;
  const runningCount = jobs.filter((j) => j.status === "running" || j.status === "queued").length;

  return (
    <div className="p-8 space-y-6 bg-zinc-950 min-h-full">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-zinc-100 text-xl font-bold flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-violet-600/15 border border-violet-500/30 flex items-center justify-center">
              <Activity size={16} className="text-violet-400" />
            </div>
            Executions
          </h1>
          <p className="text-zinc-500 text-sm mt-1 ml-11">Detailed history of every job run</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-emerald-500/10 flex items-center justify-center">
            <CheckCircle2 size={16} className="text-emerald-400" />
          </div>
          <div>
            <p className="text-zinc-100 text-xl font-bold">{loading ? "—" : successCount}</p>
            <p className="text-zinc-500 text-xs">Success</p>
          </div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-rose-500/10 flex items-center justify-center">
            <XCircle size={16} className="text-rose-400" />
          </div>
          <div>
            <p className="text-zinc-100 text-xl font-bold">{loading ? "—" : failedCount}</p>
            <p className="text-zinc-500 text-xs">Failed</p>
          </div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-amber-500/10 flex items-center justify-center">
            <Loader2 size={16} className="text-amber-400" />
          </div>
          <div>
            <p className="text-zinc-100 text-xl font-bold">{loading ? "—" : runningCount}</p>
            <p className="text-zinc-500 text-xs">In progress</p>
          </div>
        </div>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-sm">
        <div className="flex justify-between items-center px-5 py-3.5 border-b border-zinc-800">
          <h2 className="text-zinc-100 font-semibold text-sm">All executions</h2>
          <button onClick={load} className="flex items-center gap-1.5 text-zinc-500 hover:text-violet-400 text-xs transition-colors">
            <RefreshCw size={12} /> refresh
          </button>
        </div>

        <div className="flex items-center gap-4 px-5 py-2 text-zinc-600 text-[11px] uppercase tracking-wide border-b border-zinc-800/60">
          <span className="w-[19px]" />
          <span className="w-16">ID</span>
          <span className="w-28">Workbook</span>
          <span className="w-28">Inventory</span>
          <span>Status</span>
          <span className="ml-auto">Duration</span>
        </div>

        {loading ? (
          <p className="text-center text-zinc-600 py-8 text-sm">Loading…</p>
        ) : sorted.length === 0 ? (
          <p className="text-center text-zinc-600 py-8 text-sm">No executions yet</p>
        ) : (
          sorted.map((j) => (
            <ExecutionRow
              key={j.id}
              job={j}
              expanded={expandedId === j.id}
              onToggle={() => setExpandedId(expandedId === j.id ? null : j.id)}
            />
          ))
        )}
      </div>
    </div>
  );
}

export default Executions;