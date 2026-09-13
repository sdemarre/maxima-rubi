# Matcher Substrate — Plan 1 (P0–P2): baseline, `mr-match`, `mr-tree`

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the class-3 campaign, re-measure the three-class baseline on the
current build, and deliver a tested Mathematica-semantics matcher (`mr-match`) and
Maxima↔tree converter (`mr-tree`) whose regression suite passes the spec's P1/P2
gates — without touching the running package (Plan 2 wires them in).

**Architecture:** `maxima_rubi_match.lisp` is a focused rewrite of mma4max
`newmatch.lisp` in the same continuation-passing structure (m1 / ordered list /
Pattern / Blank), plus `match-flat` for Plus/Times, native Optionals, a condition
hook and two switches; bindings are an immutable alist threaded through
continuations. `maxima_rubi_tree.lisp` converts simplified Maxima internal form to
canonical Mathematica-form trees and back. The probe-02 round trip, the 02 controls
and the spike-01 cases are retargeted to these two files and become the committed
matcher regression suite under `test/matcher/`.

**Tech Stack:** Maxima `branch_5_50_base_84_g4204fb669` (build date 2026-08-31
13:27:47) / SBCL 2.6.7; Common Lisp loaded into Maxima with `load("…lisp")`;
Python 3 harnesses (`probes/matcher/02-*.py`, `test/*.py`); corpus records under
`test/`.

**Spec:** `docs/superpowers/specs/2026-09-12-matcher-substrate-design.md`
(committed `48c61b8`). This is Plan 1 of three (user decision 2026-09-12: plans
written just in time — Plan 2 = P3–P4, Plan 3 = P5–P6).

**Deviations from the spec's wording (stated, not silent):**

1. *Order of P0 vs the campaign close.* The campaign's Task 5 needs full class-1
   and class-2 runs; those are the same runs P0 needs. Task 3 runs all three
   classes on the campaign's final tree; Task 4 closes the campaign (records, docs,
   ledger — no code or rule change) and asserts the rules-core fingerprint is
   unchanged, so the runs are "at that commit" for every file that affects them.
2. *Binding stack.* §3.2 asks for "a growable binding stack with an overflow
   check". `mr-match` binds into an immutable alist passed through continuations:
   there is no fixed-size stack to overflow; recursion depth is bounded by the
   pattern size.
3. *Fork granularity.* §3.2 says "fork of `newmatch.lisp`". The kept functions
   (m1, mlist, mpattern, mblank) are re-implemented in their original structure
   without mma4max's stack, `meval`, `ucons`, `Alternatives`/`Action`/`Except`
   paths; the dropped paths are the ones no Rubi LHS uses (02-FINDINGS layer 1).
4. *Spike-01 cases gate at P2, not P1.* §4 lists them in the P1 suite, but 69 of
   their 71 targets are Maxima strings that need the converter; Task 8 gates them.
   The P1 suite (Task 6) is the round trip's tree leg plus the controls.

## Global Constraints

Every task's requirements implicitly include this section.

- **Build (stamp, never pin):** every committed measurement output carries
  `build_info()` (Maxima-version, build date) or, for a no-Maxima Python probe, the
  run date and git HEAD.
- **TLS:** any maxima process that loads *rule files* runs with
  `-X "--tls-limit 100000"` (two argv tokens). The matcher/converter tests load no
  rule files and need no flag.
- **Layer A gate:** `maxima --very-quiet -X "--tls-limit 100000" -b test_maxima_rubi.mac`
  ends `Results: 892 passed, 0 failed` throughout this plan (no Layer A test is added
  or removed in Plan 1).
- **Byte-identity gate:** `python3 generator/generate_rules.py --class 1`,
  `--class 2`, `--class 3` leave `git status --porcelain rules/` empty. Plan 1 changes
  no generator or rule file.
- **30 s corpus cap STAYS.** Layer B runs use `test/corpus_driver.py` for all three
  classes (the generalized driver; the class-1 driver is a shim).
- **Bash tool cap 120 s:** long runs go through `setsid … &` and are polled; never
  block a tool call on a corpus run.
- **Git:** no `git add -A` (the tree carries untracked campaign logs/baselines);
  commit messages end with the `Claude-Session:` trailer, no `Co-Authored-By`;
  push only when asked; default branch `master`.
- **Test protocol:** every suite prints `PASS:`/`FAIL:` lines and ends with
  `Results: <n> passed, <m> failed`; a missing Results line is a failure.
- **Tree notation (shared by every task):** a tree is an atom — integer, ratio,
  double-float, complex, string, or symbol in package `MRS` (case preserved) — or a
  list `(head arg…)` whose head is a tree. Mathematica heads are the symbols
  `MRS::|Plus|`, `MRS::|Times|`, `MRS::|Power|`, … Text form = the probe-02
  s-expressions (`rd.to_sexp`): ratios `n/d`, complex `#C(re im)`.
- **Matcher semantics oracle:** `verify()` in `probes/matcher/02-roundtrip.py`
  (narrow reading; `WIDE` for the wide reading). `mr-match` must agree with it.

## File structure

| file | responsibility | task |
|---|---|---|
| `probes/matcher/02-mma-reader.py` (modify `key`) | float atoms in the total order | 1 |
| `probes/matcher/02-construct-census.py` (modify) | Plus/Times node census section | 1 |
| `probes/matcher/03-*` (commit) | expression-model probe, three arms | 1 |
| `test/record_medians.py` (create) | per-record entry count, PASS count, median/p90 wall | 2 |
| `test/test_record_medians.py` (create) | its checks | 2 |
| `test/corpus_class{1,2,3}.pre-matcher.out` (create) | P0 baseline records | 3–4 |
| `.superpowers/sdd/progress.md` (append section `## Plan: 2026-09-12 matcher substrate plan 1`) | migration ledger (P0 numbers, per-task gate outcomes) | 4–8 |
| `maxima_rubi_match.lisp` (create) | package `MR-MATCH`: trees, canonical order, `prepare`, `match`, `match-flat` | 5 |
| `test/matcher/test_mr_match.lisp` + `.mac` (create) | matcher unit tests | 5 |
| `probes/matcher/02-roundtrip.py` (modify) | `MR_MODES` / `MR_LEGS` env for the judge (defaults = probe 02 as committed) | 6 |
| `test/matcher/roundtrip.lisp` / `roundtrip.mac` (create) | round trip through `mr-match` (tree leg; maxima leg from Task 8) | 6, 8 |
| `test/matcher/controls.lisp` / `controls.mac` (create) | 02 controls through `mr-match` | 6 |
| `test/matcher/gate.py` (create) | reads the judge/controls/spike outputs, prints the gate `Results:` | 6 |
| `test/matcher/run.sh` (create) | the suite runner: gen → shards → judge → controls → gate | 6, 8 |
| `test/matcher/{roundtrip,controls,gate}.out` (commit) | the committed gate evidence | 6, 8 |
| `maxima_rubi_tree.lisp` (create) | package `MR-TREE`: `max->tree`, `tree->max`, head table | 7 |
| `test/matcher/test_mr_tree.lisp` + `.mac` (create) | converter unit tests | 7 |
| `test/matcher/spike01.lisp` / `spike01.mac` (create) | spike-01 cases through `mr-match` + `mr-tree` | 8 |

## Task overview

| task | phase | deliverable | gate |
|---|---|---|---|
| 1 | P0 | probe 03 fixed + committed; node census committed | reader selftest 27/27; census re-run diff = new section only |
| 2 | P0 | `test/record_medians.py` | its checks green |
| 3 | P0 | three full corpus runs on the campaign's final tree | merges complete 25,697 / 965 / 3,085 |
| 4 | P0 | campaign closed; `matcher-substrate` branch; baseline records + ledger | fingerprint unchanged; Layer A 892/0 |
| 5 | P1 | `mr-match` (ordered core, `match-flat`, switches, condition hook) | unit tests 48/0 |
| 6 | P1 | matcher regression suite (tree leg + controls) | P1 gate (spec §4) |
| 7 | P2 | `mr-tree` | unit tests green |
| 8 | P2 | Maxima leg (defaults + flags arm) + spike-01 cases | P2 gate (spec §4) |

**Pre-validation (plan-writing session, 2026-09-12, throwaway prototypes in the
session scratchpad, not committed):** the Task 5 matcher and Task 6 runner code below
was run before this plan was written — unit tests 48/0 under SBCL 2.6.7 and inside
Maxima batch; the full tree-leg round trip (7,444 rules, 20 SBCL shards) judged
by probe 02's judge with the Task 6 patch: narrow and wide 7,444/7,444 rules with
every positive OK, 0 UNSOUND, 0 false mutation matches, narrow collapsed witnesses
0 FALSE, wide 2,041 WIDE-OK, single-match p50 0.005 ms / max 15.6 ms; gate 35/0.
The Task 7/8 code was run the same way: converter unit tests 46/0; round trip with the
Maxima leg (20 Maxima shards) — defaults arm MODEL-LOST narrow 1,166 variants / 395
rules, wide 1,046 / 307, flags arm 23 / 4, 0 UNSOUND everywhere; spike-01 69/69 gated
cases; gate 107/0 on both arms. Two converter bugs were found and fixed on the way
(Maxima's case inversion of `mm_sin`; `polylog(n,x)` staying `$polylog`), each now a
unit test. Tasks 6 and 8 re-measure all of it and commit the evidence — the numbers
here are expectations, not citations.

---

### Task 1: Probe hygiene — reader float order, probe 03 re-run, node census

Branch: `matcher-spike` (the probe 03 files are untracked there).

**Files:**
- Modify: `probes/matcher/02-mma-reader.py` (`key()`, `_selftest()`)
- Modify: `probes/matcher/02-construct-census.py` (`main()`, after the "(ii) Optionals" table)
- Regenerate: `probes/matcher/02-construct-census.out`, `probes/matcher/03-model-touch.out`,
  `probes/matcher/03-model-touch.radexpand-logexpand.out`, `probes/matcher/03-model-touch.domain-complex.out`
- Commit (already present, untracked): `probes/matcher/03-model-touch.py`, `probes/matcher/03-simp-flags.mac`, `probes/matcher/03-simp-flags.out`

**Interfaces:** none consumed; produces the committed evidence the spec cites in §0.2 / §2.1 / §2.2.

- [ ] **Step 1: Add the failing self-test check**

In `probes/matcher/02-mma-reader.py` `_selftest()`, replace the last two lines of the function body

```python
    print("Results: %d passed, %d failed" % (len(cases) + 1 - bad, bad))
    return bad
```

with

```python
    # key() is a total order over mixed atoms: 02-roundtrip.parse_sexp yields
    # Python floats that sort next to symbols (03-model-touch, 2.3 e194 L219)
    try:
        sorted([("Times", "x", 0.1), "x", 0.1, Fraction(1, 3), 2], key=key)
        ok = True
    except TypeError:
        ok = False
    bad += not ok
    print("%s key() orders a float among symbols" % ("PASS:" if ok else "FAIL:"))
    print("Results: %d passed, %d failed" % (len(cases) + 2 - bad, bad))
    return bad
```

- [ ] **Step 2: Run it — expect exactly one failure**

Run: `python3 probes/matcher/02-mma-reader.py | tail -3`
Expected: `FAIL: key() orders a float among symbols` and `Results: 26 passed, 1 failed`.

- [ ] **Step 3: Fix `key()`**

In `key(e)`, directly after the `Real` branch

```python
    if isinstance(e, Real):
        return (1, e.text)
```

insert

```python
    if isinstance(e, float):
        return (1, repr(e))
```

- [ ] **Step 4: Re-run the self-tests**

Run: `python3 probes/matcher/02-mma-reader.py | tail -1 && python3 probes/matcher/02-roundtrip.py selftest | tail -1`
Expected: `Results: 27 passed, 0 failed` and `Results: 14 passed, 0 failed` (the round-trip self-test is unaffected).

- [ ] **Step 5: Re-run probe 03, all three arms, in the background**

```bash
cd /home/serge/src/maxima-rubi
setsid sh -c 'python3 probes/matcher/03-model-touch.py > probes/matcher/03-model-touch.out 2>&1; \
  python3 probes/matcher/03-model-touch.py --flags "radexpand:false\$ logexpand:false\$" > probes/matcher/03-model-touch.radexpand-logexpand.out 2>&1; \
  python3 probes/matcher/03-model-touch.py --flags "domain:complex\$" > probes/matcher/03-model-touch.domain-complex.out 2>&1; \
  echo done > /tmp/claude-mr-03.done' > /dev/null 2>&1 &
```

Poll (≤ 110 s per call) until `/tmp/claude-mr-03.done` exists.

- [ ] **Step 6: Check the three outputs**

Run: `grep -c 'TypeError' probes/matcher/03-model-touch*.out; grep -E '^(settings|SECTION ALL)' probes/matcher/03-model-touch*.out`
Expected: `0` for each file; the `settings before the probe:` lines read `(Maxima defaults)`,
`radexpand:false$ logexpand:false$`, `domain:complex$`; each `SECTION ALL` reports
`failures {}` and compares 29,747 entries. Record the three "stored differently" totals —
if any differs from the spec's 614 / 47 / 42 by more than the one previously failing
entry, stop and report (the spec §2.2 figures would need a correction commit).

- [ ] **Step 7: Add the Plus/Times node census**

In `probes/matcher/02-construct-census.py` `main()`, directly after the call

```python
    table("(ii) Optionals by parent head and count directly under that head (#heads-occurrences)",
          [(h, n, c) for (h, n), c in sorted(opt_hist.items(), key=lambda kv: (-kv[1], kv[0]))],
          ["parent head", "#Optionals among its arguments", "#occurrences"])
```

insert

```python
    # (ii-b) what sits directly under each Plus/Times pattern node -- sizes the
    # matcher's match-flat search (matcher substrate spec section 3.2)
    def flat_nodes(e):
        if isinstance(e, tuple):
            if e[0] in ("Plus", "Times"):
                yield e
            for a in e:
                yield from flat_nodes(a)

    node_hist = Counter()            # (head, #bare, #optional, #structured) -> #nodes
    two_bare = defaultdict(list)     # head -> rules with a node carrying >= 2 bare blanks
    max_struct = 0
    for r in ok:
        heads_two = set()
        for node in flat_nodes(r.lhs_eval[1]):
            bare = opt = struct = 0
            for a in node[1:]:
                if isinstance(a, tuple) and a[0] == "Optional":
                    opt += 1
                elif isinstance(a, tuple) and a[0] == "Pattern" and a[2] == ("Blank",):
                    bare += 1
                elif isinstance(a, tuple):
                    struct += 1
            node_hist[(node[0], bare, opt, struct)] += 1
            max_struct = max(max_struct, struct)
            if bare >= 2:
                heads_two.add(node[0])
        for h in heads_two:
            two_bare[h].append(r.id)
    table("(ii-b) Plus/Times pattern nodes by what sits directly under them",
          [(h, b, o, s, c) for (h, b, o, s), c in
           sorted(node_hist.items(), key=lambda kv: (kv[0][0], -kv[1]))],
          ["head", "#bare named blanks x_", "#Optionals x_.", "#structured children", "#nodes"])
    print("largest number of structured children directly under one Plus/Times node: %d" % max_struct)
    print("largest number of Optionals directly under one Plus/Times node: %d" %
          max((o for (_h, _b, o, _s) in node_hist), default=0))
    union_two = sorted({i for ids in two_bare.values() for i in ids})
    print("rules with a Plus/Times node carrying >= 2 bare named blanks: %d (%s) -- %s" % (
        len(union_two), ", ".join("%s %d" % (h, len(two_bare[h])) for h in sorted(two_bare)),
        ids_str(union_two, 5)))
```

- [ ] **Step 8: Re-run the census and check the diff is additive**

Run:
```bash
python3 probes/matcher/02-construct-census.py > probes/matcher/02-construct-census.out
git diff probes/matcher/02-construct-census.out | grep -E '^-[^-]'
```
Expected: exactly one removed line — the `=== probes/matcher/02-construct-census  run:` timestamp.
Then `grep -A3 'largest number of structured' probes/matcher/02-construct-census.out`
shows the three summary lines; the Optionals maximum must be 1 and the structured maximum
≤ 5 (spec §2.1 relies on both). If either is violated, stop and report.

- [ ] **Step 9: Commit**

```bash
git add probes/matcher/02-mma-reader.py probes/matcher/02-construct-census.py probes/matcher/02-construct-census.out \
  probes/matcher/03-model-touch.py probes/matcher/03-model-touch.out probes/matcher/03-model-touch.radexpand-logexpand.out \
  probes/matcher/03-model-touch.domain-complex.out probes/matcher/03-simp-flags.mac probes/matcher/03-simp-flags.out
git commit -m "$(printf 'probe: matcher 03 expression model on the corpus (3 simplifier arms) + Plus/Times node census\n\nreader key() orders Python floats (fixes the 2.3 e194 PARSE:TypeError);\n02-construct-census gains section (ii-b), the per-node census the\nmatcher substrate spec section 3.2 is sized against.\n\nClaude-Session: https://claude.ai/code/session_01D5eoebxrtMKBBUSqYf2MGa')"
```

---

### Task 2: `test/record_medians.py` — per-record wall summary

Branch: `matcher-spike`.

**Files:**
- Create: `test/record_medians.py`
- Test: `test/test_record_medians.py`

**Interfaces:**
- Consumes: `test/ab_records.py` — `load_record(path) -> {(rel, entry): (class, seconds)}`,
  `driver_pass_classes() -> set[str]`.
- Produces: `summarize(path, pass_classes) -> dict` with keys `entries`, `pass`, `median`,
  `p90`, `timeouts`; CLI line
  `<path>: entries <n>  PASS <p>  median <m>s  p90 <q>s  timeout <t>` (seconds with one decimal).
  Plan 3's performance gate reads this line.

- [ ] **Step 1: Write the failing test**

Create `test/test_record_medians.py`:

```python
#!/usr/bin/env python3
"""Checks for test/record_medians.py (no Maxima; synthetic records).

  1. summarize(): entries, PASS count (driver PASS_CLASSES), median, p90,
     timeout count on an odd-sized record.
  2. median of an even-sized record is the mean of the two middle values.
  3. CLI prints one summary line per record, in the documented format.

Re-runnable:  python3 test/test_record_medians.py
"""

import importlib.util
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("record_medians", os.path.join(HERE, "record_medians.py"))
rm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rm)

HEADER = "=== maxima-rubi class3 corpus run (full, 24 shards merged) ===\nfilter: '3 Logarithms/'\n\n"
ODD = HEADER + """\
verified       t=   1.0s 3 Logarithms/a b.mac e1 L10
verified       t=   2.0s 3 Logarithms/a b.mac e2 L11
deferred       t=   3.0s 3 Logarithms/a b.mac e3 L12
no-answer      t=   4.0s 3 Logarithms/a b.mac e4 L13
timeout        t=  30.0s 3 Logarithms/a b.mac e5 L14
Results: 3 passed, 2 failed
"""
EVEN = HEADER + """\
verified       t=   1.0s 3 Logarithms/a b.mac e1 L10
verified       t=   2.0s 3 Logarithms/a b.mac e2 L11
verified       t=   4.0s 3 Logarithms/a b.mac e3 L12
verified       t=   9.0s 3 Logarithms/a b.mac e4 L13
"""


def write(tmp, name, text):
    p = os.path.join(tmp, name)
    with open(p, "w") as f:
        f.write(text)
    return p


def main():
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        odd, even = write(tmp, "odd.out", ODD), write(tmp, "even.out", EVEN)
        s = rm.summarize(odd, rm.ab.driver_pass_classes())
        want = {"entries": 5, "pass": 3, "median": 3.0, "p90": 30.0, "timeouts": 1}
        print(("PASS:" if s == want else "FAIL:"), "summarize odd record", s)
        if s != want:
            failures.append("summarize odd")
        s = rm.summarize(even, rm.ab.driver_pass_classes())
        ok = s["median"] == 3.0 and s["entries"] == 4
        print(("PASS:" if ok else "FAIL:"), "even median", s)
        if not ok:
            failures.append("even median")
        out = subprocess.run([sys.executable, os.path.join(HERE, "record_medians.py"), odd, even],
                             capture_output=True, text=True).stdout.splitlines()
        want_line = f"{odd}: entries 5  PASS 3  median 3.0s  p90 30.0s  timeout 1"
        ok = len(out) == 2 and out[0] == want_line
        print(("PASS:" if ok else "FAIL:"), "CLI lines", out)
        if not ok:
            failures.append("cli")
    print(f"Results: {3 - len(failures)} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run it — expect it to fail**

Run: `python3 test/test_record_medians.py`
Expected: a `FileNotFoundError` traceback for `record_medians.py` (no `Results:` line).

- [ ] **Step 3: Implement**

Create `test/record_medians.py`:

```python
#!/usr/bin/env python3
"""Per-record wall-time summary of merged corpus records.

The matcher substrate migration's performance gate (spec
docs/superpowers/specs/2026-09-12-matcher-substrate-design.md section 4)
compares the per-class median per-entry wall of a new record with the P0
baseline. For each record this prints: entries, PASS count (the driver's
PASS_CLASSES, read through test/ab_records.py), median and p90 of the t=
field over ALL entries, and the timeout count.

Usage:  python3 test/record_medians.py RECORD [RECORD ...]
"""

import importlib.util
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("ab_records", os.path.join(HERE, "ab_records.py"))
ab = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ab)


