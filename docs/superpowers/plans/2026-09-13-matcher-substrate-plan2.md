# Matcher Substrate — Plan 2 (P3–P4): generator, dispatcher, runtime

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Regenerate the class 1–3 rule files as evaluated-FullForm pattern records
(`%mr_defrule`) and run them on the matcher substrate — a Lisp dispatcher over `MR-MATCH` /
`MR-TREE` that replaces `defmatch` and the pass-2–4 rescans — with the spec's P3 static gate
and P4 gates green.

**Architecture:** The generator emits each rule's `Int[<pattern>, x_Symbol]` LHS as the
reader's evaluated FullForm s-expression, with the Maxima capture names as pattern-variable
names, and keeps every cond/repl body byte-identical except the spec's closed exception list
(inner conditions move into cond, nonzero guards go, MatchQ sites become pattern strings, 9.1
becomes a generated source). `maxima_rubi_dispatch.lisp` prepares each pattern once at load
and `%mr_dispatch_tree` walks the table: `mr-match:match` with a condition hook that builds the
`mm` binding list, runs cond under `errcatch` (retrying bindings per `mr_cond_retry`), then
repl. `mr_top` dispatches once, binding `radexpand:false` / `logexpand:false` while
`mr_model_flags` is true.

**Tech Stack:** Maxima `branch_5_50_base_84_g4204fb669` (build date 2026-08-31 13:27:47) /
SBCL 2.6.7; Common Lisp loaded into Maxima with `load("…lisp")`; Python 3 generator and
gates.

**Spec:** `docs/superpowers/specs/2026-09-12-matcher-substrate-design.md` (committed
`48c61b8`) — §3.4 (generator, rule format), §3.5 (dispatch, runtime, TLS), §3.6 (switches),
§4 P3/P4 (gates), §6 (risks), §7 (deletions, P3/P4 rows). This is Plan 2 of three (user
decision 2026-09-12: Plan 2 = P3–P4, Plan 3 = P5–P6). Plan 1
(`docs/superpowers/plans/2026-09-12-matcher-substrate-plan1.md`) is executed; its figures are
in `.superpowers/sdd/progress.md` § "Plan: 2026-09-12 matcher substrate plan 1".

**Attachments:** `docs/superpowers/plans/2026-09-13-matcher-substrate-plan2.files/`, committed
with this plan — the verbatim inputs too long to repeat inline (user decision 2026-09-13):

| attachment | used by |
|---|---|
| `generator/splice_gen.py`, `generator/new_matchq.py`, `generator/new_with.py`, `generator/new_emit.py`, `generator/new_main.py` | Task 2 Step 2 |
| `generator/generate_rules.handedits.patch` | Task 2 Step 3 |
| `utils/edit_utils.py`, `utils/maxima_rubi_utils.handedits.patch` | Task 5 Steps 2–3 |
| `loader/maxima_rubi.mac.patch` | Task 5 Step 4 |
| `layerA/layerA_rewrite.py`, `layerA/binds_helper.mac`, `layerA/test_*.mac` (9 replaced sections + `test_generated_matchq_shapes.mac`) | Task 6 |
| `probes/06-dispatch-cost.{mac,sh}`, `probes/07-fault-survival.sh`, `probes/08-runtime-load.sh` | Task 7 |

**Deviations from the spec's wording (stated, not silent):**

1. *Capture names in the pattern.* The emitted s-expression names each pattern variable with
   its Maxima capture name (`_mr_<key>_r<n>_<v>`; `x` keeps its name and is pre-bound), so the
   dispatcher's binding list is the `mm` list itself (§3.4 "Captures").
2. *Record handles.* `%mr_defrule` returns an integer handle (a 1-based index into a Lisp
   registry); `mr_rules_<key>` and `mr_rule_table` are lists of handles. Every
   `mr_rules_<key> : [ … ]$` line stays byte-identical.
3. *MatchQ is 4-arg* (§3.4 says 3-arg): `%mr_matchQ(u, "<pattern>", [<parts>], cond)`. MatchQ
   patterns contain `x`, outer captures (1.4.2 r17, 3.2.3 r16) and computed values
   (`%mr_expon(…)`, 1.4.1 r4/r68); each pattern-free non-numeric part becomes a placeholder
   `(MRArg k)` whose Maxima value is the k-th list element, evaluated at call time.
   `%mr_matchQ_bindings` (same arguments) returns the accepted binding list.
4. *9.1 = 28 generated rules; total 3,513* (§2.3 / §4 say 3,514): the pinned 9.1 source's
   first rule (`Int[u_.*(v_+w_)^p_., x_Symbol]`, L4) is commented out; the manual port carried
   it as a 29th, dead rule. The static gate expects 9_1: 29 → 28.
5. *One accepted G-9 risk* (§3.4 makes every risk flag a `GenError`): 9.1 r11's
   `Complex[0, a_]` (`ACCEPTED_RISKS`, a closed list); 9.1 is outside the probe-02 census.
6. *Function-valued captures* (3.1.5 r58/r59, 3.3 r58, 3.4 r37): `F[args]` in cond/repl →
   `apply(<cap>, [args])`; `MemberQ[{ArcSin, …}, F]` → `%mr_memberQ([asin, …], <cap>)`. The
   dispatcher binds the head to the `MR-TREE` head table's operator symbol, the symbol the
   typed name reads as (`asin` reads as the noun `%asin`); a `$verbify`'d `$ASIN` is not a
   member of the literal list (measured 2026-09-13).
7. *Fault guard* (§3.5 step 5: "the process never dies on a matcher fault"). The dispatcher
   catches every `serious-condition` a match, a cond or the conversion signals and counts it as
   no match. It cannot make control-stack exhaustion survivable when SBCL hits the guard page
   inside an allocation: a runaway Maxima recursion in a cond called from inside
   `mr-match:match` killed the process ("Control stack exhausted while pseudo-atomic") in 5 of
   6 measured shapes, while the same recursion at Maxima's top level survived 8 of 8 (Task 7,
   probe 07). The unit test uses a signalled `storage-condition`; the corpus-level check
   (crash counts vs P0) belongs to P5 (Plan 3).
8. *Switch recording.* The three switches are `defmvar`s in `maxima_rubi_dispatch.lisp`
   (`mr_flat_wide` false, `mr_cond_retry` true, `mr_model_flags` true). Writing them into the
   driver's `filter:` line (§3.6) is deferred to Plan 3: P5's runs are the first to flip them.
9. *Test and debug entries* not in the spec: `%mr_rule_bindings(h, f, x)` (first complete
   binding, no cond), `%mr_rule_accept(h, f, x)` (first binding the cond accepts),
   `%mr_rule_apply(h, f, x)` (pattern, cond and repl, as the dispatcher runs them).
10. *`%mr_algebraicFunctionQ` gains Rubi's optional flag* (IntegrationUtilityFunctions.m:1681
    `AlgebraicFunctionQ[u_, x_Symbol, flag_:False]`). Exactly three rules pass it (3.1.5 r30,
    3.3 r32, 3.3 r61); `defmatch` never reached their conds, and on the substrate the 2-arg
    port raised "Too many arguments" (a misfire).
