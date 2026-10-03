Decisions I made for Assignment 2:

- At first, I was going to investigate the playwright viewport error I observed in Assignment 1. However, once I started looking into it, I realized the custom crawler had more issues than SQLiFuzz itself. I chose
to go in a different direction to avoid using the crawler as it seemed I would never get accurate results or understand why it was failing. The crawler also takes 20 minutes for each run and the experiment
became too time consuming.
- Instead I chose to go into a direction recommended to me by Professor Liu. She recommended I investigate context-aware/metamorphic testing by "generating paired true/false payloads and checking whether they cause 
meaningful changes in the SQL structure or results". I continued in this direction and it was much faster and easier to troubleshoot than the previous direction.
- I chose to run each control, case, and variant three times to ensure I got accurate results.
- For the additional variant, I asked ChatGPT and Claude for their suggestions and went with a POST variant to see if the weak point in SQLiFuzz was actually just the mutation set or something related to the request.
