import React, { useEffect, useState } from "react";
import { api } from "./api.js";

const NEXT = { open: "in_progress", in_progress: "done", done: "open" };
const STATE_LABEL = { open: "Open", in_progress: "In progress", done: "Done" };
const ACUITY = {
  high: { rank: 1, word: "High" },
  medium: { rank: 2, word: "Med" },
  low: { rank: 3, word: "Low" },
};
const ORDER = { high: 0, medium: 1, low: 2 };

function age(iso, now) {
  if (!iso) return "--";
  const secs = Math.max(0, Math.floor((now - new Date(iso + (iso.endsWith("Z") ? "" : "Z")).getTime()) / 1000));
  if (secs < 60) return `${secs}s`;
  if (secs < 3600) return `${Math.floor(secs / 60)}m`;
  if (secs < 86400) return `${Math.floor(secs / 3600)}h`;
  return `${Math.floor(secs / 86400)}d`;
}

const Chevron = () => (
  <svg viewBox="0 0 16 16" aria-hidden="true" className="ic">
    <path d="M6 3.5 10.5 8 6 12.5" fill="none" stroke="currentColor" strokeWidth="1.75"
      strokeLinecap="square" />
  </svg>
);

const Cross = () => (
  <svg viewBox="0 0 16 16" aria-hidden="true" className="ic">
    <path d="M4.5 4.5l7 7M11.5 4.5l-7 7" fill="none" stroke="currentColor" strokeWidth="1.75"
      strokeLinecap="square" />
  </svg>
);

const Plus = () => (
  <svg viewBox="0 0 16 16" aria-hidden="true" className="ic">
    <path d="M8 3.25v9.5M3.25 8h9.5" fill="none" stroke="currentColor" strokeWidth="1.9"
      strokeLinecap="square" />
  </svg>
);