11. *Layer A.* The matcher-coupled sections (§2.3) are rewritten against the substrate entries
    (Task 6); where `MR-MATCH` disagrees with a defmatch-era pin, the pin follows `MR-MATCH`
    (listed in Task 6). Count 892 → 897: the rewrite leaves 875, and a new section pins the
    nine generated MatchQ pattern shapes no other check covers (22 checks, §3.4). The matcher,
    converter and dispatcher checks §4 P4 adds live in the three `test/matcher/` unit suites
    (Plan 1's layout; Tasks 3–4), not in `test_maxima_rubi.mac`. The c4 / b3 / c5 answer checks' minimal tables gain the
    3_1_x files: once deviation 10 makes 3.3 r61 (the `Unintegrable` catch-all) reachable, it
    fires on their sub-integrals when the 3.1.x rules are not loaded ahead of it.
12. *Task split.* P3 is two tasks (the gate, then the whole generator change — the closed
    exception list is one end state). The dispatcher (Task 4) is unit-tested by loading the
    matcher, converter, utils and dispatcher directly, before the loader is rewired (Task 5).
    Plan 1's carried items are placed as follows: 1 (dispatch cost) → Task 7; 2 (fault guard)
    → Task 4 and deviation 7; 3 (converter: CRE, booleans) → Task 3 — the `MX_` plist
    re-read issue is not reachable (the dispatcher never prints and re-reads a tree) and is
    deferred, and `sb-ext:with-timeout` stays out of the dispatcher; 4 (`prepare` invariant)
    and 8 (nits) → Task 3; 5 (MODEL-LOST diff), 6 (launcher stale shards) and 7 (speed-gate
    definition) → Plan 3, whose P5 runs need them.

## Global Constraints

Every task's requirements implicitly include this section.

- **Build (stamp, never pin):** every committed measurement output carries `build_info()`
  (`build_info()@version`, `build_info()@timestamp`) or, for a no-Maxima script, the run date
  and git HEAD.
- **TLS:** any maxima process that loads *rule files* runs with `-X "--tls-limit 100000"` (two
  argv tokens) until Task 7's measurement retires the rule. The matcher, converter and
  dispatcher unit suites load no rule files and need no flag.
- **P3/P4 coupling (spec §4):** between Task 2's commit and Task 5's the package does not run
  (the regenerated rules need the new dispatcher). No Layer A or Layer B run is taken on those
  commits; P3's gate is static. The P0 commit `0a6664c` and its pinned core are the rollback.
- **Byte-identity after Task 2:** `python3 generator/generate_rules.py --class 1`, `--class 2`,
  `--class 3` leave `git status --porcelain rules/` empty.
- **30 s corpus cap STAYS.** No Layer B run in this plan (P5 is Plan 3).
- **Bash tool cap 120 s:** runs longer than that go through `run_in_background` or
  `setsid … &` and are polled; never block a tool call on them.
- **Git:** no `git add -A` (the tree carries untracked campaign logs and baselines); commit
  messages end with the executing session's `Claude-Session:` trailer and never
  `Co-Authored-By`; push only when asked; default branch `master`; work on `matcher-substrate`.
- **Test protocol:** every suite prints `PASS:`/`FAIL:` lines and ends with
  `Results: <n> passed, <m> failed`; a missing Results line is a failure.
- **A killed maxima needs stdin from `/dev/null`:** a fatal SBCL error drops into the `ldb`
  monitor, which otherwise waits for input and hangs the caller; probes that can hit one use
  `< /dev/null` and `timeout -s KILL`.
- **Tree notation (Plan 1):** a tree is an atom — integer, ratio, double-float, complex, string,
  or symbol in package `MRS` (case preserved) — or a list `(head arg…)`. Text form = the
  probe-02 s-expressions (`rd.to_sexp`); `|…|` quotes a name with lowercase letters.
- **Rule record notation:** `(Int <pattern> (Pattern x (Blank Symbol)))`; `(Pattern name
  (Blank))` = `name_`; `(Optional (Pattern name (Blank)))` = `name_.` (the default comes from
  the parent: Plus 0, Times 1, Power exponent 1).
- **Matcher semantics oracle:** `verify()` in `probes/matcher/02-roundtrip.py` (narrow
  reading); the matcher regression suite (`test/matcher/run.sh`) holds `MR-MATCH` to it.

## File structure

| file | responsibility | task |
|---|---|---|
| `generator/mma_reader.py` (`git mv` from `probes/matcher/02-mma-reader.py`) | Mathematica reader, `evaluate_lhs`, self-test | 1 |
| `probes/matcher/02-roundtrip.py`, `02-construct-census.py` (modify) | import the reader from `generator/` | 1 |
| `test/check_generated_rules.py` (create) | the P3 static gate | 1 |
| `test/matcher/prepare_patterns.lisp` (create) | prepares every pattern string in plain SBCL (gate check 11) | 1 |
| `generator/generate_rules.py` (modify) | workaround emitters deleted; pattern emission, `%mr_defrule` format, inner-condition move, MatchQ strings, 9.1 source | 2 |
| `generator/translation_table.py` (modify) | `Identity` | 2 |
| `rules/class{1,2,3}/*.mac` (regenerate; `rules/class1/9_1.mac` now generated) | the rule records | 2 |
| `maxima_rubi_match.lisp` (modify) | `prepare` rejects a Power-exponent Optional default ≠ 1; `flat-absorb` docstring | 3 |
| `maxima_rubi_tree.lisp` (modify) | booleans ↔ `True`/`False`; CRE input | 3 |
| `test/matcher/test_mr_match.lisp`, `test_mr_tree.lisp` (modify) | +2 / +5 checks | 3 |
| `test/matcher/{roundtrip,controls,spike01,gate}.out`, `{roundtrip,gate}.flags.out` (regenerate) | regression-suite records | 3, 7 |
| `maxima_rubi_dispatch.lisp` (rewrite) | records, dispatcher, MatchQ entries, switches, arity dispatchers | 4 |
| `test/matcher/test_mr_dispatch.mac` (create) | dispatcher unit suite (45 checks) | 4 |
| `maxima_rubi_utils.mac` (modify) | deleted families; `mr_top` / `%mr_hybrid_body` dispatch; utility MatchQ sites; `%mr_algebraicFunctionQ` flag | 5 |
| `maxima_rubi.mac` (modify) | loads match / tree / dispatch with witnesses | 5 |
| `maxima_rubi_implicit1.lisp`, `maxima_rubi_pass4.lisp` (delete) | — | 5 |
| `test/build_rules_core.sh`, `test/corpus_driver.py` (modify) | core fingerprint file lists | 5 |
| `test_maxima_rubi.mac` (modify) | matcher-coupled sections rewritten; generated MatchQ shapes section added | 6 |
| `probes/matcher/06-dispatch-cost.{mac,sh,out}`, `07-fault-survival.{sh,out}`, `08-runtime-load.{sh,out}` (create) | measured dispatch cost, fault survival, TLS / load / core build | 7 |
| `AGENTS.md`, `todo/TODO.md`, `.superpowers/sdd/progress.md` (modify) | TLS rule, suite commands and counts, P3 gate command, status, ledger | 7 |

## Task overview

| task | phase | deliverable | gate |
|---|---|---|---|
| 1 | P3 | reader promoted; static gate + pattern preparer | gate red on the P0 tree: `6 passed, 5 failed` |
| 2 | P3 | generator rewritten; classes 1–3 regenerated | static gate `11 passed, 0 failed`; regeneration idempotent |
| 3 | P4 | matcher / converter hardening | `test_mr_match` 53/0, `test_mr_tree` 51/0, regression suite 109/0 both arms |
| 4 | P4 | dispatcher + unit suite | `test_mr_dispatch` 45/0 |
| 5 | P4 | runtime wiring (loader, utils, deletions, core lists) | package loads; `mr_load_all()` 3,513; smoke answers; unit suites green |
| 6 | P4 | Layer A rewrite + generated MatchQ shapes section | Layer A `897 passed, 0 failed` |
| 7 | P4 | measurements (TLS flagless, load, core build, dispatch cost, fault survival); docs; ledger | P4 gate records (spec §4) |

**Pre-validation (plan-writing sessions 2026-09-12/13, throwaway worktree
`.claude/worktrees/plan2-proto`, not committed):** the code of every task was run before this
plan was written, on build `branch_5_50_base_84_g4204fb669` / SBCL 2.6.7. The static gate
reads `Results: 6 passed, 5 failed` on the P0 tree and `11 passed, 0 failed` after Task 2
(bodies identical 3,209; nonzero guards removed 2,347; inner conditions moved 226 + 1 in an
exempt rule; MatchQ sites 20 + 3; 3,537 pattern strings prepare). The attachments replayed
from `3fcc474` reproduce the prototype byte for byte (every non-ignored file; the regression
suite's run records excluded). Unit suites `test_mr_match` 53/0, `test_mr_tree` 51/0,
`test_mr_dispatch` 45/0 (48/0 while it still carried the three `mr_model_flags` checks);
matcher regression suite 109/0 on both arms (51.2 s and 50.9 s wall); Layer A 897/0 in 1.8 s
wall with the TLS flag and 1.9 s without it (875/0 in 1.3 s before the MatchQ-shapes section); flagless `mr_load_all()` + `rubi` answered (table 3,513,
1.4 s); `mr_load_all()` 1.0 s; rules core build 2.9 s. Dispatch cost (full-table walk of
`%mr_rule_accept`): `sin(x)^x` 0.04 s; `x^2*(a+b*x)^3*(c+d*x)^4*(e+f*x)^5*(g+h*x)^6*log(x)`
77.9 s, of which 3.5 r37 (a moved inner condition that integrates) 19.1 s, 3.1.5 r28 and 3.5
r11 (moved inner conditions that expand) 9.3 s each; `x*y1*…*yk` k = 6/8/10/12: 2.0 / 7.8 /
34.3 / 172.7 s; end-to-end `rubi()` on the 77.9 s integrand 39.7 s vs 47.8 s on the P0
package. The numbers here are expectations, not citations: Task 7 re-measures and commits
them.

---

### Task 1: Reader promotion and the P3 static gate (red on the P0 tree)

Branch: `matcher-substrate` (at `3fcc474`, the P0 tree for every generated file).

**Files:**
- Move: `probes/matcher/02-mma-reader.py` → `generator/mma_reader.py` (docstring header)
- Modify: `probes/matcher/02-roundtrip.py` (line 70), `probes/matcher/02-construct-census.py` (line 44)
- Create: `test/matcher/prepare_patterns.lisp`, `test/check_generated_rules.py`

**Interfaces:**
- Consumes: Plan 1's `maxima_rubi_match.lisp` (`MR-MATCH`: `read-tree`, `prepare`); git objects of
  the P0 commit `0a6664c`.
- Produces:
  - `generator/mma_reader.py`, importable as `mma_reader` with `generator/` on `sys.path` (Task 2:
    `import mma_reader as rd`; uses `rd.parse`, `rd.evaluate_lhs`, `rd.to_sexp`, `rd.fullform`,
    `rd.ParseError`, `rd.Str`, `rd.Real`).
  - `python3 test/check_generated_rules.py [--base <commit>]` — the P3 gate; exit 0 iff it ends
    `Results: 11 passed, 0 failed`.
  - `sbcl --script test/matcher/prepare_patterns.lisp <maxima_rubi_match.lisp> <patterns.tsv>` —
    one `FAIL:` line per pattern that does not read or prepare; ends with a `Results:` line.

- [ ] **Step 1: Move the reader**

```bash
git mv probes/matcher/02-mma-reader.py generator/mma_reader.py
```

In `generator/mma_reader.py` replace the first lines of the module docstring

```python
"""probes/matcher/02-mma-reader.py -- Mathematica InputForm reader for the
matcher expressibility probes (handoffs/2026-09-11-matcher-design.md, move 2).

Library module, loaded by the other 02-* probes through importlib (the file
name is not an importable module name).  Run directly it executes its
self-test:  python3 probes/matcher/02-mma-reader.py
```

with

```python
"""generator/mma_reader.py -- Mathematica InputForm reader: the generator's
pattern emitter (matcher substrate spec section 3.4) and the matcher
expressibility probes (handoffs/2026-09-11-matcher-design.md, move 2).

Library module: generator/generate_rules.py imports it; the 02-* probes load
it through importlib (it was probes/matcher/02-mma-reader.py until plan 2).
Run directly it executes its self-test:  python3 generator/mma_reader.py
```

- [ ] **Step 2: Point the two probes at the new path**

In both `probes/matcher/02-roundtrip.py` and `probes/matcher/02-construct-census.py` replace

```python
_spec = importlib.util.spec_from_file_location("mmareader", HERE / "02-mma-reader.py")
```

with

```python
_spec = importlib.util.spec_from_file_location("mmareader", HERE.parents[1] / "generator" / "mma_reader.py")
```

- [ ] **Step 3: Run the self-tests**

Run: `python3 generator/mma_reader.py | tail -1` and `python3 probes/matcher/02-roundtrip.py selftest | tail -1`
Expected: `Results: 27 passed, 0 failed` and `Results: 14 passed, 0 failed`.

- [ ] **Step 4: Create `test/matcher/prepare_patterns.lisp`**

```lisp
;;;; test/matcher/prepare_patterns.lisp -- prepare every generated pattern
;;;; string in MR-MATCH: part of the P3 static gate
;;;; (test/check_generated_rules.py; matcher substrate spec section 4 P3).
;;;; No Maxima: plain SBCL.
;;;;
;;;; Run: sbcl --script test/matcher/prepare_patterns.lisp <maxima_rubi_match.lisp> <patterns.tsv>
;;;; TSV lines: <id> TAB <pattern s-expression>.  One FAIL: line per pattern
;;;; that does not read or prepare; ends with "Results: <n> passed, <m> failed".

(let* ((args (last sb-ext:*posix-argv* 2))
       (passed 0)
       (failed 0))
  (load (first args))
  (let ((read-tree (find-symbol "READ-TREE" :mr-match))
        (prepare (find-symbol "PREPARE" :mr-match)))
    (with-open-file (in (second args))
      (loop for line = (read-line in nil)
            while line
            do (let ((tab (position #\Tab line)))
                 (handler-case
                     (progn (funcall prepare (funcall read-tree (subseq line (1+ tab))))
                            (incf passed))
                   (error (e)
                     (incf failed)
                     (format t "FAIL: ~a ~a~%" (subseq line 0 tab)
                             (substitute #\Space #\Newline (princ-to-string e)))))))))
  (format t "Results: ~a passed, ~a failed~%" passed failed))
```

- [ ] **Step 5: Create `test/check_generated_rules.py`**

```python
#!/usr/bin/env python3
"""test/check_generated_rules.py -- the P3 static gate of the matcher
substrate migration (spec docs/superpowers/specs/2026-09-12-matcher-
substrate-design.md section 4, P3; section 3.4 closed exception list).

Compares the generated rule files of the working tree with those of a base
commit (default: the P0 baseline commit 0a6664c) without running Maxima:

  1. rule counts per file unchanged (9_1: 29 -> 28, the pinned source's
     commented-out L4 rule), every mr_rules_<key> list line unchanged
     (9_1 excepted);
  2. no defmatch / matchdeclare left in any rule file; one %mr_defrule per
     rule;
  3. every cond and repl body byte-identical to the base, except the closed
     exception list, each exception verified as the exact text
     transformation it claims to be:
       - removed nonzero guards: old cond == "(" + new + ")  and  " + guards
       - moved inner conditions: the repl loses its
         "(if is(C) = true then X else false)" guard and the cond gains
         "  and  block([L], A, is(C) = true)"
       - MatchQ sites: each %mr_matchQ(...) call is compared masked
       - the 29 manual 9.1 rules and the 52 rules that had a workaround
         emitter (no defmatch in the base) are exempt;
  4. the generator's reader self-test is green;
  5. every moved inner condition whose With/Module locals call a package
     entry (mr_int, rubi, ...) is listed and must be in RESOLVED;
  6. every %mr_defrule and %mr_matchQ pattern string prepares in MR-MATCH
     (plain SBCL, test/matcher/prepare_patterns.lisp).

Usage:  python3 test/check_generated_rules.py [--base <commit>]
Ends with "Results: <n> passed, <m> failed".
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P0_BASE = "0a6664c"
WORKAROUND_RULES = 52
MOVED_INNER = 227
MATCHQ_SITES = 23
ENTRY_CALL = re.compile(r"\b(mr_int|mr_top|rubi|rubi_fallback|rubi_hybrid|rubi_hybrid_exact)\(")
# user decision 2026-09-12 (Plan 2 writing session): move all 227 inner
# conditions, including those whose locals integrate (IntHide -> mr_int);
# their extra cost is watched by the P5 median-wall gate.
RESOLVED_ENTRY_LOCALS = {
    "3_1_3 r18", "3_1_4 r23", "3_1_5 r21", "3_3 r26", "3_5 r37", "3_5 r38", "3_5 r40",
}
FUN = re.compile(r"^_mr_(cond|repl)_([0-9a-z_]+?)_r(\d+)\(mm, x\) := (.*?)\)\$\n", re.M | re.S)
GUARDS = re.compile(r"%mr_neQ\(_mr_[0-9A-Za-z_]+, 0\)(  and  %mr_neQ\(_mr_[0-9A-Za-z_]+, 0\))*")


class Gate:
    def __init__(self):
        self.passed = self.failed = 0

    def check(self, name, ok, detail=""):
        if ok:
            self.passed += 1
            print("PASS: %s" % name)
        else:
            self.failed += 1
            print("FAIL: %s%s" % (name, ("\n    " + detail) if detail else ""))


def git_show(base, rel):
    r = subprocess.run(["git", "show", "%s:%s" % (base, rel)], cwd=ROOT,
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def rule_files(base):
    r = subprocess.run(["git", "ls-tree", "--name-only", base, "rules/class1/",
                        "rules/class2/", "rules/class3/"], cwd=ROOT,
                       capture_output=True, text=True, check=True)
    return sorted(set(r.stdout.split()) |
                  {p.relative_to(ROOT).as_posix() for p in ROOT.glob("rules/class*/*.mac")})


def bodies(text):
    return {(k, int(n), kind): body for kind, k, n, body in FUN.findall(text or "")}


def mask_matchq(s):
    """Replace every balanced %mr_matchQ(...) call by a marker; -> (text, count)."""
    out, i, count = [], 0, 0
    while True:
        j = s.find("%mr_matchQ(", i)
        if j < 0:
            out.append(s[i:])
            return "".join(out), count
        depth, k = 0, j + len("%mr_matchQ")
        in_str = False
        while k < len(s):
            ch = s[k]
            if ch == '"':
                in_str = not in_str
            elif not in_str:
                depth += ch == "("
                depth -= ch == ")"
                if depth == 0:
                    break
            k += 1
        out.append(s[i:j] + "%mr_matchQ(...)")
        count += 1
        i = k + 1


def unsnap(s):
    return re.sub(r"(_mr_[0-9A-Za-z_]+?)__s\b", r"\1", s)


def moved_inner(old_repl, new_repl, old_cond_base, new_cond):
    """None if (old, new) is not a moved inner condition; else the inner
    block text (for the entry-call listing) when the transformation is exact,
    or False when the shapes look moved but do not match exactly."""
    x = new_repl[:-1] if new_repl.endswith(")") else None
    if x is None:
        return None
    for k in [m.start() for m in re.finditer(r"\(if is\(", old_repl)]:
        pre = old_repl[:k]
        if not new_repl.startswith(pre):
            continue
        inner = new_repl[len(pre):-1]
        tail = ") = true then " + inner + " else false))"
        if not old_repl.endswith(tail) or len(old_repl) - len(tail) < k + 7:
            continue
        c = old_repl[k + 7:len(old_repl) - len(tail)]
        scope = pre[pre.rindex("block(["):]
        want = "(%s)  and  %sis(%s) = true)" % (old_cond_base, unsnap(scope), unsnap(c))
        return want if new_cond == want else False
    return None


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=P0_BASE)
    a = ap.parse_args(argv)
    g = Gate()
    files = rule_files(a.base)
    counts_ok, lists_ok = [], []
    stats = dict(identical=0, guard=0, moved=0, matchq_old=0, workaround=0, nine=0,
                 no_defmatch=0, exempt_inner=0, exempt_matchq=0)
    unexplained, entry_locals, bad_moves = [], [], []
    for rel in files:
        old = git_show(a.base, rel)
        new = (ROOT / rel).read_text() if (ROOT / rel).exists() else None
        key = Path(rel).stem
        oc = re.search(r"^mr_rules_count_\w+ : (\d+)\$", old or "", re.M)
        nc = re.search(r"^mr_rules_count_\w+ : (\d+)\$", new or "", re.M)
        want = (29, 28) if key == "9_1" else (oc and int(oc.group(1)), oc and int(oc.group(1)))
        counts_ok.append((rel, bool(oc and nc) and (int(oc.group(1)), int(nc.group(1))) == want))
        if key != "9_1":
            ol = re.search(r"^mr_rules_\w+ : \[.*\]\$$", old or "", re.M)
            nl = re.search(r"^mr_rules_\w+ : \[.*\]\$$", new or "", re.M)
            lists_ok.append((rel, bool(ol and nl) and ol.group(0) == nl.group(0)))
        if new is not None:
            if re.search(r"^(defmatch|matchdeclare)\(", new, re.M):
                unexplained.append("%s: defmatch/matchdeclare present" % rel)
            ndef = len(re.findall(r"^_mr_rule_\w+ : %mr_defrule\(", new, re.M))
            if nc and ndef != int(nc.group(1)):
                unexplained.append("%s: %d %%mr_defrule for %s rules" % (rel, ndef, nc.group(1)))
        ob, nb = bodies(old), bodies(new)
        n_rules = int(oc.group(1)) if oc else 0
        for n in range(1, n_rules + 1):
            rid = "%s r%d" % (key, n)
            has_defmatch = re.search(r"^defmatch\(_mr_pat_%s_r%d," % (re.escape(key), n), old, re.M)
            if key == "9_1" or not has_defmatch:
                # exempt; counted so the totals reconcile with the spec's
                # closed list (227 inner conditions, 52 workaround rules,
                # 23 MatchQ sites are counted over all 3,514 rules)
                stats["nine" if key == "9_1" else "workaround"] += 1
                stats["no_defmatch"] += not has_defmatch
                orep = ob.get((key, n, "repl")) or ""
                stats["exempt_inner"] += bool(re.search(r"\(if is\(.*= true then", orep, re.S))
                rfun = re.search(r"^_mr_rule_%s_r%d\(f, x\) := (.*?)\)\$\n" % (re.escape(key), n),
                                 old, re.M | re.S)
                stats["exempt_matchq"] += (mask_matchq(ob.get((key, n, "cond")) or "")[1]
                                           + mask_matchq(orep)[1]
                                           + (mask_matchq(rfun.group(1))[1] if rfun else 0))
                continue
            oc_, or_ = ob.get((key, n, "cond")), ob.get((key, n, "repl"))
            nc_, nr_ = nb.get((key, n, "cond")), nb.get((key, n, "repl"))
            if None in (oc_, or_, nc_, nr_):
                unexplained.append("%s: cond/repl missing" % rid)
                continue
            # a body is "block([<locals>],\n  <binds>,\n  <expression>": the
            # locals and binds lines must match; the exceptions live in the
            # expression line
            parts = [b.split("\n  ", 2) for b in (oc_, or_, nc_, nr_)]
            if any(len(p) != 3 for p in parts) or parts[0][:2] != parts[2][:2] \
                    or parts[1][:2] != parts[3][:2]:
                unexplained.append("%s: locals/binds lines differ" % rid)
                continue
            oc_m, qo1 = mask_matchq(parts[0][2])
            or_m, qo2 = mask_matchq(parts[1][2])
            nc_m, _ = mask_matchq(parts[2][2])
            nr_m, _ = mask_matchq(parts[3][2])
            stats["matchq_old"] += qo1 + qo2
            base = oc_m
            if oc_m.startswith("("):
                for m in re.finditer(r"\)  and  ", oc_m):
                    if GUARDS.fullmatch(oc_m[m.end():]):
                        base = oc_m[1:m.start()]
                        stats["guard"] += 1
                        break
            if nr_m == or_m and nc_m == base:
                stats["identical"] += 1
                continue
            mv = moved_inner(or_m, nr_m, base, nc_m)
            if mv:
                stats["moved"] += 1
                if ENTRY_CALL.search(mv[mv.index("  and  "):]):
                    entry_locals.append(rid)
                continue
            (bad_moves if mv is False else unexplained).append(
                "%s: cond %s, repl %s" % (rid, "same" if nc_m == base else "DIFF",
                                          "same" if nr_m == or_m else "DIFF"))
    bad_counts = [r for r, ok in counts_ok if not ok]
    g.check("rule counts per file unchanged (9_1: 29 -> 28), %d files" % len(counts_ok),
            not bad_counts, "differ: %s" % bad_counts)
    bad_lists = [r for r, ok in lists_ok if not ok]
    g.check("mr_rules_<key> list lines unchanged (9_1 excepted)", not bad_lists, "differ: %s" % bad_lists)
    total = sum(int(m) for rel in files if (ROOT / rel).exists()
                for m in re.findall(r"^mr_rules_count_\w+ : (\d+)\$", (ROOT / rel).read_text(), re.M))
    g.check("total rules 3,513 (3,514 - the dead 9.1 L4 rule)", total == 3513, "total %d" % total)
    g.check("no defmatch/matchdeclare; one %mr_defrule per rule; every cond/repl explained",
            not unexplained, "\n    ".join(unexplained[:40]))
    g.check("moved inner conditions are exact transformations", not bad_moves, "\n    ".join(bad_moves[:40]))
    print("INFO: bodies identical %(identical)d, nonzero guards removed %(guard)d, inner conditions "
          "moved %(moved)d (+%(exempt_inner)d in exempt rules), MatchQ sites compared %(matchq_old)d "
          "(+%(exempt_matchq)d in exempt rules), rules without defmatch %(no_defmatch)d "
          "(workaround emitters %(workaround)d of them outside 9.1), manual 9.1 rules %(nine)d" % stats)
    g.check("inner conditions: moved + in exempt rules = %d" % MOVED_INNER,
            stats["moved"] + stats["exempt_inner"] == MOVED_INNER,
            "%d + %d" % (stats["moved"], stats["exempt_inner"]))
    g.check("rules without defmatch in the base = %d" % WORKAROUND_RULES,
            stats["no_defmatch"] == WORKAROUND_RULES, str(stats["no_defmatch"]))
    g.check("MatchQ sites: compared + in exempt rules = %d" % MATCHQ_SITES,
            stats["matchq_old"] + stats["exempt_matchq"] == MATCHQ_SITES,
            "%d + %d" % (stats["matchq_old"], stats["exempt_matchq"]))
    for rid in entry_locals:
        print("INFO: moved inner condition with a package entry in its locals: %s%s" % (
            rid, " (resolved)" if rid in RESOLVED_ENTRY_LOCALS else " (UNRESOLVED)"))
    g.check("every moved inner condition calling a package entry is resolved (%d)" % len(entry_locals),
            set(entry_locals) <= RESOLVED_ENTRY_LOCALS and entry_locals,
            "unresolved: %s" % sorted(set(entry_locals) - RESOLVED_ENTRY_LOCALS))
    r = subprocess.run([sys.executable, str(ROOT / "generator" / "mma_reader.py")],
                       capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or [""])[-1]
    g.check("reader self-test green (%s)" % last, re.fullmatch(r"Results: \d+ passed, 0 failed", last) is not None)
    with tempfile.NamedTemporaryFile("w", suffix=".tsv", delete=False) as tsv:
        n_pat = 0
        for p in sorted(ROOT.glob("rules/class*/*.mac")):
            text = p.read_text()
            for key, n, pat in re.findall(r'^_mr_rule_\w+ : %mr_defrule\("([0-9a-z_]+)", (\d+), "([^"]*)"',
                                          text, re.M):
                tsv.write("%s r%s\t%s\n" % (key, n, pat))
                n_pat += 1
            for pat in re.findall(r'%mr_matchQ\([^"]*?, "([^"]*)"', text):
                tsv.write("%s matchq\t%s\n" % (p.stem, pat))
                n_pat += 1
    r = subprocess.run(["sbcl", "--script", str(ROOT / "test" / "matcher" / "prepare_patterns.lisp"),
                        str(ROOT / "maxima_rubi_match.lisp"), tsv.name], capture_output=True, text=True)
    out = r.stdout.strip().splitlines()
    last = out[-1] if out else r.stderr[-300:]
    g.check("every pattern string prepares in MR-MATCH (%d strings; %s)" % (n_pat, last),
            last == "Results: %d passed, 0 failed" % n_pat, "\n    ".join(out[-10:]))
    print("Results: %d passed, %d failed" % (g.passed, g.failed))
    return 1 if g.failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 6: Run the gate on the P0 tree and confirm it is red for the right reasons**

Run: `python3 test/check_generated_rules.py | grep -a '^FAIL\|^Results'`
Expected (exactly these five FAIL lines, then the count):

```
FAIL: rule counts per file unchanged (9_1: 29 -> 28), 87 files
FAIL: total rules 3,513 (3,514 - the dead 9.1 L4 rule)
FAIL: no defmatch/matchdeclare; one %mr_defrule per rule; every cond/repl explained
FAIL: inner conditions: moved + in exempt rules = 227
FAIL: every moved inner condition calling a package entry is resolved (0)
Results: 6 passed, 5 failed
```

The six PASS lines are the list lines, exact moves (vacuous), 52 rules without defmatch, 23
MatchQ sites, the reader self-test and the pattern preparer (0 strings on the P0 tree).

- [ ] **Step 7: Commit**

```bash
git add generator/mma_reader.py probes/matcher/02-roundtrip.py probes/matcher/02-construct-census.py \
        test/check_generated_rules.py test/matcher/prepare_patterns.lisp
git commit -m "generator: promote the Mathematica reader; P3 static gate (red on the P0 tree)"
```

---

### Task 2: Generator rewrite and regeneration (P3 gate)

Branch: `matcher-substrate`.

**Files:**
- Modify: `generator/generate_rules.py` (3,712 → 1,580 lines), `generator/translation_table.py` (`RENAME`)
- Regenerate: every `rules/class1/*.mac`, `rules/class2/*.mac`, `rules/class3/*.mac` (`rules/class1/9_1.mac`
  becomes a generated file)

**Interfaces:**
- Consumes: Task 1's `generator/mma_reader.py` and gate; the attachments `generator/*`.
- Produces — the rule record format Tasks 4–6 load (cond and repl as before, then the registration):

```maxima
_mr_cond_1_1_1_1_r2(mm, x) := block([_mr_1_1_1_1_r2_m],
  _mr_1_1_1_1_r2_m : geteqR(mm, '_mr_1_1_1_1_r2_m),
  freeof(x, _mr_1_1_1_1_r2_m)  and  %mr_neQ(_mr_1_1_1_1_r2_m, -1))$
_mr_repl_1_1_1_1_r2(mm, x) := block([_mr_1_1_1_1_r2_m__s],
  _mr_1_1_1_1_r2_m__s : geteqR(mm, '_mr_1_1_1_1_r2_m),
  x^(_mr_1_1_1_1_r2_m__s + 1)/(_mr_1_1_1_1_r2_m__s + 1))$
_mr_rule_1_1_1_1_r2 : %mr_defrule("1_1_1_1", 2, "(Int (Power (Pattern x (Blank)) (Optional (Pattern |_mr_1_1_1_1_r2_m| (Blank)))) (Pattern x (Blank Symbol)))", _mr_cond_1_1_1_1_r2, _mr_repl_1_1_1_1_r2)$
```

  - `%mr_defrule(key, n, pattern-string, cond, repl)` → handle (Task 4); `mr_rules_<key> : [ _mr_rule_<key>_r1, … ]$` unchanged.
  - A MatchQ site: `%mr_matchQ(u, "<pattern with (MRArg k)>", [<part 1>, …], lambda([%mr_mqb], <cond with %mr_mk(<marker>, %mr_mqb)>))`
    or `…, true)` (Task 4), e.g. 1.1.2.10 r2:
    `not(%mr_matchQ(_mr_1_1_2_10_r2_Pq, "(Times (Optional (Pattern |_mr_1_1_2_10_r2mq1_u| (Blank))) (Power (MRArg 1) (Optional (Pattern |_mr_1_1_2_10_r2mq1_m| (Blank)))))", [x], lambda([%mr_mqb], integerp(%mr_mk(_mr_1_1_2_10_r2mq1_m, %mr_mqb)))))`.
  - A moved inner condition: `_mr_cond_… := block([caps], binds, (<outer cond>)  and  block([<locals>], <local assignments>, is(<inner cond>) = true))$`; the repl keeps `block([<locals>], …, <body>)` without the `(if is(…) = true then … else false)` guard.
  - A function-valued capture `F` in cond/repl: `apply(<cap F>, [<args>])`; `MemberQ[{ArcSin, …}, F]` → `%mr_memberQ([asin, acos, …], <cap F>)`.

- [ ] **Step 1: Delete the workaround emitters**

Confirm the four ranges' boundaries on the P0 file first:

```bash
for n in 203 204 575 576 748 749 840 841 1298 1299 1317 1318 1674 1675 3198 3199; do
  printf '%5d| %s\n' $n "$(sed -n "${n}p" generator/generate_rules.py | cut -c1-70)"; done
```

Expected: 204, 576, 749, 841, 1299, 1318, 1675, 3199 blank; 203 `    return vs - {"x"}`;
575 `    return out`; 748 `    return (s[:pos].strip(), s[pos+1:].strip())`; 840 `    return res`;
1298 `    return ", ".join(segs)`; 1317 `    return pats`; 1674 `    return f"{name}({', '.join(arglist)})"`;
3198 `_BARE_PAT = re.compile(r"_mr[0-9A-Za-z_]+\Z")`. Then:

```bash
sed -i '1675,3198d;1299,1317d;749,840d;204,575d' generator/generate_rules.py
```

The ranges (spec §3.4 "Deleted from the generator", §7 P3 row): 204–575 the two-binomial-power
manual matcher (`binpow_manual_match`) and the slot matcher (`slots_from_lhs`,
`_slot_tag_branches`, …); 749–840 `nonzero_guard_caps` and its helpers; 1299–1317
`power_dups`; 1675–3198 the workaround emitters (`_emit_binpow_manual`, `_MM_BOOL_GUARD`, the
headvar emitter, the slot-rule lines, C2 `dhead10`, M1, B33, C5, C4, C3) and the bare
catch-all special case.

- [ ] **Step 2: Splice in pattern emission, the new rule emitter and the 9.1 source**

```bash
A=docs/superpowers/plans/2026-09-13-matcher-substrate-plan2.files
python3 $A/generator/splice_gen.py $A/generator
```

Expected: `spliced 1557 lines`. `splice_gen.py` makes six asserted edits: (1) imports
`mma_reader as rd` and `Fraction`; (2) drops the MatchQ-marker branch of `translate_atom`
(patterns are no longer translated); (3) replaces `_emit_matchq` with `new_matchq.py`
(`_evaluated`, `_sexp`, `pattern_sexp`, `_input_form`, the 4-arg `%mr_matchQ` emitter);
(4) removes the headvar branch of `emit_head` and replaces its `With`/`Module` branch with
`new_with.py` (an inner `/;` reaching it is a `GenError`); (5) replaces `emit_rule` /
`emit_file` with `new_emit.py` (`split_inner_condition`, the cond/repl/`%mr_defrule` emitter,
the capture snapshots); (6) replaces `configure` and `main` with `new_main.py` (the 9.1 source
at the end of the class-1 table, `EXPECTED_TOTAL` class 1 = 2710 + EXTRA + 28).

- [ ] **Step 3: Apply the six hand edits**

```bash
git apply docs/superpowers/plans/2026-09-13-matcher-substrate-plan2.files/generator/generate_rules.handedits.patch
```

The patch adds: the `MemberQ[{…}, F]` path in `translate()` (deviation 6); `ACCEPTED_RISKS`
and its use in `_evaluated` (deviation 5); `NATIVE_FUNCTION_HEADS` (ArcSin…ArcCoth →
asin…acoth); `_input_form` parenthesizing only a nested Power operand (so `x^2` stays `x^2`
for `_emit_expon`); in `emit_head`, a capture used as a head → `apply(<cap>, [args])` and
`Complex[re, im]` → `(re + im*%i)` (9.1 L15).

- [ ] **Step 4: Translate `Identity`**

In `generator/translation_table.py`, in `RENAME`, after the line `"NonsumQ": "%mr_nonsumQ",` add

```python
    # 9.1 as a generated source (matcher substrate spec 3.4): Identity[-1],
    # Complex[Identity[0], a] (9.1.m L14/L15). Maxima's identity(x)
    # returns x (describe("identity", exact), 2026-09-12).
    "Identity": "identity",
```

- [ ] **Step 5: Regenerate classes 1–3**

```bash
for c in 1 2 3; do python3 generator/generate_rules.py --class $c | grep TOTAL; done
```

Expected: `TOTAL: 3054 rules — OK (== 3054)`, `TOTAL: 125 rules — OK (== 125)`,
`TOTAL: 334 rules — OK (== 334)`. Then check the new format:

Run: `grep -c '^_mr_rule_.* : %mr_defrule(' rules/class1/*.mac rules/class2/*.mac rules/class3/*.mac | awk -F: '{s+=$2} END {print s}'` and `grep -l 'defmatch\|matchdeclare' rules/class*/*.mac | wc -l`
Expected: `3513` and `0`.

- [ ] **Step 6: Regeneration is idempotent**

```bash
git add -N rules/ && git diff --stat rules/ | tail -1 > /tmp/p2t2-first.txt
for c in 1 2 3; do python3 generator/generate_rules.py --class $c > /dev/null; done
git diff --stat rules/ | tail -1 | diff - /tmp/p2t2-first.txt && echo IDEMPOTENT
```

Expected: `IDEMPOTENT`.

- [ ] **Step 7: Run the P3 gate**

Run: `python3 test/check_generated_rules.py | grep -a -v '^PASS'`
Expected:

```
INFO: bodies identical 3209, nonzero guards removed 2347, inner conditions moved 226 (+1 in exempt rules), MatchQ sites compared 20 (+3 in exempt rules), rules without defmatch 52 (workaround emitters 50 of them outside 9.1), manual 9.1 rules 29
INFO: moved inner condition with a package entry in its locals: 3_1_3 r18 (resolved)
INFO: moved inner condition with a package entry in its locals: 3_1_4 r23 (resolved)
INFO: moved inner condition with a package entry in its locals: 3_1_5 r21 (resolved)
INFO: moved inner condition with a package entry in its locals: 3_3 r26 (resolved)
INFO: moved inner condition with a package entry in its locals: 3_5 r37 (resolved)
INFO: moved inner condition with a package entry in its locals: 3_5 r38 (resolved)
INFO: moved inner condition with a package entry in its locals: 3_5 r40 (resolved)
Results: 11 passed, 0 failed
```

The seven resolved rules are the user decision recorded in the gate
(`RESOLVED_ENTRY_LOCALS`): all 227 inner conditions move, including those whose locals
integrate. No Layer A or Layer B run on this commit (Global Constraints, P3/P4 coupling).

- [ ] **Step 8: Commit**

```bash
git add generator/generate_rules.py generator/translation_table.py rules/class1 rules/class2 rules/class3
git commit -m "generator: evaluated-FullForm patterns + %mr_defrule records; classes 1-3 regenerated (P3 gate 11/0)"
```

---

### Task 3: Matcher and converter hardening (P4)

Branch: `matcher-substrate`.

**Files:**
- Modify: `maxima_rubi_match.lisp` (`prepare`, the Optional branch near line 197; `flat-absorb` docstring near line 407)
- Modify: `maxima_rubi_tree.lisp` (`convert` near line 132; the name → symbol function near line 162)
- Modify: `test/matcher/test_mr_match.lisp` (`test-prepare`), `test/matcher/test_mr_tree.lisp` (`test-max->tree`)
- Regenerate: `test/matcher/roundtrip.out`, `controls.out`, `spike01.out`, `gate.out`, `roundtrip.flags.out`, `gate.flags.out`

**Interfaces:**
- Consumes: Plan 1's `MR-MATCH` / `MR-TREE`; Maxima's `$ratdisrep`, `resimplify`.
- Produces (Task 4 relies on them):
  - `(mr-tree:max->tree e)` accepts CRE input (a `mrat` form converts through `ratdisrep`, re-simplified) and the
    booleans (`T` → `True`, `NIL` → `False`); `(mr-tree:tree->max (sym "True"))` = `T`, `False` → `NIL`.
  - `(mr-match:prepare p)` signals an error for a Power-exponent `Optional` whose explicit default is not 1
    (`collapsible-p` and `m-power` read that exponent as 1).

- [ ] **Step 1: Write the failing checks**

In `test/matcher/test_mr_match.lisp`, `test-prepare`, replace the last check

```lisp
    (check "rejects an Optional under Sin" (rejects "(Sin x_.)"))))
