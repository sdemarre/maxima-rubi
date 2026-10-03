# The native baseline's times are not comparable with rubi's

Status: ready-for-agent
Type: harness fidelity (timing)
Filed: 2026-10-03 (user request: time both arms the same way, then shared
maxima-rubi / native time histograms in the grade report artifact)

## Symptom

Every native-baseline time (`test/corpus_class<N>.baseline.out`, `t=`) is at
least 0.4 s, even for `integrate(x, x)`; rubi's records start at 0.0 s. Over the
passing entries, no native time in any section falls below 0.4 s, while 40 % of
rubi's section-1 passes are under 0.1 s.

## Cause (measured 2026-10-03)

Both arms are timed alike: `test/corpus_driver.py` `build_text` brackets the one
integrator call with `elapsed_run_time()` (Maxima's CPU clock) and prints
`ANSWERED <cpu>`; that value is the record's `t=`. `showtime` is not involved.
They differ in what the timed call includes:

1. **First-call loading.** rubi runs from the prebuilt image
   (`test/mr_rules.core`), its code loaded before the clock starts. The native arm
   is stock Maxima in a fresh process, and `integrate` loads parts of itself on
   first use, inside the timed call: a fresh `maxima --very-quiet -b` measured
   `integrate(x, x)` at 0.244 s CPU, then `integrate(x^2, x)` and
   `integrate(sin(x)*x, x)` at 0.000 s (build `branch_5_50_base_84_g4204fb669`;
   the probe text is in the 2026-10-03 session, to be committed as a probe by this
   ticket). `risch`, run in its own fresh process, pays the same kind of cost.
2. **The integrate -> risch hand-off.** When `integrate`'s class is
   `timeout`/`error`/`deferred`/`contains-noun`/`unverified`, `run_entry_detail` (`:1097`)
   re-runs the entry with `risch` in a second process and, when risch passes,
   the record takes risch's verdict and **risch's time only**
   (`corpus_driver.py:1136`, `who, r, dt = "risch", r2, dt2`). The time integrate
   spent failing first is in the `.via` sidecar but not in `t=`, so `t=`
   understates what a user who tries `integrate` and then `risch` waits.

## Wanted

- **A warm-up before the clock**, in the native arm: one throwaway call of the
  same integrator on a trivial integrand (`integrate(x, x)` / `risch(x, x)`)
  before `mr_t0`, so the timed call does not pay first-use loading. Measure
  whether rubi has any first-call cost from the core (a probe timing
  `rubi(x, x)` twice in a fresh core process); if it does, warm it up the same
  way so the arms stay symmetric, and say so in the record.
- **The hand-off time counted**: when the record takes risch's verdict, `t=` is
  integrate's CPU plus risch's. The per-leg times stay in `.via`.
- The record's `filter:` line states the timing mode (e.g. `timing: warm`), and
  the mergers refuse to mix modes, like the cap kind.

## Decision (user, 2026-10-03): one 30 s budget per integral -- option (b)

`risch` gets only what `integrate` left of the 30 s CPU cap; the record's `t=` is
the sum and never exceeds 30 s, the same budget maxima-rubi has. Rejected: (a) per-
leg caps with `t=` > 30 s (a "> 30 s" histogram bin only native could reach), (c)
summing but capping the histogram.

Measured on the 2026-09-30/10-01 baseline `.via` sidecars before deciding: risch's
verdict was taken on **1,295** entries (integrate first: contains-noun 400,
deferred 377, error 315, timeout 116, unverified 87; section 4 527, 1 408, 3 179,
7 96, 5 63, 8 12, 6 6, 2 4). integrate's time before risch: median 0.4 s, under
1 s on 88 %. **1,179 fit a shared 30 s budget and keep their verdict; the 116
whose integrate timed out become `timeout` under (b)** -- the expected PASS -> FAIL
of the re-run, not a regression; attribute exactly these. Examples (run
2026-10-03): `sqrt(x^2+x^3)` (integrate returns the noun, risch
`(sqrt(x+1)*(6*x^2+2*x-4))/15`); `sin(x)/(%i+cot(x))` (integrate errors);
`expintegral_e(-2,a+b*x)` (integrate leaves an interior integral);
`sin(a+b/sqrt(c+d*x))` (integrate times out, risch answers in < 1 s);
`cos(a+b*x)/(c+d*x)^(2/3)` (integrate's gamma_incomplete answer is unverified,
risch's expintegral_e form verifies -- the checker's limit, not risch's gain).

Implementation note: the remaining budget is `TIMEOUT - integrate's CPU` (the
ANSWERED value, or the process CPU when integrate never returned); a risch leg
whose remaining budget is <= 0 is not run, and the entry keeps integrate's class.

## Acceptance

- Guards: `test/test_driver_baseline.py` gains the warm-up and the summed time
  (no Maxima); the first-call probe committed under `probes/`.
- A full native re-run of sections 0-8 (`setsid sh test/baseline_measure.sh`,
  about 9 h with 24 workers -- overnight). The verdicts must not move except at
  the cap: A/B with `test/ab_records.py` and `test/ab_grades.py` against the
  2026-09-30/10-01 baseline records, every PASS -> FAIL attributed (expected:
  the 116 integrate-timeout risch rescues above).
- Then the follow-up the user asked for: **shared time histograms** in the grade
  report artifact (https://claude.ai/artifact/XHpx6cnE6geM8QV8Y1vN8L), maxima-rubi
  and native Maxima side by side per section on the same 1-2-5 bins (`<0.1` ...
  `20-30` s; under the decision above no time exceeds 30 s), each arm as a share of
  its own passing integrals. The rubi-only panels of version 9 are the template.
