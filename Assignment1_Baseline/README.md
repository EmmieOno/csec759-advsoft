## SETUP
1. Clone the SQLiFuzz repo ```git clone https://github.com/websecfuzz/SQLiFuzz.git```
2. Navigate to the directory ```cd SQLiFuzz```
3. Grab the this specific commit ```git checkout 1b7e2ede42af8e2b9d6d1c44358851e9d4616db9```
4. Apply the following code fixes
  - Add ```#!/bin/bash``` as the first line of ```scripts/sqlifuzz.sh``` and ```scripts/bacfuzz.sh```
(missing in the upstream repo, causes the scripts to be misinterpreted by dash on Ubuntu)
  - Copy ```Assignment1_Baseline/scripts/utils.py``` into ```SQLiFuzz/crawler/utils.py``` (reconstructed — 
  this module does not exist anywhere in the upstream repository's commit history)
  - Apply ```Assignment1_Baseline/scripts/general_functions.py``` to restore a stubbed ```read_cov_from_file()``` 
function (the upstream version was removed without updating its caller in Input.py)
  - Apply ```Assignment1_Baseline/scripts/docker-compose.dvwa.yaml``` to ```SQLiFuzz/WUT/dvwa/docker-compose.yml```, adding a 
bind-mounted volumes: entry so DVWA's config.inc.php persists across container recreation 
instead of resetting to config.inc.php.dist
5. Create and activate a Python virtual environment, then install dependencies
```
python3 -m venv venv 
source venv/bin/activate 
pip install -r requirements.txt
```
6. Install system-level dependencies ```sudo apt install python-is-python3```
7. Install Playwright's browser binaries ```sudo -E bash -c "source venv/bin/activate && playwright install"```
8. Configure the ENV variables

## SMOKE TEST COMMANDS
1. Bring up the DVWA containers and initialize the database
```
sudo docker compose --env-file ~/SQLiFuzz-a1/.env -f 
~/SQLiFuzz-a1/WUT/dvwa/docker-compose.yaml up -d
```
2. Set the environment variables
```
env WUT_NAME=dvwa WUT_PORT=8081 HOST_NAME="$(hostname)" FUZZER_NAME=defense IDLE_TIMEOUT=10 
mitmdump --mode reverse:http://localhost:8081 --flow-detail 0 --set flow_storage=memory-limited 
--listen-port 8888 -s sqlifuzz/mitmproxy_addon.py
```
3. In a second terminal, send one request
```COOKIE_HEADER=$(cat login_state/dvwa/Admin.txt)```
4. Then run this command:
```
curl -s -H "$COOKIE_HEADER" "http://localhost:8888/vulnerabilities/sqli/?id=1&Submit=Submit" 
-o /dev/null -w "HTTP status: %{http_code}\n"
```
5. Go back to terminal 1 and observe the final results.
   
## REPRODUCTION COMMANDS
- 

## EXPECTED OUTPUTS
- 

## RUNTIME ESTIMATE
- The smoke test should take between 1-3 minutes.
- The full reproduction takes about 20-23 minutes.

## KNOWN LIMITATIONS
- 
