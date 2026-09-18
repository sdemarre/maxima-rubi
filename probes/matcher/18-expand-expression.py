#!/usr/bin/env python3
"""probes/matcher/18-expand-expression.py -- the ExpandExpression /
SmartApart / ExpandCleanup port (exact seen test design,
docs/superpowers/specs/2026-09-15-matcher-seen-test-intpart-design.md 3.4):
red on the tree before the port, green after.

VALUES   %mr_expandIntegrand / %mr_expandExpression / %mr_smartApart /
         %mr_expand_x / %mr_collectReciprocals / %mr_expandCleanup and the
         rational-factor split, on the design 3.5 case list. Expectations
         are derived by hand from the .m definitions
         (IntegrationUtilityFunctions.m :1593, :1606, :3762, :3780, :3805,
         :3824, :3897, :3980) and compared as a term COUNT plus a zero
         test on the difference.
         The zero oracle is radcan -- ratsimp(radcan(d)) = 0 -- not bare
         ratsimp (design 0.4, the third amendment): once ExpandCleanup has
         rewritten two conjugate-radical denominators, ratsimp cannot
         prove the difference zero on the nested-radical shapes and
         reports FALSE defects in a port that is value-preserving
         (measured 2026-09-16: residual numerator (sqrt(a)+1)^2 - a -
         2 sqrt(a) - 1, i.e. 0; radcan and a numeric substitution both
         close it).
         On the pre-port tree %mr_expandExpression and its siblings are
         undefined, so their calls stay NOUNS and the checks fail: that is
         the red signal.
ENTRIES  1.1.1.4 e4 -- the entry whose ExpandIntegrand result decided the
         port: the pre-port fallback expand(u) hands on an
         expanded-denominator form which, under the exact seen test,
         dispatches >= 794 declines in 60 s and times out at 120 s, where
         Rubi's ExpandExpression splits it into partial fractions.
         Check: e4 is PASS.
         Plus a FIXED sample of 60 of the 805 class-1 entries that P5b
         answered PASS and the first design version (exact seen test, no
         SmartApart) lost at a rule whose replacement calls
         %mr_expandIntegrand (18-expand-expression.sample.tsv, committed
         beside this probe; evenly spaced over the sorted (file, entry)
         keys). Their classes and fire traces are RECORDED, not checked:
         the tree's default is rules-only (mr_nested_fallback false), so
         an entry whose P5b PASS came from a nested integrate fall-through
         legitimately answers the unintegrable noun here. The summary
         counts them by class so the plan's acceptance can read how much
         the port restored.

Every entry runs through the corpus driver's own per-entry text
(test/corpus_driver.py build_text) on the tree's rules core, with the
tree's default switches, cap 30 s, 8 workers, stdin /dev/null.
Nothing else may run. Re-runnable (repo root):
  python3 probes/matcher/18-expand-expression.py > probes/matcher/18-expand-expression.out
"""

import concurrent.futures
import importlib.util
import os
import re
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
CAP = 30
WORKERS = 8
SUITE = "reference/maxima-syntax-test-suite"
PASS = {"expected", "verified", "no-answer"}
SAMPLE = os.path.join("probes", "matcher", "18-expand-expression.sample.tsv")
F1114 = ("1 Algebraic functions/1.1 Binomial products/1.1.1 Linear/"
         "1.1.1.4 (a+b x)^m (c+d x)^n (e+f x)^p (g+h x)^q.mac")
E4 = 4

# The integrands the design 3.5 case list names, as Maxima text.
E4_TEXT = "(a+b*x)/((c+d*x)*(e+f*x)*(g+h*x))"
EXDENOM = "(a+b*x)/expand((c+d*x)*(e+f*x)*(g+h*x))"
NESTRAD = "1/((x-sqrt(1+sqrt(a)))*(x+sqrt(1+sqrt(a))))"
RADCOEF = "x/((x+sqrt(2))*(x-1))"
NONRAT = "sqrt(x)/((x+1)*(x+2))"

