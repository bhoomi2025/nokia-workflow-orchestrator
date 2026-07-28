import {
  Bell,
  Search,
  UserCircle,
  LogOut,
  Moon,
  ChevronDown,
} from "lucide-react";

function Navbar({ onLogout }) {
  return (
    <header className="sticky top-0 z-40 h-16 bg-slate-900/80 backdrop-blur-xl border-b border-slate-800 flex items-center justify-between px-8">

      {/* Left Section */}
      <div className="flex items-center gap-5">

        <div>
          <h1 className="text-white text-xl font-semibold tracking-wide">
            Workflow Orchestrator
          </h1>

          <p className="text-xs text-slate-500">
            Enterprise Automation Platform
          </p>
        </div>

      </div>

      {/* Center Search */}
      <div className="hidden lg:flex w-[420px]">

        <div className="relative w-full">

          <Search
            size={17}
            className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
          />

          <input
            type="text"
            placeholder="Search workflows, jobs..."
            className="
              w-full
              bg-slate-800
              border
              border-slate-700
              rounded-xl
              py-2.5
              pl-11
              pr-4
              text-sm
              text-white
              placeholder:text-slate-500
              outline-none
              transition
              focus:border-cyan-500
              focus:ring-2
              focus:ring-cyan-500/20
            "
          />

        </div>

      </div>

      {/* Right Section */}
      <div className="flex items-center gap-4">

        {/* API Status */}
        <div className="hidden md:flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-3 py-1">

          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>

          <span className="text-xs text-emerald-300">
            API Connected
          </span>

        </div>

        {/* Dark Mode */}
        <button className="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center hover:border-cyan-500 transition">

          <Moon size={18} className="text-slate-300"/>

        </button>

        {/* Notification */}
        <button className="relative w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center hover:border-cyan-500 transition">

          <Bell size={18} className="text-slate-300"/>

          <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-red-500"></span>

        </button>

        {/* User */}
        <div className="flex items-center gap-3 bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 hover:border-cyan-500 transition cursor-pointer">

          <UserCircle
            size={34}
            className="text-cyan-400"
          />

          <div className="hidden lg:block">

            <h3 className="text-sm text-white font-medium">
              Admin
            </h3>

            <p className="text-xs text-slate-400">
              Nokia Team
            </p>

          </div>

          <ChevronDown
            size={16}
            className="text-slate-500"
          />

        </div>

        {/* Logout */}
        <button
          onClick={onLogout}
          className="
            flex
            items-center
            gap-2
            bg-red-500/10
            border
            border-red-500/20
            text-red-400
            px-4
            py-2
            rounded-xl
            hover:bg-red-500
            hover:text-white
            transition-all
            duration-300
          "
        >
          <LogOut size={16}/>
          Logout
        </button>

      </div>

    </header>
  );
}

export default Navbar;