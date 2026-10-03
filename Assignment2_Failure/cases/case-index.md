# Case Index: Boolean-Blind Injection vs. SQLiFuzz's Error-Based Oracle

| Case ID | Role | File | Request method | Expected behavior | Basis for expectation |
|---|---|---|---|---|---|
| `control` | Matched control | `a2_control.php` | GET | SQLiFuzz detects SQLi | Source: no input filtering; apostrophe reaches query unmodified, triggers MySQL syntax error |
| `filtered-get` | Primary failed case | `a2_filtered.php` | GET | Page IS exploitable (boolean-blind); SQLiFuzz is expected to MISS it | `notes/ground_truth_boolean_check.md` — manual check independent of SQLiFuzz |
| `filtered-post` | Additional variant | `a2_filtered_post.php` | POST | Same vulnerability/filter as filtered-get; method is the only intended change | Identical source logic to `a2_filtered.php`; see diff below |

## Diff: `a2_control.php` → `a2_filtered.php`

The only functional change is the `$filterEnabled` flag (the file ships
with a toggle for exactly this comparison, rather than being two
independently-written files, to minimize unrelated differences):

```diff
- $filterEnabled = false;
+ $filterEnabled = true;
```

Everything else — the query construction (`SELECT first_name, last_name
FROM users WHERE user_id = $id`, unquoted/unescaped), the database
connection, and the response format — is identical between the two files.

## Diff: `a2_filtered.php` → `a2_filtered_post.php`

```diff
- <form method="GET">
+ <form method="POST">
...
- $id = $_GET['id'] ?? '';
+ $id = $_POST['id'] ?? '';
...
- if (isset($_GET['Submit'])) {
+ if (isset($_POST['Submit'])) {
```

The filter regex, query construction, and all other logic are byte-for-byte
identical to `a2_filtered.php`. This isolates HTTP method/parameter-source
as the single varied factor.

## Results summary

See `derived/results_table.csv` for the full per-run results, and
`notes/prediction-boolean-oracle-post-variant.md` for the prediction
recorded before the `filtered-post` runs.
