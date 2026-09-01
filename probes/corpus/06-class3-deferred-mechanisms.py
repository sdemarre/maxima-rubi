#!/usr/bin/env python3
"""Class-3 deferred-mechanisms triage probe (class-3 deferred campaign,
Task 2; plan docs/superpowers/plans/2026-08-30-class3-deferred-campaign.md).

Measures, for every entry of the class-3 `deferred` population
(test/corpus_class3.out: 1,033 entries — the package's top-level
no-answer nouns on a corpus that expects an answer), the mechanism by
which the dispatch 0-fires:

  (1) the production dispatch trace — the rubi_verbose "fired on"
      lines under rubi(mr_f, x) (the passes 1-3 rule fires, if any);
  (2) the per-bare-factor wrapped table sweep — the pass-4 prototype:
      for each bare top-level factor, a full table scan with the
      findfun shadow (maxima_rubi_implicit1.lisp's
      *mr-implicit1-which*) offering that factor, both scan
      directions, via Task 1's shared primitive %mr_p4_once
      (maxima_rubi_utils.mac) — the SAME unit the production pass-4
      sweep will call (spec section 5.2);
  (3) the non-firing drill — for 0-sweep entries, every class-3 rule's
      pattern call (the exact expression the _mr_rule body calls, so
      the four %mr_headvar_match rules are covered too) plus the cond
      evaluated clause by clause; the drill functions are generated
      from the committed rules/class3/*.mac source at --gen time.

One fresh core subprocess per entry (120 s safety cap; two entries
measured 60 s against the original 60 s cap, the rest 0.7-27.6 s),
24 LPT shards packed on the record's t= (the plan's step 4).

Reader-desync buffer (measured 2026-08-30, entries/0620 = 3.3 e287):
rubi()'s rule scan can hit the build's `expt: undefined: 0 to a
negative exponent.` error path mid-evaluation (the 0^negative
emitter), and this build's error recovery then calls the READER on
the input stream, consuming the following lines as a continuation
and desyncing the rest of the batch (RETRIEVE: End of file
encountered, rc=0, every marker after the witness lost — 27 of the
29 first-run subprocess-died entries, all with t= 6-42 s; the
remaining 2 were 60 s-cap timeouts, a separate cause). The corpus driver's
build_text (test/corpus_driver.py) carries a 60-line pos/no filler
buffer after the witness for exactly this reason; entry_mac now
carries the same buffer after the witness. The sweep's
per-candidate scans run the same rule machinery, but all 166 first-
run sweep scans (37 entries x 4-6 candidates) completed clean
without a buffer, so the template mirrors the driver's single
buffer; a mid-sweep desync would surface as a subprocess-died label
at merge and is the follow-up signal. With the buffer the 0620
re-run completes clean (PROD integrate, P4CENSUS 0 false, all DR
lines, DONE; the run consumed 2 filler lines and printed no
RETRIEVE).

Per-entry result (one MECH line in the merged .out):
  MECH <label:16s> t=<dt:6.1f>s <rel> e<n> L<ln> npat=<j> swept=<s> <detail>
  (the label field is 16s: RECORD-MISMATCH is 15 chars — review round 2)
  label in {FIRE4, D-NEST, 0FIRE-EXPL, 0FIRE-POOL, RECORD-MISMATCH}:
  The plan's step-5 label logic counts ANY P4FIRE as FIRE4. This
  probe refines it (measured 2026-08-30 against the committed
  dispatch, maxima_rubi_utils.mac:140-176): a rule whose replacement
  is a pure sub-integral call 0-fires the nested dispatch and RETURNS
  A TOP-LEVEL NOUN ANSWER, and %mr_dispatch returns a noun answer as
  a non-false res (`res # false -> ans : res`), so the sweep
  P4FIREs it. A noun sweep fire cannot rescue the entry (the A/B
  re-measurement would not move it), so:
    FIRE4           a sweep fire with a non-noun top-level answer
    D-NEST          no non-noun sweep fire; a production rule fired
                    and the answer is a top-level noun (the nested
                    sub-integral 0-fired); a noun sweep re-fire is
                    recorded as a sweep-noun= fact
    0FIRE-EXPL      0-fires; the integrand has an explicit-power
                    top-level factor (the shadow-dead case — the
                    original findfun returns the explicit factor
                    before the shadow runs); detail carries the
                    P4DIAG strings
     0FIRE-POOL      0-fires; no explicit power; detail carries the
                     drill facts (per-rule clause vectors, CRASH/BOOL/
                     CONDE counts, nonproduct for a non-product top).
                     A DR line is a matched rule: no line = the
                     pattern 0-bound; CRASH = the pattern call
                     crashed; BOOL = the match carries a boolean;
                     CONDE = the cond crashed on a matched binding
                     (a decline-in-production fact)
     RECORD-MISMATCH the record says deferred but production now
                     answers (drift signal; the merge asserts 0)
   npat  = the count of drill lines that carry a clause vector
           (neither CRASH nor BOOL nor CONDE; 0 when the sweep fired
           — the drill runs on 0-fire only)
   swept = the number of P4SCAN lines (0 = the sweep skipped; else
           2*k over the k bare factors) — the sweep-cost metric key
    A cap-exceeded entry (the 120 s per-entry safety net) carries a
    trailing `cap` in the detail for manual follow-up (none expected:
    deferred package times are 0.7-27.6 s; two first-run entries hit
    the original 60 s cap under the sweep + drill overhead, so the
    cap was raised — the re-run confirms or refutes the need)

Target mass (spec section 2.1: 788 = 329 certain + 459
baseline-unverified) is carried per entry from
test/corpus_class3.baseline.out: the baseline class of the same
(rel, n) key in {verified, expected, unverified} = flagged (313 /
16 / 459); {no-answer, timeout, error} = the 150 / 76 / 19
remainder.

Calibration gate: --calibrate re-runs the Task-1 16-entry set (f1,
f2, f5 + 3.1.5 e186-e197 verbatim + the atom-top row — the plan's
"16" was a typo for 15; the atom row, review round 1, makes 16
real) through this probe's OWN per-entry measurement and asserts
the Task-1 table (f2 FIRE4 first-fire 3_1_5 / f1 0FIRE-EXPL pick
x^3 / f5 0FIRE-POOL nonproduct / e186-e193 FIRE4 prod 3_5 /
e194-e197 0FIRE-EXPL pick F(a*x)^2 / atom: no crash, census
0,false, P4SKIP, no P4DIAG — the %mr_barefactors atom-top guard
regression), then the fire-attribution proofs (a synthetic wrapped
fired-on block + five real >38-char deferred entries: every fired
event non-empty, full-integrand fires attributed — the review-
round-2 continuation-fold regression) — "a harness that
misclassifies a calibration case does not ship". --merge embeds
the calibration section and fails on any row mismatch.

Run (see 06-class3-deferred-mechanisms.run):
  sh probes/corpus/06-class3-deferred-mechanisms.run
  (calibrate + gen + launch; then, when the pid file is clean:
   python3 probes/corpus/06-class3-deferred-mechanisms.py --merge <workdir>)
Or by hand:
  python3 probes/corpus/06-class3-deferred-mechanisms.py --gen
  python3 probes/corpus/06-class3-deferred-mechanisms.py --launch
  python3 probes/corpus/06-class3-deferred-mechanisms.py --shard <K>
  python3 probes/corpus/06-class3-deferred-mechanisms.py --merge <workdir>
  python3 probes/corpus/06-class3-deferred-mechanisms.py --calibrate
  python3 probes/corpus/06-class3-deferred-mechanisms.py --gen --smoke 10

Build quirks baked into the generated .mac (each measured 2026-08-30,
Maxima branch_5_50_base_84_g4204fb669 / SBCL 2.6.7; the Task-1
calibration header is the committed record):
- string building uses concat(...) — this build's "+" on strings does
  NOT concatenate (it reads the string contents as symbols and
  returns their sum); the plan template's `"..." + "..."` forms are
  all concat here;
- P4DIAG renders via string(...) — the plan's sapply(lambda[[s],s],
  ...) errors on a flat list of strings in this build;
- the plan template's errcatch read (`mm # false` directly on the
  errcatch value) is wrong — errcatch returns [value] on success and
  [] on error (probe-errcatch-semantics; the %mr_dispatch idiom), so
  the drill unwraps part(mm, 1) before the # false / BOOL / clause
  reads;
- the template variables are mr_-prefixed (the driver's convention,
  corpus_driver.py build_text): the corpus texts re-parse in their
  scope and the class-3 parameter set includes f, which would
  collide with a bare `f :=` name;
- every simple assignment is the single-colon `x: expr` form — in
  this build the `:=` form is broken in every non-interactive mode
  measured (-b file, -b stdin, --batch-string, and inside blocks
  too): a top-level `foo := x` dies with `define: argument cannot
  be an atom or a subscripted memoizing function; found: foo` and
  a `b := 5` inside a block kills the call, while `foo : x` works
  in all of them. Function definitions `f(a) := ...` are UNAFFECTED
  (the rule files are full of them). The codebase idiom is already
  single-colon (maxima_rubi_utils.mac, the driver template); the
  plan template's `mr_f :=` forms are `mr_f:` here;
 - relational ops stay nouns at top level; every boolean position in
   the template is an is() or an if-test (the codebase idiom);
  - op() on an atomic expression is a HARD ERROR in this build
    (`part: argument must be a non-atomic expression`) — the P4DIAG
    guard is `if (not atom(mr_f)) and is(op(mr_f) = "*")`: the atom
    arm short-circuits before op() is reached (measured 2026-08-30,
    review round 1 — the atom calibration row dies on the unguarded
    form; %mr_barefactors carries the same guard for f itself).

Template deviations from the plan's step-2 template (review round 2):
- rubi_verbose stays on THROUGH the sweep (the plan turns it off
  before the sweep) — the sweep's "fired on" rule names are what the
  triage records (documented in the Task-1 .mac header; carried here
  for self-containment);
- the template emits an ADDITIVE `disp(concat("MRFSTR ",
  string(mr_f)))` line (not in the plan): the full-integrand identity
  for fire attribution — a nested sub-integral fire carries a
  DIFFERENT integrand string, and the full-integrand match selects the
  top-level fire of each call (parse_output's attribution);
- the verbose fired-on print is a 4-arg print and WRAPS AT THE
  ARGUMENT BOUNDARY when the integrand exceeds ~37 chars: the fired-on
  line then carries no integrand and no trailing backslash, and the
  integrand lands on the next physical line, indented, backslash-free
  (measured 2026-08-30, review round 2). parse_output FOLDS that
  continuation into the fired event (an empty-capture fired-on line
  absorbs the following non-anchor line); integrands >70 chars wrap in
  the backslash-terminated mode the backslash join catches. The
  --calibrate gate re-runs both a synthetic wrapped block and five
  real >38-char deferred entries as the re-runnable proof;
- a boolean sweep/production answer prints the `bool` marker (the
  template checks %mr_containsBoolean BEFORE atom — booleanp does not
  exist in this build, measured) so a boolean leak is not conflated
  with a constant answer; a bool fire is a non-rescue fact
  (sweep-noun=), exactly like a noun fire (label_entry's NONRESCUE).
  The Task-1 calibration .mac (a separate committed artifact) still
  prints the unmarked atom form — no empirical occurrence is known.
  """

