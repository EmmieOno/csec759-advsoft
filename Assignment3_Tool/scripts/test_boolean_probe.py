"""Run: python test_boolean_probe.py   (no server, no SQLiFuzz imports needed)"""
from types import SimpleNamespace as NS

from boolean_probe import (judge, mask_literals, normalize_body, numeric_candidates,
                           payload_in_code, strip_response, template, MASK)

BASE = "SELECT first_name, last_name FROM users WHERE user_id = "
PT, PF = "1 AND 1=1", "1 AND 1=0"


def entry(body, *queries, status=200):
    return {"status": status, "body": body, "queries": list(queries)}


def test_strip_response():
    assert strip_response("select 1 *#*# error 1064 syntax") == ("select 1", " error 1064 syntax")


def test_mask_handles_quotes_escapes_comments():
    assert MASK not in mask_literals("select 1")
    assert mask_literals("a 'x' b") == "a " + MASK * 3 + " b"
    assert mask_literals(r"a 'x\'y' b") == "a " + MASK * 6 + " b"
    assert mask_literals("a 'it''s' b") == "a " + MASK * 7 + " b"
    assert mask_literals("a /* c */ b") == "a " + MASK * 7 + " b"
    assert mask_literals("a -- c\nb") == "a " + MASK * 4 + "\nb"
    assert mask_literals("a 'unterminated") == "a " + MASK * 13


def test_payload_in_code_numeric_slot():
    assert payload_in_code(BASE + PT, PT)
    assert payload_in_code((BASE + PT).lower() + " *#*# ok", PT)       # suffix ignored, case-insensitive
    assert payload_in_code("select a from t where x in (" + PT + ")", PT)


def test_payload_in_code_rejects_literals_and_comments():
    assert not payload_in_code(BASE + "'" + PT + "'", PT)              # emulated prepare / quoted context
    assert not payload_in_code(BASE + '"' + PT + '"', PT)              # double-quoted literal
    assert not payload_in_code("select 1 /* " + PT + " */", PT)
    assert not payload_in_code("select 1 -- " + PT, PT)
    assert not payload_in_code("select ? from t where id = ?", PT)     # native prepare, value not in text


def test_template_shape():
    assert template(BASE + PT) == template(BASE + PF)
    assert template(BASE + "'" + PT + "'") != template(BASE + PT)
    assert template(BASE + "1") == "select first_name, last_name from users where user_id = ?"


def test_numeric_candidates():
    pv = lambda p, v, pos, nonce=False: NS(param=p, value=v, position=NS(name=pos),
                                          is_nested=lambda: False, is_nonce=nonce)
    req = NS(paramvals=[pv("sec-fetch-user", "?1", "HEADER"), pv("path0", "a.php", "PATH"),
                        pv("id", "1", "URL"), pv("Submit", "Submit", "URL"),
                        pv("n", "7", "BODY", nonce=True), pv("empty", "", "URL")])
    assert numeric_candidates(req) == [2]


def test_normalize_body():
    assert normalize_body("<pre> ROWS=1 </pre> tok=" + "a1" * 10) == "<pre> ROWS=1 </pre> tok=<tok>"


def test_judge_confirmed():
    r = [(entry("ROWS=1", BASE + PT), entry("ROWS=0", BASE + PF))] * 2
    assert judge(r, PT, PF)[0] == "confirmed"


def test_judge_rejected_before_db_is_inconclusive():
    r = [(entry("INPUT REJECTED", "use db"), entry("INPUT REJECTED", "use db"))] * 2
    # 'use db' is not matched to the probe, so queries lists are empty in practice:
    r = [(entry("INPUT REJECTED"), entry("INPUT REJECTED"))] * 2
    assert judge(r, PT, PF)[0] == "inconclusive"


def test_judge_quoted_context_is_unsupported():
    q = lambda p: BASE + "'" + p + "'"
    r = [(entry("ROWS=1", q(PT)), entry("ROWS=1", q(PF)))] * 2
    assert judge(r, PT, PF)[0] == "unsupported"


def test_judge_no_difference_and_instability():
    r = [(entry("ROWS=1", BASE + PT), entry("ROWS=1", BASE + PF))] * 2
    assert judge(r, PT, PF)[0] == "inconclusive"                        # injected but not observable
    r = [(entry("ROWS=1", BASE + PT), entry("ROWS=0", BASE + PF)),
         (entry("ROWS=2", BASE + PT), entry("ROWS=0", BASE + PF))]
    assert judge(r, PT, PF)[0] == "inconclusive"


def test_judge_request_failure():
    r = [(entry("", status=None), entry("ROWS=0", BASE + PF))]
    assert judge(r, PT, PF)[0] == "inconclusive"


def test_ablation_response_diff_only_gives_false_positive():
    # safe page whose output varies with the input, no SQL structure change observed
    r = [(entry("hello 1 AND 1=1"), entry("hello 1 AND 1=0"))] * 2
    assert judge(r, PT, PF, require_structure=True)[0] == "inconclusive"
    assert judge(r, PT, PF, require_structure=False)[0] == "confirmed"  # the ablation's failure mode


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print("PASS", name)
    print(f"{len(tests)} passed")
