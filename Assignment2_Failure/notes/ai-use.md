## AI USE

# ChatGPT Work
- ChatGPT was used for the bulk of this assignment. It was used for troubleshooting and helping pivot to the regex filtering failure baseline.
- ChatGPT gave most of the php files (a2_control.php and a2_filtered.php) and instructions with how to run the cases.

# Summary from ChatGPT Work session:
- Checking the working pipeline: helped identify the DB-log path issue and verify that SQLiFuzz detected both original DVWA SQLi cases when requests were supplied manually.
- Designing the A2 experiment: provided two constructed PHP pages—a vulnerable control and a filtered vulnerable case differing by one filter setting.
- Establishing expected behavior: guided manual true/false Boolean tests to demonstrate vulnerability independently of SQLiFuzz.
- Reviewing results: verified control detection and a completed filtered-case miss, including all 70 fuzzing iterations.
- Troubleshooting evidence collection: inspected logs and source, suggested direct-to-file logging, and identified the missing final_result/FR directory that caused report saving and shutdown to fail.
- Planning repeat trials and documentation: explained randomization, consistent settings, evidence preservation, and how to record incomplete runs and timing anomalies.

# Claude AI
- Claude was used to develop the scripts in scripts/ for smoother reproduction.
- Claude also created the case index file and ground truth documentation template.
- Claude helped explain the additional variant and instructions for executing the process.