import argparse
import glob
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SECTION = "3 Logarithms"
SLUG = "06-class3-deferred-mechanisms"
PKG_RECORD = os.path.join(ROOT, "test", "corpus_class3.out")
BASE_RECORD = os.path.join(ROOT, "test", "corpus_class3.baseline.out")
OUT = os.path.join(ROOT, "probes", "corpus", SLUG + ".out")
DEFAULT_WORKDIR = os.path.join(ROOT, "probes", "corpus", SLUG + ".work")
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")

# Pinned population (the plan's global constraints + spec section 2.1;
# the join was re-verified against the committed records at writing
# time — a drift here means the records moved, and the probe must not
# silently triage a different set).
EXPECTED_DEFERRED = 1033
EXPECTED_FLAGGED = 788
EXPECTED_SPLIT = {"verified": 313, "expected": 16, "unverified": 459}
EXPECTED_BASE_REMAINDER = {"no-answer": 150, "timeout": 76, "error": 19}
EXPECTED_RULES = 333

N_SHARDS = 24
ENTRY_CAP = 120         # per-entry safety cap (s); the 30 s corpus cap
                        # is policy, this is the probe's safety net
                        # (60 -> 120 measured 2026-08-30: two entries
                        # hit the 60 s cap under sweep + drill)

# Entry line: <class:14s> t=<dt:6.1f>s <rel> e<n> L<lineno>. The t=
# field is PADDED (t=%6.1fs) — the plan's regex (t=<dt>\d+\.\d) misses
# it; the \s* is the fix, re-verified against both committed records.
ENTRY_RE = re.compile(
    r"^(?P<cls>\S+)\s+t=\s*(?P<t>\d+\.\d)s\s+"
    r"(?P<rel>\S.*?) e(?P<n>\d+) L(?P<ln>\d+)\s*$")

NUONOUN = {"integrate", "unintegrable"}   # the driver's top-level noun ops
# A boolean answer prints the "bool" marker (the template checks
# %mr_containsBoolean before atom — booleanp does not exist in this
# build, measured review round 2) and is a non-rescue exactly like a
# noun answer: it cannot move the entry in the A/B re-measurement.
NONRESCUE = NUONOUN | {"bool"}
FLAG_CLASSES = ("verified", "expected", "unverified")

# The driver is the single source of truth for the core path (SBCL
# resolution, RULES_CORE, the fingerprint). Importing it runs
# ensure_rules_core() at module level — the core is built (single-
# flight) if missing/stale before any launch, exactly as the corpus
# runs get. The driver also parses sys.argv at import time (its
# standalone-run knobs); neutralize it before the exec and restore
# it after (the launch scripts do the same,
# e.g. launch_class_shards.py:65).
_drv_argv = sys.argv
sys.argv = ["corpus_driver"]
try:
    _spec = importlib.util.spec_from_file_location(
        "corpus_driver", os.path.join(ROOT, "test", "corpus_driver.py"))
    assert _spec is not None and _spec.loader is not None, \
        "test/corpus_driver.py not found"
    driver = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(driver)
finally:
    sys.argv = _drv_argv
CORE = driver.RULES_CORE
SBCL = driver.SBCL
assert SBCL, "no sbcl on PATH — the core subprocess path needs it"


def split_elements(entry_text):
    """Depth-aware split at top-level commas (driver mirror)."""
    parts, depth, cur = [], 0, ""
    for ch in entry_text:
        if ch in "[(":
            depth += 1
        elif ch in "])":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts]


