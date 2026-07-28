import { useState, useEffect, useCallback } from "react";
import { Briefcase, Plus, RefreshCw } from "lucide-react";
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
  return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function Jobs({ token, onChanged }) {
  const [jobs, setJobs] = useState([]);
  const [workbooks, setWorkbooks] = useState([]);
  const [inventories, setInventories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  const [workbookId, setWorkbookId] = useState("");
  const [inventoryId, setInventoryId] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    const [jb, wb, inv] = await Promise.all([
      apiFetch("/jobs/", token),
      apiFetch("/workbooks/", token),
      apiFetch("/inventories/", token),
    ]);
    setJobs(Array.isArray(jb.data) ? jb.data : []);
    setWorkbooks(Array.isArray(wb.data) ? wb.data : []);
    setInventories(Array.isArray(inv.data) ? inv.data : []);
    setLoading(false);
  }, [token]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (!workbookId || !inventoryId) {
      setError("Please select both a workbook and an inventory.");
      return;
    }

    setSubmitting(true);

    const { ok, data } = await apiFetch("/jobs/", token, {
      method: "POST",
      body: JSON.stringify({
        workbook_id: Number(workbookId),
        inventory_id: Number(inventoryId),
      }),
    });

    setSubmitting(false);

    if (!ok) {
      setError(data.detail || data.message || "Something went wrong.");
      return;
    }

    setWorkbookId("");
    setInventoryId("");
    setShowForm(false);
    load();
    onChanged?.();
  }

  const sortedJobs = [...jobs].sort((a, b) => b.id - a.id);

  return (
    <div className="p-8 space-y-6 bg-zinc-950 min-h-full">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-zinc-100 text-xl font-bold flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-violet-600/15 border border-violet-500/30 flex items-center justify-center">
              <Briefcase size={16} className="text-violet-400" />
            </div>
            Jobs
          </h1>
          <p className="text-zinc-500 text-sm mt-1 ml-11">Run a workbook against an inventory</p>
        </div>
        <button
          onClick={() => setShowForm((s) => !s)}
          disabled={workbooks.length === 0 || inventories.length === 0}
          className="flex items-center gap-1.5 bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-medium text-sm px-4 py-2 rounded-lg transition-colors shadow-sm hover:shadow-violet-600/20"
        >
          <Plus size={16} />
          {showForm ? "Cancel" : "Submit Job"}
        </button>
      </div>

      {(workbooks.length === 0 || inventories.length === 0) && !loading && (
        <div className="bg-amber-500/10 border border-amber-500/30 text-amber-400 text-sm rounded-lg px-4 py-3">
          You need at least one Workbook and one Inventory before you can submit a job.
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-3 max-w-xl shadow-sm">
          <div>
            <label className="text-xs font-medium text-zinc-400 uppercase tracking-wide">Workbook</label>
            <select
              value={workbookId}
              onChange={(e) => setWorkbookId(e.target.value)}
              className="mt-1.5 w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500/40 transition-colors"
            >
              <option value="">Select a workbook…</option>
              {workbooks.map((w) => (
                <option key={w.id} value={w.id}>
                  #{w.id} — {w.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs font-medium text-zinc-400 uppercase tracking-wide">Inventory</label>
            <select
              value={inventoryId}
              onChange={(e) => setInventoryId(e.target.value)}
              className="mt-1.5 w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500/40 transition-colors"
            >
              <option value="">Select an inventory…</option>
              {inventories.map((i) => (
                <option key={i.id} value={i.id}>
                  #{i.id} — {i.name}
                </option>
              ))}
            </select>
          </div>

          {error && <div className="text-rose-400 text-xs">{error}</div>}

          <button
            type="submit"
            disabled={submitting}
            className="bg-violet-600 hover:bg-violet-500 disabled:opacity-60 text-white font-medium px-4 py-2 rounded-lg text-sm transition-colors"
          >
            {submitting ? "Running… (takes a couple seconds)" : "Run Job"}
          </button>
        </form>
      )}

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-sm">
        <div className="flex justify-between items-center px-5 py-3.5 border-b border-zinc-800">
          <h2 className="text-zinc-100 font-semibold text-sm">Job history</h2>
          <button onClick={load} className="flex items-center gap-1.5 text-zinc-500 hover:text-violet-400 text-xs transition-colors">
            <RefreshCw size={12} />
            refresh
          </button>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-zinc-500 text-xs uppercase text-left">
              <th className="px-5 py-2.5">ID</th>
              <th className="px-5 py-2.5">Workbook</th>
              <th className="px-5 py-2.5">Inventory</th>
              <th className="px-5 py-2.5">Status</th>
              <th className="px-5 py-2.5">Started</th>
              <th className="px-5 py-2.5">Finished</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="6" className="text-center text-zinc-600 py-8">
                  Loading…
                </td>
              </tr>
            ) : sortedJobs.length === 0 ? (
              <tr>
                <td colSpan="6" className="text-center text-zinc-600 py-8">
                  No jobs run yet
                </td>
              </tr>
            ) : (
              sortedJobs.map((j) => (
                <tr key={j.id} className="border-t border-zinc-800 hover:bg-zinc-800/40 text-zinc-200 transition-colors">
                  <td className="px-5 py-3">#{j.id}</td>
                  <td className="px-5 py-3">WB-{j.workbook_id}</td>
                  <td className="px-5 py-3">INV-{j.inventory_id}</td>
                  <td className="px-5 py-3">
                    <Badge status={j.status} />
                  </td>
                  <td className="px-5 py-3">{fmtTime(j.started_at)}</td>
                  <td className="px-5 py-3">{fmtTime(j.finished_at)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Jobs;
