# Milestone 2 — Class-2 (Exponentials) Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generalize the milestone-1 pipeline (census → translation table →
generator → utils ports → loader → rules core → corpus driver/launcher →
A/B acceptance) so that porting a Rubi class is a runbook, and prove it
end-to-end on class 2 (exponentials): 125 rules, 965 corpus entries,
measured against the T3 `integrate` baseline with the class-1 accepted
record untouched.

**Architecture:** The same option-D architecture as milestone 1 — one
generated `.mac` per Rubi `.m` file, a flat ordered `mr_rule_table`,
defmatch matching at Maxima level, the saved rules core, one fresh
subprocess per corpus integral, verification by differentiation. Class 2
adds: (a) a `--class` parameter through the generator/launcher/merger
chain, (b) a two-sided answer-head normalization in the driver (the corpus
carries Rubi-notation heads `GAMMA(`/`Ei(`; the package emits native
`gamma_incomplete(`/`expintegral_ei(`), (c) a new utils cluster (~25
`%mr_` functions) including one upstream gap — `PowerOfLinearQ` & co. are
called by the pinned Rubi 4 class-2 rule files but **defined nowhere in
the clone** (measured) — ported from the call-site contract with
decline-safe semantics, (d) a Mathematica `Part` (`u[[i]]`) handler in the
generator parser (two class-2 rules use it; the class-1 parser never met
it).

**Tech Stack:** Maxima 5.50.0 / SBCL 2.6.7 (installed build), Python 3
(generator, census, driver, launcher), the pinned reference clones under
`reference/` (gitignored). All work happens in the worktree
`.worktrees/milestone-2` on branch `milestone-2`.

## Global Constraints

These apply to every task.

1. **Build stamp.** All measurements run on the installed Maxima 5.50.0
   (build date 2026-08-20 21:36:22) on SBCL 2.6.7. Stamp every committed
   record with `build_info()` (`version` is unbound in this build — use
   the `Maxima`/`Lisp`/`Host` lines). Do not pin to 5.50; on upgrade,
   re-measure.
2. **TLS flag.** Any maxima process that loads rule files runs with
   `-X "--tls-limit 100000"` (two argv tokens). Plain processes may load
   at most a handful of rules (~384 slots measured for 40 rules).
3. **House rules** (milestone-1 plan, carried over): booleans through
   `is(…)`; no value-position comparisons (`2 > 1` stays a noun); guards
   are value-carrying `if … then A else B`; no `filter` (use `map` /
   explicit recursion); fresh per-rule capture names, never killed at
   runtime; internal names carry `%mr_`, shims never take the native
   name; the package never prompts; noun discipline (the fall-through
   `integrate(f, x)` noun vs the `mr_int` recursion call vs the
   `unintegrable[f, x]` corpus marker are never conflated); batch-parser
   traps (`rules` is protected; no quoted symbol after a comma nested
   inside another call's arguments; `;`/`$` terminate, a trailing `,`
   continues).
4. **Byte-identity gate.** After ANY change to `generator/generate_rules.py`
   or `generator/translation_table.py`, regenerate class 1 and
   `git diff` must be empty (all 73 class-1 `.mac` files byte-identical).
   The class-1 accepted record (19,731/25,697, core fingerprint
   `f1f0611f…`) depends on these bytes.
5. **Class 1 is not re-run.** Per the pilot design, class-1 records are
   not re-run. The one shared-code change that could touch class-1
   behavior is the driver's answer-head normalization: it is a measured
   no-op on the class-1 section (0 renamable-head occurrences — Task 1
   probe) and Task 8 additionally spot-checks 50 class-1 entries against
   the last merged record. Every shared-code change is flagged in the
   ledger.
6. **The 30 s per-entry cap STAYS** (user decision 2026-08-27). The
   `timeout` class of the merged class-2 record is re-run at 300 s
   (standing re-check protocol) before acceptance is declared.
7. **Git.** Default branch `master`; no remote configured — never
   `git push`; no `Co-Authored-By` trailers; one commit per task step
   group; logical units.
8. **Measured-claims discipline.** Every non-trivial claim in a `docs/`
   file cites a committed, re-runnable probe under `probes/`.
9. **Reading protocol.** Every Layer A run ends with
   `Results: <n> passed, <m> failed` — read that line; a mid-run death
   prints no Results line and is itself a failure. Every corpus run's
   completeness is asserted against the section entry count.
10. **Spec.** The design this plan implements is
    `docs/superpowers/specs/2026-08-28-milestone-2-class2-pilot-design.md`
    (committed on `milestone-2` as `ff814e9`).

## Measured basis (2026-08-28, 5.50.0 / SBCL 2.6.7)

- **Class-2 rule set:** 3 files, **125 rules** — `2.1 (c+d x)^m
  (a+b (F^(g (e+f x)))^n)^p.m` = 14, `2.2 (c+d x)^m (F^(g (e+f x)))^n
  (a+b (F^(g (e+f x)))^n)^p.m` = 4, `2.3 Miscellaneous exponentials.m` =
  107 (`rule_runs` over the pinned clone `61e9c18e…`).
- **Class-2 corpus:** 3 files, **965 entries** — 2.1 = 98, 2.2 = 93,
  2.3 = 774.
- **New tokens** (class-1 census parser): `TrueQ` 9, `PowerOfLinearQ` 6,
  `Exponent` 7, `PowerOfLinearMatchQ` 3, `NormalizePowerOfLinear` 6,
  `FunctionOfExponentialQ` 1, `FunctionExpand` 1, `FunctionOfExponential`
  1, `FunctionOfExponentialFunction` 1, `NormalizeIntegrand` 1, `PowerQ`
  2, `FullSimplify` 3, `Erf` 3, `Erfi` 1, `ExpIntegralEi` 3, `Gamma` 5
  (all 2-arg — upper incomplete), `Exp` 2. Rule files also use
  `Module[{…}]` (2), `With[{…}]` (18), `u[[i]]` Part (6 sites, 2 rules),
  `Denominator`/`Numerator` (11/3 — already in the table),
  `$UseGamma` (inside the 9 `TrueQ` sites).
- **Upstream gap (measured 2026-08-28):** `PowerOfLinearQ`,
  `PowerOfLinearMatchQ`, `NormalizePowerOfLinear` are **defined nowhere**
  in the pinned clone (grep of all `.m`) nor in the Rubi-5 stub
  (`Rubi-5.m`, 0 matches). `$UseGamma` is defined nowhere in `Rubi.m`
  either; the class-2 corpus file headers state the optimal
  antiderivatives assume `$UseGamma = false`.
- **Generator gap (measured 2026-08-28):** the class-1 parser has no
  `Part` (`[[…]]`) handling — `translate("Not[TrueQ[$UseGamma]]")`
  passes `$UseGamma` through verbatim (invalid Maxima: `$` terminates a
  line in the Maxima reader), and `head_args("uu[[2]]")` parses it as
  head `uu` with arg `[2]`, which the emit path rejects.
- **Maxima natives (probed 2026-08-28 in the installed build):**
  `gamma_incomplete(a, z)` — 2-arg, **upper** incomplete gamma:
  `diff(gamma_incomplete(2.3, z), z) = -%e^(-z) z^1.3` and the numeric
  identity closed (Mathematica `Gamma[a, z]` convention — the corpus's
  `GAMMA(a, z)` maps straight over); does NOT auto-expand for integer
  `a` (noun survives; `diff` works). `expintegral_ei(z)`:
  `diff = %e^z/z` ✓. `erf`/`erfi` native, correct `diff` ✓ (the corpus
  already uses lowercase `erf(`/`erfi(`). `hypergeometric([], [b], z)`
  differentiates to `hypergeometric([], [b+1], z)/b` (relevant only to
  the follow-up classes — the class-2 corpus `F0(` is a **free function
  symbol**, not a 0F1 hypergeometric: all 14 occurrences are 1-arg
  `F0(x)`-style). `exp` native ✓.
- **Naming trap (confirmed 2026-08-28):** the public names carry
  underscores (`expintegral_ei`, `lambert_w`, `gamma_incomplete`);
  `describe(name, exact)` in the running build is the arbiter.
- **Class-2 corpus answer heads (probed 2026-08-28):** `GAMMA(` 191
  (all 2-arg), `Ei(` 237 (all 1-arg), `erf(` 10, `erfi(` 175, `F0(` 14
  (free function), `%e^` 1438, `exp(` 0, `E(` 0 — so the driver's
  normalization for class 2 is exactly two rewrites: `GAMMA(` →
  `gamma_incomplete(`, `Ei(` → `expintegral_ei(`.
- **Class-1 no-op proof (probed 2026-08-28):** 0 occurrences of every
  renamable head (`Ei(`, `E1(`, `E(`, `GAMMA(`, `ProductLog(`,
  `FresnelC(`, `FresnelS(`, `Chi(`, `Shi(`, `Si(`, `Ci(`, `Li(`, `Erf(`,
  `Erfi(`, `Erfc(`, `expintegral*`, `gamma_incomplete(`, `lambert_w(`) in
  `1 Algebraic functions/*.mac`.
- **Already ported (milestone-1 utils, reused):** `%mr_degree` (general
  polynomial degree — the `Exponent` port), `%mr_sumQ`, `%mr_linearQ`,
  `%mr_quadraticQ`, `%mr_polynomialQ`, `%mr_binomialQ`, `%mr_trinomialQ`,
  `%mr_binomialMatchQ`, `%mr_trinomialMatchQ`, `%mr_linearMatchQ`,
  `%mr_monomialQ`, `%mr_expandToSum`, `%mr_expandIntegrand`, `%mr_simp`
  (2-arg), `%mr_rationalQ`, `%mr_fractionQ`, `%mr_coeff`, `%mr_eqQ`,
  `%mr_neQ`, `%mr_negQ`, `%mr_posQ`, `%mr_leafCount`, `%mr_cancel`,
  `%mr_together`, `%mr_subst`, `%mr_inverseFunctionQ`, `%mr_simplerQ`,
  `%mr_int`, `mr_sum` (4-arg, concretizes numeric bounds —
  `maxima_rubi_utils.mac:53`), `mr_unintegrable`. `member()` in this
  build returns a **boolean** (`maxima_rubi_utils.mac:758` note).
- **Class-1 census convention:** `probes/translation/01-class1-syntax-census.{py,out,run}` —
  committed output + re-run command. Class 2 follows as `03-class2-*`
  (02 is taken by the support-surface probe). The census token regex
  (`\b[A-Z][A-Za-z0-9]*` before `[`) does NOT count `$`-globals —
  `$UseGamma` is a variable, not a head token.

## File structure

Created:
- `generator/generate_rules.py` — the generalized generator (`--class 1|2`).
- `probes/translation/03-class2-syntax-census.out` / `.run` — class-2 census record.
- `probes/corpus/02-class2-answer-heads.py` / `.out` / `.run` — corpus answer-head census.
- `probes/load_wall/probe-class2-load.mac` / `.out` / `.run` — full table load under the TLS flag.
- `test/corpus_driver.py` — the generalized corpus driver (section via the
  existing filter positional; class-1+class-2 fingerprint; answer-head
  normalization).
- `test/launch_class_shards.py` — the generalized shard launcher.
- `test/merge_class_shards.py` — the generalized shard merger.
- `test/test_head_rewrites.py` — pure-Python unit test for the head rewrites.
- `rules/class2/2_1.mac`, `2_2.mac`, `2_3.mac` — generated (do not edit).
- `docs/corpus-class2-baseline-uplift.md`, `docs/class-porting.md` — Task 11.

Modified:
- `generator/translation_table.py` — class-2 RENAME entries.
- `generator/generate_class1.py` — becomes a shim over `generate_rules.py`.
- `probes/translation/01-class1-syntax-census.py` — class-prefix argv (default `"1 "`).
- `probes/corpus/probe-integrate-sample.py` — section argv (default class 1).
- `maxima_rubi_utils.mac` — the class-2 predicate cluster + `mr_use_gamma_flag`.
- `maxima_rubi.mac` — `mr_load_all()` (class 1 + class 2, LoadRules order).
- `test/build_rules_core.sh` — fingerprint over class-1 + class-2 files; image runs `mr_load_all()`.
- `test/corpus_class1_driver.py`, `test/launch_class1_shards.py`,
  `test/merge_class1_shards.py` — become shims over the generalized versions.
- `test/wait_and_merge.sh` — takes the pids file + merge script as arguments (class-1 defaults).
- `test_maxima_rubi.mac` — class-2 test blocks.
- `todo/TODO.md` — milestone-2 status (Task 11).

---

### Task 1: Class-2 census + corpus answer-head probes (committed evidence)

**Files:**
- Modify: `probes/translation/01-class1-syntax-census.py`
- Create: `probes/translation/03-class2-syntax-census.out`, `probes/translation/03-class2-syntax-census.run`
- Create: `probes/corpus/02-class2-answer-heads.py`, `.out`, `.run`

