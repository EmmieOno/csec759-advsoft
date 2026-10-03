## CONTRIBUTION
Emmalee Carpenter (eoc7219) - Solo Contributor

Baseline - https://github.com/websecfuzz/SQLiFuzz (1b7e2ede42af8e2b9d6d1c44358851e9d4616db9)

## SETUP
Follow the setup instructions in ../Assignment1_Baseline/README.md

## QUICK START

   
## EXACT CASE-RUN


## ANALYSIS COMMANDS

## EXPECTED OUTPUTS
- final_result/FR/FR-dvwa*.txt — summary dict (total_req, sql_req, sql_injection_detected, etc.) plus a ###Matched SQL Injection Detected block listing each endpoint/parameter combination where a DBMS syntax error was triggered by a fuzzed value
- terminal.log - full output of the terminal after running the above commands
- mysql_proxy*.log - database logs

## RUNTIME ESTIMATE
- A full run should take ~4 minutes.

## KNOWN LIMITATIONS
- Environment differs from the paper's bare-metal cloud server (Intel Xeon Platinum 8358P, 8 cores, 32GB RAM), this reproduction ran on a VMware Workstation VM (4 vCPUs, 8GB RAM).
