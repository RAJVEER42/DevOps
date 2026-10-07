def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_ready_hits_the_database(client):
    assert client.get("/ready").json() == {"status": "ready"}


def test_create_returns_201_and_defaults(client):
    r = client.post("/api/issues", json={"title": "Login button misaligned"})
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "open" and body["priority"] == "medium" and body["id"] == 1


def test_create_rejects_bad_priority(client):
    r = client.post("/api/issues", json={"title": "x", "priority": "urgent"})
    assert r.status_code == 422


def test_list_and_filter(client):
    client.post("/api/issues", json={"title": "a"})
    client.post("/api/issues", json={"title": "b", "status": "done"})
    assert len(client.get("/api/issues").json()) == 2
    assert [i["title"] for i in client.get("/api/issues", params={"status_": "done"}).json()] == ["b"]


def test_get_update_delete_cycle(client):
    issue_id = client.post("/api/issues", json={"title": "Flaky checkout", "priority": "high"}).json()["id"]
    assert client.get(f"/api/issues/{issue_id}").json()["title"] == "Flaky checkout"
    r = client.put(f"/api/issues/{issue_id}", json={"status": "in_progress", "assignee": "jp"})
    assert r.status_code == 200 and r.json()["status"] == "in_progress" and r.json()["assignee"] == "jp"
    assert client.delete(f"/api/issues/{issue_id}").status_code == 204
    assert client.get(f"/api/issues/{issue_id}").status_code == 404


def test_stats(client):
    client.post("/api/issues", json={"title": "a", "priority": "high"})
    client.post("/api/issues", json={"title": "b", "priority": "high", "status": "done"})
    client.post("/api/issues", json={"title": "c", "priority": "low", "status": "in_progress"})
    s = client.get("/api/issues/stats").json()
    assert s["total"] == 3
    assert s["by_status"] == {"open": 1, "in_progress": 1, "done": 1}
    assert s["open_high_priority"] == 1


def _metric(body, name):
    line = next(l for l in body.splitlines() if l.startswith(name + " "))
    return float(line.split()[-1])


def test_metrics_endpoint_counts_requests(client):
    before = _metric(client.get("/metrics").text, "tracker_issues_created_total")
    client.get("/health")
    client.post("/api/issues", json={"title": "metrics"})
    body = client.get("/metrics").text
    assert 'tracker_http_requests_total{method="GET",route="/health",status="200"}' in body
    assert _metric(body, "tracker_issues_created_total") == before + 1
    assert "tracker_http_request_duration_seconds_bucket" in body