# (tag, maxima expression, kind, expected)
#   nterms -> the number of top-level Plus terms
#   zero   -> ratsimp(radcan(<expr>)) is 0          (the design 0.4 oracle)
#   eq     -> the printed value equals the expectation, as Maxima's `is`
VALUES = [
    ("e4-nterms", f"mr18_nterms(%mr_expandIntegrand({E4_TEXT}, x))", "nterms", 3),
    ("e4-value", f"%mr_expandIntegrand({E4_TEXT}, x) - ({E4_TEXT})", "zero", None),
    ("e4-expandExpression-nterms",
     f"mr18_nterms(%mr_expandExpression({E4_TEXT}, x))", "nterms", 3),
    ("exdenom-nterms", f"mr18_nterms(%mr_expandIntegrand({EXDENOM}, x))", "nterms", 3),
    ("exdenom-value", f"%mr_expandIntegrand({EXDENOM}, x) - ({EXDENOM})", "zero", None),
    ("replinear-nterms",
     "mr18_nterms(%mr_expandIntegrand(1/((x+1)^2*(x+2)), x))", "nterms", 3),
    ("replinear-value",
     "%mr_expandIntegrand(1/((x+1)^2*(x+2)), x) - 1/((x+1)^2*(x+2))", "zero", None),
    ("polypart-nterms",
     "mr18_nterms(%mr_expandIntegrand((x^3+1)/(x+2), x))", "nterms", 4),
    ("polypart-value",
     "%mr_expandIntegrand((x^3+1)/(x+2), x) - (x^3+1)/(x+2)", "zero", None),
    # kept, as in Rubi: partfrac does not split these
    ("irrquad-nterms",
     "mr18_nterms(%mr_expandIntegrand((x+1)/((x^2+x+1)*(x-2)), x))", "nterms", 2),
    ("abx2-kept",
     "%mr_expandIntegrand(1/(a+b*x^2), x) = 1/(a+b*x^2)", "eq", None),
    ("symexp-kept",
     "%mr_expandIntegrand(1/((x+a)^m*(x+b)), x) = 1/((x+a)^m*(x+b))", "eq", None),
    # radicals: value-preserving under the radcan oracle (design 0.4)
    ("nestrad-value", f"%mr_expandIntegrand({NESTRAD}, x) - ({NESTRAD})", "zero", None),
    ("radcoef-value", f"%mr_expandIntegrand({RADCOEF}, x) - ({RADCOEF})", "zero", None),
    ("nonrat-nterms", f"mr18_nterms(%mr_expandIntegrand({NONRAT}, x))", "nterms", 2),
    ("nonrat-value", f"%mr_expandIntegrand({NONRAT}, x) - ({NONRAT})", "zero", None),
    ("ratFactors",
     f"%mr_rationalFunctionFactors({NONRAT}, x) = 1/((x+1)*(x+2))", "eq", None),
    ("nonratFactors", f"%mr_nonrationalFunctionFactors({NONRAT}, x) = sqrt(x)", "eq", None),
    # ExpandAlgebraicFunction (.m :3980/:3984)
    ("expalg-plus",
     "%mr_expandAlgebraicFunction((x+1)*sqrt(y), x) = x*sqrt(y)+sqrt(y)", "eq", None),
    ("expalg-power",
     "%mr_expandAlgebraicFunction((x+1)^2*sqrt(y), x) = x^2*sqrt(y)+2*x*sqrt(y)+sqrt(y)",
     "eq", None),
    ("expalg-declines",
     "%mr_expandAlgebraicFunction(x*sqrt(y), x) = false", "eq", None),
    # Expand[u, x]: the x-free factors stay unmultiplied
    ("expand_x-keeps-xfree",
     "%mr_expand_x((a+b)^2*(x+1)^2, x) = (a+b)^2*x^2 + 2*(a+b)^2*x + (a+b)^2", "eq", None),
    # CollectReciprocals (.m :3824-:3832)
    ("collectRecip-pair",
     "%mr_collectReciprocals(1/(a+b*x) + 1/(a-b*x), x) = 2*a/(a^2-b^2*x^2)", "eq", None),
    ("collectRecip-nonpair-nterms",
     "mr18_nterms(%mr_collectReciprocals(1/(x+1) + 1/(x+2), x))", "nterms", 2),
    # ExpandCleanup must not recombine: %mr_simplifyTerm returns a CRE and
    # Maxima's "+" merges CRE operands into one fraction (design 3.4 (d))
    ("cleanup-keeps-sum",
     f"mr18_nterms(%mr_expandCleanup(partfrac({E4_TEXT}, x), x))", "nterms", 3),
    ("smartApart-2arg-eq-3arg",
     f"%mr_smartApart({E4_TEXT}, x) = %mr_smartApart({E4_TEXT}, x, x)", "eq", None),
    # the two specific ExpandIntegrand branches are unchanged
    ("posPowerOfSum",
     "%mr_expandIntegrand((x+1)^2, x) = x^2+2*x+1", "eq", None),
]

