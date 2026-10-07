import React, { useEffect, useState } from "react";
import { api } from "./api.js";

const NEXT = { open: "in_progress", in_progress: "done", done: "open" };
const LABEL = { open: "Open", in_progress: "In progress", done: "Done" };

export default function App() {
  const [issues, setIssues] = useState([]);
  const [stats, setStats] = useState(null);
  const [backend, setBackend] = useState("checking");
  const [filter, setFilter] = useState("all");
  const [form, setForm] = useState({ title: "", priority: "medium", assignee: "" });
  const [error, setError] = useState("");

  async function refresh() {
    try {
      const [list, s, h] = await Promise.all([api.list(), api.stats(), api.health()]);
      setIssues(list); setStats(s); setBackend(h.status); setError("");
    } catch (e) {
      setBackend("unreachable"); setError(e.message);
    }
  }
  useEffect(() => { refresh(); }, []);

  async function submit(e) {
    e.preventDefault();
    if (!form.title.trim()) return;
    try { await api.create(form); setForm({ title: "", priority: "medium", assignee: "" }); refresh(); }
    catch (e) { setError(e.message); }
  }

  const shown = filter === "all" ? issues : issues.filter((i) => i.status === filter);

  return (
    <div className="shell">
      <aside className="side">
        <h1>Issue Tracker</h1>
        <p className="muted">frontend: React + Vite<br />backend: FastAPI<br />db: PostgreSQL</p>
        <div className={`pill ${backend === "ready" ? "ok" : "bad"}`}>backend {backend}</div>
      </aside>
      <main>
        <section className="kpis">
          <Kpi label="Total" value={stats?.total ?? "–"} />
          <Kpi label="Open" value={stats?.by_status.open ?? "–"} />
          <Kpi label="In progress" value={stats?.by_status.in_progress ?? "–"} />
          <Kpi label="Done" value={stats?.by_status.done ?? "–"} />
          <Kpi label="Open & high" value={stats?.open_high_priority ?? "–"} accent />
        </section>

        <form className="create" onSubmit={submit}>
          <input placeholder="New issue title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          <select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}>
            <option value="low">low</option><option value="medium">medium</option><option value="high">high</option>
          </select>
          <input placeholder="assignee" value={form.assignee} onChange={(e) => setForm({ ...form, assignee: e.target.value })} />
          <button type="submit">Add</button>
        </form>
        {error && <p className="error">{error}</p>}

        <div className="filters">
          {["all", "open", "in_progress", "done"].map((f) => (
            <button key={f} className={filter === f ? "active" : ""} onClick={() => setFilter(f)}>{f === "all" ? "All" : LABEL[f]}</button>
          ))}
        </div>

        <table>
          <thead><tr><th>#</th><th>Title</th><th>Priority</th><th>Assignee</th><th>Status</th><th></th></tr></thead>
          <tbody>
            {shown.map((i) => (
              <tr key={i.id}>
                <td className="muted">{i.id}</td>
                <td>{i.title}</td>
                <td><span className={`badge ${i.priority}`}>{i.priority}</span></td>
                <td>{i.assignee || <span className="muted">unassigned</span>}</td>
                <td><button className="status" onClick={() => api.update(i.id, { status: NEXT[i.status] }).then(refresh)}>{LABEL[i.status]} →</button></td>
                <td><button className="x" onClick={() => api.remove(i.id).then(refresh)}>delete</button></td>
              </tr>
            ))}
            {shown.length === 0 && <tr><td colSpan="6" className="muted center">No issues here.</td></tr>}
          </tbody>
        </table>
      </main>
    </div>
  );
}

function Kpi({ label, value, accent }) {
  return <div className={`kpi ${accent ? "accent" : ""}`}><div className="v">{value}</div><div className="l">{label}</div></div>;
}
