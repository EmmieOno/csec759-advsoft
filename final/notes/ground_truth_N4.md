# N4 ground truth (DVWA impossible), Sun Nov 15 02:45:20 PM EST 2026
## id=1
		<pre>ID: 1<br />First name: admin<br />Surname: admin</pre>
	</div>

	<h2>More Information</h2>
## id=1 AND 1=1
## id=1 AND 1=0
## bad-token check: HTTP 302 (token validation is active)
## RECHECK id=1 AND 1=0 (fresh token)
HTTP 200, 4316 bytes
## RECHECK id=1 AND 1=1 (fresh token)
HTTP 200, 4316 bytes
## RECHECK id=1 (fresh token)
HTTP 200, 4375 bytes
## N4 summary: 1 AND 1=1 and 1 AND 1=0 both HTTP 200, 4316 bytes (identical); id=1 is 4375 bytes (contains user row). Earlier empty greps reused single-use tokens and are superseded by the RECHECK results.