```

with

```lisp
    (check "rejects an Optional under Sin" (rejects "(Sin x_.)"))
    ;; collapsible-p and m-power read a Power exponent Optional as exponent 1
    (check "rejects a Power exponent Optional with default 2"
           (rejects "(Power x_ (Optional (Pattern m (Blank)) 2))"))
    (check "accepts a Power exponent Optional with explicit default 1"
           (not (rejects "(Power x_ (Optional (Pattern m (Blank)) 1))")))))
```

In `test/matcher/test_mr_tree.lisp`, `test-max->tree`, after the line
`  (check-conv "polylog(2,x)" "(PolyLog 2 x)")` add

```lisp
  ;; the dispatcher converts integrands and bindings, which can be CRE or boolean
  (check-conv "rat(a+b*x)" "(Plus a (Times b x))")
  ;; (a CRE numerator is an expanded polynomial)
  (check-conv "rat((1+x)^2/(2*y))" "(Times 1/2 (Plus 1 (Power x 2) (Times 2 x)) (Power y -1))")
  (check-conv "true" "True")
  (check-conv "false" "False")
  (check "tree->max True/False -> the Maxima booleans"
         (and (eq (tree->max (sym "True")) t) (null (tree->max (sym "False")))))
```

- [ ] **Step 2: Run them to see them fail**

Run: `maxima --very-quiet -b test/matcher/test_mr_match.mac | grep -a 'FAIL\|^Results'`
Expected: `FAIL: rejects a Power exponent Optional with default 2` and `Results: 52 passed, 1 failed`.

Run: `maxima --very-quiet -b test/matcher/test_mr_tree.mac < /dev/null 2>&1 | grep -a -A2 'rror\|^Results'`
Expected: `Maxima encountered a Lisp error:` / `mr-tree: cannot convert (#:G… …)` and no `Results:` line
(`convert` has no `mrat` case).

- [ ] **Step 3: The `prepare` invariant**

In `maxima_rubi_match.lisp`, in `prepare`'s Optional branch, replace

```lisp
                               (inner (second p)))
                          (unless (and (consp inner) (eq (car inner) +pattern+)
```

with

```lisp
                               (inner (second p)))
                          ;; collapsible-p and m-power read a Power exponent
                          ;; Optional as the implicit exponent 1
                          (when (and (eq parent +power+) (eql pos 2) (not (eql default 1)))
                            (fail "Power exponent Optional with default ~a (only 1 is supported): ~a"
                                  (tree-string default) (tree-string p)))
                          (unless (and (consp inner) (eq (car inner) +pattern+)
```

- [ ] **Step 4: The converter — booleans and CRE**

In `maxima_rubi_tree.lisp`, in `convert`, replace

```lisp
        ((floatp e) (coerce e 'double-float))
        ((symbolp e) (symbol->tree e))
```

with

```lisp
        ((floatp e) (coerce e 'double-float))
        ;; Maxima's booleans are the Lisp symbols T and NIL
        ((eq e t) (sym "True"))
        ((null e) (sym "False"))
        ((symbolp e) (symbol->tree e))
```

and replace

```lisp
           (cond ((eq op 'maxima::rat) (/ (first args) (second args)))
```

with

```lisp
           (cond ((eq op 'maxima::rat) (/ (first args) (second args)))
                 ;; CRE (rat()) input: convert its general representation,
                 ;; re-simplified -- ratdisrep's result is not in simplified
                 ;; form (1/(2*y) comes back as (2*y)^-1), which would give a
                 ;; non-canonical tree (plan-2 pre-validation, 2026-09-13)
                 ((eq op 'maxima::mrat) (convert (maxima::resimplify (maxima::$ratdisrep e))))
```

In the tree-symbol → Maxima-symbol function (the one that maps `"E"` / `"Pi"` / `"I"`), replace

```lisp
          ((string= n "I") 'maxima::$%i)
```

with

```lisp
          ((string= n "I") 'maxima::$%i)
          ((string= n "True") t)
          ((string= n "False") nil)
```

- [ ] **Step 5: The `flat-absorb` docstring (Plan 1 nit)**

In `maxima_rubi_match.lisp`, `flat-absorb`, replace

```lisp
them) is pure waste.  An absorber's pattern is a named Blank, so matching it
calls no condition hook -- the pruning changes no result and no hook call."
```

with

```lisp
them) is pure waste.  An absorber's pattern is a Blank -- named, unnamed or
headed, possibly under an Optional -- so matching it calls no condition hook:
the pruning changes no result and no hook call."
```

- [ ] **Step 6: Run the unit suites**

Run: `maxima --very-quiet -b test/matcher/test_mr_match.mac | grep -a '^Results'`,
`maxima --very-quiet -b test/matcher/test_mr_tree.mac | grep -a '^Results'` and
`sbcl --non-interactive --load maxima_rubi_match.lisp --load test/matcher/test_mr_match.lisp --eval '(mr-match-test:run)' | grep -a '^Results'`
Expected: `Results: 53 passed, 0 failed`, `Results: 51 passed, 0 failed`, `Results: 53 passed, 0 failed`.

- [ ] **Step 7: Run the matcher regression suite on both arms**

Each arm takes ~50 s wall; run them one after the other in the background
(`run_in_background`), then read the gate lines:

```bash
MR_LEGS=tree,maxima MR_SPIKE=1 sh test/matcher/run.sh > /tmp/p2t3-defaults.log 2>&1
MR_LEGS=tree,maxima MR_MODEL_FLAGS=1 MR_SPIKE=1 sh test/matcher/run.sh > /tmp/p2t3-flags.log 2>&1
grep -a 'Results' /tmp/p2t3-defaults.log /tmp/p2t3-flags.log
```

Expected: `Results: 109 passed, 0 failed` for both. Every changed line of the six records must
be a judged / git HEAD / build / TIMING line:

```bash
for f in roundtrip.out roundtrip.flags.out controls.out spike01.out gate.out gate.flags.out; do
  printf '%s ' $f; git diff test/matcher/$f | grep '^[-+]' | grep -v '^[-+][-+]' \
    | grep -v -i 'judged\|git HEAD\|TIMING\|build\|shard0.log\|run:' | wc -l; done
```

Expected: `0` after every file name.

- [ ] **Step 8: Commit**

```bash
git add maxima_rubi_match.lisp maxima_rubi_tree.lisp test/matcher/test_mr_match.lisp test/matcher/test_mr_tree.lisp \
        test/matcher/roundtrip.out test/matcher/controls.out test/matcher/spike01.out test/matcher/gate.out \
        test/matcher/roundtrip.flags.out test/matcher/gate.flags.out
git commit -m "matcher: prepare rejects a Power-exponent Optional default != 1; converter takes CRE and booleans"
```

---

### Task 4: The dispatcher and its unit suite (P4)

Branch: `matcher-substrate`. The package does not load in this task's end state (the P0 loader
still expects the deleted declaim / implicit-1 / pass-4 entries; Task 5 rewires it), so the
suite loads its four files directly.

