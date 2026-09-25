# Class 7 (inverse hyperbolic functions) port — 6,552 entries

Status: ready
Type: task (port, runbook-driven)
Filed: 2026-08-30 (milestone-3 close; the M2 TODO's class-7 item, now
against the instantiated runbook)

## Scope

Port the "7 Inverse hyperbolic functions" section (section name
VERIFIED against `reference/maxima-syntax-test-suite/7 Inverse
hyperbolic functions/` — 20 `.mac` files under subdirs 7.1 Inverse
sine … 7.6 Inverse cosecant) and its rule files
(`reference/rubi/Rubi/IntegrationRules/7 Inverse hyperbolic
functions/`) per `docs/class-porting.md` Steps 1–10. The
milestone-3 instantiation (`docs/corpus-class3-baseline-uplift.md`)
is the template; its standing constraints bind (byte-identity gate
for every accepted class, 30 s per-entry cap, 100 s timeout
re-check, A/B vs the `integrate` baseline, acceptance record per the
class-2/class-3 template, TLS probe on the core rebuild).

## Recon numbers (measured 2026-08-30 — PRE-CENSUS; the runbook
Step-1 census probe is the first act of the port and supersedes
these)

- **Corpus: 6,552 entries** — counted over the section's 20 `.mac`
  files (lines starting with `[`); matches the M2 TODO's figure.
- Rule files: **25 `.m` files in the tree, 21 `Rubi.m` LoadRules
  entries** — 4 `.m` files are NOT in the LoadRules list; the
  Step-1 census (which counts only loaded files, the class-1/3
  precedent) settles membership, and the record must state which
  files are excluded and why (absent from Rubi.m, as class 3's
  corpus-less 3.1.1/3.1.3 were absent from the suite — the inverse
  situation).
- Rule count: **1,075 `Int[... ] :=` lines** across the 25 `.m`
  files (recon count over ALL files in the tree, loaded or not; the
  Step-1 census probe is the authoritative loaded count).

## Known interactions

- The inverse-hyperbolic heads (`asinh`/`acosh`/`atanh`) are the
  class-3 headvar allow-list spellings with the `%mr_` shims
  existing for class 1–2 byte-identity; `asech`/`acsch`/`acoth`-
  style spellings, if present in expected texts, need the
  Step-1 answer-head census to decide table/rewrite disposition
  (boundness probe first — the class-3 ArcCot/ArcCoth
  unbound-noun adjudication is the precedent).
- Queue position: fourth (8 → 5 → 6 → 7 → 4).

## Acceptance

Per the runbook: merged records complete (6,552/6,552), A/B
triaged with nothing unexplained, re-check read, acceptance record
committed, the byte-identity gates for classes 1–3 (and 8/5/6 if
accepted earlier) green, Layer A green.

## Comments

### 2026-09-25 — Step 1 (census) COMPLETE; status needs-triage -> ready

Build `branch_5_50_base_84_g4204fb669` (2026-08-31 13:27:47), SBCL 2.6.7.
Branch `class-ports` (worktree `mr-ports`), on top of the class-8
(`be6b1af..4f8144a`) and class-5 (`19fe549..995bbc1`) ports, base `cd0a421`.

**Probes committed (re-runnable):**

- `probes/translation/11-class7-syntax-census.{run,out}` — Step 1(a): the 01
  census over the loaded "7 " files; the class-5 closure probe
  `probes/translation/10-class5-table-closure.py "7 "` (the table closure,
  counted the generator's way, and the transitive closure through
  `IntegrationUtilityFunctions.m`); and the new
  `probes/translation/11-class7-excluded-files.py`, which lists the tree's
  `.m` files Rubi.m does not load and what they are.
- `probes/corpus/21-class7-answer-heads.{run,out}` — Step 1(b) (the class-6
  script with the section as its argument).
- `probes/answer-side/06-class7-answer-side-identities.{py,run,out}` — the
  six native inverse-hyperbolic heads through the harness's own zero chain,
  Mathematica's conventions, the simplifier on negated/reciprocal
  arguments, the singular points, `op()` of a call, and the shim bodies.

