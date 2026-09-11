# Matcher spike 01 — can Fateman's mma4max matcher replace `defmatch`?

Brief: `handoffs/2026-09-11-matcher-spike.md` (question, case set, fixed gate).
Branch `matcher-spike` (off `class3-deferred` @ `d535e24`).

**Stamps.** Maxima `branch_5_50_base_84_g4204fb669` (build 2026-08-31
13:27:47), SBCL 2.6.7 — `build_info()` in both outputs.
`01-mma4max-feasibility.out` run 2026-09-11 19:35 UTC;
`01-corpus-arity.out` run 2026-09-11 19:33 UTC. References:
`reference/fateman/PROVENANCE.txt` (mma4max = Wayback 2022-01-18 + nilqed/abcl_maxima
@ `097b49b0`; `newmatch.lisp` 2011-03-21), `reference/rubi` @ `61e9c18e`
(pins in `todo/TODO.md`).

**Re-run.** `sh probes/matcher/01-mma4max-feasibility.run` (~8 min; prints the
summary lines) and `python3 probes/matcher/01-corpus-arity.py >
probes/matcher/01-corpus-arity.out` (~1 min). No rule files are loaded, so no
`--tls-limit` flag.

## Verdict: **FORK**

The gate, applied as written in the brief:

| LIBRARY clause | measured | result |
|---|---|---|
| every group G1–G7 ≥ 90 % correct bindings | 53/53 (100 % in each group) | pass |
| zero false matches on NEG | **3/15** (N-07, N-14, N-15) | **FAIL** |
| median ≤ 0.5 ms per match, no case > 50 ms | median of per-case medians 0.0445 ms; worst single match 16.5 ms | pass |
| converter ≤ ~300 lines, no simplification of its own | 29 lines (23 code) | pass |
| loads without editing more than a handful of lines | 0 source edits | pass |

LIBRARY fails on the NEG clause. Against the OWN clauses:

- *Semantic failures in ≥ 2 groups that are not local* — none: 53/53
  positives bind as Mathematica would.
- *A false match rooted in the design* — the 3 false matches have **one root
  cause in one function**, `mblank1` (below). The behaviour is a deliberate
  choice in Fateman's design — his own `matchtests.lisp:241` expects it and
  annotates `;;?? mma would fail.` — but it is local in the code: a one-line
  guard removes all three false matches with no change to any positive case
  (experiment below). Judged **local → FORK**.
- *Inherent combinatorial blowup* — `matchfol` is exponential (~3× per extra
  summand, SCALE series). It is confined to one named function — the brief's
  own FORK example is "the Flat+Orderless path" — and the corpus's starting
  integrands stay far below the sizes where it bites (Plus/Times args p99 5,
  max 9). Judged **local → FORK**, with `matchfol`'s search named as the one
  change that is a rewrite rather than a patch.
- *Most of the code would need rewriting to load and run* — no: 0 edits.

**The judgement call, stated plainly:** both OWN-adjacent findings were
classified local because each is confined to one named function and the
first is fixed by a measured one-line change. A reader who weighs "rooted in
the design" by intent rather than by code locality (the identity binding is
intended), or who treats an exponential Flat+Orderless search as inherent,
would read OWN. The evidence for either reading is below; the design step
should confirm the reading before committing to it.

## Per group