**Files:**
- Rewrite: `maxima_rubi_dispatch.lisp`
- Create: `test/matcher/test_mr_dispatch.mac`

**Interfaces:**
- Consumes: Task 3's `MR-MATCH` (`read-tree`, `prepare`, `match` with `:bindings` and `:cond-hook`,
  `sym`, `*flat-wide*`, `*cond-retry*`) and `MR-TREE` (`max->tree`, `tree->max`, `head-table`);
  utils' `geteqR`, `%mr_containsBoolean`, `%mr_memberQ`, `%mr_mk`, `rubi_verbose`, `%mr_boolcheck`
  (unchanged from P0); Maxima's `errcatch`, `mfuncall`, `meval`, `errlfun1`, `bindlist`, `loclist`.
- Produces (Maxima entries; every one takes `&rest` args and checks its arity):
  - `%mr_defrule(key, n, "<pattern>", cond, repl)` → integer handle; a pattern `prepare` rejects is a
    Maxima error naming `key rn`.
  - `%mr_dispatch_tree(f, x, table, depth)` → the first answering rule's repl value, or `false`
    (`table` a list of handles; `depth` informational). Outcomes per rule: no match / cond false,
    unknown or error / repl error (misfire) / repl `false` (decline) / repl holding a boolean while
    `%mr_boolcheck` (misfire) → next rule.
  - `%mr_rule_bindings(h, f, x)`, `%mr_rule_accept(h, f, x)` → `mm` list or `false`;
    `%mr_rule_apply(h, f, x)` → answer or `false`.
  - `%mr_matchQ(u, "<pattern>", [<parts>], cond)` → `true`/`false`;
    `%mr_matchQ_bindings(…)` → binding list or `false`. `cond` is `true` or a function of the binding
    list; every complete binding is tried (MatchQ semantics, independent of `mr_cond_retry`).
  - Option variables `mr_flat_wide` (false), `mr_cond_retry` (true), `mr_model_flags` (true).
  - `%mr_binomialQ` / `%mr_intBinomialQ` arity dispatchers, unchanged.
  - Lisp: `(mr-rule-of handle)` → struct with `mr-rule-key`, `mr-rule-n`, `mr-rule-pattern`,
    `mr-rule-cond`, `mr-rule-repl` (probe 06 reads key and n).

- [ ] **Step 1: Write the failing unit suite**

Create `test/matcher/test_mr_dispatch.mac`:

```maxima
/* test/matcher/test_mr_dispatch.mac -- unit tests for the rule records, the
   dispatcher and the MatchQ entries (maxima_rubi_dispatch.lisp; matcher
   substrate spec sections 3.4-3.6). Synthetic rules only; loads the matcher,
   the converter, the utils and the dispatcher directly — no rule files, so
   no TLS flag (mr_top's mr_model_flags binding is pinned in Layer A).
   From the repo root:
     maxima --very-quiet -b test/matcher/test_mr_dispatch.mac
   Ends with a Results: line; a missing Results line is a failure. */
display2d : false$

tests_passed : 0$
tests_failed : 0$

check(test_name, actual, expected) := block([],
  if actual = expected then (
    tests_passed : tests_passed + 1,
    print("  PASS: ", test_name)
  ) else (
    tests_failed : tests_failed + 1,
    print("  FAIL: ", test_name),
    print("    expected: ", expected),
    print("    actual:   ", actual)
  ),
  true)$

check_bool(test_name, actual) := block([v],
  v : is(actual),
  if v = true then (
    tests_passed : tests_passed + 1,
    print("  PASS: ", test_name)
  ) else (
    tests_failed : tests_failed + 1,
    print("  FAIL: ", test_name),
    print("    actual:   ", actual)
  ),
  true)$

load("maxima_rubi_match.lisp")$
load("maxima_rubi_tree.lisp")$
load("maxima_rubi_utils.mac")$
load("maxima_rubi_dispatch.lisp")$

/* ---- synthetic conds and repls (the generated (mm, x) signature) ---- */
t_true(mm, x) := true$
t_false(mm, x) := false$
t_err(mm, x) := error("t_err: deliberate")$
t_unknown(mm, x) := tq > 0$
/* The fault guard catches any serious-condition a match signals. It is
   tested with a signalled storage-condition, not with runaway recursion:
   SBCL control-stack exhaustion is fatal ("Control stack exhausted while
   pseudo-atomic") when the guard page is hit inside an allocation, which
   a runaway Maxima recursion does (measured 2026-09-13, plan-2
   pre-validation) — the guard cannot make that case survivable. */
t_fault(mm, x) := ?error('?storage\-condition)$
t_42(mm, x) := 42$
t_7(mm, x) := 7$
t_m(mm, x) := geteqR(mm, '_t_m)$
t_u(mm, x) := geteqR(mm, '_t_u)$
t_leak(mm, x) := [1, true]$
t_half(mm, x) := is(geteqR(mm, '_t_p) = 1/2)$
t_p(mm, x) := geteqR(mm, '_t_p)$
t_inv(mm, x) := %mr_memberQ([asin, acos], geteqR(mm, '_t_F))$
t_app(mm, x) := apply(geteqR(mm, '_t_F), [2])$
t_flags(mm, x) := sconcat(radexpand, " ", logexpand)$

/* Int[x^m_., x] */
p_xm : "(Int (Power (Pattern x (Blank)) (Optional (Pattern |_t_m| (Blank)))) (Pattern x (Blank Symbol)))"$
/* Int[u_, x] */
p_u : "(Int (Pattern |_t_u| (Blank)) (Pattern x (Blank Symbol)))"$
/* Int[(a_.+b_.*x)^p_.*(c_.+d_.*x)^q_., x] -- two complete bindings on
   (1+2x)^3*(4+5x)^(1/2) */
p_two : "(Int (Times (Power (Plus (Optional (Pattern |_t_a| (Blank))) (Times (Optional (Pattern |_t_b| (Blank))) (Pattern x (Blank)))) (Optional (Pattern |_t_p| (Blank)))) (Power (Plus (Optional (Pattern |_t_c| (Blank))) (Times (Optional (Pattern |_t_d| (Blank))) (Pattern x (Blank)))) (Optional (Pattern |_t_q| (Blank))))) (Pattern x (Blank Symbol)))"$
/* Int[F_[x], x] */
p_head : "(Int ((Pattern |_t_F| (Blank)) (Pattern x (Blank))) (Pattern x (Blank Symbol)))"$

test_records() := block([h1, h2],
  print("--- rule records ---"),
  h1 : %mr_defrule("t", 1, p_xm, t_true, t_42),
  h2 : %mr_defrule("t", 2, p_xm, t_true, t_7),
  check_bool("%mr_defrule returns an integer handle", integerp(h1)),
  check("handles are consecutive", h2, h1 + 1),
  check("a pattern prepare rejects is a load error",
        errcatch(%mr_defrule("t", 3, "(Int (Alternatives (Pattern |_t_a| (Blank)) (Pattern |_t_b| (Blank))) (Pattern x (Blank Symbol)))", t_true, t_42)),
        []),
  check("a non-handle is an error", errcatch(%mr_rule_apply(10^9, x^3, x)), []),
  check("wrong arity is an error", errcatch(%mr_defrule("t", 4, p_xm, t_true)), []),
  true)$

test_dispatch() := block([h42, h7, hm, hdecl, hmis, hleak, hcf, hce, hcu, hfault],
  print("--- dispatcher: firing, order, outcomes ---"),
  h42 : %mr_defrule("t", 10, p_xm, t_true, t_42),
  h7 : %mr_defrule("t", 11, p_xm, t_true, t_7),
  hm : %mr_defrule("t", 12, p_xm, t_true, t_m),
  hdecl : %mr_defrule("t", 13, p_xm, t_true, t_false),
  hmis : %mr_defrule("t", 14, p_xm, t_true, t_err),
  hleak : %mr_defrule("t", 15, p_xm, t_true, t_leak),
  hcf : %mr_defrule("t", 16, p_xm, t_false, t_42),
  hce : %mr_defrule("t", 17, p_xm, t_err, t_42),
  hcu : %mr_defrule("t", 18, p_xm, t_unknown, t_42),
  hfault : %mr_defrule("t", 19, p_xm, t_fault, t_42),
  check("the firing rule's answer", %mr_dispatch_tree(x^3, x, [h42], 1), 42),
  check("first firing rule wins (order a)", %mr_dispatch_tree(x^3, x, [h42, h7], 1), 42),
  check("first firing rule wins (order b)", %mr_dispatch_tree(x^3, x, [h7, h42], 1), 7),
  check("no match -> false", %mr_dispatch_tree(sin(x), x, [h42], 1), false),
  check("empty table -> false", %mr_dispatch_tree(x^3, x, [], 1), false),
  check("binding reaches repl", %mr_dispatch_tree(x^3, x, [hm], 1), 3),
  check("Optional exponent default 1", %mr_dispatch_tree(x, x, [hm], 1), 1),
  check("x is pre-bound to the integration variable",
        %mr_dispatch_tree(y^3, x, [hm], 1), false),
  check("decline (repl false) -> next rule", %mr_dispatch_tree(x^3, x, [hdecl, h7], 1), 7),
  check("misfire (repl error) -> next rule", %mr_dispatch_tree(x^3, x, [hmis, h7], 1), 7),
  check("misfire (boolean leak) -> next rule", %mr_dispatch_tree(x^3, x, [hleak, h7], 1), 7),
  %mr_boolcheck : false,
  check("boolean leak passes with %mr_boolcheck false",
        %mr_dispatch_tree(x^3, x, [hleak, h7], 1), [1, true]),
  %mr_boolcheck : true,
  check("cond false -> next rule", %mr_dispatch_tree(x^3, x, [hcf, h7], 1), 7),
  check("cond error -> next rule", %mr_dispatch_tree(x^3, x, [hce, h7], 1), 7),
  check("cond unknown -> next rule", %mr_dispatch_tree(x^3, x, [hcu, h7], 1), 7),
  check("fault guard: a storage-condition signalled in cond -> next rule",
        %mr_dispatch_tree(x^3, x, [hfault, h7], 1), 7),
  check("the process survives the fault", %mr_dispatch_tree(x^3, x, [h42], 1), 42),
  true)$

/* Int[(g_.+h_.*x)*Sin[x], x] -- G-6: the narrow reading does not match
   h*x*sin(x); the wide reading binds g = 0, h = h */
p_wide : "(Int (Times (Plus (Optional (Pattern |_t_g| (Blank))) (Times (Optional (Pattern |_t_h| (Blank))) (Pattern x (Blank)))) (Sin (Pattern x (Blank)))) (Pattern x (Blank Symbol)))"$
t_h(mm, x) := geteqR(mm, '_t_h)$

test_bindings() := block([hu, hm, hr, hF, hw],
  print("--- dispatcher: bindings, retry, head symbols, CRE ---"),
  hu : %mr_defrule("t", 20, p_u, t_true, t_u),
  check("u_ binds a constant integrand", %mr_dispatch_tree(5, x, [hu], 1), 5),
  check("a binding holding a boolean is rejected", %mr_dispatch_tree(true, x, [hu], 1), false),
  hm : %mr_defrule("t", 21, p_xm, t_true, t_m),
  check("CRE integrand converts", %mr_dispatch_tree(rat(x^3), x, [hm], 1), 3),
  hr : %mr_defrule("t", 22, p_two, t_half, t_p),
  mr_cond_retry : true,
  check("mr_cond_retry true: the cond reaches the second binding",
        %mr_dispatch_tree((1+2*x)^3*sqrt(4+5*x), x, [hr], 1), 1/2),
  mr_cond_retry : false,
  check("mr_cond_retry false: the first complete binding is final",
        %mr_dispatch_tree((1+2*x)^3*sqrt(4+5*x), x, [hr], 1), false),
  mr_cond_retry : true,
  hF : %mr_defrule("t", 23, p_head, t_inv, t_app),
  check("a head capture binds the symbol the cond's list holds",
        %mr_dispatch_tree(asin(x), x, [hF], 1), asin(2)),
  check("a head outside the cond's list declines",
        %mr_dispatch_tree(sin(x), x, [hF], 1), false),
  hw : %mr_defrule("t", 24, p_wide, t_true, t_h),
  mr_flat_wide : false,
  check("mr_flat_wide false: an Optional-reduced Plus takes no run (G-6 narrow)",
        %mr_dispatch_tree(h*x*sin(x), x, [hw], 1), false),
  mr_flat_wide : true,
  check("mr_flat_wide true: an Optional-reduced Plus takes a run (G-6 wide)",
        %mr_dispatch_tree(h*x*sin(x), x, [hw], 1), h),
  mr_flat_wide : false,
  true)$

test_entries() := block([hm, hcf],
  print("--- test entries: bindings / accept / apply ---"),
  hm : %mr_defrule("t", 30, p_xm, t_true, t_m),
  hcf : %mr_defrule("t", 31, p_xm, t_false, t_42),
  check("%mr_rule_bindings ignores the cond", %mr_rule_bindings(hcf, x^3, x), [_t_m = 3]),
  check("%mr_rule_accept honours the cond (false)", %mr_rule_accept(hcf, x^3, x), false),
  check("%mr_rule_accept returns the accepted binding", %mr_rule_accept(hm, x^3, x), [_t_m = 3]),
  check("%mr_rule_apply answers", %mr_rule_apply(hm, x^3, x), 3),
  check("%mr_rule_apply on a cond-false rule", %mr_rule_apply(hcf, x^3, x), false),
  check("%mr_rule_bindings on no match", %mr_rule_bindings(hm, sin(x), x), false),
  true)$

t_fault1(b) := ?error('?storage\-condition)$

test_matchq() := block([B],
  print("--- MatchQ entries ---"),
  check_bool("MatchQ 5*x^2 vs u_.*x^m_. /; IntegerQ[m]",
             %mr_matchQ(5*x^2, "(Times (Optional (Pattern |_t_mq1_u| (Blank))) (Power (MRArg 1) (Optional (Pattern |_t_mq1_m| (Blank)))))",
                        [x], lambda([%mr_mqb], integerp(%mr_mk(_t_mq1_m, %mr_mqb))))),
  B : %mr_matchQ_bindings(5*x^2, "(Times (Optional (Pattern |_t_mq1_u| (Blank))) (Power (MRArg 1) (Optional (Pattern |_t_mq1_m| (Blank)))))",
                          [x], true),
  check_bool("MatchQ bindings u = 5, m = 2",
             listp(B) and is(geteqR(B, '_t_mq1_u) = 5) and is(geteqR(B, '_t_mq1_m) = 2)),
  check("MatchQ x^y vs x^m_ /; IntegerQ[m] is false",
        %mr_matchQ(x^y, "(Power (MRArg 1) (Pattern |_t_mq2_m| (Blank)))",
                   [x], lambda([%mr_mqb], integerp(%mr_mk(_t_mq2_m, %mr_mqb)))),
        false),
  check_bool("MatchQ a Times part splices into Plus (f_+g_.*x^2)^r_.",
             %mr_matchQ(3 + 5*x^2, "(Power (Plus (Pattern |_t_mq3_f| (Blank)) (Times (Optional (Pattern |_t_mq3_g| (Blank))) (MRArg 1))) (Optional (Pattern |_t_mq3_r| (Blank))))",
                        [x^2], true)),
  /* Plus is Flat: f_ alone can take the run 3 + 7*x^4, so only the
     FreeQ cond rejects the trinomial */
  check("MatchQ trinomial vs (f_+g_.*x^2)^r_. /; FreeQ[f, x] is false",
        %mr_matchQ(3 + 5*x^2 + 7*x^4, "(Power (Plus (Pattern |_t_mq3_f| (Blank)) (Times (Optional (Pattern |_t_mq3_g| (Blank))) (MRArg 1))) (Optional (Pattern |_t_mq3_r| (Blank))))",
                   [x^2], lambda([%mr_mqb], freeof(x, %mr_mk(_t_mq3_f, %mr_mqb)))),
        false),
  mr_cond_retry : false,
  check_bool("MatchQ tries every binding whatever mr_cond_retry says",
             %mr_matchQ((1+2*x)^3*sqrt(4+5*x),
                        "(Times (Power (Plus (Optional (Pattern |_t_mq4_a| (Blank))) (Times (Optional (Pattern |_t_mq4_b| (Blank))) (MRArg 1))) (Optional (Pattern |_t_mq4_p| (Blank)))) (Power (Plus (Optional (Pattern |_t_mq4_c| (Blank))) (Times (Optional (Pattern |_t_mq4_d| (Blank))) (MRArg 1))) (Optional (Pattern |_t_mq4_q| (Blank)))))",
                        [x], lambda([%mr_mqb], is(%mr_mk(_t_mq4_p, %mr_mqb) = 1/2)))),
  mr_cond_retry : true,
  check("MatchQ fault guard: a storage-condition signalled in cond -> false",
        %mr_matchQ(x, "(Pattern |_t_mq5_u| (Blank))", [], t_fault1), false),
  check("MatchQ wrong arity is an error",
        errcatch(%mr_matchQ(x, "(Pattern |_t_mq5_u| (Blank))", [], true, 5)), []),
  true)$

test_records()$
test_dispatch()$
test_bindings()$
test_entries()$
test_matchq()$
print("")$
print("========================================")$
print("Results: ", tests_passed, " passed, ", tests_failed, " failed")$
print("========================================")$
```

