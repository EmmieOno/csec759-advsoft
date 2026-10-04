# Ground Truth: Boolean-Blind Injection on the Filtered Page

This establishes the expected behavior of `a2_filtered.php` **independently
of SQLiFuzz**.

## Method

Manual HTTP requests sent directly to DVWA (port 8081), bypassing the
SQLiFuzz proxy (port 8888) entirely, no SQLiFuzz process was running
during this check.

## Test 1 — true condition
```
Request: id = 1 AND 1=1
URL: http://localhost:8081/a2_filtered.php?id=1+AND+1%3D1&Submit=Submit
```
**Result:** `ROWS=1`
**Screenshot:** 

<img width="781" height="235" alt="image" src="https://github.com/user-attachments/assets/8a1e014c-c348-4384-b3ad-51f2b674490a" />

## Test 2 — false condition
```
Request: id = 1 AND 1=0
URL: http://localhost:8081/a2_filtered.php?id=1+AND+1%3D0&Submit=Submit
```
**Result:** `ROWS=0`
**Screenshot:** 

<img width="780" height="247" alt="image" src="https://github.com/user-attachments/assets/f85dfa5b-616d-49b8-b1b8-46557c544300" />


## Interpretation

The two requests differ only in a boolean condition (`1=1` vs `1=0`) and
produce different, observable outcomes (`ROWS=1` vs `ROWS=0`). This is the
defining signature of boolean-blind SQL injection.

Critically, **both payloads pass the page's input filter**, the regex
```
/\A[0-9]{1,6}(?:[ \t]+(?:AND|OR)[ \t]+[0-9]{1,6}[ \t]*=[ \t]*[0-9]{1,6})*\z/i
```
explicitly permits numeric `AND`/`OR` comparisons. The filter blocks
SQLiFuzz's syntax-breaking mutation characters (apostrophe, etc.) while
leaving this entire attack class untouched.

This confirms the page is genuinely exploitable regardless of what
SQLiFuzz itself reports.