VAL_RX = re.compile(r"^P18 (\S+) :: (.*)$", re.M)
OUTCOME_RX = re.compile(r"rubi: rule\s+(\S+)(?:\s+(r\d+))?\s+"
                        r"(fired on|declined on|misfire|cond not accepted|matcher fault)")
RET_RX = re.compile(r"^MR18 RETURNED answer=(.*)$", re.M)
passed = failed = 0


def check(label, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"PASS: {label}")
    else:
        failed += 1
        print(f"FAIL: {label}  {detail}")


def load_driver(section):
    path = os.path.join(ROOT, "test", "corpus_driver.py")
    saved = sys.argv
    sys.argv = [path, section + "/", "999999", str(CAP), SUITE]
    try:
        spec = importlib.util.spec_from_file_location(
            "corpus_driver_" + section.split()[0], path)
        d = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(d)
    finally:
        sys.argv = saved
    assert d.USE_RULES_CORE, f"{section}: no rules core in use"
    return d


def values_text():
    """One batch: every VALUES case as a tagged line."""
    lines = ["display2d : false$",
             "mr18_nterms(e) := if not atom(e) and is(op(e) = \"+\") "
             "then length(args(e)) else 0$",
             # the design 0.4 oracle
             "mr18_zero(e) := block([r], r : errcatch(ratsimp(radcan(e))), "
             "if r = [] then false else is(first(r) = 0))$"]
    for tag, expr, kind, want in VALUES:
        if kind == "nterms":
            got = f"string({expr})"
        elif kind == "zero":
            got = f"if mr18_zero({expr}) then \"zero\" else \"NONZERO\""
        else:
            got = f"if is({expr}) then \"true\" else \"false\""
        # errcatch: on the pre-port tree the calls are nouns, and a noun
        # reaching is()/op() can error rather than answer
        lines.append(f'block([r], r : errcatch({got}), '
                     f'?format(true, "~&P18 {tag} :: ~a~%", '
                     f'if r = [] then "ERROR" else first(r)))$')
    return "\n".join(lines) + "\n"


def run_entry(d, sf, e):
    entries, _line_nos = d.extract_entries(os.path.join(ROOT, SUITE, sf))
    els = d.split_elements(entries[e - 1][1:-1])
    body = d.build_text(d.normalize_heads(els[0]), els[1], d.normalize_heads(els[3]),
                        d.normalize_heads(els[4]) if len(els) == 5 else None)
    answers = "pos$\n" * 40 + "no$\n" * 20
    i = body.index("\nmr_r: ")
    j = body.index(answers, i)
    assert body[i:j].count("\n") == 2, "answer-line anchor"
    j += len(answers)
    body = (body[:j]
            + '?format(true, "~&MR18 RETURNED answer=~a~%", string(mr_r))$\n'
            + body[j:])
    ts = time.time()
    out, timed_out = d.maxima_run("rubi_verbose : true$\n" + body, CAP)
    dt = time.time() - ts
    cls = next((s.strip()[6:].strip() for s in out.splitlines()
                if s.strip().startswith("CLASS ")), None)
    if cls is None:
        cls = "timeout" if timed_out else "error"
    ret = RET_RX.search(out)
    fires = [(f"{m.group(1)}_{m.group(2)}" if m.group(2) else m.group(1))
             for m in OUTCOME_RX.finditer(out) if m.group(3) == "fired on"]
    return dict(cls=cls, t=dt, fires=fires,
                answer=ret.group(1) if ret else None,
                declines=sum(1 for m in OUTCOME_RX.finditer(out)
                             if m.group(3) == "cond not accepted"))