def extract_entries(path):
    """Entry texts (outer brackets, no trailing comma/$) + line nos."""
    lines = open(path, encoding="utf-8").read().splitlines()
    entries, line_nos = [], []
    for i, l in enumerate(lines, 1):
        if l.strip().startswith("["):
            t = l.rstrip()
            if t.endswith("$"):
                t = t[:-1]
            if t.endswith(","):
                t = t[:-1]
            entries.append(t)
            line_nos.append(i)
    assert entries and entries[-1].endswith("]]"), path
    entries[-1] = entries[-1][:-1]
    return entries, line_nos


def load_record(path):
    """Ordered (key, cls, t) list + key -> (cls, t) dict."""
    items, d = [], {}
    for line in open(path, encoding="utf-8"):
        m = ENTRY_RE.match(line.rstrip("\n"))
        if m:
            k = (m["rel"], int(m["n"]))
            items.append((k, m["cls"], float(m["t"])))
            d[k] = (m["cls"], float(m["t"]))
    return items, d


def deferred_set():
    """The triage population + target flags, with the pinned asserts."""
    _items, pkg = load_record(PKG_RECORD)
    _bitems, base = load_record(BASE_RECORD)
    # Record order (the merge wrote the record sorted by (rel, n));
    # the dict preserves file order, so the entry indexes are
    # deterministic without a re-sort.
    deferred = [(k, t) for k, (cls, t) in pkg.items() if cls == "deferred"]
    assert len(deferred) == EXPECTED_DEFERRED, \
        f"deferred population moved: {len(deferred)} != {EXPECTED_DEFERRED}"
    flags = {}
    split = Counter()
    remainder = Counter()
    for k, _t in deferred:
        assert k in base, f"deferred {k} missing from the baseline record"
        cls = base[k][0]
        if cls in FLAG_CLASSES:
            split[cls] += 1
            flags[k] = cls
        else:
            remainder[cls] += 1
            flags[k] = cls
    assert len(flags) == EXPECTED_DEFERRED
    flagged = sum(split.values())
    assert flagged == EXPECTED_FLAGGED, \
        f"target mass moved: {flagged} != {EXPECTED_FLAGGED} ({dict(split)})"
    assert dict(split) == EXPECTED_SPLIT, \
        f"329/459 split moved: {dict(split)} != {EXPECTED_SPLIT}"
    assert dict(remainder) == EXPECTED_BASE_REMAINDER, \
        f"baseline remainder moved: {dict(remainder)} != {EXPECTED_BASE_REMAINDER}"
    return deferred, flags


def suite_map():
    """rel -> (entries, line_nos) for the section files."""
    m = {}
    for path in sorted(glob.glob(os.path.join(SUITE, SECTION, "*.mac"))):
        rel = SECTION + "/" + os.path.basename(path)
        m[rel] = extract_entries(path)
    assert m, "no suite .mac files under " + SECTION
    return m


def depth_split_and(text):
    """Top-level (paren/bracket depth 0) ` and `-split of a cond expr.
    The generated conds join Rubi's cond clauses with ` and ` (single
    space, the translate pass) and the nonzero-guard appends with
    `  and  ` (double space); a depth-0 `and` word is a join in both
    shapes. The surrounding-token guard keeps a name containing the
    substring 'and' intact."""
    parts, depth, cur, i, n = [], 0, "", 0, len(text)
    while i < n:
        c = text[i]
        if c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        if (depth == 0 and c == "a" and text[i:i + 3] == "and"
                and (i == 0 or text[i - 1] in " \t)]")
                and i + 3 < n and text[i + 3] in " \t"):
            parts.append(cur)
            cur = ""
            i += 3
            while i < n and text[i] == " ":
                i += 1
            continue
        cur += c
        i += 1
    parts.append(cur)
    return [p for p in parts if p.strip() != ""]


def d0_comma(text):
    depth = 0
    for c in text:
        if c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        elif c == "," and depth == 0:
            return True
    return False


COND_HDR = re.compile(
    r"^_mr_cond_(\S+?)_r(\d+)\(mm, x\) := block\(\[([^\]]*)\],\s*$")
RULE_HDR = re.compile(
    r"^_mr_rule_(\S+?)_r(\d+)\(f, x\) := block\(\[mm")


def pattern_call(lines, f, r):
    """The RHS of the `mm : <expr>,` line in _mr_rule_<f>_r<r>'s body —
    the EXACT pattern call production makes, so the four headvar
    rules (3_1_5 r58/r59, 3_3 r58, 3_4 r37: %mr_headvar_match, no
    _mr_pat_<f>_rN defmatch — 329 of the 333 are defmatch patterns,
    measured 2026-08-30) drill identically to production. The plan's
    step 3 reads the defmatch line instead; it sees 329/333 and would
    silently skip the four, so the _mr_rule body is the parse source."""
    for i, l in enumerate(lines):
        if RULE_HDR.match(l) and l.startswith(f"_mr_rule_{f}_r{r}(f, x)"):
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("mm : "):
                j += 1
            assert j < len(lines), f"no mm line in _mr_rule_{f}_r{r}"
            expr = lines[j].strip()[len("mm : "):]
            # strip the terminating depth-0 comma
            depth, cut = 0, len(expr)
            for k, c in enumerate(expr):
                if c in "([":
                    depth += 1
                elif c in ")]":
                    depth -= 1
                elif c == "," and depth == 0:
                    cut = k
                    break
            expr = expr[:cut].strip()
            assert expr.endswith(")") and " " not in expr.split("(")[0], \
                f"{f} r{r}: pattern call is not a single call: {expr[:60]}"
            # The rule bodies call their pattern with the PARAMETER
            # names (f, x); the entry batch carries the integrand in
            # the mr_f global (the driver's collision-avoidance
            # convention — the class-3 parameter set includes a bare
            # f), so the spliced call must read (mr_f, x).
            m2 = re.match(r"^(\S+)\(f, x(,|\))", expr)
            assert m2, \
                f"{f} r{r}: pattern call not in the (f, x ...) form: " \
                f"{expr[:60]}"
            # (m2.end() - 1 is the consumed ',' / ')' itself — spliced
            # once, with the remainder after it)
            return m2.group(1) + "(mr_f, x" + expr[m2.end() - 1:]
    raise AssertionError(f"no _mr_rule_{f}_r{r} definition")


def parse_class3_rules():
    """All 333 rule drill specs, per file, in file/rule order."""
    rules = []
    for path in sorted(glob.glob(os.path.join(ROOT, "rules", "class3", "*.mac"))):
        f = os.path.basename(path)[:-4]
        lines = open(path, encoding="utf-8").read().splitlines()
        for i, l in enumerate(lines):
            m = COND_HDR.match(l)
            if not m:
                continue
            assert m.group(1) == f, f"cond key/file mismatch at {path}:{i+1}"
            r = m.group(2)
            slots_txt = m.group(3)
            slots = ([s.strip() for s in slots_txt.split(",")]
                     if slots_txt.strip() else [])
            # The committed conds are uniformly 3 lines: the block
            # header, the (single) assignment line, the expr line
            # ending )$ (all 333 verified 2026-08-30; the generator
            # emits them so). A shape drift is a loud parse error,
            # not a guess.
            assert i + 2 < len(lines), f"{f} r{r}: cond truncated"
            body = lines[i + 1].rstrip()
            expr = lines[i + 2].rstrip()
            assert body.endswith(",") and expr.endswith(")$"), \
                f"{f} r{r}: cond shape moved (body={body[-40:]!r})"
            expr = expr[:-2].strip()
            assert not d0_comma(expr) and '"' not in expr, \
                f"{f} r{r}: cond expr has a depth-0 comma or a string"
            clauses = depth_split_and(expr)
            assert clauses, f"{f} r{r}: empty clause split"
            rules.append({
                "file": f, "n": r, "slots": slots,
                "assign": body[:-1].strip(),
                "clauses": clauses,
                "patcall": pattern_call(lines, f, r),
            })
    assert len(rules) == EXPECTED_RULES, \
        f"class-3 rule count moved: {len(rules)} != {EXPECTED_RULES}"
    return rules


