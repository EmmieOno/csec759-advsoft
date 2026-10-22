#!/usr/bin/env bash
# Run the pilot comparison (baseline vs prototype) and build the results table.
#
# Usage (repo root; WUT_NAME, DVWA_USER, DVWA_PASS exported):
#   scripts/run_pilot.sh                          # lean plan: 10 runs
#   SEEDS_SECONDARY="1 2 3" scripts/run_pilot.sh  # full plan: 18 runs
#
# Lean plan  = primary case x 3 seeds x 2 configs (6) + control x 1 seed x 2 (2) + POST variant x 1 seed x 2 (2)
# Baseline = same code with SQLIFUZZ_BOOLEAN=0; prototype = SQLIFUZZ_BOOLEAN=1.
# Baseline and prototype runs alternate so slow drift affects both equally.
set -u
SEEDS_PRIMARY="${SEEDS_PRIMARY:-1 2 3}"
SEEDS_SECONDARY="${SEEDS_SECONDARY:-1}"
PAUSE="${PAUSE_BETWEEN:-3}"

run() { scripts/run_trial.sh "$@"; sleep "$PAUSE"; }

for s in $SEEDS_PRIMARY; do
  run a2_filtered.php primary_case baseline  "$s" 0
  run a2_filtered.php primary_case prototype "$s" 1
done

for s in $SEEDS_SECONDARY; do
  run a2_control.php       control      baseline  "$s" 0
  run a2_control.php       control      prototype "$s" 1
  run a2_filtered_post.php variant_post baseline  "$s" 0
  run a2_filtered_post.php variant_post prototype "$s" 1
done

python3 scripts/summarize_trials.py
