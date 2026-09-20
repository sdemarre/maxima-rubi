#!/usr/bin/env python3
"""probes/matcher/17-exact-seen-intpart.py -- the exact seen test and the
IntegerPart reading (exact seen test design,
docs/superpowers/specs/2026-09-15-matcher-seen-test-intpart-design.md 3.1,
3.2, 3.4): red on the tree before the change, green after.

Every entry runs through the corpus driver's exact per-entry text
(test/corpus_driver.py build_text, switch defaults) on the tree's own rules
core, with `rubi_verbose : true$` and a probe-local trace derived from the
tree's %mr_top_body source (one anchor, asserted to occur once): at a
depth-cap hit it prints whether the integrand or any %mr_seen element holds a
float.

SEEN     probe 16's collapse entries its exact-only control arm brought to
         PASS while its trace arm did not (class 2/3 from
         probes/matcher/16-seen-guard-trace.out, class 1 from .class1.out; 78
         entries). Check: the entry is PASS -- EXCEPT where its answer holds
         the `unintegrable` noun, which is reported as its own category and
         not failed (design 3.3/3.5). The tree's default is rules-only
         (mr_nested_fallback false), so an entry whose P5b PASS was BUILT
         from a nested integrate fall-through answers that noun here: the
         switch working, not the seen test failing. The category is decided
         from the ANSWER, not the class, so a genuine miss still fails.
DRIFT    1.1.1.4 e1, e3, e4, e5, e135 and 1.1.1.7 e1, the targets of the
         2026-08-25 float/rational drift cycle (commit 891240b). Checks: the
         class is not on a worse PASS/FAIL side than the P5b run-1 record's
         (same rules-only noun exemption); no depth-cap hit with a float in
         the integrand or on %mr_seen; and e4 -- the ExpandExpression /
         SmartApart target, whose pre-port fallback dispatched >= 794
         declines under the exact seen test -- is PASS (probe 18 covers the
         values). Plus a scan of every class 1-3 corpus integrand (the
         parsed first element) for float literals. Check: none in classes 1
         and 3.
INTPART  truncate and r - truncate(r) on eight rationals (floor printed);
         %mr_intPart / %mr_fracPart on -1/2, -3/2, -5/2, 3/2, -3/2*x, 3/2 + x
         against Rubi's IntPart / FracPart (IntegrationUtilityFunctions.m
         :2952-:2981) with Mathematica's IntegerPart (toward zero) and
         FractionalPart (the sign of its argument); class 1 g27's entries
         1.2.3.2 e254, e255, e604, e605. Checks: the values; each g27 entry
         returns an answer with 1_2_3_2_r34 fired (class and answer printed;
         PASS is not required -- the AppellF1 verification gap is a separate
         mechanism).

Cap 30 s per run, 8 workers, stdin /dev/null (the driver's maxima_run).
Nothing else may run. Re-runnable (repo root):
  python3 probes/matcher/17-exact-seen-intpart.py > probes/matcher/17-exact-seen-intpart.out
"""

import concurrent.futures
import importlib.util
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
CAP = 30
WORKERS = 8
SUITE = "reference/maxima-syntax-test-suite"
PASS = {"expected", "verified", "no-answer"}
P16 = "probes/matcher/16-seen-guard-trace"
P5B_CLASS1 = "test/corpus_class1.p5b-run1.out"
F1114 = ("1 Algebraic functions/1.1 Binomial products/1.1.1 Linear/"
         "1.1.1.4 (a+b x)^m (c+d x)^n (e+f x)^p (g+h x)^q.mac")
F1117 = ("1 Algebraic functions/1.1 Binomial products/1.1.1 Linear/"
         "1.1.1.7 P(x) (a+b x)^m (c+d x)^n (e+f x)^p (g+h x)^q.mac")
F1232 = ("1 Algebraic functions/1.2 Trinomial products/1.2.3 General/"
         "1.2.3.2 (d x)^m (a+b x^n+c x^(2 n))^p.mac")