def read_sample():
    rows = []
    for line in open(os.path.join(ROOT, SAMPLE), encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        rel, entry, cut, p5b, proto = line.rstrip("\n").split("\t")
        rows.append((rel, int(entry), cut, p5b, proto))
    return rows


def short(s, n=120):
    return s if s is None or len(s) <= n else s[:n] + "..."


def main():
    src = open("maxima_rubi_utils.mac", encoding="utf-8").read()
    ported = "%mr_expandExpression(u, x) :=" in src
    sample = read_sample()
    d1 = load_driver("1 Algebraic functions")

    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        vals_fut = ex.submit(d1.maxima_run, values_text(), 120)
        e4_fut = ex.submit(run_entry, d1, F1114, E4)
        futs = {ex.submit(run_entry, d1, rel, e): k
                for k, (rel, e, _c, _p, _q) in enumerate(sample)}
        vals_out, vals_timeout = vals_fut.result()
        e4 = e4_fut.result()
        results = {futs[f]: f.result() for f in concurrent.futures.as_completed(futs)}
    wall = time.time() - t0

    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                          text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--",
                            "maxima_rubi.mac", "maxima_rubi_utils.mac",
                            "maxima_rubi_dispatch.lisp", "rules"],
                           capture_output=True, text=True).stdout.strip()
    stamp = open(d1.RULES_CORE_STAMP, encoding="utf-8").read().split("\n")[0]
    build = subprocess.run(["maxima", "--very-quiet", "--batch-string",
                            "disp(build_info());"], capture_output=True, text=True,
                           timeout=120, stdin=subprocess.DEVNULL)
    print("=== probes/matcher/18-expand-expression  "
          + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    print("\n".join(f"maxima: {s.strip()}" for s in build.stdout.splitlines()
                    if s.strip().startswith(("Maxima", "Lisp "))))
    print(f"git HEAD: {head}  (runtime sources vs HEAD: "
          f"{'clean' if not dirty else 'DIRTY'})")
    print(f"core: {d1.RULES_CORE}  {stamp}")
    print("ExpandExpression / SmartApart in this tree: "
          + ("PORTED" if ported else "not ported (pre-port tree: the calls are nouns)"))
    print(f"switches: {d1.SWITCH_SETTINGS}")
    print(f"cap {CAP} s, {WORKERS} workers, wall {wall:.0f} s")

    print("\n=== VALUES (zero oracle: ratsimp(radcan(d)) = 0, design 0.4) ===")
    if vals_timeout:
        print("    the VALUES batch hit its cap")
    got = dict(VAL_RX.findall(vals_out))
    for tag, _expr, kind, want in VALUES:
        g = got.get(tag)
        if kind == "nterms":
            ok, detail = g == str(want), f"terms={g} want={want}"
        elif kind == "zero":
            ok, detail = g == "zero", f"difference={g}"
        else:
            ok, detail = g == "true", f"is()={g}"
        check(f"values {tag}", ok, detail)

    print("\n=== ENTRIES: 1.1.1.4 e4 (the entry the port exists for) ===")
    check(f"e4 is PASS (class {e4['cls']})", e4["cls"] in PASS,
          f"class={e4['cls']} t={e4['t']:.1f}s declines={e4['declines']}")
    print(f"    class={e4['cls']} t={e4['t']:.1f}s fires={len(e4['fires'])} "
          f"declines={e4['declines']} first={','.join(e4['fires'][:6]) or '-'}")
    print(f"    answer={short(e4['answer'])}")

    print(f"\n=== ENTRIES: the fixed sample ({len(sample)} entries, recorded not checked) ===")
    tally = Counter()
    noun = 0
    for k, (rel, e, cut, p5b, proto) in enumerate(sample):
        r = results[k]
        tally[r["cls"]] += 1
        is_noun = r["answer"] is not None and "unintegrable" in r["answer"]
        if is_noun:
            noun += 1
        lab = rel.split("/")[-1].split()[0]
        print(f"    {lab:9s} e{e:<5d} cut={cut:14s} p5b={p5b:10s} "
              f"first-version={proto:10s} now={r['cls']:13s} t={r['t']:5.1f}s "
              f"fires={len(r['fires']):3d}" + ("  rules-only-noun" if is_noun else ""))
    n_pass = sum(v for k, v in tally.items() if k in PASS)
    print(f"  sample classes: {dict(sorted(tally.items()))}")
    print(f"  sample PASS {n_pass}/{len(sample)}; answers holding the "
          f"unintegrable noun (rules-only): {noun}")

    print(f"\nResults: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
