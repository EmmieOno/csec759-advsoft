"""
boolean_probe.py -- database-informed paired Boolean probing (A3 prototype).

Place next to SQLIFuzz.py. Pure helpers (strip_response, mask_literals,
payload_in_code, template, normalize_body, numeric_candidates, judge) do no I/O
and are unit-tested in test_boolean_probe.py. Only queries_in_window, _replay and
boolean_pair_probe touch the tool (sql_analysis.new_get_log, send_HTTP_request).

Design notes
- Raw proxy log lines (log["sql"]) are used, NOT check_SQL_output's SQL_detected,
  because find_queries_in_time_window deletes " and ` and lowercases the query
  before matching. That would make "1 AND 1=1" inside a double-quoted literal look
  like code.
- Only the payload's own text is looked up in the window (substring), because the
  payload is long and distinctive. The original value "1" would match almost any query.
- No calls to `random` here, so the RNG stream of test_SQLi stays aligned between
  baseline and prototype when SQLIFUZZ_SEED is fixed.
"""
import copy
import re
import time
from datetime import datetime

MASK = "\x00"
FMT = "%Y-%m-%d %H:%M:%S,%f"
SLOT_KEYWORDS = re.compile(
    r"\b(where|and|or|not|in|between|having|on|limit|offset|like|is|when|then|else)$",
    re.I,
)


# ---------------------------------------------------------------- pure helpers
def strip_response(sql):
    """Split '<query> *#*# <response info>' into (query, response_info)."""
    q, _, resp = sql.partition("*#*#")
    return q.strip(), resp


def mask_literals(sql):
    """Return sql with every string literal, quoted identifier and comment
    overwritten by MASK characters (same length, so offsets are preserved)."""
    out = list(sql)
    n = len(sql)
    i = 0

    def blank(a, b):
        for k in range(a, b + 1):
            out[k] = MASK

    while i < n:
        c = sql[i]
        if c in "'\"`":
            j = i + 1
            while j < n:
                if sql[j] == "\\" and c != "`":
                    j += 2
                    continue
                if sql[j] == c:
                    if j + 1 < n and sql[j + 1] == c:  # doubled quote
                        j += 2
                        continue
                    break
                j += 1
            end = min(j, n - 1)  # unterminated literal masks to end of string
            blank(i, end)
            i = end + 1
        elif sql.startswith("/*", i):
            j = sql.find("*/", i + 2)
            end = n - 1 if j == -1 else j + 1
            blank(i, end)
            i = end + 1
        elif c == "#" or (sql.startswith("--", i) and (i + 2 >= n or sql[i + 2] in " \t\r\n")):
            j = sql.find("\n", i)
            end = n - 1 if j == -1 else j - 1
            blank(i, end)
            i = end + 1
        else:
            i += 1
    return "".join(out)


def payload_in_code(query, payload):
    """True if `payload` occurs in `query` entirely as unquoted SQL text, in an
    operand position (after an operator, '(', ',' or a clause keyword)."""
    q = strip_response(query)[0]
    masked = mask_literals(q)
    ql, pl = q.lower(), payload.lower()
    idx = ql.find(pl)
    while idx != -1:
        if MASK not in masked[idx: idx + len(pl)]:
            prev = masked[:idx].rstrip()
            if prev and prev[-1] != MASK and (
                prev[-1] in "=<>(,+-*/%!" or SLOT_KEYWORDS.search(prev)
            ):
                return True
        idx = ql.find(pl, idx + 1)
    return False


def template(query):
    """Literal-stripped query shape: literals and numbers -> '?'."""
    q = strip_response(query)[0]
    t = re.sub(re.escape(MASK) + "+", "?", mask_literals(q))
    t = re.sub(r"\b\d+(?:\.\d+)?\b", "?", t)
    return re.sub(r"\s+", " ", t).strip().lower()


def normalize_body(text):
    """Remove long hex tokens (CSRF/session-like) and collapse whitespace."""
    t = re.sub(r"(?i)\b[0-9a-f]{16,}\b", "<tok>", text or "")
    return re.sub(r"\s+", " ", t).strip()


def numeric_candidates(req):
    """Indices of URL/BODY paramvals holding a plain integer (candidate numeric slots)."""
    out = []
    for i, pv in enumerate(req.paramvals):
        if pv.is_nested() or pv.is_nonce:
            continue
        pos = getattr(pv.position, "name", str(pv.position))
        if pos not in ("URL", "BODY"):
            continue
        if re.fullmatch(r"\d{1,9}", str(pv.value if pv.value is not None else "")):
            out.append(i)
    return out