def drill_text(rules):
    """The 333 _drill functions + the per-entry guarded drill
    statements, generated ONCE and spliced into every entry .mac (the
    plan's step 3). Each statement is its OWN top-level
    `if is(swept = 0) then (...)` block rather than one 1,332-element
    comma sequence: same evaluation (the guard is re-checked per
    rule), but small parse units per statement (this build's parser
    reflows and holds the whole sequence as one object; the split is
    the cheap insurance).

    The pattern call AND the cond evaluation are each errcatch'd and
    reported, mirroring %mr_dispatch's per-rule errcatch (a rule that
    crashes on a binding declines; the scan continues): CRASH = the
    pattern call crashed; BOOL = the match carries a boolean; CONDE =
    the cond crashed on a matched binding (the drill evaluates conds
    of ALL matched rules, production only those before the first
    fire — a crash here is a decline-in-production fact, not a
    harness bug); otherwise the clause vector."""
    funcs, stmts = [], []
    for ru in rules:
        tag = f"{ru['file']}_r{ru['n']}"
        n = len(ru["clauses"])
        locals_ = ru["slots"] + [f"c{j + 1}" for j in range(n)]
        cdefs = ", ".join(f"c{j + 1} : is({cl})"
                          for j, cl in enumerate(ru["clauses"]))
        fun = (f"_drill_{tag}(mm, x) := block([{', '.join(locals_)}],\n"
               f"  {ru['assign']},\n"
               f"  {cdefs},\n"
               f"  [{', '.join('c' + str(j + 1) for j in range(n))}])$")
        funcs.append(fun)
        stmts.append(
            f"if is(swept = 0) then (\n"
            f"  mm : errcatch({ru['patcall']}),\n"
            f"  if mm = [] then disp(concat(\"DR {tag} CRASH\"))\n"
            f"  else if part(mm, 1) # false then (\n"
            f"    if %mr_containsBoolean(part(mm, 1)) "
            f"then disp(concat(\"DR {tag} BOOL\"))\n"
            f"    else (mm2 : errcatch(_drill_{tag}(part(mm, 1), x)),\n"
            f"      if mm2 = [] then disp(concat(\"DR {tag} CONDE\"))\n"
            f"      else disp(concat(\"DR {tag} \", string(part(mm2, 1)))))\n"
            f"  )\n"
            f")$")
    return funcs, stmts


def entry_mac(f_text, var_text, funcs, stmts, d_max=1, drill=True):
    """One entry's batch file (the plan's step-2 template, with the
    measured build-quirk fixes from the module docstring, including
    the reader-desync filler buffers — see the module docstring).
    d_max bounds the sweep's direction loop (`for d : 0 thru d_max`);
    drill=False drops the triage drill (the 333 _drill functions +
    statements) for production-semantics cost runs (07). The defaults
    reproduce the committed 06 .mac files byte-for-byte."""
    # The driver's build_text filler (test/corpus_driver.py): throwaway
    # lines a mid-evaluation reader call can consume as a bogus
    # continuation without eating the real markers.
    filler = ["pos$"] * 40 + ["no$"] * 20
    L = list(funcs) if drill else []
    L += [
        f"mr_f: {f_text}$",
        f"x: {var_text}$",
        "rubi_verbose : true$",
        "mr_ans : rubi(mr_f, x)$",
        *filler,
        "disp(concat(\"MRFSTR \", string(mr_f)))$",
        "disp(concat(\"PROD \", if %mr_containsBoolean(mr_ans) then \"bool\" "
        "else if atom(mr_ans) then \"atom\" "
        "else string(op(mr_ans))))$",
        "mr_census : %mr_barefactors(mr_f)$",
        "disp(concat(\"P4CENSUS \", string(part(mr_census, 1)), \" \", "
        "string(part(mr_census, 2))))$",
        "if (not atom(mr_f)) and is(op(mr_f) = \"*\") then "
        "disp(concat(\"P4DIAG \", string(%mr_p4_diag(mr_f))))$",
        "swept : 0$",
        "if is(part(mr_census, 2) = false) and is(part(mr_census, 1) >= 2) "
        "then (\n"
        f"  for d : 0 thru {d_max} do\n"
        "    for i : 1 thru part(mr_census, 1) do (\n"
        "      disp(concat(\"P4SCAN \", string(d), \" \", string(i))),\n"
        "      mr_ans4 : %mr_p4_once(mr_f, x, mr_rule_table, 1, d, i),\n"
        "      if is(mr_ans4 # false) then (\n"
        "        disp(concat(\"P4FIRE \", string(d), \" \", string(i), \" \",\n"
        "                    if %mr_containsBoolean(mr_ans4) then \"bool\" "
        "else if atom(mr_ans4) then \"atom\" "
        "else string(op(mr_ans4)))),\n"
        "        swept : 1\n"
        "      )\n"
        "    )\n"
        ") else disp(concat(\"P4SKIP\"))$",
    ]
    if drill:
        L += stmts
    L.append("disp(concat(\"DONE\"))$")
    return "\n".join(L) + "\n"


def run_mac(mac_path, cap):
    """One fresh core subprocess on the batch file (the
    corpus_driver.maxima_run core path, verbatim)."""
    t0 = time.time()
    try:
        r = subprocess.run(
            [SBCL, "--tls-limit", "100000", "--core", CORE,
             "--noinform", "--very-quiet", "-b", mac_path],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, timeout=cap, cwd=ROOT)
        return r.stdout, False, time.time() - t0
    except subprocess.TimeoutExpired as e:
        out = e.stdout
        if isinstance(out, bytes):
            out = out.decode("utf-8", "replace")
        return out or "", True, cap


