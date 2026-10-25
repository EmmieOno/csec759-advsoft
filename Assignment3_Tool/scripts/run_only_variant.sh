#!/usr/bin/env bash
# Run the pilot comparison (baseline vs prototype) and build the results table.
#
# Usage (repo root; WUT_NAME, DVWA_USER, DVWA_PASS exported):
#   scripts/run_only_variant.sh

set -u
SEEDS_PRIMARY="${SEEDS_PRIMARY:-1 2 3}"
SEEDS_SECONDARY="${SEEDS_SECONDARY:-1 2 3}"
PAUSE="${PAUSE_BETWEEN:-3}"

run() { scripts/run_trial.sh "$@"; sleep "$PAUSE"; }

for s in $SEEDS_PRIMARY; do
  run a3_variant.php variant baseline  "$s" 0
  run a3_variant.php variant prototype "$s" 1
done

python3 scripts/summarize_trials.py
