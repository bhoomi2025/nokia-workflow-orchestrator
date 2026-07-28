import { useState } from "react";
import { apiFetch } from "../api";

function StatItem({ value, label }) {
  return (
    <div>
      <p className="text-3xl md:text-4xl font-extrabold text-cyan-400">{value}</p>
      <p className="text-slate-400 text-xs mt-1 uppercase tracking-wide">{label}</p>
    </div>
  );
}

function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    const { ok, data } = await apiFetch("/login", null, {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });

    setLoading(false);

    if (!ok || !data.access_token) {
      setError(data.detail || data.message || "Login failed. Check your credentials.");
      return;
    }

    onLogin(data.access_token);
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col lg:flex-row">
      {/* Left: Hero section */}
      <div className="relative flex-1 flex flex-col justify-center px-10 lg:px-16 py-16 overflow-hidden">
        {/* subtle glow background */}
        <div className="absolute -top-32 -left-32 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative">
          <span className="inline-block bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold tracking-wide px-3 py-1 rounded-full mb-6">
            IA :: WFO
          </span>

          <h1 className="text-4xl md:text-5xl font-extrabold text-white leading-tight">
            The internal platform for
            <br />
            <span className="text-cyan-400">workflow orchestration</span>
          </h1>

          <p className="text-slate-400 text-base mt-6 max-w-md">
            Chain workbooks, manage device inventories, and run automated jobs
            end-to-end — with full visibility and control.
          </p>

          <div className="grid grid-cols-4 gap-6 mt-14 max-w-lg">
            <StatItem value="99%" label="Uptime" />
            <StatItem value="4x" label="Faster runs" />
            <StatItem value="24/7" label="Automation" />
            <StatItem value="1" label="Control panel" />
          </div>
        </div>
      </div>

      {/* Right: Login form */}
      <div className="flex-1 flex items-center justify-center px-6 py-16 bg-slate-900/40 border-t lg:border-t-0 lg:border-l border-slate-800">
        <div className="w-full max-w-sm">
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-white">Sign in</h2>
            <p className="text-slate-500 text-sm mt-1">Access your Workflow Orchestrator dashboard</p>
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
              <label className="text-xs text-slate-400 uppercase tracking-wide">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                className="mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-400"
              />
            </div>

            <div>
              <label className="text-xs text-slate-400 uppercase tracking-wide">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-400"
              />
            </div>

            {error && <div className="text-red-400 text-xs">{error}</div>}

            <button
              type="submit"
              disabled={loading}
              className="bg-cyan-500 hover:bg-cyan-400 disabled:opacity-60 text-slate-950 font-semibold px-4 py-2.5 rounded-lg transition mt-2"
            >
              {loading ? "Signing in…" : "Sign in"}
            </button>
          </form>

          <p className="text-slate-600 text-xs mt-8 text-center">
            Connects to your local backend at{" "}
            <code className="bg-slate-900 px-1.5 py-0.5 rounded text-slate-300">
              http://127.0.0.1:8000
            </code>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;