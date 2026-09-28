# radexpand:true rewrites the integrand before rubi sees it: sqrt(c*x^2) -> sqrt(c)*abs(x)

Status: closed 2026-09-28 — documented (README, rubi definition); no package fix; harness keeps defaults
Type: Maxima behaviour / harness fidelity (655 FAIL entries over classes 1, 4, 6)
Filed: 2026-09-28

## Symptom

`rubi(x*sqrt(c*x^2), x)` at a default Maxima prompt returns
`sqrt(c)*'unintegrable(x*abs(x), x)`. Wrapped as
`block([radexpand:false], rubi(x*sqrt(c*x^2), x))`, it returns
`(c*x^2)^(3/2)/(3*c)`, which verifies.

## Mechanism

Maxima's general simplifier rewrites the integrand **when the expression is
evaluated**, before `rubi` receives it. For a literal typed at the prompt, that
happens as the line is evaluated. Under the default `radexpand:true`
(`domain:real`), roots of products and powers are rewritten in four ways:

| rewrite | example | becomes |
|---|---|---|
| even power under a root → `abs` | `sqrt(c*x^2)`, `sqrt(cos(x)^2)`, `sqrt(-9/n^2)` | `sqrt(c)*abs(x)`, `abs(cos(x))`, `3*%i/abs(n)` |
| whole powers pulled out of a root | `sqrt(x^4*(a+b*x^3))` | `x^2*sqrt(b*x^3+a)` |
| root of a product split | `((x-3)*x)^(2/3)`, `(b*sin(x))^(1/3)` | `(x-3)^(2/3)*x^(2/3)`, `b^(1/3)*sin(x)^(1/3)` |
| sign pulled out of an odd root | `(-b)^(1/3)` | `-b^(1/3)` |

Only the first produces something rubi cannot integrate at all. The other
three are harmless for most entries (see question 5 below).

`mr_model_flags` (default true) binds `radexpand:false` only around the
dispatch. By then the argument has already been simplified. The corpus
driver's `mr_f: <integrand>$` is evaluated under the defaults, like a user's
input.

**Not a port defect.** No integration rule in the pinned Rubi has `Abs` in
its pattern. `Abs` appears in three places only: one rule condition (4.7.4,
`EqQ[d/b, Abs[m+2]]`) and two utility functions (`IntegrationUtilityFunctions.m`
lines 688 and 3190). Mathematica never turns `Sqrt[c*x^2]` into `Abs`, so Rubi
never meets one. The corpus has no `abs(` in any entry: every `abs` rubi sees
was made by Maxima from a `sqrt` the corpus wrote. Maxima's `integrate`
handles `abs` with its own code, which Rubi has no counterpart for. Adding
`abs` rules would be integration beyond Rubi.

**This is arguably a Maxima bug.** The list has argued it for years.
`../maxima-lists/research/reports/sqrt-x2-abs-x.md` collects the threads:
- Fateman (2012): "I think it is an error to simplify sqrt(z^2) to abs(z)".
- Willis (2016): "not a legitimate simplification".
- #4453 and #2123 propose binding `radexpand:false` / `domain:complex` inside
  radcan; both are still open.

