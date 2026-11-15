# Predictions for N1-N4 (written before any fuzzing)

Written: Sun Nov 15, 2026. Ground-truth probes and proxy SQL log excerpts are in `notes/ground_truth_N1.md` through `ground_truth_N4.md`.
These are predictions, not results. If a trial disagrees, add a dated note below the relevant row. Do not edit the original prediction.

Configs:
- **Baseline:** `SQLIFUZZ_BOOLEAN=0`
- **Prototype:** `SQLIFUZZ_BOOLEAN=1`, `SQLIFUZZ_REQUIRE_STRUCTURE=1`
- **Ablation:** `SQLIFUZZ_BOOLEAN=1`, `SQLIFUZZ_REQUIRE_STRUCTURE=0`

## Summary

| Case | Origin | Truth | Baseline | Prototype | Ablation | Confidence |
|---|---|---|---|---|---|---|
| N1 | Hand-written | Safe (reflects input; only `(int)` cast reaches SQL) | No finding | No finding | False `BOOLEAN_PAIR` | Medium-high |
| N2 | Hand-written | Injectable only in quoted context | No finding | No finding | No finding | Medium-high |
| N3 | Real DVWA medium | Injectable (escaped, numeric context) | `syntax_error` | `syntax_error` | `syntax_error` | Medium |
| N4 | Real DVWA impossible | Safe (`is_numeric`, prepared statement, token) | No finding | No finding | No finding | Medium |

Expected detections are out of 3 seeds per cell.

## Reasoning per case

### N1: safe reflected input
- **Baseline:** no SQL error text and no syntax error reaches the detector, because the payload never enters the query.
- **Prototype:** the true and false responses differ (the reflected text changes), but the proxy log shows every query as `user_id = 1`, so the SQL-structure check refuses to confirm.
- **Ablation:** with the structure check off, the stable response difference alone is enough to confirm. This is the false positive the structure check exists to prevent.
- **Evidence:** all three probes returned `ROWS=1`, and the three logged queries read `user_id = 1`.

### N2: quoted context
- **Baseline:** the filter rejects `'`, `*` and every other ordinary mutation, so no query ever reaches the database.
- **Prototype:** the Boolean probes are plain-integer (`1 AND 1=1`) and are rejected by the filter, so they can't reach the quoted context.
- **Ablation:** same probes, same rejection, so no finding.
- **Evidence:** `1 AND 1=1` and `1'` return `INPUT REJECTED`. Quoted payloads reach SQL as `user_id = '1' AND '1'='1'` and `... '1'='2'`, with `ROWS=1` and `ROWS=0`. This documents a known limitation: the prototype does not generate quote-breaking payloads.

### N3: DVWA medium (real)
- **All configs:** `1'` becomes `1\'` after escaping and causes a MySQL syntax error, which is visible in the response (PHP 8.1 prints it as an uncaught `mysqli_sql_exception`). The baseline's syntax-error detector should fire on an early mutation, before the Boolean probe at `x == 5`.
- **Role:** regression check on real software. It shows existing behavior is preserved, not that the new mechanism helps.
- **Uncertainty:** I'm not sure how the detector's pattern list treats PHP's "Uncaught" wrapper, so the smoke test decides this. Also depends on whether the harness can run this page (POST, dropdown, security cookie).

### N4: DVWA impossible (real)
- **All configs:** `is_numeric` rejects `1 AND 1=1`, so the true and false probes return identical responses (both HTTP 200, 4316 bytes). There is no Boolean signal and no SQL error.
- **Role:** real-software safe control.
- **Uncertainty:** depends on whether the harness can handle the single-use `user_token` and the security cookie. If it can't, the trial is an execution failure, not a negative.

## Notes added after smoke test / trials

(Add dated entries here. Format: `YYYY-MM-DD: [case/config] observed X, expected Y, reason Z.`)
