# N3 ground truth (DVWA medium), Sun Nov 15 02:35:19 PM EST 2026
## id=1
		<pre>ID: 1<br />First name: admin<br />Surname: admin</pre>
	</div>

	<h2>More Information</h2>
## id=1'
## id=1 AND 1=1
		<pre>ID: 1 AND 1=1<br />First name: admin<br />Surname: admin</pre>
	</div>

	<h2>More Information</h2>
## id=1 AND 1=0
## id=1' (rerun without <pre> filter, Sun Nov 15 03:06:17 PM EST 2026)
HTTP/1.1 200 OK
<b>Fatal error</b>:  Uncaught mysqli_sql_exception: You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '\'' at line 1 in /var/www/html/vulnerabilities/sqli/source/medium.php:12
## N3 summary: id=1' returns HTTP 200 with a PHP fatal error containing the MySQL syntax error text (medium.php:12). The empty result in the first pass came from grepping only for <pre>.

2026-11-15 19:35:44,063037 [INFO] [('172.18.0.5', 56068)] ### SELECT first_name, last_name FROM users WHERE user_id = 1; *#*#Result Set
2026-11-15 19:35:44,064404 [INFO] [('172.18.0.5', 56068)] ### SELECT COUNT(*) FROM users; *#*#Result Set
2026-11-15 19:36:41,717329 [INFO] [('172.18.0.5', 42126)] ### SELECT first_name, last_name FROM users WHERE user_id = 1\'; *#*#ERROR 1064: 2000You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '\'' at line 1
2026-11-15 19:37:06,841976 [INFO] [('172.18.0.5', 51230)] ### SELECT first_name, last_name FROM users WHERE user_id = 1 AND 1=1; *#*#Result Set
2026-11-15 19:37:06,843243 [INFO] [('172.18.0.5', 51230)] ### SELECT COUNT(*) FROM users; *#*#Result Set
2026-11-15 19:37:28,473221 [INFO] [('172.18.0.5', 41120)] ### SELECT first_name, last_name FROM users WHERE user_id = 1 AND 1=0; *#*#Result Set
2026-11-15 19:37:28,474249 [INFO] [('172.18.0.5', 41120)] ### SELECT COUNT(*) FROM users; *#*#Result Set
2026-11-15 19:38:40,692788 [INFO] [('172.18.0.5', 39714)] ### USE db *#*#OK
2026-11-15 19:41:53,665911 [INFO] [('172.18.0.5', 42014)] ### USE db *#*#OK
2026-11-15 19:41:59,892327 [INFO] [('172.18.0.5', 51502)] ### SELECT table_schema, table_name, create_time
				FROM information_schema.tables
				WHERE table_schema='db' AND table_name='users'
				LIMIT 1 *#*#Result Set
2026-11-15 19:41:59,896990 [INFO] [('172.18.0.5', 51502)] ### SELECT * FROM `users` WHERE user='admin' AND password='5f4dcc3b5aa765d61d8327deb882cf99'; *#*#Result Set
2026-11-15 20:06:17,628905 [INFO] [('172.18.0.5', 60212)] ### SELECT first_name, last_name FROM users WHERE user_id = 1\'; *#*#ERROR 1064: 2000You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '\'' at line 1
