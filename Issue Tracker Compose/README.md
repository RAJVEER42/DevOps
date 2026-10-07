# Issue Tracker: a three-service application on Docker Compose

**Name:** Rajveer Bishnoi
**Enrollment Number:** 24BCS10404

A small issue tracker built to be run three ways: each piece by hand, the whole thing with one
`docker compose up`, and (later) on Kubernetes. The code is original to this repository.

```
browser ──> frontend (nginx, port 8080) ──/api──> backend (FastAPI, port 8000) ──> postgres (16)
            serves the React bundle               SQLAlchemy + Alembic                 named volume
```

| Part | Stack | Folder |
|---|---|---|
| Frontend | React 18 + Vite, served by `nginx-unprivileged`; nginx proxies `/api`, `/health`, `/ready`, `/docs` to the backend | [frontend/](frontend/) |
| Backend | FastAPI, SQLAlchemy 2, Alembic migrations, psycopg 3, pytest | [backend/](backend/) |
| Database | PostgreSQL 16 (Alpine), data on a Compose volume | `docker-compose.yml` |

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | liveness, no dependencies |
| GET | `/ready` | readiness, runs `SELECT 1` against PostgreSQL |
| GET | `/api/issues` | list, newest first, optional `?status_=open` |
| POST | `/api/issues` | create; validates priority and status, returns 201 |
| GET | `/api/issues/{id}` | one issue, 404 if missing |
| PUT | `/api/issues/{id}` | partial update |
| DELETE | `/api/issues/{id}` | 204 |
| GET | `/api/issues/stats` | totals by status and priority, open high-priority count |
| GET | `/docs` | the generated OpenAPI UI |

## 1. Tests

Seven pytest cases run against a throwaway SQLite database (the FastAPI dependency for the
DB session is overridden in `tests/conftest.py`), so they never touch PostgreSQL.

```bash
cd backend && python3.12 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest -v
```

![tests](screenshots/tests.png)

## 2. Running the application manually

Each service started on its own, the way you would during development. Ports 8000, 3000 and
5432 were already in use by other tools on this laptop, so the run used 5433, 8011 and 5174.

```bash
# database
docker run -d --name tracker-pg -e POSTGRES_DB=tracker -e POSTGRES_USER=tracker -e POSTGRES_PASSWORD=tracker -p 5433:5432 postgres:16-alpine

# backend: migrate, then serve
cd backend
export DATABASE_URL=postgresql+psycopg://tracker:tracker@localhost:5433/tracker
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --port 8011

# frontend: Vite dev server proxying /api to the backend
cd ../frontend && npm install
VITE_API_TARGET=http://localhost:8011 npm run dev -- --port 5174
```

Alembic created the `issues` table (visible with `\d issues` in psql), uvicorn came up, `/ready`
returned `ready`, and the Vite dev server served the page and proxied `/api/issues/stats`.

![manual run](screenshots/manual-run.png)

### Testing the backend APIs

Create three issues, list, fetch one, update, delete, confirm the 404, send an invalid priority
and get a 422, read the stats, and confirm the rows in PostgreSQL itself.

![manual API tests](screenshots/manual-api-tests.png)

The React UI against the manual backend, and the OpenAPI docs page:

![frontend on vite](screenshots/manual-frontend-vite.png)
![backend docs](screenshots/manual-backend-docs.png)

## 3. Dockerfiles

**backend/Dockerfile.** Two stages on `python:3.12-slim`: the first installs the pinned
requirements into a prefix, the second copies only that prefix plus the app and migrations.
Runs as a fixed non-root UID, exposes 8000, has a `HEALTHCHECK` on `/health`, and starts via
`entrypoint.sh`, which runs `alembic upgrade head` and then uvicorn. Migrations therefore run
automatically on every start, which is what makes `docker compose up` on an empty volume work.

**frontend/Dockerfile.** Two stages: `node:20-alpine` runs `npm install` and `vite build`;
`nginxinc/nginx-unprivileged:1.27-alpine` serves the `dist/` output on port 8080 with
`nginx.conf`, which falls back to `index.html` for the SPA and proxies API paths to the
`backend` service name. The browser only ever talks to one origin.

## 4. docker-compose.yml

- `postgres` has a `pg_isready` healthcheck; `backend` uses `depends_on: condition:
  service_healthy`, so migrations never race the database.
- `backend` gets `DATABASE_URL` pointing at the `postgres` service name on the Compose network.
- `frontend` depends on `backend` and publishes `8080:8080`; `backend` publishes `8011:8000`
  for direct API access; the database is not published at all.
- `pgdata` is a named volume, so the data survives `docker compose restart` and
  `docker compose down` (but not `down -v`).

```bash
docker compose up -d --build
docker compose ps
docker compose logs backend
```

![compose up](screenshots/compose-up.png)

### Testing the application and the APIs on Compose

Direct to the backend on 8011, then through nginx on 8080 (page, `/ready`, create, list,
update, stats, delete, 404), then the rows inside the postgres container, then a restart of
backend and postgres to show the volume kept the data.

![compose API tests](screenshots/compose-api-tests.png)

The UI and the docs served by the frontend container through its nginx proxy:

![frontend on compose](screenshots/compose-frontend.png)
![docs through nginx](screenshots/compose-backend-docs.png)

### Tear down

```bash
docker compose down        # containers and network; add -v to drop the volume too
```

![compose down](screenshots/compose-down.png)

## Notes

- Credentials in `docker-compose.yml` are local demo values; a real deployment would inject
  them from a secret store. `backend/.env.example` shows the variables without values that matter.
- `.gitignore` excludes `.venv`, `node_modules`, `dist`, `__pycache__` and the SQLite test file.
- Everything the course capstone adds later (Helm chart, CI with Trivy, Terraform for EKS,
  Prometheus) builds on exactly these three images.
