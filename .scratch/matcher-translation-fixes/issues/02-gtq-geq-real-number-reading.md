# GtQ / LtQ / GeQ / LeQ: port Rubi's real-number reading

Status: fixed (2026-09-25, branch class-ports-fixes)
Type: task (measure, then decide)
Filed: 2026-09-15 (matcher translation fixes, P5b attribution — outside the plan's four defects;
design §1 Out: "GtQ's RealNumberQ/N reading — siblings outside the four shapes are ticketed, not fixed")

## Problem

The generator translates Rubi's real comparisons to a bare Maxima `is`:
`generator/generate_rules.py:853` `CMP_OPS = {"GtQ": ">", "LtQ": "<", "LeQ": "<=", "GeQ": ">="}`, which
emits `is(A op B)`.

Rubi reads them differently (`reference/rubi/Rubi/IntegrationUtilityFunctions.m:403–453`, pinned clone):

```mathematica
GeQ[u_,v_] :=
  If[RealNumberQ[u],
    If[RealNumberQ[v], u>=v, With[{vn=N[Together[v]]}, Head[vn]===Real && u>=vn]],
  With[{un=N[Together[u]]},
  If[Head[un]===Real,
    If[RealNumberQ[v], un>=v, With[{vn=N[Together[v]]}, Head[vn]===Real && un>=vn]],
  False]]]
```

`GtQ`, `LtQ` and `LeQ` follow the same shape at :403, :421 and :457. On a symbol, `N[Together[u]]` is not
`Real`, so `GeQ[d, 0]` is **False** and `Not[GeQ[d, 0]]` is **True**. Maxima's `is(d >= 0)` on an
unassumed symbol answers `unknown`, which the dispatcher rejects (`is(r) = true`). What
`not(is(d >= 0))` answers, and whether the dispatcher accepts it, is **not measured**.

## Evidence

- P5b attribution, class 2 g3 e19 (`probes/matcher/10-p5b-attribution.mechanisms-class2-3.md:79–84`).
  Rubi's normalizing pair for `F^(c(a+bx))((d+ex)^n)^m` is `1_4_1_r43` / `r44` (`GeQ[a,0]` /
  `Not[GeQ[a,0]]`). The port emits `is(d >= 0)` / `not(is(d >= 0))`. On the fixed core neither rule
  fired and the entry is `deferred`. P0 answered through `1_4_1_r41` on a binding Mathematica does not
  make.
- Crude count of `is(… >= …)` in the generated rules: class 1 43, class 2 1, class 3 0 (grep, 2026-09-15,
  HEAD 5c26cc5). The other three heads are not counted yet.

## What to do

1. Probe: count every emitted `GtQ` / `LtQ` / `GeQ` / `LeQ` site per class from the Rubi source, as
   probe 13 does for the integer heads. Measure `is(sym >= 0)`, `not(is(sym >= 0))` and the dispatcher's
   verdict on each, and compare Rubi's reading on symbol / rational / float / `%pi`-constant / complex
   arguments.
2. Decide with the user: port the reading as named entries (`%mr_geQ(u, v)` etc., true/false, the
   design §3.1 pattern with static-gate undo exceptions), or record it as a deviation.
3. If ported: red/green probe, Layer A checks, regeneration, and a P5-style A/B of the affected entries.

## Investigation 2026-09-25

Measured on branch `gtq-investigation` (off `class-ports` @ `4ed1877`), Maxima
`branch_5_50_base_84_g4204fb669` (2026-08-31 13:27:47), SBCL 2.6.7. Probes in `probes/gtq/`
(`gtq-readings.mac` holds the readings). Readings compared:

- **cur** — today's emission `is(A op B)`: three-valued; the dispatcher accepts only `is(cond) = true`.
- **(F)** facts-aware two-valued — `is(A op B) = true` (unknown or an error reads False).
- **(R)** strict Rubi — `numberp` (RealNumberQ), otherwise `float(u)`, then `float(ratsimp(u))`
  (N[Together[u]]; bfloat when float overflows) must give a float. Otherwise the predicate is False.
  When both sides are numbers, they are compared.

### Site counts (`01-site-census.py` → `.out`)

| class | `>` | `<` | `>=` | `<=` | emitted | under `not()` | Rubi source calls (neg / 3-arg) |
|---|---|---|---|---|---|---|---|
| 1 | 934 | 793 | 45 | 94 | 1866 | 109 | 1911 (139 / 80) |
| 2 | 15 | 24 | 1 | 3 | 43 | 1 | 38 (1 / 9) |
| 3 | 55 | 20 | 0 | 1 | 76 | 2 | 79 (4 / 1) |
| 4 | 339 | 481 | 15 | 54 | 889 | 99 | 872 (109 / 59) |
| 5 | 188 | 96 | 10 | 6 | 300 | 14 | 304 (18 / 3) |
| 6 | 39 | 40 | 4 | 0 | 83 | 0 | 75 (0 / 10) |
| 7 | 205 | 120 | 6 | 6 | 337 | 14 | 486 (26 / 8) |
| 8 | 16 | 13 | 0 | 0 | 29 | 1 | 30 (1 / 0) |
| 9 | 7 | 5 | 1 | 1 | 14 | 1 | 38 (2 / 2) |
| all | 1798 | 1592 | 82 | 165 | **3637** | 241 | 3833 (300 / 172) |

