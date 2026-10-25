#!/usr/bin/env bash
# Variant-only comparison: OR helper, then restore the AND helper on exit.
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

restore_and() {
  cp -- "$AND_HELPER" sqlifuzz/boolean_probe.py
  echo "Restored AND helper: $AND_HELPER"
}
trap restore_and EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

cp -- "$OR_HELPER" sqlifuzz/boolean_probe.py
echo "Selected OR helper: $OR_HELPER"

SEEDS_VARIANT="${SEEDS_VARIANT:-${SEEDS_PRIMARY:-1 2 3}}"
PAUSE="${PAUSE_BETWEEN:-3}"
run() { bash "$SCRIPT_DIR/run_trial.sh" "$@"; sleep "$PAUSE"; }

for s in $SEEDS_VARIANT; do
  run a3_variant.php variant baseline  "$s" 0
  run a3_variant.php variant prototype "$s" 1
done
python3 "$SCRIPT_DIR/summarize_trials.py"
