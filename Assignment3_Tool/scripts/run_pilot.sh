#!/usr/bin/env bash
# Primary/control comparison: AND helper, three seeds per configuration.
# Run from the SQLiFuzz checkout; A3_DIR optionally locates Assignment3_Tool.
set -eu
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
A3_DIR="${A3_DIR:-$SCRIPT_DIR/..}"
AND_HELPER="$A3_DIR/scripts/boolean_probe.py"
OR_HELPER="$A3_DIR/src/boolean_probe_OR.py"

if [ ! -f sqlifuzz/mitmproxy_addon.py ]; then
  echo "Run this script from the SQLiFuzz checkout containing sqlifuzz/." >&2
  exit 1
fi
for helper in "$AND_HELPER" "$OR_HELPER"; do
  if [ ! -r "$helper" ]; then
    echo "Missing helper: $helper (set A3_DIR to Assignment3_Tool)." >&2
    exit 1
  fi
done
: "${WUT_NAME:?export WUT_NAME first}"
: "${DVWA_USER:?export DVWA_USER first}"
: "${DVWA_PASS:?export DVWA_PASS first}"

cp -- "$AND_HELPER" sqlifuzz/boolean_probe.py
echo "Selected AND helper: $AND_HELPER"

SEEDS_PRIMARY="${SEEDS_PRIMARY:-1 2 3}"
SEEDS_SECONDARY="${SEEDS_SECONDARY:-1 2 3}"
PAUSE="${PAUSE_BETWEEN:-3}"
run() { bash "$SCRIPT_DIR/run_trial.sh" "$@"; sleep "$PAUSE"; }

for s in $SEEDS_PRIMARY; do
  run a2_filtered.php primary_case baseline  "$s" 0
  run a2_filtered.php primary_case prototype "$s" 1
done
for s in $SEEDS_SECONDARY; do
  run a2_control.php control baseline  "$s" 0
  run a2_control.php control prototype "$s" 1
done
python3 "$SCRIPT_DIR/summarize_trials.py"
