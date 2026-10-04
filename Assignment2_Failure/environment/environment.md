Changes from A1:

1. Changed the DB-log directory in sqlifuzz/sql_analysis.py so that SQLiFuzz 
would read from the correct logs.

2. Created 3 new files:
- a2\_control.php (regex filtering disabled),
- a2\_filtered.php (filter enabled for regex),
- and a2\_filtered_post.php (POST instead of GET, same as a2_filtered.php)

Note about timezones: The saved terminal and database logs show a four-hour timestamp offset. For example, filtered run 2’s terminal records the starting request at October 2, 17:20:30, while the associated database entry is timestamped 21:20:30. This is consistent with Eastern Daylight Time versus UTC. Database logs are cumulative snapshots and include earlier runs. Match entries using the database timestamp quoted in the terminal log.