def parse_output(text):
    """Ordered event walk -> the per-entry facts. The subprocess stdout
    is INPUT ECHO + real output (the -b mode re-prints the batch lines
    as it parses them — see the committed calibration .out); the real
    lines are the disp/concat values, recognized by EXACT line shape
    (the echoed forms carry quotes / disp( prefixes / reflow
    indentation, none of which match the anchors below)."""
    # Long printed strings (the P4DIAG list) wrap at the print width:
    # the line ends in a backslash and the rest lands on the next
    # physical line (measured in the Task-1 calibration .out, e194).
    # Join before anchoring.
    raws = []
    for raw in text.splitlines():
        if raws and raws[-1].rstrip().endswith("\\"):
            raws[-1] = raws[-1].rstrip()[:-1] + raw
        else:
            raws.append(raw)
    # The verbose fired-on print is a 4-ARG print ("rubi: rule ", r,
    # " fired on ", f). When the integrand exceeds ~37 chars it wraps
    # at the ARGUMENT boundary: the fired-on line then carries NO
    # integrand and NO trailing backslash, and the integrand lands on
    # the next physical line, indented, backslash-free (measured
    # 2026-08-30, review round 2 — the backslash join above cannot see
    # it, and the fired event would capture an empty integrand, losing
    # the attribution). Integrand >70 chars instead wraps in the
    # backslash mode the join above catches. Fold the boundary mode:
    # an empty-capture fired-on line absorbs the immediately-following
    # non-anchor physical line (an integrand string cannot start with
    # an anchor prefix; a wrapped integrand is already one raws entry).
    _ANCHOR = ("PROD ", "P4CENSUS ", "P4DIAG ", "P4SKIP", "P4SCAN ",
               "P4FIRE ", "DR ", "MRFSTR ", "rubi: rule", "DONE")

    def _anchor(l):
        return l.strip().startswith(_ANCHOR)
    i, raws2 = 0, []
    while i < len(raws):
        raw = raws[i]
        s = raw.strip()
        if (s.startswith("rubi: rule") and "fired on" in s
                and i + 1 < len(raws) and not _anchor(raws[i + 1])):
            m2 = re.match(r"^rubi: rule\s+(\S+)\s+fired on\s*(.*)$", s)
            if m2 and not m2.group(2).strip():
                raw = raw.rstrip() + " " + raws[i + 1].strip()
                i += 1
        raws2.append(raw)
        i += 1
    raws = raws2
    ev = []   # (kind, payload) in output order
    for raw in raws:
        line = raw.strip()
        if line.startswith("PROD "):
            # string(op) prints +, -, /, * QUOTED in this build (Task-1
            # calibration); strip the one quote layer so the op compares
            # with the unquoted noun ops. The old '"'-in-line[:12] guard
            # that rejected these lines is wrong — no echo line can start
            # with bare "PROD " (the echo re-displays the disp(...) call).
            op = line[5:].strip()
            if len(op) >= 2 and op[0] == '"' and op[-1] == '"':
                op = op[1:-1]
            ev.append(("prod", op))
        elif line.startswith("P4CENSUS "):
            p = line[9:].split()
            if len(p) == 2 and p[0].isdigit():
                ev.append(("census", (int(p[0]), p[1] == "true")))
        elif line.startswith("P4DIAG "):
            ev.append(("diag", line[7:].strip()))
        elif line == "P4SKIP":
            ev.append(("skip", None))
        elif re.match(r"^P4SCAN [01] [0-9]+$", line):
            d, i = line.split()[1:]
            ev.append(("scan", (d, i)))
        elif line.startswith("P4FIRE "):
            p = line.split()
            ev.append(("fire", (p[1], p[2], p[3] if len(p) > 3 else "?")))
        elif line.startswith("DR "):
            ev.append(("dr", line[3:].strip()))
        elif line.startswith("MRFSTR "):
            ev.append(("mrfs", line[7:].strip()))
        elif line.startswith("rubi: rule") and "fired on" in line:
            m = re.match(r"^rubi: rule\s+(\S+)\s+fired on\s*(.*)$", line)
            ev.append(("fired", (m.group(1), m.group(2).strip())
                       if m else (line, "")))
        elif line == "DONE":
            ev.append(("done", None))
    info = {"ev": ev, "prod": None, "census": None, "diag": None,
            "skip": False, "fires": [], "dr": [], "done": False,
            "nscan": 0, "prod_fire": None, "scan_fires": [],
            "mrfs": None}
    for k, p in ev:
        if k == "prod" and info["prod"] is None:
            info["prod"] = p
        elif k == "census" and info["census"] is None:
            info["census"] = p
        elif k == "diag" and info["diag"] is None:
            info["diag"] = p
        elif k == "skip":
            info["skip"] = True
        elif k == "fire":
            info["fires"].append(p)
        elif k == "dr":
            info["dr"].append(p)
        elif k == "scan":
            info["nscan"] += 1
        elif k == "mrfs" and info["mrfs"] is None:
            info["mrfs"] = p
        elif k == "done":
            info["done"] = True
    # Attribution. The verbose print happens in %mr_dispatch AFTER
    # the rule body ran — the nested sub-integral fires the firing
    # rule's repl spawns print BEFORE the rule's own "fired on" line
    # (committed calibration .out, f2 block: four nested fires, then
    # the top-level 3_1_5_r27 on the full integrand, then P4FIRE).
    # The top-level fire of a call is therefore the LAST fired-on of
    # the FULL integrand (the MRFSTR identity, string() of the same
    # object) in the call's window. A 0-firing call (the fall-through
    # or a boolean-leak reject whose repl ran first) leaves only
    # orphaned nested fires on strict sub-integrals — the full-string
    # match excludes them; a re-dispatch of the full integrand cannot
    # re-fire (the %mr_seen guard falls through first).
    fires_by_di = {(d, i) for (d, i, _op) in info["fires"]}
    scans = [i for i, (k, _p) in enumerate(ev) if k == "scan"]
    first_scan = scans[0] if scans else len(ev)
    for i in range(first_scan):
        k, p = ev[i]
        if k == "fired" and p[1] == info["mrfs"]:
            info["prod_fire"] = p[0]   # last such line = top-level
    for si, s in enumerate(scans):
        hi = scans[si + 1] if si + 1 < len(scans) else len(ev)
        rule = None
        if ev[s][1] in fires_by_di:
            for j in range(s + 1, hi):
                k, p = ev[j]
                if k == "fired" and p[1] == info["mrfs"]:
                    rule = p[0]        # last such line = top-level
        info["scan_fires"].append((ev[s][1], rule))
    return info


def rule_family(name):
    """_mr_rule_3_1_5_r27 -> 3_1_5."""
    m = re.match(r"^_mr_rule_(\S+?)_r\d+$", name)
    return m.group(1) if m else name


def label_entry(info, require_noun):
    """The plan's step-5 logic with the noun refinement (module
    docstring). Returns (label, detail-string)."""
    prod = info["prod"]
    k, hp = (info["census"] or (0, False))
    # Sweep fires split on the ANSWER OP: a non-noun, non-boolean
    # answer is the rescue; a noun or bool answer is a fact
    # (sweep-noun=), never a label. The fire's rule comes from the
    # scan attribution keyed by (d, i) — a zip over the two lists
    # would mis-pair whenever an earlier scan did not fire.
    scanrule = {di: r for di, r in info["scan_fires"]}
    real, noun_fires = [], []
    for (d, i, op) in info["fires"]:
        r = scanrule.get((d, i))
        if not r:
            continue
        (real if op not in NONRESCUE else noun_fires).append((d, i, r))
    dr_lines = info["dr"]
    vecs = [d for d in dr_lines
            if not d.endswith(("CRASH", "BOOL", "CONDE"))]
    ncrash = sum(1 for d in dr_lines if d.endswith("CRASH"))
    nbool = sum(1 for d in dr_lines if d.endswith("BOOL"))
    nconde = sum(1 for d in dr_lines if d.endswith("CONDE"))
    npat = len(vecs)
    dr_facts = (" ".join(vecs)
                + f" CRASH={ncrash} BOOL={nbool} CONDE={nconde}")
    # A dead subprocess reports as subprocess-died, not as a record
    # drift: the DONE line is the harness's own liveness marker.
    if not info["done"]:
        return "0FIRE-POOL", f"drill={dr_facts} subprocess-died"
    if require_noun and (prod is None or prod not in NUONOUN):
        return "RECORD-MISMATCH", f"prod={prod}"
    if real:
        d, i, r = real[0]
        return "FIRE4", f"fire={d},{i},{r}"
    extra = ""
    if noun_fires:
        d, i, r = noun_fires[0]
        extra = f" sweep-noun={d},{i},{r}"
    if info["prod_fire"] is not None:
        return "D-NEST", f"rule={info['prod_fire']}{extra} drill={dr_facts}"
    if hp:
        diag = info["diag"] or "none"
        return "0FIRE-EXPL", f"drill=DIAG:{diag} {dr_facts}"
    extra2 = (" nonproduct" if k == 0 else "") + extra
    return "0FIRE-POOL", f"drill={dr_facts}{extra2}"


