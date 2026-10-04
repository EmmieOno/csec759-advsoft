#!/bin/bash
# run_case.sh — run one trial of a boolean-oracle case against SQLiFuzz.
#
# Usage:
#   ./run_case.sh <case_id> <php_filename> <trial_number>
#
# Example:
#   ./run_case.sh filtered-get a2_filtered.php 1
#   ./run_case.sh filtered-post a2_filtered_post.php 2
#   ./run_case.sh control a2_control.php 3
#
# Produces: evidence/<case_id>/run<trial_number>/
#   - config-general.yaml  (copy of the config used)
#   - terminal.log          (full mitmdump stdout/stderr)
#   - mysql_proxy_dvwa*.log (DB proxy query/response log)
#   - meta.txt              (case_id, php file, trial, start/end time, exit status)

set -euo pipefail

CASE_ID="${1:?Usage: run_case.sh <case_id> <php_filename> <trial_number>}"
PHP_FILE="${2:?Usage: run_case.sh <case_id> <php_filename> <trial_number>}"
TRIAL="${3:?Usage: run_case.sh <case_id> <php_filename> <trial_number>}"

cd ~/SQLiFuzz-a2
source venv/bin/activate

export HOST_NAME="$(hostname)"
export WUT_NAME=dvwa
export WUT_PORT=8081
export FUZZER_NAME=manual
export IDLE_TIMEOUT=120

trial_dir="~/csec759-advsoft/Assignment2_Failure/raw/${CASE_ID}/run${TRIAL}"
mkdir -p "$trial_dir"
cp configs/config-general.yaml "$trial_dir/"

start_time="$(date -Is)"
echo "case_id=${CASE_ID}" > "$trial_dir/meta.txt"
echo "php_file=${PHP_FILE}" >> "$trial_dir/meta.txt"
echo "trial=${TRIAL}" >> "$trial_dir/meta.txt"
echo "start_time=${start_time}" >> "$trial_dir/meta.txt"

echo "=================================================================="
echo " Case: ${CASE_ID}  |  Target: ${PHP_FILE}  |  Trial: ${TRIAL}"
echo " Open this URL now and submit id=1 once mitmdump is listening:"
echo "   http://localhost:8888/${PHP_FILE}"
echo "=================================================================="

set +e
mitmdump --mode reverse:http://localhost:8081 \
  --listen-port 8888 \
  -s sqlifuzz/mitmproxy_addon.py \
  2>&1 | tee "$trial_dir/terminal.log"
exit_status=$?
set -e

end_time="$(date -Is)"
echo "end_time=${end_time}" >> "$trial_dir/meta.txt"
echo "exit_status=${exit_status}" >> "$trial_dir/meta.txt"

cp shared-data/mysql_proxy_*.log "$trial_dir/" 2>/dev/null || \
  echo "WARNING: no mysql_proxy_dvwa*.log found to preserve" | tee -a "$trial_dir/meta.txt"

echo "Trial complete. Evidence saved to: $trial_dir"
