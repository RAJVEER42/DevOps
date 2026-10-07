#!/bin/sh
# Run pending migrations, then start the API. Postgres is already healthy thanks to the
# compose healthcheck, but retry briefly in case the network is slow.
set -e
for i in $(seq 1 10); do
  alembic upgrade head && break
  echo "database not ready yet ($i), retrying..."; sleep 2
done
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