- [ ] **Step 2: Run it against the P0 dispatcher**

Run: `maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null > /tmp/p2t4-red.out 2>&1; grep -a -c '^ *FAIL' /tmp/p2t4-red.out; grep -a -c '^Results' /tmp/p2t4-red.out`
Expected: `37` and `0` — every record check fails (`%mr_defrule returns an integer handle`, actual
`false`) and the run dies before its Results line.

- [ ] **Step 3: Write the dispatcher**

Replace the whole of `maxima_rubi_dispatch.lisp` with:

```lisp
;; maxima_rubi_dispatch.lisp — the rule records, the dispatcher and the
;; MatchQ entries on MR-MATCH / MR-TREE (matcher substrate spec
;; docs/superpowers/specs/2026-09-12-matcher-substrate-design.md sections
;; 3.4-3.6), and the arity dispatchers for the two Rubi predicates the
;; rules call at more than one arity.
;;
;; Loaded by maxima_rubi.mac after maxima_rubi_utils.mac (geteqR,
;; %mr_containsBoolean, rubi_verbose, %mr_boolcheck),
;; maxima_rubi_match.lisp and maxima_rubi_tree.lisp.
;;
;; Naming (measured 2026-08-27, this build): the Lisp symbol of an
;; ALL-LOWERCASE Maxima name is upper-cased — a defmfun for %mr_defrule
;; must be |$%MR_DEFRULE| — while a name containing an uppercase letter
;; keeps its typed case (|$%mr_matchQ|). A fixed-parameter defmfun does not
;; become a callable Maxima function in this build, so every entry takes
;; (&rest args) and checks its arity.

;; Arity dispatchers for the two Rubi predicates the generated class-1
;; rules call at more than one arity: %mr_binomialQ (2 and 3 args) and
;; %mr_intBinomialQ (7, 8 and 10 args — the three DISTINCT Rubi
;; definitions, 1.1.3.2:118 / 1.1.3.3:73 / 1.1.3.4:89). Maxima has no
;; function overloading and a wrong-arity call to a := function is a
;; hard error (measured, task-7a); each defmfun below catches the args
;; and re-dispatches to the fixed-arity Maxima := body in
;; maxima_rubi_utils.mac (named <name><arity>) via the
;; (mlambda (mget sym 'mexpr) args sym t nil) call primitive (the same
;; primitive mfunction-call-aux uses to invoke a := function,
;; fcall.lisp:89-94).
;;
;; The class-1 arity census (2026-08-23, over rules/class1): binomialQ
;; 2/3 (40/1), intBinomialQ 7/8/10 (21/10/44) — the only two
;; multi-arity names. %mr_integersQ / %mr_fractionQ / %mr_rationalQ
;; are 1-arg only (scalar-or-list in that one arg) and take their calls
;; directly as committed := ports; intLinearQ (7) and intQuadraticQ (8)
;; are fixed-arity.

(defmfun |$%mr_binomialQ| (&rest args)
  (let ((f (case (length args)
             (2 '|$%mr_binomialQ2|)
             (3 '|$%mr_binomialQ3|)
             (t nil))))
    (if f (mlambda (mget f 'mexpr) args f t nil)
        (merror (intl:gettext "%mr_binomialQ: bad arity ~A") (length args)))))

(defmfun |$%mr_intBinomialQ| (&rest args)
  (let ((f (case (length args)
             (7  '|$%mr_intBinomialQ7|)
             (8  '|$%mr_intBinomialQ8|)
             (10 '|$%mr_intBinomialQ10|)
             (t nil))))
    (if f (mlambda (mget f 'mexpr) args f t nil)
        (merror (intl:gettext "%mr_intBinomialQ: bad arity ~A") (length args)))))

;;; ------------------------------------------------------------------
;;; Migration switches (spec 3.6). Maxima option variables; the dispatcher
;;; and MatchQ read the first two, mr_top the third.

(defmvar $mr_flat_wide nil
  "Matcher substrate switch: true = the wide G-6 run-grouping of an
Optional-reduced Plus/Times item; false (default) = the narrow reading.")

(defmvar $mr_cond_retry t
  "Matcher substrate switch: true (default) = a rule's cond runs on every
complete binding until one is accepted; false = on the first complete
binding only.")

(defmvar $mr_model_flags t
  "Matcher substrate switch: true (default) = mr_top binds radexpand:false
and logexpand:false around the dispatch (the G-5 arm); false = Maxima
defaults.")

;; Maxima variables the utils define before this file loads (declared here
;; so their references compile as special).
(defvar $rubi_verbose nil)
(defvar $%mr_boolcheck t)

(defun mr-verbose (fmt &rest args)
  (when $rubi_verbose
    (apply #'mtell fmt args)))

;;; ------------------------------------------------------------------
;;; Rule records (spec 3.4): %mr_defrule(key, n, pattern, cond, repl)
;;; prepares the pattern once, at load, and returns the rule's handle (its
;;; 1-based index in *mr-rules*); mr_rules_<key> and mr_rule_table are
;;; Maxima lists of handles.

(defstruct (mr-rule (:constructor make-mr-rule (key n pattern cond repl)))
  key n pattern cond repl)

(defvar *mr-rules* (make-array 4096 :adjustable t :fill-pointer 0)
  "Every rule record %mr_defrule registered, in load order.")

(defmfun |$%MR_DEFRULE| (&rest args)
  (unless (= (length args) 5)
    (merror (intl:gettext "%mr_defrule: expected 5 args, found ~A") (length args)))
  (destructuring-bind (key n pattern cond repl) args
    (let ((compiled (handler-case (mr-match:prepare (mr-match:read-tree pattern))
                      (error (e)
                        (merror (intl:gettext "%mr_defrule: ~A r~A: ~A") key n
                                (princ-to-string e))))))
      (vector-push-extend (make-mr-rule key n compiled cond repl) *mr-rules*)
      (fill-pointer *mr-rules*))))

(defun mr-rule-of (handle)
  (if (and (integerp handle) (<= 1 handle (fill-pointer *mr-rules*)))
      (aref *mr-rules* (1- handle))
      (merror (intl:gettext "rubi: not a rule handle: ~M") handle)))

;;; ------------------------------------------------------------------
;;; Bindings -> Maxima

(defvar *mr-head-verbs* nil
  "Tree head symbol -> the Maxima operator symbol of the MR-TREE head table
(built on first use; the smallest arity wins).")

;; The table's operator is the symbol Maxima itself reads for the typed name:
;; `asin` reads as the noun %ASIN (the parser's alias), so the cond's literal
;; list [asin, acos, ...] holds %ASIN — a $verbify'd $ASIN is not member of it
;; (measured 2026-09-13, plan-2 pre-validation, probe_f12.mac).
(defun mr-head-verb (sym)
  (unless *mr-head-verbs*
    (let ((table (make-hash-table :test 'eq)))
      (dolist (row (sort (copy-list (mr-tree:head-table)) #'> :key #'second))
        (setf (gethash (first row) table) (third row)))
      (setf *mr-head-verbs* table)))
  (gethash sym *mr-head-verbs*))

(defun mr-binding-value (tree)
  "A bound tree -> its Maxima value. A function head bound to a pattern
variable (F_[...], 3_1_5 r58/r59, 3_3 r58, 3_4 r37) becomes the Maxima
operator symbol the typed name reads as (ArcSinh -> %asinh), which the cond
compares with %mr_memberQ and the repl applies; anything else goes through
tree->max."
  (or (and (symbolp tree) (mr-head-verb tree))
      (mr-tree:tree->max tree)))

(defun mr-binding-list (bindings skip)
  "MR-MATCH bindings -> the Maxima list [name = value, ...] in pattern order,
without the pre-bound name SKIP."
  (cons '(mlist simp)
        (loop for (name . value) in (reverse bindings)
              unless (eq name skip)
                collect (list '(mequal simp) (mr-tree:tree->max name)
                              (mr-binding-value value)))))

;;; ------------------------------------------------------------------
;;; Calling Maxima under errcatch

(defun mr-call (fn &rest args)
  "Call the Maxima function (or lambda) FN on ARGS under errcatch:
(values result t), or (values nil nil) when the call signals an error."
  (let ((r (errcatch (apply #'mfuncall fn args))))
    (if r (values (car r) t) (values nil nil))))

(defun mr-true-p (v)
  "is(v) = true (unknown and false are not true)."
  (eq (meval `(($is) ((mquote) ,v))) t))

