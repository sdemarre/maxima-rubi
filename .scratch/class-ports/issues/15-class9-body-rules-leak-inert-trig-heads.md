# 9.3 body rules fire inside the inert-trig domain and leak `%mr_itan` & co into answers — at least 281 class-6 answers, 69 of them previously CORRECT

Status: fixed (c13e213, 2026-09-23); the four-class re-measure is pending with ticket 14
Type: bug (HIGH — unusable answers; the sharpest defect in the section-9 measurement)
Filed: 2026-09-23 (section-9 port, Task 14 attribution; spec
`docs/superpowers/specs/2026-09-22-section9-port-design.md` A6.2)

## The finding

The class-4 bridge record `4_1_0_1 r1` is Rubi's
`Int[u_,x_Symbol] := Int[DeactivateTrig[u,x],x] /; FunctionOfTrigOfLinearQ[u,x]`:
below it the integrand carries the six INERT trig heads (`%mr_isin` …
`%mr_icsc`), and only class-4/6 records — which re-activate as they emit — are
meant to run there. Our table has nothing between that deactivation and 9.3's
BODY, because class 4 is ported only as the eight-record bridge subset.

So `9_3 r41` — Rubi's
`Int[u_.*(a_.*v_^m_.)^p_,x] := a^IntPart[p]*(a*v^m)^FracPart[p]/v^(m*FracPart[p]) * Int[u*v^(m*p),x]`
(`9 Miscellaneous/9.3 Miscellaneous integration rules.m:346-348`) — fires on the DEACTIVATED
integrand and emits its prefactor OUTSIDE the recursive `mr_int`. Nothing
re-activates that factor, so an inert head reaches the user-visible answer.

The rule's condition is a byte-faithful port of the upstream line. In
Mathematica the specific `Int[(b_.*tan[c_.+d_.*x_])^n_,x_]` rules of 4.3.2 are
more specific and are tried first, so Rubi never gets here.

## Measured (2026-09-23, build `branch_5_50_base_84_g4204fb669`, SBCL 2.6.7)

Branch core `434c241a` (3,997 rules) vs reference core `0182d32c` (3,911):

- The driver names the leaked head on stderr, so the leak set can be counted
  exactly. Over the **paired rerun** of the changed entries
  (`test/section9_paired_class6.new/queue.log`) **286 entries leak**:
  `%mr_isin` 112, `%mr_itan` 92, `%mr_icsc` 46, `%mr_icos` 32, `%mr_isec` 2,
  and 2 entries carrying two heads — that partition is of the **286**, not of
  the 281 below.
- In the **full 24-worker record** (`test/corpus_class6.s9.out`) 281 of those
  286 are `error` and the other 5 are `timeout`: they hit the 30 s cap before
  the leaking answer was produced. So **281 is a FLOOR** on the number of
  leaking answers in that record, not the whole leak set. The reference core
  produced **zero** `error` verdicts and zero `inert-leak` stderr lines.
- The driver classifies such an answer `error`
  (`test/test_driver_inert_leak.py`), and EVERY `error` in
  `test/corpus_class6.s9.out` is one of these — no other kind of error occurs
  in that record.
- **89 of them were PASS before**: 39 `verified`, 30 `expected`, 20
  `no-answer`. All 69 of the previously-CORRECT ones carry `%mr_itan` — the
  `(b tanh)^(n/2)` and `(b coth)^(n/2)` families of `6.3.2` and `6.4.2`.

Witness — **committed probe `probes/section9/02-inert-leak.{mac,run,out}`**,
`sh probes/section9/02-inert-leak.run`:
`6 Hyperbolic functions/6.3 Hyperbolic tangent/6.3.2` e13
`(b*tanh(c+d*x))^(7/2)` (corpus: a closed form in 7 steps), `rubi_verbose` on
both cores:

