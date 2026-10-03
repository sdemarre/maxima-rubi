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

## Decision needed before implementing

- **The cap when the times are summed**: each leg keeps its own 30 s cap today.
  With `t=` the sum, a risch-answered entry can show `t=` above 30 s although
  neither leg hit its cap. Options: (a) keep per-leg caps and allow `t=` > 30 s
  for risch-answered entries (the histograms then need a "> 30 s" bin for the
  native arm); (b) give risch only what integrate left of the 30 s; (c) report
  the sum but cap the histogram at 30 s and count the rest separately.

## Acceptance

- Guards: `test/test_driver_baseline.py` gains the warm-up and the summed time
  (no Maxima); the first-call probe committed under `probes/`.
- A full native re-run of sections 0-8 (`setsid sh test/baseline_measure.sh`,
  about 9 h with 24 workers -- overnight). The verdicts must not move except at
  the cap: A/B with `test/ab_records.py` and `test/ab_grades.py` against the
  2026-09-30/10-01 baseline records, every PASS -> FAIL attributed.
- Then the follow-up the user asked for: **shared time histograms** in the grade
  report artifact (https://claude.ai/artifact/XHpx6cnE6geM8QV8Y1vN8L), maxima-rubi
  and native Maxima side by side per section on the same 1-2-5 bins (`<0.1` ...
  `20-30` s, plus whatever the cap decision above adds), each arm as a share of
  its own passing integrals. The rubi-only panels of version 9 are the template.
