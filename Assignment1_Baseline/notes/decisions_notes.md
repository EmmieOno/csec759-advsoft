Decisions I made throughout the reproduction...

1. The paper never names the two specific known SQLi cases, therefore I decided to interpret that
as DVWA /vulnerabilities/sqli/ and /vulnerabilities/sqli_blind/.
2. I decided to run a second identical reproduction after the first reproduction gave a result of
1/2 detected SQLi cases. I thought I had done something wrong and wanted to see if the results 
would differ. That is why there is both run1 and run2, in addition to the prediction run (run3)
3. At first, I was going to frame the debugging decision around the run1 detection miss but then
decided to use the utils.py/read_cov_from_file scenario instead because I had to actually change
things to make the tool run. In the run1 detection miss, I didn't have to change anything to see 
it actually detect what it needed to.
4. I decided to classify the outcome as approximately reproduced rather than reproduced because I
thought with the amount of editing and adding of files I needed to do, it didn't feel like a true
reproduction. Also the first run was not fully reproduced and that situation still has the 
possibility of happening.
5. I chose to make the security-level toggle as my controlled variation because I wanted to see 
if DVWA would be more secure against SQLiFuzz.
