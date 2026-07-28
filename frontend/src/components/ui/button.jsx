function Button({ children, variant = "primary", icon: Icon, disabled, onClick, type = "button", className = "" }) {
  const base = "inline-flex items-center justify-center gap-2 font-medium text-sm rounded-lg transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-violet-500/50";
  const variants = {
    primary: "bg-violet-600 hover:bg-violet-500 text-white px-4 py-2 shadow-sm hover:shadow-violet-600/20",
    secondary: "bg-transparent border border-zinc-700 hover:border-violet-500/60 hover:bg-zinc-800/60 text-zinc-200 px-4 py-2",
    ghost: "bg-transparent hover:bg-zinc-800/60 text-zinc-400 hover:text-zinc-100 px-3 py-1.5",
    icon: "bg-transparent hover:bg-zinc-800/60 text-zinc-400 hover:text-zinc-100 p-2",
  };

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`${base} ${variants[variant] || variants.primary} ${className}`}
    >
      {Icon && <Icon size={16} />}
      {children}
    </button>
  );
}

export default Button;