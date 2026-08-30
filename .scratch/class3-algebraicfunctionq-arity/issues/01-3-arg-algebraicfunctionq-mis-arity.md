# `AlgebraicFunctionQ` 3-arg Rubi form: three generated rules call the 2-arg utility and fatal

Status: ready-for-agent
Type: bugfix (generator special-case + utility port)
Filed: 2026-08-30 (Task 10 of milestone 3 — the class-3 package run's
error census; root cause adjudicated by the Task-10 reviewer against
the run's own core image)

## Observation

`maxima_rubi_utils.mac:3109` defines

```
%mr_algebraicFunctionQ(u, x) := block(...)
```

with exactly TWO parameters (its header comment: "The generated
class-1 call is the 2-arg form, so flag is false: a power counts only
with an explicit rational exponent"). The generator renames
`AlgebraicFunctionQ` 1:1 (`generator/translation_table.py:66`) and
carries every argument through, so the three class-3 rules whose
pinned Rubi source uses the 3-arg form with the flag

- `Rubi/IntegrationRules/3 Logarithms/3.1.5 u (a+b log(c x^n))^p.m:34`
- `Rubi/IntegrationRules/3 Logarithms/3.3 u (a+b log(c (d+e x)^n))^p.m:35`
- `Rubi/IntegrationRules/3 Logarithms/3.3 u (a+b log(c (d+e x)^n))^p.m:65`

  (each ends `&& AlgebraicFunctionQ[AFx, x, True]`)

emit THREE-arg calls:

- `rules/class3/3_1_5.mac:679` — `%mr_algebraicFunctionQ(_mr_3_1_5_r30_AFx, x, true)`
- `rules/class3/3_3.mac:732` — `%mr_algebraicFunctionQ(_mr_3_3_r32_AFx, x, true)`
- `rules/class3/3_3.mac:1422` — `%mr_algebraicFunctionQ(_mr_3_3_r61_AFx, x, true)`

Calling a 2-arg Maxima `:=` function with 3 args is the uncatchable
fatal "Too many arguments supplied to %mr_algebraicFunctionQ(u, x)"
followed by "Control stack exhausted while pseudo-atomic" in the error
path (the utility body is never reached). Measured on
`branch_5_50_base_84_g4204fb669` (2026-08-29 17:58:20) / SBCL 2.6.7,
reproduced in isolation on the run's own core image at ~3.1 s.

## Corpus exposure (class-3 records, 2026-08-30)

- **Fired once**: 3.3 e492 L689 (suite file
  `3 Logarithms/3.3 u (a+b log(c (d+e x)^n))^p.mac`, entry 492) via
  rule 3_3 r61 — integrand
  `(a+b*log(c*(d*(e+f*x)^p)^q))^2/(g+h*x)^(3/2)`, AFx =
  `1/(h x+g)^(3/2)`. This is the `error` entry in both
  `test/corpus_class3.out` (t=3.2 s) and its 100 s re-check.
- **Not yet exercised**: 3_3 r32 (its LHS requires the log arg
  `c*(d+e*x)^n` — a different shape from r61's `c*(d*(e+f*x)^m)^n`;
  3_3 r32's condition returned false on the e492 integrand) and 3_1_5
  r30 (no 3.1.5 entry is `error` in either record; its only death,
  re-check e30, is a confirmed OOM with no arity message).
- The three rules are `Unintegrable`-answering fallbacks, so a fixed
  condition can only convert `error` → `no-answer`/`deferred`/an
  earlier rule's answer — never a verified answer.

## Root cause (adjudicated — do NOT re-diagnose as a Maxima builtin bug)

The Maxima error text is Maxima's arity error for a `:=` call; the
defect is the generated call, not the utility or the build. (The
initial report attributed it to "the builtin's handling of a
radical-with-fractional-power denominator" — refuted by the reviewer:
the utility body is never reached; the radical is merely the AFx
argument value printed in the message.)

Rubi's flag (IntegrationUtilityFunctions.m:1680-1681, pinned clone):
`AlgebraicFunctionQ[u_, x_Symbol, flag_:False]` — "If flag is True,
exponents can be nonnumeric": the PowerQ arm counts a power
`u[[1]]^u[[2]]` as algebraic when `RationalQ[u[[2]]] || (flag &&
FreeQ[u[[2]], x])`. The three rules require flag=TRUE semantics.

## Fix (option (a) — the only semantically correct one)

1. **Utility**: add a flag-aware 3-arg form next to the existing 2-arg
   one in `maxima_rubi_utils.mac` (Maxima `:=` functions have no
   optional args, so two definitions): keep
   `%mr_algebraicFunctionQ(u, x)` delegating with flag=false (the
   class-1 call shape, `rules/class1/1_4_1.mac` r34, is frozen by the
   byte-identity gate and must keep working), and add e.g.
   `%mr_algebraicFunctionQFlag(u, x, flag)` (name is a choice) whose
   PowerQ arm is `is(num(expo) = 1) and ... rational-exponent test ...
   or (flag and freeof(x, expo))` per the Rubi body; both delegate to
   one shared internal to keep a single source of truth. Add Layer A
   checks for the flag difference (a power with a symbolic x-free
   exponent: false under the 2-arg form, true under flag=true — e.g.
   `(x^2+1)^(a*x+1)`... pick an x-FREE exponent like `(x^2+1)^(a+b)`,
   and the e492 AFx shape `1/(g+h*x)^(3/2)` where 3/2 is rational →
   true under both).
2. **Generator**: special-case the `AlgebraicFunctionQ` rename — a 2-arg
   call emits `%mr_algebraicFunctionQ(a, b)` (unchanged), a 3-arg call
   with a literal `True`/`False` third arg emits
   `%mr_algebraicFunctionQFlag(a, b, true/false)`. (A generic
   "drop literal-True third arg" rule is NOT acceptable — see below.)
3. **Regenerate** `rules/class3/3_1_5.mac` + `rules/class3/3_3.mac`
   (only those two files carry the 3-arg call; 3_2_3 r19/r20 are
   2-arg and must stay byte-identical). Gates: `--class 1` → 3,026
   byte-identical + empty `git status --porcelain rules/` for the
   class-1 tree; `--class 2` → 125 byte-identical; Layer A green.
4. **Core + re-run**: rebuild `test/mr_rules.core` (fingerprint
   changes; update both mirrors in `test/build_rules_core.sh` and
   `test/corpus_driver.py` is NOT needed — the fp list already globs
   `rules/class3/*.mac`), re-run the TLS full-table probe
   (`probes/load_wall/probe-class3-load.run`), then a FULL class-3
   corpus re-run + merge (the three rules' conditions can now be
   evaluated, so the accepted record `test/corpus_class3.out` is no
   longer like-for-like) and the A/B against
   `test/corpus_class3.baseline.out` (expect e492 error → a non-error
   class; no other change expected, but the re-run is the proof).
5. **Why not option (b)** (strip the flag in the generator):
   semantically wrong — the 2-arg form returns `false` for
   `(g+h*x)^(non-rational)`-shape AFx where flag=true returns `true`
   (measured: 2-arg on `1/(h x+g)^(3/2)` is actually `true` because
   3/2 is rational, but for a symbolic exponent AFx the two forms
   differ) — stripping would silently narrow the three rules'
   coverage. The rules' semantics require the flag.

## Acceptance

- The three generated files carry the flag-aware call; the utility
  implements the Rubi flag body (cite the pinned .m line in the
  header comment, per repo convention).
- Gates: class-1/class-2 byte-identity EMPTY; Layer A 0 failed
  (including the new flag-difference checks); parse sweep of the two
  regenerated files clean; TLS probe `TABLE_AT_LOAD 3513` unchanged.
- Full class-3 re-run: completeness 3,085/3,085; 3.3 e492 no longer
  `error`; zero NEW `error` entries vs `test/corpus_class3.out` (the
  other 14 deaths are OOM/control-stack resource exhaustion, tracked
  separately); A/B vs the baseline re-read with the e492 transition
  recorded.
- Ledger/TODO pointers updated; the OOM and control-stack findings
  stay out of scope here.

## Comments
