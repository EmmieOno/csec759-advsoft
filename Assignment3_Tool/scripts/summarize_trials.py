"""Build derived/results_table.csv from <raw>/<group>/run<N>/ trial folders
(default raw = ~/csec759-advsoft/Assignment3_Tool/raw; config and seed come from each run's meta.txt).

Per trial (one row): detected?, which path found it (boolean_pair / syntax_error / none),
fuzzed_req (requests sent by the fuzzer), processing_time_total (sum of request durations,
i.e. active fuzzing time), total_run_time_s (whole run), and run status.
Definitions (state these in the report):
  detected   = the final report does NOT contain "No SQL Injection Detected"
  fuzzed_req = SQLiCollection statistics value 'fuzzed_req' (all fuzzing requests, all parameters)
Usage: python3 scripts/summarize_trials.py [raw_dir] [out_csv]
"""
import collections
import csv
import glob
import os
import re
import sys

DEFAULT_RAW = os.environ.get("RAW_DIR", os.path.expanduser("~/csec759-advsoft/Assignment3_Tool/raw"))
raw_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RAW
out_csv = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(raw_dir.rstrip("/")), "derived", "results_table.csv")


def parse_meta(path):
    meta = {}
    with open(path, errors="replace") as f:
        for line in f:
            if "=" in line:
                k, v = line.rstrip("\n").split("=", 1)
                meta[k] = v
    return meta


def last_number(pattern, text, cast=float):
    hits = re.findall(pattern, text)
    return cast(hits[-1]) if hits else None


def hms_to_seconds(text):
    m = re.findall(r"Total run time: (\d+):(\d+):([\d.]+)", text)
    if not m:
        return None
    h, mi, s = m[-1]
    return int(h) * 3600 + int(mi) * 60 + float(s)


rows = []
for meta_path in sorted(glob.glob(os.path.join(raw_dir, "*", "*", "meta.txt"))):
    d = os.path.dirname(meta_path)
    meta = parse_meta(meta_path)
    log_path = os.path.join(d, "terminal.log")
    log = open(log_path, errors="replace").read() if os.path.exists(log_path) else ""

    if "FINAL RESULT" not in log:
        status, detected, path = "no_final_result", "NA", "NA"
    else:
        detected_bool = "No SQL Injection Detected" not in log
        detected = int(detected_bool)
        if not detected_bool:
            path = "none"
        elif "BOOLEAN_PAIR" in log:
            path = "boolean_pair"
        else:
            path = "syntax_error"
        status = "timeout" if meta.get("mitmdump_exit") == "124" else "ok"

    rows.append({
        "trial": os.path.relpath(d, raw_dir),
        "group": meta.get("group"), "config": meta.get("config"), "seed": meta.get("seed"),
        "detected": detected, "detection_path": path,
        "fuzzed_req": last_number(r"'fuzzed_req': (\d+)", log, int),
        "processing_time_total_s": last_number(r"'processing_time_total': ([\d.]+)", log),
        "total_run_time_s": hms_to_seconds(log),
        "status": status,
        "seed_applied": meta.get("seed_line_in_terminal_log"),
    })

if not rows:
    sys.exit(f"no trials found under {raw_dir}/*/*/meta.txt")

os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
with open(out_csv, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

groups = collections.defaultdict(list)
for r in rows:
    groups[(r["group"], r["config"])].append(r)


def mean(vals):
    vals = [v for v in vals if v is not None]
    return f"{sum(vals) / len(vals):.1f}" if vals else "NA"


print(f"\nwrote {out_csv} ({len(rows)} trials)\n")
print(f"{'group':<14}{'config':<11}{'runs':<6}{'detected':<10}{'mean fuzzed_req':<17}{'mean total s':<14}notes")
for (g, c), rs in sorted(groups.items()):
    ok = [r for r in rs if r["status"] == "ok"]
    det = sum(1 for r in ok if r["detected"] == 1)
    notes = []
    bad = len(rs) - len(ok)
    if bad:
        notes.append(f"{bad} non-ok run(s) excluded from counts; see CSV")
    if any(r["seed_applied"] != "yes" for r in rs):
        notes.append("seed line missing in some logs")
    print(f"{g:<14}{c:<11}{len(rs):<6}{f'{det}/{len(ok)}':<10}"
          f"{mean([r['fuzzed_req'] for r in ok]):<17}{mean([r['total_run_time_s'] for r in ok]):<14}{'; '.join(notes)}")