def mech_line(info, dt, rel, n, ln, require_noun, timed_out=False):
    label, detail = label_entry(info, require_noun)
    if timed_out:
        # The plan's step 4: a cap-exceeded entry is flagged `cap`
        # for manual follow-up (none are expected: deferred package
        # times are 0.7-27.6 s against the 60 s cap).
        detail = (detail + " cap").rstrip()
    vecs = [d for d in info["dr"]
            if not d.endswith(("CRASH", "BOOL", "CONDE"))]
    npat = len(vecs)
    return (f"MECH {label:16s} t={dt:6.1f}s {rel} e{n} L{ln} "
            f"npat={npat} swept={info['nscan']} {detail}").rstrip()


def gen_entries(workdir, deferred, flags, rules):
    """Write the per-entry .mac files + the LPT shard plan; return
    (entry list, plan). The entry index is the record-order position
    (0-based) — the deterministic pick the --smoke 10 reuses."""
    os.makedirs(os.path.join(workdir, "entries"), exist_ok=True)
    funcs, stmts = drill_text(rules)
    suite = suite_map()
    entries = []
    for idx, ((rel, n), t) in enumerate(deferred):
        assert rel in suite, f"{rel} not in the suite"
        ents, line_nos = suite[rel]
        assert n <= len(ents), f"{rel} e{n} out of range"
        els = split_elements(ents[n - 1][1:-1])
        assert len(els) in (4, 5), f"{rel} e{n}: bad entry shape"
        assert line_nos[n - 1] == ln_of((rel, n)), \
            f"{rel} e{n}: record line {ln_of((rel, n))} != suite line " \
            f"{line_nos[n - 1]}"
        f_text, var_text = els[0], els[1]
        p = os.path.join(workdir, "entries", f"{idx:04d}.mac")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(entry_mac(f_text, var_text, funcs, stmts))
        # The sidecar the shard runner reads for the MECH line's
        # identity (the .mac itself carries no key).
        jp = os.path.join(workdir, "entries", f"{idx:04d}.json")
        with open(jp, "w") as fh:
            json.dump({"rel": rel, "n": n, "ln": line_nos[n - 1]}, fh)
        entries.append({"idx": idx, "rel": rel, "n": n,
                        "ln": line_nos[n - 1], "t": t,
                        "flag": flags[(rel, n)], "mac": p})
    # LPT on the record's t= (the plan's step 4: sort desc, assign to
    # the currently-lightest shard).
    shards = [[] for _ in range(N_SHARDS)]
    loads = [0.0] * N_SHARDS
    for e in sorted(entries, key=lambda e: -e["t"]):
        j = min(range(N_SHARDS), key=lambda j: loads[j])
        shards[j].append(e["idx"])
        loads[j] += e["t"]
    plan = {str(j): {"idx": sh, "cost": round(c, 1)}
            for j, (sh, c) in enumerate(zip(shards, loads))}
    with open(os.path.join(workdir, "shard-plan.json"), "w") as fh:
        json.dump(plan, fh)
    return entries, plan


# ln_of: the record's L= (the merge asserts it equals the suite line
# number, so either source works; the record's keeps the MECH line's
# key identity with the package record).
_LN = {}


def ln_of(key):
    return _LN[key]


def load_ln():
    for line in open(PKG_RECORD, encoding="utf-8"):
        m = ENTRY_RE.match(line.rstrip("\n"))
        if m:
            _LN[(m["rel"], int(m["n"]))] = int(m["ln"])


# ---------------- calibration ----------------

CALI_F = {
    "f1": "x^3*(d+e*x)*(a+b*log(c*x^n))",
    "f2": "(d+e*x)*(a+b*log(c*x^n))",
    "f5": "(d+e*x)*(a+b*log(c*x^n))/x",
    # atom-top row (review round 1): the %mr_barefactors atom-top guard
    # regression — integrand x, atomic top. Measured: 1_1_1_1_r2 fires
    # on the degenerate x^1 bind (PROD non-noun); the row's gate is the
    # census line, not the PROD op.
    "atom": "x",
}
# 3.1.5 e186-e197 (the 12 F_-domain corpus texts; the suite file is
# the source — verbatim by construction).
CALI_E_FILE = "3.1.5 u (a+b log(c x^n))^p.mac"
CALI_E_RANGE = range(186, 198)


