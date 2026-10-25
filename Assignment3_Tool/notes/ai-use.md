# Contributions and AI Use

## Author contribution

Emmalee Carpenter (eoc7219) was a solo contributor. I configured and operated the local DVWA/SQLiFuzz environment, ran the baseline and prototype trials, collected raw evidence, and performed the manual OR ground-truth checks.

I selected the final OR variant, reviewed the results, and organized the source files, environment records, and supporting evidence. The primary and control cases and earlier compatibility fixes were reused from A2 and documented as inherited work.

## AI assistance

I used **ChatGPT Work and Claude** for implementation and scripting assistance.

- Claude helped develop and troubleshoot the experiment scripts. ChatGPT helped with Boolean-probing implementation suggestions, experiment design, interpretation of results, and repository reproducibility checks. Script-related assistance covered browser automation, trial execution, output organization, and results summarization.

- ChatGPT also helped implement automatic AND/OR helper selection in the trial runners through a GitHub pull request. It assisted with drafting and revising the README, decision notes, budget and metric definitions, ground-truth explanation, and report text.

- AI-assisted components include the Boolean probing helper and supporting scripts under `scripts/`, the OR helper under `src/`, and associated documentation. These components should not be interpreted as entirely unaided code or writing.

## Verification

I ran the integrated prototype against the local DVWA cases and preserved the commands, configurations, seeds, logs, and results under `raw/` and `derived/`.

The saved unit-test output reports 13 passing tests. These tests check helper logic using constructed inputs; they do not replace the live pilot experiments. I also manually checked the OR inputs directly against DVWA, independently of the detector's verdict.

ChatGPT performed additional code review, summary-table reproduction, and simulated runner checks.

## Upstream and reused work

The original SQLiFuzz artifact provides the request handling, proxy infrastructure, mutation framework, and syntax-error detection. DVWA provides the target environment. Earlier setup fixes and A2 cases are reused with attribution.

The A3 extension adds paired Boolean probing, SQL structure checks, integration controls, and supporting evaluation automation. The supplied patch identifies tracked changes relative to the recorded upstream commit.