**Interfaces:**
- Produces: the class-2 token census (the authoritative closure for Task 3's table) and the answer-head counts that Task 8's normalization rewrites are built from.

- [ ] **Step 1: Parameterize the census script (class prefix, default `"1 "`)**

In `probes/translation/01-class1-syntax-census.py`, `main()` currently
reads `root = Path(sys.argv[1] …)` and filters with
`parts[0].startswith("1 ")`. Add the class prefix as `argv[2]`:

```python
def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "reference/rubi")
    classp = sys.argv[2] if len(sys.argv) > 2 else "1 "
    rubi_m = (root / "Rubi" / "Rubi.m").read_text()
    rule_dir = root / "Rubi" / "IntegrationRules"

    loaded = []
    for parts, _gated in parse_load_rules(rubi_m):
        if parts[0].startswith("$") or not parts[0].startswith(classp):
            continue
```

(Only the two marked lines change; the gated flag stays ignored — class 1
selects the non-gated `"1 "` files, class 2 the gated `"2 "` files, and
the prefix is the selector either way.)

- [ ] **Step 2: Run the class-1 census unchanged and confirm the gate**

Run: `python3 probes/translation/01-class1-syntax-census.py reference/rubi > /tmp/c1.out`
Expected: `/tmp/c1.out` byte-identical to `probes/translation/01-class1-syntax-census.out`
(`cmp /tmp/c1.out probes/translation/01-class1-syntax-census.out` — no output).

_Post-review correction (2026-08-28, verified): the literal byte gate was
structurally unattainable as written — the committed .out carries the
`.run`'s dated header line (which the bare python run does not print) and
the pre-fix script hash-randomized equal-count tie order
(PYTHONHASHSEED). The standing substantive gate, verified on the
generalized script: the `.run` re-capture is deterministic (deterministic
tie sort + dated header), so a same-day `sh …-census.run` reproduces the
committed .out byte-for-byte, and the class-1 headline (67 files / 2,710
rules / 2,709 with condition) and the token set are unchanged by the
generalization (line multiset identical, verified 2026-08-28)._

- [ ] **Step 3: Run and commit the class-2 census**

Run:
```
python3 probes/translation/01-class1-syntax-census.py reference/rubi "2 " > probes/translation/03-class2-syntax-census.out
```
Write `probes/translation/03-class2-syntax-census.run`:
```sh
#!/bin/sh
# Class-2 syntax census (the token closure for the class-2 translation
# table). Re-run from the worktree root; stamp before comparing.
cd "$(dirname "$0")/../.." || exit 1
echo "maxima $(maxima --version 2>&1 | head -1)  date $(date -u '+%F %T UTC')"
python3 probes/translation/01-class1-syntax-census.py reference/rubi "2 "
```
Expected: the token table lists exactly the new tokens of the Measured
basis (`TrueQ 9, PowerOfLinearQ 6, Exponent 7, PowerOfLinearMatchQ 3,
NormalizePowerOfLinear 6, FunctionOfExponentialQ 1, FunctionExpand 1,
FunctionOfExponential 1, FunctionOfExponentialFunction 1,
NormalizeIntegrand 1, PowerQ 2, FullSimplify 3, Erf 3, Erfi 1,
ExpIntegralEi 3, Gamma 5, Exp 2`) plus the class-1-shared tokens. Any
token NOT in that union is a plan defect — stop and reconcile before
Task 3.

- [ ] **Step 4: Write the corpus answer-head probe**

Create `probes/corpus/02-class2-answer-heads.py`:

```python
#!/usr/bin/env python3
"""Class-2 corpus answer-head census: which Rubi-notation special-function
heads the 2 Exponentials section carries, with arity, so the driver's
answer normalization (test/corpus_driver.py HEAD_REWRITES) is built from
measured need. Commits the counts the rewrites are justified by."""
import glob
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SECTION = sys.argv[1] if len(sys.argv) > 1 else "2 Exponentials"
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite", SECTION)

HEADS = ["GAMMA", "Ei", "E1", "E", "F0", "ProductLog", "FresnelC",
         "FresnelS", "Chi", "Shi", "Si", "Ci", "Li", "Erf", "Erfi", "Erfc"]

def call_arity(s, head):
    """Top-level argument counts of every head(… call in s."""
    out = []
    for m in re.finditer(re.escape(head) + r"\(", s):
        i, depth, args = m.end() - 1, 0, 0
        while i < len(s):
            c = s[i]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            elif c == "," and depth == 1:
                args += 1
            i += 1
        out.append(args + 1)
    return out

print(f"section: {SECTION!r}   date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
total_entries = 0
arity = {h: {} for h in HEADS}
for f in sorted(glob.glob(os.path.join(SUITE, "*.mac"))):
    s = open(f, encoding="utf-8").read()
    total_entries += sum(1 for ln in s.splitlines() if ln.lstrip().startswith("["))
    for h in HEADS:
        for n in call_arity(s, h):
            arity[h][n] = arity[h].get(n, 0) + 1
    for nat in ["gamma_incomplete(", "expintegral_ei(", "erf(", "erfi(",
                "lambert_w(", "exp(", "%e^"]:
        c = len(re.findall(re.escape(nat), s))
        if c:
            print(f"{nat:22s} {c}")
print(f"entries: {total_entries}")
for h in HEADS:
    if arity[h]:
        print(f"{h + '(':8s} {dict(sorted(arity[h].items()))}")

```

Run: `python3 probes/corpus/02-class2-answer-heads.py > probes/corpus/02-class2-answer-heads.out`
Expected (the measured basis): `entries: 965`, `GAMMA( {2: 191}`,
`Ei( {1: 237}`, `F0( {1: 14}`, native lines `erf( 10`, `erfi( 175`,
`%e^ 1438`. Write `probes/corpus/02-class2-answer-heads.run`:
```sh
#!/bin/sh
cd "$(dirname "$0")/../.." || exit 1
echo "date $(date -u '+%F %T UTC')"
python3 probes/corpus/02-class2-answer-heads.py
```

- [ ] **Step 5: Commit**

```
git add probes/translation/01-class1-syntax-census.py \
        probes/translation/03-class2-syntax-census.out \
        probes/translation/03-class2-syntax-census.run \
        probes/corpus/02-class2-answer-heads.py \
        probes/corpus/02-class2-answer-heads.out \
        probes/corpus/02-class2-answer-heads.run
git commit -m "probe: class-2 syntax census + corpus answer-head census (milestone-2 basis)"
```

---

### Task 2: Generalize the generator + the byte-identity gate

**Files:**
- Create: `generator/generate_rules.py` (copy of `generate_class1.py` + the edits below)
- Modify: `generator/generate_class1.py` (→ shim)

**Interfaces:**
- Produces: `generate_rules.main(class_num=None)` — regenerates the
  `rules/class<N>/` tree and prints the ordered load list;
  `configure(class_num)` sets the module globals `CLASS`, `CLASS_PREFIX`,
  `OUT`, `EXPECTED_TOTAL` used by `main`/`emit_file`.
- Consumes: `translation_table.translate` (unchanged this task),
  `parse_load_rules` / `strip_comments` (the T1 inventory, unchanged),
  `rule_runs` / `split_rule` (the census parser, unchanged).

- [ ] **Step 1: Copy and rename**

```
cp generator/generate_class1.py generator/generate_rules.py
```

- [ ] **Step 2: The class parameter (module top, after `PIN`)**

Replace `OUT = ROOT / "rules" / "class1"` with:

```python
OUT = ROOT / "rules" / "class1"   # set by configure(); class-1 default

def configure(class_num):
    """Point the generator at class <class_num> (1 or 2 in the pilot)."""
    global CLASS, CLASS_PREFIX, OUT, EXPECTED_TOTAL
    CLASS = class_num
    CLASS_PREFIX = f"{CLASS} "
    OUT = ROOT / "rules" / f"class{CLASS}"
    EXPECTED_TOTAL = {1: 2710 + EXTRA_TOTAL, 2: 125}[class_num]
```

(Place the `def` AFTER the `EXTRA_TOTAL = 316` line so the dict literal
resolves; `EXTRA_TOTAL` keeps its class-1 meaning.)

- [ ] **Step 3: `load_class1_files` → `load_class_files`**

```python
def load_class_files(rubi):
    """The class-<CLASS> .m files, in Rubi.m LoadRules order, as paths
    relative to the Rubi clone root. parse_load_rules yields (parts,
    gated); the parts are relative to IntegrationRules/ and lack the .m
    extension. The selector is the class prefix: class 1 selects the
    non-gated "1 " files, class 2 the gated "2 " files (the
    $LoadElementaryFunctionRules block) — the gated flag is not a filter
    (dropping it is a no-op for class 1: the gated block holds no "1 "
    files)."""
    order = parse_load_rules((rubi / "Rubi" / "Rubi.m").read_text())
    out = []
    for parts, gated in order:
        if not parts or not parts[0].startswith(CLASS_PREFIX):
            continue
        rel = "Rubi/IntegrationRules/" + "/".join(parts) + ".m"
        out.append(rel)
    return out
```

- [ ] **Step 4: `main()` — class argument, load-list prefix, totals**

```python
def main(class_num=None):
    if class_num is None:
        class_num = (int(sys.argv[sys.argv.index("--class") + 1])
                     if "--class" in sys.argv else 1)
    configure(class_num)
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1].replace(".", "_")
    files = load_class_files(RUBI)
```

In the two `load_lines.append(…)` calls (the main loop and the
`EXTRA_CLASS1` loop), replace the hard-coded path with:

```python
        load_lines.append(
            f"%mr_load_sibling(\"rules/class{CLASS}/{key}.mac\", "
            f"'mr_witness_{key})$")
```

The `EXTRA_CLASS1` loop is wrapped so it runs only for class 1:

```python
    if CLASS == 1:
        # The five corpus-tested dead siblings (EXTRA_CLASS1), `b`-suffixed,
        # table position immediately after their same-numbered sibling.
        for rel_m in EXTRA_CLASS1:
            … (body unchanged, indented one level) …
```

The total check and its message:

```python
    expected = EXPECTED_TOTAL
    note = (f"OK (== {expected})" if (total == expected and not only)
            else ("partial (--only)" if only
                  else f"MISMATCH (expected {expected})"))
    print(f"TOTAL: {total} rules — {note}")
    if not only and total != expected:
        raise GenError(f"rule total {total} != {expected} "
                       f"(T1 census + EXTRA_CLASS1 for class 1); aborting")
```

- [ ] **Step 5: `emit_file` header — the class path**

```python
    header = (f"/* rules/class{CLASS}/{key}.mac — GENERATED; do not edit.\n"
              f" * Source: Rubi 4 {PIN}\n"
              f" *          {rel_m}\n * Regenerate: "
              f"python3 generator/generate_rules.py --class {CLASS} "
              f"--only {key} */\n"
              f"{MIT}\n\n")
```

- [ ] **Step 6: The Part handler in `translate()` (the `[[…]]` gap)**

At the top of `translate()` (after `s = s.strip()`, before
`head, args = head_args(s)`):

```python
    m = re.match(r"^([A-Za-z][A-Za-z0-9]*)\[\[([0-9]+)\]\]$", s)
    if m:
        # Mathematica Part, single integer index (class 2: uu[[1]] /
        # uu[[2]] in the Module locals of 2.1 r18 / 2.3 r10). Nested
        # indices (u[[1, 2]]) are not used in class 2; the [0-9]+ guard
        # makes any such use fail loudly at the parse instead of
        # mis-emitting.
        return f"part({translate(m.group(1), ctx)}, {m.group(2)})"
```

Rationale (measured): `head_args("uu[[2]]")` returns head `uu` with arg
`[2]`, which the emit path rejects as an unlisted head; inside a larger
atom expression the `translate_atom` walk routes `uu[[2]]` back through
`translate(name + "[" + argtxt + "]")`, where this regex catches it.

- [ ] **Step 7: `generate_class1.py` becomes the shim**

Replace the whole file with:

```python
#!/usr/bin/env python3
"""Class-1 entry point — the documented command keeps working:
    python3 generator/generate_class1.py [--only KEY]
The general generator is generate_rules.py (milestone 2)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_rules

if __name__ == "__main__":
    generate_rules.main(1)
```

- [ ] **Step 8: THE GATE — class-1 byte identity**

```
python3 generator/generate_rules.py --class 1
git status --porcelain rules/   # expected: EMPTY
git diff --stat                 # expected: EMPTY
```
Then through the shim, same result:
```
python3 generator/generate_class1.py
git status --porcelain rules/   # expected: EMPTY
```
Any diff is a task failure — fix before continuing.

- [ ] **Step 9: Smoke the class-2 parse (expected to FAIL on the table)**

```
python3 generator/generate_rules.py --class 2
```
Expected: a `GenError` naming the first unlisted class-2 head
(`TrueQ` or similar) — proving the parse path (including the Part
handler) runs to the table boundary. Record the failing token in the
ledger; it must be one the Task 3 table covers.

- [ ] **Step 10: Commit**

```
git add generator/generate_rules.py generator/generate_class1.py
git commit -m "feat: generalized rule generator (--class) + Part handler; class-1 byte-identity gate green"
```

---

### Task 3: Extend the translation table (class-2 closure) + generate class 2

**Files:**
- Modify: `generator/translation_table.py`
- Modify: `generator/generate_rules.py` (marker-as-head emission, the r96 gap)
- Modify: `maxima_rubi_utils.mac` (the MatchQ matcher's marker-head case)
- Modify: `test_maxima_rubi.mac` (Layer A tests for the marker-head case)
- Create: `rules/class2/2_1.mac`, `rules/class2/2_2.mac`, `rules/class2/2_3.mac` (generated)

**Interfaces:**
- Consumes: Task 2's generator.
- Produces: the three generated class-2 rule files (14 / 4 / 107 rules)
  and the printed load list (3 `%mr_load_sibling` lines + the flatten
  term list) that Task 7 pastes into `maxima_rubi.mac`.
- Task-1 census closure adjudication (2026-08-28, recorded per the
  closure gate): `Expand` — direct builtin (the census BUILTIN tier →
  Maxima `expand`), no table entry; `F` — token-extractor artifact (the
  single-letter pattern variable in `InverseFunctionQ[F[x]]`, 2.3 line
  104), not a function token, no table entry. The class-2 token set is
  CLOSED: every token is a Measured-basis token, a class-1-shared token,
  `Expand`, or the `F` artifact.

- [ ] **Step 1: The RENAME additions**

Append to the `RENAME` dict in `generator/translation_table.py`:

```python
    # class 2 (exponentials) — answer-side natives (the naming trap: the
    # public names carry underscores; describe(name, exact) is the
    # arbiter — probed 2026-08-28 on 5.50.0, the identities close:
    # diff(gamma_incomplete(a,z),z) = -z^(a-1) %e^-z [UPPER, the corpus
    # GAMMA(a,z) convention], diff(expintegral_ei(z),z) = %e^z/z,
    # erf/erfi native):
    "Exp": "exp", "Erf": "erf", "Erfi": "erfi",
    "ExpIntegralEi": "expintegral_ei",
    "Gamma": "gamma_incomplete",   # 2-arg UPPER only (class 2: 5/5 2-arg)
    # class-2 utility ports (Tasks 4-6):
    "TrueQ": "%mr_trueQ", "PowerQ": "%mr_powerQ",
    "Exponent": "%mr_degree",      # M1 port — general polynomial degree
    "FullSimplify": "ratsimp",     # measured approximation: on the
                                   # class-2 sites (symbolic quotients of
                                   # free constants) ratsimp preserves the
                                   # quotient so num/denom read the
                                   # formal Numerator/Denominator (the
                                   # unit test pins denom() on r61's shape)
    "PowerOfLinearQ": "%mr_powerOfLinearQ",
    "PowerOfLinearMatchQ": "%mr_powerOfLinearMatchQ",
    "NormalizePowerOfLinear": "%mr_normalizePowerOfLinear",
    "FunctionExpand": "%mr_functionExpand",
    "FunctionOfExponentialQ": "%mr_functionOfExponentialQ",
    "FunctionOfExponential": "%mr_functionOfExponential",
    "FunctionOfExponentialFunction": "%mr_functionOfExponentialFunction",
    "NormalizeIntegrand": "%mr_normalizeIntegrand",
    # Rubi's undocumented $UseGamma control global (absent from Rubi.m;
    # the class-2 corpus headers assume it false) — a VARIABLE, not a
    # function (the SimplifyFlag precedent):
    "$UseGamma": "mr_use_gamma_flag",
```

No `RESTRUCTURE` additions: every new token is a 1:1 arity map or a
utility port; `Module`/`With`/`If`/`Subst`/`Int` are already structural.

- [ ] **Step 2: THE GATE again — class-1 byte identity**

```
python3 generator/generate_rules.py --class 1
git status --porcelain rules/   # expected: EMPTY
```
(Adding table entries cannot change class-1 output only if no class-1
rule file uses the new tokens — the class-1 census proves it; a diff
means a token collided and the entry must be scoped per-class.)

- [ ] **Step 3: Generate class 2 (expect the r96 blocker)**

```
python3 generator/generate_rules.py --class 2
```
Expected: `2_1` (14) and `2_2` (4) emit, then generation stops with
`GenError ... 2_3 r96: unlisted head 'F'` — the marker-as-head gap
(`F_[v_]` in r96's second MatchQ; the `F` closure adjudication above).
Record the error line. Any OTHER token failing means the census (Task 1)
missed it — add the table entry (same discipline: native for natives,
`%mr_` port for utilities, provenance comment citing the Rubi definition
line), re-run, and re-run Step 2.

- [ ] **Step 4: The marker-as-head fix (generator + matcher + tests)**

Basis (measured 2026-08-28, 5.50.0/SBCL): `F` in r96 is the second
MatchQ's own pattern variable — a function-valued head: the pattern
`E^(c(a+bx))*F_[v_]` tests "u carries a factor F[v] with F an inverse
function", and the cond applies the binding: `InverseFunctionQ[F[x]]`.
r96 is the first ported rule with a marker in HEAD position. This
build's defmatch REJECTS pattern variables in head position
(`defmatch: some pattern variables are not atoms` — the predicate is
never even defined), so the custom `%mr_matchQ` matcher (already the
runtime for all 16 class-1 MatchQ rules) gains one new pattern form
instead of Maxima's matcher.

(a) Generator — `generator/generate_rules.py`, two emission sites,
both emitting a Maxima application whose op is the RAW marker name:
- The `translate_atom` marker branch (~line 890, `name in
  ctx["markers"]`): when the marker is consumed with a PLAIN `_` (not
  `_.`) and is followed, modulo blanks, by `[`, consume the balanced
  bracket group (the same depth scan as the nested-head branch at
  ~line 921), split the inner text on top-level commas, translate each
  piece in the current (marker) scope, and emit
  `f"{ctx['markers'][name]}({', '.join(...)})"`, advancing past `]`.
  (Pattern side: `F_[v_]` → `_mF(_mV)`.)
- The `translate_atom` nested-head branch (~line 919): before the
  `translate(name + "[" + argtxt + "]")` recursion, if
  `ctx["markers"]` is active and `name` is in `ctx["markers"]`, emit
  the same `f"{ctx['markers'][name]}({inner})"` form (args translated
  and comma-joined). (Cond side: `F[x]` → `_mF(x)`, which the existing
  `\b...\b` post-pass in `_emit_matchq` rewrites to
  `%mr_mk(_mF, %mr_mqb)(x)` — the `(` is a word boundary, so the
  rewrite is safe; longest-name-first is irrelevant because the `\b`
  guard already kills prefix collisions.)
- Why raw-marker emission on both sides: the pattern (no post-pass)
  keeps the marker atom literal — exactly the shape the matcher's new
  case consumes; the cond gets the named lookup for free.
- Runtime semantics verified (probes 2026-08-28): a bound value is an
  atom (the op of a stored call), and `<atom>(<arg>)` evaluates to the
  intended application for both known-function and unknown-function
  ops (`f:'asin$ f(x)` → asin(x); `g:'foo$ g(x)` → foo(x) noun);
  `op`/`length` of stored calls are atomic/integer as the matcher
  expects.

(b) Matcher — `maxima_rubi_utils.mac`: ONE new dispatch case in BOTH
`%mr_mq_match` (insert after the `"^"` branch, before the final
`else false`, ~line 972) and `%mr_mq_search` (same position,
~line 1077) — the op of a non-atomic pattern is a registered marker:
```
  elseif %mr_isMQMarker(op(P)) then (
    if atom(E) or not atom(op(E)) then false
    else if not is(length(P) = length(E)) then false
    else block([b],
      b : %mr_mq_bind(B, op(P), op(E)),
      if atom(b) then false
      else %mr_mq_seqargs(P, E, 1, b)))
```
with two small helpers placed next to `%mr_mq_seq` (~line 796):
```
/* ordered argument-list match — function-call arguments are ordered,
 * no permutation (unlike the commutative "*" / "+" flat match) */
%mr_mq_seqargs(P, E, i, B) := block([b],
  if i > length(P) then B
  else (
    b : %mr_mq_match(part(P, i), part(E, i), B),
    if atom(b) then false
    else %mr_mq_seqargs(P, E, i + 1, b)))$

/* the cond-threading variant: chain the existing "match" goal type —
 * no %mr_mq_apply_goal change */
%mr_mq_seqargs_search(P, E, i, B, G) := block([],
  if i > length(P) then %mr_mq_apply_goal(G, B)
  else %mr_mq_search(part(P, i), part(E, i), B,
    ["match", part(P, i + 1), part(E, i + 1), G]))$
```
and the search branch's last call is `%mr_mq_seqargs_search(P, E, 1, b, G)`.
- Semantics (the .m reading): a marker head binds ANY head of a
  non-atomic E, strict arity (`length(P) = length(E)`), the op must be
  an atom (stored Maxima calls have atomic ops), arguments ordered.
  Binding `+`/`*`/`^` as a head is the .m-faithful reading for
  multi-slot patterns and is allowed. Documented deviation (measured):
  Maxima stores unary minus as a 1-arg `"-"` node where the .m has
  `Times[-1, u]`, so a MULTI-slot marker-head pattern cannot match
  `-u`; no pilot rule needs it — r96's 1-slot `F_[v_]` on a
  unary-minus factor binds F := `"-"`, and the
  `InverseFunctionQ` cond fails closed: the same `Not[false]`
  outcome as the .m non-match.
- No new marker registration: the r96 markers already flow through
  `ctx["decls"]` (_emit_matchq) into the file's trailing
  `%mr_register_markers` line.

(c) Layer A tests — `test_maxima_rubi.mac`: a new section
`test_class2_marker_head` (registered synthetic markers — the existing
unit-marker registration precedent; the membership test is registry-
based, so unregistered names fail closed):
1. Head bind + cond: `%mr_matchQ(asin(x), _mF(_mV), lambda([%mr_mqb],
   %mr_inverseFunctionQ(%mr_mk(_mF, %mr_mqb)(%mr_mk(_mV, %mr_mqb)))))`
   → true.
2. Non-inverse fails closed: same shape, target `sin(x)` → false.
3. Arity/shape: target `x + 1` (2-arg `+`) → false; target `x` (atom)
   → false.
4. Consistent re-binding: pattern `_mF(_mV)*_mF(_mW)` on
   `asin(x)*sin(x)` → false (one F cannot be two heads).
5. Full r96 shape (run after Step 5, once `2_3.mac` exists): load
   utils + `rules/class2/2_3.mac` in a plain process (107 rules fit
   the plain-process TLS budget) and evaluate the emitted r96 MatchQ
   (extract the `%mr_matchQ(...)` call from the file) against
   `%e^(c*(a+b*x))*asin(x)` → true and against
   `%e^(c*(a+b*x))*sin(x)` → false (free-symbol a, b, c).

- [ ] **Step 5: Regenerate class 2**

```
python3 generator/generate_rules.py --class 2
```
Expected:
```
  2_1: 14 rules
  2_2: 4 rules
  2_3: 107 rules
TOTAL: 125 rules — OK (== 125)
# maxima_rubi.mac load list (Rubi LoadRules order):
%mr_load_sibling("rules/class2/2_1.mac", 'mr_witness_2_1)$
%mr_load_sibling("rules/class2/2_2.mac", 'mr_witness_2_2)$
%mr_load_sibling("rules/class2/2_3.mac", 'mr_witness_2_3)$
mr_rule_table : flatten([mr_rules_2_1, mr_rules_2_2, mr_rules_2_3])$
```

- [ ] **Step 6: Static sanity of the generated files**

```
grep -c "^_mr_rule_" rules/class2/2_1.mac rules/class2/2_2.mac rules/class2/2_3.mac   # 14 / 4 / 107
grep -n "part(" rules/class2/2_1.mac | head    # the Part sites emitted as part(uu, 1)/part(uu, 2)
grep -n "mr_use_gamma_flag" rules/class2/*.mac | wc -l   # 9 (the TrueQ sites)
grep -n '\$[A-Za-z]' rules/class2/*.mac         # EMPTY — no raw Rubi $-global leaked
                                                 # (the literal '\$' form is impossible:
                                                 # Maxima's statement terminator is $)
grep -n "gamma_incomplete\|expintegral_ei" rules/class2/*.mac | wc -l   # 8 (5 Gamma + 3 Ei)
```
Plus the r96 spot-check: the emitted 2_3 r96 carries
`%mr_matchQ(` whose pattern contains the F-marker applied to its
argument (grep the marker name with a following `(`), and its cond
contains `%mr_mk(<F-marker>, %mr_mqb)(x)`.

- [ ] **Step 7: Layer A**

Run: `maxima --very-quiet -b test_maxima_rubi.mac`
Expected: all `test_class2_marker_head` checks PASS and
`Results: <511 + the new section's count> passed, 0 failed`. The
matcher change is runtime code the accepted class-1 record depends on
(16 class-1 MatchQ rules run through `%mr_mq_search`) — the full suite
is the regression gate.

- [ ] **Step 8: Commit**

```
git add generator/translation_table.py generator/generate_rules.py \
        maxima_rubi_utils.mac test_maxima_rubi.mac rules/class2/
git commit -m "feat: class-2 table closure + MatchQ marker-head case + generated class-2 rules (125 rules, 3 files)"
```

---

### Task 4: Utils cluster A — the small predicates

**Files:**
- Modify: `maxima_rubi_utils.mac` (append the cluster after the class-1
  clusters, before the file's closing witness comment)
- Modify: `test_maxima_rubi.mac` (new `test_class2_cluster_a()` block +
  one line in `run_all_tests`)

**Interfaces:**
- Produces (consumed by Tasks 5-7 and the generated rules):
  `%mr_trueQ(v)`, `mr_use_gamma_flag` (global, `false`),
  `%mr_powerQ(u)`, `%mr_calculusQ(u)`, `%mr_hyperbolicQ(u)`,
  `%mr_everyQ(f, lst)`, `%mr_powerOfLinearQ(u, x)`,
  `%mr_powerOfLinearMatchQ(u, x)`, `%mr_normalizePowerOfLinear(u, x)`.

- [ ] **Step 1: Write the failing tests**

Append to `test_maxima_rubi.mac` (before `run_all_tests`):

```maxima
/* Class-2 cluster A — the small predicates (milestone-2 plan Task 4). */
test_class2_cluster_a() := block([],
  print("--- class-2 cluster A: small predicates ---"),
  check_bool("trueQ true", is(%mr_trueQ(true) = true)),
  check_bool("trueQ false", is(%mr_trueQ(false) = false)),
  check_bool("trueQ noun", is(%mr_trueQ('f(x)) = false)),
  check("use-gamma flag default", mr_use_gamma_flag, false),
  check_bool("powerQ power", is(%mr_powerQ(x^2) = true)),
  check_bool("powerQ bare x", is(%mr_powerQ(x) = false)),
  check_bool("powerQ sum", is(%mr_powerQ(a + b*x) = false)),
  check_bool("calculusQ integrate noun", is(%mr_calculusQ(integrate(f(x), x)) = true)),
  check_bool("calculusQ diff noun", is(%mr_calculusQ(diff(f(x), x)) = true)),
  check_bool("calculusQ product", is(%mr_calculusQ(f*x) = false)),
  check_bool("hyperbolicQ sinh", is(%mr_hyperbolicQ(sinh(x)) = true)),
  check_bool("hyperbolicQ sin", is(%mr_hyperbolicQ(sin(x)) = false)),
  check_bool("everyQ all", is(%mr_everyQ(lambda([q], integerp(q)), [1, 2, 3]) = true)),
  check_bool("everyQ one false", is(%mr_everyQ(lambda([q], integerp(q)), [1, %i]) = false)),
  check_bool("powerOfLinearQ linear", is(%mr_powerOfLinearQ(a + b*X, X) = true)),
  check_bool("powerOfLinearQ rational power", is(%mr_powerOfLinearQ((a + b*X)^(3/2), X) = true)),
  check_bool("powerOfLinearQ non-linear base", is(%mr_powerOfLinearQ((a + b*X^2)^(1/2), X) = false)),
  check_bool("powerOfLinearQ free of X", is(%mr_powerOfLinearQ(a*X, X) = true)),
  check_bool("powerOfLinearMatchQ agrees", is(%mr_powerOfLinearMatchQ((a + b*X)^(3/2), X) = true)),
  check("normalizePowerOfLinear identity", %mr_normalizePowerOfLinear((a + b*X)^(3/2), X), (a + b*X)^(3/2)),
  true
)$
```

And in `run_all_tests()`, after `test_cluster_l_powered_form(),`:
```maxima
  test_class2_cluster_a(),
```

- [ ] **Step 2: Run — verify it fails**

Run: `maxima --very-quiet -b test_maxima_rubi.mac`
Expected: the `test_class2_cluster_a` checks print `FAIL` (the functions
are undefined — a noun, `is(noun = true)` = false) and the Results line
shows 20 failures. (If Maxima dies mid-run with no Results line, the
failure is a parse error in the test block — fix syntax first.)

- [ ] **Step 3: Implement the cluster**

Append to `maxima_rubi_utils.mac`:

```maxima
/* ---- class-2 (exponentials) cluster A: the small predicates -------- */

/* Rubi TrueQ — true iff the value is literally true (Mathematica
   builtin; used in class 2 only on the $UseGamma control flag).
   is() gives the true/false/unknown trichotomy; unknown is not true. */
%mr_trueQ(v) := block([], is(is(v) = true))$

/* The package home of Rubi's $UseGamma control variable. Undefined in
   the pinned Rubi 4 (grep 2026-08-28: absent from Rubi.m and the
   utility files); the class-2 corpus file headers state the optimal
   antiderivatives assume $UseGamma = false, so the default is false —
   the gamma-form rules decline by default and fire only if the flag is
   set true explicitly. A variable, not a function (the
   mr_simplify_flag precedent, this file's line 11). */
mr_use_gamma_flag : false$

/* Rubi PowerQ (:162) — the Power-head test. MEASURED 2026-08-28
   (5.50.0/SBCL): a power's op is the STRING "^" (stringp(op(x^2))
   true, symbolp false; is(op(x^2) = "^") true — this file's house
   idiom, e.g. line 624; is(op(x^2) = power) false, the symbol
   power # the string "^"). Maxima strips the exponent-1 Power head
   (x^1 -> x), so a bare linear form reaches this as an atom/sum —
   the %mr_linearQ branch of the PowerOfLinear family covers that
   case; and x^(1/2) is stored as a 'sqrt node (the line-1242 note),
   so PowerQ(sqrt(x)) is false by design — this predicate sees only
   kept power nodes. */
%mr_powerQ(u) := block([],
  if atom(u) then false
  else is(op(u) = "^"))$

/* Rubi CalculusQ — head in the calculus list ($CalculusFunctions =
   {D, Integrate, Sum, Product, Int, Unintegrable, CannotIntegrate,
   Dif, Subst}). The package nouns stand in: the diff/integrate/
   sum/product nouns, and the 'unintegrable[f, x] noun (the catch-all
   marker, mr_unintegrable, this file's line 27); mr_int and %mr_subst
   are evaluated functions (no noun forms) but their names stay in the
   list for the stand-in mapping. Dif and CannotIntegrate have no
   package counterpart.
   MEASURED 2026-08-28 (5.50.0/SBCL): a NOUN's op is an internal
   symbol whose string() is the head name — NOT the function symbol
   (is(op('integrate[f(x),x]) = 'integrate) false, likewise for
   'diff/'sum/'product/'unintegrable), so a member() over function
   symbols never matches; the test runs on string(op(u)) — a member
   over the string list (is(string(op('diff[f(x),x])) = "diff")
   true; the diff noun's internal symbol DISPLAYS as `derivative` in
   math mode but string()s to "diff"). For operator heads op()
   already returns a string (op(f*x) is "*"), and string() of a
   string is the identity, so one test covers both. member() returns
   a boolean in this build (note at line 758). Also measured:
   integrate/sum of an x-INDEPENDENT summand EVALUATE to an ordinary
   product (integrate(f, x) = f*x, sum(f, x, 1, n) = f*n even at
   symbolic bound, op "*"), so a calculus noun only exists when the
   summed/integrated object depends on the variable. */
%mr_calculusQ(u) := block([s],
  if atom(u) then false
  else (
    s : string(op(u)),
    is(member(s, ["integrate", "diff", "sum", "product",
                  "mr_int", "mr_subst", "unintegrable"]) = true)
  ))$

/* Rubi HyperbolicQ — the six hyperbolic heads (the
   FunctionOfExponential machinery's explicit-exponential detection).
   All six are native in this build (5.50.0). MEASURED 2026-08-28: an
   ordinary function application's op IS the function symbol
   (is(op(sinh(x)) = sinh) true — unlike the noun heads above), so
   member() over the symbol list matches directly. */
%mr_hyperbolicQ(u) := block([],
  if atom(u) then false
  else is(member(op(u), [sinh, cosh, tanh, coth, sech, csch]) = true))$

/* Rubi EveryQ — func over every element, true iff all true.
   MEASURED 2026-08-28 (5.50.0/SBCL): list iteration is `for e in
   lst` — `for e : lst` parses as `for e from lst` (the definition
   echo shows it), which iterates the whole list as ONE element and
   made everyQ([1,2,3]) false. f(e) applies the lambda parameter
   directly (measured equal to apply(f, [e])). */
%mr_everyQ(f, lst) := block([r],
  r : true,
  for e in lst while r do r : is(f(e)),
  r)$

/* PowerOfLinearQ / PowerOfLinearMatchQ / NormalizePowerOfLinear —
   UNDEFINED in the pinned Rubi 4 clone (measured 2026-08-28: no
   definition in IntegrationUtilityFunctions.m or anywhere in the
   clone; absent from the Rubi-5 stub too), yet called by 2.1 r17/r18
   and 2.3 r8/r9/r10/r38 (upstream numbers; the generated call sites
   are 2.1 r12/r13 and 2.3 r5/r6/r7/r35). Ported from the call-site
   contract: u is a rational power of a linear form in x.
   Storage adaptations, MEASURED 2026-08-28 (5.50.0/SBCL):
   * Maxima strips the exponent-1 Power head (x^1 -> x), so a bare
     linear form counts (the %mr_linearQ branch is the exponent-1
     case);
   * (linear)^(1/2) is stored as a 'sqrt node (the op string of
     (a+b*X)^(1/2) is "sqrt"), so the sqrt-of-linear branch is the
     exponent-1/2 case;
   * the EXONENT is the part that must be x-free (freeof(x,
     part(u, 2))): the base is linear in x by construction, and the
     generated replacement code itself tests freeof(x, part(uu, 2))
     (rules/class2/2_1.mac r13, 2.3 r7).
   The MatchQ variant is the same test WITHOUT the implicit-exponent
   branches — the strict stored-power structure (%mr_powerQ, x-free
   rational exponent, linear base). It must not be identical to the
   value test: the 2.3 r35 condition
   %mr_powerOfLinearQ(v, x) and not(%mr_powerOfLinearMatchQ(v, x))
   is unsatisfiable (Q and not Q) if the two coincide, which would
   kill the rule; the strict reading fires exactly for the
   implicit-exponent v (bare linear / sqrt-linear), whose
   replacement re-dispatches into the F^(linear) rules.
   NormalizePowerOfLinear is the identity: the progress the recursion
   needs (u^m combining into a simpler power) comes from Maxima's own
   power combining — ((a+b x)^(p/q))^m -> (a+b x)^(p m/q) — which the
   specialized 2.1 r1-r16 patterns then re-match. A pathological
   no-progress self-refire is bounded by the runner depth cap (no
   wrong answers; bounded cost) — revisit if the class-2 run shows
   timeout mass in these shapes (ledger: milestone-2). */
%mr_powerOfLinearQ(u, x) := block([],
  if atom(u) then false
  else if %mr_linearQ(u, x) then true
  else if string(op(u)) = "sqrt" and %mr_linearQ(part(u, 1), x) then true
  else if %mr_powerQ(u) and freeof(x, part(u, 2))
       and %mr_linearQ(part(u, 1), x) and %mr_rationalQ(part(u, 2))
  then true
  else false)$

%mr_powerOfLinearMatchQ(u, x) := block([],
  if atom(u) then false
  else if %mr_powerQ(u) and freeof(x, part(u, 2))
       and %mr_linearQ(part(u, 1), x) and %mr_rationalQ(part(u, 2))
  then true
  else false)$

%mr_normalizePowerOfLinear(u, x) := u$
```

_Task-4 post-implementation correction (2026-08-28, commit 4cc259e):
the original draft of this step carried five build defects found by
measurement during the TDD runs — `lambda([q]) : expr` is not Maxima
syntax (colon form dies the run; the comma form is used above),
`for e : lst` parses as `for e from lst`, the power op is the string
`"^"` (not the symbol `power`), noun ops are internal symbols so
calculusQ tests `string(op(u))` against a string list, and the
PowerOfLinear exponent check is `freeof(x, part(u, 2))` (the base is
linear-in-x by construction). Plus two design corrections:
PowerOfLinearMatchQ is the strict stored-power test (NOT an alias of
Q — the alias makes the 2.3 r38 condition `Q and not MatchQ`
unsatisfiable, killing the rule; verified against the .m call sites
2.1 r17/r18 and 2.3 r8-r10/r38), and the sqrt-of-linear branch
covers the stored `(linear)^(1/2)` case. The block above is the
committed code, verbatim._

- [ ] **Step 4: Run — verify it passes**

Run: `maxima --very-quiet -b test_maxima_rubi.mac`
Expected: every `test_class2_cluster_a` check `PASS`; Results line
`<511 + Task-3's marker-head delta + 20> passed, 0 failed`.

- [ ] **Step 5: Commit**

```
git add maxima_rubi_utils.mac test_maxima_rubi.mac
git commit -m "feat: class-2 utils cluster A — small predicates (trueQ/powerQ/calculusQ/hyperbolicQ/everyQ/powerOfLinear family/use-gamma flag)"
```

---

### Task 5: Utils cluster B — the NormalizeIntegrand chain

**Files:**
- Modify: `maxima_rubi_utils.mac`
- Modify: `test_maxima_rubi.mac`

**Interfaces:**
- Produces: `%mr_integerPowerQ(u)`, `%mr_numericFactor(u)`,
  `%mr_contentFactor(u)` (documented stub), `%mr_signOfFactor(u)` →
  `[n, v]`, `%mr_absorbMinusSign(u)`, `%mr_normalizeLeadTermSigns(u)`,
  `%mr_monomialExponent(u, x)`, `%mr_minimumMonomialExponent(u, x)`,
  `%mr_mergeMonomials(u, x)`, `%mr_togetherSimplify(u)`,
  `%mr_unifyTerm(term, lst, x)`, `%mr_unifyTerms(lst, x)`,
  `%mr_unifySum(u, x)`, `%mr_simplifyTerm(u, x)`,
  `%mr_xpwsumP(v, x)`, `%mr_normalizeIntegrandFactorBase(u, x)`,
  `%mr_normalizeIntegrandFactor(u, x)`, `%mr_normalizeIntegrandAux(u, x)`,
  `%mr_normalizeIntegrand(u, x)`.
- Consumes (Task 4 / M1): `%mr_simp(e, [v])`, `%mr_together(u)`,
  `%mr_cancel(u)`, `%mr_leafCount(u)`, `%mr_sumQ(u)`,
  `%mr_monomialQ(u, x)`, `%mr_binomialQ(u, x)`, `%mr_binomialMatchQ(u, x)`,
  `%mr_trinomialQ(u, x)`, `%mr_trinomialMatchQ(u, x)`,
  `%mr_polynomialQ(u, x)`, `%mr_degree(u, x)`, `%mr_rationalQ(u)`,
  `%mr_fractionQ(u)`, `%mr_linearQ(u, x)`, `%mr_expandToSum(u, x)`.

Scope note (measured): the only class-2 call site is 2.3 r60
(`Int[u*F^v*G^w, x] → Int[u*NormalizeIntegrand[E^z, x], x]`, z
binomial or quadratic). Maxima splits `%e^z` over a sum on its own, so
the factors reaching `FactorBase` are `%e` (an atom) and
`%e^(linear)` / `%e^(quadratic)`. The full Sum-tail of the chain
(`ContentFactor`'s deep branches, `FixSimplify`) is unreachable on that
shape — those two are ported as documented stubs/adoptions; everything
else is faithful to the pinned definitions (cited by line in the code).

- [ ] **Step 1: Write the failing tests**

Append to `test_maxima_rubi.mac` before `run_all_tests`:

```maxima
/* Class-2 cluster B — the NormalizeIntegrand chain (milestone-2 plan
   Task 5). Shapes are the 2.3 r60 call site: E^z with z a binomial or
   quadratic (Maxima splits %e^z over the sum). */
test_class2_cluster_b() := block([],
  print("--- class-2 cluster B: NormalizeIntegrand chain ---"),
  check_bool("integerPowerQ int", is(%mr_integerPowerQ((a + b*X)^3) = true)),
  check_bool("integerPowerQ frac", is(%mr_integerPowerQ((a + b*X)^(3/2)) = false)),
  check("numericFactor number", %mr_numericFactor(4), 4),
  check("numericFactor neg number", %mr_numericFactor(-6), -6),
  check("numericFactor sum content", %mr_numericFactor(4 + 6*X), 2),
  check_bool("signOfFactor pos", is(%mr_signOfFactor(3*X) = [1, 3*X])),
  check_bool("signOfFactor neg sum", is(%mr_signOfFactor(-4 - 6*X) = [-1, 4 + 6*X])),
  check_bool("absorbMinusSign sum", is(%mr_absorbMinusSign(2*(-a - b*X)) = 2*(a + b*X))),
  check_bool("leadTermSigns identity", is(%mr_normalizeLeadTermSigns(%e^(3*X)) = %e^(3*X))),
  check("monomialExponent", %mr_monomialExponent(5*X^2, X), 2),
  check("monomialExponent free of X", %mr_monomialExponent(5*Y, X), 0),
  check_bool("normalizeIntegrand E^binomial stable",
    is(%mr_normalizeIntegrand(%e^(A + B*X), X) = %e^(A + B*X))),
  check_bool("normalizeIntegrand E^quadratic stable",
    is(%mr_normalizeIntegrand(%e^(A + B*X + C*X^2), X) = %e^(A + B*X + C*X^2))),
  check_bool("mergeMonomials linear cancel",
    is(%mr_mergeMonomials((A + B*X), X) = (A + B*X))),
  true
)$
```

In `run_all_tests()`, after `test_class2_cluster_a(),`:
```maxima
  test_class2_cluster_b(),
```

- [ ] **Step 2: Run — verify it fails**

Run: `maxima --very-quiet -b test_maxima_rubi.mac`
Expected: the `test_class2_cluster_b` checks FAIL (undefined nouns);
Results line shows the added failures.

- [ ] **Step 3: Implement the chain**

Append to `maxima_rubi_utils.mac`:

```maxima
/* ---- class-2 cluster B: the NormalizeIntegrand chain ---------------
 * Pinned definitions: IntegrationUtilityFunctions.m :1988 (Normalize-
 * Integrand), :1999 (Aux), :2004 (Factor), :2020 (FactorBase),
 * :2111-:2135 (MergeMonomials), :2160-:2180 (NormalizeLeadTermSigns /
 * AbsorbMinusSign), :2144-:2155 (UnifySum / UnifyTerms / UnifyTerm /
 * SimplifyTerm), :2178 (TogetherSimplify), :1100 (NumericFactor),
 * :1107 (ContentFactor), :1550-ish (MonomialExponent /
 * MinimumMonomialExponent), :160 (PowerQ), the IntegerPowerQ item.
 * The only class-2 call site is 2.3 r60 (E^z, z binomial/quadratic);
 * Maxima splits %e^z over the sum, so the FactorBase base is %e (atom)
 * or a linear/quadratic. Two documented deviations:
 *   (a) TogetherSimplify drops TimeConstrained/$TimeLimit (Maxima has
 *       no time-constrained evaluator) and FixSimplify (its GCD power
 *       combining is subsumed by Maxima's own power combining on
 *       re-simplification) — the ratsimp/together chain is the
 *       measured Maxima equivalent.
 *   (b) ContentFactor's UnifyNegativeBaseFactors deep branch
 *       (negative-base factor unification) is unreachable on the r60
 *       shape — the port keeps the atom/integer-power/product/sum
 *       surface (the sum branch factors out the GCD of the term
 *       contents) and returns its input in the deep case.
 * SignOfFactor's ProductQ branch: the .m's Map[SignOfFactor, u] over a
 * product yields a product of {n, v} pairs whose Part extraction
 * (NormalizeLeadTermSigns takes lst[[1]]/lst[[2]]) only composes when
 * the pairs are multiplied out; the port returns the COMPOSED pair
 * [n_total, v_total], which satisfies the usage contract ("n*v equals
 * u") and matches the .m on every r60-reachable shape (all factors
 * {1, f}). */

%mr_integerPowerQ(u) := block([],
  if atom(u) then false
  else if is(op(u) = power) and integerp(part(u, 2)) then true
  else false)$

%mr_contentFactor(u) := block([c, t],
  /* The .m's ContentFactorAux (:1107) minus its UnifyNegativeBaseFactors
     deep branch (unreachable on the r60 shape — the identity there is
     the decline-safe behavior). The sum branch factors out the GCD of
     the TERM contents — not via %mr_numericFactor (that would cycle:
     NumericFactor's sum branch calls ContentFactor). c*(u/c) with the
     division in the parentheses: Maxima evaluates (u/c) first and
     distributes it over the sum, so 2*(4+6 X)/2 -> 2*(2+3 X) without
     re-absorbing the 2. */
  if atom(u) then u
  else if %mr_integerPowerQ(u) then
    if %mr_sumQ(part(u, 1)) and is(%mr_numericFactor(part(part(u, 1), 1)) < 0)
    then (-1)^part(u, 2)*%mr_contentFactor(-part(u, 1))^part(u, 2)
    else %mr_contentFactor(part(u, 1))^part(u, 2)
  else if not atom(u) and is(op(u) = "*") then
    apply("*", map(lambda([f]) : %mr_contentFactor(f), args(u)))
  else if %mr_sumQ(u) then (
    c : 0,
    for t : args(u) do c : gcd(c, %mr_numericFactor(t)),
    if is(c # 1) and is(c # 0) then c*(u/c) else u
  )
  else u)$

%mr_numericFactor(u) := block([m, n, cf],
  if numberp(u) then (
    if is(imag(u) = 0) then real(u)
    else if is(real(u) = 0) then imag(u)
    else 1
  )
  else if %mr_powerQ(u) then (
    if %mr_rationalQ(part(u, 1)) and %mr_fractionQ(part(u, 2)) then
      if is(part(u, 2) > 0) then 1/denom(part(u, 1))
      else 1/denom(1/part(u, 1))
    else 1
  )
  else if not atom(u) and is(op(u) = "*") then
    prod(map(lambda([f]) : %mr_numericFactor(f), args(u)))
  else if %mr_sumQ(u) then (
    if %mr_leafCount(u) < 50 then (
      /* The .m's Function[If[SumQ[#], 1, NumericFactor[#]]][Content-
         Factor[u]] — content 1 (the factored form is still a sum)
         terminates with 1; a factored-out content recurses on the
         product. */
      cf : %mr_contentFactor(u),
      if %mr_sumQ(cf) then 1 else %mr_numericFactor(cf)
    )
    else (
      m : %mr_numericFactor(part(u, 1)),
      n : %mr_numericFactor(rest(u)),
      if is(m < 0) and is(n < 0) then -gcd(-m, -n) else gcd(m, n)
    )
  )
  else 1)$

%mr_signOfFactor(u) := block([],
  if (if %mr_rationalQ(u) then is(u < 0) else false)
     or (if %mr_sumQ(u) then is(%mr_numericFactor(part(u, 1)) < 0) else false)
  then [-1, -u]
  else if %mr_integerPowerQ(u) and %mr_sumQ(part(u, 1))
        and is(%mr_numericFactor(part(part(u, 1), 1)) < 0)
  then [(-1)^part(u, 2), (-part(u, 1))^part(u, 2)]
  else if not atom(u) and is(op(u) = "*") then
    block([ns, vs, p, f],
      ns : 1, vs : 1,
      for f : args(u) do (
        p : %mr_signOfFactor(f),
        ns : ns*part(p, 1),
        vs : vs*part(p, 2)),
      [ns, vs])
  else [1, u])$

%mr_absorbMinusSign(u) := block([],
  /* The .m's two structural branches (u_*v_Plus, u_*v_Plus^m odd): the
     minus is pushed into the odd-degree sum factor. Maxima: -u already
     distributes over an odd power of a sum on re-expansion, so the
     value -u IS the normalized form for the r60 shapes; the structural
     branch is kept for the explicit 2-factor case. */
  if not atom(u) and is(op(u) = "*") and length(args(u)) = 2 then (
    block([f1, f2],
      f1 : part(args(u), 1), f2 : part(args(u), 2),
      if %mr_sumQ(f1) then -f1*f2
      else if %mr_sumQ(f2) then -f2*f1
      else -u)
  )
  else -u)$

%mr_normalizeLeadTermSigns(u) := block([lst],
  lst : if not atom(u) and is(op(u) = "*")
        then apply("*", map(lambda([f]) : %mr_signOfFactor(f), args(u)))
        else %mr_signOfFactor(u),
  /* For the product case apply("*" over pairs) leaves a product of
     [n, v] pairs — compose them the same way %mr_signOfFactor does. */
  if not atom(u) and is(op(u) = "*") then (
    block([ns, vs, p, f],
      ns : 1, vs : 1,
      for f : args(u) do (
        p : %mr_signOfFactor(f),
        ns : ns*part(p, 1),
        vs : vs*part(p, 2)),
      if is(ns = 1) then vs else %mr_absorbMinusSign(vs))
  )
  else (
    if is(part(lst, 1) = 1) then part(lst, 2)
    else %mr_absorbMinusSign(part(lst, 2))))$

%mr_monomialExponent(u, x) := block([f],
  if freeof(x, u) then 0
  else if not atom(u) and is(op(u) = "*") then (
    for f : args(u) do
      if %mr_powerQ(f) and is(part(f, 1) = x) and freeof(x, part(f, 2))
      then return(part(f, 2)),
    0
  )
  else if %mr_powerQ(u) and is(part(u, 1) = x) and freeof(x, part(u, 2))
  then part(u, 2)
  else 0)$

%mr_minimumMonomialExponent(u, x) := block([n, t],
  n : %mr_monomialExponent(part(u, 1), x),
  for t : args(u)
    while is(n - %mr_monomialExponent(t, x) >= 0)
  do n : %mr_monomialExponent(t, x),
  n)$

%mr_mergeMonomials(u, x) := block([],
  /* Rules 1-2 (the proportional-linear-power merge, the
     (c*(a+b x)^n)^p merge): unreachable on the r60 shape (the factors
     are %e^a, %e^(b x), %e^(c x^2) — no linear powers); deferred with
     the identity (decline-safe). Rule 3 (a*u^m -> a*u^Simplify[m]) is
     a Maxima no-op (a*u^m is already the simplified form for free
     m; ratsimp would not rewrite it). Rule 4 (linear -> Cancel) is
     ported. */
  if atom(u) then u
  else if %mr_linearQ(u, x) then %mr_cancel(u)
  else u)$

%mr_togetherSimplify(u) := ratsimp(%mr_together(ratsimp(%mr_together(u))))$

%mr_xpwsumP(v, x) := block([f1, f2],
  /* The .m's MatchQ[v, x^m_.*w_ /; FreeQ[m, x] && SumQ[w]] — a 2-factor
     product with one x-power factor (exponent free of x) and one sum
     factor, either order. */
  if atom(v) or not is(op(v) = "*") or length(args(v)) # 2 then false
  else (
    f1 : part(args(v), 1), f2 : part(args(v), 2),
    if %mr_powerQ(f1) and is(part(f1, 1) = x) and freeof(x, part(f1, 2))
       and %mr_sumQ(f2) then true
    else if %mr_powerQ(f2) and is(part(f2, 1) = x) and freeof(x, part(f2, 2))
         and %mr_sumQ(f1) then true
    else false))$

%mr_unifyTerm(term, lst, x) := block([tmp],
  if length(lst) = 0 then [term]
  else (
    tmp : %mr_simp(part(lst, 1)/term, [x]),
    if freeof(x, tmp) then prepend(rest(lst), (1 + tmp)*term)
    else prepend(%mr_unifyTerm(term, rest(lst), x), part(lst, 1))))$

%mr_unifyTerms(lst, x) := block([],
  if length(lst) = 0 then lst
  else %mr_unifyTerm(part(lst, 1), %mr_unifyTerms(rest(lst), x), x))$

%mr_unifySum(u, x) := block([],
  if %mr_sumQ(u) then apply("+", %mr_unifyTerms(args(u), x))
  else %mr_simplifyTerm(u, x))$

%mr_simplifyTerm(u, x) := block([v, w],
  /* The .m's active SimplifyTerm returns w in BOTH branches (the v
     branch is commented out upstream); ported as written. */
  v : %mr_simp(u, [x]),
  w : %mr_together(v),
  %mr_normalizeIntegrand(w, x))$

%mr_normalizeIntegrandFactorBase(u, x) := block([v],
  if atom(u) then u
  else if %mr_binomialQ(u, x) then
    if %mr_binomialMatchQ(u, x) then u else %mr_expandToSum(u, x)
  else if %mr_trinomialQ(u, x) then
    if %mr_trinomialMatchQ(u, x) then u else %mr_expandToSum(u, x)
  else if not atom(u) and is(op(u) = "*") then
    apply("*", map(lambda([f]) : %mr_normalizeIntegrandFactor(f, x), args(u)))
  else if %mr_polynomialQ(u, x) and %mr_degree(u, x) <= 4 then
    %mr_expandToSum(u, x)
  else if %mr_sumQ(u) then (
    v : %mr_togetherSimplify(u),
    if %mr_sumQ(v) or %mr_xpwsumP(v, x)
       or is(%mr_leafCount(v) > %mr_leafCount(u) + 2)
    then %mr_unifySum(u, x)
    else %mr_normalizeIntegrandFactorBase(v, x)
  )
  else apply("+", map(lambda([f]) : %mr_normalizeIntegrandFactor(f, x), args(u))))$

%mr_normalizeIntegrandFactor(u, x) := block([bas, deg, min],
  if atom(u) then u
  else if %mr_powerQ(u) and freeof(x, part(u, 2)) then (
    bas : %mr_normalizeIntegrandFactorBase(part(u, 1), x),
    deg : part(u, 2),
    if integerp(deg) and %mr_sumQ(bas)
       and %mr_everyQ(lambda([t]) : %mr_monomialQ(t, x), args(bas))
    then (
      min : %mr_minimumMonomialExponent(bas, x),
      x^(min*deg)*apply("+",
        map(lambda([t]) : %mr_simp(t/x^min, [x]), args(bas)))^deg
    )
    else bas^deg
  )
  else if %mr_powerQ(u) and freeof(x, part(u, 1)) then
    part(u, 1)^%mr_normalizeIntegrandFactorBase(part(u, 2), x)
  else (
    bas : %mr_normalizeIntegrandFactorBase(u, x),
    if %mr_sumQ(bas) and %mr_everyQ(lambda([t]) : %mr_monomialQ(t, x), args(bas))
    then (
      min : %mr_minimumMonomialExponent(bas, x),
      x^min*apply("+", map(lambda([t]) : %mr_simp(t/x^min, [x]), args(bas)))
    )
    else bas))$

%mr_normalizeIntegrandAux(u, x) := block([mm],
  if %mr_sumQ(u) then
    apply("+", map(lambda([t]) : %mr_normalizeIntegrandAux(t, x), args(u)))
  else (
    mm : %mr_mergeMonomials(u, x),
    if not atom(mm) and is(op(mm) = "*") then
      apply("*", map(lambda([f]) : %mr_normalizeIntegrandFactor(f, x), args(mm)))
    else %mr_normalizeIntegrandFactor(mm, x)))$

%mr_normalizeIntegrand(u, x) := block([v],
  v : %mr_normalizeLeadTermSigns(%mr_normalizeIntegrandAux(u, x)),
  if is(v = %mr_normalizeLeadTermSigns(u)) then u else v)$
```

- [ ] **Step 4: Run — verify it passes**

Run: `maxima --very-quiet -b test_maxima_rubi.mac`
Expected: all cluster-B checks PASS; Results line shows only 0 failed.
If the `E^quadratic stable` check fails (Maxima may rewrite
`%e^(A+B*X+C*X^2)` into a product that the chain normalizes to a
different but equal form), replace the `is(… = …)` with the
zero-residual form `is(ratsimp(%mr_normalizeIntegrand(…) - %e^(A+B*X+C*X^2)) = 0)`
— the chain's contract is value equality, not syntactic identity.

- [ ] **Step 5: Commit**

```
git add maxima_rubi_utils.mac test_maxima_rubi.mac
git commit -m "feat: class-2 utils cluster B — NormalizeIntegrand chain (two documented deviations)"
```

---

### Task 6: Utils cluster C — FunctionOfExponential family + FunctionExpand

**Files:**
- Modify: `maxima_rubi_utils.mac`
- Modify: `test_maxima_rubi.mac`

**Interfaces:**
- Produces: `%mr_foE_test(u, x)` → `false` or `[flag, F, v]`,
  `%mr_foE_testAux(base, expon, x, st)` → `false` or `[flag, F, v]`,
  `%mr_functionOfExponentialQ(u, x)`, `%mr_functionOfExponential(u, x)`,
  `%mr_functionOfExponentialFunction(u, x)`, `%mr_foEFunctionAux(u, x, st)`,
  `%mr_fullSimplify(u)`, `%mr_functionExpand(u)`.
- Consumes: Task 4's `%mr_calculusQ`/`%mr_hyperbolicQ`/`%mr_powerQ`/
  `%mr_everyQ`; M1's `%mr_linearQ`, `%mr_sumQ`, `%mr_rationalQ`,
  `%mr_coeff(u, x, n)`, `%mr_eqQ(a, b)`, `%mr_negQ(u)`, `%mr_simp(e, [v])`.

- [ ] **Step 1: Write the failing tests**

Append to `test_maxima_rubi.mac` before `run_all_tests`:

```maxima
/* Class-2 cluster C — the FunctionOfExponential family (milestone-2
   plan Task 6). F/G/A/… are free symbols; X the variable. */
test_class2_cluster_c() := block([],
  print("--- class-2 cluster C: FunctionOfExponential family ---"),
  check_bool("foE: F^(c (a+b x))", is(%mr_functionOfExponentialQ(F^(C*(A + B*X)), X) = true)),
  check_bool("foE: %e^(a+b x)", is(%mr_functionOfExponentialQ(%e^(A + B*X), X) = true)),
  check_bool("foE: sinh(a+b x) tests true",
    is(not atom(%mr_foE_test(sinh(A + B*X), X)) = true)),
  check_bool("foE: sinh(a+b x) flag false (no explicit power)",
    is(part(%mr_foE_test(sinh(A + B*X), X), 1) = false)),
  check_bool("foE: free of X", is(%mr_functionOfExponentialQ(F^C, X) = true)),
  check_bool("foE: two different bases refused",
    is(%mr_functionOfExponentialQ(F^(A + B*X)*G^(C + D*X), X) = false)),
  check_bool("foE: non-exponential refused", is(%mr_functionOfExponentialQ(A*X^2, X) = false)),
  check_bool("foE: the variable itself refused", is(%mr_functionOfExponentialQ(X, X) = false)),
  check("foE: returns F^v (first call keeps full expon)",
    %mr_functionOfExponential(F^(C*(A + B*X)), X), F^(C*(A + B*X))),
  check_bool("foEF: F^(b x) -> X (v through the origin)",
    is(%mr_functionOfExponentialFunction(F^(B*X), X) = X)),
  check_bool("foEF: sinh(b x) -> sinh-shaped rewrite closes",
    is(ratsimp(%mr_functionOfExponentialFunction(sinh(B*X), X)
              - (X^(B*1/(B)) /2 - 1/(2*X^(B*1/(B))))) = 0)
    or is(%mr_functionOfExponentialFunction(sinh(B*X), X) = (X - 1/X)/(X + 1/X))),
  check_bool("functionExpand: gamma(3) case value",
    is(abs(float(%mr_functionExpand(gamma_incomplete(3, 1.7)))
           - float(gamma_incomplete(3, 1.7))) < 1e-9)),
  check_bool("functionExpand: passthrough", is(%mr_functionExpand(F^X) = F^X)),
  /* is(sym # 0) is unknown (not true) on free symbols — the
     value-equality form is the sound assertion: ratsimp of the
     difference closes iff the quotient survived as a quotient. */
  check_bool("fullSimplify: quotient keeps quotient",
    is(ratsimp(denom(%mr_fullSimplify(G1*H1*log(G2)/(D1*E1*log(F1))))
               - D1*E1*log(F1)) = 0)),
  true
)$
```

(The `foEF: sinh(b x)` check is intentionally loose on the first
attempt — Step 4 pins the exact emitted form against the measured
output and tightens the check to `check(…, actual, expected)`.)

In `run_all_tests()`, after `test_class2_cluster_b(),`:
```maxima
  test_class2_cluster_c(),
```

- [ ] **Step 2: Run — verify it fails**

Run: `maxima --very-quiet -b test_maxima_rubi.mac`
Expected: cluster-C checks FAIL (undefined nouns).

- [ ] **Step 3: Implement the family**

Append to `maxima_rubi_utils.mac`:

```maxima
/* ---- class-2 cluster C: the FunctionOfExponential family ----------
 * Pinned definitions: IntegrationUtilityFunctions.m :4264 (Q), :4270
 * (FunctionOfExponential), :4277 (FunctionOfExponentialFunction),
 * :4284 (FunctionOfExponentialFunctionAux), :4200-ish
 * (FunctionOfExponentialTest / TestAux). The .m uses three FLUID
 * variables ($base$, $expon$, $exponFlag$) set inside Block; Maxima
 * has no dynamic variables, so the state is threaded explicitly as the
 * list [flag, F, v] — the same information, no globals, safe under the
 * runner's re-entrant rule evaluation.
 * FunctionExpand: the .m calls it only on Gamma[p, z] with p a
 * positive integer (2.3 r28, IGtQ[p, 0]); Maxima does not auto-expand
 * gamma_incomplete(n, z) (measured 2026-08-28: noun survives, diff
 * works), so the port expands Gamma[n, z] = gamma(n) %e^-z
 * sum_{k=0}^{n-1} z^k/k! via the concretizing mr_sum, and returns
 * other shapes unchanged (decline-safe).
 * FullSimplify: ratsimp — on the TestAux/Aux shapes (quotients of
 * logs and coefficients) ratsimp preserves the quotient and cancels
 * common factors; the unit test pins the denom behavior. */

%mr_fullSimplify(u) := ratsimp(u)$

%mr_foE_test(u, x) := block([], %mr_foE_test2(u, x, [false, false, false]))$

%mr_foE_test2(u, x, st) := block([base, expon, r],
  if freeof(x, u) then st
  else if is(u = x) or %mr_calculusQ(u) then false
  else if %mr_powerQ(u) and freeof(x, part(u, 1))
       and %mr_linearQ(part(u, 2), x) then (
    base : part(u, 1), expon : part(u, 2),
    /* $exponFlag$ = True — an explicit F^v power occurred. */
    r : %mr_foE_testAux(base, expon, x, [true, part(st, 2), part(st, 3)]),
    if atom(r) then false else r
  )
  else if %mr_hyperbolicQ(u) and %mr_linearQ(part(u, 1), x) then (
    /* Hyperbolic of a linear form: base %e, flag UNCHANGED (no
       explicit power). */
    r : %mr_foE_testAux(%e, part(u, 1), x, st),
    if atom(r) then false else r
  )
  else if %mr_powerQ(u) and freeof(x, part(u, 1))
       and %mr_sumQ(part(u, 2)) then (
    /* F^(v1 + v2 + …) = F^v1 F^v2 … — test the split factors, thread
       the state. */
    r : %mr_foE_test2(part(u, 1)^part(part(u, 2), 1), x, st),
    if atom(r) then false
    else %mr_foE_test2(part(u, 1)^rest(part(u, 2)), x, r)
  )
  else (
    /* Catch[Scan[If[Not[FunctionOfExponentialTest[#, x]], Throw[False]]],
       u]; True — every subpart must test, state threaded through. */
    block([st2, p],
      st2 : st,
      for p : args(u) while not atom(st2) do
        st2 : %mr_foE_test2(p, x, st2),
      st2)))$

%mr_foE_testAux(base, expon, x, st) := block([F, v, tmp],
  if is(part(st, 2) = false) then
    /* $base$ === Null — first base seen: take it, keep the full
       expon. */
    [part(st, 1), base, expon]
  else (
    F : part(st, 2), v : part(st, 3),
    tmp : %mr_fullSimplify(log(base)*%mr_coeff(expon, x, 1)
                           /(log(F)*%mr_coeff(v, x, 1))),
    if not %mr_rationalQ(tmp) then false
    else if %mr_eqQ(%mr_coeff(v, x, 0), 0)
          or %mr_neQ(tmp, %mr_fullSimplify(
               log(base)*%mr_coeff(expon, x, 0)
               /(log(F)*%mr_coeff(v, x, 0))))
    then (
      /* The constant-term ratio is inconsistent (or the stored expon
         has none): the common expon is through the origin, v =
         coeff(x)*x/denom(tmp). The .m's IGtQ[base, 0] && IGtQ[$base$,
         0] && base < $base$ swap is false for symbolic free constants
         (IGtQ requires integers) — dropped as unreachable (documented).
         The sign flip: tmp < 0 && coeff < 0 -> -v. */
      block([e],
        e : %mr_coeff(expon, x, 1)*x/denom(tmp),
        if is(tmp < 0) and %mr_negQ(%mr_coeff(expon, x, 1))
        then [part(st, 1), F, -e]
        else [part(st, 1), F, e])
    )
    else (
      /* Consistent: fold both expons to the common expon/denom(tmp). */
      [part(st, 1), F, v/denom(tmp)])))$

%mr_functionOfExponentialQ(u, x) := block([st],
  st : %mr_foE_test(u, x),
  is(not atom(st) and part(st, 1) = true))$

%mr_functionOfExponential(u, x) := block([st],
  st : %mr_foE_test(u, x),
  part(st, 2)^part(st, 3))$

%mr_functionOfExponentialFunction(u, x) := block([st],
  st : %mr_foE_test(u, x),
  if atom(st) then u
  else %mr_simp(%mr_foEFunctionAux(u, x, st), [x]))$

%mr_foEFunctionAux(u, x, st) := block([F, v, tmp],
  F : part(st, 2), v : part(st, 3),
  if atom(u) then u
  else if %mr_powerQ(u) and freeof(x, part(u, 1))
       and %mr_linearQ(part(u, 2), x) then (
    /* u = F0^(m x + c0) -> (F0/F)^… X^ratio: the .m's two branches on
       EqQ[Coefficient[$expon$, x, 0], 0]. */
    if %mr_eqQ(%mr_coeff(v, x, 0), 0) then
      part(u, 1)^%mr_coeff(part(u, 2), x, 0)
      *x^%mr_fullSimplify(log(part(u, 1))*%mr_coeff(part(u, 2), x, 1)
                          /(log(F)*%mr_coeff(v, x, 1)))
    else
      x^%mr_fullSimplify(log(part(u, 1))*%mr_coeff(part(u, 2), x, 1)
                         /(log(F)*%mr_coeff(v, x, 1)))
  )
  else if %mr_hyperbolicQ(u) and %mr_linearQ(part(u, 1), x) then (
    /* The .m's Switch on Head[u]: sinh/cosh/tanh/coth/sech/csch of the
       tmp = X^(coeff ratio) form. */
    tmp : x^%mr_fullSimplify(%mr_coeff(part(u, 1), x, 1)
                             /(log(F)*%mr_coeff(v, x, 1))),
    if is(op(u) = sinh) then tmp/2 - 1/(2*tmp)
    else if is(op(u) = cosh) then tmp/2 + 1/(2*tmp)
    else if is(op(u) = tanh) then (tmp - 1/tmp)/(tmp + 1/tmp)
    else if is(op(u) = coth) then (tmp + 1/tmp)/(tmp - 1/tmp)
    else if is(op(u) = sech) then 2/(tmp + 1/tmp)
    else if is(op(u) = csch) then 2/(tmp - 1/tmp)
  )
  else if %mr_powerQ(u) and freeof(x, part(u, 1))
       and %mr_sumQ(part(u, 2)) then
    /* F^(v1+v2) -> the product of the rewrites (Map over the Power's
       sum splits multiplicatively in the .m too). */
    %mr_foEFunctionAux(part(u, 1)^part(part(u, 2), 1), x, st)
    *%mr_foEFunctionAux(part(u, 1)^rest(part(u, 2)), x, st)
  else (
    /* Map[Function[FunctionOfExponentialFunctionAux[#, x]], u] —
       head-preserving over +/* (the r104 call path sees only
       products/sums of powers and hyperbolics); any other head
       returns u unchanged (decline-safe). */
    if is(op(u) = "*") then
      apply("*", map(lambda([p]) : %mr_foEFunctionAux(p, x, st), args(u)))
    else if is(op(u) = "+") then
      apply("+", map(lambda([p]) : %mr_foEFunctionAux(p, x, st), args(u)))
    else u))$

%mr_functionExpand(u) := block([n, z],
  if not atom(u) and is(op(u) = gamma_incomplete)
     and length(args(u)) = 2 then (
    n : part(args(u), 1), z : part(args(u), 2),
    if integerp(n) and is(n > 0) then
      /* Gamma[n, z] = gamma(n) %e^-z sum_{k=0}^{n-1} z^k/k! — mr_sum
         concretizes the numeric bounds (this file's line 53). */
      gamma(n)*exp(-z)*mr_sum(z^k/factorial(k), 'k, 0, n - 1)
    else u
  )
  else u)$
```

- [ ] **Step 4: Run, read the actual forms, tighten the loose checks**

Run: `maxima --very-quiet -b test_maxima_rubi.mac`
Read the cluster-C output. For the `foEF: sinh(b x)` check: print
`disp(%mr_functionOfExponentialFunction(sinh(B*X), X));` in a scratch
batch (`maxima --very-quiet --batch-string='…'` after loading the
package files the way the suite does), and replace the loose
`check_bool` with `check("foEF: sinh(b x) exact", <actual expression
read from the output>, <same expression>)` — the exact form is the
one the runner will produce on real corpus entries, and the A/B
comparison relies on it being deterministic. Expected final: every
cluster-C check PASS, Results line `0 failed`.

- [ ] **Step 5: Commit**

```
git add maxima_rubi_utils.mac test_maxima_rubi.mac
git commit -m "feat: class-2 utils cluster C — FunctionOfExponential family (state-threaded) + functionExpand (gamma integer case)"
```

---

### Task 7: Loader + rules core + fingerprint wiring

**Files:**
- Modify: `maxima_rubi.mac`
- Modify: `test/build_rules_core.sh`
- Create: `probes/load_wall/probe-class2-load.mac`, `.out`, `.run`
- Modify: `test_maxima_rubi.mac` (the class-2 census spot check)
- Modify: `test/corpus_class1_driver.py` (the `_core_fingerprint` glob —
  moved with the driver in Task 8; done HERE in the class-1 file so the
  core is usable before Task 8)

**Interfaces:**
- Produces: `mr_load_all()` (loads class 1 then class 2, LoadRules
  order, 3180 rules), a rules core carrying the full table, the
  3180 witness.

- [ ] **Step 1: `mr_load_all()` in `maxima_rubi.mac`**

Append after the `mr_load_class1_all()` definition:

```maxima
/* Full table load (Rubi.m LoadRules order): class 1 (the 73-term
   flatten above) then class 2 — the first $LoadElementaryFunctionRules
   block (3 files, 125 rules; measured 2026-08-28). The table is the
   76-term flatten (3,180 rules). MR: the driver and the rules core
   call this; Layer A still loads only the 1.1.1.1 core file above (the
   defmatch budget of a plain process holds a handful of rules — see
   the load-wall note above). */
mr_load_all() := block([],
  mr_load_class1_all(),
  %mr_load_sibling("rules/class2/2_1.mac", 'mr_witness_2_1),
  %mr_load_sibling("rules/class2/2_2.mac", 'mr_witness_2_2),
  %mr_load_sibling("rules/class2/2_3.mac", 'mr_witness_2_3),
  mr_rule_table : flatten([mr_rule_table, mr_rules_2_1,
                           mr_rules_2_2, mr_rules_2_3])
)$
```

- [ ] **Step 2: The full-load probe (under the TLS flag)**

Create `probes/load_wall/probe-class2-load.mac`:
```maxima
/* Full table load: class 1 + class 2 (3,180 rules) under the TLS flag.
   Witness: TABLE_AT_LOAD 3180. Re-run: see .run. */
load("maxima_rubi.mac")$
mr_load_all()$
disp(concat("TABLE_AT_LOAD ", string(length(mr_rule_table))))$
```
Create `probes/load_wall/probe-class2-load.run`:
```sh
#!/bin/sh
cd "$(dirname "$0")/../.." || exit 1
echo "maxima $(maxima --version 2>&1 | head -1)  date $(date -u '+%F %T UTC')"
maxima --very-quiet -X "--tls-limit 100000" -b probes/load_wall/probe-class2-load.mac
```
Run: `sh probes/load_wall/probe-class2-load.run > probes/load_wall/probe-class2-load.out`
Expected: `TABLE_AT_LOAD 3180` and no error. (If a generated rule
file fails to load, the witness error names the file — fix the
generation defect, not the probe.)

- [ ] **Step 3: `build_rules_core.sh` — fingerprint + load list**

In the `FP=$( { printf … } | …)` block, add the class-2 glob to the
file list (after `ls rules/class1/*.mac`):
```sh
FP=$( { printf '%s\n' maxima_rubi.mac maxima_rubi_utils.mac maxima_rubi_dispatch.lisp \
        maxima_rubi_implicit1.lisp
        ls rules/class1/*.mac rules/class2/*.mac
      } | LC_ALL=C sort | xargs -d '\n' cat | md5sum | cut -d' ' -f1 )
```
and in the image script (`printf 'batch_answers_from_file: true$ …'`),
replace `mr_load_class1_all()` with `mr_load_all()`. Update the
header comment: "…every class-1 AND class-2 rule file…".

- [ ] **Step 4: The driver's `_core_fingerprint()` mirror**

In `test/corpus_class1_driver.py`, `_core_fingerprint()` — the `rels`
list — add the class-2 glob (keep C-locale sorted order, matching the
shell `LC_ALL=C sort`):
```python
    rels = sorted(["maxima_rubi.mac", "maxima_rubi_utils.mac",
                   "maxima_rubi_dispatch.lisp",
                   "maxima_rubi_implicit1.lisp"] +
                  [os.path.relpath(p, ROOT) for p in
                   glob.glob(os.path.join(ROOT, "rules", "class1", "*.mac"))] +
                  [os.path.relpath(p, ROOT) for p in
                   glob.glob(os.path.join(ROOT, "rules", "class2", "*.mac"))])
```
(Both sides must change TOGETHER — the script's NOTE and the driver's
docstring both say the order must match; a mismatch makes every freshly
built core look stale.)

- [ ] **Step 5: Rebuild the core and witness**

```
sh test/build_rules_core.sh
```
Expected: `built test/mr_rules.core (… bytes) rules=3180 fingerprint=<new>`
and `test/mr_rules.core.stamp` with the new fingerprint + `rules 3180`.
Then confirm the driver sees it fresh:
```
python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('d', 'test/corpus_class1_driver.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print(m.rules_core_state())"
```
Expected: `on`. (Run from the worktree root; the driver computes
`ROOT` from its own path, and the module top level reads only argv
defaults — no cwd dependence.)

- [ ] **Step 6: Layer A — the class-2 census spot check**

Append to `test_maxima_rubi.mac` before `run_all_tests` (mirrors
`test_census`'s loadable-subset approach — 4 rules is budget-safe in a
plain process):

```maxima
/* Class-2 census cross-check (loadable subset; the full 3,180 table
   lives in the rules core / the TLS-flagged probe — the plain-process
   defmatch budget holds a handful of rules, the load-wall note in
   maxima_rubi.mac). */
test_class2_census() := block([saved_table],
  print("--- class-2 census cross-check (loadable subset) ---"),
  saved_table : mr_rule_table,
  %mr_load_sibling("rules/class2/2_2.mac", 'mr_witness_2_2),
  check("2.2 count = 4 (T1 inventory)", mr_rules_count_2_2, 4),
  check_bool("2.2 witness survived", is(mr_witness_2_2() = true)),
  check("core 1.1.1.1 count still 5", mr_rules_count_1_1_1_1, 5),
  mr_rule_table : saved_table,
  true
)$
```
In `run_all_tests()`, after `test_class2_cluster_c(),`:
```maxima
  test_class2_census(),
```

Run: `maxima --very-quiet -b test_maxima_rubi.mac`
Expected: the three new checks PASS; Results line `0 failed` with the
total grown by the cluster A+B+C+census additions.

- [ ] **Step 7: Commit**

```
git add maxima_rubi.mac test/build_rules_core.sh test/corpus_class1_driver.py \
        probes/load_wall/probe-class2-load.mac probes/load_wall/probe-class2-load.run \
        probes/load_wall/probe-class2-load.out test_maxima_rubi.mac test/mr_rules.core test/mr_rules.core.stamp
git commit -m "feat: mr_load_all (class1+class2, 3180 rules) + core/fingerprint wiring + TLS full-load probe"
```
(Commit the rebuilt core and stamp — they are generated artifacts the
driver consumes by fingerprint; the stamp's `git_dirty`/`git_tree`
lines make the build self-describing.)

---

### Task 8: Generalize the corpus driver/launcher/merger + answer normalization

**Files:**
- Create: `test/corpus_driver.py`, `test/launch_class_shards.py`,
  `test/merge_class_shards.py`, `test/test_head_rewrites.py`
- Modify: `test/corpus_class1_driver.py`, `test/launch_class1_shards.py`,
  `test/merge_class1_shards.py` (→ shims), `test/wait_and_merge.sh`

**Interfaces:**
- Produces: `test/corpus_driver.py` — the class-1 driver's interface
  (the 10 positionals: filter, per-file, timeout, suite-dir,
  start-index, append, skip-first, out-file, stop-index, shard-file)
  plus: `HEAD_REWRITES` (the head normalization),
  `normalize_heads(text)` → rewritten text + cumulative `REWRITE_STATS`
  (printed in the record header), `_core_fingerprint()` over class-1 +
  class-2 files. `test/launch_class_shards.py [SECTION] [MERGED]
  [DRIVER] [--launch]` — the class-1 launcher's behavior parameterized
  (slug = `"class" + section.split()[0]` drives the pid/shard file
  names). `test/merge_class_shards.py [SECTION] [OUT] [DRIVER]` — the
  class-1 merger parameterized.

- [ ] **Step 1: `corpus_driver.py` — copy + the three deltas**

```
cp test/corpus_class1_driver.py test/corpus_driver.py
```
Delta 1 — add `import re` to the import block (the class-1 driver has
os/subprocess/sys/tempfile/time/datetime — no `re`), then the rewrites
table (top of file, after the imports):
```python
import re

HEAD_REWRITES = [
    # Corpus expected answers carry Rubi-notation special-function
    # heads; the package emits the native Maxima names (the generator
    # table). Rewrite the corpus text so both sides of the zero chain
    # carry the same (native, differentiable) head. Measured 2026-08-28
    # on 5.50.0: gamma_incomplete(a, z) is the UPPER 2-arg (d/dz =
    # -z^(a-1) %e^-z — the corpus GAMMA(a, z) convention), d/dz
    # expintegral_ei(z) = %e^z/z (probes/corpus/02-class2-answer-heads).
    # The lookbehind keeps longer names (e.g. a free function named
    # "XEi") intact.
    (re.compile(r"(?<![A-Za-z0-9_])GAMMA\("), "gamma_incomplete("),
    (re.compile(r"(?<![A-Za-z0-9_])Ei\("), "expintegral_ei("),
]
REWRITE_STATS = {}

def normalize_heads(text):
    for rx, rep in HEAD_REWRITES:
        text, n = rx.subn(rep, text)
        if n:
            REWRITE_STATS[rep] = REWRITE_STATS.get(rep, 0) + n
    return text
```

Delta 2 — apply the normalization to the entry texts in `main()` where
the elements are split:
```python
            f_text, var_text, _steps, e_text = els[0], els[1], els[2], els[3]
            e_text2 = els[4] if len(els) == 5 else None
```
becomes:
```python
            f_text = normalize_heads(els[0])
            var_text = els[1]
            _steps = els[2]
            e_text = normalize_heads(els[3])
            e_text2 = normalize_heads(els[4]) if len(els) == 5 else None
```

Delta 3 — the record header gains the rewrite stats (after the
`out_lines.append(f"filter: …")` line):
```python
    out_lines.append(f"head rewrites: {REWRITE_STATS or '{}'}")
```

Delta 4 — `_core_fingerprint()` already gained the class-2 glob in
Task 7 Step 4; move that logic HERE verbatim (the class-1 file becomes
a shim in Step 2, so the implementation lives in exactly one place):
the `rels` list includes BOTH the `rules/class1/*.mac` and
`rules/class2/*.mac` globs, C-locale sorted.

- [ ] **Step 2: The shims**

`test/corpus_class1_driver.py` becomes:
```python
#!/usr/bin/env python3
"""Legacy class-1 driver entry point. launch_class1_shards.py,
merge_class1_shards.py, and launch_timeout_rerun.py exec this file
IN-PROCESS (importlib spec_from_file_location + exec_module) and call
its file_list() / extract_entries() — the shim therefore RE-EXPORTS
those two names, not just main(). The implementation is
test/corpus_driver.py (milestone 2); class-1 behavior is unchanged —
the head rewrites are a measured no-op on the class-1 section (0
renamable-head occurrences, probes/corpus/02-class2-answer-heads
covers the class-2 counts; the class-1 no-op is the driver's
`head rewrites: {}` header line on every class-1 record)."""
import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "corpus_driver", os.path.join(ROOT, "test", "corpus_driver.py"))
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# Re-exports for the in-process consumers (the launcher's cost model
# and the merger's completeness assertion).
file_list = _mod.file_list
extract_entries = _mod.extract_entries

if __name__ == "__main__":
    _mod.main()
```
`test/launch_class_shards.py` (created in Step 3) is a copy of
`test/launch_class1_shards.py` with the hard-coded names parameterized
(Step 3); `test/launch_class1_shards.py` becomes:
```python
#!/usr/bin/env python3
"""Legacy class-1 launcher (documented interface, AGENTS.md). The
implementation is test/launch_class_shards.py (milestone 2)."""
import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.argv = ["launch_class_shards.py",
            "1 Algebraic functions",
            os.path.join(ROOT, "test", "corpus_class1.out"),
            os.path.join("test", "corpus_class1_driver.py")] \
    + list(sys.argv[1:])
runpy.run_path(os.path.join(HERE, "launch_class_shards.py"),
              run_name="__main__")
```
`test/merge_class_shards.py` (created in Step 4) is a copy of
`test/merge_class1_shards.py` parameterized; `test/merge_class1_shards.py`
becomes the analogous shim (same re-export shape is NOT needed — the
merger is only ever run as a CLI, not execed; the shim is a 4-line
argv-forwarding script to `merge_class_shards.py` with the class-1
defaults).

- [ ] **Step 3: `launch_class_shards.py` — the four parameterized names**

Copy `test/launch_class1_shards.py` to `test/launch_class_shards.py`.
The class-1 file has, right after the docstring:

```python
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRIVER = os.path.join("test", "corpus_class1_driver.py")
SECTION = "1 Algebraic functions"
SUITE_REL = "reference/maxima-syntax-test-suite"
N_PROCS = int(os.environ.get("MR_N_PROCS") or os.cpu_count() or 24)
```
and, after the cost-model constants,
```python
MERGED = os.path.join(ROOT, "test", "corpus_class1.out")
...
LAUNCH = "--launch" in sys.argv
sys.argv = ["corpus_class1_driver.py", SECTION + "/", "999999", "30"]
```
Replace the constants block and the argv rewrite with (the three
positionals are consumed from the ORIGINAL argv, before the rewrite):
```python
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECTION = sys.argv[1] if len(sys.argv) > 1 else "1 Algebraic functions"
MERGED = sys.argv[2] if len(sys.argv) > 2 \
    else os.path.join(ROOT, "test", "corpus_class1.out")
DRIVER = sys.argv[3] if len(sys.argv) > 3 \
    else os.path.join("test", "corpus_class1_driver.py")
SLUG = "class" + SECTION.split()[0]     # "1 …" -> class1, "2 …" -> class2
SUITE_REL = "reference/maxima-syntax-test-suite"
N_PROCS = int(os.environ.get("MR_N_PROCS") or os.cpu_count() or 24)
```
and, where the class-1 file rewrites argv for the in-process driver
exec:
```python
LAUNCH = "--launch" in sys.argv
sys.argv = [DRIVER, SECTION + "/", "999999", "30"]
```

Then the file-name uses:
- `pidfile = os.path.join(ROOT, "test", f"corpus_{SLUG}.shard-pids")`
- `out = os.path.join("test", f"corpus_{SLUG}.shard{idx:02d}.out")`
- `log = os.path.join("test", f"corpus_{SLUG}.shard{idx:02d}.log")`
- `sfp = os.path.join(shardfile_dir, f"corpus_{SLUG}.shard{idx:02d}.files")`
- the plan report header `"=== class-1 shard plan ==="` →
  `f"=== {SLUG} shard plan ==="`
- the docstring's class-1 references → "the <SLUG> corpus run".

- [ ] **Step 4: `merge_class_shards.py`**

Copy `test/merge_class1_shards.py` to `test/merge_class_shards.py`
and replace the constants block:
```python
SECTION = sys.argv[1] if len(sys.argv) > 1 else "1 Algebraic functions"
SLUG = "class" + SECTION.split()[0]
OUT = sys.argv[2] if len(sys.argv) > 2 \
    else os.path.join("test", "corpus_class1.out")
DRIVER = sys.argv[3] if len(sys.argv) > 3 \
    else os.path.join("test", "corpus_class1_driver.py")
SHARD_GLOB = sys.argv[4] if len(sys.argv) > 4 \
    else f"corpus_{SLUG}.shard*.out"
```
Replace the hard-wired shard discovery:
```python
inputs = sorted(glob.glob(os.path.join(ROOT, "test",
                                       "corpus_class1.shard*.out")))
```
with:
```python
inputs = sorted(glob.glob(os.path.join(ROOT, "test", SHARD_GLOB)))
```
and the header line
`f"=== maxima-rubi class-1 corpus run (full, {len(inputs)} shards merged) ==="`
with
`f"=== maxima-rubi {SLUG} corpus run (full, {len(inputs)} shards merged) ==="`.
The completeness assertion already runs against the driver's
`file_list()` as the class-1 version does (the driver
is execed with `sys.argv = [DRIVER, SECTION + "/", "999999", "30"]` —
the generalized driver honors the filter, so this carries over). The
`RESULT`/`KNOWN_CLASSES`/`PASS_CLASSES` regexes and classes are
unchanged.

- [ ] **Step 5: `wait_and_merge.sh` — parameterized**

```bash
#!/bin/bash
# Wait for the shard driver processes (pids from the pids file) to
# exit, then run the completeness-checked merge. Launched detached
# (setsid) by the session that started the run.
#
# Usage: wait_and_merge.sh [pids-file] [merge-script] [merge-log]
# Defaults: the class-1 run (the documented AGENTS.md invocation).
cd "$(dirname "$0")/.." || exit 1
PIDS=${1:-test/corpus_class1.shard-pids}
MERGE=${2:-test/merge_class1_shards.py}
MERGELOG=${3:-test/full_core_merge.out}
pids=$(awk '{print $2}' "$PIDS")
echo "$(date -u '+%F %T UTC') watcher: waiting for pids: $pids"
for pid in $pids; do
  while kill -0 "$pid" 2>/dev/null; do sleep 120; done
done
echo "$(date -u '+%F %T UTC') watcher: all shards exited; merging"
python3 "$MERGE" > "$MERGELOG" 2>&1
rc=$?
echo "$(date -u '+%F %T UTC') watcher: merge rc=$rc" >> "$MERGELOG"
exit $rc
```

- [ ] **Step 6: The pure-Python unit test for the rewrites**

Create `test/test_head_rewrites.py` (run directly: `python3
test/test_head_rewrites.py`; it exits nonzero on failure, prints
`Results: n passed, m failed` per the house reading protocol):

```python
#!/usr/bin/env python3
"""Unit test for the answer-head rewrites (test/corpus_driver.py
HEAD_REWRITES). Pure Python — no Maxima needed."""
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "corpus_driver", os.path.join(ROOT, "test", "corpus_driver.py"))
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

passed = failed = 0
def check(name, actual, expected):
    global passed, failed
    if actual == expected:
        passed += 1
        print(f"PASS: {name}")
    else:
        failed += 1
        print(f"FAIL: {name}\n  expected: {expected!r}\n  actual:   {actual!r}")

n = m.normalize_heads
check("GAMMA 2-arg", n("GAMMA(m + 1, -f*g*log(F)/d*(c + d*x))"),
      "gamma_incomplete(m + 1, -f*g*log(F)/d*(c + d*x))")
check("Ei 1-arg", n("F^(g*(e - c*f/d))/d*Ei(f*g*(c + d*x)*log(F)/d)"),
      "F^(g*(e - c*f/d))/d*expintegral_ei(f*g*(c + d*x)*log(F)/d)")
check("longer name intact", n("XEi(2)"), "XEi(2)")
check("free F0 untouched", n("F0(x)/(x + F0(x))"), "F0(x)/(x + F0(x))")
check("erf lowercase untouched", n("2*erf(z)"), "2*erf(z)")
check("native already-native untouched",
      n("gamma_incomplete(2, z)"), "gamma_incomplete(2, z)")
check("both in one line", n("GAMMA(a, z)*Ei(w)"),
      "gamma_incomplete(a, z)*expintegral_ei(w)")
print(f"Results: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
```

Run: `python3 test/test_head_rewrites.py`
Expected: `Results: 7 passed, 0 failed`.

- [ ] **Step 7: The class-1 no-op spot check (50 entries vs the last record)**

Pick 50 entries spread over the class-1 section — file 0 entries
1-17, file 1 entries 1-17, file 2 entries 1-16 (the driver's
start-file-index positional) — and run them through the NEW driver to
scratch records:
```
python3 test/corpus_driver.py "1 Algebraic functions/" 17 30 reference/maxima-syntax-test-suite 0 "" 0 /tmp/class1_spot.out
python3 test/corpus_driver.py "1 Algebraic functions/" 17 30 reference/maxima-syntax-test-suite 1 "" 0 /tmp/class1_spot2.out
python3 test/corpus_driver.py "1 Algebraic functions/" 16 30 reference/maxima-syntax-test-suite 2 "" 0 /tmp/class1_spot3.out
```
Expected on each: the `head rewrites: {}` header line (the measured
no-op), and the per-entry class lines identical to the same
`(file, entry)` lines in the current `test/corpus_class1.out` (the
class-1 full record is 25,697 lines — spot-check these 50):
```
for f in /tmp/class1_spot*.out; do grep -E '^(expected|verified|unverified|no-answer|unexpected|error|timeout|deferred|contains-noun) ' "$f"; done > /tmp/spot_new
```
then compare those 50 `(file e#)` class assignments against
`test/corpus_class1.out` (e.g. a small Python loop over the two
record formats — both are the T3 line format, so a
`(rel, entry) -> class` dict diff). A mismatch is a task failure —
the normalization or the fingerprint changed class-1 behavior.

- [ ] **Step 8: Class-1 interface regression — the documented commands still work**

```
python3 test/launch_class1_shards.py            # dry run: prints the plan (measured cost model)
python3 test/merge_class1_shards.py --help 2>/dev/null || python3 -c "import py_compile; py_compile.compile('test/merge_class1_shards.py', doraise=True)"
maxima --very-quiet -b test_maxima_rubi.mac     # Layer A still green
```
Expected: the plan prints with the same shape as before (cost model
unchanged), the shim compiles, Layer A `0 failed`.

- [ ] **Step 9: Commit**

```
git add test/corpus_driver.py test/launch_class_shards.py test/merge_class_shards.py \
        test/corpus_class1_driver.py test/launch_class1_shards.py test/merge_class1_shards.py \
        test/wait_and_merge.sh test/test_head_rewrites.py
git commit -m "feat: generalized corpus driver/launcher/merger + two-sided answer-head normalization (class-1 no-op proven)"
```

---

### Task 9: Class-2 baseline (native `integrate`, T3 mechanics)

**Files:**
- Modify: `probes/corpus/probe-integrate-sample.py` (section argv)
- Create: `test/corpus_class2.baseline.out` (the merged baseline record)

**Interfaces:**
- Produces: the merged class-2 `integrate` baseline (965 entries,
  30 s cap) — the A/B yardstick for Task 10.

- [ ] **Step 1: Parameterize the section (and fix the hard-coded ROOT)**

In `probes/corpus/probe-integrate-sample.py`, the constants:
```python
ROOT = "/home/serge/src/maxima-rubi"
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
SECTION = "1 Algebraic functions"
```
and
```python
FILTER = sys.argv[1] if len(sys.argv) > 1 else SECTION + "/"
```
become:
```python
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
SECTION = sys.argv[10] if len(sys.argv) > 10 else "1 Algebraic functions"
...
FILTER = sys.argv[1] if len(sys.argv) > 1 else SECTION + "/"
```
(the section is the LAST positional — the nine existing positionals
keep their order; the usage docstring gains `[section]`; the ROOT fix
lets the probe run from the worktree against the worktree's
`reference/` symlink).

- [ ] **Step 2: Run the three files as three shards**

The class-2 section has 3 files (98 / 93 / 774 entries) — one
process per file, 30 s cap, per-file out files:
```
python3 probes/corpus/probe-integrate-sample.py "2 Exponentials/" 999999 30 \
  reference/maxima-syntax-test-suite 0 "" 0 \
  test/corpus_class2.baseline.shard00.out 1 "2 Exponentials" &
python3 probes/corpus/probe-integrate-sample.py "2 Exponentials/" 999999 30 \
  reference/maxima-syntax-test-suite 1 "" 0 \
  test/corpus_class2.baseline.shard01.out 2 "2 Exponentials" &
python3 probes/corpus/probe-integrate-sample.py "2 Exponentials/" 999999 30 \
  reference/maxima-syntax-test-suite 2 "" 0 \
  test/corpus_class2.baseline.shard02.out 3 "2 Exponentials" &
wait
```
(Each run: start-file-index → stop-file-index exclusive; the section
positional is the 10th argument.)

- [ ] **Step 3: Merge + completeness**

The baseline shards use the T3 line format the merger parses; the
merger's completeness check asserts against the section's
`file_list()` (which, via the driver, honors the `"2 Exponentials/"`
filter). Merge with the generalized merger (Task 8 Step 4), pointed at
the baseline output and the baseline shard glob:
```
python3 test/merge_class_shards.py "2 Exponentials" \
  test/corpus_class2.baseline.out test/corpus_driver.py \
  "corpus_class2.baseline.shard*.out"
```
(The fourth positional is the `SHARD_GLOB` the class-2 package run
must distinguish from the baseline shards — without it the default
`corpus_class2.shard*.out` would miss the baseline files.)
Expected: the merge asserts **965/965** (no dupes/missing/extra) and
prints the summary — read the `Results:` line.

- [ ] **Step 4: Commit**

```
git add probes/corpus/probe-integrate-sample.py test/merge_class_shards.py \
        test/corpus_class2.baseline.out
git commit -m "baseline: class-2 integrate baseline (965 entries, T3 mechanics)"
```
(The baseline shard .out files: commit only the merged record; the
shards are intermediates, as in class 1.)

---

### Task 10: Full class-2 package run + A/B + timeout re-check

**Files:**
- Create: `test/corpus_class2.out` (the merged package record)

**Interfaces:**
- Consumes: the rules core (Task 7), the generalized launcher/driver
  (Task 8), the baseline (Task 9).
- Produces: the measured class-2 acceptance record.

- [ ] **Step 1: The shard plan (dry run)**

```
python3 test/launch_class_shards.py "2 Exponentials" test/corpus_class2.out test/corpus_driver.py
```
Expected: the plan over 3 files / 965 entries; no measured times yet
(fresh section) → count-based balancing; the 774-entry file is split
into chunks so no job carries >~40 entries × 3.5 s. Read the plan —
every job ≤ the target.

- [ ] **Step 2: Launch + watch**

First, extend `test/wait_and_merge.sh`'s merge invocation to pass
through the merger's own arguments (Task 8's version runs
`python3 "$MERGE"` with none) — replace its
`python3 "$MERGE" > "$MERGELOG" 2>&1` line with:
```bash
python3 "$MERGE" "${@:4}" > "$MERGELOG" 2>&1
```
(`${@:4}` = argv from the 4th on — the merger's
`[SECTION] [OUT] [DRIVER] [SHARD_GLOB]` positionals.) Then:
```
python3 test/launch_class_shards.py "2 Exponentials" test/corpus_class2.out test/corpus_driver.py --launch
setsid sh test/wait_and_merge.sh test/corpus_class2.shard-pids \
  test/merge_class_shards.py test/class2_merge.out \
  "2 Exponentials" test/corpus_class2.out test/corpus_driver.py \
  "corpus_class2.shard*.out" &
```
(The class-1 documented invocation `setsid sh test/wait_and_merge.sh`
keeps working: no args → the three class-1 defaults + an empty
`${@:4}`.) Run wall: 965 entries × ~3.5 s core / 24 procs ≈ 4-8 min +
load. Watch `test/class2_merge.out` for the watcher's lines; the merge
asserts **965/965** completeness — read the `Results:` line of
`test/corpus_class2.out`.

- [ ] **Step 3: The A/B against the baseline**

Compare `test/corpus_class2.out` (package) vs
`test/corpus_class2.baseline.out` (integrate) per verdict class:

```
python3 - <<'EOF'
import re
R = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)\s*$")
def counts(p):
    c = {}
    for ln in open(p, encoding="utf-8"):
        m = R.match(ln.rstrip("\n"))
        if m:
            c[m.group(1)] = c.get(m.group(1), 0) + 1
    return c
base = counts("test/corpus_class2.baseline.out")
pkg = counts("test/corpus_class2.out")
tot_b = sum(base.values()); tot_p = sum(pkg.values())
pass_b = sum(v for k, v in base.items() if k in {"expected", "verified", "no-answer"})
pass_p = sum(v for k, v in pkg.items() if k in {"expected", "verified", "no-answer"})
print(f"baseline: {pass_b}/{tot_b} ({100*pass_b/tot_b:.1f}%)  {base}")
print(f"package:  {pass_p}/{tot_p} ({100*pass_p/tot_p:.1f}%)  {pkg}")
EOF
```
Record the two lines in the ledger; the uplift is REPORTED, not a
target (the pilot proves the process).

- [ ] **Step 4: The timeout re-check (300 s, standing protocol)**

`launch_timeout_rerun.py` hard-wires `SECTION = "1 Algebraic
functions"` and (in the in-process driver exec)
`sys.argv = ["corpus_class1_driver.py", SECTION + "/", "999999",
str(CAP)]`. Parameterize: the usage line becomes
`launch_timeout_rerun.py [source-record] [cap-s] [run-dir] [section]
[--launch]` (the three existing positionals keep their order), and:
```python
pos = [a for a in sys.argv[1:] if a != "--launch"]
...
SECTION = pos[3] if len(pos) > 3 else "1 Algebraic functions"
DRIVER = ("corpus_class1_driver.py" if SECTION == "1 Algebraic
          functions" else "corpus_driver.py")
...
sys.argv = [DRIVER, SECTION + "/", "999999", str(CAP)]
```
(the class-1 section keeps the re-exporting shim — behaviorally the
same module; class 2 points at the generalized driver directly).
`wait_timeout_rerun.sh` and `merge_timeout_rerun.py` need no change:
the rerun runs under `<run-dir>/`, the watcher reads the source
record from `<run-dir>/source`, and the merge is already
`merge_timeout_rerun.py [shard-glob] [out-file] [source-record]`.
Then re-run exactly the record's `timeout` class at 300 s:
```
python3 test/launch_timeout_rerun.py test/corpus_class2.out 300 test/corpus_class2.timeout-rerun "2 Exponentials" --launch
setsid sh test/wait_timeout_rerun.sh test/corpus_class2.timeout-rerun \
  >> test/corpus_class2.timeout-rerun/wait.log 2>&1 &
```
(completeness is asserted against the record's timeout class; the cap
is read from the shard headers). Read the transitions: timeouts that
pass at 300 s are slow-correct — the route for them is matcher speed,
not budget (the 30 s cap stays).

- [ ] **Step 5: Commit**

```
git add test/corpus_class2.out test/wait_and_merge.sh test/launch_timeout_rerun.py \
        test/corpus_class2.timeout-rerun/   (if the merge produced a committed record there — per class-1 precedent, commit the merged rerun record)
git commit -m "corpus: class-2 package run (965/965) + A/B vs integrate baseline + 300 s timeout re-check"
```

---

### Task 11: Pilot close — the measured record, the runbook, the ledger

**Files:**
- Create: `docs/corpus-class2-baseline-uplift.md`, `docs/class-porting.md`
- Modify: `todo/TODO.md`

**Interfaces:**
- Produces: the milestone-2 acceptance record (measured claims,
  probes cited) and the runbook that makes classes 3-8 tickets.

- [ ] **Step 1: `docs/corpus-class2-baseline-uplift.md`**

Sections (write when the evidence exists — it does, from Tasks 1-10):
- **Header:** date, Maxima build (`build_info()` lines from the merged
  record), the milestone-2 branch + core fingerprint + rule count
  (3,180), the pilot's scope sentence.
- **Rule set:** 3 files / 125 rules (2.1=14, 2.2=4, 2.3=107), AUTO /
  MANUAL split from the census; the token closure table (Task 1
  output) with the two documented upstream gaps (PowerOfLinear family
  undefined; $UseGamma undocumented) and their port decisions.
- **Answer-side normalization:** the two rewrites with the measured
  conventions (the gamma_incomplete UPPER identity, the expintegral_ei
  identity) + the class-1 no-op proof (0 occurrences).
- **Baseline:** the integrate class counts (Task 9) + the % verified.
- **Package run:** the class counts (Task 10) + the % + the per-class
  A/B delta table + the timeout re-check transitions (Task 10 Step 4).
- **Residues:** the unverified/deferred/timeout masses by corpus file
  (2.1/2.2/2.3) with the first ~5 example entries each and their
  likely cause (rule coverage vs the 6 PowerOfLinear rules'
  semantics vs timeout) — the input to the follow-up tickets.
- **Class-1 status:** untouched (the byte-identity gate commits, the
  50-entry spot check, the no-op proof) — the explicit statement that
  the class-1 accepted record stands.
- **Ledger flags:** every shared-code change (driver normalization,
  core rebuild, launcher/merger shims) listed with its no-regression
  evidence.

- [ ] **Step 2: `docs/class-porting.md` — the runbook**

The repeatable process, step by step, as executed for class 2 (this is
the pilot's deliverable — classes 3-8 are tickets against it):
1. Census: `01-class1-syntax-census.py reference/rubi "<N> "` → committed
   `<n>-classN-syntax-census.out`; the token closure (new tokens →
   table entries or ports; upstream-undefined utilities → call-site
   contract + documented decline-safe semantics).
2. Table: RENAME additions (natives with the measured
   diff/float conventions; `%mr_` ports; `$`-globals → package
   variables), class-1 byte-identity gate.
3. Generator: `--class N` (no code change for a new class — that is
   the point); any new parser construct (like Part) added with a loud
   failure mode.
4. Utils ports: Layer A tests first (the red→green discipline), the
   cluster-per-commit shape.
5. Generate + static sanity greps (rule counts vs the census; no raw
   `$`; the renames landed).
6. Loader: the class-N block in `mr_load_all()` in LoadRules order;
   the core rebuild; the fingerprint mirror (BOTH sides, same sort).
7. Driver: the section's answer-head census → the `HEAD_REWRITES`
   entries (native, differentiable targets only — structural rewrites
   like F0→hypergeometric are a separate, measured decision); the
   class-1 (and earlier classes') no-op check.
8. Baseline: `probe-integrate-sample.py` over the section, T3
   mechanics, merged record, completeness assertion.
9. Package run: launcher + watcher + merger, completeness, A/B, the
   300 s timeout re-check.
10. Close: the uplift record, the residue analysis, the follow-up
    tickets.
Plus the standing constraints: the TLS flag, the 30 s cap, the
byte-identity gate for every class already accepted, the reading
protocol, the measured-claims discipline.

- [ ] **Step 3: `todo/TODO.md`**

Record milestone-2-pilot state per the file's conventions: the spec +
plan paths, the measured acceptance (the two % lines), the open
follow-ups (classes 3-8 as runbook tickets — the order from the
spec's follow-ups: 3 (logarithms, 3,085 entries), 8 (special, 1,949),
5 (inverse trig, 4,585), 6 (hyperbolic, 5,080), 7 (inverse hyperbolic,
6,552), 4 (trig, 22,472 — last); the polylog/AppellF1 residue
decision deferred to the first class that needs it), the PowerOfLinear
semantics revisit if Task 10's residue shows it.

- [ ] **Step 4: Final gates**

```
maxima --very-quiet -b test_maxima_rubi.mac        # Results: <total> passed, 0 failed
python3 generator/generate_rules.py --class 1 && git status --porcelain rules/   # EMPTY (the gate one last time)
python3 test/test_head_rewrites.py                 # 0 failed
```

- [ ] **Step 5: Commit**

```
git add docs/corpus-class2-baseline-uplift.md docs/class-porting.md todo/TODO.md
git commit -m "docs: milestone-2 pilot close — class-2 acceptance record + the class-porting runbook"
```

---

## Self-review notes (run when the plan is finished, per the skill)

- **Spec coverage:** process-first pilot (spec §Scope) → Tasks 1-11 in
  order; byte-identity gate → Tasks 2/3/8/11; two-sided normalization
  → Tasks 1 (evidence), 8 (mechanism), 11 (record); polylog/AppellF1
  ceiling → not in class 2 (measured: no rule emits them) — recorded in
  Task 11's runbook as a follow-class decision; runbook → Task 11
  Step 2; measured acceptance → Tasks 9/10; class-1 untouched →
  Constraints 4/5 + Task 8 Step 7 + Task 11.
- **Placeholder scan:** one intentional looseness, called out at its
  step: Task 6 Step 1's loose `foEF: sinh(b x)` check is tightened in
  Step 4 against the measured output (explicit, not a TBD). All other
  steps carry complete code.
- **Type consistency:** the state list `[flag, F, v]` is used with that
  exact order in every cluster-C function; `%mr_simp(e, [v])` 2-arg
  everywhere; `mr_sum(fun, var, lo, hi)` with a QUOTED var symbol in
  `%mr_functionExpand`; the `SLUG`/`SECTION`/`MERGED`/`DRIVER` argv
  order (section, out, driver) is consistent across launcher, merger,
  and the `wait_and_merge.sh` passthrough; `_core_fingerprint`'s file
  list matches `build_rules_core.sh`'s `FP` list (same four top files,
  same two globs, C-locale sorted) in Task 7 Steps 3-4.
- **Known risks (to watch at execution, not plan defects):** (a)
  `denom()`/`num()` on Maxima's `%mr_fullSimplify` output at the r61-
  r70 `FullSimplify` sites — if ratsimp rewrites the quotient into a
  non-quotient for some symbol shape, `denom` returns 1 and the rule
  mis-fires; the Layer A `fullSimplify: quotient keeps quotient` check
  and the class-2 run's 2.3 file outcome are the detectors. (b) The
  identity `NormalizePowerOfLinear` (Task 4) — bounded by the depth
  cap, but if Task 10 shows timeout mass in the 2.3 r8-r10 shapes, the
  revisit is already specced in the provenance comment. (c) `member()`
  on `op(u)` where `u`'s head is a quoted data symbol — the house
  rule 2 discipline (quote data symbols) is honored in
  `%mr_calculusQ` (`'unintegrable`).