| group | mechanism | positives correct | cases | what `defmatch` does today (cited per case in the `.out`) |
|---|---|---|---|---|
| G1 | Optional defaults `a_.`, `m_.`, `F_^(g_.*(e_.+f_.*x_))` | 11/11 | G1-01..11 (+ G1-04 model) | synthetic controls; `(2*x)^m` "uncatchable" (see §model) |
| G2 | product factor order, both stored orders | 8/8 | 4 targets × 2 orders | pass-2 whole-table reverse rescan (e115: record `deferred`) |
| G3 | exponent 1 dropped at construction | 7/7 | incl. e20 (1.1.2.6), e171, e67 | pass-3 `findfun` shadow; M2 rows adjudicated "faithful 0-bind" |
| G4 | bare-factor permutation | 6/6 | e5, e91 (both orders), e209, e215 | pass-4 sweep — correct but rejected on cost |
| G5 | slotted inner exponent (C1/C5) | 11/11 | e1, e183, K1, e367, e130, e251, e446, e387, 3.4 L63/66/67 | 0-binds (probes Q1/Q2/K1/K2/P1) |
| G6 | ratio log-argument (C3) | 5/5 | e93, e178, e236, e10, e214 | 0-binds (probe pA) |
| G7 | monomial head `(d*x)^m` (C2/M6) | 4/4 | e65, e66, L14 tree, e191 (+ G7-M1 model) | 0-binds |
| NEG | must not match | 12/15 correct | N-01..15 | — |
| CTL | repeated-name consistency; two Optionals under one head | 1/2 | C-01 ok, C-02 **false negative** | — |

The FreeQ condition is honoured with backtracking: N-03, N-04 and N-10 match
structurally (`struct=T`) and are correctly vetoed by the condition
(`matched=NIL`).

## Root causes, named

1. **`mblank1`** (`newmatch.lisp:1041-1064`; the binding
   `(spush env name (or e (|Default| gh)))` at `:1055-1056`). When a Flat
   remainder is empty (`e` = NIL) a named Blank binds the head's identity (0
   for Plus, 1 for Times). Mathematica never lets a Blank match nothing. The
   false matches:
   - N-07 `x^5*(a+b*log(c*x^n))` vs 3.1.3.m L4 `(d_+e_.*x_^r_.)^q_.*(…)` →
     `d=0 e=1 r=1 q=5` (i.e. `x^5` read as `(0+1*x^1)^5`);
   - N-14 `x^m*log(c*(d+e*x^n)^p)` vs 3.4.m L14 `(f_*x_)^m_*…` → `f=1`;
   - N-15 `x^m*(c+d*x)` vs 1.1.1.2.m L4 `(a_+b_.*x_)^m_.*(c_+d_.*x_)` → `a=0 b=1`.

   **Experiment** (runtime redefinition; reference file untouched): a nil-guard
   (`and e …`) on `mblank1` → `PATCHED NEG false matches 0/15`, every group
   still 100 %, only N-07/N-14/N-15 change (`PCASE` lines). Fateman's own
   suite goes 147/149 → 135/149: the 8 new failures (62 63 65 71 77 80 81 83)
   are exactly the tests that expect a Blank to bind 0/1 from an empty
   remainder, which Mathematica rejects (e.g. #81 `Plus[a, x_]` vs `a` →
   `x=0`); the other 4 (139 140 146 147) produce the same bindings in a
   different alist order.
2. **`remopts` / `mapremopts`** (`newmatch.lisp:568-596`, `:2084-2091`).
   `remopts` rewrites only the first `Optional` of an argument list into
   `Alternatives` and returns; the level is not revisited. Control C-02
   `Times[a_., b_., x_^m_]` vs `x^3` → no match (Mathematica: `a=1 b=1 m=3`).
   How many Rubi LHSs put two Optionals directly under one head is **not
   measured** (a text grep is not level-aware).
3. **`matchfol`** (`newmatch.lisp:1543-1680`). For each non-atomic pattern
   term it enumerates every subset of the expression's arguments (`docomb`,
   `:1645`). SCALE series, 1.2.1.1.m L9 `(a_.+b_.*x_+c_.*x_^2)^p_`, minimum of
   3 single matches (ms):

   | summands | no match (`N`) | patched | summands | match, `a_.` absorbs z's (`M`) | patched |
   |---|---|---|---|---|---|
   | 4 | 0.321 | 0.139 | 5 | 1.683 | 0.418 |
   | 6 | 3.044 | 1.344 | 7 | 17.701 | 4.203 |
   | 8 | 27.604 | 12.629 | 9 | 138.382 | 38.579 |
   | 10 | 267.289 | 118.718 | 11 | 1197.551 | 358.822 |
   | 12 | 2414.501 | 1083.659 | 13 | 7192.731 | 3293.441 |

   ~9–10× per two summands (~3× per summand), bindings correct throughout;
   the guard halves the constant, not the growth.