export default function App() {
  const [issues, setIssues] = useState([]);
  const [stats, setStats] = useState(null);
  const [backend, setBackend] = useState("checking");
  const [filter, setFilter] = useState("all");
  const [form, setForm] = useState({ title: "", priority: "medium", assignee: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [admitted, setAdmitted] = useState(null);
  const [now, setNow] = useState(Date.now());

  async function refresh() {
    try {
      const [list, s, h] = await Promise.all([api.list(), api.stats(), api.health()]);
      setIssues(list); setStats(s); setBackend(h.status); setError("");
    } catch (e) {
      setBackend("unreachable"); setError(e.message);
    }
  }
  useEffect(() => { refresh(); }, []);
  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 15000);
    return () => clearInterval(t);
  }, []);

  async function submit(e) {
    e.preventDefault();
    if (!form.title.trim() || busy) return;
    setBusy(true);
    try {
      const created = await api.create(form);
      setForm({ title: "", priority: "medium", assignee: "" });
      setAdmitted(created?.id ?? null);
      setTimeout(() => setAdmitted(null), 1400);
      await refresh();
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }

  async function advance(issue) {
    try { await api.update(issue.id, { status: NEXT[issue.status] }); await refresh(); }
    catch (e) { setError(e.message); }
  }

  async function discharge(issue) {
    try { await api.remove(issue.id); await refresh(); }
    catch (e) { setError(e.message); }
  }

  const count = (f) => (f === "all" ? issues.length : issues.filter((i) => i.status === f).length);
  const shown = (filter === "all" ? issues : issues.filter((i) => i.status === filter))
    .slice()
    .sort((a, b) => (ORDER[a.priority] - ORDER[b.priority]) || (a.id - b.id));

  const census = [
    { k: "total", label: "Census", value: stats?.total },
    { k: "open", label: "Open", value: stats?.by_status.open },
    { k: "in_progress", label: "In progress", value: stats?.by_status.in_progress },
    { k: "done", label: "Done", value: stats?.by_status.done },
    { k: "acute", label: "Open · acuity 1", value: stats?.open_high_priority, acute: true },
  ];

  return (
    <div className="board">
      <header className="rail">
        <div className="ident">
          <h1>Issue Board</h1>
          <p className="sub">Triage, admission and discharge</p>
        </div>
        <dl className="census">
          {census.map((c) => (
            <div key={c.k} className={`fig${c.acute ? " fig-acute" : ""}`}>
              <dd>{c.value ?? "--"}</dd>
              <dt>{c.label}</dt>
            </div>
          ))}
        </dl>
        <p className={`lamp lamp-${backend === "ready" ? "ok" : "bad"}`}>
          <span className="bulb" aria-hidden="true" />
          Backend {backend}
        </p>
      </header>

      <form className="intake" onSubmit={submit}>
        <label className="fld fld-title">
          <span>New issue</span>
          <input value={form.title} placeholder="What is wrong?" required
            onChange={(e) => setForm({ ...form, title: e.target.value })} />
        </label>
        <label className="fld">
          <span>Acuity</span>
          <select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}>
            <option value="high">1 · High</option>
            <option value="medium">2 · Med</option>
            <option value="low">3 · Low</option>
          </select>
        </label>
        <label className="fld">
          <span>Assignee</span>
          <input value={form.assignee} placeholder="Unassigned"
            onChange={(e) => setForm({ ...form, assignee: e.target.value })} />
        </label>
        <button type="submit" disabled={busy || !form.title.trim()}>
          <Plus /> {busy ? "Admitting" : "Admit"}
        </button>
      </form>

      {error && (
        <p className="alert" role="alert">
          <strong>Request failed.</strong> {error} Check the backend is up, then retry.
        </p>
      )}

      <nav className="views" aria-label="Board views">
        {["all", "open", "in_progress", "done"].map((f) => (
          <button key={f} className={filter === f ? "on" : ""} aria-pressed={filter === f}
            onClick={() => setFilter(f)}>
            {f === "all" ? "All" : STATE_LABEL[f]}
            <span className="tally">{count(f)}</span>
          </button>
        ))}
      </nav>

      <table className="sheet">
        <caption className="sr">Issues on the board, ranked by acuity</caption>
        <thead>
          <tr>
            <th scope="col" className="c-ac">Acuity</th>
            <th scope="col">Issue</th>
            <th scope="col" className="c-as">Assignee</th>
            <th scope="col" className="c-st">State</th>
            <th scope="col" className="c-ag">Age</th>
            <th scope="col" className="c-dc"><span className="sr">Discharge</span></th>
          </tr>
        </thead>
        <tbody>
          {shown.map((i) => {
            const a = ACUITY[i.priority] ?? ACUITY.low;
            return (
              <tr key={i.id} className={`${i.status === "done" ? "is-done" : ""}${admitted === i.id ? " is-new" : ""}`}>
                <td className="c-ac">
                  <span className={`ac ac-${a.rank}`}>
                    <b>{a.rank}</b>{a.word}
                  </span>
                </td>
                <th scope="row" className="c-ti">{i.title}</th>
                <td className="c-as">{i.assignee || <span className="none">Unassigned</span>}</td>
                <td className="c-st">
                  <button className={`st st-${i.status}`} onClick={() => advance(i)}
                    title={`Advance to ${STATE_LABEL[NEXT[i.status]]}`}>
                    {STATE_LABEL[i.status]} <Chevron />
                  </button>
                </td>
                <td className="c-ag"><time>{age(i.created_at, now)}</time></td>
                <td className="c-dc">
                  <button className="dc" onClick={() => discharge(i)}
                    aria-label={`Discharge ${i.title}`} title="Discharge"><Cross /></button>
                </td>
              </tr>
            );
          })}
          {shown.length === 0 && (
            <tr className="blank">
              <td colSpan="6">
                {issues.length === 0
                  ? "The board is clear. Admit an issue above to start."
                  : `Nothing in ${STATE_LABEL[filter] ?? "this view"}.`}
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <footer className="foot">
        <span>React · FastAPI · PostgreSQL</span>
        <span>Acuity 1 is most urgent</span>
      </footer>
    </div>
  );
}
