## AI USE

ChatGPT Work
- ChatGPT was used for determining feasibility of the project. I asked ChatGPT if the project was feasible
given the paper I chose and the assignment guidelines. I also asked for a walk-through of the workflow and
what steps I need to take in order to complete the assignment.
- One suggestion I verified was how to run the smoke test. I cross-verified with Claude to ensure the
commands were correct. I also ran the smoke test 4-5 times to verify that the commands were correct.
- One suggestion I rejected was troubleshooting the DB proxy. I didn't believe it was giving me valuable
solutions after I ran the first command and it did not work. Therefore, I asked ChatGPT to start the whole
process over.

Claude AI
- Claude AI was used for reproduction instructions and troubleshooting. I used Claude to understand the
paper author's code and how to run it correctly. I also used Claude to help me generate code that needed
to be added to the paper author's pipeline in order to run the tool (general_functions.py) and (utils.py).
In addition, Claude generated code for derivation of raw output and helped explain report questions.
- One suggestion I verified was why run1 did not detect both SQLi vulnerabilities. I verified this by giving
Claude the exact output logs and going into my VM to observe the logs myself. At first, it gave an answer I
did not agree with so giving the logs helped me understand the true answer based on my real data.
- One suggestion I rejected was the first code for derivation. The first suggestion they gave me for deriving
the result was a single grep command. I felt it didn't produce anything of value and asked for a more 
in-depth derivation script.