(defun mr-contains-boolean-p (e)
  "%mr_containsBoolean(e); an error counts as containing one."
  (multiple-value-bind (r ok) (mr-call '|$%mr_containsBoolean| e)
    (or (not ok) (eq r t))))

(defmacro mr-guarded (fault-form &body body)
  "Run BODY; a signalled fault inside it (any serious-condition — a Lisp
error that escaped errcatch, a storage-condition) unwinds Maxima's dynamic
bindings as errcatch does and yields FAULT-FORM (spec 3.5 step 5). Not
covered: SBCL control-stack exhaustion hit inside an allocation is fatal
before any condition is signalled — a runaway Maxima recursion in a cond
killed the process in 5 of 6 measured shapes (probes/matcher/07)."
  (let ((saved (gensym "SAVED")) (c (gensym "C")))
    `(let ((,saved (cons bindlist loclist)))
       (handler-case (progn ,@body)
         (serious-condition (,c)
           (errlfun1 ,saved)
           (let ((condition ,c))
             (declare (ignorable condition))
             ,fault-form))))))

;;; ------------------------------------------------------------------
;;; The dispatcher (spec 3.5)

(defun mr-accept (rule expr pre x check-cond)
  "Match RULE's pattern against EXPR (x pre-bound). The condition hook
converts each complete binding into the mm list, rejects one holding a
boolean and — when CHECK-COND — runs the rule's cond under errcatch:
is(cond) = true accepts; false, unknown or an error goes on to the next
binding (mr_cond_retry). Returns the accepted mm list, or nil."
  (let ((accepted nil)
        (xname (car (first pre))))
    (mr-guarded
        (progn (mr-verbose "rubi: rule ~A r~A matcher fault: ~A~%"
                           (mr-rule-key rule) (mr-rule-n rule) (princ-to-string condition))
               (setf accepted nil))
      (mr-match:match
       (mr-rule-pattern rule) expr :bindings pre
       :cond-hook (lambda (b)
                    (let ((r (errcatch
                              (let ((mm (mr-binding-list b xname)))
                                (and (not (mr-contains-boolean-p mm))
                                     (or (not check-cond)
                                         (multiple-value-bind (v ok) (mr-call (mr-rule-cond rule) mm x)
                                           (and ok (mr-true-p v))))
                                     mm)))))
                      (when (car r)
                        (setf accepted (car r))
                        t)))))
    accepted))

(defun mr-integrand (f x)
  "-> (values expr pre) for matching Int[f, x], or nil when f does not
convert."
  (let ((xtree (mr-tree:max->tree x)))
    (mr-guarded (progn (mr-verbose "rubi: integrand does not convert: ~M~%" f) nil)
      (values (list (mr-match:sym "Int") (mr-tree:max->tree f) xtree)
              (list (cons (mr-match:sym "x") xtree))))))

(defun mr-apply-rule (rule expr pre f x)
  "Try one rule on the converted integrand: the answer, or nil (no match,
decline or misfire)."
  (let ((mm (mr-accept rule expr pre x t))
        (key (mr-rule-key rule))
        (n (mr-rule-n rule)))
    (when mm
      (multiple-value-bind (r ok) (mr-call (mr-rule-repl rule) mm x)
        (cond ((not ok)
               (mr-verbose "rubi: rule ~A r~A misfire (repl error) on ~M~%" key n f) nil)
              ((null r)
               (mr-verbose "rubi: rule ~A r~A declined on ~M~%" key n f) nil)
              ((and $%mr_boolcheck (mr-contains-boolean-p r))
               (mr-verbose "rubi: rule ~A r~A misfire (boolean leaked) on ~M~%" key n f) nil)
              (t
               (mr-verbose "rubi: rule ~A r~A fired on ~M with ~M~%" key n f mm) r))))))

(defmacro with-mr-switches (&body body)
  `(let ((mr-match:*flat-wide* (not (null $mr_flat_wide)))
         (mr-match:*cond-retry* (not (null $mr_cond_retry))))
     ,@body))

(defmfun |$%MR_DISPATCH_TREE| (&rest args)
  "%mr_dispatch_tree(f, x, table, depth): walk the rule handles of TABLE in
order; the first rule whose pattern binds, whose cond accepts and whose repl
answers wins. false when no rule answers."
  (unless (= (length args) 4)
    (merror (intl:gettext "%mr_dispatch_tree: expected 4 args, found ~A") (length args)))
  ;; (the fourth argument, the recursion depth, is informational: DEPTH is
  ;; a Maxima special variable, so it is not bound here)
  (destructuring-bind (f x table &rest ignored) args
    (declare (ignore ignored))
    (unless ($listp table)
      (merror (intl:gettext "%mr_dispatch_tree: the table is not a list: ~M") table))
    (multiple-value-bind (expr pre) (mr-integrand f x)
      (when expr
        (with-mr-switches
          (dolist (h (cdr table) nil)
            (let ((r (mr-apply-rule (mr-rule-of h) expr pre f x)))
              (when r (return r)))))))))

(defmfun |$%MR_RULE_BINDINGS| (&rest args)
  "%mr_rule_bindings(handle, f, x): the mm list of the rule's first complete
binding of Int[f, x] (no cond), or false — a test and debugging entry."
  (unless (= (length args) 3)
    (merror (intl:gettext "%mr_rule_bindings: expected 3 args, found ~A") (length args)))
  (destructuring-bind (h f x) args
    (multiple-value-bind (expr pre) (mr-integrand f x)
      (and expr (with-mr-switches (mr-accept (mr-rule-of h) expr pre x nil))))))

(defmfun |$%MR_RULE_ACCEPT| (&rest args)
  "%mr_rule_accept(handle, f, x): the mm list of the rule's first complete
binding of Int[f, x] that its cond accepts (under mr_cond_retry, as the
dispatcher runs it), or false — a test and debugging entry."
  (unless (= (length args) 3)
    (merror (intl:gettext "%mr_rule_accept: expected 3 args, found ~A") (length args)))
  (destructuring-bind (h f x) args
    (multiple-value-bind (expr pre) (mr-integrand f x)
      (and expr (with-mr-switches (mr-accept (mr-rule-of h) expr pre x t))))))

(defmfun |$%MR_RULE_APPLY| (&rest args)
  "%mr_rule_apply(handle, f, x): the one rule's answer on Int[f, x] (pattern,
cond, repl, as the dispatcher runs it), or false."
  (unless (= (length args) 3)
    (merror (intl:gettext "%mr_rule_apply: expected 3 args, found ~A") (length args)))
  (destructuring-bind (h f x) args
    (multiple-value-bind (expr pre) (mr-integrand f x)
      (and expr (with-mr-switches (mr-apply-rule (mr-rule-of h) expr pre f x))))))

;;; ------------------------------------------------------------------
;;; MatchQ (spec 3.4): %mr_matchQ(u, "<pattern>", [<parts>], cond)

