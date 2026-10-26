## CONTRIBUTION
Emmalee Carpenter (eoc7219) - Solo Contributor

Baseline - https://github.com/websecfuzz/SQLiFuzz (1b7e2ede42af8e2b9d6d1c44358851e9d4616db9)

Dharmaadi, I. P. A., Pham, V.-T., Mohsen, F., & Turkmen, F. (2026, June 30). SQLiFuzz: Uncovering SQL Injection in Any Web Applications. ACM Digital Library. Retrieved September 13, 2026, from https://dl.acm.org/doi/pdf/10.1145/3808149

## SETUP
Follow the setup instructions in ../Assignment2_Failure/README.md, when cloning SQLiFuzz rename the directory to SQLiFuzz-a3.

1. Clone SQLiFuzz and check out commit 1b7e2ede42af8e2b9d6d1c44358851e9d4616db9.
2. Apply patches/sqlifuzz-runtime.patch with ```git apply```.
3. Copy the reconstructed crawler/utils.py into place.
4. Install the AND/OR Boolean helper as sqlifuzz/boolean_probe.py and sqlifuzz/boolean_probe_OR.py.
5. Navigate to SQLiFuzz-a3/WUT/dvwa and set WUT_NAME and HOST_NAME and start the docker containers.
  - ```sudo env WUT_NAME=dvwa HOST_NAME="$(hostname)" docker compose up```
7. Deploy the PHP cases into DVWA.

```
sudo docker cp a2_control.php dvwa:/var/www/html/a2_control.php
sudo docker cp a2_filtered.php dvwa:/var/www/html/a2_filtered.php
sudo docker cp a3_variant.php dvwa:/var/www/html/a3_variant.php
```

## VERSIONS

| Component | Recorded version |
|---|---|
| SQLiFuzz upstream | Commit `1b7e2ede42af8e2b9d6d1c44358851e9d4616db9` |
| A3 modifications | `patches/sqlifuzz-runtime.patch` and the supplied Boolean helpers |
| Python | 3.12.3 |
| mitmproxy | 11.0.2 |
| Playwright | 1.45.1 |
| Playwright Chromium | 127.0.6533.17 |
| Docker | 29.8.0 |
| Docker Compose | v5.5.1 |
| DVWA | Local image `dvwa-dvwa`; image details preserved in `environment/A1A2Env/dvwa-container-inspect.json` |
| Database | Local image `dvwa-db`; image details preserved in `environment/A1A2Env/dvwa-db-container-inspect.json` |

Python is confirmed by `environment/python-version.txt`. The other software versions are recorded in `environment/A1A2Env/interpreter_versions.txt` and `versions.txt`. The preserved dependency list is `environment/A1A2Env/requirements_actual.txt`; current container names and ports are recorded in `environment/containers-current.txt`.

## HARDWARE NEEDS
This reproduction ran on a VMware Workstation VM (4 vCPUs, 8GB RAM).

## UNIT TESTS

The unit tests check the Boolean probing helper's decision logic. They require Python 3 and use only the standard library. DVWA, Docker, mitmproxy, Playwright, and database services do not need to be running.

From the top-level repository directory, run:

```bash
python3 Assignment3_Tool/scripts/test_boolean_probe.py
```

The script imports the adjacent `scripts/boolean_probe.py`, executes 13 test functions, and prints a `PASS` line for each successful test. Expected final output:

```text
13 passed
```

A failed assertion produces a traceback and a nonzero exit code.

The tests cover SQL literal/comment masking, numeric parameter selection, query-shape comparison, response normalization, confirmed findings, missing SQL evidence, quoted payloads, unstable responses, and request failures. A focused ablation test checks the false-positive risk of accepting response differences without SQL structure evidence.

These tests exercise helper functions using constructed inputs. They do not launch the scanner or verify live request replay, database-log association, OR payload generation, or complete application detection. Those behaviors are evaluated separately through the pilot evidence.

## SHORT TEST

This test requires the configured DVWA/database-proxy services, deployed PHP cases, installed dependencies, and patched SQLiFuzz checkout. Export `WUT_NAME`, `HOST_NAME` if required, `DVWA_USER="admin"`, and `DVWA_PASS="password"` first.

From the SQLiFuzz runtime checkout, select the AND helper and run one prototype trial:

```bash
export A3_DIR="$HOME/csec759-advsoft/Assignment3_Tool"
cd "$HOME/SQLiFuzz-a3"

cp -- "$A3_DIR/scripts/boolean_probe.py" sqlifuzz/boolean_probe.py

RAW_DIR="$A3_DIR/raw_smoke" \
  bash "$A3_DIR/scripts/run_trial.sh" \
  a2_filtered.php primary_case prototype 1 1 1
```

The separate `raw_smoke/` directory keeps this check out of the reported pilot results. Each execution creates the next available run folder.

## EXPECTED OUTPUT

The terminal should report a Boolean-pair finding containing:

```text
FOUND SQLi (boolean pair)!
BOOLEAN_PAIR
```

The saved evidence should show:

| Probe | Expected page output |
|---|---|
| `1 AND 1=1` | `ROWS=1` |
| `1 AND 1=0` | `ROWS=0` |

The final report should identify `id` as the affected parameter and include the corresponding SQL queries as unquoted Boolean expressions.

For the first smoke test, output is saved under:

```text
raw_smoke/primary_case/prototype_run1/
```

Check `terminal.log`, `meta.txt`, and the reports in `final_result/`. Both `mitmdump_exit` and `driver_exit` should be `0`.

Allow approximately 2–5 minutes on the pilot environment. The runtime includes the 120-second idle shutdown delay; the outer timeout is 900 seconds.

## REPRODUCE PILOT
Complete the setup instructions and export WUT_NAME, HOST_NAME if required, DVWA_USER, and DVWA_PASS first. Stop any existing mitmdump process.

Run these commands from the configured SQLiFuzz checkout:

```
export A3_DIR="$HOME/csec759-advsoft/Assignment3_Tool"
cd "$HOME/SQLiFuzz-a3"

# Use a new output directory to preserve the submitted evidence.
export RAW_DIR="$A3_DIR/raw_reproduction"

# Twelve primary/control trials using AND probes.
bash "$A3_DIR/scripts/run_pilot.sh"

# Six variant trials using OR probes.
bash "$A3_DIR/scripts/run_only_variant.sh"
```

Both runners use seeds 1, 2, and 3 and alternate baseline/prototype configurations. The variant runner selects the OR helper automatically and restores AND afterward.

Raw outputs are saved under raw_reproduction/. Each runner updates derived/results_table.csv beside that directory, so use the following command after both finish to write a separately named reproduction table:

python3 "$A3_DIR/scripts/summarize_trials.py" \
  "$RAW_DIR" \
  "$A3_DIR/derived/results_table_fresh.csv"

Use a new RAW_DIR for each complete reproduction campaign; otherwise additional trials accumulate in the same directory.

## EXPECTED RUNTIME
The expected runtime is between 3 and 5 minutes per trial. The original 18 trials recorded approximately 51 minutes of tool runtime. Allow about one hour for a fresh campaign on comparable hardware, with additional time for setup. Individual trials have a 900-second outer timeout.
