# Select AND and OR probe configurations

The runners select the helper before starting a fresh mitmdump process. The
detector implementation and payloads are unchanged.

- `scripts/run_pilot.sh` copies `scripts/boolean_probe.py` (AND) into the
  runtime checkout as `sqlifuzz/boolean_probe.py`, then runs primary/control.
- `scripts/run_only_variant.sh` copies `src/boolean_probe_OR.py` into that same
  runtime path, then runs only the variant. It restores the packaged AND helper
  on normal exit, an error, Ctrl+C, or a TERM signal. Forced termination such as
  SIGKILL cannot execute a cleanup trap.
- `run_trial.sh` records the active helper SHA-256 in each trial's metadata.

Run one comparison at a time, from the configured SQLiFuzz checkout. The checkout
must already have the integrated `SQLIFuzz.py`, dependencies, target PHP pages,
and database proxy configured. Stop any existing mitmdump before switching
helpers. These scripts replace the runtime helper with the packaged version.

Example (after exporting WUT_NAME, DVWA_USER, and DVWA_PASS):

```bash
export A3_DIR="$HOME/csec759-advsoft/Assignment3_Tool"
cd "$HOME/SQLiFuzz-a3"
bash "$A3_DIR/scripts/run_only_variant.sh"
```

That command creates six new variant trials with seeds 1, 2, and 3. It does not
launch the primary or control trials. Existing run folders are preserved; new
run numbers are chosen by `run_trial.sh`. The summary is regenerated from all
available raw trials. Default output root is
`$HOME/csec759-advsoft/Assignment3_Tool/raw`; set `RAW_DIR` to override it.

To run primary/control with AND selected:

```bash
bash "$A3_DIR/scripts/run_pilot.sh"
```

For a single seed, set `SEEDS_VARIANT=1` before the variant command. The Boolean
toggle remains 0 for baseline and 1 for prototype. Do not change the payload
files manually between runs.

To restore AND manually after a forced termination, from the runtime checkout:

```bash
cp -- "$A3_DIR/scripts/boolean_probe.py" sqlifuzz/boolean_probe.py
```

Verification: inspect each prototype final report for `probe_true` and
`probe_false`. Variant reports should contain OR payloads; primary reports
should contain AND payloads. Restore selection does not modify saved results.