def calibrate(workdir, verbose=True):
    """Run the Task-1 16-entry set through this probe's own per-entry
    measurement and assert the Task-1 table. Returns the section text
    (the merge embeds it); exits 1 on any row mismatch."""
    suite = suite_map()
    rules = parse_class3_rules()
    funcs, stmts = drill_text(rules)
    os.makedirs(os.path.join(workdir, "cali"), exist_ok=True)
    rows = []
    checks = []
    ents = suite[SECTION + "/" + CALI_E_FILE][0]
    for n in CALI_E_RANGE:
        els = split_elements(ents[n - 1][1:-1])
        CALI_F[f"e{n}"] = els[0]
    for name in (["f2", "f1", "f5"] + [f"e{n}" for n in CALI_E_RANGE]
                + ["atom"]):
        f_text = CALI_F[name]
        p = os.path.join(workdir, "cali", name + ".mac")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(entry_mac(f_text, "x", funcs, stmts))
        out, timed_out, dt = run_mac(p, ENTRY_CAP)
        info = parse_output(out)
        label, detail = label_entry(info, require_noun=False)
        row = {"name": name, "label": label, "detail": detail,
               "dt": dt, "info": info, "timed_out": timed_out}
        rows.append(row)
        if verbose:
            print(f"  {name:5s} {label:16s} t={dt:6.1f}s  {detail}")
    # The Task-1 expected table (the calibration .out header is the
    # committed record; a row miss is a harness failure).
    by_name = {r["name"]: r for r in rows}

    def chk(name, cond, what):
        ok = cond(by_name[name])
        checks.append((name, what, ok))
        return ok

    def real_fires(info):
        """(d, i, rule) of the sweep fires whose ANSWER is non-noun,
        in scan order (a noun answer is not a rescue — the refinement
        in the module docstring)."""
        scanrule = {di: r for di, r in info["scan_fires"]}
        return [(d, i, scanrule[(d, i)]) for (d, i, op) in info["fires"]
                if op not in NUONOUN and scanrule.get((d, i))]

    chk("f2", lambda r: r["label"] == "FIRE4"
        and r["info"]["prod"] not in NUONOUN
        and real_fires(r["info"])
        and rule_family(real_fires(r["info"])[0][2]) == "3_1_5",
        "FIRE4, non-noun PROD, first fire in the 3_1_5 family")
    chk("f1", lambda r: r["label"] == "0FIRE-EXPL"
        and "pick-fwd=x^3" in (r["info"]["diag"] or "")
        and "pick-rev=x^3" in (r["info"]["diag"] or ""),
        "0FIRE-EXPL, P4DIAG pick-fwd=pick-rev=x^3")
    chk("f5", lambda r: r["label"] == "0FIRE-POOL"
        and r["info"]["census"] == (0, False),
        "0FIRE-POOL nonproduct (census 0,false)")
    for n in range(186, 194):
        nm = f"e{n}"
        chk(nm, lambda r: r["label"] == "FIRE4"
            and r["info"]["prod_fire"] is not None
            and rule_family(r["info"]["prod_fire"]) == "3_5",
            "FIRE4, production first fire in 3_5")
    for n in range(194, 198):
        nm = f"e{n}"
        chk(nm, lambda r: r["label"] == "0FIRE-EXPL"
            and "^2" in (r["info"]["diag"] or ""),
            "0FIRE-EXPL, P4DIAG pick = the F(a*x)^2 factor")
    chk("atom", lambda r: r["info"]["done"]
        and r["info"]["census"] == (0, False)
        and r["info"]["skip"]
        and r["info"]["diag"] is None,
        "atom-top guard: no crash, census 0,false, P4SKIP, no P4DIAG")
    # Fire-attribution proofs (review round 2): the 4-arg verbose print
    # wraps at the ARGUMENT boundary for a >37-char integrand — the
    # fired-on line carries no integrand and no backslash; the
    # integrand is the next physical line, indented, backslash-free.
    # (a) SYNTHETIC parse test: fabricate the wrapped block in both
    # windows and assert the fold attributes rule + integrand identity.
    achecks = []
    longf = "x*(a+b*log(c*x^n))*log(d*(e+f*x^2)^m)*log(g*(h+i*x)^k)"
    synth = "\n".join([
        "rubi: rule  _mr_rule_3_1_5_r27  fired on  ",
        "         " + longf,
        "MRFSTR " + longf,
        "PROD unintegrable",
        "P4CENSUS 2 true",
        "P4SCAN 0 1",
        "rubi: rule  _mr_rule_3_5_r43  fired on  ",
        "         " + longf,
        "P4FIRE 0 1 /",
        "P4SCAN 0 2",
        "P4SKIP",
        "DONE",
    ]) + "\n"
    si = parse_output(synth)
    achecks.append(("synth-wrap",
                    "fold attributes prod_fire + scan_fires from the "
                    "wrapped fired-on (folded integrand == MRFSTR)",
                    si["mrfs"] == longf
                    and si["prod_fire"] == "_mr_rule_3_1_5_r27"
                    and si["scan_fires"]
                    == [(("0", "1"), "_mr_rule_3_5_r43"),
                        (("0", "2"), None)]))
    # (b) real long-integrand smoke: the first five deferred entries
    # (record order) whose parsed integrand text exceeds 38 chars —
    # every fired event must carry a NON-EMPTY integrand, and a
    # full-integrand fire (integrand == MRFSTR) must be attributed.
    deferred, _fl = deferred_set()
    longsmoke = []
    for (rel, n) in [k for k, _t in deferred]:
        els = split_elements(suite[rel][0][n - 1][1:-1])
        if len(els[0]) > 38:
            longsmoke.append((rel, n, els[0]))
        if len(longsmoke) >= 5:
            break
    for (rel, n, f) in longsmoke:
        base = os.path.basename(rel)
        p = os.path.join(workdir, "cali", f"long-{base[:10]}-{n}.mac")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(entry_mac(f, "x", funcs, stmts))
        out, _to, dt = run_mac(p, ENTRY_CAP)
        li = parse_output(out)
        fired = [pl for (k2, pl) in li["ev"] if k2 == "fired"]
        nfull = sum(1 for pl in fired if pl[1] == li["mrfs"])
        achecks.append((f"long-{base[:10]}-{n}",
                        f"long-integrand smoke (len={len(f)}): "
                        "every fired event non-empty integrand; "
                        "full-integrand fire attributed",
                        li["done"]
                        and all(pl[1] for pl in fired)
                        and (nfull == 0
                             or li["prod_fire"] is not None
                             or any(r for (_di, r) in li["scan_fires"]))))
        if verbose:
            print(f"  long-{base[:10]}-{n} fired={len(fired)} "
                  f"full={nfull} t={dt:6.1f}s")
    bad = [(n, w) for n, w, ok in checks if not ok]
    bad += [(n, w) for n, w, ok in achecks if not ok]
    section = ["=== calibration re-run (the probe's own measurement of the "
               "Task-1 16-entry set) ==="]
    for r in rows:
        section.append(f"{r['name']:5s} {r['label']:16s} t={r['dt']:6.1f}s  "
                       f"{r['detail']}")
    section.append("")
    section.append("=== fire-attribution proofs (review round 2) ===")
    for n, w, ok in achecks:
        section.append(f"  {n:22s} {'OK' if ok else 'FAIL'} — {w}")
    if bad:
        section.append(f"CALIBRATION FAIL: {len(bad)} row(s) off:")
        for n, w in bad:
            section.append(f"  {n}: expected {w}")
        section.append("The harness misclassifies a calibration case — "
                       "it does not ship (stop, investigate, fix).")
        print("\n".join(section))
        raise SystemExit(1)
    section.append(f"CALIBRATION OK: {len(checks)}/{len(checks)} Task-1 "
                   f"rows + {len(achecks)}/{len(achecks)} attribution "
                   "proofs")
    if verbose:
        print("\n".join(section))
    return "\n".join(section)


# ---------------- gen / smoke / shard / launch / merge ----------------

def do_gen(workdir, smoke=None):
    load_ln()
    deferred, flags = deferred_set()
    rules = parse_class3_rules()
    entries, plan = gen_entries(workdir, deferred, flags, rules)
    print(f"gen: {len(entries)} deferred entries (788 target-flagged: "
          + "/".join(f"{c} {flags_c}" for c, flags_c in
                     sorted(Counter(e['flag'] for e in entries
                                   if e['flag'] in FLAG_CLASSES).items()))
          + f"), {len(rules)} rules, {N_SHARDS} shards")
    for j in range(N_SHARDS):
        sh = plan[str(j)]
        print(f"  shard{j:02d}  entries={len(sh['idx']):4d}  "
              f"cost~{sh['cost']:6.0f}s (record t= sum)")
    if smoke:
        for e in entries[:smoke]:
            out, timed_out, dt = run_mac(e["mac"], ENTRY_CAP)
            info = parse_output(out)
            line = mech_line(info, dt, e["rel"], e["n"], e["ln"],
                             require_noun=True, timed_out=timed_out)
            print(line)
            if timed_out:
                print(f"  (shard smoke: {e['idx']} hit the 60 s cap)")


def do_shard(workdir, k):
    plan = json.load(open(os.path.join(workdir, "shard-plan.json")))
    sh = plan[str(k)]
    outp = os.path.join(workdir, f"shard-{k:02d}.out")
    with open(outp, "w") as of:
        for idx in sh["idx"]:
            mac = os.path.join(workdir, "entries", f"{idx:04d}.mac")
            meta = json.load(open(os.path.join(workdir, "entries",
                                               f"{idx:04d}.json")))
            out, timed_out, dt = run_mac(mac, ENTRY_CAP)
            info = parse_output(out)
            line = mech_line(info, dt, meta["rel"], meta["n"], meta["ln"],
                             require_noun=True, timed_out=timed_out)
            of.write(line + "\n")
            of.flush()
            print(line, flush=True)


def do_launch(workdir):
    plan = json.load(open(os.path.join(workdir, "shard-plan.json")))
    pidf = os.path.join(workdir, "shard-pids")
    with open(pidf, "w") as pf:
        for j in range(N_SHARDS):
            cmd = [sys.executable,
                   os.path.join(ROOT, "probes", "corpus", SLUG + ".py"),
                   "--shard", str(j), "--workdir", workdir]
            p = subprocess.Popen(cmd, cwd=ROOT,
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL,
                                 start_new_session=True)
            pf.write(f"shard{j:02d} {p.pid}\n")
    print(f"launched {N_SHARDS} shards; pids in {pidf}")
    print(f"merge when the pid file is clean:")
    print(f"  python3 probes/corpus/{SLUG}.py --merge {workdir}")


def build_info_lines():
    r = subprocess.run(
        ["maxima", "--very-quiet", "--batch-string", "disp(build_info());"],
        capture_output=True, text=True, timeout=120, cwd=ROOT)
    out = []
    for line in r.stdout.splitlines():
        line = line.strip()
        if line.startswith(("Maxima", "Lisp ", "Host ")):
            out.append(f"maxima: {line}")
    return out


