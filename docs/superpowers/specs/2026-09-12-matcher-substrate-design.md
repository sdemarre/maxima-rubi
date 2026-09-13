# Matcher substrate — design: classes 1–3 re-hosted on a Mathematica-semantics matcher

Date: 2026-09-12. Designed on branch `matcher-spike` (=
`class3-deferred` @ `d535e24` + the two matcher probe commits `1df41df`,
`adc55de`; `class3-deferred` is 34 commits ahead of `master` @ `1d998cc`
and unmerged). Measurements stamped Maxima
`branch_5_50_base_84_g4204fb669` (build date 2026-08-31 13:27:47) /
SBCL 2.6.7 / x86_64-pc-linux-gnu — the installed build, per the
AGENTS.md discipline — except where a record carries its own older
stamp (section 2.4). Design brainstorm with the user 2026-09-11/12
(handoffs `2026-09-11-matcher-design.md`,
`2026-09-12-matcher-design-brainstorm.md`).

## 0. Context

### 0.1 Why the matching substrate is replaced

User decision 2026-09-11, after an independent assessment of the
class-3 deferred campaign: close that campaign at its current state,
do **not** start class 4+ on Maxima's `defmatch`, and replace the
matching substrate with a Lisp matcher that has Mathematica semantics
(Optional defaults, Flat+Orderless backtracking), fed by the existing
generator; keep the ported predicates, shims, harness and records.

What `defmatch` costs the package today (this tree, counts in
section 2.3):

- three extra dispatch passes that exist only to compensate for the
  matcher — pass 2 reverse factor scan (`%mr_dispatch_rev`,
  `maxima_rubi_dispatch.lisp`), pass 3 implicit exponent-1 rescan
  (`maxima_rubi_implicit1.lisp`), pass 4 bare-factor sweep
  (`maxima_rubi_pass4.lisp`);
- 52 of the 3,514 generated rules emitted by hand-written workaround
  emitters (headvar, binpow, M1/B33, C5, C4, C3, C2) instead of a
  faithful pattern;
- `rubi_hybrid` / `rubi_hybrid_exact`, which keep passes 2–3 alive for
  the nested re-dispatches of the manually ported 9.1 file;
- the TLS special-variable wall: every process that loads rule files
  must run with `-X "--tls-limit 100000"` (AGENTS.md).

### 0.2 What the probes established

- **Spike 01, verdict FORK** (`probes/matcher/01-FINDINGS.md`):
  Fateman's mma4max `newmatch.lisp` loads into Maxima's SBCL with zero
  edits and binds 53/53 positive cases as Mathematica would, including
  every shape passes 2–4 and the re-transcriptions exist for; 3/15
  false matches share one root cause in `mblank1` (a one-line guard
  removes all three); `matchfol`'s Flat+Orderless search is
  exponential (~3× per extra term).
- **Probe 02, expressibility** (`probes/matcher/02-FINDINGS.md`): the
  7,444 Rubi Int rules use a narrow pattern language; with the
  `mblank1` guard, mma4max binds every valid witness in 7,403 / 7,444
  rules (99.45 %) and makes 0 false matches on 37,747 mutations. Gap
  list:

  | id | gap | size | disposition in this design |
  |---|---|---|---|
  | G-1 | Blank binds the identity of an empty Flat remainder | 519 rules false-match without the guard | structural fix in `match-flat` (3.2) |
  | G-2 | `F_[..]` / compound head directly under Plus/Times never matches | 41 rules | `m1` head match for such elements (3.2) |
  | G-3 | `Complex[re, im]` patterns | 9 LHSs, all class 4 | converter folds numeric `%i` terms; out of scope for the gate (class 4) |
  | G-4 | wrong bindings, `(a_.+b_.*F[u_])^p_.*(e_*x_)^m_.` family | 8 rules, classes 4/6 | named work item, exit criterion in 4 (P1) |
  | G-5 | Maxima's simplified form no longer Mathematica's shape | 312 rules, 1,142 witness variants | simplifier-flag A/B arm (3.3) |
  | G-6 | Optional-reduced Plus/Times item taking a run of the parent's elements | 1,919 rules' collapsed witnesses | narrow reading default, wide behind a switch (3.2, 3.6) |
  | G-7 | `remopts` rewrites one Optional per argument list | 0 rules | disappears with native Optionals |
  | G-8 | utility-only constructs never exercised | typed/sequence blanks etc. | only the MatchQ patterns classes 1–3 use, each unit-tested (3.4) |
  | G-9 | LHS evaluation before storage | 1,814 rules differ; 38 not emulated, all classes 4/8 | generator emits the evaluated form; loud failure on a risk rule (3.4) |

