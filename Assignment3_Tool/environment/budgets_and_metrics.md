# Budgets and Metrics

## Budgets and stopping rules

- Each baseline/prototype configuration was run three times using seeds **1, 2, and 3**.
- All trials used a **900-second outer timeout**; `TRIAL_TIMEOUT` was not overridden.
- The fuzzer provides **70 iteration slots per eligible captured request** and stops early when injection is detected.
- The prototype tries Boolean probing after six ordinary mutations. Each true/false pair is repeated twice, producing **four Boolean requests per tested numeric parameter**. These replace later mutation slots.
- The proxy shuts down after **120 seconds of inactivity** when no fuzzing tasks remain.
- Baseline disables Boolean probing; prototype enables it with SQL structure checks. Primary/control use AND probes; the variant uses OR probes.

## Metrics

| Metric | Definition |
|---|---|
| Detection frequency | Completed trials reporting injection divided by completed trials for that configuration, such as `3/3`. Repeated probes are not separate detections. |
| `fuzzed_req` | Completed fetch calls through the shared request sender, including Boolean replays. The prototype’s **10 requests include six mutations plus four Boolean requests**. Browser login/navigation traffic is excluded. |
| `processing_time_total_s` | Sum of recorded fetch durations. Excludes SQL-log waits, other analysis, and idle shutdown. |
| `total_run_time_s` | Tool start-to-finish elapsed time from the terminal log, including idle shutdown. It is not time to first detection. |

All 18 pilot trials have browser and proxy exit codes of zero. Raw logs and metadata are retained. A baseline miss means no injection was detected within the tested budget; it does not establish that the application is safe.

Regression reuses the control trials, and the Boolean-probing ablation reuses the primary baseline/prototype comparison. These do not count as additional trials.
