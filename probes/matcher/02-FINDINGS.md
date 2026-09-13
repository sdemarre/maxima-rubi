# Matcher probe 02 — is every Rubi rule expressible with the mma4max matcher?

Brief: `handoffs/2026-09-11-matcher-design.md`, move 2 (static census + per-rule
round trip, before the design brainstorm). Branch `matcher-spike`.
Predecessor: `probes/matcher/01-FINDINGS.md` (spike, verdict FORK).

**Stamps.** Maxima `branch_5_50_base_84_g4204fb669` (build 2026-08-31
13:27:47), SBCL 2.6.7 — `build_info()` in `02-controls.out` and the round-trip
shard logs (quoted in `02-roundtrip.out`). Round-trip shards run 2026-09-11
21:56 UTC; controls 2026-09-11 22:05 UTC; census 2026-09-11. References:
`reference/rubi` @ `61e9c18e`, mma4max per `reference/fateman/PROVENANCE.txt`.

**Re-run.**
- `python3 probes/matcher/02-construct-census.py > probes/matcher/02-construct-census.out` (~5 s, no Maxima)
- `sh probes/matcher/02-roundtrip.run` (~5 min wall, 20 maxima shards; `MR_JUDGE_ONLY=1` re-judges)
- `sh probes/matcher/02-controls.run` (~30 s)
- self-tests: `python3 probes/matcher/02-mma-reader.py` (26/26), `python3 probes/matcher/02-roundtrip.py selftest` (14/14)

No rule files are loaded by any of them, so no `--tls-limit` flag.

## The answer

"Expressible" in the handoff's three layers:

1. **Pattern language (every LHS construct).** The 7,444 Int rules (all 7,432
   inventory runs plus 12 single-line ShowSteps wrappers) use a narrow
   language: named Blanks, `x_Symbol`, Optional `x_.` (always exactly one per
   argument list, under Times / Plus / as a Power exponent), repeated names,
   pattern-variable Power bases, pattern-variable heads `F_[..]` (77 rules),
   compound heads `Derivative[n_][f_][x_]` (21), literals (integers,
   rationals, `E` 208 rules, `Pi` 13, 3 reals) and `Complex[0, fz_]` (9). No
   LHS uses `x_:v`, `x:pat`, `_?test`, a condition inside the pattern,
   `Alternatives`, `Except`, `Repeated`, `HoldPattern`, `Verbatim`, a sequence
   blank or any typed blank other than `x_Symbol`. Every construct has a code
   path in `newmatch.lisp` **except `Complex[re, im]`** (gap G-3, 9 rules).
2. **Matching semantics (measured by the round trip).** With the spike's
   `mblank1` nil-guard, mma4max binds every valid witness correctly in
   **7,403 / 7,444 rules (99.45 %)** and makes **0 false matches on 37,747
   mutations**. The 41 rules that miss all carry a pattern-variable or compound
   head directly under Plus/Times — a placement mma4max never matches (G-2).
   8 rules get wrong bindings on one witness variant (G-4). As published
   (no guard) the figures are 6,864 rules (92.21 %), 519 rules with false
   mutation matches and 277 rules with wrong bindings: **the guard is
   required**, and it removes every one of those without costing a positive.
3. **What rides next to the matcher.** 7,427 rules carry an outer `/;`
   condition; 384 carry a condition inside an RHS `With` (373) / `Module` (11)
   that withdraws the rule after it matched; 47 rule conditions (+2 RHSs) call
   `MatchQ` with a condition *inside* the pattern. `IntegrationUtilityFunctions.m`
   defines 328 functions (757 definitions); 90 dispatch among several pattern
   definitions, 53 have conditioned definitions, 30 call `MatchQ`, 2 `Switch`,
   1 a `ReplaceAll` rule. Those uses need constructs the LHSs never use —
   typed blanks (`_Integer`, `_List`, `_Plus`, `_Rational`, `_Complex`,
   `_Power`, `_Times`), sequence blanks, `x_:v`, anonymous blanks, conditions
   inside patterns — all with mma4max code paths but **untested** (G-8), plus
   `Complex` patterns in 7 functions (G-3).

Separately from the matcher, **Maxima's simplifier changes 1,817 of the
72,347 witness variants it is given, and 312 rules lose a match** their
Mathematica-form witness had (G-5, the expression-model gap, now counted
per rule).

## Gap list (input to the design brainstorm)

