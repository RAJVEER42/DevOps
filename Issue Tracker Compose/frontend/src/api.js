// Same-origin calls; the dev server or nginx proxies them to the backend.
async function request(path, options = {}) {
  const res = await fetch(path, { headers: { "Content-Type": "application/json" }, ...options });
  if (res.status === 204) return null;
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail ? JSON.stringify(body.detail) : `${res.status} ${res.statusText}`);
  return body;
}

export const api = {
  health: () => request("/ready"),
  list: () => request("/api/issues"),
  stats: () => request("/api/issues/stats"),
  create: (issue) => request("/api/issues", { method: "POST", body: JSON.stringify(issue) }),
  update: (id, patch) => request(`/api/issues/${id}`, { method: "PUT", body: JSON.stringify(patch) }),
  remove: (id) => request(`/api/issues/${id}`, { method: "DELETE" }),
};