DRIFT = [(F1114, e) for e in (1, 3, 4, 5, 135)] + [(F1117, 1)]
G27 = [(F1232, e) for e in (254, 255, 604, 605)]
SEEN_COUNT = 78
# (label, u, IntegerPart-based IntPart[u], FractionalPart-based FracPart[u])
INTPART = [("-1/2", "-1/2", "0", "-1/2"), ("-3/2", "-3/2", "-1", "-1/2"),
           ("-5/2", "-5/2", "-2", "-1/2"), ("3/2", "3/2", "1", "1/2"),
           ("-3/2*x", "-3/2*x", "0", "-3/2*x"), ("3/2+x", "3/2+x", "1", "1/2+x")]
RATIONALS = "[-5/2, -3/2, -1/2, 0, 1/2, 3/2, -2, 2]"
TRUNC_WANT = "[-2, -1, 0, 0, 0, 1, -2, 2]"
FRAC_WANT = "[-1/2, -1/2, -1/2, 0, 1/2, 1/2, 0, 0]"

COMMON = r'''
%mr17_hasfloat(e) := if atom(e) then floatnump(e)
  else block([a : errcatch(args(e))],
    if a = [] then false else some(%mr17_hasfloat, first(a)))$
%mr17_cap(f) := (
  ?format(true, "~&MR17 CAP ffloat=~a seenfloat=~a seenlen=~a f=~a~%",
          if %mr17_hasfloat(f) then "yes" else "no",
          if some(%mr17_hasfloat, %mr_seen) then "yes" else "no",
          length(%mr_seen), string(f)),
  ?finish\-output(), true)$
%mr17_returned(r) := (
  ?format(true, "~&MR17 RETURNED answer=~a~%", string(r)),
  ?finish\-output(), r)$
'''
BODY_HEAD = "\n%mr_top_body(f, x, fb"
BODY_TAIL = "  ) else ans)$"
# The depth-cap branch. The pre-3.3 tree tests the utils global
# %mr_max_depth; from the run switches (exact seen test design 3.3) it
# tests the defmvar mr_max_depth and counts the hit in mr_depth_cap_hits.
# Both spellings are accepted so this probe runs on either tree (red on
# the pre-change tree, green after).
CAP_ANCHORS = ("  if depth_level > %mr_max_depth then (\n",
               "  if depth_level > mr_max_depth then (\n")
CAP_RX = re.compile(r"^MR17 CAP ffloat=(\S+) seenfloat=(\S+) seenlen=(\d+) f=(.*)$", re.M)
RET_RX = re.compile(r"^MR17 RETURNED answer=(.*)$", re.M)
OUTCOME_RX = re.compile(r"rubi: rule\s+(\S+)(?:\s+(r\d+))?\s+"
                        r"(fired on|declined on|misfire|cond not accepted|matcher fault)")
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)\s*$")
passed = failed = 0


def check(label, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"PASS: {label}")
    else:
        failed += 1
        print(f"FAIL: {label}  {detail}")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_driver(section):
    path = os.path.join(ROOT, "test", "corpus_driver.py")
    saved = sys.argv
    sys.argv = [path, section + "/", "999999", str(CAP), SUITE]
    try:
        d = module("corpus_driver_" + section.split()[0], "test/corpus_driver.py")
    finally:
        sys.argv = saved
    assert d.USE_RULES_CORE, f"{section}: no rules core in use"
    return d


def instrumentation(src):
    """%mr_top_body from the tree's utils with the depth-cap trace."""
    assert src.count(BODY_HEAD) == 1, "one %mr_top_body definition"
    start = src.index(BODY_HEAD) + 1
    end = src.index(BODY_TAIL, start) + len(BODY_TAIL)
    body = src[start:end]
    found = [a for a in CAP_ANCHORS if body.count(a) == 1]
    assert len(found) == 1, (
        "exactly one depth-cap branch, in one of the two spellings "
        f"(matched {len(found)}: {found})")
    anchor = found[0]
    return body.replace(anchor, anchor + "    %mr17_cap(f),\n") + "\n"


def rule_name(key, n):
    return f"{key}_{n}" if n else re.sub(r"^_mr_rule_", "", key)


