#!/bin/bash
# reset_state.sh — reset target/proxy state between A2 trials.
#
# Run this between every trial to avoid stale shared-data logs, leftover
# mitmdump processes, or carried-over DB proxy state contaminating the
# next run's evidence.
#
# Usage: ./reset_state.sh

set -euo pipefail
cd ~/SQLiFuzz

echo "Killing any leftover mitmdump/proxy processes..."
pkill -f mitmdump 2>/dev/null || true
sleep 1

echo "Archiving and clearing shared-data logs so the next trial starts clean..."
if ls shared-data/mysql_proxy_dvwa*.log >/dev/null 2>&1; then
  mkdir -p shared-data/_archived
  mv shared-data/mysql_proxy_dvwa*.log shared-data/_archived/ 2>/dev/null || true
fi

echo "Confirming DVWA container is up and responsive..."
if ! sudo docker ps --filter "name=dvwa" --filter "status=running" | grep -q dvwa; then
  echo "DVWA container is not running — bringing it up..."
  (cd WUT/dvwa && sudo docker compose up --detach)
  sleep 5
fi

status_code="$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/login.php || echo "000")"
if [ "$status_code" != "200" ]; then
  echo "WARNING: DVWA login page returned HTTP ${status_code}, expected 200."
  echo "Check container health before running the next trial."
  exit 1
fi

echo "Reset complete. Target is ready for the next trial."