Every emitted site is in a `_mr_cond_` function (none in a repl). RHS: 1696 are `0`, 1607 another
literal number and 334 an expression. There are also 22 boolean `is(... and q-n >= 0 and ...) = true`
bodies holding a raw Rubi relation (class 1: 19, class 2: 3). These are not GtQ-family calls and are
already two-valued.

### Facts probe (`02-facts-probe.run` → `.out`; `R = rubi` on all 155 rows: 50 shapes × 3 contexts + 5 radexpand/logexpand:false rows)

- **is() never prompts and never errors.** Its asksign/sign path does not ask: stdin was `/dev/null`
  and no prompt or Lisp error appeared (grep count 0). The census confirms it: 0 errors in 8,843
  corpus calls. `prederror` is false. If it were true, is() would raise the error that errcatch
  catches.
- **Complex arguments:** `is(%i > 0)`, `is(%i < 0)`, `is(1+%i > 0)`, `is(sqrt(-2) > 0)`,
  `is(a+%i > 0)` and `is(%i*a > 0)` are all **false**. None is unknown and none errors. Today's `not(is(..))`
  therefore reads True on them, which matches Rubi. But is() also answers false on an expression that
  is *real in value* while carrying `%i` syntactically (see the census).
- **Where (F) ≠ Rubi, with no facts at all** (7 of 50 shapes). These come from Maxima's own
  real-symbol reasoning, not from the facts database: `a >= a`, `a < a+1`, `a^2+1 > 0`, `a^2 >= 0`,
  `exp(a) > 0`, `abs(a)+1 > 0` and `sqrt(a) >= 0` (also `sqrt(a^2) >= 0` under
  radexpand:false). In every one of them (F) is True and Rubi is False, so under (F) the
  `Not[GtQ[..]]` rule is lost and the `GtQ` rule fires in its place.
- **With `assume(a > 0)`** 12 shapes differ (5 more: `a > 0`, `a >= 0`, `a^2 > 0`, `sqrt(a) > 0`,
  `a^b > 0`). **With `declare(n, integer), assume(n > 0)`** 8 differ (1 more: `2n+1 > 0`), but
  `n-1 >= 0` is still unknown because is() does not use integrality.
- Numbers, rationals, floats and `%pi`/`%e`/`sqrt`/`log`/`sin` constants give the same answer under
  all readings. `(a^2-1)/(a-1)-a > 0` is True under both (R) and (F). `exp(1000) > 0` needed the
  bfloat fallback in (R): `float` overflows there.

### Cost (`03-cost.run` → `.out`; µs per call, sequential, 20,000 calls, host loadavg ~7)

| shape (u > 0) | cur `is()` | (F) inline | (F) named + errcatch | (R) named |
|---|---|---|---|---|
| `a`, numbers, `sqrt(2)-1`, `%e^a` | 0.4–1.8 | 0.9–2.0 | 4–8 | 7–15 |
| `m+1` | 4–7 | 5–8 | 8–10 | 12–13 |
| `a^2+1` | 26–30 | 27–31 | 30–35 | 13–15 |
| `b^2-4*a*c` | 91–92 | 97–116 | 99–102 | 18–20 |

(R) costs at most ~20 µs per call. It is cheaper than is() on polynomials, where sign() does real
work. The census averages 30 calls per entry, so every reading costs well under 1 ms per entry.

### Disagreement census (`04-select-entries.py` → `census.entries`, `05-census.py` → `.out`, `06-summarize.py` → `06-summary.out`)

Setup:

- The runtime overlay (`make_census_overlay.py`, baked into a pinned core by
  `build_census_core.sh`) routes all 3,637 sites through `%mr_gtq_W`. That wrapper computes cur, (F)
  and (R), logs every call where (F) ≠ (R), and returns the arm's value.
- 295 entries: 40 from each of sections 1 and 3–8 and 15 from section 2, taken from the files with
  the most sites and a record t ≤ 10 s.
- Each entry ran in three arms, cur / F / R, alternating, through the driver's own
  `build_text`/`maxima_run`, one process at a time, with a 30 s cpu cap.
- The cur arm reproduces the source records exactly (295/295 verdicts).

Results:

- **Calls:** 8,843. Under the current emission 1,340 are true, 6,730 false and **773 unknown
  (8.7 %)**, with 0 errors.
- **(F) ≠ (R): 10 calls in 5 entries, 5 distinct shapes, 0 verdict differences** (F PASS 247 = R PASS 247).

