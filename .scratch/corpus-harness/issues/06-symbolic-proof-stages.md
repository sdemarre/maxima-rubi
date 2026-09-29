# Verification: record which stage proved an entry, and add the radcan-family symbolic stages

Status: in progress (branch `verification-stages`)
Type: task (driver + harness guard + full-corpus A/B)
Filed: 2026-09-26 (user request, after the README examples' symbolic verification)

## Why

`verified` is supposed to mean "the answer is proved correct". Today it can rest on numeric
evidence alone. `zero_chain` (`test/corpus_driver.py` ~L676) runs, in order:

1. a **numeric stage first**: evaluate `d = diff(r, x) - f` at x = 0.35 and 0.65 (parameters
   substituted `a=0.9, b=1.3, …, p=2`); both |residual| < 1e-9 → closed;
2. two symbolic chains built only from `factor` / `ratsimp` / `expand`;
3. the fallback `radcan(rat(d))`, gated off for elliptic residuals.

The numeric stage leads for measured reasons (elliptic residuals that crash the symbolic stages,
budget-eaters like 1.1.2.4 e983). But a numeric pass is not a proof: the user's standard
(2026-09-26) is that residuals "don't really count". The records do not say which stage closed an
entry, so **how many of today's 55,259 `verified` entries (classes 1-8, promoted records) are
numeric-only is unknown**.

Meanwhile the README examples showed a family of symbolic reductions the chain never tries. Each
reduces `d` to exactly 0 where `ratsimp`/`factor` do not
(`probes/readme-examples/01-symbolic-verification.mac` → `.out`, `Results: 16 passed, 0 failed`,
build `branch_5_50_base_84_g4204fb669`):

| stage | closed (README examples) | residual shape it handles |
|---|---|---|
| `radcan(d)` | 8 of 16 | logs, nested radicals (`sqrt(2+sqrt(2))`), `li[2]`/`li[3]` of exponentials and quotients |
| `radcan(exponentialize(d))` | 4 | trig/hyperbolic mixes, `tanh(8*x)^(1/3)`, `expintegral_si` times `sin` |
| `radcan(exponentialize(rectform(d)))` | 1 | answers with `(-1)^(1/4)`-type constants; `rectform` must come FIRST (after `exponentialize` it does not close) |
| `radcan(trigexpand(d))` | 1 | `elliptic_f(2*atan(x), m)` derivatives (`sin(2*atan(x))`) |
| `radcan(trigexpand(demoivre(d)))` | 1 | `%e^(%i*asin(u))` (`demoivre`, then `sin(asin y) = y`, `cos(asin y) = sqrt(1-y^2)`) |
| `radcan(logarc(d))` | 1 | `%e^(asinh(u))` (`asinh y = log(y + sqrt(y^2+1))`) |

These are the shapes `rubi` answers produce (`li[2]` of exponentials, inverse functions inside
exponentials, roots of unity), so the gain is likely concentrated in classes 3-7.

## The work

1. **Record the closing stage.** Every zero-test (self-diff `zv`, expected-diff `ze`/`ze2`) reports
   which stage closed it, e.g. `numeric`, `sym:<n>`, `fallback`, `radcan:<name>`. Carry it into
   the record line (a new field after the class, or a sidecar like `.caps`), so `ab_records.py`
   and the mergers keep working. Guard it in a driver unit test (the
   `test_driver_radcan_fallback.py` pattern: synthetic residuals, not corpus entries).
2. **Add the radcan-family stages** after the existing symbolic chains and before the
   fallback, cheapest first, EACH in its own `errcatch` (a crash in one stage must not end the
   chain — the 2026-08-25 lesson in the numeric stage's comment):
   `radcan(d)`, `radcan(exponentialize(d))`, `radcan(exponentialize(rectform(d)))`,
   `radcan(trigexpand(d))`, `radcan(trigexpand(demoivre(d)))`, `radcan(logarc(d))`.
   Keep `trigrat` OUT (109 s on one README residual). Consider the elliptic gate for the new
   stages too (the fallback's measured `radcan(rat())` burn on elliptic residuals).
3. **Measure** (full corpus, classes 1-8, queue runner, 24 workers, 30 s cpu cap; about 245k
   core-seconds by the promoted records' `t=`, roughly 3-4 h wall), A/B against the promoted
   records. Read:
   - `unverified` → `verified` (new symbolic closures);
   - among `verified`, the split numeric-only vs symbolic, before (stage recording alone, a
     separate arm with the new stages off) and after the new stages;
   - `verified`/`expected` → `timeout` (the new stages' cost pushing entries over the cap).
     Attribute every PASS→FAIL as usual.
4. **Decide (user)** with those numbers: keep the numeric stage as a PASS, or split out a
   `numeric` class (PASS or FAIL), and whether the numeric stage should still lead or move after
   the symbolic stages.

## Cautions

- **Branches.** `radcan` and `logarc` pick principal branches; a 0 from them is a proof modulo
  branch choice, the same caveat the existing `radcan(rat())` fallback carries.
- **Cost / hangs.** One chain in the README battery hung beyond 300 s on `1/(x^8+1)`'s residual
  (which one was not isolated). Stages must be ordered and errcatch'd, and the A/B's
  `→ timeout` count is the gate for that.
- **Same-statement rat state.** Verify in a statement after the `rubi` call
  (`.scratch/rubi-rat-state-leak/issues/01`); the driver already does.

## Gates

Harness guards (AGENTS.md list) including the new stage-recording guard; the full-corpus A/B
above with every PASS→FAIL attributed.

## Comments

### 2026-09-28 — user decisions, and the implementation on `verification-stages`

Decisions (asked with the measured options):

- **Symbolic first, numeric last.** Numeric residuals are an indication, not a proof, in either
  direction (a mismatch can be precision, branch or evaluation trouble). Every symbolic stage runs
  before the numeric check; the tag says which kind closed an entry.
- **Verification gets its own budget.** rubi keeps 30 s cpu; the checker gets `MR_VERIFY_CAP`
  (30 s) on top, and each stage `MR_STAGE_CAP` (5 s cpu, `ITIMER_VIRTUAL`). A process killed after
  rubi answered is not a rubi timeout.
- **Proof stage in a `.proof` sidecar**, like `.caps`, so `ab_records.py` and the mergers keep
  their line format.
- **No full re-run yet**: improve the checker as far as possible first.

Built (TDD): `test/mr_verify.mac` / `test/mr_verify.lisp` (the checker, `mr_check_entry`),
`test/test_mr_verify.mac` (24 checks), `test/test_driver_proof.py` (20 checks); the driver, queue
runner and class merger carry the protocol (`ANSWERED`, `NUMERIC`, `CLASS`, `PROOF`), the budget
and the `verify:` header field. `test_driver_radcan_fallback` narrows the stage list to
`["rat-radcan"]` (the radcan family now closes its witnesses first); `test_driver_parens` checks
the list hand-over; `test_run_records`' stub speaks the new protocol.

Found on the way: `float(li[s](z))` stays unevaluated unless `z` is already `a + b*%i`, so the
numeric check declined on correct polylog answers (5.4.1 e18). The check now rectforms `li`
arguments; e18 itself is now proved symbolically by `logarc`.

Also built: `test/merge_proof.py` (merges and censuses the `.proof` sidecars against the merged
record; `test/test_merge_proof.py`, 8 checks).

### 2026-09-28 — the unverified subset (`probes/verify-stages/01-unverified-subset.{sh,out}`)

The 1,530 `unverified` entries of `test/corpus_class<N>.pfs.out`, re-run under the checker (12
workers, 30 s cpu rubi + 30 s verification, 5 s per stage; rules core `f2cb4fc6` = master
`b62d6d7`). **386 now pass**, 384 of them proved symbolically:

| closing stage | entries |
|---|---:|
| `exponentialize` | 325 (class 4 trig, 7.3.6 exponentials of atanh) |
| `radcan` | 38 (mostly class 1, the expected-diff) |
| `logarc` | 10 |
| `demoivre` | 7 |
| `rectform` | 4 |
| numeric only | 2 |

Per class: 1 +38, 3 +4, 4 +231, 5 +16, 6 +59, 7 +38; 2 and 8 none.

The 1,144 still unproved: ~950 `none/numeric-declined` (the numeric check cannot evaluate them --
mostly a free `m`/`n` or AppellF1), ~190 `none/numeric-mismatch` (a hand-inspection list, not a
defect list: 4.1.7, 4.2.7, 6.1.7, 6.2.7 carry most of them).

Stage cost: `rectform` accounts for 325 of the ~450 stage timeouts and both heap fills, and closed
4 entries -- the first candidate for reordering or a tighter limit.

Three checker defects the run exposed (18 entries read `error`), fixed test-first; the 18 re-run
as `unverified` with honest tags (the record's last section):
- the numeric check read its float value OUTSIDE its guard: `realpart`/`cabs` of a float
  hypergeometric with a pole parameter raise `pquotient` (2.3 e477);
- a corpus answer that fails to simplify (`expt: undefined: 0 to a negative exponent`, 4.2.7 e80)
  was evaluated outside any errcatch -- each answer is now `errcatch`'d, a failure skipped;
- heap exhaustion (4.5.1.2 e713/e714, the `rectform` stage filled the 1 GB heap, fatal in SBCL):
  the stage timer's 20 ms tick now stops a stage above `mr_heap_fraction` (0.6) of the dynamic
  space. Garbage of a stopped stage can stop the following stages of that entry too (`(heap)` in
  the tag); a forced GC is not a way out (0.8-27 s in the rules core, and a deadlock from the
  handler), so it stays -- 2 of 1,530 entries.

Next, before any full run (user: improve the checker as far as possible first):
1. `rectform`: last, or a tighter limit;
2. give the numeric check values for `m`/`n`, and AppellF1 support (derivative + numeric
   evaluator) -- an indication for ~950 entries, never a proof;
3. hand-check a sample of the ~190 mismatches;
4. a control sample (~1,000) of currently-`verified` entries: the numeric-only share, and any
   verdict the new stages or the budget change;
5. whether `rat-radcan` still earns its place behind `radcan` (no synthetic witness found that it
   closes and `radcan` does not).

- 2026-09-28 (late): **the 13 remaining wrong answers** (`handoffs/2026-09-28-checker-wrong-answers.md`,
  probe 05 regenerated on `d961e8e`). Per category:
  - **2, 4.1.0 e304 e305 e309 e310 e314 e315 e320 (7): not wrong answers.** rubi's answers pass a
    principal-branch finite difference. The checker's default-flag residual mis-evaluates complex
    fractional powers, and no stage closes their 2F1 residuals. Parked (user decision: no
    hypergeometric special case): `.scratch/corpus-harness/issues/07`, probe
    `verify-stages/06`.
  - **4, 1.2.2.2 e1000: table order.** The legacy 9.1 r3 (`EqQ[a, 0]`) accepts the unsimplified
    zero constant but sits after 1_2_2_2 r17, which divides by it. With 9.1 first, rubi returns
    the corpus answer (radcan-proved). Ticket `class-ports/issues/09` (comment); not moved: that
    ticket's full-table A/B is the gate.
  - **5, 2.3 e725: fixed** (`e5a9d89`). `%mr_fullSimplify` was `ratsimp`, which leaves
    `2*log(2)/log(4)` unreduced; the answer's 2F1 parameters floated to 3+-eps and evaluated to
    -1e15. Now `verified` (radcan). Class 2 A/B (965/965, same checker): 0 PASS->FAIL, 3
    FAIL->PASS (e475, e487 -> expected; e725).
  - **3, 7.2.4b e96 / 7.2.5 e50: fixed** (`4763cab`). An upstream typo in Rubi's 1.1.2.6
    r13/r14, `f/e^2` for `f/g^2` (added in the 2023-12 release). New generator errata table
    `RUBI_ERRATA`, undone by the P3 gate. Both now `verified` (radcan). A/B over classes 5 and 7
    plus 1.1.2.4-6 (12,459/12,459, same checker, base core `e5a9d89`): 0 PASS->FAIL, 4
    FAIL->PASS (e96, e50 -> verified; 7.4.2 e769, e771 -> expected).
  - **6, 4.7.7 e865: fixed** (`4c62ae1`). Rubi's 4.1.0.2 r18 leaves `b` out of FreeQ and out of
    the RHS; `b` bound `sqrt(csc(x))` and was dropped. Erratum: `b` in FreeQ, `b^n` on the RHS.
    Now `verified`, but numeric only (`numeric/timeout:rectform`); the answer is correct but
    less tidy than the corpus's (its elliptic parts do not collapse). No class-4 A/B yet.
  - **7, 4.1.1.2 e466: not a wrong answer.** The residual is 1e-47 at `fpprec: 50` and 1e-97 at
    100, so float cancellation only. With the parameters substituted as exact rationals, the
    plain-float residual is 5e-13, under the tolerance: **checker idea**, substitute rationals
    (then float) instead of floats first. Not implemented.

- 2026-09-29: the measurements behind the comment above are committed as
  `probes/verify-stages/07-*`: `07-e466-bigfloat` (category 7), `07-e1000-legacy-9_1-first`
  (category 4), `07-sympy-check` (an independent CAS: SymPy's `simplify` takes e96's and e50's
  residuals to 0; e865's residual is below 1e-173 at 40 digits at four points but `simplify` does
  not close it; the 1.1.2.6 r13 split is 0 with `f/g^2` and `f*g^m*x^(m+2)*…*(g^2-e^2)/e^2` with
  `f/e^2`; SymPy's own `integrate` leaves both e96 and e50 unevaluated), `07-ab-runner.py` and the
  two A/B reports (`07-ab-fullsimplify-class2.out`, `07-ab-errata-1.1.2.6.out`).