(defvar *mr-matchq-trees* (make-hash-table :test 'equal)
  "%mr_matchQ pattern text -> its tree, read once.")

(defun mr-substitute-parts (tree parts)
  "Replace each (MRArg k) in TREE with the k-th of PARTS (trees); a
substituted Plus/Times directly under the same head is spliced in, as
Mathematica's evaluation of the pattern would flatten it."
  (let ((mrarg (mr-match:sym "MRArg"))
        (flat (list (mr-match:sym "Plus") (mr-match:sym "Times"))))
    (labels ((walk (e)
               (cond ((atom e) e)
                     ((eq (car e) mrarg) (nth (1- (second e)) parts))
                     (t (let ((h (walk (car e)))
                              (args (mapcar #'walk (cdr e))))
                          (cons h (if (member h flat)
                                      (loop for a in args
                                            if (and (consp a) (eq (car a) h))
                                              append (cdr a)
                                            else collect a)
                                      args)))))))
      (walk tree))))

(defun mr-matchq (u text parts cond)
  "The Maxima binding list [marker = value, ...] of the first complete binding
of the pattern TEXT (its (MRArg k) placeholders replaced by the values PARTS)
against U that COND accepts, or nil. COND is true or a function of the
binding list. MatchQ semantics: every complete binding is tried
(mr_cond_retry does not apply)."
  (let ((accepted nil)
        (raw (or (gethash text *mr-matchq-trees*)
                 (setf (gethash text *mr-matchq-trees*) (mr-match:read-tree text)))))
    (mr-guarded (setf accepted nil)
      (let ((mr-match:*flat-wide* (not (null $mr_flat_wide)))
            (mr-match:*cond-retry* t)
            (compiled (mr-match:prepare
                       (if (cdr parts)
                           (mr-substitute-parts raw (mapcar #'mr-tree:max->tree (cdr parts)))
                           raw))))
        (mr-match:match
         compiled (mr-tree:max->tree u)
         :cond-hook (lambda (b)
                      (let ((r (errcatch
                                (let ((mb (mr-binding-list b nil)))
                                  (and (or (eq cond t)
                                           (multiple-value-bind (v ok) (mr-call cond mb)
                                             (and ok (mr-true-p v))))
                                       mb)))))
                        (when (car r)
                          (setf accepted (car r))
                          t))))))
    accepted))

(defun mr-matchq-args (name args)
  (unless (= (length args) 4)
    (merror (intl:gettext "~A: expected 4 args, found ~A") name (length args)))
  (unless (and (stringp (second args)) ($listp (third args)))
    (merror (intl:gettext "~A: expected (u, \"<pattern>\", [<parts>], cond)") name))
  args)

(defmfun |$%mr_matchQ| (&rest args)
  "%mr_matchQ(u, \"<pattern>\", [<parts>], cond): true iff some binding of the
pattern against u satisfies cond (true or lambda([%mr_mqb], ...))."
  (if (apply #'mr-matchq (mr-matchq-args "%mr_matchQ" args)) t nil))

(defmfun |$%mr_matchQ_bindings| (&rest args)
  "%mr_matchQ_bindings(u, \"<pattern>\", [<parts>], cond): the accepted
binding list [marker = value, ...], or false."
  (apply #'mr-matchq (mr-matchq-args "%mr_matchQ_bindings" args)))
```

- [ ] **Step 4: Run the suite**

Run: `maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null | grep -a 'FAIL\|^Results'`
Expected: `Results: 45 passed, 0 failed` (records 5, dispatcher outcomes 17, bindings / retry / head
symbols / CRE / G-6 9, entries 6, MatchQ 8).

- [ ] **Step 5: Commit**

```bash
git add maxima_rubi_dispatch.lisp test/matcher/test_mr_dispatch.mac
git commit -m "dispatch: %mr_defrule records, %mr_dispatch_tree and MatchQ on MR-MATCH; unit suite 45/0"
```

---

### Task 5: Runtime wiring — loader, utils, deletions, core lists (P4)

Branch: `matcher-substrate`.

**Files:**
- Modify: `maxima_rubi_utils.mac` (7,392 → 5,007 lines: `utils/edit_utils.py`, then `utils/maxima_rubi_utils.handedits.patch`)
- Modify: `maxima_rubi.mac` (`loader/maxima_rubi.mac.patch`)
- Delete: `maxima_rubi_implicit1.lisp`, `maxima_rubi_pass4.lisp`
- Modify: `test/build_rules_core.sh` (fingerprint list, two comments), `test/corpus_driver.py` (`_core_fingerprint`)

**Interfaces:**
- Consumes: Task 4's entries; Task 2's rule files; utils' `%mr_mk`, `geteqR`, `%mr_seenp`, `mr_unintegrable`.
- Produces:
  - `load("maxima_rubi.mac")` loads the utils, `maxima_rubi_match.lisp` (witness `mr_witness_match`),
    `maxima_rubi_tree.lisp` (`mr_witness_tree`), `maxima_rubi_dispatch.lisp` (`mr_witness_dispatch`,
    which calls `%mr_dispatch_tree(1, x, [], 1)`) and the 1.1.1.1 core; `mr_load_all()` sets
    `mr_rule_table` to the 3,513 handles in LoadRules order.
  - `mr_top(f, x, fb)` (hence `rubi`, `rubi_fallback`, `mr_int`) and `%mr_hybrid_body` dispatch once
    through `%mr_dispatch_tree(f, x, mr_rule_table, depth_level)`, inside
    `block([radexpand : false, logexpand : false], …)` while `mr_model_flags` is true.
  - The utility predicates whose `.m` definitions match patterns (TrinomialQ, LinearMatchQ,
    QuadraticMatchQ, BinomialMatchQ, TrinomialMatchQ, GeneralizedBinomialParts / MatchQ,
    GeneralizedTrinomialParts / MatchQ) call the 4-arg `%mr_matchQ` / `%mr_matchQ_bindings`.
  - `%mr_algebraicFunctionQ(u, x)` and `%mr_algebraicFunctionQ(u, x, flag)`.
  - Deleted (spec §7, P4 rows): `%mr_dispatch`; `%mr_barefactors`, `%mr_p4_once`, `%mr_pass4_scan`;
    passes 2–3 in `mr_top`; the `%mr_mq_*` matcher (`%mr_mk` stays); `%mr_mbp_*`, `%mr_lpfac*`,
    `%mr_bpf_*`, `%mr_binpowfactors`; `%mr_hv_*` / `%mr_headvar_match`; `%mr_logpow_*`;
    `%mr_logratio_*`; the Lisp `%mr_dispatch_rev`, `%mr_declaim_matchvars`, `%mr_dispatch_i1`,
    `%mr_dispatch_p4` and their files. `rubi_hybrid` / `rubi_hybrid_exact` stay until P6 (spec §3.5).

- [ ] **Step 1: No remaining caller outside the utils**

Run:

```bash
FAM='%mr_mbp_\|%mr_binpowfactors\|%mr_lpfac\|%mr_bpf_\|%mr_headvar_match\|%mr_hv_\|%mr_logpow_\|%mr_logratio\|%mr_mq_\|%mr_dispatch(\|%mr_dispatch_rev\|%mr_declaim_matchvars\|%mr_barefactors\|%mr_p4_once\|%mr_pass4_scan\|%mr_dispatch_i1\|%mr_dispatch_p4'
grep -rn "$FAM" rules/ generator/ maxima_rubi_dispatch.lisp | wc -l
```

Expected: `0` (spec §7: a family is deleted only after a grep shows nothing still calls it).

- [ ] **Step 2: The utils deletions and the MatchQ sites**

Run: `python3 docs/superpowers/plans/2026-09-13-matcher-substrate-plan2.files/utils/edit_utils.py maxima_rubi_utils.mac`
Expected: `utils: 7392 -> 5017 lines`.

`edit_utils.py` asserts eleven anchor lines of the P0 file, then rebuilds it from exact line
ranges: it drops the `%mr_dispatch` description and definition, the pass-4 helpers, the
`%mr_mq_*` MatchQ matcher (keeping `%mr_mk`), `%mr_mbp_*` / `%mr_lpfac*` / `%mr_binpowfactors`,
and `%mr_headvar_match` / `%mr_logpow_*` / `%mr_logratio_*`; replaces `mr_top`'s dispatch and
pass-2–3 tail, and `%mr_hybrid_body`'s dispatch, with the single `%mr_dispatch_tree` call under
`mr_model_flags`; and rewrites the sixteen utility MatchQ sites as 4-arg pattern strings (made
with the generator's `_emit_matchq`), with the capture wrapper replaced by
`%mr_matchQ_bindings` and a new section header for the Generalized* predicates.

- [ ] **Step 3: The `%mr_algebraicFunctionQ` flag and the stale comments**

Run: `git apply docs/superpowers/plans/2026-09-13-matcher-substrate-plan2.files/utils/maxima_rubi_utils.handedits.patch && wc -l < maxima_rubi_utils.mac && grep -c "$FAM" maxima_rubi_utils.mac`
Expected: `5007` and `0`.

The patch ports `AlgebraicFunctionQ[u_, x_Symbol, flag_:False]` (IntegrationUtilityFunctions.m:1681)
as `%mr_algebraicFunctionQ(u, x, [flag])` — a flag of `true` also admits a power with an x-free
exponent, and the flag is passed down every recursive call — and rewrites six comments that
still described the deleted `%mr_dispatch`, the `%mr_mq_*` matcher or the pass gates (the
`rubi_hybrid` comment now says no rule file calls it).

- [ ] **Step 4: The loader**

Run: `git apply docs/superpowers/plans/2026-09-13-matcher-substrate-plan2.files/loader/maxima_rubi.mac.patch`

The patch removes the two `%mr_declaim_matchvars` calls from `%mr_load_sibling`; loads
`maxima_rubi_match.lisp` and `maxima_rubi_tree.lisp` with `?find_package` witnesses before the
dispatcher; changes the dispatcher witness to `%mr_dispatch_tree(1, x, [], 1) = false`; removes
the implicit-1 and pass-4 loads and witnesses; and rewrites the load-wall comments (class 1 =
3,054 rules, total 3,513, the TLS rule pending Task 7's measurement).

- [ ] **Step 5: Delete the pass files**

```bash
git rm maxima_rubi_implicit1.lisp maxima_rubi_pass4.lisp
grep -n "$FAM\|implicit1\|pass4" maxima_rubi.mac | wc -l
```

Expected: `0`.

- [ ] **Step 6: The core fingerprint lists**

In `test/build_rules_core.sh` replace

```sh
# NOTE: the file list below (loader + utils + dispatch lisp + implicit-1
# lisp + pass-4 lisp + every class-1, class-2 AND class-3 rule file)
# must stay in sync with the driver's _core_fingerprint()
# (test/corpus_class1_driver.py).
```

with

```sh
# NOTE: the file list below (loader + utils + dispatch lisp + matcher lisp
# + converter lisp + every class-1, class-2 AND class-3 rule file)
# must stay in sync with the driver's _core_fingerprint()
# (test/corpus_driver.py).
```

replace

```sh
# Fingerprint over exactly the files the image is built from: the loader,
# the utils, the dispatch lisp, the implicit-1 lisp, the pass-4 lisp, and
# every generated class-1, class-2 AND class-3 rule file. The file list
# is sorted (C locale) so the byte order matches the driver's
# _core_fingerprint() (test/corpus_class1_driver.py) exactly — a
```

with

```sh
# Fingerprint over exactly the files the image is built from: the loader,
# the utils, the dispatch lisp, the matcher lisp, the converter lisp, and
# every generated class-1, class-2 AND class-3 rule file. The file list
# is sorted (C locale) so the byte order matches the driver's
# _core_fingerprint() (test/corpus_driver.py) exactly — a
```

and replace

```sh
FP=$( { printf '%s\n' maxima_rubi.mac maxima_rubi_utils.mac maxima_rubi_dispatch.lisp \
        maxima_rubi_implicit1.lisp maxima_rubi_pass4.lisp
```

with

```sh
FP=$( { printf '%s\n' maxima_rubi.mac maxima_rubi_utils.mac maxima_rubi_dispatch.lisp \
        maxima_rubi_match.lisp maxima_rubi_tree.lisp
```

In `test/corpus_driver.py`, `_core_fingerprint`, replace

```python
    image (loader + utils + dispatch lisp + implicit-1 lisp + pass-4
    lisp + every class-1, class-2 AND class-3 rule file)."""
```

with

```python
    image (loader + utils + dispatch lisp + matcher lisp + converter
    lisp + every class-1, class-2 AND class-3 rule file)."""
```

and replace

```python
                   "maxima_rubi_implicit1.lisp",
                   "maxima_rubi_pass4.lisp"] +
```

with

```python
                   "maxima_rubi_match.lisp",
                   "maxima_rubi_tree.lisp"] +
```

- [ ] **Step 7: Smoke — the package loads, the table is complete, a rule answers**

Create `/tmp/p2t5-smoke.mac`:

```maxima
display2d : false$
load("maxima_rubi.mac")$
mr_load_all()$
print("SMOKE rules", length(mr_rule_table))$
print("SMOKE answer", rubi(x^3*(a+b*x^2)^(5/2), x))$
```

Run: `maxima --very-quiet -X "--tls-limit 100000" -b /tmp/p2t5-smoke.mac < /dev/null | grep -a '^SMOKE'`
Expected:

```
SMOKE rules 3513
SMOKE answer (14*b*x^2*(b*x^2+a)^(7/2)-4*a*(b*x^2+a)^(7/2))/(126*b^2)
```

- [ ] **Step 8: The suites and the static gate, and the rules core builds**

Run: `maxima --very-quiet -b test/matcher/test_mr_match.mac | grep -a '^Results'`,
`maxima --very-quiet -b test/matcher/test_mr_tree.mac | grep -a '^Results'`,
`maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null | grep -a '^Results'` (now on the new utils),
`python3 test/check_generated_rules.py | tail -1` and `sh test/build_rules_core.sh | tail -1`
Expected: `53 passed, 0 failed`; `51 passed, 0 failed`; `45 passed, 0 failed`;
`Results: 11 passed, 0 failed`; `built test/mr_rules.core (<n> bytes) rules=3513 fingerprint=<md5>`.
Layer A is Task 6 (it still dies in `test_dispatch` here).

- [ ] **Step 9: Commit**

```bash
git add maxima_rubi_utils.mac maxima_rubi.mac test/build_rules_core.sh test/corpus_driver.py
git commit -m "runtime: loader, mr_top and utils on %mr_dispatch_tree; defmatch-era passes and matchers deleted"
```

---

### Task 6: Layer A — the matcher-coupled sections rewritten (P4)

Branch: `matcher-substrate`.

**Files:**
- Modify: `test_maxima_rubi.mac` (via `docs/superpowers/plans/2026-09-13-matcher-substrate-plan2.files/layerA/layerA_rewrite.py`)

**Interfaces:**
- Consumes: Task 5's package — `%mr_defrule`, `%mr_dispatch_tree`, `%mr_rule_bindings`,
  `%mr_rule_accept`, `%mr_rule_apply`, `%mr_matchQ`, `%mr_matchQ_bindings`, `mr_model_flags`,
  `rubi`, the generated `_mr_rule_<key>_r<n>` handles and `_mr_cond_<key>_r<n>` functions, the
  capture names `_mr_<key>_r<n>_<v>`.
- Produces: the Layer A count 897 (Task 7 records it in AGENTS.md); the Layer A helper
  `binds(mm, [name = value, …])` — true iff `mm` is a list and `geteqR` finds every name bound to its
  value.

- [ ] **Step 1: Run Layer A as it stands**

Run: `maxima --very-quiet -X "--tls-limit 100000" -b test_maxima_rubi.mac < /dev/null > /tmp/p2t6-red.out 2>&1; grep -a -c '^ *PASS' /tmp/p2t6-red.out; grep -a -c '^ *FAIL' /tmp/p2t6-red.out; grep -a -c '^Results' /tmp/p2t6-red.out`
Expected: `9`, `3`, `0` — the run dies in `test_dispatch`, whose lambda-table end-to-end check
calls `rubi` on a table the new dispatcher rejects (`%mr_dispatch` is gone).

- [ ] **Step 2: Apply the rewrite**

Run: `python3 docs/superpowers/plans/2026-09-13-matcher-substrate-plan2.files/layerA/layerA_rewrite.py`
Expected: `rewrote 9 functions, 12 literal edits`.

The script asserts every edit. It inserts `binds()` before `test_smoke`; replaces nine
functions, each with the comment block directly above it, by `layerA/<name>.mac`
(`test_dispatch`, `test_matchQ_predicates`, `test_class2_marker_head`,
`test_class3_headvar`, `test_class3_c1_slotted`, `test_class3_c4_321`,
`test_class3_c3_ratio`, `test_class3_b3_33`, `test_class3_c5_34`); inserts the new section
`layerA/test_generated_matchq_shapes.mac` after `test_class2_marker_head` and its call after
that section's call in the run list; rewrites the pattern-level
calls of `test_class3_b1_freeof`, `test_class3_c2_dhead`, `test_class3_c6_cassimp` and
`test_class3_c6b_functionoflog` to `%mr_rule_bindings` / `%mr_rule_accept` /
`%mr_rule_apply`; and fails if any deleted entry (`_mr_pat_`, `%mr_mbp_`, `%mr_logpow_match`,
`%mr_logratio`, `%mr_headvar_match`, `%mr_register_markers`, `%mr_isMQMarker`, `%mr_dispatch(`,
`%mr_lpfac`, or a direct `_mr_rule_…(` call) is still referenced outside comments.

What changes in substance (each measured in the plan-2 pre-validation; the sections' comments
record them):
- **Mechanism checks.** `test_dispatch` uses synthetic `%mr_defrule` records and gains the three
  `mr_model_flags` checks (`rubi` inside `mr_top`); the MatchQ checks use the 4-arg form and
  drop the marker registry (`%mr_register_markers` / `%mr_isMQMarker` are gone with the
  `%mr_mq_*` matcher); the headvar checks run the real rules (3.1.5 r58/r59, 3.3 r58, 3.4 r37)
  instead of the deleted slot matcher.
- **Pins that follow `MR-MATCH` instead of the defmatch era.** `x^2+x^3` against `u_.*x^m_.` is
  false; `3+5x^2+7x^4` against `(f_+g_.*x^2)^r_.` is true without the FreeQ cond (Plus is Flat)
  and false with it; the headvar rule with no leftover factor binds `Px = 1` (the source writes
  `Px_.`); c2's free-d head `(dd*x)^mm2` binds `d = dd, m = mm2`; c1's 3.1.4 r23 rep is
  `x^2*sqrt(…)` (with `5*x^2` the head `(f_.*x_)^m_.` declines); c3's e104 accepted binding is
  `e = (be-af)/(de-cf), f = 1`; 3.2.1 r15 does not bind the numeric-k distributed quotient (r16's
  form); c6 reads the accepted binding (the first complete binding's cond is false).
- **Answer-level tables.** c4, b3 and c5 load the 3_1_x files ahead of their families (deviation
  11); c4 e210's answer carries `polylog`, which has no `diff` rule in this build, so its pin is
  "not a noun and no nested `unintegrable`" instead of a zero-chain.
- **Removed pins** whose helpers are deleted (`%mr_mbp_isfac` rejections, `%mr_lpfac_parse`
  recovery, `%mr_logpow_match` / `%mr_logratio_match` rejections) are replaced by the same
  integrands against the real rules.
- **Generated MatchQ shapes (new section, 22 checks; spec §3.4 "each distinct pattern the
  MatchQ sites use gets a unit test").** The generated sites carry 13 distinct pattern texts;
  `test_matchQ_predicates` and `test_class2_marker_head` pin four (`x^m_.*u_.`,
  `(f_+g_.*x^2)^r_.`, `a_+b_.*v_`, 2.3 r96's `F_[v_]`). `test_generated_matchq_shapes` pins the
  other nine (1.1.1.7 r1 / 1.4.1 r16, 1.4.1 r4 / r68, the two 1.4.2 r17 sites, 9.1 r12, 2.3 r96's
  first site, 3.2.3 r16, 3.3 r59, 3.5 r20) — at least one positive with its bindings and one
  negative each, on the emitted pattern text with the site's cond where it carries one. Maxima
  distributes a power over a product even for a symbolic exponent (`(2*x^3)^m` is stored as
  `2^m*x^(3*m)`), so the 2.3 r96 shape `w_*(a_.*v_^n_)^m_` is pinned on a nested power
  `((1+x)^n)^mm`.

- [ ] **Step 3: Run Layer A**

Run: `maxima --very-quiet -X "--tls-limit 100000" -b test_maxima_rubi.mac < /dev/null | grep -a '^ *FAIL\|^Results'`
Expected: `Results: 897 passed, 0 failed` (~1.8 s wall).

- [ ] **Step 4: Commit**

```bash
git add test_maxima_rubi.mac
git commit -m "tests: Layer A matcher-coupled sections on the substrate entries; generated MatchQ shapes (897/0)"
```

---

### Task 7: P4 measurements, docs and the ledger (P4 gate)

Branch: `matcher-substrate`.

**Files:**
- Create: `probes/matcher/06-dispatch-cost.{mac,sh}`, `probes/matcher/07-fault-survival.sh`,
  `probes/matcher/08-runtime-load.sh` (from the attachments `probes/`), and their `.out` records
- Modify: `AGENTS.md` (§ "Loading rule files: the TLS limit"; § Tests: the Layer A paragraph, the
  matcher substrate unit suites paragraph, a new P3 static gate paragraph)
- Modify: `todo/TODO.md` (§ "Matcher substrate")
- Modify: `.superpowers/sdd/progress.md` (a new section at the end)
- Regenerate: `test/matcher/{roundtrip,controls,spike01,gate}.out`, `{roundtrip,gate}.flags.out` (the
  final-tree gate run)

**Interfaces:**
- Consumes: Tasks 1–6's end state — `load("maxima_rubi.mac")`, `mr_load_all()`, `mr_rule_table`,
  `rubi`, `%mr_rule_accept`, `%mr_dispatch_tree`, `%mr_defrule`, `%mr_matchQ`, the Lisp accessors
  `mr-rule-of` / `mr-rule-key` / `mr-rule-n`; `test/build_rules_core.sh`; `test_maxima_rubi.mac`
  (897); the three unit suites; `test/check_generated_rules.py`; the P0 commit `0a6664c`.
- Produces: the spec §4 P4 gate records (flagless load + Layer A, load time, core build time) and
  the carried-item evidence (dispatch cost, fault survival) as committed probe outputs; the
  AGENTS.md rules Plan 3's runs follow (the TLS flag retired, Layer A 897, three unit suites, the
  P3 gate command); the ledger section Plan 3 reads its inputs from.

- [ ] **Step 1: Copy the probe scripts**

```bash
A=docs/superpowers/plans/2026-09-13-matcher-substrate-plan2.files
cp $A/probes/06-dispatch-cost.mac $A/probes/06-dispatch-cost.sh $A/probes/07-fault-survival.sh \
   $A/probes/08-runtime-load.sh probes/matcher/
```

What each measures (every script stamps `git HEAD`, the UTC time and `build_info()`):
- **08** (spec §3.5 "TLS", §4 P4): without and with `-X "--tls-limit 100000"`,
  `load("maxima_rubi.mac")` + `mr_load_all()` + `rubi(x^3*(a+b*x^2)^(5/2), x)` verified by
  differentiation (`radcan`), and the whole Layer A run, each counting `Thread local storage`
  lines; the dispatcher suite without the flag; the rules core build wall. It leaves
  `test/mr_rules.core` rebuilt (gitignored).
- **07** (deviation 7): a runaway Maxima recursion in 11 places, 2 processes each, no rule files —
  at top level (4 shapes), in a dispatcher cond (named, 2-arg, lambda), in a repl, in
  `%mr_rule_accept`'s cond, in a MatchQ cond (lambda, named) — counting `R SURVIVED`, SBCL's fatal
  `while pseudo-atomic` and Maxima's `Automatically continuing`.
- **06** (Plan 1 carried item 1): the full-table walk (`%mr_rule_accept` on every record — an upper
  bound on a dispatch, which stops at the first answering rule) on five integrands; two real
  dispatches; the collapsible-claimer walk on `x*y1*…*yk`, k = 6, 8, 10, 12; per-record cost on
  the costliest integrand (top 25 over 50 ms); end-to-end `rubi()` on that integrand, and the same
  on the P0 package when `MR_P0_TREE` names a checkout of `0a6664c`.

- [ ] **Step 2: Probe 08 — flagless load and Layer A**

Run: `sh probes/matcher/08-runtime-load.sh > probes/matcher/08-runtime-load.out 2>&1; cat probes/matcher/08-runtime-load.out`
(~20 s). Every one of these must hold:
- both `LOAD` lines end `TLS lines 0`, each followed by an `R load … rules 3513` line and
  `R smoke answered true radcan zero-chain true`;
- both `LAYER-A` lines read `TLS lines 0: Results:  897  passed,  0  failed`;
- `DISPATCH-SUITE flagless … Results:  45  passed,  0  failed`;
- `CORE-BUILD … exit 0: built test/mr_rules.core (<bytes> bytes) rules=3513 fingerprint=<md5>`.

Pre-validation (2026-09-13, the build above, Layer A then 875): `load` 0.38–0.43 s,
`mr_load_all` 1.10–1.49 s, Layer A 1.5–1.6 s wall, core build 3.6–4.5 s wall, 112,775,536 bytes.
Walls are records, not gates.

If a flagless line shows a TLS line or lacks its `Results:` line, **stop and report to the user**:
the spec's fallback (shared capture names in the generator, §3.5) is a design change outside this
plan, and AGENTS.md's TLS rule stays as it is.

- [ ] **Step 3: Probe 07 — fault survival**

Run it with `run_in_background` (~1–2 min):
`sh probes/matcher/07-fault-survival.sh > probes/matcher/07-fault-survival.out 2>&1`

Expected table (columns `survived fatal-pseudo caught-top`, the same on both runs of a variant):

| variant | survived | fatal-pseudo | caught-top | result |
|---|---|---|---|---|
| `accept_cond_named`, `dispatch_cond_2arg`, `dispatch_cond_lambda`, `dispatch_cond_named`, `matchq_cond_named` | 0 | 1 | 0 | |
| `matchq_cond_lambda` | 1 | 0 | 0 | `R result false` |
| `dispatch_repl`, `top_2arg`, `top_mfuncall`, `top_w0`, `top_w2` | 1 | 0 | 1 | |

These are deviation 7's figures (fatal in 5 of the 6 substrate cond shapes; the top-level shapes
survive 8 of 8). A different table is not a task failure — the guard's behaviour on signalled
conditions is gated by the dispatcher suite — but it is recorded as measured in the ledger and
reported at the task review, because deviation 7 and the Plan 3 crash-count check cite it.

- [ ] **Step 4: Probe 06 — dispatch cost**

Start it only after Step 3 has finished and with nothing else running (its cases are sequential
single-process walls). ~11 min: `run_in_background`, then poll.

```bash
git worktree add --detach "${TMPDIR:-/tmp}/mr-p0-tree" 0a6664c
MR_P0_TREE="${TMPDIR:-/tmp}/mr-p0-tree" sh probes/matcher/06-dispatch-cost.sh > probes/matcher/06-dispatch-cost.out 2>&1
```

When `=== done` is in the file: `git worktree remove --force "${TMPDIR:-/tmp}/mr-p0-tree"`.

Must hold: eight `CASE` blocks (`walk`, `claim6`, `claim8`, `claim10`, `claim12`, `attr`, `rubi`,
`rubi-p0`), each with its `R build` line and ending `R DONE`; `rules 3513` in every case but
`rubi-p0` (`rules 3514`, the P0 table with the dead 9.1 rule); both `rubi` lines `answered [true]`.

Pre-validation ranges (two runs, 2026-09-13; expectations, not gates — the P5 median-wall gate
judges cost):
- walk: `sin(x)^x` 0.04–0.05 s, accepting 0; `(a+b*x)^2*(c+d*x)^3*sin(x)` 1.0–1.3 s;
  `x^2*(a+b*x)^3*(c+d*x)^4*(e+f*x)^5*(g+h*x)^6*log(x)` 78–83 s; four symbolic linear powers
  5.4–5.7 s; `x^2*(a+b*log(c*(d+e*sqrt(x))^n))^2` 0.45–0.50 s; dispatch `sin(x)^x` 0.03 s
  answered false; dispatch four symbolic linear powers 0.14–0.16 s answered true.
- claims k = 6 / 8 / 10 / 12: 2.0–2.1 / 7.8–9.0 / 34–40 / 173–194 s, accepting 7 (exponential in
  k: the collapsible claimer, Plan 1 carried item 1).
- attr: 71 records over 50 ms; the top three are `3_5 r37` (a moved inner condition that
  integrates, `mr_int`), `3_1_5 r28` and `3_5 r11` (moved inner conditions that expand,
  `%mr_expandIntegrand`), each accepting (`true`); then generic product patterns (`1_4_1 r4`,
  `1_3_3 r3`, `1_1_1_7 r9`, …) whose polynomial predicates re-run per binding under cond retry.
- rubi on that integrand: substrate 40–51 s vs `rubi-p0` 48–60 s (the substrate was faster in
  both runs).

- [ ] **Step 5: Commit the probes**

```bash
git add probes/matcher/06-dispatch-cost.mac probes/matcher/06-dispatch-cost.sh probes/matcher/06-dispatch-cost.out \
        probes/matcher/07-fault-survival.sh probes/matcher/07-fault-survival.out \
        probes/matcher/08-runtime-load.sh probes/matcher/08-runtime-load.out
git commit -m "probe: matcher 06/07/08 — dispatch cost, fault survival, flagless load + Layer A (P4)"
```

- [ ] **Step 6: AGENTS.md — the TLS section**

Replace the whole section from `## Loading rule files: the TLS limit` up to (not including)
`## Looking up Maxima itself`:

````markdown
## Loading rule files: the TLS limit

The SBCL special-variable pool is a hard per-process cap: creating a
`defmatch`/`matchdeclare` slot beyond it is the **uncatchable** FATAL
"Thread local storage exhausted". The installed core's baked-in limit is
~4098 special vars (`probes/load_wall/probe-tls-calibration.out`), and a
generated class-1 rule costs ~9.6 of them on average
(`probes/load_wall/probe-load-curve.out`) — the default limit holds only
~310 class-1 rules. **Any maxima process that loads rule files must be
run with `-X "--tls-limit 100000"`** (user decision 2026-08-22). The flag
takes two argv tokens — not `--tls-limit=N`. 100000 covers the full
loaded Rubi set (7,432 rules, T1 count) at ~1.4x headroom; the probes
above self-flag if the build moves.
````

with

````markdown
## Loading rule files: the TLS limit

The SBCL special-variable pool is a hard per-process cap (~4098 in the
installed core, `probes/load_wall/probe-tls-calibration.out`); creating a
special variable beyond it is the **uncatchable** FATAL "Thread local
storage exhausted". Under `defmatch` every generated rule's
`defmatch`/`matchdeclare` slots were special variables (~9.6 per class-1
rule, `probes/load_wall/probe-load-curve.out`), so from 2026-08-22 (user
decision) until the matcher substrate's P4 every maxima process that
loaded rule files ran with `-X "--tls-limit 100000"`.

The rule files are now `%mr_defrule` records: a pattern is a string the
Lisp matcher prepares, and no rule creates a pattern-variable slot.
Without the flag, `load("maxima_rubi.mac")` + `mr_load_all()` (3,513
rules) answers and verifies a smoke integral and the whole Layer A run
is green, with no TLS message (`probes/matcher/08-runtime-load.out`,
build `branch_5_50_base_84_g4204fb669`). **The flag is no longer
required** (spec `docs/superpowers/specs/2026-09-12-matcher-substrate-design.md`
§3.5). It is harmless: `test/build_rules_core.sh` and
`test/corpus_driver.py` still pass it. cond/repl `block` locals are
still special variables — if a later port brings the error back, re-run
probe 08 and restore the flag rule (two argv tokens:
`-X "--tls-limit 100000"`, not `--tls-limit=N`).
````

- [ ] **Step 7: AGENTS.md — the Tests paragraphs**

Replace

````markdown
**Layer A — unit suite** (the per-change gate), one batch run:

```sh
maxima --very-quiet -X "--tls-limit 100000" -b test_maxima_rubi.mac
```

The TLS flag is MANDATORY (measured 2026-09-01, class-3 deferred
campaign C1): the test set loads rule siblings cumulatively per
process, and the C1 tests (3_1_3/3_1_4/3_1_5) pushed the union over
the ~4098 special-var cap — the flagless gate now dies with the
uncatchable TLS HALT at 3_1_5 (slot cost is never freed; see the TLS
section above). It was flagless only while the loaded subset fit.

892 targets (green: `Results: 892 passed, 0 failed`; the
````

with

````markdown
**Layer A — unit suite** (the per-change gate), one batch run:

```sh
maxima --very-quiet -b test_maxima_rubi.mac
```

No TLS flag since the matcher substrate's P4 (the flagless run is
green, `probes/matcher/08-runtime-load.out`; see the TLS section above).
From 2026-09-01 (class-3 deferred campaign C1) until then the flag was
mandatory: the test set loads rule siblings cumulatively per process,
and the `defmatch` slots of 3_1_3/3_1_4/3_1_5 overran the special-var
cap.

897 targets (green: `Results: 897 passed, 0 failed`; the
````

replace

```markdown
→ 892 C6b (3.5 r42 FunctionOfLog catch-all port + bare catch-all
pattern fix, e134/e139/e258, 23 checks)).
```

with

```markdown
→ 892 C6b (3.5 r42 FunctionOfLog catch-all port + bare catch-all
pattern fix, e134/e139/e258, 23 checks), → 897 matcher substrate P4
(the matcher-coupled sections rewritten against the substrate entries,
892 → 875, and the generated MatchQ pattern shapes, 22 checks)).
```

and replace

````markdown
**Matcher substrate — unit suites** (the per-change gate for
`maxima_rubi_match.lisp` / `maxima_rubi_tree.lisp`; branch
`matcher-substrate`, spec
`docs/superpowers/specs/2026-09-12-matcher-substrate-design.md`). No
rule files are loaded, so no TLS flag:

```sh
maxima --very-quiet -b test/matcher/test_mr_match.mac
maxima --very-quiet -b test/matcher/test_mr_tree.mac
```

Green: `Results: 51 passed, 0 failed` (mr-match; 48 at Plan 1's Task 5,
+3 at the final-review fix wave: the last-absorber cost bounds and the
empty-leftover lock) and `Results: 46 passed, 0 failed` (mr-tree).
````

with

````markdown
**Matcher substrate — unit suites** (the per-change gate for
`maxima_rubi_match.lisp` / `maxima_rubi_tree.lisp` /
`maxima_rubi_dispatch.lisp`; branch `matcher-substrate`, spec
`docs/superpowers/specs/2026-09-12-matcher-substrate-design.md`). No
rule files are loaded:

```sh
maxima --very-quiet -b test/matcher/test_mr_match.mac
maxima --very-quiet -b test/matcher/test_mr_tree.mac
maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null
```

Green: `Results: 53 passed, 0 failed` (mr-match; 48 at Plan 1's Task 5,
+3 at the final-review fix wave: the last-absorber cost bounds and the
empty-leftover lock, +2 at Plan 2: the Power-exponent Optional
default), `Results: 51 passed, 0 failed` (mr-tree; 46, +5 at Plan 2:
CRE input and the booleans) and `Results: 45 passed, 0 failed`
(dispatch: rule records, dispatcher outcomes, bindings / retry / head
symbols / CRE / G-6, the test entries, MatchQ).
````

Then, directly after that paragraph's last sentence (the plain-SBCL `test_mr_match.lisp` command),
insert a blank line and:

````markdown
**Generator — P3 static gate** (the per-change gate for
`generator/generate_rules.py` and the regenerated rule files; spec
section 4 P3). No Maxima; `sbcl` must be on the PATH:

```sh
python3 test/check_generated_rules.py
```

Green: `Results: 11 passed, 0 failed`. It compares the working tree's
`rules/class{1,2,3}/*.mac` with the P0 commit `0a6664c` (`--base
<commit>` for another base): rule counts and `mr_rules_<key>` lines, no
`defmatch`, every cond/repl body byte-identical to the base except the
spec's closed exception list (each exception checked as the exact text
transformation it claims to be), the reader self-test
(`python3 generator/mma_reader.py`), and every pattern string preparing
in `MR-MATCH`. Regeneration is byte-identical:
`python3 generator/generate_rules.py --class <1|2|3>` leaves
`git status --porcelain rules/` empty.
````

Run: `grep -c 'tls-limit' AGENTS.md` — Expected: `2` (the historical sentence and the restore
instruction in the TLS section).

- [ ] **Step 8: `todo/TODO.md` — the Matcher substrate section**

Replace the heading `## Matcher substrate — in prog (Plan 1 complete 2026-09-12)` with
`## Matcher substrate — in prog (Plan 2 complete YYYY-MM-DD)`, where `YYYY-MM-DD` is the date
of this commit (`date +%F`). Keep the intro paragraph (`Classes 1–3 re-hosted …` through
`(plan 1 section).`) and replace the two bullets under it

```markdown
- Next: Plan 2 = P3 (generator: pattern emission, `%mr_defrule`, static
  check) – P4 (dispatcher and loader, Layer A rewrite), written just in
  time — open
- Known cost item for Plan 2: a collapsible claimer (e.g.
  `(c_.*x_)^m_.` under Times) still enumerates every sub-run of a
  product's factors (exponential in the factor count; measured in the
  ledger's final-review fix-wave block) — open
```

with

```markdown
Plan 2 (P3–P4,
`docs/superpowers/plans/2026-09-13-matcher-substrate-plan2.md`) is
complete on the same branch: the generator emits evaluated-FullForm
pattern records (`%mr_defrule`; 3,513 rules, 9.1 generated; P3 static
gate `test/check_generated_rules.py` 11/0);
`maxima_rubi_dispatch.lisp` dispatches on `mr-match` / `mr-tree` (unit
suite 45/0); passes 2–4, the `defmatch`-era matchers and
`maxima_rubi_implicit1.lisp` / `maxima_rubi_pass4.lisp` are deleted;
Layer A 897/0; the TLS flag is no longer required
(`probes/matcher/08-runtime-load.out`); dispatch cost
`probes/matcher/06-dispatch-cost.out`; fault survival
`probes/matcher/07-fault-survival.out`. Ledger: plan 2 section.

- Next: Plan 3 = P5 (four full class 1–3 runs, one switch flipped per
  run; gates against the P0 records) – P6 (close), written just in
  time — open
- Carried into Plan 3: the MODEL-LOST figures (1,166 / 395 measured vs
  the spec's 1,142 / 312) unexplained; the shard launcher leaves stale
  shard files; the speed-gate definition; the three switches written
  into the driver's `filter:` line (plan 2 deviation 8); crash-class
  counts against P0 (a runaway recursion in a cond is fatal inside
  `mr-match:match`, probe 07) — open
- Deferred: the `MX_` plist re-read issue in `mr-tree` (not reachable:
  the dispatcher never prints and re-reads a tree) — open
- Known cost item: a collapsible claimer (e.g. `(c_.*x_)^m_.` under
  Times) still enumerates every sub-run of a product's factors — the
  full-table walk on `x*y1*…*y12` takes minutes; on large products the
  walk is dominated by moved inner conditions that integrate or expand
  (3.5 r37, 3.1.5 r28, 3.5 r11) (`probes/matcher/06-dispatch-cost.out`)
  — open, judged by the P5 median-wall gate
```

- [ ] **Step 9: The final-tree P4 gate**

Run each and compare with the expected line:

| command | expected |
|---|---|
| `maxima --very-quiet -b test_maxima_rubi.mac < /dev/null \| grep -a '^ *FAIL\|^Results'` | `Results: 897 passed, 0 failed` (flagless: the AGENTS.md command) |
| `maxima --very-quiet -b test/matcher/test_mr_match.mac \| grep -a '^Results'` | `Results: 53 passed, 0 failed` |
| `sbcl --non-interactive --load maxima_rubi_match.lisp --load test/matcher/test_mr_match.lisp --eval '(mr-match-test:run)' \| grep -a '^Results'` | `Results: 53 passed, 0 failed` |
| `maxima --very-quiet -b test/matcher/test_mr_tree.mac \| grep -a '^Results'` | `Results: 51 passed, 0 failed` |
| `maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null \| grep -a '^Results'` | `Results: 45 passed, 0 failed` |
| `python3 test/check_generated_rules.py \| tail -1` | `Results: 11 passed, 0 failed` |
| `for c in 1 2 3; do python3 generator/generate_rules.py --class $c > /dev/null; done; git status --porcelain rules/ \| wc -l` | `0` |

Then the matcher regression suite on both arms, one after the other with `run_in_background`
(~50 s wall each):

```bash
MR_LEGS=tree,maxima MR_SPIKE=1 sh test/matcher/run.sh > /tmp/p2t7-defaults.log 2>&1
MR_LEGS=tree,maxima MR_MODEL_FLAGS=1 MR_SPIKE=1 sh test/matcher/run.sh > /tmp/p2t7-flags.log 2>&1
grep -a 'Results' /tmp/p2t7-defaults.log /tmp/p2t7-flags.log
```

Expected: `Results: 109 passed, 0 failed` for both, and against Task 3's committed records only
judged / git HEAD / TIMING / build lines change:

```bash
for f in roundtrip.out roundtrip.flags.out controls.out spike01.out gate.out gate.flags.out; do
  printf '%s ' $f; git diff test/matcher/$f | grep '^[-+]' | grep -v '^[-+][-+]' \
    | grep -v -i 'judged\|git HEAD\|TIMING\|build\|shard0.log\|run:' | wc -l; done
```

Expected: `0` after every file name.

- [ ] **Step 10: The ledger**

Append to `.superpowers/sdd/progress.md` a section in the form of the Plan 1 section above it.
Every `<…>` below is a measured value copied verbatim from the run named next to it — no
figure is retyped from this plan:

```markdown
## Plan: 2026-09-13 matcher substrate plan 2 (P3–P4; branch matcher-substrate)

Spec: docs/superpowers/specs/2026-09-12-matcher-substrate-design.md
Plan: docs/superpowers/plans/2026-09-13-matcher-substrate-plan2.md (+ .files/ attachments)

### P3 — static gate (Tasks 1–2)
- build: <build_info() version / timestamp> / SBCL 2.6.7
- Task 1, P0 tree (red): <the five FAIL lines and the Results line of Task 1 Step 6>
- Task 2: <the INFO line and the Results line of Task 2 Step 7>; TOTAL lines 3054 / 125 / 334; regeneration idempotent

### P4 — matcher, converter, dispatcher, runtime, Layer A (Tasks 3–6)
- Task 3 red: <the FAIL and Results lines of Task 3 Step 2>; green: <the three Results lines of Task 3 Step 6>
- Task 3 regression suite: defaults <gate Results line, judged time, git HEAD, wall>; flags <same>
- Task 4 red: <FAIL count and Results count of Task 4 Step 2>; green: <Results line of Task 4 Step 4>
- Task 5: utils <the edit_utils.py line> -> 5007 lines; <the two SMOKE lines>; <the four Results lines and the core build line of Task 5 Step 8>
- Task 6 red: <PASS / FAIL / Results counts of Task 6 Step 1>; green: <Results line of Task 6 Step 3>

### P4 gate records (Task 7)
- probe 08 (probes/matcher/08-runtime-load.out, <its === line>): <every LOAD / R / LAYER-A / DISPATCH-SUITE / CORE-BUILD line>
- probe 07 (probes/matcher/07-fault-survival.out, <its === line>): fatal-pseudo in <variants>; survived in <variants>
- probe 06 (probes/matcher/06-dispatch-cost.out, <its === line>): walk <the five walk walls and the two dispatch lines>; claims k 6/8/10/12 <walls>; attr <total, records over 50 ms, the top three>; rubi <substrate wall> vs P0 <rubi-p0 wall>
- final tree (Task 7 Step 9): <the seven expected-column results>; regression suite defaults <Results, judged, git HEAD> / flags <same>
- Plan 2 complete: P3 and P4 gates green. Next: Plan 3 (P5–P6).
```

- [ ] **Step 11: Commit**

```bash
git add AGENTS.md todo/TODO.md .superpowers/sdd/progress.md \
        test/matcher/roundtrip.out test/matcher/controls.out test/matcher/spike01.out test/matcher/gate.out \
        test/matcher/roundtrip.flags.out test/matcher/gate.flags.out
git commit -m "docs: P4 gate — TLS flag retired, Layer A 897, dispatch suite and P3 gate commands; TODO; ledger plan 2"
```