**Counts.** 25 `.m` files in the tree, **21 loaded** (7.1 Inverse
hyperbolic sine 6, 7.2 Inverse hyperbolic cosine 6, 7.3 Inverse hyperbolic
tangent 7, 7.5 Inverse hyperbolic secant 2; Rubi has no separate
arccoth/arccsch files: each file carries both members of its pair). The 01
census counts **710** rules; 7.3.7 carries TWO single-line
`If[TrueQ[$LoadShowSteps], <ShowStep rule>, <plain rule>]` wrappers (L28,
L29 — the ArcTanh/ArcCoth twins of class 5's 5.3.7 r27/r28) which the
census's `rule_runs` glues onto the rule before them; the generator
unwraps them to their plain branch, so the port total is **712** (7.3.7
72, not 70) — class 5's adjustment exactly. Every rule has a `/;`
condition. AUTO 386 / MANUAL 324 by the census's own tiers. Corpus
**6,552** entries over 20 `.mac` files (the recon's figure; 7.4 arccoth and
7.6 arccsch have corpus files but no rule files of their own). No head
variables. No bare-`u_` record, so class 7 adds nothing to the tail.

**The four EXCLUDED files** (in the tree, absent from Rubi.m's LoadRules —
probe 11 part 3). All four are in `7.3 Inverse hyperbolic tangent/` and
are the section's OLD numbering, superseded by the loaded renumbered files:

| excluded file | `Int[` | what it is |
|---|---|---|
| `7.3.1 u (a+b arctanh(c x^n))^p.m` | 193 | the old omnibus, split into the loaded 7.3.1-7.3.4: 179 of its 193 rule runs occur verbatim in loaded 7.3.2 (6), 7.3.3 (12), 7.3.4 (161); 14 occur in no loaded file (rules Rubi has since rewritten — the new 7.3.1 has 10) |
| `7.3.2 u (a+b arctanh(c+d x))^p.m` | 20 | loaded 7.3.5, identical but for the `(* 7.3.x title *)` header comment |
| `7.3.3 Exponentials of inverse hyperbolic tangent.m` | 82 | loaded 7.3.6, same |
| `7.3.4 Miscellaneous inverse hyperbolic tangent.m` | 70 | loaded 7.3.7, same |

They are excluded because Rubi excludes them (the class-1/3 precedent: the
census counts loaded files only); porting them would load duplicates of
rules already in the table at a different priority.

**Token closure — 79 tokens; 75 already have rows; 2 are
emitter-dispatched (`PolyQ` 10 rules, `IGeQ` 1 — 7.3.4 r136); 2 UNLISTED,
both adjudicated:**

*A. Native heads — `ArcSech` 38 rules -> `asech`, `ArcCsch` 36 -> `acsch`.
Step 2 rows.* Both differentiate through the zero chain (probe 06 A5/A6),
float-evaluate on their real domain (E5/E6; `asech(1.7)` is complex, E9),
and follow Mathematica's conventions `ArcSech[z] = ArcCosh[1/z]`,
`ArcCsch[z] = ArcSinh[1/z]` (C1/C2 through the chain, C4-C6 as floats).
`ArcCoth[z] = ArcTanh[1/z]` holds for the class-3 `acoth` row too (C3,
C7/C8). mr-tree already maps both heads (`+functions+`), and
`%mr_inverseFunctionQ` / `%mr_inverseHead` (class 5) already list them.

*B. Not a token, but the class's one real table decision: ArcTanh /
ArcSinh / ArcCosh.* The table renames them to the `%mr_atanh` /
`%mr_asinh` / `%mr_acosh` shims (class 1, "this binary lacks the name"),
which are `:=` functions evaluating to their log forms on the spot
(`maxima_rubi_utils.mac` L3125-3132). Class 7 cannot use them. Its rules
recurse on their own heads (e.g. `Int[(a+b ArcSinh[c x])^n, x]` ->
`Int[x (a+b ArcSinh[c x])^(n-1)/Sqrt[1+c^2 x^2], x]`, which a 7.1.2 rule
matches on the pattern's `asinh`), 452/299/404 uses of the three heads;
the shim body is a quotient / a log (probe 06 K1/K2), so the recursive
integrand would carry no head any class-7 pattern names. And 7.3.7's
ShowSteps pair compares `EqQ[Head[tmp], ArcTanh]` — `op()` of the call is
`atanh` (H1/H7), never `%mr_atanh`. The natives are bound, differentiate
through the chain (A1-A4), float-evaluate (E1-E4, E7/E8 complex off the
real domain), `logarc` is false by default, and `ratsimp` / `radcan` leave
them alone (S11-S13). **Decision: a per-class override row** —
class 7 emits the natives; every other class keeps the shims (their
accepted records' byte-identity). The earlier classes' own recursive uses
(3.1.3 r14's `Int[ArcSinh[..]/x]`, 5.3.2 r3's `Int[..ArcTanh[..]..]`) are
ticket 18.

**Transitive closure (the CENSUS TRAP check).** 195 utilities reachable
(41 rule-side, 154 transitive-only): table 71, ported 68, ABSENT 56. **No
rule-side utility is ABSENT** (class 5 ported the three it needed,
`HalfIntegerQ`, `InverseFunctionOfLinear`, `SubstForInverseFunction`, and
class 7's 7.3.7 ShowSteps pair reuses them with `Head`). The 56 ABSENTs are
class 5's list less those three: the inlined `InverseTrigQ` /
`InverseHyperbolicQ`, `FunctionOfExponentialTest(Aux)`, the algebra
substrate under `Simp`/`Subst`/`ExpandIntegrand`/`SmartApart`/`Rt`/`FreeQ`
(including `SimplifyAntiderivative`'s `RectifyTangent`/`Cotangent`), and:

**FunctionOfQ's hyperbolic arms** (`FunctionOf{Sinh,Cosh,Tanh}Q`,
`PureFunctionOf{Sinh,Cosh,Tanh,Coth}Q`, `OddHyperbolicPowerQ`, `ReapList` —
ticket 05's "Carried" list). **Not reached**: class 7's six `FunctionOfQ`
calls (7.1.6 1, 7.2.6 1, 7.3.7 2, 7.5.2 2) are all
`FunctionOfQ[(c+d*x)^(m+1), u, x]`, a power `v`, which takes the general
`FunctionOfExpnQ` arm class 8 ported — the class-5 reading. So porting
them is out of scope for this class.

**Answer side (Step 7 input): no new `HEAD_REWRITES` row.** The discovery
pass finds 31 native heads (`sqrt(` 37,536, `atanh(` 8,769, `asinh(`
6,616, `acosh(` 5,854, `log(` 4,005, `polylog(` 3,416, `acoth(` 2,070,
`asech(` 1,228, `acsch(` 1,013, …) and 11 non-native ones, every one
already disposed of:

| head | uses | disposition |
|---|---|---|
| `Unintegrable(` 618, `CannotIntegrate(` 34 | 652 | corpus markers |
| `Chi(` 561, `Shi(` 545, `Ci(` 6, `Si(` 3 | 1,115 | class-3 rows |
| `GAMMA(` 178 (all 2-arg) | 178 | class-2 reading of the arity-dispatched row |
| `HypergeometricPFQ(` 38 | 38 | class-8 row |
| `FresnelS(` 36, `FresnelC(` 36 | 72 | class-8 rows |
| `AppellF1(` 47 | 47 | no native — the structural ceiling |

The six inverse-hyperbolic natives the answers are made of differentiate
through the zero chain and float-evaluate (probe 06 A1-A6, E1-E6), so "no
rewrite" is sound, `asech`/`acsch`/`acoth` included (the boundness probe
the ticket asked for: all three are BOUND, unlike class 3's
`arccot`/`arcoth`). Step 7 is therefore the no-op check and the rewrite
totals for section 7.

**Simplifier facts the matcher will see (probe 06 S1-S10):** Maxima
rewrites a syntactically negated argument of the odd ones — `asinh(-x) =
-asinh(x)`, `atanh(-x) = -atanh(x)`, `acoth(-x) = -acoth(x)`, `acsch(-x) =
-acsch(x)` — and leaves `acosh(-x)`, `asech(-x)` and every reciprocal
argument alone. **Singular points (N1/N2):** `atanh(1)` and `acoth(1)` are
Maxima ERRORS (`errcatch` gives `[]`), where Mathematica answers
ComplexInfinity; `acosh(1) = asech(1) = atanh(0) = 0` (N3).