def run_one(d, instr, sf, e):
    entries, line_nos = d.extract_entries(os.path.join(ROOT, SUITE, sf))
    els = d.split_elements(entries[e - 1][1:-1])
    body = d.build_text(d.normalize_heads(els[0]), els[1], d.normalize_heads(els[3]),
                        d.normalize_heads(els[4]) if len(els) == 5 else None)
    # The answer print goes after the prompt-answer lines that follow the mr_r
    # line (probe 15/16's anchor).
    answers = "pos$\n" * 40 + "no$\n" * 20
    i = body.index("\nmr_r: ")
    j = body.index(answers, i)
    assert body[i:j].count("\n") == 2, "answer-line anchor"
    j += len(answers)
    body = body[:j] + "%mr17_returned(mr_r)$\n" + body[j:]
    text = "rubi_verbose : true$\n" + COMMON + instr + body
    ts = time.time()
    out, timed_out = d.maxima_run(text, CAP)
    dt = time.time() - ts
    cls = next((s.strip()[6:].strip() for s in out.splitlines()
                if s.strip().startswith("CLASS ")), None)
    if cls is None:
        cls = "timeout" if timed_out else "error"
    ret = RET_RX.search(out)
    return dict(cls=cls, t=dt, caps=CAP_RX.findall(out), answer=ret.group(1) if ret else None,
                fires=[rule_name(m.group(1), m.group(2)) for m in OUTCOME_RX.finditer(out)
                       if m.group(3) == "fired on"])


def table_rows(path):
    """The cells of probe 16's `=== table (fixed core)` rows, in order."""
    rows, on = [], False
    for line in open(os.path.join(ROOT, path), encoding="utf-8"):
        if line.startswith("=== table (fixed core)"):
            on = True
            continue
        if on:
            if not line.startswith("|"):
                if rows:
                    break
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells[0] in ("entry", "---"):
                continue
            rows.append(cells)
    return rows


def seen_entries():
    """Probe 16's entries whose exact-only class is PASS and trace class is not."""
    p16 = module("p16", P16 + ".py")
    sets = [
        ([(g, sf, e) for g, sf, e, _s in p16.ENTRIES], table_rows(P16 + ".out"),
         lambda sf: sf.split("/")[-1][:5].strip()),
        ([(g, sf, e) for g, sf, e, _s in p16.read_entry_tsvs([P16 + ".class1.tsv"])],
         table_rows(P16 + ".class1.out"), lambda sf: sf.split("/")[-1].split()[0]),
    ]
    out = []
    for entries, rows, lab in sets:
        assert len(entries) == len(rows), (len(entries), len(rows))
        for (g, sf, e), row in zip(entries, rows):
            assert row[0] == f"{lab(sf)} e{e}", (row[0], sf, e)
            if row[4] in PASS and row[3] not in PASS:
                out.append((g, sf, e, row[3], row[4]))
    return out


def float_scan(d):
    rx = re.compile(r"(?<![\w.])\d+\.\d*(?!\w)|(?<![\w.])\.\d+")
    counts, hits = {}, []
    for section in ("1 Algebraic functions", "2 Exponentials", "3 Logarithms"):
        n = 0
        for dirpath, _dn, names in sorted(os.walk(os.path.join(ROOT, SUITE, section))):
            for name in sorted(names):
                if not name.endswith(".mac"):
                    continue
                path = os.path.join(dirpath, name)
                entries, _ = d.extract_entries(path)
                for k, t in enumerate(entries):
                    f = d.split_elements(t[1:-1])[0]
                    if rx.search(f):
                        n += 1
                        hits.append(f"{os.path.relpath(path, os.path.join(ROOT, SUITE))} e{k + 1}: {f[:80]}")
        counts[section.split()[0]] = n
    return counts, hits


def intpart_text():
    # ok= prints a Maxima string: a bare boolean prints as Lisp T / NIL through ?format
    lines = [
        "display2d : false$",
        f"mr17_L : {RATIONALS}$",
        f'?format(true, "~&MR17 TRUNC ok=~a got=~a~%", if is(map(truncate, mr17_L) = {TRUNC_WANT}) then "true" else "false", '
        f'string(map(truncate, mr17_L)))$',
        f'?format(true, "~&MR17 TRUNCFRAC ok=~a got=~a~%", '
        f'if is(map(lambda([r], r - truncate(r)), mr17_L) = {FRAC_WANT}) then "true" else "false", '
        f'string(map(lambda([r], r - truncate(r)), mr17_L)))$',
        '?format(true, "~&MR17 FLOOR got=~a~%", string(map(floor, mr17_L)))$',
    ]
    for label, u, ip, fp in INTPART:
        lines.append(f'?format(true, "~&MR17 IP {label} ok=~a got=~a~%", '
                     f'if is(equal(%mr_intPart({u}), {ip})) then "true" else "false", string(%mr_intPart({u})))$')
        lines.append(f'?format(true, "~&MR17 FP {label} ok=~a got=~a~%", '
                     f'if is(equal(%mr_fracPart({u}), {fp})) then "true" else "false", string(%mr_fracPart({u})))$')
    return "\n".join(lines) + "\n"


