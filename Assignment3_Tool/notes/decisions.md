# A3 Technical Decisions

The original decision dates are preserved below. The explanations and evidence references were expanded retrospectively on October 25, 2026; they do not imply that all supporting analysis was recorded on the original decision date.

## October 22, 2026 — Automate trial execution

I used AI assistance to develop scripts for browser interaction, trial execution, and results summarization. This reduced repeated manual steps and made configuration and seed recording consistent.

`scripts/run_pilot.sh` runs the primary and control configurations sequentially, alternating baseline and prototype for each seed. `scripts/run_only_variant.sh` runs the variant comparison separately. `scripts/run_trial.sh` records terminal output, database-log slices, configuration, seed, source hashes, and exit codes.

Evidence: `raw/run_index.txt`, each trial's `meta.txt`, and `derived/results_table.csv`. The recorded trials use seeds 1–3 for each compared configuration.

## October 23, 2026 — Reuse cases for regression and ablation

I reused the matched control as the regression check because syntax-error detection already worked on that case. Both baseline and prototype detected it in all three trials through the syntax-error path.

I reused the primary baseline as the disabled configuration for an ablation of the added Boolean probing path. With `SQLIFUZZ_BOOLEAN=0`, the primary case was detected in 0/3 trials. With probing enabled, it was detected in 3/3 trials.

Evidence: `raw/control/`, `raw/primary_case/`, and their corresponding rows in `derived/results_table.csv`.

## October 23, 2026 — Use OR probes for the additional variant

I initially considered changing the application's query comparison from `=` to `>`. I instead selected a probe-family variant that changes AND to OR while keeping the application logic equivalent to the primary case.

The primary pair is:

- `1 AND 1=1`
- `1 AND 1=0`

The variant pair is:

- `1 OR 1=1`
- `1 OR 1=0`

The OR variant tests whether the detector recognizes a stable difference when both responses contain results. The recorded variant responses contain `ROWS=5` and `ROWS=1`, and all three prototype trials report `BOOLEAN_PAIR`.

Evidence: `src/boolean_probe_OR.py`, `cases/diff_filtered_and_variant.md`, and the final reports and database-log slices under `raw/variant/prototype_run1/` through `prototype_run3/`.

## October 25, 2026 — Retrospective review of the SQL structure requirement

The implementation requires both a stable HTTP response difference and evidence that the payload appears as unquoted SQL. A plausible alternative explanation for differing responses is that a safe application simply reflects the supplied input.

`test_ablation_response_diff_only_gives_false_positive()` isolates this decision using constructed response entries without SQL evidence. With `require_structure=True`, `judge()` returns `inconclusive`. With the requirement disabled, it returns `confirmed`.

The saved test output in `tests/results_of_tests.txt` reports that this test and the other 12 tests passed. This supports retaining the SQL structure requirement.

Code references: `judge()`, `payload_in_code()`, and `mask_literals()` in `scripts/boolean_probe.py`; the focused test is in `scripts/test_boolean_probe.py`.
