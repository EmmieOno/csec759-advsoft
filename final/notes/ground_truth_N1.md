# N1 ground truth, Sun Nov 15 02:29:56 PM EST 2026
## id=1
<pre>You searched for: 1</pre><pre>ROWS=1</pre></body>
## id=1 AND 1=0
<pre>You searched for: 1 AND 1=0</pre><pre>ROWS=1</pre></body>
## id=1 AND 1=1
<pre>You searched for: 1 AND 1=1</pre><pre>ROWS=1</pre></body>

2026-11-15 19:30:32,878093 [INFO] [('172.18.0.5', 43292)] ### USE db *#*#OK
2026-11-15 19:30:32,895128 [INFO] [('172.18.0.5', 43292)] ### SELECT first_name, last_name FROM users WHERE user_id = 1 *#*#Result Set
2026-11-15 19:30:46,254930 [INFO] [('172.18.0.5', 53888)] ### USE db *#*#OK
2026-11-15 19:30:46,259548 [INFO] [('172.18.0.5', 53888)] ### SELECT first_name, last_name FROM users WHERE user_id = 1 *#*#Result Set
2026-11-15 19:31:31,485332 [INFO] [('172.18.0.5', 39940)] ### USE db *#*#OK
2026-11-15 19:31:31,489975 [INFO] [('172.18.0.5', 39940)] ### SELECT first_name, last_name FROM users WHERE user_id = 1 *#*#Result Set

## N1 SQL seen by the proxy
Source: mysql_proxy_dvwaemmalee-VMware-Virtual-Platform.log. Timestamps are UTC (notes headers are EST).
The three lines below were matched by timestamp to the three N1 probes, in order.
2026-11-15 19:30:32,895128 [INFO] [('172.18.0.5', 43292)] ### SELECT first_name, last_name FROM users WHERE user_id = 1 *#*#Result Set
2026-11-15 19:30:46,259548 [INFO] [('172.18.0.5', 53888)] ### SELECT first_name, last_name FROM users WHERE user_id = 1 *#*#Result Set
2026-11-15 19:31:31,489975 [INFO] [('172.18.0.5', 39940)] ### SELECT first_name, last_name FROM users WHERE user_id = 1 *#*#Result Set
Observation: all three queries read "user_id = 1". None contain AND/OR.
