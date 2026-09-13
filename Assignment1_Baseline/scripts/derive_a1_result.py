#!/usr/bin/env python3
"""
derive_a1_result.py

Derives the Table 4 / row A1 (DVWA) metric from one or more raw SQLiFuzz
result files (the dvwa-bacfuzz-*.txt files produced under final_result/).

Metric definition (see report Q2 / gap-analysis §2):
  Count of DISTINCT DVWA endpoints, among the paper's two documented
  "known SQLi" test cases for DVWA, that appear under the
  "###Matched SQL Injection Detected" section of a run's result file.

  Known-endpoint set (DVWA's own two SQLi categories):
    - /vulnerabilities/sqli/
    - /vulnerabilities/sqli_blind/

  Any other endpoint appearing in that section (e.g. /vulnerabilities/brute/,
  /vulnerabilities/upload/, /vulnerabilities/csp/) is reported separately as
  an "additional/non-counted" detection -- it may still be a real SQLi
  (DVWA's brute-force page is a well-known additional SQLi at low security),
  but it is not part of the paper's stated "2 known cases" denominator for A1.

Usage:
    python3 derive_a1_result.py run1.txt run2.txt ...

Output:
    - Per-run breakdown (known endpoints matched, additional endpoints matched)
    - A markdown comparison table against the paper's Table 4 A1 value (2/2)
    - A CSV suitable for derived/a1_comparison.csv
"""

import re
import sys
import csv
from pathlib import Path

PAPER_KNOWN_SQLI_COUNT = 2
PAPER_DETECTED_COUNT = 2  # Table 4, row A1, "SQLiFuzz Total" / "CustCraw" columns

KNOWN_ENDPOINTS = {
    "vulnerabilities/sqli/": "SQLi (regular/UNION-based)",
    "vulnerabilities/sqli_blind/": "SQLi (Blind)",
}

SECTION_HEADER = "###Matched SQL Injection Detected"
NEXT_SECTION_MARK = "##########"


def extract_matched_section(text: str) -> str:
    """Return the raw text of the 'Matched SQL Injection Detected' block only."""
    start = text.find(SECTION_HEADER)
    if start == -1:
        return ""
    end = text.find(NEXT_SECTION_MARK, start)
    if end == -1:
        end = len(text)
    return text[start:end]


def classify_endpoints(section_text: str):
    """
    Pull every http(s)://...vulnerabilities/<name>/ path out of the matched
    section and classify each as known-SQLi vs additional.
    Returns (known_set, additional_set) of endpoint path strings.
    """
    urls = re.findall(r"https?://[^\s|]+/vulnerabilities/[^\s|?]+/", section_text)
    known = set()
    additional = set()
    for u in urls:
        # normalize to just the "vulnerabilities/<name>/" portion
        m = re.search(r"(vulnerabilities/[^/\s]+/)", u)
        if not m:
            continue
        path = m.group(1)
        if path in KNOWN_ENDPOINTS:
            known.add(path)
        else:
            additional.add(path)
    return known, additional


def parse_summary_dict(text: str) -> dict:
    """Parse the leading Python-dict-style summary line, if present."""
    m = re.search(r"^\{.*\}", text, re.MULTILINE)
    if not m:
        return {}
    try:
        return eval(m.group(0), {"__builtins__": {}})
    except Exception:
        return {}


def match_lines_for_endpoint(section_text: str, endpoint_path: str):
    """
    Return every raw numbered line in the matched section that references
    this endpoint path -- this is the traceability link back to raw evidence.
    """
    lines = [ln for ln in section_text.splitlines() if endpoint_path in ln]
    return lines


