import { useState, useEffect, useCallback, useRef } from "react";
import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
} from "reactflow";
import "reactflow/dist/style.css";
import { Workflow, Plus, Play, Save, X, BookOpen } from "lucide-react";
import { apiFetch } from "../api";

function WorkbookNode({ data }) {
  return (
    <div className="px-4 py-3 rounded-xl bg-slate-800 border-2 border-cyan-500/50 shadow-lg shadow-cyan-500/10 min-w-[160px]">
      <Handle type="target" position={Position.Left} className="!bg-cyan-400 !w-3 !h-3" />
      <div className="flex items-center gap-2">
        <BookOpen size={14} className="text-cyan-400 shrink-0" />
        <span className="text-white text-sm font-medium truncate">{data.label}</span>
      </div>
      <p className="text-slate-500 text-[10px] mt-0.5">Workbook #{data.workbookId}</p>
      <Handle type="source" position={Position.Right} className="!bg-cyan-400 !w-3 !h-3" />
    </div>
  );
}

const nodeTypes = { workbook: WorkbookNode };

function FlowBuilder({ token }) {
  const [flows, setFlows] = useState([]);
  const [workbooks, setWorkbooks] = useState([]);
  const [inventories, setInventories] = useState([]);
  const [activeFlowId, setActiveFlowId] = useState(null);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const [showNewFlow, setShowNewFlow] = useState(false);
  const [newFlowName, setNewFlowName] = useState("");
  const [newFlowDesc, setNewFlowDesc] = useState("");

  const [runInventoryId, setRunInventoryId] = useState("");
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState(null);
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState("");

  const wrapperRef = useRef(null);
  const rfInstance = useRef(null);
  const idCounter = useRef(0);

  const loadAll = useCallback(async () => {
    const [fl, wb, inv] = await Promise.all([
      apiFetch("/flows/", token),
      apiFetch("/workbooks/", token),
      apiFetch("/inventories/", token),
    ]);
    const flowList = Array.isArray(fl.data) ? fl.data : [];
    setFlows(flowList);
    setWorkbooks(Array.isArray(wb.data) ? wb.data : []);
    setInventories(Array.isArray(inv.data) ? inv.data : []);
  }, [token]);

  useEffect(() => { loadAll(); }, [loadAll]);

  useEffect(() => {
    async function loadSteps() {
      if (!activeFlowId) {
        setNodes([]);
        setEdges([]);
        return;
      }
      const { data } = await apiFetch(`/flows/${activeFlowId}`, token);
      const steps = (data?.steps || []).slice().sort((a, b) => a.position - b.position);

      const newNodes = steps.map((s, idx) => ({
        id: `n${s.id ?? idx}`,
        type: "workbook",
        position: { x: 80 + idx * 220, y: 160 },
        data: {
          label: workbooks.find((w) => w.id === s.workbook_id)?.name || `Workbook ${s.workbook_id}`,
          workbookId: s.workbook_id,
        },
      }));

      const newEdges = [];
      for (let i = 0; i < newNodes.length - 1; i++) {
        newEdges.push({
          id: `e${i}`,
          source: newNodes[i].id,
          target: newNodes[i + 1].id,
          animated: true,
          style: { stroke: "#22d3ee", strokeWidth: 2 },
        });
      }

      setNodes(newNodes);
      setEdges(newEdges);
    }
    loadSteps();
  }, [activeFlowId, workbooks, token, setNodes, setEdges]);

  const onConnect = useCallback(
    (params) =>
      setEdges((eds) =>
        addEdge({ ...params, animated: true, style: { stroke: "#22d3ee", strokeWidth: 2 } }, eds)
      ),
    [setEdges]
  );

  const onDragOver = useCallback((e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    const raw = e.dataTransfer.getData("application/workbook");
    if (!raw || !rfInstance.current || !wrapperRef.current) return;
    const wb = JSON.parse(raw);

    const bounds = wrapperRef.current.getBoundingClientRect();
    const position = rfInstance.current.project({
      x: e.clientX - bounds.left,
      y: e.clientY - bounds.top,
    });

    idCounter.current += 1;
    const newNode = {
      id: `drop-${Date.now()}-${idCounter.current}`,
      type: "workbook",
      position,
      data: { label: wb.name, workbookId: wb.id },
    };
    setNodes((nds) => nds.concat(newNode));
  }, [setNodes]);

  async function handleCreateFlow(e) {
    e.preventDefault();
    const { ok, data } = await apiFetch("/flows/", token, {
      method: "POST",
      body: JSON.stringify({ name: newFlowName, description: newFlowDesc }),
    });
    if (!ok) {
      alert(data.detail || data.message || "Could not create flow");
      return;
    }
    setNewFlowName("");
    setNewFlowDesc("");
    setShowNewFlow(false);
    await loadAll();
    setActiveFlowId(data.data.id);
  }

  function computeOrderedSteps() {
    if (nodes.length === 0) return [];
    const incoming = new Set(edges.map((e) => e.target));
    const startNode = nodes.find((n) => !incoming.has(n.id)) || nodes[0];

    const order = [];
    const visited = new Set();
    let current = startNode;

    while (current && !visited.has(current.id)) {
      order.push(current);
      visited.add(current.id);
      const nextEdge = edges.find((e) => e.source === current.id);
      current = nextEdge ? nodes.find((n) => n.id === nextEdge.target) : null;
    }

    nodes.forEach((n) => {
      if (!visited.has(n.id)) order.push(n);
    });

    return order.map((n, idx) => ({
      position: idx + 1,
      workbook_id: n.data.workbookId,
    }));
  }

  async function handleSaveSteps() {
    if (!activeFlowId) return;
    setSaving(true);
    setSaveMsg("");

    const steps = computeOrderedSteps();
    const { ok, data } = await apiFetch(`/flows/${activeFlowId}/steps`, token, {
      method: "PUT",
      body: JSON.stringify({ steps }),
    });

    setSaving(false);
    setSaveMsg(ok ? "Saved ✓" : data.detail || data.message || "Save failed");
    setTimeout(() => setSaveMsg(""), 2500);
  }

  async function handleRun() {
    if (!activeFlowId || !runInventoryId) {
      alert("Select an inventory first.");
      return;
    }
    setRunning(true);
    setRunResult(null);
    const { ok, data } = await apiFetch(`/flows/${activeFlowId}/run`, token, {
      method: "POST",
      body: JSON.stringify({ inventory_id: Number(runInventoryId) }),
    });
    setRunning(false);
    if (ok) {
      setRunResult(data);
    } else {
      alert(data.detail || data.message || "Run failed");
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <div className="flex items-center justify-between px-5 py-3 border-b border-slate-700 bg-slate-900">
        <div className="flex items-center gap-3">
          <Workflow size={18} className="text-cyan-400" />
          <select
            value={activeFlowId || ""}
            onChange={(e) => setActiveFlowId(Number(e.target.value) || null)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-white"
          >
            <option value="">Select a flow…</option>
            {flows.map((f) => (
              <option key={f.id} value={f.id}>#{f.id} — {f.name}</option>
            ))}
          </select>
          <button
            onClick={() => setShowNewFlow(true)}
            className="flex items-center gap-1 text-cyan-400 hover:text-cyan-300 text-xs border border-cyan-500/30 rounded-lg px-3 py-1.5"
          >
            <Plus size={14} /> New Flow
          </button>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleSaveSteps}
            disabled={!activeFlowId || saving}
            className="flex items-center gap-1.5 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-white text-sm px-3 py-1.5 rounded-lg transition"
          >
            <Save size={14} /> {saving ? "Saving…" : "Save Flow"}
          </button>
          {saveMsg && <span className="text-emerald-400 text-xs">{saveMsg}</span>}

          <select
            value={runInventoryId}
            onChange={(e) => setRunInventoryId(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white"
          >
            <option value="">Inventory…</option>
            {inventories.map((i) => (
              <option key={i.id} value={i.id}>#{i.id} — {i.name}</option>
            ))}
          </select>
          <button
            onClick={handleRun}
            disabled={!activeFlowId || running}
            className="flex items-center gap-1.5 bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-slate-900 font-semibold text-sm px-4 py-1.5 rounded-lg transition"
          >
            <Play size={14} /> {running ? "Running…" : "Run"}
          </button>
        </div>
      </div>

      {showNewFlow && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <form onSubmit={handleCreateFlow} className="bg-slate-800 border border-slate-700 rounded-xl p-6 w-96 space-y-3">
            <div className="flex justify-between items-center">
              <h3 className="text-white font-semibold text-sm">New Flow</h3>
              <button type="button" onClick={() => setShowNewFlow(false)} className="text-slate-400 hover:text-white">
                <X size={16} />
              </button>
            </div>
            <input
              value={newFlowName}
              onChange={(e) => setNewFlowName(e.target.value)}
              placeholder="Flow name"
              required
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-400"
            />
            <input
              value={newFlowDesc}
              onChange={(e) => setNewFlowDesc(e.target.value)}
              placeholder="Description"
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-400"
            />
            <button type="submit" className="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-semibold py-2 rounded-lg text-sm">
              Create
            </button>
          </form>
        </div>
      )}

      <div className="flex flex-1 overflow-hidden">
        <aside className="w-56 bg-slate-900 border-r border-slate-700 p-4 overflow-y-auto">
          <p className="text-slate-400 text-xs uppercase tracking-wide mb-3">Drag a workbook onto the canvas</p>
          <div className="space-y-2">
            {workbooks.map((w) => (
              <div
                key={w.id}
                draggable
                onDragStart={(e) => {
                  e.dataTransfer.setData("application/workbook", JSON.stringify(w));
                  e.dataTransfer.effectAllowed = "move";
                }}
                className="flex items-center gap-2 bg-slate-800 border border-slate-700 hover:border-cyan-500/50 rounded-lg px-3 py-2 cursor-grab active:cursor-grabbing"
              >
                <BookOpen size={14} className="text-cyan-400 shrink-0" />
                <span className="text-white text-xs truncate">{w.name}</span>
              </div>
            ))}
            {workbooks.length === 0 && (
              <p className="text-slate-600 text-xs">No workbooks yet — create one first.</p>
            )}
          </div>
        </aside>

        <div className="flex-1" ref={wrapperRef} onDrop={onDrop} onDragOver={onDragOver}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onInit={(instance) => { rfInstance.current = instance; }}
            nodeTypes={nodeTypes}
            fitView
            className="bg-slate-950"
          >
            <Background color="#1e293b" gap={18} />
            <Controls className="!bg-slate-800 !border-slate-700" />
            <MiniMap className="!bg-slate-900" nodeColor="#22d3ee" maskColor="rgba(15,23,42,0.7)" />
          </ReactFlow>
        </div>

        {runResult && (
          <aside className="w-72 bg-slate-900 border-l border-slate-700 p-4 overflow-y-auto">
            <p className="text-white text-sm font-semibold mb-2">Run result</p>
            <p className="text-slate-400 text-xs mb-3">{runResult.message}</p>
            <div className="space-y-2">
              {runResult.results?.map((r, idx) => (
                <div key={idx} className="bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-xs">
                  <p className="text-slate-300">Step {r.position} · WB-{r.workbook_id}</p>
                  <p className={r.status === "success" ? "text-emerald-400" : "text-red-400"}>{r.status}</p>
                </div>
              ))}
            </div>
          </aside>
        )}
      </div>
    </div>
  );
}

function Flows({ token }) {
  return (
    <ReactFlowProvider>
      <FlowBuilder token={token} />
    </ReactFlowProvider>
  );
}

export default Flows;