| id | gap | size | evidence | locus |
|---|---|---|---|---|
| G-1 | Blank binds the identity of an empty Flat remainder (published mma4max) | 519 rules with false mutation matches, 277 with wrong bindings, 580 rules failing a positive | `02-roundtrip.out` MODE pub; removed entirely by the guard (MODE guard) | `mblank1` (01-FINDINGS root cause 1) — fixed by the guard |
| G-2 | pattern-variable head `F_[..]` or compound head `h[..][..]` as a direct argument of Plus/Times never matches | 41 rules (31 `F_`, 20 compound, 10 both): 3.1.5 L63, 3.3 L62, 4.7.5 ×10, 8.1 L55/L72, 8.2 L56, 8.4 L32, 8.5 L32, 9.1 ×20, 9.3 L23/29/35/41 (full list: `FAILRULES guard`) | `MISS by head placement guard`: F_ under Plus/Times 31/31, compound under Plus/Times 20/20; of the 41 rules with a MISS, 41 carry such a head directly under Plus/Times and 0 carry none; controls H2/H4/H8 NIL vs H1/H3/H5/H6/H7 T (`02-controls.out`) | `m2` Flat+Orderless clause (`newmatch.lisp:757-759`) hands every compound element to `matchfol` with the element's own head as `op`; `matchfol` compares `op` with `eq` (`:1567`, `:1597`) and never pattern-matches it (call trace below) |
| G-3 | `Complex[re, im]` patterns | 9 LHSs (4.1.10 L6/L8/L9/L30/L34, 4.3.10 L4/L6, 4.5.10 L4/L6), 2 RHS `MatchQ` (4.3.10 L28, 4.5.10 L16), 7 utility functions (FixSimplify, NormalizeHyperbolic, ReduceInertTrig, SimpFixFactor; RectifyCotangent, RectifyTangent, SimpHelp) | census `GAP`/`UGAP`/`CGAP`; spike-01 SMOKE #132 | `newmatch.lisp:436` rebuilds the atom as `(Complex re im)` with an unescaped symbol; and Maxima has no complex-number atom (`2*%i` is a product: the 4.1.10 witnesses come back `Times[2, I, ..]`, rewrite kind `-Complex`) |
| G-4 | wrong bindings in the `(a_.+b_.*F[u_])^p_.*(e_*x_)^m_.` family (guard) | 8 rules: 4.1.12 L82, 4.3.11 L24, 4.5.11 L18, 6.1.12 L74, 6.3.11 L20 (collapsed only-1 witness, both legs); 6.5.11 L8/L10/L18 (Maxima-leg witness) | `UNSOUNDRULES guard`; controls U1/U2: `e=Sin[u] u=e`, `u=Sech[u]^p b=b^p`, identical with every symbol renamed (U1r/U2r) — not a naming artifact; published mma4max binds `u=Sequence[]` on the same cases | not localized; the guard converts an empty-Sequence binding into a different wrong one — the `mblank1` / Optional-Alternatives interaction |
| G-5 | expression model: Maxima's simplified form no longer matches | 312 rules, 1,142 witness variants (guard) | `MODEL-LOST guard` (variants/rules): `+Abs` 597/132, same heads other structure 311/165, `-Complex` 100/9, `-Power` 78/21, `+Abs -Power` 13/3, `+Plus` 12/4, `+Times` 10/5, `-Plus` 8/2, `+Abs+Times` 7/4, `+Times -Power` 6/3 | converter side, not matcher (01-FINDINGS §model) |
| G-6 | undecided semantics: an Optional-reduced Plus/Times item taking a run of the parent's elements (`(g_.+h_.*x_)` with g = 0 matching `h·x` inside a product) | collapsed witnesses of 1,919 rules match only under this reading (tree leg 2,477 variants; guard) | `SUMMARY guard collapsed …`: FALSE/WIDE-OK 2,477, OVERMATCH 0, UNSOUND 6 | mma4max implements the wide reading consistently; no oracle decides what Mathematica does — a design decision |
| G-7 | Optionals rewritten one per argument list (`remopts`, spike control C-02) | **0 rules**: no LHS, condition or utility pattern has two Optionals directly under one head | census (ii) Optionals table | not needed by the rule set |
| G-8 | constructs used only by conditions / utility functions, never exercised | typed blanks 7 kinds, sequence blanks (EqQ… catch-alls, RationalQ…), `x_:v` (5 functions), anonymous `_` (8), Condition inside a pattern (47 rule conditions, 28 functions — needs an evaluator hook), `Switch` / `ReplaceAll` consumers | census utility tables (status CODE) | untested code paths; mma4max evaluates conditions with its own `meval` |
| G-9 | LHS evaluation before storage | 1,814 rules' evaluated LHS differs from the parsed one (Sqrt → Power 941, numeric folding 1,058, Power-of-Power 1,031, integer powers distributed 580); 38 rules carry evaluation the reader does not emulate (8.8 PolyLog numeric args ×11, trig args with `Pi` ×13, `Complex` ×9, …) | census `LHS evaluation effects` | the generator must emit the *evaluated* pattern; the emulation is unverified (no Mathematica here) |