4. **Evaluation during matching** (code reading, no wrong binding observed in
   the case set): `remopts` evaluates the default-substituted pattern
   (`(meval s)`, `:595`); `bindifposs` (`:859`) and `mpattern` (`:894`)
   evaluate subexpressions when a name is already bound. mma4max's evaluator
   carries rules (e.g. `Int`), so a port should match structurally.

## Corpus sizes (`01-corpus-arity.out`)

All 29,747 class-1..3 entries simplify (0 failures); per integrand, the
largest Plus-or-Times argument count anywhere in the tree: p50 3, p90 4,
p99 5, **max 9**; ≥ 8 args: 25 entries (0.08 %), ≥ 10: none. Top-level
Plus/Times: p99 4, max 8. Read against the SCALE table, a failing 3-term Plus
search at the corpus p99 size costs between 0.32 ms (4 summands) and 3.0 ms
(6); at the corpus maximum between 27.6 ms (8) and 267 ms (10) — per rule
tried. **Not measured:** the sizes of intermediate integrands produced during
rewriting (expansions), and how many rules a dispatch would try per integrand.

## Timing (gated case set, unpatched)

71 cases (200 single matches + a 1000-match batch each): per-case median min
0.0005 / p50 0.0445 / p90 0.1563 / max 7.0425 ms; worst single match 16.5 ms;
no timeouts or errors. Slowest by batch mean: N-10 7.23 ms (a failing search
over the 3-factor ratio log-argument), G6-01 1.15, G6-02 1.14, G6-03 0.63,
G1-08 0.34 ms. Per-rule preparation (Optional rewrite + variable renaming,
mma4max's `rulefix` path) 0.08–3 ms for these LHSs; the full-table cost is
not measured.

## Expression model (not the matcher)

Two targets cannot be posed faithfully because Maxima's simplifier stores
them in shapes Mathematica does not produce; both are excluded from the gate
and reported as `MODEL`:

- G1-04 `(2*x)^m` is stored as `2^m*x^m` → no match; the Mathematica-form
  twin G1-04t `Power[Times[2,x],m]` binds `a=0 b=2 m=m`.
- G7-M1 `(d*x^2)^m` is stored as `d^m*abs(x)^(2*m)` → no match; the twin
  G7-03 binds `d=d q=2 m=m`.

How many corpus integrands carry such rewrites is not measured.

## Loading and harness observations

- **Loads with 0 source edits**: the 16 files of `init.lisp`'s list, from
  source, in order (`01-mma4max-load.lisp`; `LOAD … OK` lines in the `.out`).
  The loader then calls `initialize-mma`, as mma4max's own entry point `(tl)`
  does — it is what gives Plus/Times their Flat/Orderless/Default attributes.
- **Fateman's suite** (`matchtests.lisp`: `tests`, `rubit`, `tests2`):
  147/149 (`SMOKE` line); the two failures are a `Complex` destructuring case
  and the one `tests2` case his own comment marks broken. The file is read
  with the standard reader, where `Sin` becomes `CL:SIN`; the runner maps it
  to `|Sin|` (mma's package uses CL).
- **Package hygiene the port must fix** (code reading): `newmatch.lisp:32`,
  `parser.lisp:27`, `simp1.lisp:20` proclaim `(speed 3) (safety 0)` globally
  — inside Maxima this leaks to everything compiled afterwards; the binding
  stack (`stack1.lisp:13-31`) sizes its arrays from the special `SIZE` (100)
  and `spush` has no overflow check (the probe binds 5000).
- **Session observations, not committed as probes:** mma4max's
  `parser.lisp` `pstring` blocked on a string in this SBCL (two attempts,
  killed at their caps) — the patterns were therefore hand-transcribed into a
  compact FullForm notation (the generator can emit that directly);
  `get-internal-real-time` advanced in ~1 ms steps (the first run's integer
  millisecond maxima), so the probe times with `sb-unix:clock-gettime`;
  `sb-sys:with-deadline` did not interrupt a compute loop, `sb-ext:with-timeout`
  did.

## Committed claims this spike contradicts (not re-adjudicated here)

Read with Mathematica pattern semantics against the pinned `.m` text:

1. **M2 "faithful 0-bind in both systems"** (`adjudication-g1.md:213`;
   `docs/corpus-class3-deferred-uplift.md` §2 Wave 1 D, M2 ×28). The `.m`
   covers carry `q_.` — optional — (3.1.4.m L5 and L25 as pinned), so
   Mathematica binds a bare binomial with `q=1`; G3-05 binds e171 that way.
   L5's remaining conditions (`IGtQ[q,0] && IGtQ[m,0]`) hold for `q=1, m=5`
   (derived, not run).
2. **e191 "faithful reject — `FreeQ[m,x]` rejects m=−1+n"** (uplift §2 Wave 1
   D). `FreeQ[-1+n, x]` is True; 3.1.2.m L13's only condition is that FreeQ,
   and G7-04 binds `d=1 m=-1+n p=p`.
3. **e387's cover "3.1.4.m r24/L30"** (`adjudication-g1.md:246`). L29/L30
   require an `(f_.*x_)^m_.` factor, which is not optional as a factor: N-12
   does not match (as in Mathematica); 3.1.3.m L4 binds e387 (G5-08).
4. **Dead shape C "numeric-literal factor in the power base: uncatchable by
   ANY pattern form"** (`matcher-probe-series.md:62`). The target never
   reaches a matcher in that shape: Maxima stores `(2*x)^m` as `2^m*x^m`
   (G1-04 tree).

## Secondary: the other lineages

`reference/fateman/other/mixima/translator/match.lisp` (688 lines) and
`other/mockmma/match.lisp` (684) differ by 114 lines, contain no `remopts` or
`matchfol`, and say so in their headers: "version 15 does not include
flat+orderless. or Optional", "Orderless functions are matched only if they
have a fixed number of arguments", "Functions which are both Flat and
Orderless … not handled by this version" (mockmma adds "version 16 doesn't
work as well"). mma4max's own older `match.lisp` has neither function either.
They add nothing beyond `newmatch.lisp` (static section of the `.out`).

## Case table

Expected bindings are hand-derived from Mathematica semantics (the `why:`
line of each case in the `.out`, with the pattern-variable `x` always bound
to `x`); `\|` separates admissible alternatives the FreeQ clause cannot
separate. "swap" = the same target with its top-level factors reversed.
Per-case timings, trees, bindings and the `defmatch`-today citation are in
`01-mma4max-feasibility.out`.

| id | group | rule (.m, pinned) | target | expected | matched | verdict |
|---|---|---|---|---|---|---|
| G1-01 | G1 | 1.1.1.1.m L5 | `x^3` | m=3 | T | OK |
| G1-02 | G1 | 1.1.1.1.m L5 | `x^m` | m=m | T | OK |
| G1-03 | G1 | 1.1.1.1.m L7 | `(3+2*x)^4` | a=3 b=2 m=4 | T | OK |
| G1-04 | G1 (model) | 1.1.1.1.m L7 | `(2*x)^m` | a=0 b=2 m=m | NIL | WRONG (model) |
| G1-04t | G1 | 1.1.1.1.m L7 | tree `(Power (Times 2 x) m)` | a=0 b=2 m=m | T | OK |
| G1-05 | G1 | 1.1.1.1.m L7 | `(1+x)^m` | a=1 b=1 m=m | T | OK |
| G1-06 | G1 | 1.1.1.1.m L7 | `x^3` | a=0 b=1 m=3 | T | OK |
| G1-07 | G1 | 1.1.1.2.m L15 | `(1+2*x)^3*(4+5*x)^(1/2)` | a=1 b=2 m=3 c=4 d=5 n=1/2 \| a=4 b=5 m=1/2 c=1 d=2 n=3 | T | OK |
| G1-08 | G1 | 2.1.m L8 | `x*exp(2*x)` | c=0 d=1 m=1 F=%e g=2 e=0 f=1 \| … g=1 e=0 f=2 | T | OK |
| G1-09 | G1 | 1.1.2.2.m L47 | `x*(a+b*x^2)^p` | c=1 m=1 a=a b=b p=p | T | OK |
| G1-10 | G1 | 3.3.m L4 | `log(c*(d+e*x)^n)` | a=0 b=1 c=c d=d e=e n=n p=1 | T | OK |
| G1-11 | G1 | 3.3.m L4 | `(a+b*log(d+e*x))^2` | a=a b=b c=1 d=d e=e n=1 p=2 | T | OK |
| G2-01 | G2 | 1.2.1.2.m L26 | `(d*x)^m/(b*x+c*x^2)` (e115) | e=d m=m b=b c=c p=-1 | T | OK |
| G2-02 | G2 | 1.2.1.2.m L26 | same, swap | e=d m=m b=b c=c p=-1 | T | OK |
| G2-03 | G2 | 1.1.2.2.m L47 | `(c*x)^m*(a+b*x^2)^p` | c=c m=m a=a b=b p=p | T | OK |
| G2-04 | G2 | 1.1.2.2.m L47 | same, swap | c=c m=m a=a b=b p=p | T | OK |
| G2-05 | G2 | 1.2.1.2.m L26 | `(d*x)^m*sqrt(b*x+c*x^2)` | e=d m=m b=b c=c p=1/2 | T | OK |
| G2-06 | G2 | 1.2.1.2.m L26 | same, swap | e=d m=m b=b c=c p=1/2 | T | OK |
| G2-07 | G2 | 3.1.2.m L13 | `(d*x)^m*(a+b*log(c*x^n))^2` | d=d m=m a=a b=b c=c n=n p=2 | T | OK |
| G2-08 | G2 | 3.1.2.m L13 | same, swap | d=d m=m a=a b=b c=c n=n p=2 | T | OK |
| G3-01 | G3 | 1.1.1.1.m L5 | `x` | m=1 | T | OK |
| G3-02 | G3 | 1.1.1.2.m L15 | `x*(a+b*x)` | a=0 b=1 m=1 c=a d=b n=1 \| a=a b=b m=1 c=0 d=1 n=1 | T | OK |
| G3-03 | G3 | 1.1.1.2.m L15 | `x*(a+b*x)^2` | a=0 b=1 m=1 c=a d=b n=2 \| a=a b=b m=2 c=0 d=1 n=1 | T | OK |
| G3-04 | G3 | 1.1.2.6.m L48 | `(e*x)^m*(A+B*x^2)*(c+d*x^2)^3/(a+b*x^2)^2` (e20) | g=e m=m e=A f=B; a=a b=b p=-2 c=c d=d q=3 \| a=c b=d p=3 c=a d=b q=-2 | T | OK |
| G3-05 | G3 | 3.1.4.m L5 | `x^5*(d+e*x^2)*(a+b*log(c*x^n))` (e171) | m=5 d=d e=e r=2 q=1 a b c n | T | OK |
| G3-06 | G3 | 3.1.2.m L13 | `x/(a+b*log(c*x^n))` (e67) | d=1 m=1 a b c n p=-1 | T | OK |
| G3-07 | G3 | 3.1.4.m L29 | `x*(d+e*x^2)*(a+b*log(c*x^n))` | f=1 m=1 d=d e=e r=2 q=1 a b c n | T | OK |
| G4-01 | G4 | 3.1.5.m L45 | `(a+b*log(c*x^n))*log(1+e*x)` (e5) | d=1 e=1 f=e m=1 r=1 a b c n p=1 | T | OK |
| G4-02 | G4 | 3.1.5.m L51 | `x*(a+b*log(c*x^n))*log(d*(e+f*x^2)^m)` (e91) | g=1 q=1 d=d e=e f=f m=2 r=m a b c n | T | OK |
| G4-03 | G4 | 3.1.5.m L60 | `x*(a+b*log(c*x^n))*polylog(2,e*x)` (e209) | d=1 m=1 k=2 e=e q=1 a b c n | T | OK |
| G4-04 | G4 | 3.1.5.m L60 | `x*(a+b*log(c*x^n))*polylog(3,e*x)` (e215) | d=1 m=1 k=3 e=e q=1 a b c n | T | OK |
| G4-05 | G4 | 3.1.5.m L56 | `(a+b*log(c*x^n))*polylog(2,e*x^2)` | k=2 e=e q=2 a b c n | T | OK |
| G4-06 | G4 | 3.1.5.m L51 | e91, swap | g=1 q=1 d=d e=e f=f m=2 r=m a b c n | T | OK |
| G5-01 | G5 | 3.1.4.m L5 | `x^3*(d+e*x)*(a+b*log(c*x^n))` (e1) | m=3 d=d e=e r=1 q=1 a b c n | T | OK |
| G5-02 | G5 | 3.1.4.m L5 | `x^5*(d+e*x^2)^2*(a+b*log(c*x^n))` (e183) | m=5 r=2 q=2 … | T | OK |
| G5-03 | G5 | 3.1.4.m L5 | `x^5*(d+e*x^r)^2*(a+b*log(c*x^n))` (K1) | m=5 r=r q=2 … | T | OK |
| G5-04 | G5 | 3.1.4.m L5 | `x^5*(d+e*x^r)*(a+b*log(c*x^n))` (e367) | m=5 r=r q=1 … | T | OK |
| G5-05 | G5 | 3.1.4.m L29 | `x^3*(a+b*log(c*x^n))*sqrt(d+e*x)` (e130) | f=1 m=3 r=1 q=1/2 … | T | OK |
| G5-06 | G5 | 3.1.4.m L29 | `x^5*(a+b*log(c*x^n))*sqrt(d+e*x^2)` (e251) | f=1 m=5 r=2 q=1/2 … | T | OK |
| G5-07 | G5 | 3.1.3.m L6 | `(d+e/x^(1/(q+1)))^q*(a+b*log(c*x^n))` (e446) | d=d e=e r=-1/(1+q) q=q … | T | OK |
| G5-08 | G5 | 3.1.3.m L4 | `(d+e*x^r)^2*(a+b*log(c*x^n))` (e387) | d=d e=e r=r q=2 … | T | OK |
| G5-09 | G5 | 3.4.m L12 | `x^3*log(c*(a+b*sqrt(x))^p)` (3.4 L63) | m=3 a=0 b=1 c=c d=a e=b n=1/2 p=p q=1 | T | OK |
| G5-10 | G5 | 3.4.m L5 | `log(c*(a+b*sqrt(x))^p)` (3.4 L66) | c=c d=a e=b n=1/2 p=p | T | OK |
| G5-11 | G5 | 3.4.m L12 | `log(c*(a+b*sqrt(x))^p)/x` (3.4 L67) | m=-1 a=0 b=1 c=c d=a e=b n=1/2 p=p q=1 | T | OK |
| G6-01 | G6 | 3.2.1.m L19 | `(A+B*log(e*(a+b*x)/(c+d*x)))/(a*g+b*g*x)^2` (e93) | f=a*g g=b*g m=-2 A B e a b c d n=1 p=1 | T | OK |
| G6-02 | G6 | 3.2.1.m L21 | `(A+B*log(e*(c+d*x)/(a+b*x)))/(a*g+b*g*x)^2` (e178) | f=a*g g=b*g m=-2 a=c b=d c=a d=b n=1 p=1 … | T | OK |
| G6-03 | G6 | 3.2.1.m L23 | `(A+B*log(e*(a+b*x)/(c+d*x)))/(f+g*x)^2` (e236) | f=f g=g m=-2 … n=1 p=1 | T | OK |
| G6-04 | G6 | 3.2.2.m L6 | `(a*g+b*g*x)^3*(c*i+d*i*x)^2*(A+B*log(e*(a+b*x)/(c+d*x)))` (e10) | f=a*g g=b*g m=3 h=c*i i=d*i q=2 \| swapped pair; n=1 p=1 | T | OK |
| G6-05 | G6 | 3.2.2.m L8 | `(a*g+b*g*x)^m*(c*i+d*i*x)^(-2-m)*(A+B*log(e*((a+b*x)/(c+d*x))^n))` (e214) | m=m q=-2-m \| swapped pair; n=n p=1 | T | OK |
| G7-01 | G7 | 3.1.2.m L13 | `x^3/(a+b*log(c*x^n))` (e65) | d=1 m=3 … p=-1 | T | OK |
| G7-02 | G7 | 3.1.2.m L13 | `x^2/(a+b*log(c*x^n))` (e66) | d=1 m=2 … p=-1 | T | OK |
| G7-03 | G7 | 3.1.2.m L14 | tree `(d x^2)^m (a+b log(c x^n))` | d=d q=2 m=m … p=1 | T | OK |
| G7-04 | G7 | 3.1.2.m L13 | `x^(-1+n)*(a+b*log(c*x^n))^p` (e191) | d=1 m=-1+n … p=p | T | OK |
| G7-M1 | G7 (model) | 3.1.2.m L14 | `(d*x^2)^m*(a+b*log(c*x^n))` | d=d q=2 m=m … p=1 | NIL | WRONG (model) |
| N-01 | NEG | 1.1.1.1.m L7 | `5*(3+2*x)^4` | no match | NIL | OK |
| N-02 | NEG | 3.1.4.m L7 | `x^5*(d+e*x^2)*(a+b*log(c*x^n))` | no match | NIL | OK |
| N-03 | NEG | 1.1.1.1.m L7 | `(a+b*x)^x` | no match (FreeQ veto) | NIL | OK |
| N-04 | NEG | 1.1.1.1.m L7 | `(x^2+b*x)^3` | no match (FreeQ veto) | NIL | OK |
| N-05 | NEG | 3.3.m L4 | `log(5+2*z)` | no match | NIL | OK |
| N-06 | NEG | 1.1.1.2.m L8 | `(1+x)^(1/2)*(1-x)^(1/3)` | no match (repeated `m_`) | NIL | OK |
| N-07 | NEG | 3.1.3.m L4 | `x^5*(a+b*log(c*x^n))` | no match | T | **WRONG** |
| N-08 | NEG | 1.1.2.2.m L47 | `(a+b*x^2)^p` | no match | NIL | OK |
| N-09 | NEG | 2.1.m L8 | `%e^(a+b*x)` | no match | NIL | OK |
| N-10 | NEG | 3.2.1.m L19 | `(A+B*log(x*(a+b*x)/(c+d*x)))/(f+g*x)^2` | no match (FreeQ veto) | NIL | OK |
| N-11 | NEG | 1.1.1.1.m L5 | `z^3` | no match | NIL | OK |
| N-12 | NEG | 3.1.4.m L29 | `(d+e*x^r)^2*(a+b*log(c*x^n))` (e387) | no match | NIL | OK |
| N-13 | NEG | 1.1.1.1.m L7 | `a+b*x` | no match | NIL | OK |
| N-14 | NEG | 3.4.m L14 | `x^m*log(c*(d+e*x^n)^p)` | no match | T | **WRONG** |
| N-15 | NEG | 1.1.1.2.m L4 | `x^m*(c+d*x)` | no match | T | **WRONG** |
| C-01 | CTL | 1.1.1.2.m L8 | `(1+x)^m*(1-x)^m` | a=1 b=1 c=1 d=-1 m=m \| a=1 b=-1 c=1 d=1 m=m | T | OK |
| C-02 | CTL | synthetic | `x^3` vs `Times[a_.,b_.,x_^m_]` | a=1 b=1 m=3 | NIL | **WRONG** |

"…" / "a b c n" abbreviate the log-factor slots `a=a b=b c=c n=n` (in G6: the
ratio slots `A=A B=B e=e a=a b=b c=c d=d`); the full expectations are in the
`.out`.

## Out of scope / not measured

Conditions other than `FreeQ`; rule-table integration and dispatch; full-table
preparation cost; intermediate-integrand sizes; the number of Rubi LHSs with
two Optionals under one head; the number of corpus integrands affected by the
§model rewrites. Timings are single-process on one machine and include GC
noise (single-match maxima vary; batch means are the stable figure).
