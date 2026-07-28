function Card({ title, actions, children, className = "", noPadding = false }) {
  return (
    <div
      className={`bg-zinc-900 border border-zinc-800 rounded-xl shadow-sm hover:border-zinc-700 transition-colors duration-200 ${className}`}
    >
      {title && (
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-zinc-800">
          <h3 className="text-zinc-100 font-semibold text-sm">{title}</h3>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      )}
      <div className={noPadding ? "" : "p-5"}>{children}</div>
    </div>
  );
}

export default Card;