# Class-3 deferred campaign — design: the 788 "obviously integrable" declines

Date: 2026-08-30. Working branch: to be cut from `master` after the
`milestone-3` branch is merged and closed (its final-review fixes are
still open at the time of writing — section 0.3, the precondition).
Measurements stamped Maxima `branch_5_50_base_84_g4204fb669` (build
date 2026-08-29 17:58:20) / SBCL 2.6.7 / x86_64-pc-linux-gnu — the
installed build, per the AGENTS.md discipline.

## 0. Context

### 0.1 Where class 3 closed

Milestone 3 (2026-08-30 close, `docs/corpus-class3-baseline-uplift.md`)
ported the Rubi class-3 (logarithms) rule set — 11 files, 333 rules,
3,513-rule core (fingerprint `00e05dca117aefd8df3d266652b11e93`) — and
measured the full 3,085-entry corpus:

- package (rules-only `rubi(f, x)`): **1,736 PASS / 3,085 (56.3 %)**
  — verified 1,367, expected 66, no-answer 303;
- `integrate` baseline: **1,441 PASS / 3,085 (46.7 %)**;
- delta **+295 / +9.6 pt** — the first runbook-ported class to beat
  the baseline (class 1, ported bespoke, beat it by +27.0 pt from the
  start; class 2 came out −9.6 pt at the pilot and reached
  parity-and-a-fraction only after the radcan-fallback harness fix).
- FAIL mass 1,349: **deferred 1,033 (33.5 %)** — the dominant class;
  unverified 158, timeout 117, unexpected 22, contains-noun 13,
  error 6.

`deferred` = the package returned the top-level `unintegrable` noun:
`rubi(f, x)` (`mr_top` with `fb=false`) ran the three dispatch passes
(forward scan, reversed-factor scan, implicit-exponent-1
shadow+lift) and none fired a rule. The 30 s cap and budget policy
are untouched by this campaign (standing user decision 2026-08-27).

### 0.2 The campaign (user request 2026-08-30)

The user's framing: if `rubi` returns `unintegrable` while native
`integrate` has a non-noun answer, the integrand is obviously
integrable — something in our rules is at fault. Two scope decisions
were made in the design interview (user decisions 2026-08-30):

- **Target mass: the 788** — every entry where the package returned
  the top-level `unintegrable` noun AND the baseline `integrate`
  produced a non-noun answer: 313 baseline-`verified` + 16
  baseline-`expected` + 459 baseline-`unverified`. The 329
  verified/expected are the certain-integrable subset, reported
  separately as the clean yardstick; the 459 carry the caveat that
  the native answer is unverified (possibly wrong).
- **Fix strategy: triage decides** — Phase 1 measures the
  per-entry mechanism for the whole deferred population; Phase 2
  chooses the fix per family from the measured distribution
  (shared-dispatch pass vs class-3-local workarounds vs rule ports).

### 0.3 Precondition

The `milestone-3` branch's final whole-branch review fixes are open
at the time of writing: two new committed probes
(`probes/answer-side/02-class3-answer-side-identities`,
`probes/corpus/05-class3-inverse-function-exposure`), the correction
of the F_-rules exposure claim in the acceptance record (the
task-3 smoke reported "0 of 3,085"; the committed probe measures
**12** — 3.1.5 e186–e197, which the package run fires and verifies
4 of), the AGENTS.md Layer-A count, the plan in-place corrections,
and the final-review ledger entry. The campaign branch is cut from
`master` only after that close lands, so the campaign's baseline
records and the probes tree it extends are settled.

## 1. Scope

**In**:

1. **Phase 1 — the triage probe** (committed, re-runnable):
   classify all 1,033 deferred entries by mechanism, with the 788
   target mass in detail.
2. **Phase 2 — the fix(es)**, chosen from the Phase-1 distribution:
   the shared-dispatch pass for the single-candidate mass; condition
   port-bug fixes if any are found; rule ports from pinned Rubi if
   missing rules are found; documentation of faithful declines.
