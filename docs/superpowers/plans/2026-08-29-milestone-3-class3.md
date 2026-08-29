# Milestone 3 — Class-3 (Logarithms) Port Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task.
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port Rubi section "3 Logarithms" (11 rule files, 333 rules;
3,085-entry corpus section) to `maxima-rubi` by executing the
class-porting runbook (`docs/class-porting.md`, Steps 1–10) end to end,
with measured A/B acceptance against the native `integrate` baseline
and the accepted class-1/class-2 records untouched (byte-identity
gate).

**Architecture:** Unchanged from milestones 1–2 — one generated `.mac`
per Rubi `.m` file, a flat ordered `mr_rule_table`, defmatch matching
at Maxima level with the custom `%mr_matchQ` structural matcher, the
saved rules core (option D), one fresh subprocess per corpus integral,
verification by differentiation. Class 3 adds: (a) **two new
answer-side native renames with a new arity dispatch** — the corpus
carries Rubi-notation heads `Chi(`/`Shi(`/`Si(`/`Ci(`/`Li(` (8/8/8/8/22
occurrences) that map to the bound, diff-known natives
`expintegral_chi/shi/si/ci` and `expintegral_li` (probed 2026-08-29);
`Gamma` becomes an **emitter-dispatched arity token** (1-arg → native
`gamma`, 2-arg → `gamma_incomplete` — the class-2 row stays);
(b) `LogGamma` as a structural rewrite to `log(gamma(v))` (the
build's `loggamma` is an undifferentiable noun — probed);
(c) `PolyLog` as a **1:1 rename to the native `polylog` spelling** —
the active corpus expected texts already carry native `polylog(`
(**1,195 of 3,085 entries, 2,793 occurrences** — the section's dominant
answer surface; the 10 `PolyLog[` lines a first grep found are
commented-out entries in bracket notation the driver never reads).
The build's `diff(polylog(·,·),·)` AND `polylog(·,numeric)` are nouns
(probed 2026-08-29), so a polylog entry's zero chain can close only
via the two-sided expected chain on a FORM-IDENTICAL answer (the
difference cancels to 0 before the diff — measured
`diff(polylog(2,-x)-polylog(2,-x),x) = 0`); the class-2-deferred
ceiling decision lands in Task 11 with this measured mass; (d) **a head-position pattern variable** (`F_[…]` in the two
3.1.5 rules) — a new generator pattern form emitting a structural
matcher rule with a `MemberQ` allow-list binding; (e) ~10 new `%mr_`
utility ports in two TDD clusters.

**Tech Stack:** Maxima — the installed build was **rebuilt
2026-08-29 17:58** (branch_5_50_base_84_g4204fb669, SBCL 2.6.7); the
AGENTS.md 2026-08-20 build stamp is superseded (Layer A re-verified
581/0 on the new core, 2026-08-29). Python 3 (generator, census,
driver, launcher). Pinned reference clones under `reference/`
(gitignored). All work on branch `milestone-3`.

## Global Constraints

These apply to every task.

1. **Build stamp.** All measurements run on the installed build
   (stamp via `build_info()`: version `branch_5_50_base_84_g4204fb669`,
   build date `2026-08-29 17:58:20`, SBCL 2.6.7). Do not pin; on
   upgrade, re-measure. The accepted class-1 (19,731/25,697) and
   class-2 (594/965 post-harness-port) records were measured on the
   2026-08-20 build and stand as stamped history; the class-3 A/B
   yardstick is the class-3 baseline measured in Task 9 on the current
   build (apples-to-apples by construction).
2. **TLS flag.** Any maxima process that loads rule files runs with
   `-X "--tls-limit 100000"` (two argv tokens).
3. **House rules** (milestone-1 plan, carried over): booleans through
   `is(…)`; no value-position comparisons; guards are value-carrying
   `if … then A else B`; no `filter`; fresh per-rule capture names;
   internal names carry `%mr_`, shims never take the native name; the
   package never prompts; noun discipline (`integrate(f,x)` fall-through
   noun vs `mr_int` recursion call vs the `unintegrable` corpus marker
   are never conflated); batch-parser traps (`rules` is protected;
   `;`/`$` terminate, a trailing `,` continues).
4. **Byte-identity gate for every already-accepted class.** After ANY
   change to `generator/generate_rules.py` or
   `generator/translation_table.py`: `python3 generator/generate_rules.py
   --class 1` and `--class 2` must leave `git status --porcelain rules/`
   EMPTY. Run it at Task 2 (table), Task 3 (generator), and once more at
   Task 11 close.
5. **The 30 s per-entry cap STAYS** (user decision 2026-08-27). The
   merged class-3 record's `timeout` class is re-run at the 100 s
   standing cap (Task 10) before acceptance is declared.
6. **Reading protocol.** Every Layer A run ends with
   `Results: <n> passed, <m> failed` — read that line; a mid-run death
   prints no Results line and is itself a failure. Every corpus merge
   asserts completeness 3,085/3,085 (no dupes/missing/extra).
7. **Git.** Default branch `master`; work happens on branch
   `milestone-3`; **never `git push`** (origin now exists but the
   runbook constraint stands); no `Co-Authored-By` trailers; one commit
   per task step group.
8. **Measured-claims discipline.** Every non-trivial claim cites a
   committed, re-runnable probe under `probes/`; counts and timings are
   stamped with date + `build_info()`.
9. **Run-flight rule.** Never modify rule files, the generator, the
   utils, or `test/mr_rules.core` while a sharded run is in flight
   (run-6 contamination lesson). Task 9/10 runs are launched only from
   a committed, gated tree.
10. **Runbook.** The step-by-step content, acceptance checks, and cost
    profile are `docs/class-porting.md` (Steps 1–10 + standing
    constraints); this plan is its class-3 instantiation. Where the two
    differ on a number, the re-measured class-3 value wins and the plan
    is corrected in place.

## Class-3 recon (pre-plan measurements, 2026-08-29)

Static census (the two committed records land in Task 1):

- **Rule set:** 11 files / **333 rules** / 332 with `/;` condition;
  AUTO 241 (72.4 %) / MANUAL 92 (27.6 %).
- **LoadRules order** (Rubi.m :211-221): 3.1.1, 3.1.2, 3.1.3, 3.1.4,
  3.1.5, 3.3, 3.4, 3.2.1, 3.2.2, 3.2.3, 3.5.
- **Corpus section** "3 Logarithms": **9 files** (3.1.1 and 3.1.3 have
  no corpus file — no class-1-style dead-sibling problem), **3,085
  entries**.
- **UNLISTIED tokens** (13): `PolyLog` (17 rules / 37 uses, repl),
  `InverseFunctionFreeQ` (13/17, cond), `F` (4/4 — a head-position
  pattern capture, not a function), `MemberQ` (4/4, cond), `FalseQ`
  (3/3, cond), `DerivativeDivides` (2/2, cond), `ProductQ` (2/2,
  cond), `Gamma` (1/1 repl + 1 pattern head, 3.5), `IntegralFreeQ`
  (1/1, cond), `LogGamma` (1/1 rule, 2 rhs uses, repl),
  `LogIntegral` (1/1, repl), `RationalFunctionExponents` (1/1,
  cond), `SubstForFractionalPowerOfLinear` (1/1, repl).
- **Answer heads in corpus expected texts:** `GAMMA(` 304 (all 2-arg),
  `Ei(` 220 (all 1-arg) — both already in the class-2
  HEAD_REWRITES; new: `Chi(` 8, `Shi(` 8, `Si(` 8, `Ci(` 8 (all
  1-arg), `Li(` 22 (1-arg); **the active expected texts carry the
  native `polylog(` spelling — 1,195 of 3,085 entries / 2,793
  occurrences** (per file: 3.1.2: 0, 3.1.4: 187, 3.1.5: 179, 3.2.1:
  91, 3.2.2: 106, 3.2.3: 65, 3.3: 243, 3.4: 237, 3.5: 87; orders
  2/3/4/5/6 + symbolic `k`/`n`/`1±k`), while Rubi-notation `PolyLog(`
  paren occurrences in active entries = 0 (the 10 `PolyLog[` lines a
  first grep found are COMMENTED-OUT entries in bracket notation —
  the driver reads only `[`-leading active lines); native `erf(` 14 /
  `erfi(` 137 / `%e^` 790; **no** `LogGamma`/`LogIntegral`/
  `ProductLog` in any expected text.
- **Native conventions probed on the current build (2026-08-29):**
  `diff(expintegral_shi(x),x)=sinh(x)/x`,
  `diff(expintegral_chi(x),x)=cosh(x)/x`,
  `diff(expintegral_si(x),x)=sin(x)/x`,
  `diff(expintegral_ci(x),x)=cos(x)/x` — all four bound, float
  evaluable; `diff(expintegral_li(x),x)=1/log(x)` bound; **short
  names `shi/chi/si/ci` are UNBOUND nouns** (the naming trap — use the
  `expintegral_*` long forms); `gamma` bound,
  `diff(log(gamma(x)),x)=psi[0](x)` (known); `loggamma` unbound noun
   with undifferentiated diff; **`diff(polylog(2,x),x)`,
   `diff(polylog(s,x),x)`, `polylog(2,0.5)` and `polylog(3,0.5)` all
   stay nouns** (no symbolic derivative, no numeric eval), while
   `diff(polylog(2,-x) - polylog(2,-x), x) = 0` — the difference of
   form-identical polylog terms cancels before the diff, so the
   two-sided expected chain closes on a form-identical answer and the
   self-diff chain never closes on a polylog answer; `psi(x,0)` is
   bound (2-arg) but its own diff is a noun.
- **Existing ports reused:** `%mr_inverseFunctionQ` (utils :3091),
  `%mr_calculusQ` (utils :4575), `%mr_freeFactors`/`%mr_nonfreeFactors`
  (utils :2754/:2771), `%mr_substFor`/`%mr_substPower` (M1),
  `%mr_polynomialQ`, `%mr_sumQ`, `%mr_rationalFunctionQ`,
  `%mr_degree` (Exponent), `%mr_matchQ`, the 3-arg `%mr_coeff`,
  `mr_int`/`%mr_dist`/`%mr_simp`.
- **`.m` line refs for the utility ports:** ProductQ :170-172;
  InverseFunctionFreeQ :316-322 (uses InverseFunctionQ :303 /
  CalculusQ :283 over the `$CalculusFunctions` global :282);
  IntegralFreeQ :351-353; RationalFunctionExponents :1618-1633;
  SubstForFractionalPowerOfLinear :6056-6064 over
  FractionalPowerOfLinear :6067 + SubstForFractionalPower :1874;
  DerivativeDivides :7450-7463 over EasyDQ :7466-7480.
- **Head-position pattern variable** (the two 3.1.5 rules, .m L62-63):
  `Int[Px_*F_[d_.*(e_+f_.*x_)]^m_.*(a_+b_.*Log[c_.*x_^n_]), x]` with
  `MemberQ[{ArcSin,ArcCos,ArcSinh,ArcCosh},F]` (L62) /
  `MemberQ[{ArcTan,ArcCot,ArcTanh,ArcCoth},F]` (L63) — `defmatch`
  rejects head-position pattern variables (the class-2 r96 finding),
  so these emit structural matcher rules; the repl builds the
  `F[…]^m` call from the bound head.

## Task 1: Census (runbook Step 1)

**What.** Commit the two static census records for class 3 and complete
the token closure table. No Maxima.

- [ ] Write `probes/translation/04-class3-syntax-census.run` (copy of
      the 03-class2 driver, `python3 probes/translation/01-class1-syntax-census.py
      reference/rubi "3 "`, date-stamped) and run it →
      `probes/translation/04-class3-syntax-census.out`.
- [ ] Write `probes/corpus/03-class3-answer-heads.py` (copy of the
      02-class2 probe, default section `"3 Logarithms"`, **HEADS list
      extended with `"PolyLog"`** (documents the Rubi-paren-notation
      count in active entries — measured 0) and **NATS list extended
      with `"polylog("** (the active native spelling — 2,793
      occurrences)), `.run` driver, and run it →
      `probes/corpus/03-class3-answer-heads.out`.
- [ ] Verify the records against the recon values above (11 files /
      333 rules / AUTO 241 / MANUAL 92; answer heads GAMMA 304 {2:304},
      Ei 220 {1:220}, Chi/Shi/Si/Ci 8 each, Li 22, `PolyLog(` 0 /
      `polylog(` 2793 over 1,195 of 3,085 entries, entries 3085). Any
      mismatch is a probe/parse defect — fix and re-run (the recon
      values came from the same scripts).
- [ ] **Token closure** — every UNLISTIED token adjudicated (this plan's
      recon section is the adjudication; record it in the report):
      `PolyLog` → 1:1 RENAME `polylog` (the active corpus expected
      texts are natively spelled — 1,195 entries / 2,793 occurrences;
      the build's polylog diff and numeric eval are nouns, so the
      entries close only via the two-sided expected chain on
      form-identical answers — the Task-11 ceiling decision carries
      this mass);
      `LogGamma` → structural `log(gamma(v))`; `LogIntegral` →
      `expintegral_li`; `Gamma` → arity-dispatched (1-arg `gamma` /
      2-arg `gamma_incomplete`); `Chi/Shi/Si/Ci` → the
      `expintegral_*` natives (answer-side renames; no rule emits
      them — they appear only in corpus expected texts, so NO table
      rows, only Task-8 HEAD_REWRITES rows); `Li` → likewise
      (HEAD_REWRITES row only); `InverseFunctionFreeQ`, `MemberQ`,
      `FalseQ`, `ProductQ`, `IntegralFreeQ`,
      `RationalFunctionExponents`, `DerivativeDivides`,
      `SubstForFractionalPowerOfLinear` → `%mr_` ports (Tasks 4–5);
      `F` → the head-position pattern capture (Task 3 form, not a
      table token). No other U tokens exist.
- [ ] Commit: `probes: class-3 census (11 files / 333 rules; answer heads
      for the class-3 HEAD_REWRITES)`.

**Acceptance.** Both `.out` committed with date stamps, matching the
recon headline; closure table complete (13/13 U tokens adjudicated);
rule counts match the T1 inventory convention (files = Rubi.m
LoadRules list).

## Task 2: Translation-table additions (runbook Step 2)

**What.** `generator/translation_table.py` gains the class-3 rows; each
new answer-side native is probed in the installed build first (the
recon already probed them — re-verify in-task and cite in the table
comment, the house "naming trap" rule).

- [ ] RENAME rows: `"Chi": "expintegral_chi"`, `"Shi":
      "expintegral_shi"`, `"Si": "expintegral_si"`, `"Ci":
      "expintegral_ci"` (four are needed for completeness of the closed
      table — they are not in the class-3 rule token set, but the table
      is the closure; if the generator never sees them the rows are
      inert — record that), `"LogIntegral": "expintegral_li"`,
      `"InverseFunctionFreeQ": "%mr_inverseFunctionFreeQ"`,
      `"MemberQ": "%mr_memberQ"`, `"FalseQ": "%mr_falseQ"`,
      `"ProductQ": "%mr_productQ"`, `"IntegralFreeQ":
      "%mr_integralFreeQ"`, `"RationalFunctionExponents":
      "%mr_rationalFunctionExponents"`, `"DerivativeDivides":
       "%mr_derivativeDivides"`, `"SubstForFractionalPowerOfLinear":
       "%mr_substForFractionalPowerOfLinear"`, `"PolyLog": "polylog"`
       (1:1 — the active corpus expected texts are natively spelled,
       2,793 occurrences; the build's `diff(polylog(·,·),·)` is a noun,
       so no spurious self-diff closure; the comment cites the probe).
- [ ] `Gamma` arity dispatch: the emitter dispatches `Gamma` by
      argument count — 1-arg → `gamma`, 2-arg → `gamma_incomplete`
      (the existing row's behavior for class 2 is unchanged; implement
      like the PolyQ emitter dispatch, with a loud failure on any
      other arity).
- [ ] RESTRUCTURE rows: `"LogGamma": "loggamma"` — the handler emits
      `log(gamma(<arg>))` (probe: `diff(log(gamma(x)),x) = psi[0](x)`
      closes; `loggamma` is an undifferentiable noun — both probed
       2026-08-29).
- [ ] **Byte-identity gate:** `python3 generator/generate_rules.py
      --class 1` and `--class 2`, `git status --porcelain rules/` EMPTY
      for both. (The new rows are class-3-only tokens; the arity
      dispatch must leave every class-1/2 emission byte-identical —
      class 2's 5 `Gamma` uses are all 2-arg.)
- [ ] Commit: `generator: class-3 translation rows (expintegral_*
      answer natives, Gamma arity dispatch, LogGamma restructure,
      PolyLog rename, %mr_ port names)`.

**Acceptance.** Table closed for every class-3 token (the Task-1
closure); gates green; class-1/2 regeneration byte-identical.

## Task 3: Generate + the head-position pattern variable (runbook Step 3)

**What.** `python3 generator/generate_rules.py --class 3` completes with
zero unlisted tokens; the four head-position `F_[…]` rules emit through
a new structural pattern form. RECON CORRECTION (2026-08-29, Task 3
review): the census "C-tier token examples" section lists the first
rule(s) per token, which showed only 3.1.5 — the `.m` sources actually
carry four head-position capture rules: 3.1.5 L62–63 (lin arg;
free-m / bare), 3.3 L62 (lin arg, bare, lpow log arg, all-eight
allow-list), 3.4 L41 (monomial arg, free-m, bpow log arg, no Px
slot). The detection is generic (capture followed by `[` in the lhs
head position), so all four are emitted by the same mechanism; an
optional-form capture (`F_.[`) is a loud GenError (class 3 uses only
the required form — grep-verified zero `_.[` in the eleven .m files).

- [ ] Pre-check: run the generator; every failure is a
      `GenError`-naming the file/rule/token (loud-failure gate) — fix
      table/generator gaps as they surface, re-run until clean.
- [ ] **Head-position capture form.** `defmatch` rejects
      head-position pattern variables (class-2 r96, 5.50.0). The
      generator detects a capture immediately followed by `[` in the
       lhs (the 3.1.5 / 3.3 / 3.4 shape) and emits a structural rule: a
      generated `%mr_`-prefixed matcher call (new helper in
      `maxima_rubi_utils.mac`, e.g. `%mr_headvar_match(f, x,
      [slot-specs], allowed-heads)`) decomposes the integrand's
      product factors, binds the pattern slots (Px / the `F[d(e+fx)]^m`
      factor / the `(a+b log(c x^n))` factor), tries each allowed head
       from the rule's `MemberQ[{...}, F]` list (ADJUDICATED 2026-08-29:
       the pattern-side allow-lists use the NATIVE bound spellings for
       all eight — asin/acos/atan/asinh/acosh/atanh/acot/acoth are bound
       natives with closed diffs, arccot/arcoth are unbound nouns —
       probed; the pattern side is spelling-agnostic but the answer side
       carries the bound symbol, so a noun head could never close the
       zero chain; the RENAME table's %mr_ hyperbolic shims stay for
       class 1–2 answer-side byte-identity, and the new table rows are
       ArcCot→acot, ArcCoth→acoth), and binds `F` to the
      matched head symbol. The repl builds the `F[…]`/`F[…]^m` call
      from the bound symbol (`apply(F, [arg])` idiom — probe). A
      head-position capture WITHOUT a `MemberQ` allow-list in cond is a
      loud `GenError` (no silent pass-through). Layer A tests for the
      helper: positive (both allow-lists, m = 1 and m > 1), negative
      (head outside the list, non-linear argument, wrong factor
      count), and a no-op self-match guard (the bound integrand
      re-dispatch must not loop — the seen-guard covers it; assert
      decline on a non-matching integrand).
- [ ] **TDD for the helper:** failing Layer A checks first (RED, read
      the line), implement, GREEN. The helper's Layer A checks are
      written in this task (it is a matcher, not a utils port — it
      ships with the generator form).
- [ ] Generation completes: 11 files / 333 rules (per-file counts per
      the Task-1 census). The generated-header Regenerate line carries
      the `--class 3` form (the M2 class-gate).
- [ ] Static spot checks on the 3.1.5 / 3.3 / 3.4 files: the structural
      emission is present (4 rules: 3.1.5 r58+r59, 3.3 r58, 3.4 r37),
      the `MemberQ` allow-lists are the translated native head lists,
      no raw `$[A-Za-z]`, no `_mr` name corruption (the M1
      drop_optionals bug class).
- [ ] **Byte-identity gate** (generator changed): classes 1 and 2
      regenerate EMPTY porcelain.
- [ ] Commit: `generator: class-3 generation + head-position capture
      (F_[...] structural form)`.

**Acceptance.** Zero unlisted tokens; 333/333 emitted; Layer A green
(new checks included); gates green; the four `F_[…]` rules visibly
structural.

## Task 4: Utils ports — cluster A, small predicates (runbook Step 4)

**What.** The cond-side predicate ports, TDD red→green per the runbook:
write the failing checks in `test_maxima_rubi.mac`, run (RED),
implement in `maxima_rubi_utils.mac`, run (GREEN).

- [ ] **RED:** add Layer A checks for `%mr_memberQ` (list/element,
      both polarities; the arg order is `MemberQ[list, elem]` → Maxima
      `member(elem, list)` — probe the built-in), `%mr_falseQ`
      (u = false; probe how Maxima stores `false` — the atom boolean),
      `%mr_productQ` (op(u) = "*" non-atom; a sum/atom → false),
      `%mr_integralFreeQ` (freeof over the `integrate`/`int`/
      `unintegrable`/`CannotIntegrate`-marker surface — map the four
      .m heads to the package nouns and record the mapping),
      `%mr_inverseFunctionFreeQ` (the .m :316 recursion over
      InverseFunctionQ/CalculusQ/Hypergeometric2F1/AppellF1 — reuse
      `%mr_inverseFunctionQ` + `%mr_calculusQ`; the Hypergeometric2F1 /
      AppellF1 head tests are string(op) checks),
      `%mr_rationalFunctionExponents` (the .m :1618 branch ladder:
      polynomial → {deg, 0}; integer power → scaled/Reversed recursion;
      product → list sum; sum → Together-then-recursion with the
      Max[lst1.1+lst2.2, lst2.1+lst1.2] numerator form; else {0,0} —
      line-port with the Maxima `ratsimp`/`together` noun traps from
      the M1 ledger; test all five branches on the pinned shapes).
- [ ] **GREEN:** implement the six `%mr_` functions (house rules:
      atom-gate before `op()`, `is()` booleans, `for i : 1 thru
      length(L)` iteration, no value-position comparisons). Every
      measured build quirk stamped in-code with date + build.
- [ ] Commit: `utils: class-3 cluster A predicates (memberQ, falseQ,
      productQ, integralFreeQ, inverseFunctionFreeQ,
      rationalFunctionExponents)`.

**Acceptance.** Layer A green at the cluster end (Results line read);
RED→GREEN counts in the report; the .m line citations verified against
the pinned clone.

## Task 5: Utils ports — cluster B, fractional-power Subst family
(runbook Step 4)

**What.** The heavy substitution ports, TDD red→green.

- [ ] **RED:** Layer A checks for `%mr_easyDQ` (the .m :7466-7480
      ladder — the `u_*x_^m_` product case with FreeQ[m,x], the
      atom/free-of-x/empty True arm, the CalculusQ False arm, the
      Length[u] == 1 arm, the recursive else — pin each arm),
      `%mr_derivativeDivides` (the .m :7450 contract: `a_*x` → false;
      polynomial-u with matching Exponent or EasyD[y,x]; v = 0 →
      false; `Simplify[u/v]` free of x → the quotient, else false —
      the Simplify = `%mr_simp` reading; test the quotient-return
      shape and the decline), `%mr_fractionalPowerOfLinear` (the .m
      :6067 contract: finds `(a+b x)^(m/n)` with n > 1 integer →
      {n, a+b x}, else false — pin the n > 1 / m-integer guards),
      `%mr_substForFractionalPower` (the .m :1874 contract — read the
      full .m definition first; it is the fractional-power twin of the
      ported SubstFor), `%mr_substForFractionalPowerOfLinear` (the .m
      :6056 contract: {v, n, a+b x, 1/b} over
      FractionalPowerOfLinear + SubstForFractionalPower +
      `%mr_nonfreeFactors`/`%mr_freeFactors` (both ported) +
      `x^(n-1)` times; False decline when no fractional linear power
      is present).
- [ ] **GREEN:** implement over the existing helpers; the 3.5 r16
      call-site shape (RFx*(a+b Log[u]) with a fractional linear power
      in the base) gets an end-to-end Layer A check on a concrete
      integrand (e.g. (a+b log(x^(2/3))) * (x+1) — pick the shape the
      .m's own examples use; the returned 4-list pinned element-wise).
- [ ] Commit: `utils: class-3 cluster B (easyDQ, derivativeDivides,
      fractionalPowerOfLinear, substForFractionalPower,
      substForFractionalPowerOfLinear)`.

**Acceptance.** Layer A green; RED→GREEN counts; the 4-list contract
pinned on a concrete shape.

## Task 6: Regenerate + static sanity (runbook Step 5)

**What.** Regenerate class 3 with the final table + utils names; grep
the committed files.

- [ ] `python3 generator/generate_rules.py --class 3` — per-file
      `defmatch`/structural-rule counts equal the census (333 total;
      per-file per Task 1).
- [ ] **No raw `$[A-Za-z]`** in any `rules/class3/*.mac` (`$`
      terminates a Maxima reader line — a passed-through `$UseGamma`-
      class token is a guaranteed parse failure).
- [ ] Rename spot counts: `expintegral_li` present (the 3.1.1
      LogIntegral rule), `log(gamma(` present (the 3.5 LogGamma
      rule's repl), `polylog(` emitted (the 17-rule / 37-use PolyLog
      surface), no `PolyLog(` Rubi-notation anywhere,
      `expintegral_{shi,chi,si,ci}` occurrences = 0 (no rule emits
      them — the HEAD_REWRITES are the corpus-side).
- [ ] The parse sweep (the M1 parse-sweep probe form over
      `rules/class3/*.mac`) is clean — every file parses in a fresh
      Maxima (with the TLS flag).
- [ ] Commit (if regeneration changed bytes): `rules: class-3
      regenerated (statics)`.

**Acceptance.** Counts = census exactly; 0 raw-`$` hits; parse sweep
11/11 clean.

## Task 7: Loader + rules core (runbook Step 6)

**What.** Wire class 3 into the load chain and rebuild the core.

- [ ] `mr_load_all()` in `maxima_rubi.mac` gains the class-3 block in
      the LoadRules order (3.1.1 → 3.1.2 → 3.1.3 → 3.1.4 → 3.1.5 →
      3.3 → 3.4 → 3.2.1 → 3.2.2 → 3.2.3 → 3.5), after all of class 2.
- [ ] **Fingerprint mirror, BOTH sides, same sort** (the
      runbook's only mechanical harness change): `test/build_rules_core.sh`
      `FP` list gains `rules/class3/*.mac`; `test/corpus_driver.py`
      `_core_fingerprint()` gains the same glob (C-locale sorted, same
      top files). A mismatched core is a loud driver failure.
- [ ] `bash test/build_rules_core.sh` — rebuild; the stamp's rules
      count = 3,180 (class 1+2) + 333 = **3,513**; record the
      fingerprint.
- [ ] TLS full-table probe: `sh probes/load_wall/probe-class3-load.run`
      (copy of the class-2 probe, section-agnostic load of the full
      table under the TLS flag) → committed `.out` printing
      `TABLE_AT_LOAD 3513`.
- [ ] Census spot check (the M2 form): a class-3 file's rule count via
      the table, a witness integrand firing a class-3 rule, and a
      class-1 witness (1.1.1.1 r1) still firing.
- [ ] Layer A green (581 + the class-3 Task 3/4/5 checks).
- [ ] Commit: `loader: class-3 block + core (3513 rules, fingerprint
      <stamp>)`.

**Acceptance.** Stamp agrees with the driver fingerprint; probe
`TABLE_AT_LOAD 3513`; Layer A green.

## Task 8: Driver normalization (runbook Step 7)

**What.** `HEAD_REWRITES` in `test/corpus_driver.py` gains the class-3
rows; unit tests; no-op proof for the accepted classes.

- [ ] New rows (native, differentiable targets only — each probed in
      Task 2): `Chi(` → `expintegral_chi(`, `Shi(` →
      `expintegral_shi(`, `Si(` → `expintegral_si(`, `Ci(` →
       `expintegral_ci(`, `Li(` → `expintegral_li(`. **No polylog row**
       (the package emits the native `polylog(` spelling and the
       active corpus expected texts are already natively spelled; the
       commented-out `PolyLog[` bracket lines are never read by the
       driver).
      Lookbehind guards per the existing rows (the atom-charset
      lookbehind keeps longer names intact — add negative unit cases:
      `expintegral_li(` itself, `expintegral_si(` vs a `Si(` inside
      `...Si(`, and the existing `GAMMA(` row must not fire inside
      `LogGamma(`).
- [ ] Unit tests in `test/test_head_rewrites.py`: positive + negative
      per new row (pure Python, the existing shape).
- [ ] **No-op check for every accepted class:** run the driver over a
      slice of class 1 AND class 2 sections — the record header prints
      `head rewrites: {}` for the class-1 slice (0 renamable heads) and
      the class-2 slice shows only the existing two rows; an N-entry
      spot check (the M2 50-entry form, per class) classifies
      **identical** to the accepted merged records
      (`test/corpus_class1.out`, `test/corpus_class2.out`). NOTE
      (constraint 1): the spot check compares classifications
      re-measured on the 2026-08-29 build against records measured on
      the 2026-08-20 build — any diff is triaged build-drift vs
      normalization-drift and recorded in the report (a
      normalization-caused diff is a Task-8 defect; a build-drift diff
      on the rebuild is recorded, and the slice is re-run on the
      old-build core if available to confirm).
- [ ] Commit: `driver: class-3 HEAD_REWRITES (expintegral_shi/chi/si/
      ci + expintegral_li rows) + no-op proof for classes 1-2`.

**Acceptance.** Rewrite unit 0 failed; no-op checks green for classes
1 and 2; spot check N/N both classes.

## Task 9: Baseline — native `integrate` (runbook Step 8)

**What.** The T3 probe mechanics over the 9-file section, 30 s cap,
one process per file (or shard), merged with the generalized merger.

- [ ] Three per-file-group shards (START/STOP file indices into the
      section's sorted file list, STOP exclusive): (0,3), (3,6), (6,9)
      — `python3 probes/corpus/probe-integrate-sample.py "3 Logarithms/"
      999999 30 reference/maxima-syntax-test-suite <start> "" 0
      test/corpus_class3.baseline.shardNN.out 1 "3 Logarithms" &` (the
      M2 command form; the relative suite-dir positional is
      load-bearing — the Task-9 M2 merger/launcher fix).
- [ ] Merge: `python3 test/merge_class_shards.py "3 Logarithms"
      test/corpus_class3.baseline.out test/corpus_driver.py
      "corpus_class3.baseline.shard*.out"` — completeness asserted
      3,085/3,085.
- [ ] Read the Results line; record the per-class tally.
- [ ] Commit: `corpus: class-3 integrate baseline (3085 entries,
      <tally> PASS)`.

**Acceptance.** Merged record with build-stamped header
(2026-08-29 build — the A/B yardstick, constraint 1); 3,085/3,085;
Results line read. The yardstick's mechanics note (probe 4-stage
symbolic chain, no head rewrites, noun-on-answer-expected = PASS
no-answer — the yardstick errs slightly conservative for the package)
carries into the Task-10 readout.

## Task 10: Package run + A/B + timeout re-check (runbook Step 9)

**What.** The package run over the section, the full A/B, the 100 s
re-check.

- [ ] Launch (from the gated Task-7/8 tree, constraint 9):
      `python3 test/launch_class_shards.py "3 Logarithms"
      test/corpus_class3.out test/corpus_driver.py --launch` +
      `setsid sh test/wait_and_merge.sh test/corpus_class3.shard-pids
      test/merge_class_shards.py test/class3_merge.out "3 Logarithms"
      test/corpus_class3.out test/corpus_driver.py
      "corpus_class3.shard*.out" &`. First run for the section: the
      cost model falls back to count-balancing (no prior record).
- [ ] Merge; completeness 3,085/3,085; read the Results line.
- [ ] **Full A/B vs the Task-9 baseline** — per verdict class +
      entry-level (rel,entry)-keyed comparison of the two records' T3
      lines (PASS = {expected, verified, no-answer}); every PASS→FAIL
      remainder triaged into genuine declines vs yardstick
      reclassification (the M2 178/131 worked-example method); the
      yardstick mechanics note quoted in the readout.
- [ ] **100 s timeout re-check** on the record's `timeout` class:
      `python3 test/launch_timeout_rerun.py test/corpus_class3.out 100
      test/corpus_class3.timeout-rerun "3 Logarithms" --launch` + the
      watcher; read the transitions (now-PASS = slow-correct;
      still-timeout = genuine non-terminators; error = death census —
      a reproducible build bug is its own ticket).
- [ ] Commit the merged record + re-check record: `corpus: class-3
      package run (3085 entries, <tally>) + 100s re-check`.

**Acceptance.** Record committed, completeness N/N; A/B remainders
triaged (none unexplained); re-check record committed with the
transitions read.

## Task 11: Close (runbook Step 10)

**What.** The acceptance record, the residue analysis, the TODO
entry, the final gates.

- [ ] `docs/corpus-class3-baseline-uplift.md` in the class-2 record's
      shape (header / rule set / normalization / baseline / package
      run with per-class A/B + re-check transitions / residues /
      earlier-class status / ledger flags).
- [ ] **Residue analysis:** FAIL masses per corpus file, ~5 sample
      entries each with T3-line timing, likely-cause classification
      (rule coverage vs ported-semantics decisions vs measured build
      bugs — "likely" where a guess); the residue → expected-head
      census.
- [ ] **The polylog/AppellF1 structural-ceiling decision, now with
      class-3 numbers** (the M2-deferred decision): the polylog mass is
      **1,195 of 3,085 entries (38.7 %) / 2,793 occurrences** (per
      file: 3.1.4: 187, 3.1.5: 179, 3.2.1: 91, 3.2.2: 106, 3.2.3: 65,
      3.3: 243, 3.4: 237, 3.5: 87; 3.1.2: 0) against the 17
      PolyLog-emitting rules. Measured mechanism (2026-08-29 build):
      `diff(polylog(·,·),·)` and `polylog(·,numeric)` are nouns, so a
      polylog entry can PASS only through the two-sided expected chain
      on a form-identical answer (identical polylog terms cancel before
      the diff) — the self-diff/numeric stages cannot close. Read the
      measured PASS/unverified/deferred split of the 1,195 from the
      Task-10 records: if the unverified+deferred polylog mass is
      material, a `polylog(2,·)` derivative shim (its derivative
      `-log(1-u)/u` is elementary; the higher-order recursion
      `d/dz polylog(s,z) = polylog(s-1,z)/z`) becomes a follow-up
      ticket with that number as its go; otherwise the ceiling stands
      (record the decision + numbers).
- [ ] `todo/TODO.md` milestone-3 entry (one short entry per follow-up:
      status + link; the queue after class 3 is 8 → 5 → 6 → 7 → 4).
- [ ] **Final gates**, run and recorded:
      `maxima --very-quiet -b test_maxima_rubi.mac` (Results line, 0
      failed); `python3 generator/generate_rules.py --class 1` and
      `--class 2` with `git status --porcelain rules/` EMPTY (the
      byte-identity gate, every accepted class);
      `python3 test/test_head_rewrites.py` (0 failed).
- [ ] Follow-up tickets created (one per remaining class against the
      runbook, one per measured finding).
- [ ] Commit: `docs: class-3 acceptance record + runbook close`.

**Acceptance.** Record + TODO committed; gates green; the ledger's
per-task entries complete.
