#!/usr/bin/env python3
"""
derive_results.py

Builds the A2 results table required by the assignment ("case ID, expected
behavior and basis, observed behavior, run/budget information,
interpretation, and paths to raw evidence") from the evidence/ folder
produced by scripts/run_case.sh.

Usage:
    python3 derive_results.py --evidence-dir evidence --out derived/results_table.csv

Detection logic: scans each trial's terminal.log for SQLiFuzz's known
detection markers. If none are found, the trial is recorded as NOT DETECTED.
This mirrors the same "search for the matched-detection section" approach
used in the A1 derive_a1_result.py script, generalized to a single
binary detected/not-detected outcome per case (since each A2 case targets
one specific parameter/vulnerability, not a set of known endpoints).
"""

import argparse
import csv
import re
from pathlib import Path

NOT_DETECTED_LITERAL = "No SQL Injection Detected."


def find_fr_file(run_dir: Path):
    matches = list(run_dir.glob("FR-*.txt"))
    return matches[0] if matches else None


def parse_fr_file(fr_path: Path):
    """
    Parses an FR-*.txt result file: a leading Python-dict-style summary line,
    followed by a '###Matched SQL Injection Detected' section listing either
    'No SQL Injection Detected.' or one or more numbered match lines.
    """
    text = fr_path.read_text(errors="replace")

    summary = {}
    m = re.search(r"^\{.*\}", text, re.MULTILINE)
    if m:
        try:
            summary = eval(m.group(0), {"__builtins__": {}})
        except Exception:
            summary = {}

    section_start = text.find("###Matched SQL Injection Detected")
    section_end = text.find("####", section_start + 1) if section_start != -1 else -1
    section = text[section_start:section_end] if section_start != -1 else ""

    if NOT_DETECTED_LITERAL in section:
        detected = False
        matched_lines = []
    else:
        matched_lines = [ln.strip() for ln in section.splitlines()
                          if re.match(r"^\d+\.\s", ln.strip())]
        detected = len(matched_lines) > 0

    return detected, summary, matched_lines

# Fill in / edit this table to match your actual case definitions.
# "expected" and "basis" should summarize your independently-established
# ground truth (see Q2's requirement that expectation not come from the
# baseline's own output).
CASE_DEFINITIONS = {
    "control": {
        "expected": "SQLi detected (filter off; apostrophe reaches query, causes syntax error)",
        "basis": "Source inspection of a2_control.php: $filterEnabled=false, no character restriction before query",
    },
    "primary_case": {
        "expected": "Page IS exploitable (boolean-blind, id=1 AND 1=1 vs id=1 AND 1=0); "
                    "SQLiFuzz is expected to MISS it due to the filter blocking its mutation set",
        "basis": "Manual ground-truth check: id=1 AND 1=1 -> ROWS=1, id=1 AND 1=0 -> ROWS=0 "
                 "(see notes/ground_truth_boolean_check.md), established independently of SQLiFuzz",
    },
    "post-variant": {
        "expected": "Same underlying vulnerability and filter logic as primary_case; method changed to POST only",
        "basis": "Identical source logic to a2_filtered.php except $_GET -> $_POST and form method; "
                 "see cases/difference_of_filtered_and_filtered_post.txt",
    },
    "additional_variant": {
        "expected": "Same underlying vulnerability and filter logic as primary_case; method changed to POST only",
        "basis": "Identical source logic to a2_filtered.php except $_GET -> $_POST and form method; "
                 "see cases/difference_of_filtered_and_filtered_post.txt",
    },
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", default="raw",
                     help="Root containing <case_id>/<run_name>/FR-*.txt, e.g. raw/control/control-run1/")
    ap.add_argument("--out", default="derived/results_table.csv")
    args = ap.parse_args()

    raw_root = Path(args.raw_dir)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Normalize two possible layouts under raw/:
    #   nested:  raw/<case_id>/<run_name>/FR-*.txt   (e.g. raw/control/control-run1/)
    #   flat:    raw/<run_name>/FR-*.txt             (e.g. raw/post-variant-run1/)
    # For flat layout, case_id is inferred by stripping a trailing "-runN" or
    # "runN" suffix from the folder name (post-variant-run1 -> post-variant).
    run_entries = []  # list of (case_id, run_name, run_dir)
    for entry in sorted(raw_root.glob("*")):
        if not entry.is_dir():
            continue
        if find_fr_file(entry) is not None:
            # Flat layout: this directory IS a run.
            inferred_case_id = re.sub(r"[-_]?run\d+$", "", entry.name, flags=re.IGNORECASE)
            run_entries.append((inferred_case_id, entry.name, entry))
        else:
            # Nested layout: this directory's children are runs.
            case_id = entry.name
            for run_dir in sorted(entry.glob("*")):
                if run_dir.is_dir() and find_fr_file(run_dir) is not None:
                    run_entries.append((case_id, run_dir.name, run_dir))

    rows = []
    for case_id, run_name, run_dir in run_entries:
        case_def = CASE_DEFINITIONS.get(case_id, {"expected": "[FILL IN]", "basis": "[FILL IN]"})
        fr_file = find_fr_file(run_dir)

        if fr_file is None:
            observed = "NO FR RESULT FILE FOUND"
            summary = {}
            matched_lines = []
        else:
            detected, summary, matched_lines = parse_fr_file(fr_file)
            observed = "DETECTED" if detected else "NOT DETECTED"

        rows.append({
            "case_id": case_id,
            "run": run_name,
            "expected_behavior": case_def["expected"],
            "basis_for_expectation": case_def["basis"],
            "observed_behavior": observed,
            "sql_injection_detected_field": summary.get("sql_injection_detected", ""),
            "fuzzed_req": summary.get("fuzzed_req", ""),
            "running_time": summary.get("running_time", ""),
            "matched_lines": " || ".join(matched_lines),
            "raw_evidence_path": str(run_dir),
        })

    with out_path.open("w", newline="") as f:
        fieldnames = ["case_id", "run", "expected_behavior", "basis_for_expectation",
                      "observed_behavior", "sql_injection_detected_field", "fuzzed_req",
                      "running_time", "matched_lines", "raw_evidence_path"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {out_path}")
    print("\nSummary by case:")
    by_case = {}
    for r in rows:
        by_case.setdefault(r["case_id"], []).append(r["observed_behavior"])
    for case_id, outcomes in by_case.items():
        detected_count = sum(1 for o in outcomes if o == "DETECTED")
        print(f"  {case_id}: {detected_count}/{len(outcomes)} runs detected")


if __name__ == "__main__":
    main()
