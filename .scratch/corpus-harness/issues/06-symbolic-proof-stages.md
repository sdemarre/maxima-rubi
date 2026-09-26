# Verification: record which stage proved an entry, and add the radcan-family symbolic stages

Status: ready-for-agent
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