`matchfol`'s exponential search (01-FINDINGS root cause 3) is not a gap at
witness sizes: guard-mode single matches p50 0.021 ms, p90 0.071, p99 0.41,
max 44.5 ms (4.5.1.2 L8), none over 50 ms; published p99 3.4 ms, max 150 ms.
Preparing all 7,444 patterns (fixopts + bindfix) took 2.04 s in total
(p50 0.135 ms, p99 2.6 ms, max 22 ms), with 0 failures.

## A. Static census (`02-construct-census.{py,out}`)

**Reader.** `02-mma-reader.py` parses Mathematica InputForm to FullForm
(Mathematica precedences; newline ends a complete expression at bracket
depth 0, as `Get` reads a file). Completeness: 199 files; 7,432 inventory
runs (asserted per file against `01-inventory.py`) + 12 single-line
`If[TrueQ[$LoadShowSteps], ..]` rules outside the inventory convention; 0
parse failures. Whole-file parse cross-check: 7,412 top-level Int
definitions + 44 in ShowSteps `If` branches = 7,456 = 7,432 runs + 12 × 2
branches; Mathematica with `$LoadShowSteps=True` defines 7,434 Int
DownValues. Found on the way: one run (9.2.m L111) truncated by the
inventory convention at a comment-only line inside its condition (extended
here); 5 helper definitions glued to rule runs (`IntLinearQ` 1.1.1.2 L44,
`IntBinomialQ` ×3, `IntQuadraticQ` 1.2.1.2 L151) plus `$UseGamma` (2.1 L4);
a stray top-level `MemberQ[{Sinh,Cosh,Sech,Csch},f]` at
IntegrationUtilityFunctions.m:6114.

**LHS evaluation.** `Int` has no Hold attribute when the rule files are read
(`Rubi.m:114`; the `HoldAll` at IntegrationUtilityFunctions.m:7743 is
Block-local to `FixIntRules`), so Mathematica evaluates every LHS argument
before storing the rule; the census walks the evaluated LHS (reader's
emulation, labelled as such — G-9).

