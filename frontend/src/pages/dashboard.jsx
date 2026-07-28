import { useState, useEffect, useCallback } from "react";
import { BookOpen, Server, Workflow, Briefcase, RefreshCw } from "lucide-react";
import { apiFetch } from "../api";

function StatCard({ icon: Icon, label, value, sub }) {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 hover:border-cyan-500/40 transition">
      <Icon className="text-cyan-400 mb-3" size={22} />
      <p className="text-slate-400 text-xs uppercase tracking-wide">{label}</p>
      <p className="text-white text-3xl font-bold mt-1">{value}</p>
      <p className="text-slate-500 text-xs mt-1">{sub}</p>
    </div>
  );
}

function Badge({ status }) {
  const s = (status || "queued").toLowerCase();
  const styles = {
    success: "bg-emerald-500/10 text-emerald-400",
    failed: "bg-red-500/10 text-red-400",
    running: "bg-yellow-500/10 text-yellow-400",
    queued: "bg-yellow-500/10 text-yellow-400",
  };
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs uppercase font-medium ${styles[s] || styles.queued}`}>
      {s}
    </span>
  );
}

function fmtTime(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function Dashboard({ token, refreshKey }) {
  const [workbooks, setWorkbooks] = useState([]);
  const [inventories, setInventories] = useState([]);
  const [flows, setFlows] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadAll = useCallback(async () => {
    setLoading(true);
    try {
      const [wb, inv, fl, jb] = await Promise.all([
        apiFetch("/workbooks/", token),
        apiFetch("/inventories/", token),
        apiFetch("/flows/", token),
        apiFetch("/jobs/", token),
      ]);
      setWorkbooks(Array.isArray(wb.data) ? wb.data : []);
      setInventories(Array.isArray(inv.data) ? inv.data : []);
      setFlows(Array.isArray(fl.data) ? fl.data : []);
      setJobs(Array.isArray(jb.data) ? jb.data : []);
    } catch (err) {
      console.error("Dashboard load failed:", err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { loadAll(); }, [loadAll, refreshKey]);

  const successCount = jobs.filter((j) => j.status === "success").length;
  const failedCount = jobs.filter((j) => j.status === "failed").length;
  const sortedJobs = [...jobs].sort((a, b) => b.id - a.id);

  return (
    <div className="p-8 space-y-6">
      <div className="grid grid-cols-4 gap-4">
        <StatCard icon={BookOpen} label="Workbooks" value={loading ? "—" : workbooks.length} sub="Reusable execution plans" />
        <StatCard icon={Server} label="Inventories" value={loading ? "—" : inventories.length} sub="Registered device groups" />
        <StatCard icon={Workflow} label="Flows" value={loading ? "—" : flows.length} sub="Chained workbook sequences" />
        <StatCard
          icon={Briefcase}
          label="Jobs run"
          value={loading ? "—" : jobs.length}
          sub={loading ? "—" : `${successCount} success / ${failedCount} failed`}
        />
      </div>

      <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <div className="flex justify-between items-center px-5 py-3 border-b border-slate-700">
          <h2 className="text-white font-semibold text-sm">Recent job history</h2>
          <button onClick={loadAll} className="flex items-center gap-1.5 text-slate-400 hover:text-cyan-400 text-xs">
            <RefreshCw size={12} /> refresh
          </button>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-slate-400 text-xs uppercase text-left">
              <th className="px-5 py-2">ID</th>
              <th className="px-5 py-2">Workbook</th>
              <th className="px-5 py-2">Inventory</th>
              <th className="px-5 py-2">Status</th>
              <th className="px-5 py-2">Started</th>
              <th className="px-5 py-2">Finished</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="6" className="text-center text-slate-500 py-6">Loading…</td></tr>
            ) : sortedJobs.length === 0 ? (
              <tr><td colSpan="6" className="text-center text-slate-500 py-6">No jobs run yet</td></tr>
            ) : (
              sortedJobs.map((j) => (
                <tr key={j.id} className="border-t border-slate-700/60 hover:bg-slate-700/30 text-slate-200">
                  <td className="px-5 py-2.5">#{j.id}</td>
                  <td className="px-5 py-2.5">WB-{j.workbook_id}</td>
                  <td className="px-5 py-2.5">INV-{j.inventory_id}</td>
                  <td className="px-5 py-2.5"><Badge status={j.status} /></td>
                  <td className="px-5 py-2.5">{fmtTime(j.started_at)}</td>
                  <td className="px-5 py-2.5">{fmtTime(j.finished_at)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Dashboard;