def do_merge(workdir):
    deferred, flags = deferred_set()
    expected = {(rel, n) for (rel, n), _t in deferred}
    shard_files = sorted(glob.glob(os.path.join(workdir, "shard-*.out")))
    assert shard_files, f"no shard .out files under {workdir}"
    # rel is ANCHORED against the known suite files (the plan's greedy
    # (.*) rel capture would silently mis-key if a future detail token
    # ever formed " e<d> L<d> npat=" — review round 2). Longest file
    # names first so the alternation matches the full name.
    files = sorted({k[0] for k in expected}, key=len, reverse=True)
    mech_re = re.compile(
        r"^MECH (\S+)\s+t=\s*([\d.]+)s\s+(" +
        "|".join(re.escape(f) for f in files) +
        r") e(\d+) L(\d+)\s+npat=(\d+) swept=(\d+)\s+(.*)$")
    seen, dupes = {}, 0
    for path in shard_files:
        for line in open(path, encoding="utf-8"):
            line = line.rstrip("\n")
            m = mech_re.match(line)
            if not m:
                continue
            key = (m.group(3), int(m.group(4)))
            if key in seen:
                dupes += 1
            seen[key] = line
    missing = expected - set(seen)
    extra = set(seen) - expected
    assert not missing and not extra and not dupes, \
        f"INCOMPLETE: missing={len(missing)} extra={len(extra)} " \
        f"dupes={dupes}" + (f"\n  missing {sorted(missing)[:10]}"
                            if missing else "")
    # The calibration gate (run now, embedded below; a mismatch raises).
    calib = calibrate(workdir, verbose=False)
    # Distribution.
    by_label = {}
    for (rel, n), line in seen.items():
        label = line.split()[1]
        by_label.setdefault(label, []).append((rel, n))
    flag_groups = ["verified", "expected", "unverified",
                   "no-answer", "timeout", "error"]
    cross = {}
    for label, keys in by_label.items():
        row = Counter(flags[k] for k in keys)
        cross[label] = row
    # Sweep cost (swept entries: dt_total - record t=).
    costs = []
    pkg_items, _d = load_record(PKG_RECORD)
    t_of = {k: t for k, _c, t in pkg_items}
    for (rel, n), line in seen.items():
        m = re.search(r"swept=(\d+)\s", line)
        mt = re.match(r"^MECH \S+\s+t=\s*([\d.]+)s", line)
        if m and mt and int(m.group(1)) > 0:
            costs.append(float(mt.group(1)) - t_of[(rel, n)])
    costs.sort()

    def pct(p):
        if not costs:
            return 0.0
        i = min(len(costs) - 1, int(len(costs) * p))
        return costs[i]

    lines = [
        f"=== class-3 deferred-mechanisms triage "
        f"({SLUG}, full run) ===",
        f"merge date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
    ] + build_info_lines() + [
        f"core fingerprint: {driver._core_fingerprint()} "
        f"(rules core, test/mr_rules.core)",
        f"package record: test/corpus_class3.out "
        f"({EXPECTED_DEFERRED} deferred)",
        f"baseline record: test/corpus_class3.baseline.out "
        f"({EXPECTED_FLAGGED} target-flagged)",
        f"entries: {len(seen)}  ({len(shard_files)} shards merged)",
        "",
    ]
    for rel in sorted({k[0] for k in expected}):
        for n in sorted(k[1] for k in expected if k[0] == rel):
            lines.append(seen[(rel, n)])
    lines += ["", "=== distribution ==="]
    lines.append(f"{'label':16s} {'total':>6s}  "
                 + "  ".join(f"{g:>9s}" for g in flag_groups))
    for label in sorted(cross, key=lambda l: -sum(cross[l].values())):
        row = cross[label]
        lines.append(f"{label:16s} {sum(row.values()):6d}  "
                     + "  ".join(f"{row.get(g, 0):9d}" for g in flag_groups))
    flag_tot = sum(cross.values(), Counter())
    lines.append(f"{'total':16s} {sum(flag_tot.values()):6d}  "
                 + "  ".join(f"{flag_tot.get(g, 0):9d}" for g in flag_groups))
    lines += ["", "--- label x file x target-flag "
                 "(the 788/329 cross-tab; the Phase-2 prioritization "
                 "input — not recoverable from the two 2-way "
                 "projections above; review round 2) ---"]
    # per file, per flag group: the label counts (the 3-way table).
    file_flag_label = {}
    for (rel, n), line in seen.items():
        label = line.split()[1]
        file_flag_label.setdefault(rel, {}) \
            .setdefault(flags[(rel, n)], Counter())[label] += 1
    for rel in sorted(file_flag_label):
        ff = file_flag_label[rel]
        lines.append(f"{rel}  "
                     f"({sum(sum(c.values()) for c in ff.values())} deferred)")
        for g in flag_groups:
            if g in ff:
                row = ff[g]
                cells = "  ".join(f"{l}={row[l]}"
                                  for l in sorted(row,
                                                  key=lambda l: (-row[l], l)))
                lines.append(f"  {g:10s} ({sum(row.values()):3d}): {cells}")
    lines += [
        "",
        "--- sweep cost (swept entries: dt_total - record t=, s) ---",
        (f"n={len(costs)}  mean={sum(costs) / len(costs):6.2f}  "
         f"p50={pct(0.50):6.2f}  p95={pct(0.95):6.2f}  max={costs[-1]:6.2f}"
         if costs else "n=0"),
        "",
    ]
    lines.append(calib)
    lines.append("")
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    mismatch = sum(1 for l in lines if l.startswith("MECH RECORD-MISMATCH"))
    assert mismatch == 0, f"{mismatch} RECORD-MISMATCH entries — drift"
    print(f"OK: {len(seen)}/{len(expected)} entries, no dupes/missing/extra")
    for label in sorted(cross, key=lambda l: -sum(cross[l].values())):
        row = cross[label]
        print(f"  {label:16s} {sum(row.values()):5d}")
    print(f"wrote {OUT}")


def main():
    ap = argparse.ArgumentParser(
        description="class-3 deferred-mechanisms triage probe")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--gen", action="store_true",
                   help="parse records + suite, emit per-entry .mac + "
                        "shard plan (asserts 1033/788)")
    g.add_argument("--shard", type=int, metavar="K",
                   help="run shard K sequentially")
    g.add_argument("--launch", action="store_true",
                   help="Popen the 24 shard processes")
    g.add_argument("--merge", nargs="?", const=DEFAULT_WORKDIR,
                   metavar="WORKDIR",
                   help="merge the shard .outs -> the committed .out "
                        "(runs the calibration gate)")
    g.add_argument("--calibrate", action="store_true",
                   help="run the 16-entry Task-1 table through this "
                        "probe's own measurement and assert it")
    ap.add_argument("--smoke", type=int, metavar="N",
                    help="with --gen: run the first N deferred entries "
                         "(record order) serially and print the MECH lines")
    ap.add_argument("--workdir", default=DEFAULT_WORKDIR)
    a = ap.parse_args()
    load_ln()
    if a.gen:
        do_gen(a.workdir, smoke=a.smoke)
    elif a.shard is not None:
        do_shard(a.workdir, a.shard)
    elif a.launch:
        do_launch(a.workdir)
    elif a.merge is not None:
        do_merge(a.merge)
    elif a.calibrate:
        calibrate(a.workdir)


if __name__ == "__main__":
    main()
