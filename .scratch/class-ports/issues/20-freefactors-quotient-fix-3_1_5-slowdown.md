# The FreeFactors quotient fix sends 3.1.5 e1 into an expression blowup (unverified -> timeout)

Status: needs-triage
Type: bug (a slowdown exposed by a correct fix; a FAIL -> FAIL transition)
Filed: 2026-09-25 (class-4 port, Step 7 — ticket 05)

## The finding

The class-4 port fixed `%mr_freeFactors` / `%mr_nonfreeFactors` to read a
quotient as the product it is (`ae6b7a6`: `FreeFactors[x/2]` was 1, it is
1/2 — Rubi's ProductQ reading, inflag:true). In the class-4 Step-7 slice A/B
(`probes/corpus/25-class4-slice-ab.out`) that fix is the cause of two
transitions (`probes/corpus/26-class4-slice-attribution.out`, the fix
toggled with everything else equal):

- A1, 1.1.1.5 e2 `(a+b x)^2 (A+B x+C x^2+D x^3)/sqrt(c+d x)`:
  timeout -> verified (17.7 s with the fix; no answer in 60 s without).
- A2, **3.1.5 e1 `(a+b log(c x^n))/(d+e x+f x^2)`: unverified (10.1 s) ->
  timeout**. Without the fix it answers in 14.6 s through 1_4_1, 3_3, 3_1_3,
  ...; with it, after 1_1_2_1 r13 and 1_2_1_1 r12 (the partial fractions of
  1/(f x^2+e x+d)), 1_4_1 r4's condition is tried over bindings carrying a
  polynomial of degree ~44 in e (`e^44 - e^43 sqrt(e^2-4 d f) ...`), and no
  rule fires within 60 s.

The fix itself is faithful; the likely reading is that a caller of
FreeFactors in the 1_2_1_1 / 1_1_2_1 partial-fraction path now takes a
different arm (a coefficient pulled out as the quotient it is) and the
following expansion swells. Not traced further.

## What to do

Run the full class-1/3 corpora on the class-4 tree (Step 9) and read the
FreeFactors-attributable transitions there; if the class-3 losses are more
than this one entry, trace A2 to the utility whose arm changed.
