function Badge({ status, children }) {
  const s = (status || "default").toLowerCase();
  const styles = {
    success: "bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-500/20",
    failed: "bg-rose-500/10 text-rose-400 ring-1 ring-rose-500/20",
    running: "bg-amber-500/10 text-amber-400 ring-1 ring-amber-500/20",
    queued: "bg-amber-500/10 text-amber-400 ring-1 ring-amber-500/20",
    default: "bg-zinc-700/40 text-zinc-300 ring-1 ring-zinc-600/30",
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium uppercase tracking-wide ${styles[s] || styles.default}`}>
      {children || s}
    </span>
  );
}

export default Badge;