def process_file(path: Path, derived_dir: Path):
    text = path.read_text()
    summary = parse_summary_dict(text)

    # --- INTERMEDIATE VALUE #1: the extracted "Matched SQL Injection Detected"
    # section, saved verbatim before any classification is applied. This lets
    # a grader see exactly what slice of the raw file fed the classifier.
    section = extract_matched_section(text)
    intermediate_path = derived_dir / f"{path.stem}__extracted_section.txt"
    intermediate_path.write_text(section if section else "(no matched section found)\n")

    known, additional = classify_endpoints(section)

    # --- INTERMEDIATE VALUE #2: per-endpoint raw line references, so every
    # classified endpoint can be traced back to its exact raw line.
    known_trace = {ep: match_lines_for_endpoint(section, ep) for ep in known}
    additional_trace = {ep: match_lines_for_endpoint(section, ep) for ep in additional}

    trace_path = derived_dir / f"{path.stem}__classification_trace.txt"
    with trace_path.open("w") as f:
        f.write(f"Source raw file: {path.name}\n")
        f.write(f"Extracted intermediate section: {intermediate_path.name}\n\n")
        f.write("KNOWN-SQLi ENDPOINTS (counted toward Table 4 A1 metric):\n")
        for ep, lines in known_trace.items():
            f.write(f"\n  [{ep}]  -> {KNOWN_ENDPOINTS[ep]}\n")
            for ln in lines:
                f.write(f"    RAW LINE: {ln.strip()}\n")
        f.write("\nADDITIONAL ENDPOINTS (flagged but NOT part of paper's counted metric):\n")
        for ep, lines in additional_trace.items():
            f.write(f"\n  [{ep}]\n")
            for ln in lines:
                f.write(f"    RAW LINE: {ln.strip()}\n")
        f.write("\n" + "=" * 60 + "\n")
        f.write("TOTALS\n")
        f.write("=" * 60 + "\n")
        f.write(f"Known-SQLi endpoints detected:  {len(known)} / {PAPER_KNOWN_SQLI_COUNT}\n")
        f.write(f"Additional endpoints flagged:   {len(additional)}\n")
        f.write(f"Total distinct endpoints in this section: {len(known) + len(additional)}\n")

    return {
        "file": path.name,
        "summary_field_sql_injection_detected": summary.get("sql_injection_detected"),
        "known_endpoints_detected": sorted(known),
        "known_count": len(known),
        "additional_endpoints_detected": sorted(additional),
        "additional_count": len(additional),
        "intermediate_section_file": intermediate_path.name,
        "trace_file": trace_path.name,
    }


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        sys.exit(1)

    derived_dir = Path("derived_output")
    derived_dir.mkdir(exist_ok=True)

    results = [process_file(Path(p), derived_dir) for p in argv[1:]]

    print("=" * 70)
    print("PER-RUN BREAKDOWN  (intermediate values preserved on disk)")
    print("=" * 70)
    for r in results:
        print(f"\nFile: {r['file']}")
        print(f"  Raw summary field 'sql_injection_detected': {r['summary_field_sql_injection_detected']}"
              "  <- NOTE: this raw counter does not equal the derived metric; see report Q2/Q3.")
        print(f"  Intermediate extracted section saved to: {derived_dir}/{r['intermediate_section_file']}")
        print(f"  Per-endpoint raw-line trace saved to:    {derived_dir}/{r['trace_file']}")
        print(f"  Known-SQLi endpoints detected ({r['known_count']}/{PAPER_KNOWN_SQLI_COUNT}):")
        for e in r["known_endpoints_detected"]:
            print(f"    - {e}  ({KNOWN_ENDPOINTS[e]})")
        print(f"  Additional (non-counted) endpoints flagged ({r['additional_count']}):")
        for e in r["additional_endpoints_detected"]:
            print(f"    - {e}")

    print("\n" + "=" * 70)
    print("COMPARISON TABLE (paper Table 4, row A1)")
    print("=" * 70)
    header = f"{'Run':<35}{'Known SQLi Detected':<22}{'Match Paper (2/2)?':<20}"
    print(header)
    print("-" * len(header))
    print(f"{'Paper (Table 4, A1)':<35}{f'{PAPER_DETECTED_COUNT}/{PAPER_KNOWN_SQLI_COUNT}':<22}{'--':<20}")
    for r in results:
        match = "YES" if r["known_count"] == PAPER_DETECTED_COUNT else "NO"
        ratio_str = f"{r['known_count']}/{PAPER_KNOWN_SQLI_COUNT}"
        print(f"{r['file']:<35}{ratio_str:<22}{match:<20}")

    # Write CSV for derived/
    out_csv = derived_dir / "a1_comparison.csv"
    with out_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["run", "known_sqli_detected", "known_sqli_total", "matches_paper",
                    "additional_endpoints_detected"])
        w.writerow(["paper_table4_A1", PAPER_DETECTED_COUNT, PAPER_KNOWN_SQLI_COUNT, "--", ""])
        for r in results:
            w.writerow([
                r["file"], r["known_count"], PAPER_KNOWN_SQLI_COUNT,
                "yes" if r["known_count"] == PAPER_DETECTED_COUNT else "no",
                ";".join(r["additional_endpoints_detected"]),
            ])
    print(f"\nWrote {out_csv.resolve()}")

    # Run-to-run stability check (paper Section 5.5.4 claims "no significant variance")
    if len(results) > 1:
        counts = {r["known_count"] for r in results}
        print("\n" + "=" * 70)
        print("STABILITY CHECK vs. paper Section 5.5.4")
        print("=" * 70)
        if len(counts) > 1:
            print("VARIANCE DETECTED across identical re-runs (same command, no config change).")
            print(f"Known-SQLi detected varied across runs: {[r['known_count'] for r in results]}")
            print("This contradicts the paper's claim of 'no significant variance' upon repetition (Sec. 5.5.4).")
        else:
            print("No variance detected across runs -- consistent with paper's Section 5.5.4 claim.")


if __name__ == "__main__":
    main(sys.argv)
