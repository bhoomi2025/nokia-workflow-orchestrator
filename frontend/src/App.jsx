import { useState } from "react";
import Sidebar from "./components/sidebar";
import Navbar from "./components/navbar";


import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Inventory from "./pages/Inventory";
import Workbooks from "./pages/Workbooks";
import Jobs from "./pages/Jobs";
import Flows from "./pages/Flows";
import Executions from "./pages/Executions";
import Settings from "./pages/Settings";

function App() {
  const [token, setToken] = useState(null);
  const [page, setPage] = useState("dashboard");
  const [refreshKey, setRefreshKey] = useState(0);
  console.log("Current Page:", page);
  

  if (!token) {
    return <Login onLogin={setToken} />;
  }

  function bumpRefresh() {
    setRefreshKey((k) => k + 1);
  }

  function handleLogout() {
    setToken(null);
    setPage("dashboard");
  }

  return (
    <div className="flex bg-slate-950 min-h-screen">
      <Sidebar active={page} onNavigate={setPage} />

      <div className="flex-1">
        <Navbar onLogout={handleLogout} active={page} />
        {page === "dashboard" && <Dashboard token={token} refreshKey={refreshKey} onNavigate={setPage} />}

        {page === "inventory" && <Inventory token={token} onChanged={bumpRefresh} />}
        {page === "workbooks" && <Workbooks token={token} onChanged={bumpRefresh} />}
        {page === "jobs" && <Jobs token={token} onChanged={bumpRefresh} />}
        {page === "flows" && <Flows token={token} onChanged={bumpRefresh} />}
        {page === "executions" && <Executions token={token} />}
        {page === "settings" && <Settings onLogout={handleLogout} />}
      </div>
    </div>
  );
}

export default App;
