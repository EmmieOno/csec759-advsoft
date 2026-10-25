# A3 Environment Changes

- A3 continues from the A2 setup. Earlier environment records are preserved in `A1A2Env/`; current Python and container records are stored alongside this file. Python remains version 3.12.3.

- A3 adds Boolean probing and its integration into SQLiFuzz, configurable seeds and probing toggles, automated browser/trial scripts, results summarization, and per-trial evidence collection. The OR experiment uses a separate probe helper and `a3_variant.php`, whose application logic matches the primary filtered page.

- The database-log-path correction, crawler compatibility fixes, reconstructed crawler helper, container configuration mount, and launch-script fixes were inherited from earlier assignments. The runtime patch preserves these changes relative to the original upstream version.

- The A3 runtime checkout is `~/SQLiFuzz-a3`. DVWA is accessed directly on port 8081 and through the SQLiFuzz reverse proxy on port 8888. The Boolean helper adds no third-party Python dependencies.
