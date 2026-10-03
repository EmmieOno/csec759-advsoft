Changes from A1:

1. Changed the DB-log directory in sqlifuzz/sql_analysis.py so that SQLiFuzz 
would read from the correct logs.

2. Created 3 new files: a2\_control.php (regex filtering disabled),
a2\_filtered.php (filter enabled for regex), and a2\_filtered_post.php (POST
instead of GET, same as a2_filtered.php)
