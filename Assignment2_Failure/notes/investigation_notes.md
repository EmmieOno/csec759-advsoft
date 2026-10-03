9-30-2026
- Started Assignment 2 with fresh runs of the full SQLiFuzz tool and custom crawler.
- Did 3 runs to see if the playwright error would continue to occur.
- The playwright occur did occur.

10-01-2026
- Still on playwright failure, ran more tests as my VM kept losing internet connection.
- Dug deeper into the results and found that the button was not visible because the page was displaying a 502 bad gateway error.
- Tried to investigate further but as I ran more tests more were failing unexpectedly.
- These runs also took 20-30 minutes each and were not a good use of my time.

10-02-2026
- Started to pivot to true/false payloads and investigating the regex/mutation set that SQLiFuzz uses to trigger the SQL syntax error.
- Made different php pages and tested multiple cases.
- Finished control and primary case.
- Observed the failure and stayed on this track.

10-03-2026
- Finished all testing and tested the additional variant.
- Derived results from the raw output.
- Completing the report and fulfilling the github requirements.
