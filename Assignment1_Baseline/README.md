## SETUP
1. Clone the SQLiFuzz repo ```git clone https://github.com/websecfuzz/SQLiFuzz.git```
2. Navigate to the directory ```cd SQLiFuzz```
3. Grab the this specific commit ```git checkout 1b7e2ede42af8e2b9d6d1c44358851e9d4616db9```
4. Apply the following code fixes
  - Add ```#!/bin/bash``` as the first line of scripts/sqlifuzz.sh and scripts/bacfuzz.sh
(missing in the upstream repo, causes the scripts to be misinterpreted by dash on Ubuntu)
  - Copy Assignment1_Baseline/scripts/utils.py into SQLiFuzz/crawler/utils.py (reconstructed — 
  this module does not exist anywhere in the upstream repository's commit history)
  - Apply Assignment1_Baseline/scripts/general_functions.py to restore a stubbed ```read_cov_from_file()``` 
function (the upstream version was removed without updating its caller in Input.py)
  - Apply Assignment1_Baseline/scripts/docker-compose.dvwa.yaml to SQLiFuzz/WUT/dvwa/docker-compose.yml, adding a bind-mounted volumes: entry so DVWA's config.inc.php persists across container recreation instead of resetting to config.inc.php.dist
5. Create and activate a Python virtual environment, then install dependencies
```
python3 -m venv venv 
source venv/bin/activate 
pip install -r requirements.txt
```
6. Install system-level dependencies ```sudo apt install python-is-python3```
7. Install Playwright's browser binaries ```sudo -E bash -c "source venv/bin/activate && playwright install"```
8. Ensure .env from this repo has been downloaded and places in /SQLiFuzz

## SMOKE TEST COMMANDS
1. Bring up the DVWA containers and initialize the database
```
sudo docker compose --env-file ~/SQLiFuzz-a1/.env -f 
~/SQLiFuzz-a1/WUT/dvwa/docker-compose.yaml up -d
```
2. Set the environment variables
```
env WUT_NAME=dvwa WUT_PORT=8081 HOST_NAME="$(hostname)" FUZZER_NAME=defense IDLE_TIMEOUT=10 
mitmdump --mode reverse:http://localhost:8081 --flow-detail 0 --set flow_storage=memory-limited 
--listen-port 8888 -s sqlifuzz/mitmproxy_addon.py
```
3. In a second terminal, send one request
```COOKIE_HEADER=$(cat login_state/dvwa/Admin.txt)```
4. Then run this command:
```
curl -s -H "$COOKIE_HEADER" "http://localhost:8888/vulnerabilities/sqli/?id=1&Submit=Submit" 
-o /dev/null -w "HTTP status: %{http_code}\n"
```
5. Go back to the first terminal and observe the final results.
   
## REPRODUCTION COMMANDS
1. Navigate to the SQLiFuzz/scripts directory
2. Run the command
```
sudo -E bash -c "source ../venv/bin/activate && ./sqlifuzz.sh dvwa 8081 / openapi.json bacfuzz"
```
3. To reproduce the predicted run, edit auto_login/dvwa.py and change the values from "low" to "medium"
4. Derive the output using this command
```
python3 scripts/derive_a1_result.py raw/<Run>_Reproduction/dvwa-bacfuzz-*.txt
```
## EXPECTED OUTPUTS
- final_result/dvwa-bacfuzz-<hostname>-<timestamp>.txt — summary dict (total_req, sql_req, sql_injection_detected, etc.) plus a ###Matched SQL Injection Detected block listing each endpoint/parameter combination where a DBMS syntax error was triggered by a fuzzed value
- result/Admin_<timestamp>.txt — list of crawled DVWA page paths
- result/[REQ]Admin_<timestamp>.txt — captured HTTP requests
- log/*.log and BACFUZZ-*.log — detailed per-request analysis and crawler narration
- On a successful reproduction run, the derivation script (scripts/derive_a1_result.py) should report 2 out of 2 known DVWA SQLi endpoints detected (/vulnerabilities/sqli/ and /vulnerabilities/sqli_blind/), matching Table 4, row A1 of the paper

## RUNTIME ESTIMATE
- The smoke test should take between 1-3 minutes.
- The full reproduction takes about 20-23 minutes.

## KNOWN LIMITATIONS
- Coverage-guided prioritization is disabled. The upstream repository is missing the crawler/utils.py module that the original read_cov_from_file() depended on. The reconstructed stub always returns (0, 0), meaning the feedback-driven request/parameter prioritization described in the paper's Section 3.4.4 does not function in this reproduction. The core SQL injection detection oracle is unaffected and operates independently of this component.
- clean_docker.sh is referenced but does not exist in the scripts/ directory (called from check_mitm.sh). This did not block the rest of the pipeline and was not investigated further.
- Run-to-run nondeterminism in crawler form submission. Two identical low-security runs produced different known-SQLi detection counts (1/2 vs. 2/2). Root cause: a Playwright viewport-visibility failure caused a Submit-button click to silently fail in one run, preventing any request from being generated for /vulnerabilities/sqli/. Full evidence trail in derived/run1_low_classification_trace.txt and the corresponding raw crawler logs. This is a limitation of the crawler's DOM-interaction reliability, not of SQLiFuzz's detection logic.
- Environment differs from the paper's bare-metal cloud server (Intel Xeon Platinum 8358P, 8 cores, 32GB RAM), this reproduction ran on a VMware Workstation VM (4 vCPUs, 8GB RAM).
