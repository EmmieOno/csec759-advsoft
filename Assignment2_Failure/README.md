## CONTRIBUTION
Emmalee Carpenter (eoc7219) - Solo Contributor

Baseline - https://github.com/websecfuzz/SQLiFuzz (1b7e2ede42af8e2b9d6d1c44358851e9d4616db9)

Dharmaadi, I. P. A., Pham, V.-T., Mohsen, F., & Turkmen, F. (2026, June 30). SQLiFuzz: Uncovering SQL Injection in Any Web Applications. ACM Digital Library. Retrieved September 13, 2026, from https://dl.acm.org/doi/pdf/10.1145/3808149

## SETUP
Follow the setup instructions in ../Assignment1_Baseline/README.md, when cloning SQLiFuzz rename the directory to SQLiFuzz-a2

1. Navigate to /Assignment2_Failure/cases and copy the php files to the DVWA container.
```
sudo docker cp a2_control.php dvwa:/var/www/html/a2_control.php
sudo docker cp a2_filtered.php dvwa:/var/www/html/a2_filtered.php
sudo docker cp a2_filtered_post.php dvwa:/var/www/html/a2_filtered_post.php
```
2. In SQLiFuzz/sqlifuzz/sql_analysis.py, replace both occurrences of:
```
testloc = "/projects/fuzzing/SQLIFuzz/shared-data"
```
with:
```
testloc = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "shared-data"))
```
3. Create the a required output directory in SQLiFuzz/
```
mkdir -p final_result/FR
```
4. Log into DVWA before submitting the test input and set the security level to low
5. Use port 8081 for direct ground-truth checks and 8888 for SQLiFuzz trials.

## QUICK START

1. Before anything, navigate to SQLiFuzz/WUT/dvwa and ensure the host name and wut name variables are set.
```
sudo env WUT_NAME=dvwa HOST_NAME="$(hostname)" docker compose up -d --no-deps --force-recreate dbproxy
```

Two scripts were created after manual runs to help speed up the reproduction process for the future. These were run_case.sh and reset_state.sh. These are located in the scripts/ directory.

2. After setup run ```run_case.sh```
```
./run_case.sh <case_id> <php_filename> <trial_number>
```
For example, ```./run_case.sh primary_case a2_filtered.php 1```

2. Follow the instructions in the terminal.

3. If you want to run another trial, first run ```reset_state.sh```
```
./reset_state.sh
```
4. Repeat for however many trials and cases.
5. Ensure you save the Final Result documentation located in ```final_result/FR/FR-dvwa*.txt```
```
cp SQLiFuzz-a2/final_result/FR/<most recent run FR> Assignment2_Failure/raw/<case_id>/run#
```
6. All other output is located in ```Assignment2_Failure/raw/<case_id>/run#```
   
## EXACT CASE-RUN
For how I ran each case...

1. First I navigated to the SQLiFuzz main directory anhd activated my environment
```
cd ~/SQLiFuzz-a2
source venv/bin/activate
```
2. Then, I set environment variables.
```
export HOST_NAME="$(hostname)"
export WUT_NAME=dvwa
export WUT_PORT=8081
export FUZZER_NAME=manual
export IDLE_TIMEOUT=120
```
3. Next I set what trial I was running and saved the configuration yaml to the trial output directory.
```
trial_dir="Assignment2_Failure/raw/control-run1"
```
*For re-run use ```trial_dir="$HOME/csec759-advsoft/Assignment2_Failure/raw/control/control-run1"```
```
mkdir -p "$trial_dir"
cp configs/config-general.yaml "$trial_dir/"
```
4. Then, I started the proxy
```
mitmdump --mode reverse:http://localhost:8081 \
  --listen-port 8888 \
  -s sqlifuzz/mitmproxy_addon.py \
  2>&1 | tee "$trial_dir/terminal.log"
```
5. Then,
- Open ```http://localhost:8888/a2_<case>.php```
- Enter 1 and submit once.
- Wait for Completed fuzz (remaining: 0).
- Wait for the proxy terminal to exit gracefully.
- After shutdown, preserve the DB logs: ```cp shared-data/mysql_proxy_dvwa*.log "$trial_dir/"```
- And copy the final_result documentation to the trial_dir

## ANALYSIS COMMANDS
1. Navigate to Assignment2_Failure
2. Run this command
```
python3 scripts/derive_results.py --raw-dir raw --out derived/results_table.csv
```

## EXPECTED OUTPUTS
- final_result/FR/FR-dvwa*.txt — summary dict (total_req, sql_req, sql_injection_detected, etc.) plus a ###Matched SQL Injection Detected block listing each endpoint/parameter combination where a DBMS syntax error was triggered by a fuzzed value
- terminal.log - full output of the terminal after running the above commands
- mysql_proxy*.log - database logs
- meta.txt - full metadata of the run (only with the scripts made post-experiment due to run_case script being created after the full experiment)

## RUNTIME ESTIMATE
- A full run should take ~4 minutes.

## KNOWN LIMITATIONS
- POST run 1's reported duration is unreliable and excluded from timing comparisons.
- Cases are constructed examples, not evidence of general real-world detection rates.
- The experiement manually supplies requests and does not evaluate crawler coverage.
- Environment differs from the paper's bare-metal cloud server (Intel Xeon Platinum 8358P, 8 cores, 32GB RAM), this reproduction ran on a VMware Workstation VM (4 vCPUs, 8GB RAM).