3. **Phase 3 — re-measurement**: full class-3 A/B; full class-1 and
   class-2 A/B re-runs (the standing Layer-B gate for any
   shared-dispatch change); Layer A; the byte-identity gate; the
   100 s timeout re-check protocol on the new record.
4. The campaign acceptance record, the ledger entries, the TODO
   update, and the status update of
   `.scratch/class1-ab-remainders/issues/04-matcher-backtracking-feasibility.md`
   (section 5.4).

**Out** (tracked separately, untouched):

- the 150 `no-answer → deferred` entries (native ALSO returned a
  noun — not "obviously integrable");
- the 76+19 baseline-`timeout`/`error` deferred entries (no native
  answer at the cap);
- the polylog derivative shim (`.scratch/class3-polylog-ceiling`,
  638 go number), the verification-stage OOM ticket, the
  `%mr_algebraicFunctionQ` arity ticket, the class 4–8 ports;
- the general-backtracking matcher investigation beyond the
  implicit-exponent-1 shape — ticket 04's remaining research
  questions (annotated match-path map, how deep the loss propagates
  past `findfun`, upstream prior art) stay open (section 5.4).

## 2. Measured basis

All measurements below were taken 2026-08-30 on the installed build
against the milestone-3 core (3,513 rules, fp `00e05dca…`). The ones
the campaign promotes to committed probes are marked **(probe)**; the
rest are session measurements re-anchored by the Phase-1 probe.

### 2.1 The masses (computed from the two committed records)

`deferred` × baseline class, over the 1,033 deferred entries
(`test/corpus_class3.out` joined to `test/corpus_class3.baseline.out`
on the 3,085 (file, entry) keys):

| baseline class | count | in target mass? |
|---|---:|---|
| unverified (native answered, chain did not close) | 459 | yes |
| verified | 313 | yes (certain subset) |
| no-answer (native also a noun) | 150 | no |
| timeout (no native answer at 30 s) | 76 | no |
| error (native probe died) | 19 | no |
| expected | 16 | yes (certain subset) |

**Target mass 788 = 329 + 459.** Per file (788): 3.1.4 216, 3.4 132,
3.2.2 131, 3.3 110, 3.2.1 81, 3.5 68, 3.1.5 28, 3.2.3 22. Per file
(329): 3.1.4 128, 3.2.2 66, 3.4 39, 3.5 36, 3.2.1 34, 3.3 18, 3.2.3 8.
(Recomputable: the Phase-1 probe emits the full cross-tab.)

### 2.2 The mechanism (direct session measurements)

- `rubi(f, x)` = `mr_top(f, x, fb=false)`: pass 1 forward table scan,
  pass 2 reversed-factor scan (`%mr_dispatch_rev`), pass 3
  implicit-exponent-1 shadow + whole-integrand lift
  (`%mr_dispatch_i1`); a 0-firing returns `mr_unintegrable(f, x)`.
  Nested `mr_int` dispatches run `fb=true` and skip passes 2–3.
- `f2 = (d+e*x)*(a+b*log(c*x^n))` (the bare 2-factor form): **pass 3
  fires `3_1_5_r27`** — the 3.1.5 catch-all `Polyx*(a+b*log(c*x^n))^p`
  (cond: the freeof set + `%mr_polynomialQ(Polyx, x)`) — and the
  package answers. Measured by driving `%mr_dispatch_i1` on a
  single-rule table.
