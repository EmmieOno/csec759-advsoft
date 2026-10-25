## CONTRIBUTION
Emmalee Carpenter (eoc7219) - Solo Contributor

Baseline - https://github.com/websecfuzz/SQLiFuzz (1b7e2ede42af8e2b9d6d1c44358851e9d4616db9)

Dharmaadi, I. P. A., Pham, V.-T., Mohsen, F., & Turkmen, F. (2026, June 30). SQLiFuzz: Uncovering SQL Injection in Any Web Applications. ACM Digital Library. Retrieved September 13, 2026, from https://dl.acm.org/doi/pdf/10.1145/3808149

## SETUP

## VERSIONS

## HARDWARE NEEDS

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

## EXPECTED OUTPUT

## REPRODUCE PILOT

## EXPECTED RUNTIME