**Constructs** (#rules; status): `x_Symbol` 7,443 TESTED; named Blank under
Times 7,278 / under Plus 6,887 / elsewhere 6,847 TESTED; Optional under Times
7,227, under Plus 4,835, as Power exponent 4,100 TESTED; repeated `x` 7,022,
other repeated names 2,152 TESTED; pattern-variable Power base 2,203 TESTED;
literal integer exponents 3,773 TESTED; literal rational exponents 1,133
CODE; `E` 208, `Pi` 13, reals 3 CODE; `F_[..]` heads 77 CODE; compound heads
21 CODE; `Complex` 9 UNSUPPORTED; one rule (9.3 L596) has an untyped `x_`
second argument. Optional parents: Times 23,152, Plus 10,089, Power exponent
7,516 occurrences, always one Optional per argument list; none as a Power
base, under another head, or with an explicit default. Largest Plus/Times
argument count in an LHS pattern: 5 (30 rules), 4 (265), 3 (3,646), 2
(3,427). Heads in LHS patterns (the converter's table): 57, from Times 7,368
to Factorial 1 (`heads appearing in LHS patterns`).

## B. Round trip (`02-roundtrip.{py,lisp,mac,run,out}`)

**Oracle.** There is no Mathematica here. `verify(pattern, target,
bindings)` checks a given binding against Mathematica's pattern semantics as
documented (a Blank takes exactly one element, one or more under Flat
Plus/Times binding their Plus/Times; an Optional may take none and bind
Default 0/1; `b^m_.` matches a non-Power through `b` with m = 1; non-Flat
heads match in order; repeated names bind one value). It is a checker, not a
search: the matcher under test searches. Self-test on 13 hand-derived spike
cases (incl. the N-07/N-14/N-15 false matches, G6-01's regrouping) and on
every all-present witness (7,444/7,444 verify with their own bindings).

**Cases.** Witnesses built from each evaluated LHS (variables → fresh symbols
of the same name, `x_` → `x`, `fz_` in `Complex` → 2; Optionals all present,
all omitted, each alone omitted, each alone present): 79,910 variants, of
which 72,456 verify with their own bindings and 7,454 *collapse* (an omitted
default merges factors into a shape the LHS does not cover in Mathematica —
e.g. both linear factors of 1.1.1.2 L6 defaulted give `x^-2`); collapsed
witnesses are judged like mutations. 37,747 mutations (x → z, drop a
non-optional Plus/Times argument, bump a literal, break a repeated name).
Maxima leg: every positive written as a Maxima expression, simplified,
converted back (head table measured at run time from Maxima's own operators;
`li[n]`/`psi[n]` subscripts handled; unmapped heads and Rubi's inert
lowercase trig travel as undefined `mm_` functions) — posed for all but 109
variants (compound heads). A match whose bindings fail `verify` is split:
WIDE-OK (G-6 reading), OVERMATCH (the LHS instantiated with the bindings
evaluates to the target), UNSOUND (it does not).

**Results** (`02-roundtrip.out`):

| | published | guard |
|---|---|---|
| positives OK-EXACT / OK-ALT | 66,800 / 3,105 | 68,815 / 3,348 |
| positives WRONG (UNSOUND / OVERMATCH) | 1,368 / 773 | 0 |
| positives MISS | 410 (98 rules; 57 without a head of G-2) | 293 (41 rules, all G-2) |
| rules with every positive OK | 6,864 (92.21 %) | 7,403 (99.45 %) |
| mutations: FALSE (UNSOUND / OVERMATCH) | 399 / 306 in 519 rules | 0 (62 LEGIT) |
| collapsed, tree leg: WIDE-OK / OVERMATCH / UNSOUND | 2,374 / 14 / 117 | 2,477 / 0 / 6 |
| Maxima leg: OK / MODEL-LOST / MISS both legs / WRONG | 68,881 / 1,081 / 216 / 2,169 | 70,884 / 1,142 / 185 / 136 (132 WIDE-OK, 3 UNSOUND, 1 OVERMATCH) |

Published mma4max is also order-sensitive: 7 of its MODEL-LOST variants
(`unchanged tree`) come back from Maxima equal to the witness up to argument
order, yet match only in the witness's order; the guard run has none.

`OK-ALT` (3,348 variants under the guard) are valid bindings other than the
witness's own — symmetric LHSs such as `(a_.+b_.*x_)^m_.*(c_.+d_.*x_)^n_.`;
which binding Mathematica picks first is not decided by this probe.

Maxima rewrite kinds over the 1,817 changed variants: same heads, other
structure 793 (e.g. `(d*x)^(-1/3)` distributed), `+Abs` 597
(`(b*x^2)^p → b^p*abs(x)^(2p)`), `-Power` 213 (`log(x^n) → n*log(x)`), `-Complex`
100, `+Times -Power` 43, `+Times` 31, `+Abs -Power` 13, `+Plus` 12, `-Plus` 8
(`sec(%pi+x) → -sec(x)`), `+Abs+Times` 7.

**Call trace behind G-2** (session trace of the control H2
`Int[u_*F_[x_], x_Symbol]` vs `u*F[x]`, beside the H3 control
`Int[u_*Sin[x_], ..]`): both reach `matchfol(Times …)`, bind `u`, then call
`m2` on the remaining element with governing head Times; `m2` calls
`matchfol` with `op` = the element's head — `Sin` for H3 (the singleton
branch strips `Sin` by `eq` and matches `x_` against `x`: T) and the cons
`(Pattern F (Blank))` for H2 (the `eq` test against `F` fails, `x_` is tried
against the whole `F[x]`: NIL). The trace was a session diagnostic; the
committed evidence is the H1–H8 controls and the placement table.

## Not covered (by design of A + B)

- Conditions and numeric special cases: witnesses are generic symbols, so
  `/;` clauses are never evaluated — only a corpus replay through a
  dispatcher exercises them.
- Which binding Mathematica returns first when several pass (OK-ALT).
- Rule order (first match wins) and dispatch.
- The G-6 reading, and the LHS evaluation emulation (G-9): both rest on the
  documented semantics, not on a Mathematica run.
- Corpus integrands: the Maxima-leg counts are over witnesses, not over the
  corpus (how many corpus integrands carry a MODEL-LOST rewrite is still not
  measured).

## Committed statements this probe updates

- `01-FINDINGS.md` §root cause 2: "How many Rubi LHSs put two Optionals
  directly under one head is not measured" — measured: none (G-7).
- The handoff's "226 functions of IntegrationUtilityFunctions.m": the file
  defines 328 functions; 227 distinct names carry a `::usage` message here,
  against 226 `Name::usage` entries in `docs/rubi-architecture.md` §4
  (`02-utility-inventory.py`) — the one-name difference is not reconciled.