**Correction to that report, measured on build
`branch_5_50_base_84_g4204fb669`, 2026-09-28.** The report says
`block([radexpand:...], ...)` binds the flag too late (bug #3585486, 2012).
That does not reproduce here:
- `block([radexpand:all], sqrt(x^2))` gives `x`;
- `block([radexpand:false], sqrt(c*x^2))` gives `sqrt(c*x^2)`;
- `domain:complex` also leaves `sqrt(c*x^2)` alone.

Rubi handles the unexpanded form with its own rules. Traced with
`rubi_verbose:'matches` under `radexpand:false`:

- `x*sqrt(c*x^2)` fires **`1_4_1 r20`**, Rubi's polynomial "derivative
  divides" rule (1.4.1 source line 187):
  `Int[P*Q^m] = lc(P)*x^(p-q+1)*Q^(m+1) / ((p+m*q+1)*lc(Q))`, with `p` =
  deg P, `q` = deg Q and `lc` the leading coefficient. Its condition checks
  that P has exactly the shape that makes this the derivative. Here P = x,
  Q = c*x^2 and m = 1/2, which gives `(c*x^2)^(3/2)/(3*c)`.
- `(a+b*x)*sqrt(c*x^2)/x^3` fires **`1_4_1 r43`**, the piecewise-constant
  extraction (source line 352):
  `Int[u*(c*(a+b*x^n)^q)^p] → [(c*(a+b*x^n)^q)^p/(a+b*x^n)^(p*q)] * Int[u*(a+b*x^n)^(p*q)]`,
  under `GeQ[a,0]`.
  - It matches with a=0, b=1, n=1, q=2 and p=1/2, and pulls out
    `sqrt(c*x^2)/x`, which is constant on each side of 0.
  - The final answer, `sqrt(c*x^2)*(b*log(x)-a/x)/x`, is the corpus's own
    expected form (1.1.1.2 e762).
  - This is a 1.4.1 rule in the pinned Rubi, not a 1.1.3.2 rule as the handoff
    guessed.

## Measurement

`probes/integrate-beats-rubi/04-*`, 2026-09-28, build
`branch_5_50_base_84_g4204fb669`, master `a7ee2a3`, 30 s cpu cap, 12 workers.

**Stage 1 — which integrands are affected** (`04-radexpand-parse-set.{py,out,tsv}`).
- Every corpus integrand was simplified under both settings: 70,385 entries in
  about 20 s.
- An entry is **affected** when the two results differ. It is **`abs`** when
  only the default result carries `abs`.
- **affected PASS / FAIL** say whether master's current record
  (`test/corpus_class<N>.pfs.out`) passes or fails the entry.

| class | affected | of which `abs` | affected PASS | affected FAIL |
|---|---:|---:|---:|---:|
| 1 | 565 | 423 | 144 | 421 |
| 4 | 628 | 110 | 476 | 152 |
| 6 | 197 | 62 | 115 | 82 |
| 2, 3, 5, 7, 8 | 0 | 0 | 0 | 0 |
| **all** | **1,390** | 595 | 735 | **655** |

The handoff's regex count, 341 entries in class 1 only, was a floor.

**Stage 2 — driver A/B** (`04-radexpand-ab.{py,log}`, records
`04-radexpand-ab.<arm>.out`, diffs `04-radexpand-ab.stock-<arm>.ab`).

- The entries are the 1,390 affected ones plus a seeded control of 1,100
  unaffected entries spread over all eight classes.
- There are three arms, each run through the driver's own `run_entry`:
  - **stock**: the driver unchanged.
  - **whole**: `radexpand:false` for the whole entry text, so the integrand,
    the expected answer and the verification all run under false.
  - **parse**: `radexpand:false` only while `mr_f` is evaluated; the rest
    runs as stock.

| arm | PASS | vs stock: FAIL->PASS | PASS->FAIL |
|---|---:|---:|---:|
| stock | 1,690 | — | — |
| whole | 2,262 | 576 | 3 |
| parse | 2,242 | 557 | 4 |

**Why stock already passes 1,690.** Affected does not mean `abs`: 795 of the
1,390 get one of the other three rewrites, which rarely matter.

| group (stock arm) | PASS | FAIL |
|---|---:|---:|
| control | 990 | 110 |
| affected, no `abs` | 706 | 89 |
| affected, with `abs` | 29 | 566 |

- With `abs`, 566 of 595 entries fail.
- Most of the 29 that pass carry `abs` on a parameter rubi treats as a
  constant, e.g. 4.7.5 e27, `sqrt(-9/n^2)` → `3*%i/abs(n)`.
- A few carry `abs(x)` and still pass, e.g. 1.3.2 e848 `1/sqrt((b+a/x)*x^2)`.
  They are not traced.

Split for the **whole** arm:

- **Affected entries:** 575 of the 655 FAILs pass (416 in class 1, 88 in
  class 4, 71 in class 6), and 1 entry is lost. 80 affected entries still fail:
  5 in class 1, 65 in class 4 and 11 in class 6.
- **Control:** 1 gain and 2 losses.

The 3 losses in the **whole** arm:

- **4.2.4.2 e1433**, `verified` at 26.1 s -> `timeout`, a control entry. It is
  lost in the parse arm too, and sits at the cap, so it is borderline timing.
- **1.2.3.2 e327**, `expected` -> `unverified`, a control entry. The integrand
  is `x^m/(1+x^4+x^8)`, so the integrand is not what changed: the expected
  answer's `sqrt(3)` terms do not close in the verification under false. The
  parse arm keeps it.
- **4.7.5 e46**, `expected` 0.4 s -> `timeout`, an affected entry.
  `sqrt((-4/9)/n^2)` stays unsimplified under false, and the rules take a
  different route.

**Whole against parse.** 23 entries pass in whole and fail in parse. Almost
all of them are **verification** effects:

- **4.1.0 e304–e320 and 6.4.2 e9–e49**, 16 entries such as
  `cos(e+f*x)^4*(b*sin(e+f*x))^(1/3)` and `(b*coth(c+d*x)^2)^(2/3)`. rubi's
  answer is the same in both arms, because the integrand is simplified the same
  way. The zero chain proves the answer under `false` and not under the
  default, where the result is `unverified` as in stock. So stock's
  `unverified` on these entries is likely a verifier failure on correct
  answers.
- **4.2.2.1 e779 and 4.7.5 e33/e106** pass in both stock and whole and fail
  only in parse. rubi answers the `false` integrand, but its answer is compared
  with an expected answer simplified under `true`, and the forms don't meet.
- **1.1.3.2 e2079 and 1.1.3.8 e90** go from `timeout` in stock and parse to
  PASS in whole.

Mixing the two settings within one entry is the incoherent option, so the
parse arm is dropped.

## Decision

**User decision, 2026-09-28: document it; do not fix it in the package.**
- rubi integrates what it receives. Getting `sqrt(c*x^2)` to rubi unsimplified
  is the caller's job:
  `block([radexpand:false], rubi(x*sqrt(c*x^2), x))`.
- The rationale: the rewrite is arguably a Maxima bug. It may one day
  disappear with the automatic simplification, and this case is an argument
  for removing it.
- There is no package-side undo of `abs` and no `abs` rules.

What the documentation must say (measured, `probes/integrate-beats-rubi/04`,
this session):

- The idiom works on an expression written **inside** the `block`, and on one
  built under `radexpand:false` beforehand:
  `g: block([radexpand:false], x*sqrt(c*x^2))$ rubi(g, x)` answers.
- It does **not** rescue a variable assigned at a default prompt:
  `f: x*sqrt(c*x^2)$ block([radexpand:false], rubi(f, x))` still gives
  `sqrt(c)*'unintegrable(x*abs(x), x)`. The value of `f` was simplified to
  `sqrt(c)*x*abs(x)` when it was assigned.

**The harness keeps Maxima's defaults** (user decision, 2026-09-28). The
records go on measuring what a user at a default prompt gets. The 655
affected FAILs stay FAIL and are attributed to this ticket, and
`04-radexpand-parse-set.tsv` lists them. The **whole** arm (+572 PASS on the
sample) is on record here as the ceiling, should the decision change.

The user-facing note goes in `README.md` and at `rubi`'s definition in
`maxima_rubi.mac`.