def short(s, n=140):
    return s if len(s) <= n else s[:n] + "..."


def main():
    src = open("maxima_rubi_utils.mac", encoding="utf-8").read()
    instr = instrumentation(src)
    drivers = {k: load_driver(s) for k, s in
               (("1", "1 Algebraic functions"), ("2", "2 Exponentials"), ("3", "3 Logarithms"))}
    drv = lambda sf: drivers[sf.split()[0]]
    seen = seen_entries()
    assert len(seen) == SEEN_COUNT, f"probe 16's exact-only PASS set: {len(seen)} != {SEEN_COUNT}"
    p5b = {}
    for line in open(P5B_CLASS1, encoding="utf-8"):
        m = RESULT.match(line.rstrip("\n"))
        if m:
            p5b[(m.group(3), int(m.group(4)))] = m.group(1)

    jobs = ([("seen", k, sf, e) for k, (_g, sf, e, _t, _c) in enumerate(seen)]
            + [("drift", k, sf, e) for k, (sf, e) in enumerate(DRIFT)]
            + [("g27", k, sf, e) for k, (sf, e) in enumerate(G27)])
    t0 = time.time()
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(run_one, drv(sf), instr, sf, e): (kind, k) for kind, k, sf, e in jobs}
        ip_fut = ex.submit(drivers["1"].maxima_run, intpart_text(), CAP)
        for fu in concurrent.futures.as_completed(futs):
            results[futs[fu]] = fu.result()
        ip_out, ip_timeout = ip_fut.result()
    wall = time.time() - t0

    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "maxima_rubi_utils.mac",
                            "maxima_rubi_dispatch.lisp", "maxima_rubi_match.lisp",
                            "maxima_rubi_tree.lisp", "rules", "test/corpus_driver.py"],
                           capture_output=True, text=True).stdout.strip()
    stamp = open(drivers["1"].RULES_CORE_STAMP, encoding="utf-8").read().split("\n")[0]
    build = subprocess.run(["maxima", "--very-quiet", "--batch-string", "disp(build_info());"],
                           capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
    print("=== probes/matcher/17-exact-seen-intpart  "
          + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    print("\n".join(f"maxima: {s.strip()}" for s in build.stdout.splitlines()
                    if s.strip().startswith(("Maxima", "Lisp "))))
    print(f"git HEAD: {head}  (runtime sources vs HEAD: {'clean' if not dirty else 'DIRTY ' + dirty})")
    print(f"core: {drivers['1'].RULES_CORE}  {stamp}")
    print("seen test in this tree: "
          + ("ratsimp comparison (%mr_seenp) on mr_int" if "%mr_seenp(f) :=" in src
             else "exact member on every call"))
    print(f"switches: {drivers['1'].SWITCH_SETTINGS}  cap {CAP} s, {WORKERS} workers, wall {wall:.0f} s")

    # The tree's default is rules-only (mr_nested_fallback false, design
    # 3.3): a nested Int call with no route returns the unintegrable noun
    # instead of Maxima's integrate result. An entry whose P5b PASS was
    # BUILT from such a fall-through therefore answers a noun here — that
    # is the switch working, not the seen test failing, so the probe
    # reports it as its own category (design 3.5) and does not fail it.
    # The category is decided from the ANSWER (it holds `unintegrable`),
    # not from the class, so a genuine miss still fails.
    def rules_only_noun(r):
        return r["answer"] is not None and "unintegrable" in r["answer"]

    print("\n=== SEEN: probe 16's exact-only PASS entries (trace arm not PASS) ===")
    seen_noun = 0
    for k, (g, sf, e, tcls, ccls) in enumerate(seen):
        r = results[("seen", k)]
        lab = sf.split("/")[-1].split()[0]
        tag = ""
        if r["cls"] in PASS:
            check(f"seen {g} {lab} e{e}: PASS (probe 16 trace {tcls}, exact-only {ccls})",
                  True)
        elif rules_only_noun(r):
            seen_noun += 1
            tag = "  rules-only-noun (not a failure: design 3.3/3.5)"
            print(f"NOUN: seen {g} {lab} e{e}: the answer holds `unintegrable` "
                  f"(class {r['cls']}); its P5b PASS came from a nested "
                  f"integrate fall-through")
        else:
            check(f"seen {g} {lab} e{e}: PASS (probe 16 trace {tcls}, exact-only {ccls})",
                  False, f"class={r['cls']}")
        print(f"    class={r['cls']} t={r['t']:.1f}s fires={len(r['fires'])} "
              f"last={','.join(r['fires'][-4:]) or '-'} cap-hits={len(r['caps'])}{tag}")
    print(f"  SEEN: {len(seen)} entries, {seen_noun} answered the rules-only noun")

    print("\n=== DRIFT: the 2026-08-25 drift targets ===")
    for k, (sf, e) in enumerate(DRIFT):
        r = results[("drift", k)]
        lab = sf.split("/")[-1].split()[0]
        base = p5b[(sf, e)]
        floats = [c for c in r["caps"] if "yes" in (c[0], c[1])]
        worse = base in PASS and r["cls"] not in PASS
        if worse and rules_only_noun(r):
            print(f"NOUN: drift {lab} e{e}: class {r['cls']} answers the "
                  f"rules-only noun (P5b run 1 {base}) — not a failure")
        else:
            check(f"drift {lab} e{e}: class {r['cls']} not on a worse side "
                  f"than P5b run 1 {base}", not worse)
        check(f"drift {lab} e{e}: no depth-cap hit with a float ({len(r['caps'])} cap hits)",
              not floats, f"{[short(c[3], 80) for c in floats[:3]]}")
        print(f"    class={r['cls']} t={r['t']:.1f}s fires={len(r['fires'])} "
              f"first={','.join(r['fires'][:4]) or '-'}")
    # 1.1.1.4 e4 is the SmartApart target: the pre-port fallback handed on
    # an expanded-denominator form that dispatched >= 794 declines under
    # the exact seen test; with the port it partial-fractions (probe 18).
    e4 = results[("drift", 2)]
    check(f"drift 1.1.1.4 e4 is PASS with the ExpandExpression port "
          f"(class {e4['cls']})", e4["cls"] in PASS, f"class={e4['cls']}")
    counts, hits = float_scan(drivers["1"])
    print(f"float literals in integrands: class 1 {counts['1']}, class 2 {counts['2']}, "
          f"class 3 {counts['3']}")
    for h in hits:
        print(f"    {h}")
    check("no float literal in a class 1 or class 3 integrand", counts["1"] == 0 and counts["3"] == 0)

    print("\n=== INTPART ===")
    if ip_timeout:
        print("    the INTPART batch hit the cap")
    for tag in ("TRUNC", "TRUNCFRAC"):
        m = re.search(rf"^MR17 {tag} ok=(\S+) got=(.*)$", ip_out, re.M)
        check(f"{tag.lower()} on {RATIONALS} is {TRUNC_WANT if tag == 'TRUNC' else FRAC_WANT}",
              m is not None and m.group(1) == "true", m and m.group(2))
    m = re.search(r"^MR17 FLOOR got=(.*)$", ip_out, re.M)
    print(f"    floor: {m and m.group(1)}")
    for label, _u, ip, fp in INTPART:
        for tag, want in (("IP", ip), ("FP", fp)):
            m = re.search(rf"^MR17 {tag} {re.escape(label)} ok=(\S+) got=(.*)$", ip_out, re.M)
            name = "IntPart" if tag == "IP" else "FracPart"
            check(f"{name}[{label}] = {want}", m is not None and m.group(1) == "true",
                  f"got={m and m.group(2)}")
    for k, (sf, e) in enumerate(G27):
        r = results[("g27", k)]
        check(f"g27 1.2.3.2 e{e}: an answer, 1_2_3_2_r34 fired",
              r["answer"] is not None and "1_2_3_2_r34" in r["fires"],
              f"class={r['cls']} fires={r['fires']}")
        print(f"    class={r['cls']} t={r['t']:.1f}s answer={short(r['answer'] or '-', 200)}")

    print(f"Results: {passed} passed, {failed} failed")


if __name__ == "__main__":
    main()
