import { useState, useEffect, useCallback } from "react";
import { BookOpen, Plus, RefreshCw, Pencil, Trash2, X } from "lucide-react";
import { apiFetch } from "../api";

function Workbooks({ token, onChanged }) {
  const [workbooks, setWorkbooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [content, setContent] = useState('{"workflows": []}');
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    const { data } = await apiFetch("/workbooks/", token);
    setWorkbooks(Array.isArray(data) ? data : []);
    setLoading(false);
  }, [token]);

  useEffect(() => { load(); }, [load]);

  function resetForm() {
    setName("");
    setDescription("");
    setContent('{"workflows": []}');
    setEditingId(null);
    setShowForm(false);
    setError("");
  }

  function startEdit(w) {
    setEditingId(w.id);
    setName(w.name);
    setDescription(w.description || "");
    setContent(w.content || '{"workflows": []}');
    setShowForm(true);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    const path = editingId ? `/workbooks/${editingId}` : "/workbooks/";
    const method = editingId ? "PUT" : "POST";

    const { ok, data } = await apiFetch(path, token, {
      method,
      body: JSON.stringify({ name, description, content }),
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
    if (!confirm(`Delete workbook #${id}? This cannot be undone.`)) return;

    const { ok, data } = await apiFetch(`/workbooks/${id}`, token, { method: "DELETE" });

    if (!ok) {
      alert(data.detail || data.message || "Could not delete workbook.");
      return;
    }

    load();
    onChanged?.();
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-white text-xl font-bold flex items-center gap-2">
            <BookOpen size={22} className="text-cyan-400" />
            Workbooks
          </h1>
          <p className="text-slate-400 text-sm">Reusable instruction plans</p>
        </div>
        <button
          onClick={() => (showForm ? resetForm() : setShowForm(true))}
          className="flex items-center gap-1.5 bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-semibold text-sm px-4 py-2 rounded-lg transition"
        >
          <Plus size={16} />
          {showForm ? "Cancel" : "New Workbook"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-slate-800 border border-slate-700 rounded-xl p-6 space-y-3 max-w-xl">
          <div className="flex justify-between items-center">
            <h3 className="text-white text-sm font-semibold">
              {editingId ? `Editing Workbook #${editingId}` : "New Workbook"}
            </h3>
            {editingId && (
              <button type="button" onClick={resetForm} className="text-slate-400 hover:text-white">
                <X size={16} />
              </button>
            )}
          </div>

          <div>
            <label className="text-xs text-slate-400 uppercase tracking-wide">Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Router Config Check"
              required
              className="mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-400"
            />
          </div>
          <div>
            <label className="text-xs text-slate-400 uppercase tracking-wide">Description</label>
            <input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What does this workbook do?"
              className="mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-400"
            />
          </div>
          <div>
            <label className="text-xs text-slate-400 uppercase tracking-wide">Content (JSON)</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={5}
              className="mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-cyan-400"
            />
          </div>
          {error && <div className="text-red-400 text-xs">{error}</div>}
          <button
            type="submit"
            disabled={submitting}
            className="bg-cyan-500 hover:bg-cyan-400 disabled:opacity-60 text-slate-900 font-semibold px-4 py-2 rounded-lg text-sm transition"
          >
            {submitting ? "Saving…" : editingId ? "Save Changes" : "Create Workbook"}
          </button>
        </form>
      )}

      <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <div className="flex justify-between items-center px-5 py-3 border-b border-slate-700">
          <h2 className="text-white font-semibold text-sm">All workbooks</h2>
          <button onClick={load} className="flex items-center gap-1.5 text-slate-400 hover:text-cyan-400 text-xs">
            <RefreshCw size={12} />
            refresh
          </button>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-slate-400 text-xs uppercase text-left">
              <th className="px-5 py-2">ID</th>
              <th className="px-5 py-2">Name</th>
              <th className="px-5 py-2">Description</th>
              <th className="px-5 py-2 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="4" className="text-center text-slate-500 py-6">Loading…</td></tr>
            ) : workbooks.length === 0 ? (
              <tr><td colSpan="4" className="text-center text-slate-500 py-6">No workbooks yet</td></tr>
            ) : (
              workbooks.map((w) => (
                <tr key={w.id} className="border-t border-slate-700/60 hover:bg-slate-700/30 text-slate-200">
                  <td className="px-5 py-2.5">#{w.id}</td>
                  <td className="px-5 py-2.5">{w.name}</td>
                  <td className="px-5 py-2.5 text-slate-400">{w.description || "—"}</td>
                  <td className="px-5 py-2.5 text-right">
                    <div className="flex justify-end gap-3">
                      <button onClick={() => startEdit(w)} className="text-slate-400 hover:text-cyan-400" title="Edit">
                        <Pencil size={15} />
                      </button>
                      <button onClick={() => handleDelete(w.id)} className="text-slate-400 hover:text-red-400" title="Delete">
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

export default Workbooks;