import { useState, useEffect, useCallback } from "react";
import { Server, Plus, RefreshCw, Pencil, Trash2, X } from "lucide-react";
import { apiFetch } from "../api";

function Inventory({ token, onChanged }) {
  const [inventories, setInventories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [hosts, setHosts] = useState('{"router1": {"ip": "192.168.1.1", "port": 22}}');
  const [groups, setGroups] = useState('{"routers": ["router1"]}');
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    const { data } = await apiFetch("/inventories/", token);
    setInventories(Array.isArray(data) ? data : []);
    setLoading(false);
  }, [token]);

  useEffect(() => { load(); }, [load]);

  function resetForm() {
    setName("");
    setDescription("");
    setHosts('{"router1": {"ip": "192.168.1.1", "port": 22}}');
    setGroups('{"routers": ["router1"]}');
    setEditingId(null);
    setShowForm(false);
    setError("");
  }

  function startEdit(i) {
    setEditingId(i.id);
    setName(i.name);
    setDescription(i.description || "");
    setHosts(i.hosts || "{}");
    setGroups(i.groups || "{}");
    setShowForm(true);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    const path = editingId ? `/inventories/${editingId}` : "/inventories/";
    const method = editingId ? "PUT" : "POST";

    const { ok, data } = await apiFetch(path, token, {
      method,
      body: JSON.stringify({ name, description, hosts, groups }),
    });

    setSubmitting(false);

    if (!ok) {
      setError(data.detail || data.message || "Something went wrong.");
      return;
    }

    resetForm();
    load();
    onChanged?.();
  }

  async function handleDelete(id) {
    if (!confirm(`Delete inventory #${id}? This cannot be undone.`)) return;

    const { ok, data } = await apiFetch(`/inventories/${id}`, token, { method: "DELETE" });

    if (!ok) {
      alert(data.detail || data.message || "Could not delete inventory.");
      return;
    }

    load();
    onChanged?.();
  }

  return (
    <div className="p-8 space-y-6 bg-zinc-950 min-h-full">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-zinc-100 text-xl font-bold flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-violet-600/15 border border-violet-500/30 flex items-center justify-center">
              <Server size={16} className="text-violet-400" />
            </div>
            Inventories
          </h1>
          <p className="text-zinc-500 text-sm mt-1 ml-11">Device groups that workbooks can run against</p>
        </div>
        <button
          onClick={() => (showForm ? resetForm() : setShowForm(true))}
          className="flex items-center gap-1.5 bg-violet-600 hover:bg-violet-500 text-white font-medium text-sm px-4 py-2 rounded-lg transition-colors shadow-sm hover:shadow-violet-600/20"
        >
          <Plus size={16} />
          {showForm ? "Cancel" : "New Inventory"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-3 max-w-xl shadow-sm">
          <div className="flex justify-between items-center">
            <h3 className="text-zinc-100 text-sm font-semibold">
              {editingId ? `Editing Inventory #${editingId}` : "New Inventory"}
            </h3>
            {editingId && (
              <button type="button" onClick={resetForm} className="text-zinc-500 hover:text-zinc-200 transition-colors">
                <X size={16} />
              </button>
            )}
          </div>

          <div>
            <label className="text-xs font-medium text-zinc-400 uppercase tracking-wide">Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Delhi Lab Routers"
              required
              className="mt-1.5 w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500/40 transition-colors"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-zinc-400 uppercase tracking-wide">Description</label>
            <input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What devices does this cover?"
              className="mt-1.5 w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500/40 transition-colors"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-zinc-400 uppercase tracking-wide">Hosts (JSON)</label>
            <textarea
              value={hosts}
              onChange={(e) => setHosts(e.target.value)}
              rows={3}
              className="mt-1.5 w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-xs text-zinc-100 font-mono focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500/40 transition-colors"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-zinc-400 uppercase tracking-wide">Groups (JSON)</label>
            <textarea
              value={groups}
              onChange={(e) => setGroups(e.target.value)}
              rows={2}
              className="mt-1.5 w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-xs text-zinc-100 font-mono focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500/40 transition-colors"
            />
          </div>
          {error && <div className="text-rose-400 text-xs">{error}</div>}
          <button
            type="submit"
            disabled={submitting}
            className="bg-violet-600 hover:bg-violet-500 disabled:opacity-60 text-white font-medium px-4 py-2 rounded-lg text-sm transition-colors"
          >
            {submitting ? "Saving…" : editingId ? "Save Changes" : "Create Inventory"}
          </button>
        </form>
      )}

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-sm">
        <div className="flex justify-between items-center px-5 py-3.5 border-b border-zinc-800">
          <h2 className="text-zinc-100 font-semibold text-sm">All inventories</h2>
          <button onClick={load} className="flex items-center gap-1.5 text-zinc-500 hover:text-violet-400 text-xs transition-colors">
            <RefreshCw size={12} />
            refresh
          </button>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-zinc-500 text-xs uppercase text-left">
              <th className="px-5 py-2.5">ID</th>
              <th className="px-5 py-2.5">Name</th>
              <th className="px-5 py-2.5">Description</th>
              <th className="px-5 py-2.5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="4" className="text-center text-zinc-600 py-8">Loading…</td></tr>
            ) : inventories.length === 0 ? (
              <tr><td colSpan="4" className="text-center text-zinc-600 py-8">No inventories yet</td></tr>
            ) : (
              inventories.map((i) => (
                <tr key={i.id} className="border-t border-zinc-800 hover:bg-zinc-800/40 text-zinc-200 transition-colors">
                  <td className="px-5 py-3">#{i.id}</td>
                  <td className="px-5 py-3 font-medium">{i.name}</td>
                  <td className="px-5 py-3 text-zinc-500">{i.description || "—"}</td>
                  <td className="px-5 py-3 text-right">
                    <div className="flex justify-end gap-3">
                      <button onClick={() => startEdit(i)} className="text-zinc-500 hover:text-violet-400 transition-colors" title="Edit">
                        <Pencil size={15} />
                      </button>
                      <button onClick={() => handleDelete(i.id)} className="text-zinc-500 hover:text-rose-400 transition-colors" title="Delete">
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Inventory;