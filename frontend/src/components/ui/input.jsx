function Input({ label, type = "text", value, onChange, placeholder, required, className = "" }) {
  return (
    <div className={className}>
      {label && (
        <label className="block text-xs font-medium text-zinc-400 uppercase tracking-wide mb-1.5">
          {label}
        </label>
      )}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        className="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2.5 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500/40 transition-colors"
      />
    </div>
  );
}

export default Input;