- reference: `4_1_0_1 r1` deactivates, `4_7_5 r22` (the pure-tan substitution)
  answers, no inert head is left (`INERT_LEAK … | []`), and the record's verdict
  for the entry is `verified` at 0.4 s. (The probe's own one-step
  `RATSIMP_SELF_DIFF_ZERO` prints `false`; it is a cheap indicator, not
  `test/corpus_driver.py`'s zero chain, which is what decides `verified`.)
- branch: `4_1_0_1 r1` deactivates, then `9_3 r41` fires on
  `(-%i*%mr_itan(%i*(c+d*x)))^(7/2)` with
  `[m = 1, v = %mr_itan(%i d x + %i c), a = -%i, p = 7/2, u = 1]` and the answer
  is
  `-(b^3 sqrt(b tanh(d x+c)) sqrt(-%i %mr_itan(%i d x+%i c)) (…)) / (20 d sqrt(tanh(d x+c)) sqrt(%mr_itan(%i d x+%i c)))`.

The leaked expression is not a WRONG antiderivative — re-activating `%mr_itan`
would give a correct one — but `%mr_itan` has no meaning outside the bridge, so
the answer cannot be differentiated, verified or used.

## Suggested fix (not applied here)

Close the inert domain against class-9 (and any future non-trig) rules. Two
shapes were considered, neither measured:

1. Make the deactivation bridge apply `%mr_activateTrig` to the RESULT of the
   inner integral, so whatever a general rule emits is re-activated on the way
   out. Cheap, but it activates more than Rubi does and may change class-4/6
   answers that deliberately stay inert across a recursion.
2. Guard the class-9 records (or the dispatcher) so that an integrand carrying
   an inert head is only offered to class-4/6 records. Closer to Mathematica's
   specificity ordering, and it is what porting class 4 properly would achieve
   anyway (ticket 05).

Whichever is chosen, the gate is `test/test_driver_inert_leak.py`'s
classification plus a full class-6 A/B: the 281 `error` verdicts must go to
zero, and the 39 `verified` / 30 `expected` entries must come back.

## Related

- Ticket 05 (class-4 trigonometric port) — the real fix for the missing layer.
- Ticket 14 (`mr_giveup_last` vs 9.3's bare-`u_` tail) — 13 of these 89 entries
  are ALSO recovered by that experiment.
- Ticket 16 (`9_3 r41`'s match-enumeration blowup) — the same record, `9_3
  r41`, is implicated in both tickets; ticket 16's bisection (`only-r41`
  hangs on e190) is unrelated to the leak (e190 has no trig in it), so r41
  is worth looking at first for either defect, but neither ticket's fix
  necessarily fixes the other.
- `test/test_section9_e2e.mac`'s `mr_e2e_no_locals` check was blind to this
  leak (it filtered `listofvars`, and the six inert heads are operators, not
  variables); it now also rejects any of the six inert heads via `freeof`,
  pinned independently of the rule set by
  `test/test_section9_no_inert_leak.mac`'s synthetic witnesses. A target that
  routes through this leak still belongs with the fix, not before it -- the
  e2e gate must stay green until then -- but the gate can now catch it the
  day the fix lands.

## Fix (2026-09-23, commits d7f37dd -> c13e213)

**Shipped: `mr_inert_leak_misfire` (run switch, default true,
`maxima_rubi_dispatch.lisp`).** In the inert domain -- an integrand that
carries one of the six inert heads -- a NON-class-4 record whose answer also
carries one is a misfire in `mr-apply-rule` (beside the boolean-leak
misfire) and the walk goes on. Class-4 records re-activate as they emit and
are exempt. By induction on the recursion every answer in the inert domain
stays inert-free. The witness now routes `9_3 r41 misfire (inert head
leaked)` -> `4_7_5 r22`, the reference core's route.

**Suggested fix 2 was tried first and is WRONG** (d7f37dd, replaced by
c13e213): offering an inert integrand to class-4 records ONLY stopped every
leak but cost 650 class-6 PASS->FAIL against 209 FAIL->PASS
(`probes/section9/08-inert-guard-class6.class4-only.out`). Its premise --
nothing but class 4 acts on inert integrands -- was measured on the LEAK set
only (`probes/section9/07-inert-leak-census.out`: a non-class-4 record fires
inertly in all 284 finishing leak entries, r41 in 280; the pre-section-9
core, only 9_1 r11 in 2). Over the 650 losers
(`07-inert-leak-census.losers-pre.out`) 9_3 r51 (FunctionOfLinear) fires on
an inert integrand in 612, the 9.1 pull-outs in most of the rest: sound
records, and section 9's class-6 value. In Mathematica, too, general 9.x
rules act on an inert integrand whenever no more specific 4.x rule matches;
r41 is unsound there only because its prefactor keeps `v` outside Int.

**Measured** (`probes/section9/08-inert-guard-class6.out`; records
`test/section9_t15_class6.{pre,post}.out`): the whole of class 6, PAIRED --
pre-fix core `fa583d5f` (933a941) and fixed core `0fe237ca` (c13e213)
concurrently, 12 workers each, 30 s cpu cap, on a host carrying an emulator
(hence paired, not against the committed records):

- inert-leak answers **280 -> 0**;
- PASS 2,228 -> 2,388: **164 FAIL->PASS, 4 PASS->FAIL** -- the 4 are
  `verified -> timeout` at the cap boundary (28.4-30.0 s already in `pre`;
  r41 still pays for its recursion before it is declined);
- the ticket's gate: of the 89 entries the leak cost against the reference
  (`corpus_class6.s9-ref.out` PASS, `.s9.out` error), **all 39 `verified`
  and all 30 `expected` are back**; of the 20 `no-answer`, 13 are back and 7
  now read `contains-noun` (no leak).

Gates at c13e213: dispatch 80/0, section-9 e2e 7/0 (the leak witness
`(2*tanh(1+3*x))^(7/2)`, RED 6/1 with the switch off), rule-table order
11/0, Layer A 1293/0, no-inert-leak 5/0, mr-match 57/0, mr-tree 58/0,
generator P3 23/0, run-records 43/0.

Still open: ticket 16 (r41's match-enumeration cost, e190 has no trig) is
untouched by this fix; ticket 05 (class 4 proper) remains the real closure
of the inert domain.
