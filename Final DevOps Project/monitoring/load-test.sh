#!/bin/sh
# Generate traffic through the Ingress for a couple of minutes so the dashboard and the HPA have
# something to show. Usage: ./load-test.sh http://127.0.0.1:PORT tracker.local
URL=${1:-http://127.0.0.1:8080}; HOST=${2:-tracker.local}
end=$(( $(date +%s) + ${3:-120} ))
while [ "$(date +%s)" -lt "$end" ]; do
  curl -s -o /dev/null -H "Host: $HOST" "$URL/api/issues"
  curl -s -o /dev/null -H "Host: $HOST" "$URL/api/issues/stats"
  curl -s -o /dev/null -H "Host: $HOST" "$URL/api/issues/999"      # a 404 to keep the status label mix honest
done