def summarize(path, pass_classes):
    rec = ab.load_record(path)
    times = sorted(t for _cls, t in rec.values())
    n = len(times)
    return {
        "entries": n,
        "pass": sum(1 for cls, _t in rec.values() if cls in pass_classes),
        "median": statistics.median(times) if n else 0.0,
        "p90": times[min(n - 1, int(0.9 * n))] if n else 0.0,
        "timeouts": sum(1 for cls, _t in rec.values() if cls == "timeout"),
    }


def main(argv):
    if not argv:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 64
    pass_classes = ab.driver_pass_classes()
    for path in argv:
        s = summarize(path, pass_classes)
        print(f"{path}: entries {s['entries']}  PASS {s['pass']}  median {s['median']:.1f}s  "
              f"p90 {s['p90']:.1f}s  timeout {s['timeouts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run the test**

Run: `python3 test/test_record_medians.py`
Expected: three `PASS:` lines, `Results: 3 passed, 0 failed`.

- [ ] **Step 5: Smoke on a real record**

Run: `python3 test/record_medians.py test/corpus_class2.campaign-baseline.out`
Expected: `entries 965  PASS 594` (matches that record's `Results: 594 passed, 371 failed`).

- [ ] **Step 6: Commit**

```bash
git add test/record_medians.py test/test_record_medians.py
git commit -m "$(printf 'test: record_medians.py — per-record entries/PASS/median/p90/timeout summary\n\nThe matcher substrate performance gate reads the per-class median\nper-entry wall from merged records (spec section 4).\n\nClaude-Session: https://claude.ai/code/session_01D5eoebxrtMKBBUSqYf2MGa')"
```

---

### Task 3: Full three-class corpus runs on the campaign's final tree

Branch: any of `matcher-spike` / `class3-deferred` — both carry the same package,
utils, Lisp and rule files (the spike commits add only probes/docs). No commit in
this task; its outputs are committed in Task 4.

**Files:**
- Overwrite (working tree): `test/corpus_class1.out`, `test/corpus_class2.out` (the
  campaign's Task-5 Step-4 records)
- Create: `test/corpus_class3.pre-matcher.out` (fresh class-3 run; `test/corpus_class3.out`
  keeps the campaign's 2026-09-04 record)

**Interfaces:** produces the three merged records Task 4 commits and every later
A/B compares against.

- [ ] **Step 1: Pre-flight — core fingerprint and Layer A**

```bash
cd /home/serge/src/maxima-rubi
FP=$( { printf '%s\n' maxima_rubi.mac maxima_rubi_utils.mac maxima_rubi_dispatch.lisp \
        maxima_rubi_implicit1.lisp maxima_rubi_pass4.lisp
        ls rules/class1/*.mac rules/class2/*.mac rules/class3/*.mac
      } | LC_ALL=C sort | xargs -d '\n' cat | md5sum | cut -d' ' -f1 )
echo "tree $FP"; grep fingerprint test/mr_rules.core.stamp
maxima --very-quiet --batch-string='disp(build_info())$' | grep -E 'version|build date'
```
Expected: both fingerprints `5ef9b3bc5ee07ffac0e76f1fea54fbac`; build
`branch_5_50_base_84_g4204fb669`, `2026-08-31 13:27:47`. If the fingerprints differ,
stop: the core is stale for this tree (rebuild with `sh test/build_rules_core.sh`
only after reporting — the campaign's 2026-09-04 class-3 record was measured on
`5ef9b3bc…`).

Then run Layer A in the background and read its last line:
```bash
setsid sh -c 'maxima --very-quiet -X "--tls-limit 100000" -b test_maxima_rubi.mac > /tmp/claude-mr-layerA.out 2>&1' &
```
Poll until `/tmp/claude-mr-layerA.out` contains `Results:`; expected `Results: 892 passed, 0 failed`.

- [ ] **Step 2: Class 1 (~80 min wall)**

```bash
python3 test/launch_class_shards.py "1 Algebraic functions" test/corpus_class1.out test/corpus_driver.py --launch
setsid sh test/wait_and_merge.sh test/corpus_class1.shard-pids test/merge_class_shards.py test/class1_merge.out \
  "1 Algebraic functions" test/corpus_class1.out test/corpus_driver.py "corpus_class1.shard*.out" &
```
Poll `test/class1_merge.out` (every ≤ 110 s; the watcher writes `merge rc=` last).
Expected: `merge rc=0`, completeness 25,697/25,697, and `tail -1 test/corpus_class1.out`
is a `Results:` line.

- [ ] **Step 3: Class 2 (~8 min wall)** — only after Step 2's merge finished

```bash
python3 test/launch_class_shards.py "2 Exponentials" test/corpus_class2.out test/corpus_driver.py --launch
setsid sh test/wait_and_merge.sh test/corpus_class2.shard-pids test/merge_class_shards.py test/class2_merge.out \
  "2 Exponentials" test/corpus_class2.out test/corpus_driver.py "corpus_class2.shard*.out" &
```
Expected: `merge rc=0`, completeness 965/965.

- [ ] **Step 4: Class 3 (~28 min wall)** — only after Step 3's merge finished

```bash
python3 test/launch_class_shards.py "3 Logarithms" test/corpus_class3.out test/corpus_driver.py --launch
setsid sh test/wait_and_merge.sh test/corpus_class3.shard-pids test/merge_class_shards.py test/class3_premerge.out \
  "3 Logarithms" test/corpus_class3.pre-matcher.out test/corpus_driver.py "corpus_class3.shard*.out" &
```
(The second positional of the launcher is only the cost-balancing input; the merge
writes the new record to `test/corpus_class3.pre-matcher.out`.)
Expected: `merge rc=0`, completeness 3,085/3,085.

- [ ] **Step 5: Baseline copies, summaries, noise band**

```bash
cp test/corpus_class1.out test/corpus_class1.pre-matcher.out
cp test/corpus_class2.out test/corpus_class2.pre-matcher.out
python3 test/record_medians.py test/corpus_class1.pre-matcher.out test/corpus_class2.pre-matcher.out \
  test/corpus_class3.pre-matcher.out | tee /tmp/claude-mr-p0-medians.txt
python3 test/ab_records.py test/corpus_class3.out test/corpus_class3.pre-matcher.out > /tmp/claude-mr-p0-class3-noise.txt
sed -n '/PASS\/FAIL table/,/class transitions/p' /tmp/claude-mr-p0-class3-noise.txt
```
Expected: three summary lines with entries 25697 / 965 / 3085; the class-3 A/B (same
rules core, two runs) shows the run-to-run noise band — it is recorded in Task 4's
ledger entry, not gated.

---

### Task 4: Close the class-3 campaign; cut `matcher-substrate`; commit the baseline

**Files:**
- On `class3-deferred`: the campaign plan's Task 5/6 files —
  `test/corpus_class{1,2,3}.out`, `test/corpus_class{1,2,3}.campaign-baseline.out`,
  `docs/corpus-class3-deferred-uplift.md` (§4–§7), the ticket
  `.scratch/class1-ab-remainders/issues/04-matcher-backtracking-feasibility.md`,
  `todo/TODO.md`, `.superpowers/sdd/progress.md`
- On `matcher-substrate`: `test/corpus_class{1,2,3}.pre-matcher.out`,
  `.superpowers/sdd/progress.md` (new section)

**Interfaces:** produces branch `matcher-substrate` — the base of every later task —
and the ledger section `## Plan: 2026-09-12 matcher substrate plan 1` holding the P0
figures (per-class PASS, median, p90, timeouts; core fingerprint; build stamp).

- [ ] **Step 1: Switch to the campaign branch**

```bash
git switch class3-deferred
git status --short | head -20
```
Expected: the working-tree changes carried over are `test/corpus_class1.out`,
`test/corpus_class2.out`, `test/corpus_class3.out` (modified) plus untracked run
artifacts; the probe-01..04 and spec files are absent on this branch (they return on
`matcher-spike`).

- [ ] **Step 2: Execute the campaign plan's remaining steps**

Follow `docs/superpowers/plans/2026-08-30-class3-deferred-campaign.md` as written —
`### Task 5` Steps 3, 4 (A/B only: the class-1/2 runs are Task 3's), 5, 6, 7 and
`### Task 6` Steps 1–7 — with these deltas, each stated in the record where it
applies:

1. A/B commands: `python3 test/ab_records.py test/corpus_class3.campaign-baseline.out test/corpus_class3.out`,
   and the same for classes 1 and 2 against their `.campaign-baseline.out`. Every
   PASS→FAIL is attributed in record §5 (the gate is unchanged).
2. The five deferred C6 mechanism groups (M-implicit1, M-plus-identity,
   M-barelog-optional, M-factored-quad, M-323 — `handoffs/2026-09-02-class3-deferred-remaining.md`
   T6) are recorded in §4/§6 as **out of campaign scope, superseded by the matcher
   substrate** (user decision 2026-09-11: close at the current state; spec
   `docs/superpowers/specs/2026-09-12-matcher-substrate-design.md` §0.1).
3. Record §4 lists what landed per sub-brief with its commits (B1 `464d29f`+`2838c3a`,
   B2 `d6cee4e`, B4 `3c04b2e`, C2 `52ffb6f`, C1 `2fd677a`+`5fd0dce`, C4 `d2ae62d`,
   C3 `1c8a306`, B3 `9533528`, C5 `4702d4d`, C6 `c25e8f6`+`69b3de1`, C6b `99e1eb1`).
4. Layer A figure: 892 (the campaign plan's "743" constraint predates the campaign's
   tests).
5. The campaign's C6 ledger entry exists already (progress.md tail); Task 6 Step 6
   adds only the final acceptance entry.

- [ ] **Step 3: Assert the close changed nothing the runs depend on**

Re-run the Task 3 Step 1 fingerprint command. Expected: still
`5ef9b3bc5ee07ffac0e76f1fea54fbac` on both lines.

- [ ] **Step 4: Ask the user about `master`**

Ask (AskUserQuestion): "The class-3 campaign is closed on `class3-deferred`. Merge it
into `master` now?" Merge (`git switch master && git merge --no-ff class3-deferred`)
only on a yes; never push.

- [ ] **Step 5: Carry the close into the spike branch and cut the implementation branch**

```bash
git switch matcher-spike
git merge --no-ff class3-deferred -m "$(printf 'merge: class3-deferred (campaign closed) into matcher-spike\n\nClaude-Session: https://claude.ai/code/session_01D5eoebxrtMKBBUSqYf2MGa')"
git switch -c matcher-substrate
```
Expected: the merge is conflict-free (the spike commits touch only `probes/matcher/`,
`docs/superpowers/specs/`, `todo/TODO.md` reference pins). If `todo/TODO.md` conflicts,
keep both sides' lines.

- [ ] **Step 6: Write the ledger section**

Append to `.superpowers/sdd/progress.md`:

```markdown
## Plan: 2026-09-12 matcher substrate plan 1 (P0–P2; branch matcher-substrate)

Spec: docs/superpowers/specs/2026-09-12-matcher-substrate-design.md
Plan: docs/superpowers/plans/2026-09-12-matcher-substrate-plan1.md

### P0 baseline (Task 3 runs; campaign final tree)
- build: branch_5_50_base_84_g4204fb669 / 2026-08-31 13:27:47 / SBCL 2.6.7
- rules core fingerprint: 5ef9b3bc5ee07ffac0e76f1fea54fbac (unchanged by the campaign close)
- Layer A: <paste the Results line>
- <paste the three record_medians.py lines from /tmp/claude-mr-p0-medians.txt>
- class-3 run-to-run noise (2026-09-04 record vs pre-matcher, same core): <paste the 2x2 table>
- P5 gates read from here: per-class PASS floor = the PASS figures above; per-class
  median ceiling = the median figures above.
```

Fill every `<paste …>` with the literal output (the section must contain numbers,
not placeholders, when committed).

- [ ] **Step 7: Commit the baseline**

```bash
git add test/corpus_class1.pre-matcher.out test/corpus_class2.pre-matcher.out test/corpus_class3.pre-matcher.out \
  .superpowers/sdd/progress.md
git commit -m "$(printf 'record: matcher substrate P0 baseline — classes 1-3 on the closed campaign tree\n\nCore 5ef9b3bc, build 2026-08-31; per-class PASS and median wall in the\nledger (the P5 parity floor and performance ceiling).\n\nClaude-Session: https://claude.ai/code/session_01D5eoebxrtMKBBUSqYf2MGa')"
```

---

### Task 5: `mr-match` — the matcher core (P1)

Branch: `matcher-substrate`.

**Files:**
- Create: `maxima_rubi_match.lisp`
- Create: `test/matcher/test_mr_match.lisp`, `test/matcher/test_mr_match.mac`

**Interfaces:**
- Consumes: nothing (no Maxima dependency; loads into Maxima's SBCL or plain SBCL 2.6.7).
- Produces — package `MR-MATCH` (exported), relied on by Tasks 6–8 and Plan 2:
  - `(sym name) -> symbol` interned in package `MRS`.
  - `(read-tree string) -> tree`; `(read-pattern string) -> tree` (compact `x_`, `x_.`, `x_H` expanded);
    `(tree-string tree) -> string` (probe-02 s-expression text).
  - `(head-of tree) -> symbol` (`Integer`, `Rational`, `Real`, `Complex`, `String`, `Symbol` for atoms).
  - `(tree< a b) -> boolean` total order; `(canonicalize tree) -> tree` (Plus/Times arguments sorted by `tree<`).
  - `(prepare pattern-tree) -> compiled-pattern`; accessors `compiled-pattern-tree`
    (Optionals carry their default as a third element), `compiled-pattern-vars`.
    Signals `error` on unsupported constructs.
  - `(match compiled expr &key bindings cond-hook) -> (values alist matchedp)`; `expr` must be canonical;
    `bindings` pre-binds names (`((name . value) …)`); `cond-hook` is called with each complete binding alist.
  - Specials: `*flat-wide*` (default nil — G-6 narrow), `*cond-retry*` (default t),
    `*test-hook*` (`(lambda (kind test expr bindings))`, kind `:condition`/`:pattern-test`; default rejects).

- [ ] **Step 1: Write the failing unit tests**

Create `test/matcher/test_mr_match.mac`:

```maxima
/* test/matcher/test_mr_match.mac -- MR-MATCH unit tests.
   From the repo root:  maxima --very-quiet -b test/matcher/test_mr_match.mac
   No rule files are loaded, so no --tls-limit flag.  Ends with a Results: line. */
load("maxima_rubi_match.lisp")$
load("test/matcher/test_mr_match.lisp")$
:lisp (mr-match-test:run)
```

Create `test/matcher/test_mr_match.lisp`:

```lisp
;;;; test/matcher/test_mr_match.lisp -- MR-MATCH unit tests.
;;;; Run: maxima --very-quiet -b test/matcher/test_mr_match.mac
;;;; Ends with "Results: <n> passed, <m> failed".

(defpackage :mr-match-test (:use :cl :mr-match) (:export #:run))
(in-package :mr-match-test)

(defvar *passed* 0)
(defvar *failed* 0)

(defun check (name ok &optional detail)
  (if ok
      (progn (incf *passed*) (format t "  PASS: ~a~%" name))
      (progn (incf *failed*) (format t "  FAIL: ~a~@[~%    ~a~]~%" name detail))))

(defun tr (s) (read-tree s))

(defun m (pattern-string expr-string &key pre cond-hook)
  "Match a compact pattern against a canonicalized tree; PRE names symbols
pre-bound to themselves (the integration variable)."
  (match (prepare (read-pattern pattern-string))
         (canonicalize (tr expr-string))
         :bindings (mapcar (lambda (n) (cons (sym n) (sym n))) pre)
         :cond-hook cond-hook))

(defun bound (alist name) (cdr (assoc (sym name) alist)))

(defun binds-p (alist &rest pairs)
  "PAIRS: name value-string ...; every name bound to the tree of its string."
  (loop for (n v) on pairs by #'cddr
        always (equal (bound alist n) (canonicalize (tr v)))))

(defmacro check-match (name (pattern expr &rest keys) &rest pairs)
  `(multiple-value-bind (b ok) (m ,pattern ,expr ,@keys)
     (check ,name (and ok (binds-p b ,@pairs)) (format nil "matched=~a bindings=~a" ok (tree-string b)))))

(defmacro check-no-match (name (pattern expr &rest keys))
  `(multiple-value-bind (b ok) (m ,pattern ,expr ,@keys)
     (check ,name (not ok) (format nil "unexpected match ~a" (tree-string b)))))

(defun count-bindings (pattern expr &key pre)
  (let ((n 0))
    (m pattern expr :pre pre :cond-hook (lambda (b) (declare (ignore b)) (incf n) nil))
    n))

(defun test-trees ()
  (format t "--- trees ---~%")
  (let ((e (tr "(Power x 1/2)")))
    (check "read-tree keeps case and ratios"
           (and (eq (first e) (sym "Power")) (eq (second e) (sym "x")) (eql (third e) 1/2))))
  (check "tree-string round trip"
         (string= (tree-string (tr "(Times -1 #C(0 2) 1/3 x)")) "(Times -1 #C(0 2) 1/3 x)"))
  (check "canonicalize sorts Plus/Times arguments only"
         (equal (canonicalize (tr "(Plus x 2 (Times b a) (f b a))"))
                (tr "(Plus 2 x (Times a b) (f b a))")))
  (check "tree< is a strict order on equal trees" (not (tree< (tr "(f x)") (tr "(f x)"))))
  (check "read-pattern expands x_ x_. x_H"
         (equal (read-pattern "(f x_ m_. y_Symbol)")
                (tr "(f (Pattern x (Blank)) (Optional (Pattern m (Blank))) (Pattern y (Blank Symbol)))")))
  (check "head-of atoms"
         (equal (mapcar #'head-of (list 3 1/2 0.5d0 #C(0 1) "s" (sym "x") (tr "(Sin x)")))
                (mapcar #'sym '("Integer" "Rational" "Real" "Complex" "String" "Symbol" "Sin")))))

(defun test-prepare ()
  (format t "--- prepare ---~%")
  (check "Optional defaults from the parent"
         (equal (compiled-pattern-tree (prepare (read-pattern "(Power (Plus a_. (Times b_. x_)) m_.)")))
                (tr "(Power (Plus (Optional (Pattern a (Blank)) 0) (Times (Optional (Pattern b (Blank)) 1) (Pattern x (Blank)))) (Optional (Pattern m (Blank)) 1))")))
  (check "variables collected in order"
         (equal (compiled-pattern-vars (prepare (read-pattern "(Plus a_. (Times b_. x_))")))
                (mapcar #'sym '("a" "b" "x"))))
  (flet ((rejects (s) (handler-case (progn (prepare (read-pattern s)) nil) (error () t))))
    (check "rejects Alternatives" (rejects "(Alternatives x_ y_)"))
    (check "rejects a sequence blank under Plus" (rejects "(Plus (Pattern x (BlankSequence)) y)"))
    (check "rejects an Optional under Sin" (rejects "(Sin x_.)"))))

(defun test-ordered ()
  (format t "--- ordered core ---~%")
  (check-match "literal atom" ("3" "3"))
  (check-no-match "different atom" ("3" "4"))
  (check-match "typed blank x_Symbol" ("x_Symbol" "x") "x" "x")
  (check-no-match "typed blank rejects a number" ("x_Symbol" "3"))
  (check-match "repeated name" ("(f x_ x_)" "(f a a)") "x" "a")
  (check-no-match "repeated name must agree" ("(f x_ x_)" "(f a b)"))
  (check-no-match "pre-bound name" ("(f x_)" "(f y)" :pre '("x")))
  (check-match "H1 pattern-variable head" ("(Int (F_ x_) x_Symbol)" "(Int (F x) x)") "F" "F" "x" "x")
  (check-match "H7 compound head" ("(Int (((Derivative n_) f_) x_) x_Symbol)" "(Int (((Derivative 2) f) x) x)")
               "n" "2" "f" "f")
  (check-match "Power exponent explicit" ("(Power x_ m_.)" "(Power y 3)") "x" "y" "m" "3")
  (check-match "Power exponent default through the base" ("(Power x_ m_.)" "y") "x" "y" "m" "1")
  (check-no-match "non-optional exponent needs a Power" ("(Power x_ m_)" "y"))
  (check-match "BlankSequence in order" ("(f a (Pattern x (BlankSequence)) d)" "(f a b c d)")
               "x" "(Sequence b c)")
  (check-match "BlankNullSequence may be empty" ("(f (Pattern x (BlankNullSequence)) a)" "(f a)")
               "x" "(Sequence)")
  (check-match "Complex pattern vs complex atom" ("(Complex 0 fz_)" "#C(0 2)") "fz" "2")
  (let ((*test-hook* (lambda (kind test e b)
                       (declare (ignore test e))
                       (and (eq kind :condition) (> (bound b "x") 2)))))
    (check-match "Condition hook accepts" ("(Condition x_ (Greater x 2))" "3") "x" "3")
    (check-no-match "Condition hook rejects" ("(Condition x_ (Greater x 2))" "1"))))

(defun test-flat ()
  (format t "--- match-flat ---~%")
  (check-match "Times Optional default" ("(Times b_. x_)" "x" :pre '("x")) "b" "1")
  (check-match "Plus/Times explicit" ("(Plus a_. (Times b_. x_))" "(Plus 3 (Times 2 x))" :pre '("x")) "a" "3" "b" "2")
  (check-match "Plus/Times all defaults" ("(Plus a_. (Times b_. x_))" "x" :pre '("x")) "a" "0" "b" "1")
  (check-match "blank takes the leftover run" ("(Times u_ (Power x_ 2))" "(Times a b (Power x 2))" :pre '("x"))
               "u" "(Times a b)")
  (check-match "blank takes a single leftover" ("(Times u_ (Power x_ 2))" "(Times a (Power x 2))" :pre '("x"))
               "u" "a")
  (check-no-match "G-1 N-15: a_ has no default (1.1.1.2.m L4)"
                  ("(Int (Times (Power (Plus a_ (Times b_. x_)) m_.) (Plus c_ (Times d_. x_))) x_Symbol)"
                   "(Int (Times (Power x m) (Plus c (Times d x))) x)" :pre '("x")))
  (check-no-match "G-1 N-07: d_ cannot match nothing (3.1.3.m L4)"
                  ("(Int (Times (Power (Plus d_ (Times e_. (Power x_ r_.))) q_.) (Plus a_. (Times b_. (Log (Times c_. (Power x_ n_.)))))) x_Symbol)"
                   "(Int (Times (Power x 5) (Plus a (Times b (Log (Times c (Power x n)))))) x)" :pre '("x")))
  (check-no-match "G-1: f_ has no default under Times" ("(Times f_ x_)" "x" :pre '("x")))
  (check-match "G-2 H2 pattern head under Times" ("(Int (Times u_ (F_ x_)) x_Symbol)" "(Int (Times u (F x)) x)")
               "u" "u" "F" "F")
  (check-match "G-2 H4 pattern head under Plus" ("(Int (Plus u_ (F_ x_)) x_Symbol)" "(Int (Plus u (F x)) x)")
               "u" "u" "F" "F")
  (check-match "G-2 H8 compound head under Times"
               ("(Int (Times u_ (((Derivative n_) f_) x_)) x_Symbol)" "(Int (Times u (((Derivative 2) f) x)) x)")
               "u" "u" "n" "2" "f" "f")
  (check-match "bound name consumes its parts" ("(Times a_ (Plus a_ x_))" "(Times c (Plus c x))" :pre '("x")) "a" "c")
  (check-no-match "bound name must be present" ("(Times a_ (Plus a_ x_))" "(Times c (Plus d x))" :pre '("x")))
  (check "two bare blanks: every split of three factors"
         (= 6 (count-bindings "(Times u_ v_)" "(Times a b c)"))
         (count-bindings "(Times u_ v_)" "(Times a b c)"))
  (check-match "narrow collapse: (c_.*x_)^m_. takes c*x inside a product (1.1.2.2.m L47)"
               ("(Times (Power (Times c_. x_) m_.) (Power (Plus a_ (Times b_. (Power x_ 2))) p_.))"
                "(Times c x (Power (Plus a (Times b (Power x 2))) p))" :pre '("x"))
               "c" "c" "m" "1" "a" "a" "b" "b" "p" "p")
  (let ((pat "(Times (Plus g_. (Times h_. x_)) (Sin x_))")
        (ex "(Times h x (Sin x))"))
    (check-no-match "G-6 narrow: Optional-reduced Plus does not take a run" (pat ex :pre '("x")))
    (let ((*flat-wide* t))
      (check-match "G-6 wide: Optional-reduced Plus takes a run" (pat ex :pre '("x")) "g" "0" "h" "h"))))

(defun test-hooks ()
  (format t "--- condition hook and retry ---~%")
  (let ((pat "(Times (Power (Plus a_. (Times b_. x_)) m_.) (Power (Plus c_. (Times d_. x_)) n_.))")
        (ex "(Times (Power (Plus 1 (Times 2 x)) 3) (Power (Plus 4 (Times 5 x)) 1/2))")
        (want-m-half (lambda (b) (eql (bound b "m") 1/2))))
    (check-match "retry finds the second assignment" (pat ex :pre '("x") :cond-hook want-m-half)
                 "m" "1/2" "a" "4" "b" "5" "n" "3")
    (let ((*cond-retry* nil))
      (check-no-match "no retry: the first complete binding is final" (pat ex :pre '("x") :cond-hook want-m-half)))
    (check "hook sees exactly the two complete bindings" (= 2 (count-bindings pat ex :pre '("x"))))))

(defun run ()
  (setf *passed* 0 *failed* 0)
  (test-trees)
  (test-prepare)
  (test-ordered)
  (test-flat)
  (test-hooks)
  (format t "Results: ~a passed, ~a failed~%" *passed* *failed*)
  (finish-output))
```

- [ ] **Step 2: Run the tests — expect failure**

Run: `maxima --very-quiet -b test/matcher/test_mr_match.mac 2>&1 | tail -5`
Expected: a load error for `maxima_rubi_match.lisp` / package `MR-MATCH` and **no** `Results:` line.

- [ ] **Step 3: Implement the matcher**

Create `maxima_rubi_match.lisp`:

```lisp
;;;; maxima_rubi_match.lisp -- MR-MATCH: structural pattern matcher with
;;;; Mathematica semantics for Rubi rule patterns.
;;;;
;;;; Design: docs/superpowers/specs/2026-09-12-matcher-substrate-design.md
;;;; section 3.2.  A re-implementation, in newmatch.lisp's continuation-passing
;;;; structure (m1 / ordered list / Pattern / Blank), of Fateman's mma4max
;;;; matcher (reference/fateman/lisp/mma4max/newmatch.lisp, 2011-03-21), without
;;;; its stack, evaluator (meval) or the constructs no Rubi LHS uses
;;;; (Alternatives, Except, Repeated, Action).  No Maxima dependency.
;;;;
;;;; Trees: an atom (integer, ratio, double-float, complex, string, or a symbol
;;;; in package MRS, case preserved) or a list (head arg ...) whose head is a
;;;; tree.  Bindings: an alist ((name . value) ...) threaded through
;;;; continuations -- nothing to unwind, no fixed-size stack.
;;;;
;;;; Semantics oracle: verify() in probes/matcher/02-roundtrip.py.

(defpackage :mrs (:use))

(defpackage :mr-match
  (:use :cl)
  (:export #:sym #:read-tree #:read-pattern #:tree-string #:head-of
           #:tree< #:canonicalize
           #:prepare #:compiled-pattern-p #:compiled-pattern-tree #:compiled-pattern-vars
           #:match #:*flat-wide* #:*cond-retry* #:*test-hook*))

(in-package :mr-match)

(defun sym (name) (intern name :mrs))

(defparameter +plus+ (sym "Plus"))
(defparameter +times+ (sym "Times"))
(defparameter +power+ (sym "Power"))
(defparameter +pattern+ (sym "Pattern"))
(defparameter +blank+ (sym "Blank"))
(defparameter +blank-seq+ (sym "BlankSequence"))
(defparameter +blank-null-seq+ (sym "BlankNullSequence"))
(defparameter +optional+ (sym "Optional"))
(defparameter +condition+ (sym "Condition"))
(defparameter +pattern-test+ (sym "PatternTest"))
(defparameter +complex+ (sym "Complex"))
(defparameter +sequence+ (sym "Sequence"))
(defparameter +integer+ (sym "Integer"))
(defparameter +rational+ (sym "Rational"))
(defparameter +real+ (sym "Real"))
(defparameter +string+ (sym "String"))
(defparameter +symbol+ (sym "Symbol"))

(defparameter +unsupported+
  (mapcar #'sym '("Alternatives" "Except" "Repeated" "RepeatedNull" "HoldPattern"
                  "Verbatim" "Longest" "Shortest" "PatternSequence" "OptionsPattern"
                  "KeyValuePattern" "OrderlessPatternSequence")))

(defvar *flat-wide* nil
  "G-6 switch (spec 3.6 mr_flat_wide): when true, a Plus/Times item whose
Optionals all take their defaults but one argument may take a run of the
parent's elements.  Default: the narrow reading.")

(defvar *cond-retry* t
  "Spec 3.6 mr_cond_retry: when true the condition hook is called on every
complete binding until it accepts one; when false the match ends at the first
complete binding.")

(defvar *test-hook* (lambda (kind test expr bindings)
                      (declare (ignore kind test expr bindings))
                      nil)
  "Called for Condition / PatternTest inside a pattern as
(funcall *test-hook* kind test expr bindings), kind :condition or
:pattern-test; a true result lets the match continue.  Default: fail closed.")

;;; ------------------------------------------------------------------
;;; reading, printing, heads, canonical order

(defvar *tree-readtable*
  (let ((rt (copy-readtable nil)))
    (setf (readtable-case rt) :preserve)
    rt))

(defun read-tree (string)
  (let ((*readtable* *tree-readtable*)
        (*package* (find-package :mrs))
        (*read-default-float-format* 'double-float)
        (*read-eval* nil))
    (read-from-string string)))

(defun expand-compact (tree)
  ;; x_ -> (Pattern x (Blank)); x_. -> (Optional (Pattern x (Blank)));
  ;; x_H -> (Pattern x (Blank H)).  Other symbols are left alone.
  (cond ((consp tree) (mapcar #'expand-compact tree))
        ((and tree (symbolp tree))
         (let* ((s (symbol-name tree)) (u (position #\_ s)))
           (if (or (null u) (zerop u))
               tree
               (let ((pat (list +pattern+ (sym (subseq s 0 u))))
                     (tail (subseq s (1+ u))))
                 (cond ((string= tail "") (append pat (list (list +blank+))))
                       ((string= tail ".") (list +optional+ (append pat (list (list +blank+)))))
                       (t (append pat (list (list +blank+ (sym tail))))))))))
        (t tree)))

(defun read-pattern (string)
  "Read a pattern in compact FullForm (x_, x_., x_H) into a full pattern tree."
  (expand-compact (read-tree string)))

(defun tree-string (tree)
  (with-output-to-string (s)
    (labels ((out (e)
               (cond ((null e) (write-string "()" s))
                     ((consp e)
                      (write-char #\( s)
                      (loop for (x . more) on e
                            do (out x) (when more (write-char #\Space s)))
                      (write-char #\) s))
                     ((complexp e)
                      (write-string "#C(" s) (out (realpart e)) (write-char #\Space s)
                      (out (imagpart e)) (write-char #\) s))
                     ((typep e 'ratio) (format s "~d/~d" (numerator e) (denominator e)))
                     ((integerp e) (format s "~d" e))
                     ((floatp e) (format s "~,,,,,,'eE" e))
                     ((stringp e) (prin1 e s))
                     ((symbolp e) (write-string (symbol-name e) s))
                     (t (format s "~a" e)))))
      (out tree))))

(defun head-of (e)
  (cond ((consp e) (car e))
        ((integerp e) +integer+)
        ((typep e 'ratio) +rational+)
        ((floatp e) +real+)
        ((complexp e) +complex+)
        ((stringp e) +string+)
        (t +symbol+)))

(defun rank (e)
  (cond ((realp e) 0) ((complexp e) 1) ((symbolp e) 2) ((stringp e) 3) (t 4)))

(defun real-kind (x) (typecase x (integer 0) (ratio 1) (t 2)))

(defun tree< (a b)
  "A total order on trees: numbers < complex < symbols < strings < lists."
  (let ((ra (rank a)) (rb (rank b)))
    (cond ((/= ra rb) (< ra rb))
          ((= ra 0) (or (< a b) (and (= a b) (< (real-kind a) (real-kind b)))))
          ((= ra 1) (or (tree< (realpart a) (realpart b))
                        (and (not (tree< (realpart b) (realpart a)))
                             (tree< (imagpart a) (imagpart b)))))
          ((= ra 2) (let ((na (symbol-name a)) (nb (symbol-name b)))
                      (or (string< na nb)
                          (and (string= na nb)
                               (string< (package-name (symbol-package a))
                                        (package-name (symbol-package b)))))))
          ((= ra 3) (and (string< a b) t))
          (t (cond ((tree< (car a) (car b)) t)
                   ((tree< (car b) (car a)) nil)
                   ((/= (length a) (length b)) (< (length a) (length b)))
                   (t (loop for x in (cdr a) for y in (cdr b)
                            when (tree< x y) return t
                            when (tree< y x) return nil
                            finally (return nil))))))))

(defun canonicalize (tree)
  "Sort the arguments of every Plus/Times node by tree< (nothing else changes)."
  (if (consp tree)
      (let ((args (mapcar #'canonicalize (cdr tree)))
            (head (canonicalize (car tree))))
        (cons head (if (or (eq head +plus+) (eq head +times+))
                       (stable-sort args #'tree<)
                       args)))
      tree))

;;; ------------------------------------------------------------------
;;; prepare: validate, fill Optional defaults, collect variable names

(defstruct (compiled-pattern (:constructor %make-compiled-pattern (tree vars)))
  tree vars)

(defun flat-head-p (h) (or (eq h +plus+) (eq h +times+)))
(defun seq-blank-head-p (h) (or (eq h +blank-seq+) (eq h +blank-null-seq+)))

(defun prepare (pattern)
  "Validate PATTERN (a full pattern tree), give every Optional its default from
its parent (Plus 0, Times 1, Power exponent 1), return a compiled-pattern."
  (let ((vars nil))
    (labels ((fail (fmt &rest args) (apply #'error (concatenate 'string "mr-match prepare: " fmt) args))
             (walk (p parent pos)
               (if (atom p)
                   p
                   (let ((h (car p)))
                     (cond
                       ((member h +unsupported+) (fail "unsupported construct ~a" (symbol-name h)))
                       ((eq h +optional+)
                        (unless (<= 2 (length p) 3) (fail "bad Optional ~a" (tree-string p)))
                        (let ((default (cond ((cddr p) (third p))
                                             ((eq parent +plus+) 0)
                                             ((eq parent +times+) 1)
                                             ((and (eq parent +power+) (eql pos 2)) 1)
                                             (t (fail "Optional without a default under ~a"
                                                      (if (symbolp parent) parent "a compound head")))))
                              (inner (second p)))
                          (unless (and (consp inner) (eq (car inner) +pattern+)
                                       (consp (third inner)) (eq (car (third inner)) +blank+))
                            (fail "Optional must wrap a named Blank: ~a" (tree-string p)))
                          (list +optional+ (walk inner parent pos) default)))
                       ((eq h +pattern+)
                        (unless (and (= (length p) 3) (symbolp (second p)))
                          (fail "bad Pattern ~a" (tree-string p)))
                        (pushnew (second p) vars)
                        (list +pattern+ (second p) (walk (third p) parent pos)))
                       ((or (eq h +blank+) (seq-blank-head-p h))
                        (unless (<= (length p) 2) (fail "bad blank ~a" (tree-string p)))
                        (when (and (seq-blank-head-p h) (flat-head-p parent))
                          (fail "sequence blank directly under ~a" (symbol-name parent)))
                        p)
                       ((or (eq h +condition+) (eq h +pattern-test+))
                        (unless (= (length p) 3) (fail "bad ~a" (symbol-name h)))
                        (list h (walk (second p) parent pos) (third p)))
                       (t (cons (walk h :head 0)
                                (loop for a in (cdr p) for i from 1
                                      collect (walk a h i)))))))))
      (let ((tree (walk pattern nil nil)))
        (%make-compiled-pattern tree (nreverse vars))))))

;;; ------------------------------------------------------------------
;;; match

(defun match (compiled expr &key bindings cond-hook)
  "Match COMPILED against EXPR (a canonical tree).  BINDINGS pre-binds names
(e.g. the integration variable).  COND-HOOK, if given, is called with each
complete binding alist; see *cond-retry*.  Returns (values alist matchedp)."
  (let ((result nil) (found nil))
    (m1 (compiled-pattern-tree compiled) expr bindings
        (lambda (b)
          (cond ((or (null cond-hook) (funcall cond-hook b))
                 (setf result b found t)
                 t)
                ((not *cond-retry*) t)
                (t nil))))
    (values result found)))

(defun optional-p (p) (and (consp p) (eq (car p) +optional+)))

(defun atom-match-p (p e)
  (or (eql p e) (and (stringp p) (stringp e) (string= p e))))

(defun blank-head-ok (blank e)
  (or (null (cdr blank)) (eq (second blank) (head-of e))))

(defun m1 (p e b k)
  (if (atom p)
      (and (atom-match-p p e) (funcall k b))
      (let ((h (car p)))
        (cond
          ((eq h +pattern+) (m-pattern (second p) (third p) e b k))
          ((eq h +blank+) (and (blank-head-ok p e) (funcall k b)))
          ((seq-blank-head-p h) nil)
          ((eq h +optional+) (m1 (second p) e b k))
          ((eq h +condition+)
           (m1 (second p) e b
               (lambda (b2) (and (funcall *test-hook* :condition (third p) e b2) (funcall k b2)))))
          ((eq h +pattern-test+)
           (m1 (second p) e b
               (lambda (b2) (and (funcall *test-hook* :pattern-test (third p) e b2) (funcall k b2)))))
          ((flat-head-p h) (match-flat p e b k))
          ((and (eq h +power+) (= (length p) 3)) (m-power p e b k))
          ((and (eq h +complex+) (complexp e) (= (length p) 3))
           (m-ordered (cdr p) (list (realpart e) (imagpart e)) b k))
          (t (and (consp e)
                  (m1 h (car e) b (lambda (b2) (m-ordered (cdr p) (cdr e) b2 k)))))))))

(defun m-pattern (name sub e b k)
  (let ((cell (assoc name b :test #'eq)))
    (if cell
        (and (equal (cdr cell) e) (m1 sub e b k))
        (m1 sub e (acons name e b) k))))

(defun seq-item-p (p)
  (and (consp p)
       (or (seq-blank-head-p (car p))
           (and (eq (car p) +pattern+) (consp (third p)) (seq-blank-head-p (car (third p)))))))

(defun m-ordered (pl el b k)
  (cond ((null pl) (and (null el) (funcall k b)))
        ((seq-item-p (car pl)) (m-seq pl el b k))
        ((null el) nil)
        (t (m1 (car pl) (car el) b (lambda (b2) (m-ordered (cdr pl) (cdr el) b2 k))))))

(defun m-seq (pl el b k)
  (let* ((p (car pl))
         (name (and (eq (car p) +pattern+) (second p)))
         (blank (if name (third p) p))
         (least (if (eq (car blank) +blank-seq+) 1 0))
         (head (second blank)))
    (loop for n from least to (length el)
          for taken = (subseq el 0 n)
          while (or (null head) (every (lambda (x) (eq (head-of x) head)) taken))
          thereis (let ((value (if (= n 1) (car taken) (cons +sequence+ taken)))
                        (rest (nthcdr n el)))
                    (if name
                        (let ((cell (assoc name b :test #'eq)))
                          (if cell
                              (and (equal (cdr cell) value) (m-ordered (cdr pl) rest b k))
                              (m-ordered (cdr pl) rest (acons name value b) k)))
                        (m-ordered (cdr pl) rest b k))))))

(defun power-p (e) (and (consp e) (eq (car e) +power+) (= (length e) 3)))

(defun m-power (p e b k)
  (let ((base (second p)) (ex (third p)))
    (if (optional-p ex)
        ;; b^m_. : in order against a Power, else (or then) through the base with m = default
        (or (and (power-p e)
                 (m1 base (second e) b (lambda (b2) (m1 (second ex) (third e) b2 k))))
            (m1 (second ex) (third ex) b (lambda (b2) (m1 base e b2 k))))
        (and (power-p e)
             (m1 base (second e) b (lambda (b2) (m1 ex (third e) b2 k)))))))

;;; ------------------------------------------------------------------
;;; match-flat: Plus / Times (Flat + Orderless)

(defun bare-blank-p (p)
  (and (consp p)
       (or (equal p (list +blank+))
           (and (eq (car p) +pattern+) (equal (third p) (list +blank+))))))

(defun absorber-p (item) (or (optional-p item) (bare-blank-p item)))

(defun remove-nth (n list)
  (append (subseq list 0 n) (nthcdr (1+ n) list)))

(defun map-subsets (size list fn)
  "Call (FN chosen rest) for each SIZE-element sub-list of LIST (order kept);
return the first non-nil result."
  (labels ((walk (lst need chosen skipped)
             (cond ((zerop need) (funcall fn (reverse chosen) (append (reverse skipped) lst)))
                   ((< (length lst) need) nil)
                   (t (or (walk (cdr lst) (1- need) (cons (car lst) chosen) skipped)
                          (walk (cdr lst) need chosen (cons (car lst) skipped)))))))
    (walk list size nil nil)))

(defun remove-parts (parts list)
  "LIST without one occurrence of each of PARTS, or :fail."
  (let ((rest (copy-list list)))
    (dolist (x parts rest)
      (let ((pos (position x rest :test #'equal)))
        (if pos (setf rest (remove-nth pos rest)) (return :fail))))))

(defun head-compatible-p (item el)
  ;; cheap pre-filter for a one-element claim; t whenever m1 could still match
  (let ((h (and (consp item) (car item))))
    (cond ((or (null h) (not (symbolp h))) t)
          ((or (eq h +pattern+) (eq h +blank+) (eq h +optional+) (eq h +condition+)
               (eq h +pattern-test+) (flat-head-p h) (eq h +complex+))
           t)
          ((eq h +power+) (or (optional-p (third item)) (eq (head-of el) +power+)))
          (t (eq (head-of el) h)))))

(defun collapsible-p (q h)
  "Can item Q stand for an H-expression (and so take a run of >= 2 elements)?
Narrow reading (verify's _can_collapse_to): Q has head H, or Q is b^m_. with
b collapsible.  Wide reading adds a Plus/Times item other than H with exactly
one non-Optional argument that is collapsible."
  (and (consp q)
       (or (eq (car q) h)
           (and (eq (car q) +power+) (= (length q) 3) (optional-p (third q))
                (collapsible-p (second q) h))
           (and *flat-wide* (flat-head-p (car q)) (not (eq (car q) h))
                (= 1 (count-if-not #'optional-p (cdr q)))
                (collapsible-p (find-if-not #'optional-p (cdr q)) h)))))

(defun match-flat (p e b k)
  (let* ((h (car p))
         (elems (if (and (consp e) (eq (car e) h)) (cdr e) (list e)))
         (items (cdr p)))
    (flat-claim (remove-if #'absorber-p items) elems h b
                (lambda (left b2)
                  (flat-absorb (remove-if-not #'absorber-p items) left h b2 k)))))

(defun flat-claim (claimers elems h b k)
  "Each claimer takes one element (or, if collapsible, a run of >= 2); K gets
the leftover elements and the bindings."
  (if (null claimers)
      (funcall k elems b)
      (let ((item (car claimers)) (more (cdr claimers)))
        (or (loop for el in elems
                  for i from 0
                  thereis (and (head-compatible-p item el)
                               (m1 item el b
                                   (lambda (b2) (flat-claim more (remove-nth i elems) h b2 k)))))
            (and (collapsible-p item h)
                 (loop for size from 2 to (length elems)
                       thereis (map-subsets size elems
                                            (lambda (run rest)
                                              (m1 item (cons h run) b
                                                  (lambda (b2) (flat-claim more rest h b2 k)))))))))))

(defun flat-value (run h default)
  (cond ((null run) default)
        ((null (cdr run)) (car run))
        (t (cons h run))))

(defun flat-absorb (absorbers left h b k)
  "Bound absorbers consume their value's parts; unbound ones share the
leftovers -- a blank takes >= 1 element (G-1), an Optional >= 0 (default)."
  (if (null absorbers)
      (and (null left) (funcall k b))
      (let* ((item (car absorbers))
             (opt (optional-p item))
             (q (if opt (second item) item))
             (default (and opt (third item)))
             (name (and (eq (car q) +pattern+) (second q)))
             (cell (and name (assoc name b :test #'eq))))
        (if cell
            (let ((v (cdr cell)))
              (or (and opt (equal v default)
                       (flat-absorb (cdr absorbers) left h b k))
                  (let ((left2 (remove-parts (if (and (consp v) (eq (car v) h)) (cdr v) (list v))
                                             left)))
                    (and (not (eq left2 :fail))
                         (flat-absorb (cdr absorbers) left2 h b k)))))
            (loop for size from (if opt 0 1) to (length left)
                  thereis (map-subsets size left
                                       (lambda (run rest)
                                         (m1 q (flat-value run h default) b
                                             (lambda (b2) (flat-absorb (cdr absorbers) rest h b2 k))))))))))
```

Semantics notes for the reviewer (the code comments carry the same):
- `match-flat` = claimers (every item that is neither an Optional nor a bare named
  blank) take one element each, or — if `collapsible-p` — a run of ≥ 2 elements; the
  absorbers (Optionals, bare blanks) then share the leftovers: bound absorbers consume
  their value's parts, an unbound blank takes ≥ 1 element (G-1), an Optional ≥ 0.
- A pattern or compound head under Plus/Times is an ordinary claimer matched through
  `m1`'s head match (G-2).
- `collapsible-p` mirrors `_can_collapse_to` in `probes/matcher/02-roundtrip.py`;
  `*flat-wide*` adds exactly its `WIDE` clause.
- No `meval`, no global `declaim`/`proclaim`, no stack.

- [ ] **Step 4: Run the tests — expect green**

Run: `maxima --very-quiet -b test/matcher/test_mr_match.mac 2>&1 | grep -E 'FAIL|Results'`
Expected: `Results: 48 passed, 0 failed` and no `FAIL` line.

- [ ] **Step 5: Hygiene checks**

Run: `grep -nE '^[^;]*\((declaim|proclaim|meval|make-stack)' maxima_rubi_match.lisp; echo "hits=$?"`
Expected: no output and `hits=1` (grep found nothing).
Also: `sbcl --non-interactive --load maxima_rubi_match.lisp --load test/matcher/test_mr_match.lisp --eval '(mr-match-test:run)' 2>&1 | tail -1`
Expected: `Results: 48 passed, 0 failed` (the file has no Maxima dependency).

- [ ] **Step 6: Commit**

```bash
git add maxima_rubi_match.lisp test/matcher/test_mr_match.lisp test/matcher/test_mr_match.mac
git commit -m "$(printf 'matcher: mr-match — Mathematica-semantics structural matcher (substrate P1)\n\nRe-implementation of mma4max newmatch.lisp: ordered core, match-flat\n(claimers + absorbers; G-1 no empty blank, G-2 pattern heads under\nPlus/Times), native Optionals with parent defaults, Power exponent\ndefault, G-6 narrow/wide switch, condition hook with retry switch.\nNo meval, no global proclaim, bindings as an immutable alist.\nUnit tests 48/0 (Maxima batch and plain SBCL).\n\nClaude-Session: https://claude.ai/code/session_01D5eoebxrtMKBBUSqYf2MGa')"
```

---

### Task 6: The matcher regression suite and the P1 gate

Branch: `matcher-substrate`.

**Files:**
- Modify: `probes/matcher/02-roundtrip.py` (judge modes/legs from the environment)
- Create: `test/matcher/roundtrip.lisp`, `test/matcher/roundtrip.mac`,
  `test/matcher/controls.lisp`, `test/matcher/controls.mac`, `test/matcher/gate.py`, `test/matcher/run.sh`
- Commit outputs: `test/matcher/roundtrip.out`, `test/matcher/controls.out`, `test/matcher/gate.out`
- Ledger: `.superpowers/sdd/progress.md`

**Interfaces:**
- Consumes: Task 5's `MR-MATCH` exports; probe 02's `gen` / `judge` / `controls` subcommands and
  its `verify_case`, `parse_sexp`, `parse_bindings`, `cn`.
- Produces:
  - `sh test/matcher/run.sh` — env `MR_LEGS` (`tree` default; `tree,maxima` in Task 8),
    `MR_MODEL_FLAGS` and `MR_SPIKE` (Task 8); writes `test/matcher/roundtrip.out`,
    `controls.out`, `gate.out`; last line printed = the gate's `Results:` line.
  - Result-line formats: `R`/`PREP`/`DONE` exactly as probe 02 (`test/matcher/roundtrip.lisp` header);
    `CONTROL<TAB>mode<TAB>id<TAB>T|NIL<TAB>bindings<TAB>target<TAB>pattern`.
  - `mr-roundtrip::*converter*` — a special Task 8 binds to the MR-TREE converter.
  - `gate.py --report R --controls C [--g2 F] [--maxima] [--spike S]`.

- [ ] **Step 1: Let the probe-02 judge score other modes and legs**

In `probes/matcher/02-roundtrip.py`:

(a) after the line `MAX_SINGLE_VARIANTS = 10` add

```python
# modes / legs the judge scores (default: probe 02 as committed; the
# matcher regression suite sets MR_MODES=narrow,wide and MR_LEGS=tree or tree,maxima)
MODES = tuple(os.environ.get("MR_MODES", "pub,guard").split(","))
LEGS = tuple(os.environ.get("MR_LEGS", "tree,maxima").split(","))
```

(b) replace both occurrences of `for mode in ("pub", "guard"):` with `for mode in MODES:`;

(c) replace `if ms and (rid, v, "maxima", mode) not in results:` with
`if ms and "maxima" in LEGS and (rid, v, "maxima", mode) not in results:`.

Run: `python3 probes/matcher/02-roundtrip.py selftest | tail -1 && grep -c 'for mode in MODES' probes/matcher/02-roundtrip.py`
Expected: `Results: 14 passed, 0 failed` and `2`.

- [ ] **Step 2: Create the round-trip runner**

Create `test/matcher/roundtrip.mac`:

```maxima
/* test/matcher/roundtrip.mac -- one shard of the matcher round trip; run by
   test/matcher/run.sh (sets MR_CASES, MR_RESULTS, MR_NSHARDS, MR_SHARD,
   MR_MODES, MR_LEGS).  No rule files are loaded, so no --tls-limit flag. */
display2d : false$
build_info();
load("maxima_rubi_match.lisp")$
load("test/matcher/roundtrip.lisp")$
:lisp (mr-roundtrip:run)
```

Create `test/matcher/roundtrip.lisp`:

```lisp
;;;; test/matcher/roundtrip.lisp -- the probe-02 per-rule round trip through
;;;; MR-MATCH (matcher substrate spec section 4, P1/P2 gates).
;;;;
;;;; Reads the case file written by `python3 probes/matcher/02-roundtrip.py gen`
;;;; and writes result lines in probe 02's format, so
;;;; `02-roundtrip.py judge` scores them unchanged:
;;;;   PREP <id> <mode> <ok|error:..> <ms>
;;;;   R <id> <variant> <tree|maxima> <mode> <ok|timeout|error|maxerror> <T|NIL> <ms> <bindings> <converted>
;;;;   DONE
;;;; Environment: MR_CASES, MR_RESULTS, MR_NSHARDS, MR_SHARD, MR_LIMIT (as
;;;; probe 02); MR_MODES (default "narrow,wide": *flat-wide* nil / t);
;;;; MR_LEGS (default "tree"; "tree,maxima" once MR-TREE is loaded, Task 8).

(defpackage :mr-roundtrip (:use :cl :mr-match) (:export #:run))
(in-package :mr-roundtrip)

(defun getenv (name default) (or (sb-ext:posix-getenv name) default))

(defun split-on (s ch)
  (loop with start = 0
        for pos = (position ch s :start start)
        collect (subseq s start pos)
        while pos do (setf start (1+ pos))))

(defun now-ns ()
  (multiple-value-bind (s ns) (sb-unix:clock-gettime sb-unix:clock-monotonic)
    (+ (* s 1000000000) ns)))

(defun ms (ns) (format nil "~,4f" (/ ns 1000000.0)))

(defun line (out &rest fields)
  (format out "~{~a~^	~}~%"
          (mapcar (lambda (f) (substitute #\Space #\Newline (substitute #\Space #\Tab (princ-to-string f))))
                  fields)))

(defun load-cases (file nshards shard limit)
  ;; -> list of (id pattern-string cases), cases = ((variant tree maxima) ...)
  (let ((rules nil) (cur nil) (ordinal -1) (taken 0))
    (with-open-file (in file)
      (loop for l = (read-line in nil) while l
            do (let ((f (split-on l #\Tab)))
                 (cond ((string= (first f) "P")
                        (incf ordinal)
                        (setf cur (and (= (mod ordinal nshards) shard)
                                       (or (zerop limit) (< taken limit))
                                       (list (second f) (third f) nil)))
                        (when cur (incf taken) (push cur rules)))
                       ((and cur (string= (first f) "C"))
                        (push (list (third f) (fourth f) (or (fifth f) "")) (third cur)))))))
    (dolist (r rules) (setf (third r) (nreverse (third r))))
    (nreverse rules)))

(defun bindings-string (alist)
  (tree-string (mapcar (lambda (c) (list (car c) (cdr c))) (reverse alist))))

(defun x-name (pattern)
  ;; the Int pattern's second argument (Pattern NAME (Blank Symbol))
  (let ((second (third pattern)))
    (if (and (consp second) (eq (car second) (sym "Pattern"))) (second second) (sym "x"))))

(defvar *converter* nil
  "Task 8: a function (maxima-string) -> tree or :maxima-error; nil = no maxima leg.")

(defun run-one (out id variant leg mode compiled xname integrand convp)
  (let* ((expr (list (sym "Int") (canonicalize integrand) (sym "x")))
         (t0 (now-ns))
         (r (handler-case
                (sb-ext:with-timeout 2
                  (multiple-value-list (match compiled expr :bindings (list (cons xname (sym "x"))))))
              (sb-ext:timeout () :timeout)
              (error (e) (list :error (princ-to-string e)))))
         (dt (- (now-ns) t0))
         (conv (if convp (tree-string integrand) "")))
    (cond ((eq r :timeout) (line out "R" id variant leg mode "timeout" "" (ms dt) "" conv))
          ((eq (first r) :error) (line out "R" id variant leg mode "error" "" (ms dt) (second r) conv))
          (t (line out "R" id variant leg mode "ok" (if (second r) "T" "NIL") (ms dt)
                   (if (second r) (bindings-string (first r)) "()") conv)))))

(defun run-rule (r mode legs out)
  (destructuring-bind (id pat-string cases) r
    (let* ((t0 (now-ns))
           (compiled (handler-case (prepare (read-tree pat-string))
                       (error (e) (list :error (princ-to-string e)))))
           (dt (- (now-ns) t0)))
      (if (consp compiled)
          (line out "PREP" id mode (format nil "error:~a" (second compiled)) (ms dt))
          (let ((xname (x-name (compiled-pattern-tree compiled))))
            (line out "PREP" id mode "ok" (ms dt))
            (dolist (c cases)
              (destructuring-bind (variant tree maxima) c
                (when (member "tree" legs :test #'string=)
                  (run-one out id variant "tree" mode compiled xname (read-tree tree) nil))
                (when (and (member "maxima" legs :test #'string=) *converter* (plusp (length maxima)))
                  (let ((conv (funcall *converter* maxima)))
                    (if (eq conv :maxima-error)
                        (line out "R" id variant "maxima" mode "maxerror" "" "" "" "")
                        (run-one out id variant "maxima" mode compiled xname conv t)))))))))))

(defun run ()
  (let* ((nshards (parse-integer (getenv "MR_NSHARDS" "1")))
         (shard (parse-integer (getenv "MR_SHARD" "0")))
         (limit (parse-integer (getenv "MR_LIMIT" "0")))
         (modes (split-on (getenv "MR_MODES" "narrow,wide") #\,))
         (legs (split-on (getenv "MR_LEGS" "tree") #\,))
         (rules (load-cases (getenv "MR_CASES" "") nshards shard limit))
         (*print-pretty* nil))
    (format t "~&ROUNDTRIP shard ~a/~a: ~a rules, modes ~a, legs ~a~%" shard nshards (length rules) modes legs)
    (with-open-file (out (getenv "MR_RESULTS" "") :direction :output :if-exists :supersede)
      (dolist (mode modes)
        (let ((*flat-wide* (string= mode "wide")))
          (dolist (r rules) (run-rule r mode legs out)))
        (finish-output out))
      (format out "DONE~%"))
    (format t "~&ROUNDTRIP shard ~a done~%" shard)))
```

- [ ] **Step 3: Create the controls runner**

Create `test/matcher/controls.mac`:

```maxima
/* test/matcher/controls.mac -- probe-02 controls through MR-MATCH; run by
   test/matcher/run.sh (MR_CONTROLS = the generated data file). */
display2d : false$
load("maxima_rubi_match.lisp")$
load("test/matcher/controls.lisp")$
:lisp (load (sb-ext:posix-getenv "MR_CONTROLS"))
:lisp (mr-controls:run)
```

Create `test/matcher/controls.lisp`:

```lisp
;;;; test/matcher/controls.lisp -- probe-02 controls (U1/U1r/U2/U2r, H1..H8)
;;;; through MR-MATCH.  Data: `python3 probes/matcher/02-roundtrip.py controls`
;;;; (a Lisp file defining CL-USER::*CONTROLS*), loaded first.  Output, one line
;;;; per control and mode, read by test/matcher/gate.py:
;;;;   CONTROL <mode> <id> <T|NIL> <bindings> <target>
;;;; <target> is the Int expression matched, so gate.py can verify() bindings.

(defpackage :mr-controls (:use :cl :mr-match) (:export #:run))
(in-package :mr-controls)

(defun run (&optional (modes '("narrow" "wide")))
  (let ((*print-pretty* nil) (x (sym "x")))
    (dolist (mode modes)
      (let ((*flat-wide* (string= mode "wide")))
        (dolist (c (symbol-value (find-symbol "*CONTROLS*" :cl-user)))
          (destructuring-bind (id label pat tree note) c
            (declare (ignore label note))
            (let* ((expr (canonicalize (list (sym "Int") (read-tree tree) x)))
                   (compiled (prepare (read-tree pat))))
              (multiple-value-bind (b ok)
                  (match compiled expr :bindings (list (cons x x)))
                (format t "~&CONTROL~c~a~c~a~c~a~c~a~c~a~c~a~%"
                        #\Tab mode #\Tab id #\Tab (if ok "T" "NIL") #\Tab
                        (tree-string (mapcar (lambda (c) (list (car c) (cdr c))) (reverse b)))
                        #\Tab (tree-string (second expr)) #\Tab pat)))))))))
```

- [ ] **Step 4: Create the gate**

Create `test/matcher/gate.py`:

```python
#!/usr/bin/env python3
"""test/matcher/gate.py -- the matcher regression gate (matcher substrate
spec docs/superpowers/specs/2026-09-12-matcher-substrate-design.md section 4,
P1 and P2).

Inputs (all produced by test/matcher/*.run):
  --report    the round-trip judge report (02-roundtrip.py judge, modes narrow,wide)
  --controls  CONTROL lines from test/matcher/controls.mac
  --g2        probes/matcher/02-roundtrip.out -- the 41 G-2 rules (FAILRULES guard)
  --maxima    also gate the maxima leg (P2): its completeness; MODEL-LOST reported
  --spike     SPIKE lines from test/matcher/spike01.mac (P2)

Every check prints PASS:/FAIL:; the run ends with `Results: <n> passed, <m> failed`.
"""

import argparse
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("rt02", ROOT / "probes" / "matcher" / "02-roundtrip.py")
rt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rt)

RULE_ID = re.compile(r"(\d[\d.]*\.m L\d+) \[")
H_EXPECT = {
    "H1": {"F": "F", "x": "x"}, "H2": {"u": "u", "F": "F", "x": "x"},
    "H3": {"u": "u", "x": "x"}, "H4": {"u": "u", "F": "F", "x": "x"},
    "H5": {"F": "F", "m": "m", "x": "x"}, "H6": {"u": "u", "F": "F", "m": "m", "x": "x"},
    "H7": {"n": 2, "f": "f", "x": "x"}, "H8": {"u": "u", "n": 2, "f": "f", "x": "x"},
}
MIN_RULES_OK = 7444 - 9   # spec section 4 P1: every rule but the 9 G-3 Complex rules


class Gate:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def check(self, name, ok, detail=""):
        if ok:
            self.passed += 1
            print("PASS: %s" % name)
        else:
            self.failed += 1
            print("FAIL: %s%s" % (name, ("\n    " + detail) if detail else ""))


def line(report, pattern):
    m = re.search(pattern, report, re.M)
    return m


def kinds(text):
    return {k: int(c) for k, c in re.findall(r"([A-Z][A-Z/-]*) (\d+)", text)}


def gate_report(g, report, g2_ids, maxima):
    m = line(report, r"^completeness: rules (\d+); missing result lines (\d+)")
    g.check("round trip complete (7444 rules, 0 missing result lines)",
            bool(m) and m.group(1) == "7444" and m.group(2) == "0", m.group(0) if m else "no completeness line")
    for mode in ("narrow", "wide"):
        m = line(report, r"^SUMMARY %s positives \(tree leg\): (\d+) -- (.*)$" % mode)
        k = kinds(m.group(2)) if m else {}
        g.check("%s: 0 UNSOUND positives (tree leg)" % mode,
                bool(m) and k.get("WRONG/UNSOUND", 0) == 0, m.group(0) if m else "no positives line")
        m = line(report, r"^UNSOUNDRULES %s \((\d+)\)" % mode)
        g.check("%s: 0 rules with an UNSOUND binding (all legs, collapsed included; G-4 closed)" % mode,
                bool(m) and m.group(1) == "0", m.group(0) if m else "no UNSOUNDRULES line")
    m = line(report, r"^SUMMARY narrow rules with every positive OK \(tree leg\): (\d+)/(\d+)")
    g.check("narrow: rules with every positive OK >= %d" % MIN_RULES_OK,
            bool(m) and int(m.group(1)) >= MIN_RULES_OK, m.group(0) if m else "no rules-OK line")
    m = line(report, r"^SUMMARY narrow mutations: .*rules with a FALSE match: (\d+)$")
    g.check("narrow: 0 false mutation matches", bool(m) and m.group(1) == "0", m.group(0) if m else "no mutations line")
    m = line(report, r"^SUMMARY narrow collapsed witnesses .*$")
    g.check("narrow: 0 UNSOUND collapsed witnesses (tree leg)",
            bool(m) and "tree/FALSE/UNSOUND" not in m.group(0), m.group(0)[:300] if m else "no collapsed line")
    m = line(report, r"^FAILRULES narrow \((\d+)\): (.*)$")
    failing = set(RULE_ID.findall(m.group(2))) if m else None
    g.check("narrow: none of the %d G-2 rules fails" % len(g2_ids),
            failing is not None and not (failing & g2_ids),
            "still failing: %s" % sorted(failing & g2_ids) if failing else "no FAILRULES line")
    if maxima:
        for mode in ("narrow", "wide"):
            m = line(report, r"^SUMMARY %s maxima leg: (\d+) -- (.*); witnesses changed by Maxima: (\d+); "
                             r"rules with MODEL-LOST: (\d+)$" % mode)
            k = kinds(m.group(2)) if m else {}
            g.check("%s: maxima leg ran (%s variants; MODEL-LOST %s in %s rules; changed by Maxima %s)" % (
                mode, m.group(1) if m else "?", k.get("MODEL-LOST", 0), m.group(4) if m else "?",
                m.group(3) if m else "?"),
                bool(m) and int(m.group(1)) > 70000 and k.get("MAXIMA-ERROR", 0) == 0,
                m.group(0) if m else "no maxima-leg line")


def gate_controls(g, text):
    rows = [l.split("\t") for l in text.splitlines() if l.startswith("CONTROL\t")]
    g.check("controls: 12 controls x 2 modes present", len(rows) == 24, "%d CONTROL lines" % len(rows))
    for _tag, mode, cid, matched, binds, target, pattern in rows:
        B = dict(rt.parse_bindings(binds)) if matched == "T" else {}
        if cid in H_EXPECT:
            ok = matched == "T" and {k: rt.cn(v) for k, v in B.items()} == H_EXPECT[cid]
            g.check("controls %s %s: matches with the Mathematica bindings" % (mode, cid), ok,
                    "matched=%s bindings=%s" % (matched, binds))
        else:
            lhs = rt.parse_sexp(pattern)
            ok = matched == "NIL" or rt.verify_case(lhs, rt.parse_sexp(target), B, wide=(mode == "wide")) is True
            g.check("controls %s %s: no match or a verified binding" % (mode, cid), ok,
                    "matched=%s bindings=%s" % (matched, binds))


def gate_spike(g, text):
    rows = [l.split("\t") for l in text.splitlines() if l.startswith("SPIKE\t")]
    g.check("spike-01: 71 cases present", len(rows) == 71, "%d SPIKE lines" % len(rows))
    for _tag, cid, group, model, ok, detail in rows:
        if model == "T":
            print("INFO: spike-01 %s (model case, not gated) ok=%s %s" % (cid, ok, detail))
            continue
        g.check("spike-01 %s [%s]" % (cid, group), ok == "T", detail)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report")
    ap.add_argument("--controls")
    ap.add_argument("--g2", default=str(ROOT / "probes" / "matcher" / "02-roundtrip.out"))
    ap.add_argument("--maxima", action="store_true")
    ap.add_argument("--spike")
    a = ap.parse_args(argv)
    g = Gate()
    g2_line = re.search(r"^FAILRULES guard \((\d+)\): (.*)$", Path(a.g2).read_text(), re.M)
    g2_ids = set(RULE_ID.findall(g2_line.group(2)))
    g.check("G-2 reference list read (41 rules)", len(g2_ids) == 41, "%d ids" % len(g2_ids))
    if a.report:
        gate_report(g, Path(a.report).read_text(), g2_ids, a.maxima)
    if a.controls:
        gate_controls(g, Path(a.controls).read_text())
    if a.spike:
        gate_spike(g, Path(a.spike).read_text())
    print("Results: %d passed, %d failed" % (g.passed, g.failed))
    return 1 if g.failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 5: Create the suite runner**

Create `test/matcher/run.sh`:

```sh
#!/bin/sh
# test/matcher/run.sh -- the matcher regression suite (matcher substrate spec
# section 4, P1/P2 gates).  From anywhere:  sh test/matcher/run.sh
# Tree leg ~1 min wall with 20 shards.  Writes test/matcher/roundtrip.out,
# test/matcher/controls.out, test/matcher/gate.out; prints the gate's Results line.
# Env: MR_LEGS (default tree), MR_WORK (work dir, default ${TMPDIR:-/tmp}/mr-matcher-suite).
set -u
cd "$(dirname "$0")/../.."
N=20
LEGS=${MR_LEGS:-tree}
WORK=${MR_WORK:-${TMPDIR:-/tmp}/mr-matcher-suite}
mkdir -p "$WORK"
rm -f "$WORK"/shard*.tsv "$WORK"/shard*.log
python3 probes/matcher/02-roundtrip.py gen "$WORK/cases.tsv" > "$WORK/gen.log" || exit 1
i=0
while [ "$i" -lt "$N" ]; do
  MR_CASES="$WORK/cases.tsv" MR_NSHARDS=$N MR_SHARD=$i MR_RESULTS="$WORK/shard$i.tsv" \
    MR_MODES=narrow,wide MR_LEGS=$LEGS \
    timeout 3600 maxima --very-quiet -b test/matcher/roundtrip.mac > "$WORK/shard$i.log" 2>&1 &
  i=$((i + 1))
done
wait
{
  echo "=== test/matcher round trip  legs: $LEGS  judged: $(date -u '+%Y-%m-%d %H:%M UTC')"
  echo "git HEAD: $(git rev-parse HEAD)"
  MR_MODES=narrow,wide MR_LEGS=$LEGS python3 probes/matcher/02-roundtrip.py judge "$WORK" "$N"
} > test/matcher/roundtrip.out
python3 probes/matcher/02-roundtrip.py controls > "$WORK/controls-data.lisp" || exit 1
MR_CONTROLS="$WORK/controls-data.lisp" timeout 600 maxima --very-quiet -b test/matcher/controls.mac 2>&1 \
  | grep '^CONTROL' > test/matcher/controls.out
python3 test/matcher/gate.py --report test/matcher/roundtrip.out --controls test/matcher/controls.out \
  > test/matcher/gate.out
tail -1 test/matcher/gate.out
```

- [ ] **Step 6: Run the suite in the background**

```bash
setsid sh -c 'sh test/matcher/run.sh > /tmp/claude-mr-suite.log 2>&1; echo done >> /tmp/claude-mr-suite.log' &
```
Poll `/tmp/claude-mr-suite.log` (≤ 110 s per call) until it ends with `done`.

- [ ] **Step 7: Read the gate**

Run: `grep -E '^(FAIL|Results)' test/matcher/gate.out; grep -E '^(completeness|SUMMARY (narrow|wide) (positives|rules|mutations)|TIMING (narrow|wide) tree)' test/matcher/roundtrip.out`
Expected: `Results: 35 passed, 0 failed`, no `FAIL`; the judge's build line names
`branch_5_50_base_84_g4204fb669`.

If any check fails: **stop** and use superpowers:systematic-debugging — reproduce the
failing rule/variant as a new `check-match` / `check-no-match` case in
`test/matcher/test_mr_match.lisp` (take the pattern from the `P` line and the tree from
the `C` line of `$WORK/cases.tsv`), watch it fail, fix `maxima_rubi_match.lisp`, run
Task 5 Step 4 and this task's Steps 6–7 again. The spec's P1 exit criterion for G-4 is
"0 UNSOUND, else investigated and resolved before P2".

- [ ] **Step 8: Ledger and commit**

Append to the plan's section in `.superpowers/sdd/progress.md`:

```markdown
### Task 6 — P1 gate (matcher regression suite)
- run: <the `judged:` line and the build line of test/matcher/roundtrip.out>
- gate: <the Results line of test/matcher/gate.out>
- <the four SUMMARY lines and two TIMING lines per mode from Step 7>
- G-2: 41/41 closed; G-4: UNSOUNDRULES narrow 0 / wide 0; G-6 wide arm: <tree/FALSE/WIDE-OK count from the wide collapsed line>
```

Fill every `<…>` with the literal lines, then:

```bash
chmod +x test/matcher/run.sh
git add probes/matcher/02-roundtrip.py test/matcher/roundtrip.lisp test/matcher/roundtrip.mac \
  test/matcher/controls.lisp test/matcher/controls.mac test/matcher/gate.py test/matcher/run.sh \
  test/matcher/roundtrip.out test/matcher/controls.out test/matcher/gate.out .superpowers/sdd/progress.md
git commit -m "$(printf 'matcher: regression suite — probe-02 round trip + controls through mr-match (P1 gate)\n\ntest/matcher/run.sh: 20 Maxima shards (narrow, wide), probe-02 judge\n(MR_MODES/MR_LEGS), controls, gate.py. P1 gate green; evidence in\ntest/matcher/*.out and the ledger.\n\nClaude-Session: https://claude.ai/code/session_01D5eoebxrtMKBBUSqYf2MGa')"
```

---

### Task 7: `mr-tree` — the Maxima ↔ tree converter (P2)

Branch: `matcher-substrate`.

**Files:**
- Create: `maxima_rubi_tree.lisp`
- Create: `test/matcher/test_mr_tree.lisp`, `test/matcher/test_mr_tree.mac`

**Interfaces:**
- Consumes: Task 5's `MR-MATCH` (`sym`, `read-tree`, `tree-string`, `canonicalize`); Maxima's
  `meval`, `$parse_string`, `simplifya`, `alike1`, `$float`.
- Produces — package `MR-TREE` (exported), relied on by Task 8 and Plan 2's dispatcher:
  - `(max->tree maxima-expr) -> canonical tree` — reads SIMPLIFIED internal form; folds numeric `%i`
    terms into complex atoms (G-3); `$%e`/`$%pi` → `E`/`Pi`; `rat` → ratio; bigfloat → double-float;
    `li[n]`/`psi[n]` and `polylog(n,x)` → `PolyLog`/`PolyGamma`; table heads by operator; any other operator
    → `*unknown-head-hook*` result or a head `MX_<operator>` carrying the operator on its plist.
  - `(tree->max tree) -> simplified Maxima expression` (built unsimplified, `simplifya` once).
  - `(maxima-form string)` parse + evaluate; `(maxima-name symbol) -> string` (case-restored name without `$`/`%`).
  - `*unknown-head-hook*` — nil or `(lambda (operator-symbol) -> head-symbol-or-nil)`.
  - `(head-table) -> ((head arity operator) …)` — 45 entries, built at load from Maxima's own operators.

- [ ] **Step 1: Write the failing tests**

Create `test/matcher/test_mr_tree.mac`:

```maxima
/* test/matcher/test_mr_tree.mac -- MR-TREE unit tests.
   From the repo root:  maxima --very-quiet -b test/matcher/test_mr_tree.mac
   No rule files are loaded, so no --tls-limit flag.  Ends with a Results: line. */
display2d : false$
load("maxima_rubi_match.lisp")$
load("maxima_rubi_tree.lisp")$
load("test/matcher/test_mr_tree.lisp")$
:lisp (mr-tree-test:run)
```

Create `test/matcher/test_mr_tree.lisp`:

```lisp
;;;; test/matcher/test_mr_tree.lisp -- MR-TREE unit tests (inside Maxima).
;;;; Run: maxima --very-quiet -b test/matcher/test_mr_tree.mac

(defpackage :mr-tree-test (:use :cl :mr-match :mr-tree) (:export #:run))
(in-package :mr-tree-test)

(defvar *passed* 0)
(defvar *failed* 0)

(defun check (name ok &optional detail)
  (if ok
      (progn (incf *passed*) (format t "  PASS: ~a~%" name))
      (progn (incf *failed*) (format t "  FAIL: ~a~@[~%    ~a~]~%" name detail))))

(defun conv (s) (max->tree (maxima-form s)))

(defmacro check-conv (s expected)
  `(let ((got (conv ,s)) (want (canonicalize (read-tree ,expected))))
     (check (format nil "max->tree ~a" ,s) (equal got want)
            (format nil "got ~a want ~a" (tree-string got) (tree-string want)))))

(defun round-trips-p (s)
  (let* ((e (maxima-form s)) (back (tree->max (max->tree e))))
    (values (maxima::alike1 e back) back)))

(defun test-table ()
  (format t "--- head table ---~%")
  (let ((table (head-table)))
    (check "one entry per (head, arity) of the probe-02 table" (= (length table) 45) (length table))
    (flet ((op (head arity) (third (find-if (lambda (r) (and (string= (symbol-name (first r)) head)
                                                             (= (second r) arity)))
                                            table))))
      (check "abs -> mabs" (eq (op "Abs" 1) 'maxima::mabs))
      (check "factorial -> mfactorial" (eq (op "Factorial" 1) 'maxima::mfactorial))
      (check "Gamma/2 -> %gamma_incomplete" (eq (op "Gamma" 2) 'maxima::%gamma_incomplete)))))

(defun test-max->tree ()
  (format t "--- max->tree ---~%")
  (check-conv "a+b*x" "(Plus a (Times b x))")
  (check-conv "x^(1/3)" "(Power x 1/3)")
  (check-conv "sqrt(x)" "(Power x 1/2)")
  (check-conv "1/x" "(Power x -1)")
  (check-conv "-x" "(Times -1 x)")
  (check-conv "exp(2*x)" "(Power E (Times 2 x))")
  (check-conv "%pi*x" "(Times Pi x)")
  (check-conv "A*x" "(Times A x)")
  (check-conv "log(x)" "(Log x)")
  (check-conv "abs(x)" "(Abs x)")
  (check-conv "x!" "(Factorial x)")
  (check-conv "gamma_incomplete(a,x)" "(Gamma a x)")
  (check-conv "li[2](x)" "(PolyLog 2 x)")
  (check-conv "psi[1](x)" "(PolyGamma 1 x)")
  (check-conv "0.1*x" "(Times 0.1d0 x)")
  (check-conv "1.5b0*x" "(Times 1.5d0 x)")
  (check-conv "2*%i*x" "(Times #C(0 2) x)")
  (check-conv "1+%i" "#C(1 1)")
  (check-conv "%i" "#C(0 1)")
  (check-conv "b*a+c" "(Plus c (Times a b))")
  (let ((got (conv "foo(x)")))
    (check "unknown function -> MX_ head" (and (consp got) (search "MX_" (symbol-name (car got))))
           (tree-string got)))
  (check-conv "polylog(2,x)" "(PolyLog 2 x)")
  (check "maxima-name restores case" (equal (list (maxima-name 'maxima::$mm_sin) (maxima-name 'maxima::|$a|)
                                                  (maxima-name 'maxima::%sin))
                                            '("mm_sin" "A" "sin")))
  (let ((*unknown-head-hook* (lambda (op)
                               (let ((n (maxima-name op)))
                                 (and (> (length n) 3) (string= "mm_" n :end2 3) (sym (subseq n 3)))))))
    (check-conv "mm_Foo(x)" "(Foo x)")
    (check-conv "mm_sin(x)" "(sin x)")))

(defun test-round-trip ()
  (format t "--- tree->max round trip ---~%")
  (dolist (s '("a+b*x" "(a+b*x)^m*(c+d*x)^n" "x/(a+b*x)" "2*%i*x" "1+%i" "li[2](x)" "psi[1](x)"
               "sin(x)^2*log(c*x)" "A*x" "abs(x)" "x!" "0.1*x" "exp(2*x)" "foo(x,y)"
               "gamma_incomplete(a,x)" "sqrt(1-x^2)" "%pi*x"))
    (multiple-value-bind (ok back) (round-trips-p s)
      (check (format nil "round trip ~a" s) ok (format nil "back ~s" back)))))

(defun run ()
  (setf *passed* 0 *failed* 0)
  (test-table)
  (test-max->tree)
  (test-round-trip)
  (format t "Results: ~a passed, ~a failed~%" *passed* *failed*)
  (finish-output))
```

- [ ] **Step 2: Run — expect failure**

Run: `maxima --very-quiet -b test/matcher/test_mr_tree.mac 2>&1 | tail -5`
Expected: a load error for `maxima_rubi_tree.lisp` / package `MR-TREE`, no `Results:` line.

- [ ] **Step 3: Implement the converter**

Create `maxima_rubi_tree.lisp`:

```lisp
;;;; maxima_rubi_tree.lisp -- MR-TREE: simplified Maxima internal form <-> MR-MATCH trees.
;;;;
;;;; Design: docs/superpowers/specs/2026-09-12-matcher-substrate-design.md
;;;; section 3.3.  max->tree reads a SIMPLIFIED Maxima expression and does no
;;;; simplification of its own beyond two structural steps: numeric %i terms are
;;;; folded into complex atoms (G-3) and Plus/Times arguments are sorted
;;;; (mr-match:canonicalize).  tree->max builds unsimplified internal form and
;;;; simplifies it once.  The head table is derived at load time from Maxima's
;;;; own operators (a call is parsed and its operator read), so a Maxima rename
;;;; shows up as a load-time error, not a silent miss.
;;;;
;;;; Load after maxima_rubi_match.lisp, inside Maxima.

(defpackage :mr-tree
  (:use :cl :mr-match)
  (:export #:max->tree #:tree->max #:maxima-form #:maxima-name #:*unknown-head-hook* #:head-table))

(in-package :mr-tree)

;;; Mathematica head, arity, Maxima call name -- the probe-02 table
;;; (probes/matcher/02-roundtrip.py MAXIMA_FUN), every name measured there.
(defparameter +functions+
  '(("Log" 1 "log") ("Sin" 1 "sin") ("Cos" 1 "cos") ("Tan" 1 "tan") ("Cot" 1 "cot")
    ("Sec" 1 "sec") ("Csc" 1 "csc") ("Sinh" 1 "sinh") ("Cosh" 1 "cosh") ("Tanh" 1 "tanh")
    ("Coth" 1 "coth") ("Sech" 1 "sech") ("Csch" 1 "csch") ("ArcSin" 1 "asin")
    ("ArcCos" 1 "acos") ("ArcTan" 1 "atan") ("ArcCot" 1 "acot") ("ArcSec" 1 "asec")
    ("ArcCsc" 1 "acsc") ("ArcSinh" 1 "asinh") ("ArcCosh" 1 "acosh") ("ArcTanh" 1 "atanh")
    ("ArcCoth" 1 "acoth") ("ArcSech" 1 "asech") ("ArcCsch" 1 "acsch") ("Erf" 1 "erf")
    ("Erfc" 1 "erfc") ("Erfi" 1 "erfi") ("FresnelS" 1 "fresnel_s") ("FresnelC" 1 "fresnel_c")
    ("ExpIntegralEi" 1 "expintegral_ei") ("ExpIntegralE" 2 "expintegral_e")
    ("SinIntegral" 1 "expintegral_si") ("CosIntegral" 1 "expintegral_ci")
    ("SinhIntegral" 1 "expintegral_shi") ("CoshIntegral" 1 "expintegral_chi")
    ("LogIntegral" 1 "expintegral_li") ("Gamma" 1 "gamma") ("Gamma" 2 "gamma_incomplete")
    ("LogGamma" 1 "log_gamma") ("ProductLog" 1 "lambert_w") ("BesselJ" 2 "bessel_j")
    ("Zeta" 1 "zeta") ("Factorial" 1 "factorial") ("Abs" 1 "abs")))

;;; Maxima's subscripted functions li[n](x), psi[n](x): mqapply of an array op.
(defparameter +subscripted+ '(("PolyLog" maxima::$li) ("PolyGamma" maxima::$psi)))

(defvar *unknown-head-hook* nil
  "Nil, or a function (maxima-operator-symbol) -> head symbol or nil, tried
before the default MX_<operator> head for a Maxima operator the table lacks.")

(defvar *op->head* (make-hash-table :test 'eq))
(defvar *head->op* (make-hash-table :test 'equal))   ; (head . arity) -> operator

(defun maxima-form (string)
  "Parse and evaluate a Maxima expression string (simplified internal form)."
  (maxima::meval (maxima::meval (list (list 'maxima::$parse_string) string))))

;;; Maxima operators read as a head but never written back (tree->max uses the
;;; subscripted form): polylog(n, x) stays $polylog for a symbolic n.
(defparameter +read-only-functions+ '(("PolyLog" 2 "polylog")))

(defun function-operator (name arity)
  (let* ((call (format nil "~a(~{q~a~^,~})" name (loop for i below arity collect i)))
         (form (maxima-form call)))
    (unless (and (consp form) (consp (car form)))
      (error "mr-tree: ~a did not parse to a function call: ~s" call form))
    (caar form)))

(defun build-head-table ()
  (clrhash *op->head*)
  (clrhash *head->op*)
  (dolist (entry +functions+)
    (destructuring-bind (head arity name) entry
      (let ((op (function-operator name arity)))
        (setf (gethash op *op->head*) (sym head)
              (gethash (cons (sym head) arity) *head->op*) op))))
  (dolist (entry +read-only-functions+)
    (destructuring-bind (head arity name) entry
      (setf (gethash (function-operator name arity) *op->head*) (sym head)))))

(build-head-table)

(defun head-table ()
  "The load-time table as a list of (head arity maxima-operator)."
  (loop for (head . arity) being the hash-keys of *head->op* using (hash-value op)
        collect (list head arity op)))

;;; ------------------------------------------------------------------
;;; names

(defun invert-case (s)
  (cond ((string= s (string-upcase s)) (string-downcase s))
        ((string= s (string-downcase s)) (string-upcase s))
        (t s)))

(defun maxima-name (sym)
  ;; $x -> "x", |$a| -> "A", %sin -> "sin"
  (let ((s (symbol-name sym)))
    (invert-case (if (and (> (length s) 1) (find (char s 0) "$%")) (subseq s 1) s))))

(defparameter +reserved+ '("E" "Pi" "I"))

(defun symbol->tree (sym)
  (case sym
    (maxima::$%e (sym "E"))
    (maxima::$%pi (sym "Pi"))
    (maxima::$%i #C(0 1))
    (t (let ((n (maxima-name sym)))
         (sym (if (member n +reserved+ :test #'string=) (concatenate 'string "MXS_" n) n))))))

(defun unknown-head (op)
  (or (and *unknown-head-hook* (funcall *unknown-head-hook* op))
      (let ((h (sym (concatenate 'string "MX_" (symbol-name op)))))
        (setf (get h 'maxima-op) op)
        h)))

;;; ------------------------------------------------------------------
;;; Maxima -> tree

(defun numeric-atom-p (x) (numberp x))

(defun fold-complex (head args)
  ;; G-3: when a complex atom is present, combine it with the numeric atoms
  (if (notany #'complexp args)
      args
      (let ((nums (remove-if-not #'numeric-atom-p args))
            (rest (remove-if #'numeric-atom-p args)))
        (let ((v (if (eq head (sym "Plus")) (reduce #'+ nums) (reduce #'* nums))))
          (if (or (and (eq head (sym "Plus")) (eql v 0)) (and (eq head (sym "Times")) (eql v 1)))
              rest
              (cons v rest))))))

(defun flat-node (head args)
  (let ((args (fold-complex head args)))
    (cond ((null args) (if (eq head (sym "Plus")) 0 1))
          ((null (cdr args)) (car args))
          (t (cons head args)))))

(defun convert (e)
  (cond ((integerp e) e)
        ((floatp e) (coerce e 'double-float))
        ((symbolp e) (symbol->tree e))
        ((stringp e) e)
        ((and (consp e) (consp (car e)))
         (let ((op (caar e)) (args (cdr e)))
           (cond ((eq op 'maxima::rat) (/ (first args) (second args)))
                 ((eq op 'maxima::bigfloat) (coerce (maxima::$float e) 'double-float))
                 ((eq op 'maxima::mplus) (flat-node (sym "Plus") (mapcar #'convert args)))
                 ((eq op 'maxima::mtimes) (flat-node (sym "Times") (mapcar #'convert args)))
                 ((eq op 'maxima::mexpt) (list (sym "Power") (convert (first args)) (convert (second args))))
                 ((eq op 'maxima::mqapply)
                  (let* ((sub (first args))
                         (entry (find (caar sub) +subscripted+ :key #'second)))
                    (cons (if entry (sym (first entry)) (unknown-head (caar sub)))
                          (mapcar #'convert (append (cdr sub) (rest args))))))
                 (t (cons (or (gethash op *op->head*) (unknown-head op))
                          (mapcar #'convert args))))))
        (t (error "mr-tree: cannot convert ~s" e))))

(defun max->tree (e)
  "Simplified Maxima internal form -> canonical MR-MATCH tree."
  (canonicalize (convert e)))

;;; ------------------------------------------------------------------
;;; tree -> Maxima

(defun tree-symbol->maxima (s)
  (let ((n (symbol-name s)))
    (cond ((string= n "E") 'maxima::$%e)
          ((string= n "Pi") 'maxima::$%pi)
          ((string= n "I") 'maxima::$%i)
          (t (intern (concatenate 'string "$" (invert-case
                                               (if (and (> (length n) 4) (string= "MXS_" n :end2 4))
                                                   (subseq n 4) n)))
                     :maxima)))))

(defun unconvert (e)
  (cond ((integerp e) e)
        ((typep e 'ratio) (list '(maxima::rat) (numerator e) (denominator e)))
        ((floatp e) e)
        ((complexp e) (list '(maxima::mplus) (unconvert (realpart e))
                            (list '(maxima::mtimes) (unconvert (imagpart e)) 'maxima::$%i)))
        ((stringp e) e)
        ((symbolp e) (tree-symbol->maxima e))
        (t (let* ((h (car e)) (args (mapcar #'unconvert (cdr e)))
                  (sub (and (symbolp h) (assoc (symbol-name h) +subscripted+ :test #'string=))))
             (cond ((eq h (sym "Plus")) (cons '(maxima::mplus) args))
                   ((eq h (sym "Times")) (cons '(maxima::mtimes) args))
                   ((eq h (sym "Power")) (cons '(maxima::mexpt) args))
                   (sub (list* '(maxima::mqapply) (list (list (second sub) 'maxima::array) (first args))
                               (rest args)))
                   ((and (symbolp h) (gethash (cons h (length args)) *head->op*))
                    (cons (list (gethash (cons h (length args)) *head->op*)) args))
                   ((and (symbolp h) (get h 'maxima-op)) (cons (list (get h 'maxima-op)) args))
                   ((symbolp h) (cons (list (tree-symbol->maxima h)) args))
                   (t (error "mr-tree: no Maxima form for head ~a" (tree-string h))))))))

(defun tree->max (tree)
  "MR-MATCH tree -> simplified Maxima internal form (simplified once)."
  (maxima::simplifya (unconvert tree) nil))
```

- [ ] **Step 4: Run — expect green, no compiler warnings**

Run: `maxima --very-quiet -b test/matcher/test_mr_tree.mac 2>&1 | grep -E 'WARNING|FAIL|Results'`
Expected: exactly `Results: 46 passed, 0 failed` (no `WARNING`, no `FAIL`). Then re-run Task 5's
suite (`maxima --very-quiet -b test/matcher/test_mr_match.mac 2>&1 | tail -1`): still `Results: 48 passed, 0 failed`.

- [ ] **Step 5: Commit**

```bash
git add maxima_rubi_tree.lisp test/matcher/test_mr_tree.lisp test/matcher/test_mr_tree.mac
git commit -m "$(printf 'matcher: mr-tree — simplified Maxima form <-> canonical trees (substrate P2)\n\nHead table derived at load from Maxima operators (45 entries +\npolylog read alias); numeric %%i folded into complex atoms (G-3);\nunknown operators travel as MX_ heads and convert back; tree->max\nsimplifies once. Unit tests 46/0.\n\nClaude-Session: https://claude.ai/code/session_01D5eoebxrtMKBBUSqYf2MGa')"
```

---

### Task 8: Maxima leg, flags arm, spike-01 cases — the P2 gate

Branch: `matcher-substrate`.

**Files:**
- Create: `test/matcher/maxima-leg.lisp`, `test/matcher/spike01.lisp`, `test/matcher/spike01.mac`
- Modify (full replacement): `test/matcher/roundtrip.mac`, `test/matcher/run.sh`
- Commit outputs: `test/matcher/roundtrip.out`, `test/matcher/roundtrip.flags.out`, `test/matcher/controls.out`,
  `test/matcher/spike01.out`, `test/matcher/gate.out`, `test/matcher/gate.flags.out`
- Ledger: `.superpowers/sdd/progress.md`

**Interfaces:**
- Consumes: Task 5 `MR-MATCH`, Task 7 `MR-TREE` (`max->tree`, `maxima-form`, `maxima-name`,
  `*unknown-head-hook*`), Task 6 `mr-roundtrip::*converter*`, `gate.py --maxima --spike`.
- Produces: `sh test/matcher/run.sh` with `MR_LEGS=tree,maxima`, `MR_MODEL_FLAGS=1` (outputs suffixed
  `.flags`), `MR_SPIKE=1`; the committed P2 evidence. Plan 2 re-runs this suite after every matcher or
  converter change.

- [ ] **Step 1: The Maxima leg**

Create `test/matcher/maxima-leg.lisp`:

```lisp
;;;; test/matcher/maxima-leg.lisp -- the round trip's Maxima leg through MR-TREE
;;;; (matcher substrate spec section 4, P2).  Loaded by test/matcher/roundtrip.mac
;;;; after maxima_rubi_tree.lisp and test/matcher/roundtrip.lisp; binds
;;;; mr-roundtrip::*converter*.  With MR_MODEL_FLAGS=1 the witnesses are
;;;; simplified under radexpand:false and logexpand:false (spec section 3.3 arm).

(in-package :mr-roundtrip)

(when (equal (sb-ext:posix-getenv "MR_MODEL_FLAGS") "1")
  (setf maxima::$radexpand nil
        maxima::$logexpand nil))

(defun maxima-safe (string)
  ;; parse_string, then evaluate/simplify, each inside errcatch (probe 02's maxima-safe)
  (let ((p (maxima::meval `((maxima::$errcatch) ((maxima::$parse_string) ,string)))))
    (if (null (cdr p))
        :maxima-error
        (let ((v (maxima::meval `((maxima::$errcatch) ,(second p)))))
          (if (null (cdr v)) :maxima-error (second v))))))

(defun mm-head (op)
  ;; probe 02 writes heads without a Maxima function as mm_<Head>(...); Maxima's
  ;; reader inverts the case of an all-lowercase name (mm_sin -> $MM_SIN), so
  ;; compare the case-restored name
  (let ((n (mr-tree:maxima-name op)))
    (and (> (length n) 3) (string= "mm_" n :end2 3) (sym (subseq n 3)))))

(setf *converter*
      (lambda (string)
        (handler-case
            (sb-ext:with-timeout 20
              (let ((f (maxima-safe string)))
                (if (eq f :maxima-error)
                    f
                    (let ((mr-tree:*unknown-head-hook* #'mm-head))
                      (mr-tree:max->tree f)))))
          (sb-ext:timeout () :maxima-error)
          (error () :maxima-error))))
```

Replace `test/matcher/roundtrip.mac` with:

```maxima
/* test/matcher/roundtrip.mac -- one shard of the matcher round trip; run by
   test/matcher/run.sh (sets MR_CASES, MR_RESULTS, MR_NSHARDS, MR_SHARD,
   MR_MODES, MR_LEGS, MR_MODEL_FLAGS).  No rule files are loaded, so no
   --tls-limit flag. */
display2d : false$
build_info();
load("maxima_rubi_match.lisp")$
load("maxima_rubi_tree.lisp")$
load("test/matcher/roundtrip.lisp")$
load("test/matcher/maxima-leg.lisp")$
:lisp (mr-roundtrip:run)
```

- [ ] **Step 2: The spike-01 cases**

Create `test/matcher/spike01.mac`:

```maxima
/* test/matcher/spike01.mac -- spike-01 cases through MR-MATCH + MR-TREE; run by
   test/matcher/run.sh with MR_SPIKE=1.  No rule files, no --tls-limit flag. */
display2d : false$
load("maxima_rubi_match.lisp")$
load("maxima_rubi_tree.lisp")$
load("test/matcher/spike01.lisp")$
:lisp (mr-spike01:run)
```

Create `test/matcher/spike01.lisp`:

```lisp
;;;; test/matcher/spike01.lisp -- the spike-01 cases (probes/matcher/
;;;; 01-mma4max-feasibility.lisp *rules* / *cases*: 71 cases, groups G1-G7, NEG,
;;;; CTL; the 10 SCALE cases live in *scale-cases* and are not read) through
;;;; MR-MATCH + MR-TREE (matcher substrate spec section 4, P2).
;;;;
;;;; The case data is read from the committed spike file as data (its code is
;;;; not loaded -- mma4max is not needed).  Per case: integrand from :target via
;;;; Maxima's simplifier + max->tree, or from :tree; pattern = the rule's compact
;;;; FullForm; condition = the rule's FreeQ[{...}, x] list as the cond hook;
;;;; expected bindings from :expect (Maxima strings, '|' = alternatives).
;;;; Output, read by test/matcher/gate.py --spike:
;;;;   SPIKE <id> <group> <model T|NIL> <ok T|NIL> <detail>

(defpackage :mr-spike01 (:use :cl :mr-match :mr-tree) (:export #:run))
(in-package :mr-spike01)

(defun spike-data (path)
  "-> (values rules cases) from the spike file's defparameter/setf-append forms."
  (unless (find-package :mma) (make-package :mma :use nil))
  (unless (find-package :pat) (make-package :pat :use nil))
  (let ((rules nil) (cases nil) (*read-eval* nil) (*package* (find-package :cl-user)))
    (with-open-file (in path)
      (loop for form = (read in nil :eof)
            until (eq form :eof)
            do (when (consp form)
                 (flet ((data (f) (and (consp f) (eq (car f) 'quote) (second f))))
                   (cond ((and (eq (car form) 'defparameter) (string= (symbol-name (second form)) "*RULES*"))
                          (setf rules (data (third form))))
                         ((and (eq (car form) 'defparameter) (string= (symbol-name (second form)) "*CASES*"))
                          (setf cases (data (third form))))
                         ((and (eq (car form) 'setf) (consp (third form)) (eq (car (third form)) 'append))
                          (let ((more (data (third (third form)))))
                            (cond ((string= (symbol-name (second form)) "*RULES*") (setf rules (append rules more)))
                                  ((string= (symbol-name (second form)) "*CASES*") (setf cases (append cases more)))))))))))
    (values rules cases)))

(defun free-of-p (tree v)
  (cond ((equal tree v) nil)
        ((consp tree) (every (lambda (s) (free-of-p s v)) tree))
        (t t)))

(defun split-on (s ch)
  (loop with start = 0
        for pos = (position ch s :start start)
        collect (subseq s start pos)
        while pos do (setf start (1+ pos))))

(defun parse-expect (s)
  ;; "a=3 b=2 | a=4 b=5" -> ((("a" . tree) ...) ...)
  (mapcar (lambda (alt)
            (loop for tok in (split-on (string-trim " " alt) #\Space)
                  unless (string= tok "")
                    collect (let ((p (position #\= tok)))
                              (cons (subseq tok 0 p) (max->tree (maxima-form (subseq tok (1+ p))))))))
          (split-on s #\|)))

(defun run-case (c rules)
  (destructuring-bind (&key id group model rule target tree swap expect &allow-other-keys) c
    (declare (ignore swap))   ; canonicalize makes the stored factor order irrelevant
    (let* ((r (or (assoc rule rules :test #'string=) (error "no rule ~a" rule)))
           (x (sym "x"))
           (integrand (if tree (canonicalize (read-pattern tree)) (max->tree (maxima-form target))))
           (names (mapcar #'sym (third r)))
           (hook (lambda (b)
                   (let ((xv (cdr (assoc x b))))
                     (every (lambda (n) (let ((cell (assoc n b))) (and cell (free-of-p (cdr cell) xv))))
                            names))))
           (compiled (prepare (read-pattern (second r)))))
      (multiple-value-bind (b matched)
          (match compiled (list (sym "Int") integrand x) :bindings (list (cons x x)) :cond-hook hook)
        (let* ((alts (if (eq expect :none) nil (parse-expect expect)))
               (ok (if (eq expect :none)
                       (not matched)
                       (and matched
                            (some (lambda (alt)
                                    (every (lambda (pair) (equal (cdr (assoc (sym (car pair)) b)) (cdr pair)))
                                           (cons (cons "x" x) alt)))
                                  alts)))))
          (format t "~&SPIKE~c~a~c~a~c~a~c~a~cmatched=~a bindings=~a integrand=~a~%"
                  #\Tab id #\Tab group #\Tab (if model "T" "NIL") #\Tab (if ok "T" "NIL") #\Tab
                  (if matched "T" "NIL")
                  (tree-string (mapcar (lambda (c) (list (car c) (cdr c))) (reverse b)))
                  (tree-string integrand)))))))

(defun run (&optional (path "probes/matcher/01-mma4max-feasibility.lisp"))
  (let ((*print-pretty* nil))
    (multiple-value-bind (rules cases) (spike-data path)
      (format t "~&SPIKE-DATA rules ~a cases ~a~%" (length rules) (length cases))
      (dolist (c cases)
        (handler-case (run-case c rules)
          (error (e) (format t "~&SPIKE~c~a~c~a~cNIL~cNIL~cerror ~a~%"
                             #\Tab (getf c :id) #\Tab (getf c :group) #\Tab #\Tab #\Tab
                             (substitute #\Space #\Newline (princ-to-string e)))))))))
```

Run it once by hand: `maxima --very-quiet -b test/matcher/spike01.mac 2>&1 | grep '^SPIKE' | awk -F'\t' '$1=="SPIKE" && $5!="T"'`
Expected: exactly two lines, `G1-04` and `G7-M1`, both with model column `T` (Maxima's
`(2*x)^m` and `(d*x^2)^m` rewrites — excluded from the gate by design).

- [ ] **Step 3: Replace the suite runner**

Replace `test/matcher/run.sh` with:

```sh
#!/bin/sh
# test/matcher/run.sh -- the matcher regression suite (matcher substrate spec
# section 4, P1/P2 gates).  From anywhere:  sh test/matcher/run.sh
# Env:
#   MR_LEGS         tree (default) | tree,maxima
#   MR_MODEL_FLAGS  1: the Maxima leg simplifies under radexpand:false and
#                   logexpand:false; outputs are roundtrip.flags.out / gate.flags.out
#   MR_SPIKE        1: also run the spike-01 cases (test/matcher/spike01.out) and gate them
#   MR_WORK         work dir (default ${TMPDIR:-/tmp}/mr-matcher-suite[.flags])
# Prints the gate's Results line.
set -u
cd "$(dirname "$0")/../.."
N=20
LEGS=${MR_LEGS:-tree}
FLAGS=${MR_MODEL_FLAGS:-0}
SUFFIX=""
[ "$FLAGS" = 1 ] && SUFFIX=".flags"
WORK=${MR_WORK:-${TMPDIR:-/tmp}/mr-matcher-suite$SUFFIX}
mkdir -p "$WORK"
rm -f "$WORK"/shard*.tsv "$WORK"/shard*.log
python3 probes/matcher/02-roundtrip.py gen "$WORK/cases.tsv" > "$WORK/gen.log" || exit 1
i=0
while [ "$i" -lt "$N" ]; do
  MR_CASES="$WORK/cases.tsv" MR_NSHARDS=$N MR_SHARD=$i MR_RESULTS="$WORK/shard$i.tsv" \
    MR_MODES=narrow,wide MR_LEGS=$LEGS MR_MODEL_FLAGS=$FLAGS \
    timeout 3600 maxima --very-quiet -b test/matcher/roundtrip.mac > "$WORK/shard$i.log" 2>&1 &
  i=$((i + 1))
done
wait
{
  echo "=== test/matcher round trip  legs: $LEGS  model flags: $FLAGS  judged: $(date -u '+%Y-%m-%d %H:%M UTC')"
  echo "git HEAD: $(git rev-parse HEAD)"
  MR_MODES=narrow,wide MR_LEGS=$LEGS python3 probes/matcher/02-roundtrip.py judge "$WORK" "$N"
} > "test/matcher/roundtrip$SUFFIX.out"
python3 probes/matcher/02-roundtrip.py controls > "$WORK/controls-data.lisp" || exit 1
MR_CONTROLS="$WORK/controls-data.lisp" timeout 600 maxima --very-quiet -b test/matcher/controls.mac 2>&1 \
  | grep '^CONTROL' > test/matcher/controls.out
GATE="--report test/matcher/roundtrip$SUFFIX.out --controls test/matcher/controls.out"
case "$LEGS" in *maxima*) GATE="$GATE --maxima" ;; esac
if [ "${MR_SPIKE:-0}" = 1 ]; then
  timeout 600 maxima --very-quiet -b test/matcher/spike01.mac 2>&1 | grep '^SPIKE' > test/matcher/spike01.out
  GATE="$GATE --spike test/matcher/spike01.out"
fi
python3 test/matcher/gate.py $GATE > "test/matcher/gate$SUFFIX.out"
tail -1 "test/matcher/gate$SUFFIX.out"
```

- [ ] **Step 4: Run the defaults arm (background)**

```bash
setsid sh -c 'MR_LEGS=tree,maxima MR_SPIKE=1 sh test/matcher/run.sh > /tmp/claude-mr-p2.log 2>&1; echo done >> /tmp/claude-mr-p2.log' &
```
Poll until `/tmp/claude-mr-p2.log` ends with `done`. Expected last gate line: `Results: 107 passed, 0 failed`
(35 of Task 6 + 2 maxima-leg checks + the spike-01 count check + 69 gated spike cases).

- [ ] **Step 5: Run the flags arm (background, after Step 4 finished)**

```bash
setsid sh -c 'MR_LEGS=tree,maxima MR_MODEL_FLAGS=1 MR_SPIKE=1 sh test/matcher/run.sh > /tmp/claude-mr-p2f.log 2>&1; echo done >> /tmp/claude-mr-p2f.log' &
```
Expected: `Results: 107 passed, 0 failed` in `test/matcher/gate.flags.out`.

- [ ] **Step 6: Read the P2 evidence**

```bash
grep -E '^(FAIL|Results)' test/matcher/gate.out test/matcher/gate.flags.out
grep -E '^(SUMMARY (narrow|wide) maxima leg|MODEL-LOST (narrow|wide))' test/matcher/roundtrip.out test/matcher/roundtrip.flags.out | cut -c1-300
```
Expected (pre-validation figures; re-measured here): defaults arm narrow MODEL-LOST 1,166 variants /
395 rules, wide 1,046 / 307 (+120 WRONG/WIDE-OK); flags arm 23 / 4 in both modes; the `-Complex`
rewrite kind absent (G-3 folding). A gate `FAIL` → **stop**, systematic-debugging: reproduce the
variant as a `check-conv` (converter) or `check-match` (matcher) unit test first.

- [ ] **Step 7: Ledger and commit**

Append to the plan's section in `.superpowers/sdd/progress.md`:

```markdown
### Task 8 — P2 gate (converter, Maxima leg, spike-01)
- gate defaults arm: <Results line of test/matcher/gate.out>
- gate flags arm: <Results line of test/matcher/gate.flags.out>
- <the SUMMARY maxima leg + MODEL-LOST lines, both arms, both modes>
- spike-01: 69/69 gated cases; model cases G1-04, G7-M1 reported
- Plan 1 complete: P0 baseline, P1 and P2 gates green. Next: Plan 2 (P3–P4).
```

Fill every `<…>` with the literal lines, then:

```bash
git add test/matcher/maxima-leg.lisp test/matcher/spike01.lisp test/matcher/spike01.mac \
  test/matcher/roundtrip.mac test/matcher/run.sh \
  test/matcher/roundtrip.out test/matcher/roundtrip.flags.out test/matcher/controls.out \
  test/matcher/spike01.out test/matcher/gate.out test/matcher/gate.flags.out .superpowers/sdd/progress.md
git commit -m "$(printf 'matcher: P2 gate — Maxima leg through mr-tree (defaults + radexpand/logexpand arm) + spike-01 cases\n\nEvidence in test/matcher/*.out and the ledger. Plan 1 (P0-P2) complete.\n\nClaude-Session: https://claude.ai/code/session_01D5eoebxrtMKBBUSqYf2MGa')"
```

---

## Self-review (plan vs spec, at writing time)

- **Spec §4 P0:** Task 3 (three full runs, medians, Layer A) + Task 4 (campaign close precondition
  §0.4, fingerprint assertion, baseline records, ledger) + Task 1 (probe 03 fix and commit, node census)
  + Task 2 (the median tool). The class-3 run-to-run noise band is an addition (informs P5 attribution).
- **Spec §4 P1:** Task 5 (`mr-match`, §3.2 in full: match-flat, native Optionals, G-1, G-2, G-3 Complex
  pattern, no `meval`, hygiene, both switches, condition hook) + Task 6 (round trip + controls retargeted,
  gate: 0 UNSOUND, 0 false mutation matches, 41 G-2 rules, G-4 via UNSOUNDRULES 0, rules OK ≥ 7,435,
  narrow collapsed 0 UNSOUND). "Stack overflow" unit test: not applicable (deviation 2).
- **Spec §4 P2:** Task 7 (`mr-tree`, §3.3: head table from Maxima operators, complex folding, canonical
  order, `MX_` heads, `tree->max` simplified once) + Task 8 (Maxima leg under defaults and the
  radexpand/logexpand arm with MODEL-LOST reported, no tree-leg regression, spike-01 cases — deviation 4).
- **Out of this plan (Plans 2–3):** §3.4 generator, §3.5 dispatcher/loader/TLS, §3.6 switches as Maxima
  option variables, P3–P6.
- **Placeholders:** the only `<…>` markers are the ledger snippets whose content is literal command output
  captured during execution; each step says to fill them before committing.
- **Names used across tasks:** `MR-MATCH` exports (Task 5) are the ones Tasks 6–8 call; `mr-roundtrip::*converter*`
  (Task 6) is what `maxima-leg.lisp` (Task 8) binds; `mr-tree:maxima-name` is exported (Task 7) and used by
  `maxima-leg.lisp`; `gate.py` flags `--report/--controls/--g2/--maxima/--spike` match `run.sh`.