| calls | site | shape | cur | F | R (= Rubi) |
|---|---|---|---|---|---|
| 6 | `1_1_1_3` r65 s1/s2, r67 s1 (neg) | `i√a e/(i√a e ∓ √c d) ∓ √c d/(i√a e ∓ √c d)` (= 1) > 0 | false | false | true |
| 1 | `1_2_1_1` r13 | `4(1-i a)(1+i a) - 4a^2` (= 4) > 0 | false | false | true |
| 2 | `1_1_2_1` r13 | `1/c^2 > 0` | true | true | false |
| 1 | `1_1_2_1` r14 | `-1/a^2 < 0` | true | true | false |

The divergence runs both ways:

- **Together cancellation.** An `%i`-carrying expression that is a real number after Together is
  True for Rubi. is() calls it false, so the `Not[]` rule (r67) is taken instead.
- **Real-symbol sign reasoning.** (F) proves these, but Rubi cannot.

No call was decided by an `assume()` fact: the corpus runs with an empty facts database.

Per-entry explanations (all verdicts are identical across F and R):

- 1.2.1.2 e727 is `unverified` in all three arms. R routes through r65 and gets there faster (1.6 s
  vs 4.0 s).
- 5.3.6 e212/e39 and 7.5.1 e125/e76 are `verified` in all three arms.

**Verdicts, cur → two-valued (F and R agree on every entry):** PASS 237 → 247.

- 10 FAIL→PASS: 1.2.1.4 e319, 1.1.2.8 e12, 1.1.3.4 e620/e818, 4.5.4.2 e29, 4.3.2.1 e320,
  5.3.6 e348, 5.5.1 e65, 7.3.6 e1249, 7.1.5 e45.
- 3 FAIL→FAIL entries change from `contains-noun` to `timeout`: 4.5.3.1 e269, 6.1.7 e365 and
  7.1.4b e44. This is the same in both arms, so it comes from the two-valued reading itself (a
  `Not[GtQ]` rule now firing on a symbolic argument). It is worth attributing in the implementation's
  A/B.

The 13 verdict changes are the unknown → False fix. Choosing between (F) and (R) moved no verdict in
this slice.

### Recommendation

- **Default: (R), the strict Rubi reading**, as named entries `%mr_gtQ/%mr_ltQ/%mr_geQ/%mr_leQ(u, v)`.
  This is the design §3.1 pattern, with a static-gate undo exception. The 3-arg form becomes the
  conjunction of two of these. Reasons:
  1. It is Rubi's semantics: the project holds itself to Rubi's rules and PASS counts.
  2. It answers the same regardless of the facts database and of Maxima's real-symbol assumption.
  3. It gets the Together-cancelled `%i` shapes right, where (F) takes the wrong branch.
  4. It gains exactly what (F) gains on this slice (+10 PASS, 0 differences).
  5. Its cost is ≤ 20 µs per call.
- **Behind a switch (default false), e.g. `mr_gtq_facts`: the facts-aware reading.** This is for a
  user who calls `rubi()` under `assume()`. That is the only place facts exist, because the corpus
  never assumes anything. Prefer **(R) ∨ (F)** (true when either reading is true) over bare (F):
  - It keeps (R)'s Together cases.
  - It adds Maxima's sign reasoning and the `assume`/`declare` facts.
  - On this slice each disagreeing entry's calls went only one way, so (R) ∨ (F) would follow the
    measured F or R route and give the same verdicts.

  Record the switch arm as a documented deviation from Rubi. It changes `Not[GtQ]` rules too: when
  facts prove `GtQ`, those rules stop firing.
- **Next:** the implementation's red/green probe should reuse `02-facts-probe.mac`'s rows (R = rubi
  column) as Layer A checks. Then do a full A/B of all classes. The class-6 attribution's
  overlay-(F) estimate (49 of 190 losses) should carry over to (R) unchanged, because F = R on every
  verdict here.

## Fix (2026-09-25, user decision)

The user chose the investigation's recommendation: Rubi's reading (R) as the default, and
(R) OR (F) behind a switch.

- `maxima_rubi_utils.mac`: `%mr_gtQ` / `%mr_ltQ` / `%mr_geQ` / `%mr_leQ` (2 and 3 arguments) over
  `%mr_realCmpQ`. RealNumberQ maps to `numberp`. N[Together[u]] maps to `float(u)`, falling back
  to `bfloat` when `float` errors, and to `ratsimp` first when `u` has a variable. The result is
  always true or false.
- Run switch `mr_gtq_facts` (defmvar, default false, registered in `test/run_records.py`). When
  true, the result is (R) OR `is(u op v) = true`, so `assume()` facts count. That is a documented
  deviation from Rubi.
- Generator: `CMP_OPS` emits the named entries (`REAL_CMP`). The P3 gate undoes them to
  `is(A op B)`, with 1,944 class-1/2/3 sites pinned. Emitted over the whole tree: `%mr_gtQ` 1,798,
  `%mr_ltQ` 1,592, `%mr_leQ` 161, `%mr_geQ` 82.
- Layer A: 30 checks (the facts-probe rows in both switch values, 3-argument chains, `assume()`,
  and 1_1_2_1 r18's `Not[GtQ[a, 0]]` on a symbolic `a`). RED first; then `Results: 1583 passed,
  0 failed`.
