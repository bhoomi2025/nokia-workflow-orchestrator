function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-14 px-6">
      {Icon && (
        <div className="w-12 h-12 rounded-xl bg-zinc-800 flex items-center justify-center mb-4">
          <Icon size={22} className="text-zinc-500" />
        </div>
      )}
      <p className="text-zinc-300 font-medium text-sm">{title}</p>
      {description && <p className="text-zinc-500 text-xs mt-1 max-w-xs">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export default EmptyState;