def _first_code_query(entry, payload):
    return next((q for q in entry["queries"] if payload_in_code(q, payload)), None)


def judge(rounds, pt, pf, require_structure=True):
    """rounds: list of (true_entry, false_entry); entry = {status, body, queries}.
    Returns (verdict, reason); verdict in confirmed | inconclusive | unsupported.
    require_structure=False is the ablation (response difference only)."""
    for t, f in rounds:
        if t["status"] is None or f["status"] is None:
            return "inconclusive", "request failed (no response)"

    if require_structure:
        for t, f in rounds:
            if not t["queries"] or not f["queries"]:
                return "inconclusive", "probe not observed in any SQL query (rejected before DB, or bound)"
        for t, f in rounds:
            if _first_code_query(t, pt) is None or _first_code_query(f, pf) is None:
                return "unsupported", "probe reached SQL but only inside a literal/comment (not a numeric slot)"
        t0, f0 = rounds[0]
        if template(_first_code_query(t0, pt)) != template(_first_code_query(f0, pf)):
            return "inconclusive", "true/false probes produced different query shapes"

    nb = lambda e: normalize_body(e["body"])
    t0, f0 = rounds[0]
    if not all(nb(t) == nb(t0) and nb(f) == nb(f0) for t, f in rounds):
        return "inconclusive", "responses unstable across repetitions"
    if nb(t0) == nb(f0):
        return "inconclusive", "no response difference between true and false probe"
    return "confirmed", "paired Boolean probes changed the result" + (
        " and appeared as unquoted SQL" if require_structure else " (response diff only)"
    )


# ------------------------------------------------------------ tool-facing code
def queries_in_window(start_time, end_time, settle=1.0):
    """Raw proxy log entries whose timestamp is inside [start, end]."""
    from sql_analysis import new_get_log

    time.sleep(settle)  # mirrors the sleep(1) in find_queries_in_time_window
    s = datetime.strptime(start_time, FMT)
    e = datetime.strptime(end_time, FMT)
    return [l for l in new_get_log()
            if s <= datetime.strptime(l["timestamp"], FMT) <= e]


async def _replay(page, req, request_context, idx, value):
    from general_functions import send_HTTP_request

    prep = copy.deepcopy(req)
    prep.parent = req
    prep.update_id()
    prep.paramvals[idx].value = value
    prep.update_param_from_paramvals()
    resp = await send_HTTP_request(page, prep, request_context)
    if resp is None or prep.timing is None:
        return {"req": prep, "status": None, "body": "", "queries": []}
    body = await resp.text()
    window = queries_in_window(prep.timing["start_calculation"],
                               prep.timing["end_calculation"])
    queries = [l["sql"] for l in window
               if value.lower() in strip_response(l["sql"])[0].lower()]
    return {"req": prep, "status": resp.status, "body": body, "queries": queries}


async def boolean_pair_probe(page, req, request_context, reps=2, require_structure=True):
    """Returns (verdict, evidence, true_probe_request_or_None)."""
    notes = []
    for idx in numeric_candidates(req):
        orig = str(req.paramvals[idx].value)
        pt, pf = f"{orig} OR 1=1", f"{orig} OR 1=0"
        rounds = []
        for _ in range(reps):
            t = await _replay(page, req, request_context, idx, pt)
            f = await _replay(page, req, request_context, idx, pf)
            rounds.append((t, f))
        verdict, reason = judge(rounds, pt, pf, require_structure)
        ev = {
            "param": req.paramvals[idx].param, "original": orig,
            "probe_true": pt, "probe_false": pf, "reps": reps,
            "requests_sent": 2 * reps, "reason": reason,
            "sql_true": rounds[0][0]["queries"], "sql_false": rounds[0][1]["queries"],
            "body_true": normalize_body(rounds[0][0]["body"])[:200],
            "body_false": normalize_body(rounds[0][1]["body"])[:200],
        }
        if verdict == "confirmed":
            return verdict, ev, rounds[0][0]["req"]
        notes.append((verdict, ev))
    if not notes:
        return "unsupported", {"reason": "no numeric URL/BODY parameter"}, None
    return notes[0][0], notes[0][1], None
