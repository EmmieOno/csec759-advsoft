#!/usr/bin/env bash
# Run ONE SQLiFuzz trial end to end and save everything under
#   ~/csec759-advsoft/Assignment3_Tool/raw/<group>/run<N>/     (override the root with RAW_DIR)
# <N> is the next free run number in that group's folder (or TRIAL_NUMBER if set).
# terminal.log in that folder is the full terminal output (also shown live).
# raw/run_index.txt lists which config and seed each run was.
#
# Usage (from the repo root, the folder that contains sqlifuzz/):
#   scripts/run_trial.sh <case_page> <group> <config> <seed> <boolean 0|1> [require_structure 0|1]
# Example:
#   scripts/run_trial.sh a2_filtered.php primary_case prototype 1 1
#
# Needs these exported in your shell first:
#   WUT_NAME   name used in shared-data/mysql_proxy_<WUT_NAME>*.log (same value you used in A2)
#   DVWA_USER, DVWA_PASS   DVWA login (not stored in any file)
# Optional: HOST_NAME (if you used it in A2), SHARED_DATA (default ./shared-data), TRIAL_TIMEOUT (default 900 s)
set -u

if [ $# -lt 5 ]; then
  sed -n '2,12p' "$0"; exit 1
fi
PAGE="$1"; GROUP="$2"; CONFIG="$3"; SEED="$4"; BOOL="$5"; STRUCT="${6:-1}"

: "${WUT_NAME:?export WUT_NAME first}"
: "${DVWA_USER:?export DVWA_USER first}"
: "${DVWA_PASS:?export DVWA_PASS first}"
TIMEOUT="${TRIAL_TIMEOUT:-900}"
SHARED="${SHARED_DATA:-./shared-data}"
RAW_ROOT="${RAW_DIR:-$HOME/csec759-advsoft/Assignment3_Tool/raw}"

# Run number: TRIAL_NUMBER if you set it, otherwise the next free number in this group's folder.
if [ -n "${TRIAL_NUMBER:-}" ]; then
  N="$TRIAL_NUMBER"
else
  LAST=$(ls -1 "$RAW_ROOT/$GROUP" 2>/dev/null | sed -nE "s/^${CONFIG}_run([0-9]+)$/\1/p" | sort -n | tail -1)
  N=$(( ${LAST:-0} + 1 ))
fi
OUT="$RAW_ROOT/$GROUP/${CONFIG}_run$N"

if [ -e "$OUT" ]; then
  echo "refusing to overwrite $OUT (rename or move the old run; keep failed runs)"; exit 2
fi
if (echo > /dev/tcp/127.0.0.1/8888) 2>/dev/null; then
  echo "port 8888 is already in use (stop the old mitmdump: pkill -f mitmdump)"; exit 3
fi
mkdir -p "$OUT"
touch "$OUT/.start"

DBLOG_BEFORE=$(cat "$SHARED"/mysql_proxy_"${WUT_NAME}"*.log 2>/dev/null | wc -l)
START=$(date -u +%Y-%m-%dT%H:%M:%SZ)

SQLIFUZZ_SEED="$SEED" SQLIFUZZ_BOOLEAN="$BOOL" SQLIFUZZ_REQUIRE_STRUCTURE="$STRUCT" \
  timeout "$TIMEOUT" mitmdump --mode reverse:http://localhost:8081 --listen-port 8888 \
  -s sqlifuzz/mitmproxy_addon.py > >(tee "$OUT/terminal.log") 2>&1 &
MITM=$!

# wait (up to 30 s) for the proxy to start listening
for _ in $(seq 1 60); do
  (echo > /dev/tcp/127.0.0.1/8888) 2>/dev/null && break
  sleep 0.5
done

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/drive_browser.py" "$PAGE" > "$OUT/driver.log" 2>&1
DRV=$?
if [ "$DRV" -ne 0 ]; then
  echo "browser driver failed (exit $DRV), see $OUT/driver.log"
  kill "$MITM" 2>/dev/null
fi
wait "$MITM"; RC=$?          # mitmdump exits by itself after SQLiFuzz prints FINISH; 124 = timeout
sleep 1                      # let tee finish writing terminal.log
END=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# keep the result file(s) written during this trial and the new database-log lines
mkdir -p "$OUT/final_result"
find final_result -type f -newer "$OUT/.start" -exec cp {} "$OUT/final_result/" \; 2>/dev/null
cat "$SHARED"/mysql_proxy_"${WUT_NAME}"*.log 2>/dev/null | tail -n +$((DBLOG_BEFORE + 1)) > "$OUT/mysql_proxy_slice.log"
rm -f "$OUT/.start"

SEED_APPLIED=no
grep -q "random seed set to ${SEED}" "$OUT/terminal.log" 2>/dev/null && SEED_APPLIED=yes

{
  echo "case=$PAGE"
  echo "group=$GROUP"
  echo "config=$CONFIG"
  echo "seed=$SEED"
  echo "boolean=$BOOL"
  echo "require_structure=$STRUCT"
  echo "wut_name=$WUT_NAME"
  echo "start_utc=$START"
  echo "end_utc=$END"
  echo "mitmdump_exit=$RC"
  echo "driver_exit=$DRV"
  echo "seed_line_in_terminal_log=$SEED_APPLIED"
  echo "git_commit=$(git rev-parse HEAD 2>/dev/null || echo none)"
  echo "SQLIFuzz_py_sha256=$(sha256sum sqlifuzz/SQLIFuzz.py 2>/dev/null | cut -d' ' -f1)"
  echo "boolean_probe_py_sha256=$(sha256sum sqlifuzz/boolean_probe.py 2>/dev/null | cut -d' ' -f1)"
} > "$OUT/meta.txt"

# The folder name has only the run number, so keep a plain index of what each run was.
echo "${GROUP}/run${N}  config=${CONFIG}  seed=${SEED}  boolean=${BOOL}  require_structure=${STRUCT}  start=${START}  mitmdump_exit=${RC}" >> "$RAW_ROOT/run_index.txt"

echo "done: $OUT  (config=$CONFIG seed=$SEED, mitmdump exit $RC, driver exit $DRV, seed applied: $SEED_APPLIED)"
echo "terminal output saved to: $OUT/terminal.log"
