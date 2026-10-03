# The native baseline's times are not comparable with rubi's

Status: ready-for-agent
Type: harness fidelity (timing)
Filed: 2026-10-03 (user request: time both arms the same way, then shared
maxima-rubi / native time histograms in the grade report artifact)

## Symptom

Native-baseline times (`test/corpus_class<N>.baseline.out`, `t=`) start at
0.3 s, even for `integrate(x, x)`; rubi's records start at 0.0 s. Over the
answered entries (verified/expected/unverified) of every section, no native time
is below 0.3 s (599 at 0.3, 24,294 at 0.4, 10,283 at 0.5), while 40 % of rubi's
section-1 passes are under 0.1 s.

## Cause (measured 2026-10-03, `probes/timing/01-first-call-cost.sh` / `.out`)

Both arms are timed alike: `test/corpus_driver.py` `build_text` brackets the one
integrator call with `elapsed_run_time()` (Maxima's CPU clock) and prints
`printf(true, "ANSWERED ~,3f~%", elapsed_run_time() - mr_t0)`; that value is the
record's `t=`. `showtime` is not involved. They differ in two ways:

1. **`printf`'s autoload is inside the timed window.** In stock Maxima `printf`
   is an autoload stub (`stringproc`). The first `printf` call loads
   `stringproc` *before* its arguments are evaluated, so the load (about 0.23 s
   CPU) is in `elapsed_run_time() - mr_t0`. The rubi core has `stringproc`
   loaded already, because the package uses `printf`, so rubi never pays it.
   Measured (probe A, the driver's own `build_text`, MR_BASELINE=1, build
   `branch_5_50_base_84_g4204fb669`): `integrate(x, x)` ANSWERED 0.237-0.246 as
   is, 0.000 with `load(stringproc)` before `mr_t0`; `risch(x, x)` 0.227-0.233
   vs 0.000-0.001. Probe B: in a stock batch, the first printf-timed
   expression costs about 0.23 s even when it is `1+1`, and integrate after it
   costs 0.000.

   **integrate and risch have no first-call cost of their own.** Probe D times
   ten integrands (trig, rational, sqrt, exp, log, elliptic, parametric) with no
   `printf` in the window, in a cold process and after an `integrate(x,x)` /
   `risch(x,x)` warm-up: the medians are identical to 0.1 ms for every integrand
   and both integrators. The first draft of this ticket blamed integrate's
   first-use loading; its 0.244 s figure was the `printf` load too. Probe C:
   saving a stock image after warming integrate/risch leaves the 0.23 s (the
   warm-up never called `printf`). A rules core with warmed integrate/risch,
   one image for both arms (the user's suggestion), shows 0.000 only because
   the package had loaded `stringproc`. It is not needed: it brings no gain over
   the one-line fix below, the native arm would stop being stock Maxima, and
   that arm would become tied to the rule-file fingerprint.

   The baseline records show 0.3-0.5 s rather than 0.23 s (section 1: 21,686 of
   25,716 lines at `t= 0.4`). That is probably the 24-worker run inflating the
   load's CPU (SMT, AGENTS.md "1.35x inflation"); not measured under load.
2. **The integrate -> risch hand-off.** When `integrate`'s class is
   `timeout`/`error`/`deferred`/`contains-noun`/`unverified`, `run_entry_detail`
   re-runs the entry with `risch` in a second process and, when risch passes,
   the record takes risch's verdict and **risch's time only**
   (`corpus_driver.py`, `who, r, dt = "risch", r2, dt2`). The time integrate
   spent failing first is in the `.via` sidecar but not in `t=`, so `t=`
   understates what a user who tries `integrate` and then `risch` waits.

## Wanted

- **No `printf` load in the window**: compute the time before calling `printf`,
  `mr_dt : elapsed_run_time() - mr_t0$` then `printf(true, "ANSWERED ~,3f~%",
  mr_dt)$`. This applies to both arms; the rubi arm's numbers do not change,
  since `stringproc` is already in its core. No warm-up call and no shared image.
- **The hand-off time counted**: when the record takes risch's verdict, `t=` is
  integrate's CPU plus risch's, under the single budget of the decision below.
  The per-leg times stay in `.via`.
- The record's `filter:` line states the timing mode (e.g. `timing: dt-first`),
  and the mergers refuse to mix modes, like the cap kind. Older native records'
  `t=` carry the `printf` load and are not comparable on time.

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
`cos(a+b*x)/(c+d*x)^(2/3)` (4.2.10 e71: integrate's gamma_incomplete answer is
WRONG -- with mpmath principal-branch arithmetic its derivative misses the integrand
by 0.16-0.32 at x = 0.3/0.7/2 (a,b,c,d = 1,2,3,5) -- and risch's expintegral_e answer
is right to 1e-17; a genuine rescue. The same check shows Rubi's reference answer,
which rubi reproduces exactly, right to 1e-17, although rubi's record calls it
`unverified`: Maxima's float evaluation puts `(%i*y)^(2/3)` on another branch).

Implementation note: the remaining budget is `TIMEOUT - integrate's CPU` (the
ANSWERED value, or the process CPU when integrate never returned); a risch leg
whose remaining budget is <= 0 is not run, and the entry keeps integrate's class.

## Acceptance

- Guards: `test/test_driver_baseline.py` gains the `printf`-free window (the
  text computes `mr_dt` before any `printf`) and the summed time (no Maxima).
  The first-call probe is `probes/timing/01-first-call-cost.sh` (committed
  2026-10-03); after the fix, its probe A "as is" rows should read 0.000.
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