- `f1 = x^3*(d+e*x)*(a+b*log(c*x^n))` (3.1.4 e1's shape): **0-fires
  on pass 1 AND pass 3** (measured: `_mr_pat_3_1_5_r27` false;
  `%mr_dispatch_i1` on the single-rule table false) → `unintegrable`,
  although a valid binding exists (`Polyx := x^3*(d+e*x)`, log factor
  at exponent 1).
- `f5 = (d+e*x)*(a+b*log(c*x^n))/x`: 0-fires likewise; and
  `%mr_polynomialQ((d+e*x)/x, x)` = **false** — even a successful bind
  to r27 would be cond-rejected (faithful to Rubi: the `/x` form's
  Rubi home is the 3.1.4 negative-m rules, which meet the same
  matcher gap).
- `3_1_3_r8` is a clause-for-clause port of the 3.1.3.m
  `(d+e*x)^q*(a+b*log(c*x^n))^p` rule (`.m` line 12; the ported cond
  evaluates TRUE at q=1, p=1), and it **0-fires** on the bare-factor
  form — a pure implicit-1 gap, not a cond fault.
- Root cause: `findfun` (matrun.lisp) picks, for a pattern factor
  with a non-atomic base, the FIRST explicit-power factor of the
  target in the REVERSED stored order, **no backtracking**; and the
  implicit-1 shadow (pass 3) offers exactly ONE wrapped candidate —
  the first non-explicit-power factor in scan order, single-candidate
  by design ("No backtracking is added or removed", `maxima_rubi_
  implicit1.lisp` header). A multi-bare-factor integrand whose
  `(...)^p` slot can bind to any of several bare factors 0-fires
  whenever that one candidate is the wrong slot. The whole-integrand
  lift helps only single-factor integrands.

### 2.3 Constraints carried from ticket 04's known ground

- **Pattern recompilation is the cost center**: the rejected global
  pass-gate lift looped in pattern recompilation past 900 s on 1.1.2.6
  e20 (measured 2026-08-27). Pass 4 runs N table rescans per
  0-firing (N = number of bare top-level factors, typically 2–4); its
  per-entry cost MUST be measured on the deferred mass before
  production (section 5.1).
- **Matcher state is fragile**: loading the 29 section-9.1 patterns
  perturbs the matchreverse rescan on 7 entries (ticket 02). Any
  dispatch change re-verifies those families and the slow-form
  entries afterwards.
- **TLS wall**: each defmatch/matchdeclare slot costs ~9.6 special
  vars; pass 4 adds none (pure Lisp); a C-mass port adds rules and
  updates the core stamp the usual way.

### 2.4 The raw-wrapping mechanism (the implementation crux)

Maxima strips exponent 1 at construction; the only way a factor
carries an explicit `^1` into the matcher is a hand-built
`(mexpt base 1)` object. Measured (`maxima_rubi_implicit1.lisp`
header, 2026-08-27): a defmfun-returned raw power round-trips to the
Maxima level **unsimplified** (x^1 stays x^1), while a hand-built
MTIMES does not. Pass 3's lift avoids the problem by never letting
the wrapped object return to the Maxima level — the `mlambda`
pipeline feeds it straight to the compiled matcher. **Pass 4 uses the
same seam**: each wrapped variant is consumed internally in Lisp
(table scan via `mlambda`), never re-simplified.

## 3. Design

### 3.1 Phase 1 — the triage probe (decides Phase 2)

New committed probe `probes/corpus/06-class3-deferred-mechanisms.
{py,run,out}` (name may settle in the plan):

- **Input**: the two milestone-3 records (the 1,033 deferred keys,
  the 788 flagged) + the suite files (integrand text) + the rules
  core. Sharded over 24 processes with the standing launcher
  machinery; one fresh Maxima subprocess per entry (the Layer-B
  model), no per-entry cap needed beyond a generous safety cap
  (the deferred entries' package times are 1–12 s; the triage adds
  up to N extra table rescans — the measured cost goes in the .out).
- **Per-entry measurement**:
  1. **Production trace** — `rubi_verbose` table scan of the
     integrand: which rules fire (expect: none, or only a Rubi
     catch-all returning the `unintegrable` noun). Distinguishes
     0-firing from catch-all-firing.
  2. **Pass-4 prototype** — for each bare (non-explicit-power)
     top-level factor fᵢ, a full table scan of the integrand with
     fᵢ replaced by the raw `(mexpt fᵢ 1)` (section 2.4 seam).
     Records: any firing, which rule, which candidate. A firing
     under any variant ⇒ the binding exists and the single-candidate
     selection missed it.
  3. **Non-firing drill** — for entries where no wrapped variant
     fires: direct pattern calls on the corpus family's rules (+
     adjacent families' catch-alls), with the matchlist binding and
     the cond clauses evaluated clause by clause; then a shape
     match against the family's pinned `.m` file. Classifies
     condition port-bugs from faithful condition declines from
     missing rules.
- **Per-entry classes**: **A** single-candidate gap (a wrapped
  variant fires) / **B-port** (a cond clause is wrong vs the `.m`)
  / **B-faithful** (the ported cond matches the `.m` and declines)
  / **C-in-Rubi** (a pinned-`.m` rule covers the shape; not ported
  or not firing) / **C-absent** (no pinned-`.m` rule — upstream
  gap) / **D** (a documented faithful decline — a catch-all fired,
  or a recorded mechanism strictness such as the F_ e:=0 corner).
- **Calibration**: the prototype is calibrated on the measured
  f1/f2/f5 cases (section 2.2) and the 12 F_-domain entries (3.1.5
  e186–e197 — measured 2026-08-30 in the milestone-3 close-out:
  the eight m=1 rows are answered on pass 3 by the 3.5 catch-all
  3_5_r43 (4 of them verified), the four m=2 rows 0-fire in all
  three passes (deferred); the ported F_ headvar rules fire on
  none of the twelve — the e:=0 identity-default corner, recorded
  strictness). A harness that misclassifies any calibration case
  does not ship.
- **Output**: the committed `.out` = the distribution
  (mechanism × file × target-flag) + the per-entry table + the
  measured pass-4-prototype per-entry cost. **This table is the
  Phase-2 design input** — no Phase-2 fix is chosen on reasoning
  before it exists.
- The C-subclass shape adjudication (which pinned-`.m` rule covers
  which shape) is a human/agent judgement recorded in the campaign
  record — the probe emits the shape fingerprints, not the verdict.

### 3.2 Phase 2 — fixes per family, chosen from the distribution

Ordered by expected mass (A first — it is the dominant mechanism —
then B, then C):

- **A-mass → pass 4 in production** (extension of
  `maxima_rubi_implicit1.lisp` or a loaded sibling, per the plan):
  after passes 1–3 0-fire, table-scan each raw-wrapped variant
  (N = number of bare top-level factors). **Gating — exactly like
  passes 2–3**: top-level only, `fb=false` only, runs only on the
  0-firing path. Nothing currently passing can change (a passing
  entry fired in passes 1–3 and never reaches pass 4); only
  currently-FAILING 0-firings can newly fire — the same safety
  argument passes 2 and 3 were accepted on in milestone 1. Layer A
  tests for the mechanics (f1/f2/f5 semantics, the gating
  non-interference, the nested-dispatch unchanged case).
- **B-mass (only if found)** — condition port-bugs:
  generator/translation fixes under the byte-identity gate
  (regenerated files diff-reviewed; sibling files byte-identical);
  core rebuild + stamp.
- **C-mass (only if found)** — `C-in-Rubi`: ports from pinned Rubi
  under the standing generator discipline (translation-table row,
  witness, Layer A checks, byte-identity of the untouched files).
  `C-absent`: recorded as upstream gaps in the campaign record
  (not ported — no rule exists in the pinned commit).
- **D-mass** — documented faithful declines in the campaign record.

### 3.3 Phase 3 — re-measurement and acceptance record

- Full class-3 package run (new merged record) + entry-level A/B
  against `test/corpus_class3.out` (the campaign baseline).
- **Full class-1 run** (A/B vs the accepted 20,069/25,697) and
  **full class-2 run** (A/B vs 594/965) — the standing Layer-B
  regression gate for a shared-dispatch change; expected shape is
  FAIL→PASS transitions only; every other transition individually
  attributed.
- The 100 s timeout re-check protocol on the new class-3 record's
  timeout class (standing protocol).
- Layer A suite; the byte-identity gate; the core stamp consistent
  with the rules on disk.
- Campaign acceptance record (`docs/corpus-class3-deferred-uplift.md`
  — name may settle in the plan), the ledger entries, the TODO
  update, the ticket-04 status update.

## 4. Acceptance criteria

1. **Primary — the 788 shrinks**: the campaign record reports the
   new target-mass count and the per-mechanism recovery of the 788
   (and of the 329 certain subset, separately). No fixed floor in
   this spec: the Phase-1 distribution sets what is achievable, and
   the record states what was recovered and, entry-family by
   entry-family, why the residue was not.
2. **Regression gate**: zero unattributed PASS→FAIL on class 3 —
   any PASS→FAIL that occurs must be individually attributed and
   dispositioned in the record before acceptance, and no PASS→FAIL
   may survive the campaign unexplained; the class-1 and class-2
   full A/B runs are expected to show FAIL→PASS transitions only,
   same rule.
3. **All standing gates green**: Layer A, the byte-identity gate
   (or the documented regeneration), core fingerprint consistent,
   the 100 s re-check executed on the new record.
4. **Measured-claims discipline**: every non-trivial claim in the
   campaign record cites a committed, re-runnable probe (the
   Phase-1 probe + the re-run records).
5. **Ticket 04 updated** with the measured class-3 go/no-go number
   and the option-(ii) implementation status (section 5.4).

## 5. Risks and known sharp edges

### 5.1 Pass-4 cost

N table rescans per 0-firing (N typically 2–4) on entries that
currently FAIL fast (1–12 s package times). The pattern
recompilation cost center (section 2.3) makes this the campaign's
main performance risk. The Phase-1 probe measures the per-entry
cost; the plan decides from the measurement (ship as-is / bound N /
gate on factor count). The 30 s cap policy is untouched either way —
this is a wall-time question, not a budget question.

### 5.2 The Lisp seam

The wrapped variant objects must never round-trip through the Maxima
simplifier (section 2.4). The prototype and the production pass 4
share one Lisp implementation (the harness drives the same gated
function) so the triage classification cannot diverge from
production behavior — the plan fixes this seam as an explicit
interface.

### 5.3 Matcher-state fragility

Per ticket 02 (7 entries) and ticket 01 (9 slow-form entries), the
installed matcher's compiled state is load-order/state-sensitive.
The Phase-3 re-runs include those families' entries explicitly in
the attributed-transition check.

### 5.4 Ticket 04 (matcher backtracking feasibility)

`.scratch/class1-ab-remainders/issues/04-matcher-backtracking-
feasibility.md` (ready-for-agent, filed 2026-08-27, never executed)
asked, as question 3, for a sampled measurement of "how much of the
4,361 class-1 deferred does backtracking actually recover" as the
go/no-go input — and ranked a "backtracking findfun shadow
(generalize the implicit1 precedent, medium)" as option (ii). This
campaign executes, on the class-3 mass and with the full population
instead of a stratified sample, exactly that measurement (Phase 1,
question 3's shape) and, if the distribution says so, implements
option (ii) as pass 4 (Phase 2). The ticket's remaining questions
(the annotated match-path map, whether the loss propagates past
`findfun` into the `matmatch` recursion, the `../maxima-lists`
prior-art search, the upstream-patch sketch) stay open — the
campaign's record cites what it measured toward them, and the
ticket's status moves to "partially answered by
`docs/corpus-class3-deferred-uplift.md`" with the open questions
restated.

### 5.5 The 459 caveat

The 459 baseline-`unverified` entries carry native answers the
baseline's zero chain did not close — possibly wrong native answers.
The campaign's yardstick is the DRIVER's (the package answer is
verified against the integrand, independently of native), so
recovery of these entries is unambiguous even where the native
answer was suspect; the record reports the 329 subset separately so
the certain-integrable number is never blurred by the caveat.

## 6. Process and branch

- Spec → plan (the writing-plans step) → SDD execution (subagent per
  task, ledger in `.superpowers/sdd/progress.md` as a new campaign
  section, the milestone pattern).
- Branch: cut from `master` after the milestone-3 close (0.3); name
  `class3-deferred` unless the close suggests otherwise. No push
  (standing rule — no remote is configured).
- Framing: this is a defect-reduction campaign on the class-3
  record, not a "milestone N" (no new function class). `todo/TODO.md`
  tracks it as the follow-up work item that supersedes the deferred
  remainder noted at the milestone-3 close.