- **Probe 03, expression model on the corpus**
  (`probes/matcher/03-simp-flags.{mac,out}`,
  `probes/matcher/03-model-touch.py` + outputs; **uncommitted at the
  time of writing — fixed and committed in P0**, section 4): of the
  29,746 class 1–3 corpus integrands, 614 (2.06 %) are stored by Maxima
  in a non-Mathematica shape under default flags; 47 (0.16 %) under
  `radexpand:false` + `logexpand:false`; 42 (0.14 %) under
  `domain:complex` (section 2.2).
  *Erratum 2026-09-12 (P0 re-run, figures above kept as measured at
  writing):* the committed `probes/matcher/03-model-touch.out` reads
  615 of 29,747 (2.07 %) — the reader float fix un-failed one entry
  (e194); the committed flag-arm outputs read 48 (0.16 %,
  `03-model-touch.radexpand-logexpand.out`) and 43 (0.14 %,
  `03-model-touch.domain-complex.out`).

### 0.3 Decisions made in the brainstorm (user, 2026-09-11/12)

| topic | decision |
|---|---|
| scope | the substrate end to end: matcher core, converter, rule format/generator, dispatch; acceptance = classes 1–3 re-hosted at corpus parity with passes 2–4 deleted; class 4+ out of scope |
| approach | **A — mma4max-form island**: a forked matcher on Mathematica-form trees; integrand converted once per dispatch; bindings converted back into today's `mm` list; generated `_mr_cond_*`/`_mr_repl_*` and the utils unchanged in role. Rejected: B (port the matcher onto Maxima's internal form), C (own matcher from scratch) |
| rule source | regenerate every LHS faithfully from the pinned `.m` (evaluated FullForm); delete the workaround emitters; keep cond/RHS translation and genuine translation fixes |
| parity gate | full-corpus Record A/B vs the P0 baseline: every PASS→FAIL attributed and individually accepted; per-class PASS count does not drop |
| performance gate | no worse than today: 30 s cap unchanged; per-class median per-entry wall ≤ the P0 baseline's; every new timeout attributed |
| G-6 | narrow (documented) reading in `match-flat`; wide run-grouping behind a switch used only in the migration A/B; keep the winner, delete the other |
| G-5 | `radexpand:false` + `logexpand:false` as a migration A/B arm; keep the winner |
| condition retry | the matcher calls the condition hook on every complete binding (a false cond tries the rule's next binding); first-binding-only behind a switch for the A/B; keep the winner |
| baseline | re-measured in P0 on the current build and tree, not carried over from older-build records |

### 0.4 Precondition

The class-3 deferred campaign is closed first (endorsed follow-up,
2026-09-11): its working-tree class-3 record (`test/corpus_class3.out`,
2,058 PASS / 3,085, build 2026-08-31, uncommitted) is accepted with its
acceptance record, and the branch carrying it is the base of the
implementation branch (section 8). The migration's baseline is taken
after that close, so the rules being replaced are the settled ones.

## 1. Scope

**In**

1. `mr-match` — the forked matcher core (Lisp).
2. `mr-tree` — the Maxima ↔ Mathematica-form tree converter (Lisp).
3. The rule record format and its registration (`%mr_defrule`).
4. The generator's new pattern emission, the moved inner conditions,
   the MatchQ sites, and 9.1 as a generated source; deletion of the
   workaround emitters.
5. The Lisp dispatcher replacing `%mr_dispatch` and passes 2–4;
   `mr_top` edited in place; loader and rules-core changes.
6. Tests: matcher/converter unit tests, the round-trip regression suite,
   the Layer A rewrite, the Layer B migration A/B.
7. Documentation: the migration acceptance record, AGENTS.md, README,
   the `docs/class-porting.md` runbook revision.

**Out** (tracked separately)

- Class 4+ porting, including G-3 `Complex` patterns and the 38 G-9
  risk rules (all in classes 4/8 — `02-construct-census.out`, "LHS
  evaluation effects").
- Utility-function pattern constructs beyond the MatchQ patterns that
  classes 1–3 call (G-8 at large).
- A head index for dispatch, unless the performance gate fails (3.5).
- The other endorsed follow-ups of 2026-09-11: "package, then native
  `integrate`" user mode; an answer-quality (leaf-count) metric;
  right-sizing process and auditing recorded build quirks.
- Re-adjudication of the four class-3 doc claims the spike's reading
  contradicts (`01-FINDINGS.md` §doc-claims).

## 2. Measured basis

### 2.1 The matcher

- mma4max with the `mblank1` guard: 7,403 / 7,444 rules bind every
  valid witness, 0 false matches on 37,747 mutations; guard-mode single
  matches p50 0.021 ms, p99 0.41 ms, max 44.5 ms; preparing all 7,444
  patterns 2.04 s in total (`02-roundtrip.out`, `02-FINDINGS.md`).
- The 41 G-2 misses all carry a pattern-variable or compound head
  directly under Plus/Times; root cause `newmatch.lisp:757-759` →
  `matchfol` compares `op` with `eq` at `:1567`/`:1597` (controls
  H1–H8, `02-controls.out`).
- Pattern language facts the core is sized against
  (`02-construct-census.out`): exactly one Optional per argument list
  wherever Optionals occur (none as a Power base, none with an explicit
  default); largest Plus/Times argument count in an LHS pattern 5
  (30 rules); no `x_:v`, `x:pat`, `_?test`, in-pattern conditions,
  `Alternatives`, `Except`, `Repeated`, `HoldPattern`, `Verbatim`,
  sequence blanks or typed blanks other than `x_Symbol` on any LHS.
- Conditions riding next to the matcher (all 7,444 rules): 7,427 with
  an outer `/;`; 384 with a condition inside an RHS `With` (373) /
  `Module` (11); 47 rule conditions call `MatchQ`.
- A per-node census of Plus/Times pattern nodes (bare blanks and
  structured children per node) was run in the brainstorm session but
  is not committed; P0 adds it to `02-construct-census.py`. The design
  relies only on the committed facts above.

### 2.2 The expression model (G-5)

- Witness level (`02-roundtrip.out`, guard): Maxima's simplifier changes
  1,817 of 72,347 witness variants; 312 rules lose a match. Rewrite
  kinds: same heads other structure 793 (`(d*x)^(-1/3)` distributed),
  `+Abs` 597 (`(b*x^2)^p → b^p*abs(x)^(2p)`), `-Power` 213
  (`log(x^n) → n*log(x)`), `-Complex` 100, others ≤ 43.
- Corpus level (`03-model-touch*.out`, run 2026-09-11 22:41 UTC):

  | setting | class 1–3 integrands stored in a non-Mathematica shape |
  |---|---|
  | Maxima defaults (package and driver today) | 614 / 29,746 (2.06 %): product base of a non-integer power split 540, `abs` introduced 423, log of a power expanded 12, other 48 |
  | `radexpand:false` + `logexpand:false` | 47 (0.16 %) |
  | `domain:complex` | 42 (0.14 %) |

  *Erratum 2026-09-12 (P0 re-run; the table keeps the figures as
  measured at writing):* the committed outputs read 615 / 29,747
  (2.07 %) under defaults — split 540, `abs` 423, other structure 49,
  log of a power expanded 12, trig heads rewritten 2
  (`probes/matcher/03-model-touch.out`, SECTION ALL; the reader float
  fix un-failed e194) — 48 (0.16 %) under `radexpand:false` +
  `logexpand:false` and 43 (0.14 %) under `domain:complex`
  (`03-model-touch.{radexpand-logexpand,domain-complex}.out`).

- Flag behaviour (`03-simp-flags.out`): `radexpand:false` or
  `domain:complex` keeps `(b*x^2)^p`, `(x^2)^p`, `sqrt(x^2)`, `(2*x)^m`,
  `(d*x)^(-1/3)` whole; `log(x^n) → n*log(x)` is controlled by
  `logexpand:false` or `domain:complex`; `sin(-x) → -sin(x)` and
  `sec(%pi+x) → -sec(x)` are unconditional (Mathematica performs them
  too); `2*%i*x` has no complex-number atom under any setting.
- Inverting the splits in the converter is not viable: a split product
  is not uniquely reversible (`b^p*abs(x)^(2p)` has several
  pre-images).
- A flag acts only where an expression is simplified: inside the package
  (`mr_top` and below) and at the caller (`rubi(f, x)` receives `f`
  already simplified — the driver sets the flag before reading
  integrands).

### 2.3 Today's tree

All counts from `probes/matcher/04-tree-counts.out` (static text counts,
no Maxima run; git HEAD `adc55de`, counted files clean; re-run
`python3 probes/matcher/04-tree-counts.py > probes/matcher/04-tree-counts.out`).

- Generated rules 3,514 (class 1 3,055 = 2,710 LoadRules + 316 in the
  five `EXTRA_CLASS1` `b` files + 29 in the manual 9.1 port; class 2
  125; class 3 334).
- `defmatch` rules 3,462 (24,676 `matchdeclare` statements); the other
  52 use workaround emitters. Workaround helper call
  sites in rule files: `%mr_binpowfactors` 40, `%mr_mbp_base` 27,
  `%mr_logratio_match` 5, `%mr_headvar_match` 4, `%mr_logpow_match` 3,
  `%mr_logratio_sq_match` 2.
- Inner-condition guards (the `(if is(<inner>) = true then … else
  false)` form the generator emits into repl for a `/;` inside
  `With`/`Module`): 227 repl bodies — class 1 187, class 2 9, class 3 31.
- `%mr_matchQ`: 23 calls in 14 rule files; 9 call sites in
  `maxima_rubi_utils.mac` besides the definition (`:1121`) — 8 with a
  literal pattern (`:2383`, `:2398`, `:2415`, `:2421`, `:2439`,
  `:2460`, `:2647`, `:2811`) and one capture wrapper passing its pattern
  through (`:2519`).
- `rubi_hybrid` / `rubi_hybrid_exact`: 25 calls (outside comments) in
  `rules/class1/9_1.mac`.
- Layer A (`test_maxima_rubi.mac`, 892 checks) lines coupled to the
  current matcher: `_mr_pat_` 31, `defmatch` 11, `%mr_mbp_base` 14,
  `%mr_matchQ` 26, `matchdeclare` 3, `_mr_rule_` 3 (lines containing
  the token).

### 2.4 The records

| class | committed record | stamp | Results |
|---|---|---|---|
| 1 | `test/corpus_class1.out` (`f8d2fde`) | build 2026-08-20 21:36:22 | 20,069 passed, 5,628 failed |
| 2 | `test/corpus_class2.out` (`f8d2fde`) | build 2026-08-20 21:36:22 | 594 passed, 371 failed |
| 3 | `test/corpus_class3.out` (`f40d56b`) | build 2026-08-29 17:58:20 | 1,736 passed, 1,349 failed |
| 3 | working tree (campaign, uncommitted) | build 2026-08-31 13:27:47 | 2,058 passed, 1,027 failed |

No single build or tree covers all three classes; the parity and
performance baselines are therefore re-measured in P0 (section 4).
Records carry a per-entry wall (`t=` field), from which the medians are
computed.

## 3. Design

### 3.1 Architecture

Six units, each with one purpose and a narrow interface:

| unit | language | interface | depends on |
|---|---|---|---|
| `mr-match` | Lisp, own package | `(prepare pattern-sexp) → compiled`; `(match compiled tree &key bindings cond-hook) → binding alist or nil` | nothing Maxima |
| `mr-tree` | Lisp | `(max->tree expr) → tree`; `(tree->max tree) → Maxima expr (unsimplified)`; load-time head table | Maxima internals (read only) |
| rule records | generated `.mac` | `%mr_defrule(key, n, "<pattern>", cond-fn, repl-fn)`; `mr_rules_<key>` list | `mr-match` (prepare at load) |
| dispatcher | Lisp | `%mr_dispatch_tree(f, x, table, depth) → answer or false` | `mr-match`, `mr-tree`, Maxima `errcatch` semantics |
| generator | Python | unchanged CLI (`generate_class1.py`, class configure) | `generator/mma_reader.py` (promoted from probe 02) |
| harness | Maxima/Python | Layer A, matcher suite, Layer B driver | all of the above |

Data flow per top-level call: `rubi(f, x)` → `mr_top` (depth, loop
guard, flags) → dispatcher: `max->tree(f)` once → for each record in
LoadRules order, `match` with the condition hook → the hook converts
the bindings (`tree->max`, simplified once) into `mm`, runs cond → on
acceptance the dispatcher runs repl → first non-false answer wins;
`mr_int` calls in repl re-enter `mr_top`.

### 3.2 The matcher core `mr-match`

A fork of `newmatch.lisp` (local copy `reference/fateman/`, provenance
`PROVENANCE.txt`) without mma4max's parser, evaluator or simplifier.

- **Kept**: `m1` / `mlist` / `mpattern` / Blank handling — ordered heads,
  pattern-variable and compound heads, repeated names; sequence blanks
  are kept as mma4max has them and unit-tested only if a class 1–3
  MatchQ pattern uses one (no LHS does).
- **`match-flat` replaces `matchfol`** for Plus/Times:
  1. already-bound names consume their value's parts;
  2. structured pattern items claim one element each, filtered by head,
     with backtracking (≤ 5 items per node — section 2.1);
  3. leftover elements go to the unbound blank (≥ 1 element) and to the
     Optional (≥ 0 elements, default 0 under Plus, 1 under Times);
  4. split enumeration only for a node with two unbound bare blanks.
  - **G-1**: a Blank never binds from an empty remainder (structural,
    replaces the spike's `mblank1` guard).
  - **G-6**: the narrow reading is the default; the wide run-grouping of
    an Optional-reduced item is implemented behind the switch
    `mr_flat_wide` (3.6).
- **Native Optionals**: `match-flat` lets an Optional take nothing; a
  Power exponent `m_.` matches a non-Power through its base with m = 1.
  `fixopts` / `remopts` (Alternatives rewriting + `meval`) are deleted,
  which removes G-7 and is the prime suspect for G-4.
- **G-2**: an element with a pattern or compound head is matched through
  `m1`'s head match, never handed to the Flat search with its own head
  as the operator.
- **G-3**: `Complex[re, im]` patterns match the converter's complex atoms
  (class 4 need; implemented only if trivial, not gated).
- **G-4**: named work item; exit criterion in P1 (section 4).
- **No `meval`**: the call sites (`newmatch.lisp` 476/709 Condition,
  509/745 PatternTest, 595 `remopts`, 859/894/963 bound-name compares)
  are replaced — conditions and PatternTest call the dispatcher-supplied
  condition hook; bound-name checks are `equal` on canonical trees (the
  converter sorts Flat arguments).
- **Condition hook**: called on every complete binding; a false answer
  makes the matcher continue with the next binding (decision 0.3). With
  `mr_cond_retry` false the matcher stops after the first complete
  binding (today's `defmatch` behaviour).
- **Hygiene**: own package; no global `(speed 3) (safety 0)` proclaim;
  growable binding stack with an overflow check; local attribute table
  (Plus/Times Flat+Orderless); no `initialize-mma`.

### 3.3 The converter `mr-tree` and the expression model

- **`max->tree`**: `mplus`/`mtimes`/`mexpt` → Plus/Times/Power; `rat` →
  Lisp ratio; floats kept; `%e`/`%pi`/`%i` → `E`/`Pi`/`I`; other heads
  through a head table built at load from Maxima's own operators
  (`mabs` → Abs, `mfactorial` → Factorial, subscripted `li[n]` /
  `psi[n]` → PolyLog / PolyGamma, …); unknown heads → an unmatchable
  `MX_…` head; Flat arguments sorted by one total order; numeric `%i`
  terms folded into complex atoms (G-3). Nothing else is rewritten.
- **`tree->max`**: the inverse, used only for bindings, built
  unsimplified and simplified once.
- **Cost**: one integrand conversion per dispatch; binding conversion
  only on a complete match.
- **G-5**: the `mr_model_flags` switch (3.6) binds
  `radexpand:false` and `logexpand:false` inside `mr_top`; the driver
  sets them before reading integrands when the arm is on;
  verification by differentiation stays under Maxima defaults. The
  winning arm is kept and, if it is the flags arm, documented for
  users (a caller who simplifies `f` under defaults loses those
  shapes before `rubi` sees them).

### 3.4 The generator and the rule format

**Pattern emission.** The generator reads each rule with the reader
promoted from `probes/matcher/02-mma-reader.py` to
`generator/mma_reader.py` (self-test kept; the 02 probes import it from
there) and emits the LHS integrand as the **evaluated** FullForm
s-expression (`evaluate_lhs`, the round trip's notation). A rule whose
evaluation the reader flags as not emulated (G-9 `risk:`) is a
`GenError`; none are in classes 1–3.

**Registration.** One call per rule replaces the `matchdeclare` /
`defmatch` / `_mr_rule_*` block:

```
%mr_defrule("1_1_1_2", 1, "<evaluated FullForm s-expression>",
            _mr_cond_1_1_1_2_r1, _mr_repl_1_1_1_2_r1)$
```

The pattern string is parsed and prepared once, at load.
`mr_rules_<key>` becomes the list of the file's rule records in rule
order; `mr_rules_count_<key>` and the witness function stay.

**Captures.** The dispatcher builds today's `mm` list: Rubi pattern
variable `a` of rule `<key>` r`<n>` → `_mr_<key>_r<n>_a = value`.
`x_Symbol` is pre-bound to the integration variable before matching.
`geteqR` (`maxima_rubi_utils.mac:15`) and the `(mm, x)` signature of
cond and repl are unchanged, so every cond and repl body regenerates
byte-identical except for the closed list below.

**Conditions.** Outer `/;` conditions translate as today. The 227
inner conditions (a `/;` inside an RHS `With`/`Module`, section 2.3)
move from repl into cond: cond computes the locals and tests the
inner condition after the outer one; repl recomputes the locals and
builds the answer. Both therefore run under the condition hook and
take part in the binding retry.

**MatchQ.** The 23 generated sites emit
`%mr_matchQ(u, "<pattern s-expression>", lambda([%mr_mqb], <cond>))`;
`%mr_matchQ` becomes a thin Maxima entry over `mr-match` (pattern
prepared once and cached by string; the lambda runs as the condition
hook with the binding list). The 8 literal-pattern utility sites and the
capture wrapper (section 2.3) are rewritten to the same form. The
Maxima-side structural matcher behind today's `%mr_matchQ` (the
`%mr_mq_*` family) is deleted. Each distinct pattern used by these sites
gets a unit test (G-8).

**Deleted from the generator**: the headvar, binpow, M1/B33, C5
(R4/R8), C4, C3 and C2 (`dhead10`) emitters and their spec functions;
the bare catch-all special case; `nonzero_guard_caps` (the appended
`%mr_neQ(cap, 0)` degenerate-zero-binding guard — G-1 makes the
binding impossible); the `matchdeclare freeof(x)` declarations (the
translated cond already carries the `FreeQ`); the pattern-side
`translate` / `drop_optionals` path.

**Kept**: cond/repl translation, including `With`/`Module` locals and
the `Sum` lambda; the M-cas-simp translation fix (3.5 r10); ShowSteps
unwrapping; the source list — LoadRules classes 1–3, the five
`EXTRA_CLASS1` 1.2.1 `b` files at their table positions, and the 9.1
legacy file (`Rubi/IntegrationRules/9 Miscellaneous/9.1 Integrand
simplification rules.m`, absent from the pinned `Rubi.m` LoadRules,
needed by the 2018 corpus), which becomes a generated source at the
end of the class-1 table instead of a manual port. Its repl `Int` calls
translate to `mr_int` as everywhere else.

**Byte-identity exceptions (closed list)**: the 227 moved inner
conditions; the removed nonzero guards; the 23 MatchQ sites; the 29 9.1
rules; the 52 rules that had a workaround emitter.

### 3.5 Dispatch and runtime

**`mr_top`** keeps its shape: the depth counter (`%mr_max_depth` 16),
`%mr_seenp` with the `%mr_seen` push/pop, the `fb` semantics of both
fall-throughs (depth cap and seen guard), and the `rubi` /
`rubi_fallback` / `mr_int` API. The `%mr_dispatch` call becomes
`%mr_dispatch_tree`; the pass-2/3 blocks after it are deleted; with
`mr_model_flags` on, `mr_top` binds the two flags around the dispatch.

**The dispatcher, per call:**

1. `max->tree(f)` once; `x_Symbol` pre-bound.
2. Walk the table in LoadRules order; for each record run `match` with
   the condition hook.
3. The hook, per complete binding: build `mm` (bindings through
   `tree->max`, simplified once); reject an `mm` containing a boolean
   (`%mr_containsBoolean`, as today); run cond under `errcatch` —
   `is(r) = true` accepts; false, unknown or an error continues with
   the next binding (or, with `mr_cond_retry` false, ends the rule).
4. On acceptance run repl under `errcatch`: an error is a misfire (next
   rule); a result failing the `%mr_boolcheck` boolean-leak check is a
   misfire (next rule); a `false` result is a decline (next rule —
   expected to be unreachable once inner conditions live in cond);
   anything else is the answer.
5. A Lisp error inside `match` is caught and counts as no match for that
   rule; the process never dies on a matcher fault. `rubi_verbose`
   prints the rule id, the binding and the outcome.

**No head index in phase 1.** Every record is tried. Estimate, not a
measurement: at probe 02's 0.021 ms median per match, a full walk of
3,514 records costs about 70 ms per dispatch, less where rules reject at
the root. If the P5 median-wall gate fails, add a conservative root-head
index that may skip records but never reorders them; it must account
for Optionals (`a_.*x^m_.` matches a bare `x`, whose head is not
Times).

**Loading.** `maxima_rubi.mac` loads `mr-match` and `mr-tree` through
`%mr_load_sibling` with witnesses. Deleted: `%mr_declaim_matchvars` and
the declaim machinery in `maxima_rubi_dispatch.lisp`,
`maxima_rubi_implicit1.lisp`, `maxima_rubi_pass4.lisp`. The rules core
(option D) stays — compiling the cond/repl functions still costs load
time (measured in P4); its fingerprint file list, in
`test/build_rules_core.sh` and the driver's `_core_fingerprint()`, drops
the pass files and adds the matcher files. **TLS**: a flagless
`mr_load_all` and the whole Layer A run are measured; if both succeed,
the AGENTS.md flag rule is rewritten citing that measurement; if not,
the generator switches to shared capture names (cond/repl locals
reused across rules) and the measurement is repeated. The flag stays
mandatory until a measurement retires it.

**`rubi_hybrid` / `rubi_hybrid_exact`** are deleted if the P5 A/B shows
them unneeded: the regenerated 9.1 calls `mr_int`, as its `.m` source
calls `Int`. A PASS→FAIL in the collapse-rule family (the exact-mode
seen comparison exists for 1.2.1.3 e839) brings back the exact
comparison as a translation fix, not as a pass.

### 3.6 Migration switches

Three Maxima option variables, read by the dispatcher/matcher and set
by the driver, which writes them into each record's `filter:` line so
every A/B record states its arm:

| switch | default | alternative |
|---|---|---|
| `mr_flat_wide` | false (narrow G-6 reading) | true (wide run-grouping) |
| `mr_cond_retry` | true (hook on every complete binding) | false (first binding only) |
| `mr_model_flags` | true (`radexpand:false` + `logexpand:false`) | false (Maxima defaults) |

After P5 the winning behaviour of each is hard-wired and the switch and
the losing code are deleted (P6).

## 4. Phases and gates

Each phase ends green on its own gate before the next starts. Commands
follow AGENTS.md (Layer A with the TLS flag until P4 retires it; Layer B
sharded; Record A/B via `test/ab_records.py`).

**P0 — baseline and housekeeping.**

- Precondition 0.4 met (class-3 campaign closed).
- At that commit: build the rules core, run the full class 1, 2 and 3
  corpora on the current build, save as
  `test/corpus_class{1,2,3}.pre-matcher.out`; per-class median
  per-entry wall from `t=`; Layer A `Results: 892 passed, 0 failed`.
- Probe 03: fix the float `TypeError` in `02-mma-reader.key()` (2.3
  e194 L219), re-run the two flag-arm outputs after the head-map fix,
  commit. Add the Plus/Times node census to `02-construct-census.py`,
  re-run, commit.
- Gate: three merged records complete (25,697 / 965 / 3,085, no
  dupes/missing/extra); the P0 PASS counts and medians recorded in the
  migration ledger — these are the parity floor and the performance
  ceiling.

**P1 — matcher core.**

- `mr-match` per 3.2. The 02 round trip, the 02 controls and the
  spike-01 cases are retargeted from `newmatch.lisp` to `mr-match` and
  committed as the matcher regression suite under `test/matcher/`,
  ending in a `Results:` line. Unit tests for `match-flat` (both G-6
  arms), native Optionals, head matching, the condition hook (both
  retry arms), stack overflow.
- Gate (hard): 0 UNSOUND positives; 0 false mutation matches; the 41
  G-2 rules match every positive; the 8 G-4 rules 0 UNSOUND (else
  investigated and resolved before P2); rules with every positive OK
  ≥ 7,444 − 9 (G-3); tree-leg collapsed witnesses 0 UNSOUND under the
  narrow arm.

**P2 — converter.**

- `mr-tree` per 3.3, with round-trip unit tests (Maxima → tree → Maxima
  identity on simplified inputs; head table; complex folding;
  Flat-argument order).
- Gate: the round trip's Maxima leg runs through `mr-tree`; MODEL-LOST
  counts reported under defaults and under the flags arm (reference
  1,142 variants under defaults, section 2.2); no new MISS on the tree
  leg.

**P3 — generator.**

- Pattern emission, `%mr_defrule`, moved inner conditions, MatchQ sites,
  9.1 as a generated source, emitter deletions (3.4). Regenerate
  classes 1–3.
- Gate (a committed static-check script): rule counts per file
  unchanged (3,514 total); every cond and repl body byte-identical to
  the P0 tree except the closed exception list of 3.4; no `defmatch` /
  `matchdeclare` in any rule file; reader self-test green; the script
  lists every moved inner condition whose `With`/`Module` locals call
  `mr_int` (or another package entry), each resolved before P4.
- Between P3 and P4 the package does not run (the regenerated rule
  files need the P4 dispatcher); P3's gate is static only, and no
  Layer A or Layer B run is taken on a P3-only tree.

**P4 — dispatcher and loader.**

- `%mr_dispatch_tree`, `mr_top` edits, loader and core changes, passes
  2–4 deleted (the P0 commit and its pinned core are the rollback).
- Layer A: the matcher-coupled checks (section 2.3) rewritten against
  `%mr_defrule` / the dispatcher; matcher and converter checks added.
- Gate: Layer A green (new count recorded); the matcher regression
  suite green; flagless load + Layer A measured and recorded (3.5);
  load time and core build time recorded.

**P5 — migration A/B.**

- Four full class 1–3 runs: run 1 all defaults (narrow, retry on, flags
  on); runs 2–4 each flip one switch.
- Per switch, the arm with more PASS in every class wins; on a tie or a
  split across classes, the documented default wins (narrow, retry on)
  and for `mr_model_flags` Maxima defaults win (no user-visible
  setting). If the winners differ from run 1, one more full run of the
  winning combination is the final record.
- Gates on the final record against the P0 records:
  - `ab_records.py`: every PASS→FAIL attributed in the ledger and
    individually accepted by the user;
  - per-class PASS count ≥ P0;
  - per-class median per-entry wall ≤ P0 (else the head index of 3.5,
    then re-run);
  - every new timeout attributed; the 100 s timeout re-check run on the
    final record;
  - the matcher regression suite and Layer A green on the final tree.

**P6 — close.**

- Hard-wire the winners; delete the switches and losing code; delete
  `rubi_hybrid` / `rubi_hybrid_exact` if unneeded (3.5).
- Acceptance record `docs/matcher-substrate-migration.md` (measured,
  stamped, every claim citing a committed probe or record).
- AGENTS.md: TLS section (per the P4 measurement), Layer A count, the
  matcher suite command. README to the new state.
- `docs/class-porting.md`: Step 1 adds the pattern census and the G-9
  risk scan; Steps 3 and 5 describe pattern emission and the static
  check; Step 6 the loader, core and flag; Steps 8–10 keep their
  structure.
- Merge to `master` when the user says so.

## 5. Acceptance criteria

1. Classes 1–3 run on `mr-match` / `mr-tree` / `%mr_dispatch_tree`; no
   `defmatch`, `matchdeclare`, pass 2–4 code or workaround emitter
   remains in the package or the generator.
2. Final full-corpus records: per-class PASS ≥ P0; every PASS→FAIL
   attributed and accepted; per-class median per-entry wall ≤ P0; new
   timeouts attributed; 100 s re-check recorded.
3. Matcher regression suite: 0 UNSOUND, 0 false mutation matches, G-2
   closed, G-4 closed.
4. Layer A green; the static generator check green.
5. The TLS rule in AGENTS.md reflects a measurement taken on the final
   tree.
6. Acceptance record, AGENTS.md, README and runbook updated.

## 6. Risks and sharp edges

- **G-6 has no oracle.** Neither reading is verified against
  Mathematica; the A/B decides by corpus outcome, which measures
  usefulness, not faithfulness. The acceptance record states this.
- **Condition retry has no documented statement.** Wolfram's
  `Condition`, "Putting Constraints on Patterns" and "Flat and Orderless
  Functions" pages (read 2026-09-12) do not say whether a failing `/;`
  makes the matcher try another binding of the same rule; the indirect
  evidence is Rubi writing symmetric patterns once with asymmetric
  conditions. Retry can multiply cond evaluations on symmetric patterns
  — watched by the median-wall gate.
- **Model flags change nested simplification.** Binding
  `radexpand:false` / `logexpand:false` inside `mr_top` also changes how
  repl answers simplify; unverified answers under the arm are
  attributed in P5, not assumed benign.
- **G-9 emulation is unverified.** The evaluated LHS is the reader's
  emulation of Mathematica's evaluation; the risk list is empty for
  classes 1–3, but the emulated rewrites (numeric folding 1,058 rules,
  Power-of-Power 1,031, Sqrt → Power 941, distributed integer powers
  580) are trusted without a Mathematica run.
- **Moving inner conditions into cond** evaluates the locals twice on an
  accepted rule; a local that is expensive or has side effects (e.g.
  calls `mr_int`) is flagged by the P3 static check and handled
  individually.
- **Seen-guard interaction.** Faithful matching can change which rule
  fires first and therefore which intermediate integrands reach
  `%mr_seenp`; cycles the old passes never reached may appear —
  attributed in P5.
- **TLS may not disappear.** cond/repl block locals are still
  dynamically bound symbols; the fallback (shared capture names) is
  designed but its cond/repl byte-identity cost is paid only if needed.
- **Cost of P5.** Four to five full three-class runs; each class-1 run
  is ~80 min wall on 24 shards (AGENTS.md).

## 7. Deletions inventory

| artifact | phase |
|---|---|
| workaround emitters and spec functions in `generator/generate_rules.py` (headvar, binpow, M1/B33, C5, C4, C3, C2 `dhead10`, bare catch-all, `nonzero_guard_caps`, `matchdeclare` emission, pattern-side `translate`) | P3 |
| manual `rules/class1/9_1.mac` (replaced by the generated file) | P3 |
| the workaround utils families in `maxima_rubi_utils.mac` — `%mr_mbp_*`, `%mr_binpowfactors`, `%mr_lpfac`, `%mr_headvar_match`, `%mr_logpow_match`, `%mr_logratio_match`, `%mr_logratio_sq_match` — each only after a grep shows no ported predicate still calls it | P4 |
| the `%mr_mq_*` Maxima structural matcher (incl. `%mr_mq_capture_*`) | P4 |
| `%mr_dispatch` and the pass-4 sweep helpers `%mr_barefactors` / `%mr_p4_once` / `%mr_pass4_scan` (`maxima_rubi_utils.mac`) | P4 |
| `%mr_dispatch_rev`, `%mr_declaim_matchvars`, `mr-scan-matchvars` / `mr-declaim-matchvars` (`maxima_rubi_dispatch.lisp` — the `%mr_binomialQ` / `%mr_intBinomialQ` arity dispatchers stay) | P4 |
| `maxima_rubi_implicit1.lisp` (incl. its `findfun` shadow), `maxima_rubi_pass4.lisp` | P4 |
| losing switch arms, the switches | P6 |
| `rubi_hybrid`, `rubi_hybrid_exact` (if the A/B shows them unneeded) | P6 |

## 8. Process and branch

- Implementation branch `matcher-substrate`, cut after the class-3
  campaign close (0.4) from the branch that carries both that close and
  the two matcher probe commits (`1df41df`, `adc55de`). Whether
  `class3-deferred` is merged to `master` first is the user's call; the
  design does not depend on it.
- One commit per coherent step; ledger entries per phase; no push
  unless asked; no `git add -A` (the working tree carries untracked
  campaign logs and baselines).
- Next: `superpowers:writing-plans` produces the phased implementation
  plan from this spec.
