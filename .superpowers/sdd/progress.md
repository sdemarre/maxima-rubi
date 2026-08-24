# SDD progress ledger — milestone-1

Branch: milestone-1 (worktree .worktrees/milestone-1)
Plan: docs/superpowers/plans/2026-08-20-milestone-1-implementation.md
Merge base (master): 6754be9

## Completed tasks

Task 1: complete (commits 6754be9..ca98e3b, review clean — spec ✅, quality Approved)
Task 2: complete (commits c55cfba..f36d978, review clean after 1 fix — spec ✅, quality Approved)
  - Fixed during review: loader by-name fallback was inverted for this build
    (errcatch returns [RESULT] on success, [] on error — measured in
    probes/maxima/probe-errcatch-semantics.*). Now `if ok = []` (fire on error).
  - 9/9 + no file_search warning corroborated by report's verbatim output; batched
    path (load_pathname=false) untested — see Minor below.
Task 3: complete (commits 7781cee..c17c482, review clean after 1 fix — spec ✅, quality Approved)
  - Fixed during review: the "recursion re-dispatches" rubi() check was vacuous
    (integrate of the original and reduced integrand are equal on this build).
    Added direct firing assertions on the rec rule (fires on the product form,
    rejects x^2). Also made test_load_and_api save/restore mr_rule_table and
    removed the now-redundant D1 restore in test_runner.
  - Corrected the depth-cap premise: exp(x^2) is NOT a noun on this build
    (integrate returns an erf closed form); assertion accepts the integrate
    result or a noun.
Task 4: complete (commits 535dc07..8528996, review clean after 2 fixes — spec ✅, quality Approved)
  - Fixed during review (1): %mr_dispatch loop-level return bug — a return(value)
    inside a for loop is loop-level in this build, so dispatch ALWAYS returned
    false and rubi() was a silent pass-through to integrate. Fixed (track ans,
    bare return() to break the loop, return ans) + non-vacuous test_dispatch
    (unit + end-to-end rubi(x^7,x)=99 sentinel). CRITICAL runner defect, caught
    because the implementer measured it.
  - Fixed during review (2): generator's mandated "fail loudly on unlisted token"
    was unmet — unknown HEAD tokens passed through silently (dead KeyError).
    Fixed: emit_head fallback raises GenError naming file/rule/head for a head
    not in RENAME ∪ RESTRUCTURE ∪ {x,Pi,E,I}; atom pass-through preserved; dead
    m2m() deleted.
Task 5: complete (commits 8528996..2c65051, review clean after 1 fix — spec ✅, quality Approved)
  - Fixed during review: two systematic term-walker mistranslations (wrong-answer
    paths in class 1) — Bug B: %mr_term_xexp dropped bare-power monomial terms
    (x^2 after expand fell to else false) -> coeff/degree/polyDegQ wrong on monic
    leading terms, and %mr_degree leaked a boolean; Bug A: %mr_term_coeff dropped
    the bare-x term at n=1 -> linearQ(x+1,x)=false (Rubi: true). Fixed + 10 monic-
    term probes added. Also corrected a false "measured" claim in the report and a
    stale test name.
  - F1 (rule 5 (a+b*u)^m pattern dead — rule 4 shadows it): confirmed real,
    correctness-HARMLESS (both rules give the identical antiderivative; rule 4 or
    fall-through always yields the right answer in 1.1.1.x). Coverage/redundancy
    gap + Subst path untested end-to-end. Track for Task 6/9; re-measure on 5.50.
  - F3 (plan's /12,/9 antiderivatives were wrong): corrected to /8,/18 (verified).
Task 6: complete (commits 1a85498..0ac99b5, review Approved with 4 Important findings)
  - REVIEW OUTCOME: spec ✅, quality Approved. 4 Important findings:
    (1) PLAN-LEVEL / HUMAN DECISION — the load wall breaks the plan's core
      assumption (all 2710 in one process). (2) report mis-describes the C-tier
      handoff: 182 rules FIRE with noun-laden answers (repl has a pending C-tier
      noun, cond fully bound), not "decline" (only the 110 cond-pending rules
      decline) — wording fix pending. (3) static census re-parses Rubi SOURCE,
      never reads the committed .mac files (a corrupted generated file would
      pass) — harden pending. (4) %mr_polyDegPowerQ uses '<= n' (plan-pinned) but
      Rubi :533 needs EXACT degree (15 class-1 rules over-fire) — human chose
      "fix to exact degree", pending.
  - LOAD WALL RE-PROBED ON 5.50.0 (released, installed /home/serge/local/bin/maxima,
    source ~/src/external/maxima): cap UNCHANGED (1200 load / 1600 die; prefix 7
    files/294 rules load, file 8/361 FATAL). 5.50's matcher-speed gains do NOT
    raise the TLS cap. .out re-stamped 5.50.0.
  - HUMAN DECISION (2026-08-20): SDD execution PAUSED after Task 6. A SEPARATE
    session will investigate handling the load wall — Direction 1 "fix" the
    matching tools for SBCL (reduce per-rule special-var cost / raise the cap),
    or Direction 2 the "large if-then-else" strategy (Rubi 5: compile the rules
    into 42 Int*nnn if-then-else functions, no pattern matching -> no defmatch
    special vars -> no TLS cap). Handover doc: /tmp/opencode/handoff-2026-08-20-
    maxima-rubi-load-wall.md. Tasks 7-10 are BLOCKED on that decision (Direction 2
    would re-architect the runner + generator output).
  - Full-class generation: 67 files, 2710 rules, every per-file count equal to
    the T1 inventory (static cross-check probes/census/01-generation-vs-
    inventory, no Maxima). Emitter dispatch E1-E5/E10/E11 closed the shapes
    the census tier table could not represent 1:1 (rule-list ReplaceAll ->
    equation-list subst, the 3-arg list form being a silent no-op; ShowStep
    -> 4th arg; Sum -> 4-arg mr_sum; MatchQ RAW args in the fresh-marker
    scope; digit/paren join — 2(x+1) and (x+1)2 are parse errors).
  - Load wall measured (T5 §5): a hard process-level defmatch BUDGET, not a
    timing problem — 1200 plain patterns load / 1600 FATAL; class-1 load
    list files 1-7 (294 rules) load / file 8 (361) dies with SBCL's fatal
    "Thread local storage exhausted" (errcatch cannot catch it); unload()
    releases the budget. The loader does NOT call mr_load_class1_all()
    (it exists for a build with the headroom); eager core = utils + 1.1.1.1.
    Probe: probes/load_wall/probe-load-wall.run (6 parts, self-flagging).
  - Fixed both rule-run parsers (01-inventory + 01-class1-syntax-census): a
    comment-only line between := and the rhs silently dropped 5 rule bodies
    (4 class-1 + 1 class-9); dangling-:= exception; evidence regenerated
    (class-1 cond 2705->2709, rule totals unchanged 2710/67).
  - %mr_load_sibling read load_pathname at CALL time (top level = the batch
    file, not the library — measured probes/maxima/probe-load-pathname.out)
    -> spurious file_search1 miss per sibling + fallback reliance. Now
    %mr_lib_dir captured at definition time; suite run has zero file_search1.
  - Brief deviations, all measurement-forced and recorded in the report:
    D1 full load list wrapped in the uncalled mr_load_class1_all(); D2 table
    assembly flatten([...]) (list concat is a hard error in this build); D3
    the ~1-minute decision gate moot (budget, not time); D4 test_census is
    the loadable subset (1.1.1.2 count 40 = T1 number, witness, restore)
    with the global 2710 check in the static census probe.
  - Suite 71/0; per-file parse+witness 67/67 (one process per file).

## Work item: class-1 parse fixes (post-Task 6, pre-Task 9; 2026-08-22)

Ticket: .scratch/class1-parse-fixes/issues/01-generator-parse-defects.md.
The parse sweep (probe-parse-sweep, 5.50.0) found 6 of 67 files
parse-broken; the sweep stops at the first error per file, so root-cause
work found FIVE generator defects, each measured with a repro:
  RC1 `==` untranslated — this build's parser rejects `==` in every
    position (even `1 == 1`); `=` now HAS the syntactic-equality
    semantics (is() -> true/false, never unknown — manual entry + value
    probes). 4 rules (1.1.3.1 r11 x2, 1.1.3.7 r5, r38). Fix: walk emits
    `=` for `==`. (`#=` absent from class 1; this build's negation is `#`.)
  RC2 `;` in With/Module bodies — Maxima block statements separate with
    `,`, not `;` (measured: "Missing )" at the `;` — the 1.1.3.2 r35
    error). Exactly 8 rules (a first census pass counted the `/;` of
    inner conditionals and over-reported 185): 1.1.3.1 r13/14/21/22,
    1.1.3.2 r35-38 — the same 8 bodies as RC5.
  RC3 raw comparison chains `3 <= d <= 4` — Maxima has no chaining
    (measured: LOGICAL/ALGEBRAIC error). 2 rules (1.2.1.1 r16 cond, r17
    rhs). Expand to `is(a op b) and is(b op c)` per the existing 3-arg
    CMP_OPS convention (Rubi's own LtQ chain def is conjunctive).
  RC4 whitespace juxtaposition (`2 n`, `f Sqrt[v]`, `(x)^m (y)^q`,
    `n (2*p+1)`) — Mathematica implicit multiply; Maxima needs `*`.
    ~15 rules (1.2.3.4, 1.2.2.4, 1.4.3 r16 lhs pattern). No-space
    juxtapositions: NONE in class 1 (earlier census hits were cond+rhs
    concatenation artifacts).
  RC5 `u = Int[...]` body statements (8 rules: 1.1.3.1 r13/14/21/22,
    1.1.3.2 r35-38) — Maxima block `=` does not assign (measured: local
    left unbound, body computes on the global) — semantic, invisible to
    the parse sweep. Fix: top-level body `v = e` -> `v : e`.
Acceptance: parse sweep 0 fails; load curve clean 67-file run (2,710
measured); suite 71/0; regeneration diff touches only the five patterns.
NOTE: the Task 6 "per-file parse+witness 67/67" above is the known
probe-load-wall part-2 false positive, superseded by probe-parse-sweep.

RESOLVED 2026-08-22 (same session, ticket resolved): all five fixed in
generate_class1.py — RC1 walk emits `=` for `==`; RC2/RC5 `_maxima_stmts`
(top-level `;`->`,`, body `v = e` -> `v : e`) in the With/Module handler;
RC3 `_expand_chains` (raw `a op b op c` -> `is(a op b) and is(b op c)`,
any bracket depth) at the end of translate_atom; RC4 `_gap_join` in
_join_tokens (whitespace gap between expression terminals -> `*`) plus the
F6 no-space branches `x(…` and `…)ident` now emit `*` instead of a space.
Regenerated: the diff touches ONLY the 7 expected files (1.1.3.1, 1.1.3.2,
1.1.3.7, 1.2.1.1, 1.2.2.4, 1.2.3.4, 1.4.3 — 28 rule lines); the other 60
files byte-identical. Gates green: parse sweep 67/67 clean; load curve
clean (2,710 rules, c = 9.35 vars/rule, no broken files); suite 71/0.
New measured finding driving the RC4 rule set (one batch run per form,
5.50.0): a spaced `ident (…)` in Maxima is a SILENT noun call (`x (y)`
reads `x(y)`) — F6's space insertion for that case was semantically wrong,
not merely conservative; `) ident`, `) digit`, `digit (…`, `ident digit`,
`digit ident`, `ident ident` are parse errors; the ONLY legal spaced
juxtaposition is `) (…` — hence `*` for every terminal-terminal gap
except `)`/`]`-`(`, with a word guard (and/or/…) on both sides of the gap.

## Work item: Task-6 review fixes (2026-08-23)

The three pending "Important findings" of the Task 6 review
(above, findings (2), (3), (4)). HUMAN DECISION (2026-08-23): fix all
three before resuming Task 7.

- (4) `%mr_polyDegPowerQ` `<= n` over-fire — FIXED (exact degree). Rubi
  IntegrationUtilityFunctions.m:532-533: `PolyQ[u_,x_^v_,n_] :=
  PolyQ[u,x^v] && EqQ[Expon[u,x^v],n] && NeQ[Coeff[u,x^v,n],0]` — EXACT
  degree. The `NeQ[Coeff]` clause is subsumed: d = n means some term has
  k/v = n, and its coefficient is structurally nonzero after expand (a
  zero coefficient would drop the term). Fix: `is(d <= n)` -> `is(d = n)`
  in maxima_rubi_utils.mac (the old "DEVIATION (brief-pinned)" comment
  now records the exact match). TDD: 2 new suite probes RED first
  (`polyDegPowerQ(x^2+1, x, 2, 2)` and `..., 5)` — degree 1 < n — must be
  false; under `<= n` they passed, so 71/2 red) -> green, suite 73/0.
  The 15   over-firing rules verified by grep of the committed .mac (1_2_2_7
  x10, 1_2_3_5 x2, 1_1_3_7 / 1_3_4 / 1_4_3 x1 each); none are in the
  eager core (utils + 1_1_1_1), so no suite rule behavior changed. The
  plan's `<= n` pin is corrected in place with the decision note.

- (3) static census never read the committed .mac — FIXED.
  probes/census/01-generation-vs-inventory.py gains the committed
  half: per file, the defmatch(_mr_pat_<key>_r<N> indices must be
  exactly 1..count (catches missing/empty files, dropped rules,
  duplicated or gapped indices); total committed = 2710. Negative
  tests before restore: deleting r2's defmatch in 1_4_3.mac ->
  "count mismatch 1_4_3: committed 59 != generator 60", rc=1; renaming
  r2's defmatch to r1 -> "index anomaly 1_4_3: [1, 1, 3, ...]", rc=1;
  restore -> VERDICT OK.

- (2) Task-6 report C-tier handoff wording — FIXED, with a deeper
  finding. The report's "the conds call the %mr_* nouns, so those
  rules decline" (and the same claim in the generator's provenance
  comment template) is wrong: the inline def is trailing boilerplate
  AFTER the rule's `/;` cond — the host rule's cond does not call the
  defined predicate (verified against the source; 1.1.3.2 r109's cond
  is FreeQ && EqQ && Not[IntegerQ]). Measured per-rule on the 5
  inline-def runs: only 1_1_3_3 r65 declines (pending %mr_integersQ +
  %mr_pseudoBinomialPairQ in cond); 1_1_3_2 r109 / 1_1_3_4 r84 fire
  with a noun-laden answer (%mr_fracPart, + %mr_intPart); 1_1_1_2 r40
  / 1_2_1_2 r137 have no pending names at all. Fix: report corrected
  at all three spots; generator template now states both outcomes
  (regenerated diff = 5 files, comment lines only); NEW probe
  probes/census/02-pending-noun-surface (committed method, the 110/182
  review split is unreproducible — no method documented, and the 7
  parse-fix files regenerated after the review): on the committed
  files, C-tier scope (34 unported C_TIER predicates) = 292 decline /
  21 fire-noun / 11 both / 2397 clean; full pending surface (63
  names) = 496 decline / 852 fire-noun / 1362 clean.

REVIEW (2026-08-23, c25cb85..ef13464): verdict READY, no Critical /
Important; all four ledger numbers and the "verified against the
source" claims independently reproduced. Four Minors, all applied:
(a) probe 02's "both" column double-counted in the printed total —
relabeled `decline(cond, incl. both)` + cond-only printed, .out
re-stamped; (b) `%mr_polyDegPowerQ(0, x, v, 0)` was true, Rubi false
(Expon[0,·] = -Infinity; the atom-0 term read as a degree-0 monomial)
— pre-existing (the `<=` code had it too), unreachable from the 15
call sites (n literal 2/3), but fixed with a red probe: `is(r = 0) =
true -> false` guard + zero-poly and captured-base probes, suite 76/0;
any future `PolyQ[u, x^v, n]` port must keep rejecting u = 0;
(c) probe 01 docstring now states content integrity is OUT of scope
(rides on parse sweep / witness / suite / regeneration diffs);
(d) captured-base exactness probe added (production call-site shape).

## Task 7 (7a): C-tier predicates — in progress

Resumed 2026-08-23 after the Task-6 review fixes. Cluster order per
plan (A foundations, B int-family, C sum/simpler, D binom/quad/trinom+
match+degree, E generalized*, F pairs/split/misc).

- Cluster A1 — numeric predicates — DONE (commit 23ef9a7).
  %mr_integersQ (Rubi :70), %mr_fractionQ (:87) new; %mr_rationalQ (:97)
  fixed two silent bugs: the committed "/"-only test missed negative
  rationals (MEASURED op(-1/2) = "-", num/denom see through) and
  answered false on the 49 list-form calls the generator emits
  (generate_class1.py:877-884 list-packing branch — silent dead rules).
  Ports accept scalar-or-list per the generator contract; the list gate
  is op(u) = "[" (MEASURED: the list op is the string "[" in 5.50.0).
  14 new probes; suite 96/0.
- Cluster A2 — structural predicates — DONE (commit 610d6ed).
  %mr_polynomialQ (STRICT Mathematica port — no cancellation; dedicated
  %mr_polystrictQ walker whose only difference from %mr_polyformQ is the
  quotient branch: x-free denominator + polynomial numerator at any
  depth. MEASURED: this build keeps (x^2+x)/(x+1) as a "/" node while
  rat() cancels it, and does NOT auto-combine x/2+1 — so %mr_polyQ
  over-accepts and %mr_polyformQ under-accepts that shape), %mr_atomQ
  (= atom), %mr_monomialQ (Rubi :1391 usage semantics a*x^n, n!=0, a!=0;
  bare x and x^k are monomials via the .m optional pattern args;
  documented deviation: lone x^a with symbolic a is true here, false in
  the .m MatchQ — unreachable at the PolyQ-guarded call sites),
  %mr_leafCount (head counts as a leaf: LeafCount[1+x] = 3).
  30 new probes; suite 125/0.
- MEASURED 5.50.0 traps reused here: op()/length() are hard errors on
  atoms (walk tests atom() first — the %mr_monomialQ "*" branch hit it
  on 5*x^3 before the fix); a non-atom is not a list (the "/" node of
  1/2 misread as a 2-element list in the first draft of
  %mr_integersQ — gated on op = "[").
- Cluster A3 — %mr_matchQ structural matcher — DONE (commit e2c3895).
  The custom matcher for the 17 class-1 MatchQ call sites (matchq is
  a NOUN in this build, measured 2026-08-20).
  SCOPE DEVIATION (justified): the task-7 brief's file list was
  utils + tests only, but the MatchQ cond-holding fix is impossible
  there — Maxima evaluates call arguments eagerly (subst(val, m,
  integerp(m)) -> false: integerp runs before the subst), this
  build's ev() does NOT strip quotes (ev('integerp(2)) stays quoted;
  is('expr) -> unknown, and `if unknown then` stays unevaluated), CL
  macros are bypassed (Maxima dispatches its own function table), and
  marker values cannot survive integerp. Fix: the generator emits the
  cond as lambda([%mr_mqb], <cond with each marker m rewritten to
  %mr_mk(m, %mr_mqb)>) — a named lookup decouples marker ordering;
  the closure env resolves outer rule captures (a, b, n, ...).
  Verified pre-change: generator output == committed rules
  byte-for-byte (diff -rq rc 0), so the regeneration is
  count-invariant — exactly 9 files / 17 matchQ lines differ, 0
  MISMATCH.
  Semantics: flat partition over the expression's factors with
  COMMUTATIVE matching — every permutation of the pattern factors
  (stored order first), because Maxima's canonical factor order
  disagrees with the pattern's once long _mr_ marker names are
  involved (MEASURED: x^m*u stores [u, x^m] — a symbolic-exponent
  power sorts AFTER a bare symbol — while x^3*y stores [x^3, y];
  the stored-order partition therefore missed x^3*y = x^m*u).
  Non-empty groups before the empty (Optional) one — the Mathematica
  preference; gives the Rubi-faithful a=c, b=d, v=y binding at the
  1.3.4 site (empty-first bound a=0, b=1, v=c+d*y). Empty group =
  factor ABSENT: marker -> group identity, power with marker exponent
  -> exponent := 1 with the base SKIPPED (a literal power cannot be
  absent) — a shared "match the identity value" path wrongly demanded
  base <-> 1 and killed the x^2+x^3 = x^m*u match.
  KNOWN LIMITATION (documented in the code): the cond is not threaded
  through the partition backtracking — the first successful binding
  decides. No class-1 site exercises this: at the integerp(m) guard
  sites every structural binding of a polyQ-polynomial gives an
  integer m (exponents of x in a polynomial are integers; the
  powerless/absent routes bind m := 1).
  MEASURED 5.50.0 traps added (all 2026-08-23): string = / # NEVER
  evaluate standalone (stay equations; evaluate only inside if/and/or/
  is()) — every string comparison is an is(... = ...) in a boolean
  context; length(string) is a hard Lisp error (the marker-name
  length is an errcatch'd char scan + member() memo, one swallowed
  error line per distinct symbol); break does not take effect inside
  a comma-sequence while body (the suite hang); member(s, list)
  returns a boolean; substring(s,a,b) is END-EXCLUSIVE (start > length
  errors, start <= length clamps); `if <pending relation>` takes the
  ELSE branch while `if unknown` stays unevaluated (the cond = true
  guard in %mr_matchQ relies on the former: true = true -> true,
  lambda = true -> pending -> else).
  24 new probes; suite 149/0.
- Cluster B — int-family + binomial — DONE (commit 7d08ae3).
  %mr_intLinearQ (Rubi 1.1.1.2:44), %mr_intQuadraticQ (1.2.1.2:151),
  %mr_intBinomialQ 7/8/10-arg (1.1.3.2:118 / 1.1.3.3:73 / 1.1.3.4:89),
  %mr_binomialQ 2/3-arg + %mr_binomial_parts (BinomialQ :549,
  BinomialParts :851) — line-ported integrability guards. The class-1
  arity census (2026-08-23) shows binomialQ 2/3 (40/1) and intBinomialQ
  7/8/10 (21/10/44) as the only multi-arity names: new
  maxima_rubi_dispatch.lisp defmfun dispatchers re-dispatch onto the
  fixed-arity := bodies (named <name><arity>); maxima_rubi.mac loads
  the .lisp via %mr_load_sibling with a witness that CALLS the
  dispatched names (missed load leaves them nouns). The draft integersQ
  dispatcher dropped (census: 1-arg only).
  MEASURED 5.50.0 traps added (all 2026-08-23): op() hard-errors on
  ATOMS (symbols included — atom-gate before every op()); op() returns
  the SYMBOL 'sqrt for the sqrt head while special heads (^,+,*,/,-,[)
  stay strings (the first draft's string compare never matched);
  x^(1/2) collapses to a sqrt node (Mathematica stores it as x^(1/2))
  while x^(3/2) stays a power; 1/x stores as a "/" node, not x^(-1) —
  the power branch accepts the num = 1 reciprocal shape [0,1,-k]
  (documented deviation: c/x is one "/" node here, unreachable at the
  call sites); 3/0 hard-errors where Mathematica's Infinity answers
  false — the IntBinomialQ7 (m+1)/n disjunct is guarded on n # 0.
  41 new probes (13 binomialQ / 5 intLinearQ / 6 intQuadraticQ /
  6 intBinomialQ7 / 4 intBinomialQ8 / 6 intBinomialQ10 + the witness);
  suite 190/0.
  NOTE for the final census re-run: probes/census/02's defined_names()
  reads only the .mac files — the .lisp defmfun names stay "pending"
  in its output; extend it to parse defmfun from
  maxima_rubi_dispatch.lisp before re-stamping (else binomialQ /
  intBinomialQ / intLinearQ / intQuadraticQ still count as pending).
- Cluster C — sum/simpler — DONE (commit 0548a48).
  %mr_sumQ (:176), %mr_sumSimplerQ (:774) + %mr_sumSimplerAuxQ
  (:784, the three .m definitions: split-v AND over v's terms /
  split-u OR over u's terms / base: v # 0, NNF equality, NF ratio
  < -1/2 with the -1/2 tie broken by NF[u] < 0), %mr_simplerQ
  (:677), %mr_simplerSqrtQ (:732), %mr_niceSqrtQ (:647),
  %mr_fractionalPowerFactorQ (:658 — the NiceSqrtQ dependency,
  pulled forward from cluster F), plus %mr_numericFactor /
  %mr_nonnumericFactors (:1096/:1125) + %mr_rest_sum helper the
  SumSimplerAuxQ splits need, and the internal shims %mr_numberQ /
  %mr_complexNumberQ / %mr_orderedQ (NumberQ/ComplexNumberQ/
  OrderedQ — no Maxima builtins: complexp is a NOUN in 5.50.0).
  MEASURED 5.50.0 traps added (all 2026-08-23): is() returns the
  SYMBOL unknown for an undecidable relation and `if unknown` stays
  unevaluated, while a bare `(a op b) = true` is NOT evaluated (stays
  an equation) — conditions use the `is(a op b) = true` coercion, and
  the VALUE position of a decidable comparison returns the bare
  is() boolean (is(X) = true as a VALUE leaks the equation
  false = true on a false answer — caught by the simplerSqrtQ 2 3
  probe, which also pinned that the .m PosQ[u] && PosQ[v] branch is
  the BARE LeafCount comparison: a tie answers false, the
  Not[OrderedQ] tiebreak is only in the both-non-positive branch);
  numberp covers exactly the real explicit numbers (1/2 is a "/"
  node and numberp TRUE; %i/%pi/E/%inf/symbols false); the only
  atomic complex is %i (-%i is a unary "-" node); sqrt normalizes
  aggressively where Mathematica holds — sqrt(x^2) -> abs(x)
  (documented divergence: niceSqrtQ(x^2) true here, false in Rubi —
  unreachable at the class-1 discriminant sites), sqrt(2*x) ->
  sqrt(2)*sqrt(x), x^(1/2) -> 'sqrt node, x^(-1/2) -> 1/sqrt(x) —
  hence FPF carries 'sqrt / "/" / unary "-" branches; NF/NNF need
  atom-gates before op() and unary "-" branches (Maxima stores -3*m
  as a minus node, not a product with -1) and for-loop products
  where the .m Maps over a product (Map keeps non-list heads in
  Mathematica); SimplerSqrtQ's undecidable-sign case reproduces
  Rubi's pending-If decline by answering false (never true);
  sign() hard-errors on imaginary arguments (errcatch-able);
  OrderedQ is a total-order stand-in on sort() (measured: numbers
  first, %pi before bare symbols, x before 2*x — any consistent
  total order suffices for the tiebreak uses). The ContentFactor
  kludge (NF/NNF sum branches, LeafCount < 50 path) is omitted with
  the .m's GCD fallback kept — a sum only reaches them through a
  product-of-sums inside a captured exponent (no class-1 site).
  75 new probes; suite 265/0.
 - Cluster D — trinomial/quadratic/binomial-degree — DONE (commit
   8ad11d4). %mr_quadraticQ (:1380), %mr_binomialDegree (:846),
   %mr_trinomial_parts (:929) + %mr_trinomialQ (:568),
   %mr_linearMatchQ (:1420), %mr_quadraticMatchQ (:1427),
   %mr_binomialMatchQ (:1444), %mr_trinomialMatchQ (:1458), plus the
   unary "-" branch in %mr_binomial_parts the TrinomialParts sum
   branch needs. Line ports; the .m Drop-chain laxness and the :994
   b-slot typo are ported as written (pinned). The cluster D work
   exposed the %mr_matchQ first-binding limitation: the cond was
   evaluated once on the FIRST structural binding, so (a)
   TrinomialMatchQ's stored-order binding (c/n on the highest term,
   b/j on the next) failed j = 2*n and the n/j-swapped permutation was
   never tried, and (b) a bare x^n term bound the coefficient marker
   to the whole power (b = x^n, n = 1), the freeof cond failed, and
   the b = 1 / real-n binding was never tried. ROOT CAUSE FIX in the
   matcher: a non-trivial cond now threads through the structural
   search — explicit ["final"]/["match"]/["part"] continuations in
   %mr_mq_search / %mr_mq_flat_search / %mr_mq_part_search — and the
   match stands iff SOME structural binding makes the cond true; the
   cond = true fast path keeps the old first-success %mr_mq_match.
   MEASURED 2026-08-23: Maxima lambdas do NOT capture the local
   variables of the creating function (a lambda body sees the
   caller's / global P/E, not the creator's), so the continuation is
   an explicit list, not a closure. The trinomialMatchQ pattern uses
   the .m marker letters (b with x^n, c with x^j); the orderless
   partition search makes the stored term order non-load-bearing.
   REMAINING DIVERGENCE (documented, unreachable at the class-1 call
   sites): the matcher's absent rule cannot delete a product/sum
   factor containing a literal (b_*x, c_*x^2) as a whole via its
   optional coefficient — linearMatchQ 1+x^2, quadraticMatchQ 1+2x,
   trinomialMatchQ 1+2x stay port-false where the .m answers true.
   66 new probes; suite 331/0.
  - Cluster E — generalized binomial/trinomial — DONE (commit
    1f49775). %mr_generalizedBinomialQ (:579),
    %mr_generalizedTrinomialQ (:590),
    %mr_generalizedBinomialMatchQ (:1451),
    %mr_generalizedTrinomialMatchQ (:1465),
    %mr_generalizedBinomialDegree (:1017),
    %mr_generalizedTrinomialDegree (:1053), over
    %mr_generalizedBinomial_parts (:1022) /
    %mr_generalizedTrinomial_parts (:1058). The .m Parts pattern rules
    run the A3 matcher with fresh marker atoms; the winning binding is
    read back through the new %mr_mq_capture helper (global-state —
    the Maxima lambda the matcher calls cannot return the binding to
    the caller). The a_*u_ / x^m_*u_ product cases guard the trivial
    no-progress binding with %mr_mq_capture_self. Matcher surface
    fixes forced by the cluster: a ^-pattern matches the collapsed
    sqrt node as exponent 1/2 (x^(1/2) stores as 'sqrt(x)); against a
    TIMES pattern a unary-minus term splits into [-1, <subterm>]
    (Mathematica's Times[-1, ...]) so a_*x^q binds a = -1 on a
    negative sum term. GeneralizedTrinomialParts pins the positive
    orientation (n - q > 0) in the sum-pattern cond — the .m
    EqQ[r,2*n-q] is satisfied by either endpoint as q, and Maxima's
    stored descending term order otherwise traps the search on the
    negative-gap binding, while the GeneralizedTrinomialDegree call
    sites can only see the positive gap; the boolean Q/MatchQ answers
    are unchanged. The q := 0 form is the ORDINARY trinomial, not
    generalized (the .m PolyQ/Expon case carries NeQ[q,0]); the x^m
    shift of an ordinary trinomial is what generalizes it. 45 new
    probes; suite 376/0.
   - Cluster F — remaining C-tier condition predicates — DONE (commit
     b1bf223). %mr_linearPairQ (:1387),
     %mr_rationalFunctionQ (:1578), %mr_splitProduct (:7658) with
     %mr_sumBaseQ (:7617) special-cased for the bare `SumBaseQ` name the
     generator emits, %mr_pseudoBinomialPairQ (:1507) over
     %mr_pseudoBinomial_parts (:1524), %mr_inverseFunctionQ (:303),
     %mr_algebraicFunctionQ (:1681), and the clone-gap
     %mr_perfectSquareQ (referenced by class-1 rules but defined nowhere
     in the pinned clone — ported as a factor-exponent square test with
     the exact-rational corner; this build's factor(9/4) stays 9/4, so
     exact rationals are tested by integer numerator/denominator
     squares). PseudoBinomialParts reads Expon through %mr_degree under
     the %mr_polynomialQ gate and uses a local %mr_pseudoRoot rather than
     the still-unported public %mr_rt; PairQ keeps the .m IdentityQ tail
     reading (loose %mr_eqQ would over-accept distinct symbolic
     constants). 44 new probes; suite 420/0.
    - Cluster G — first B-tier shims — DONE (commit 25766ce).
      %mr_rt (:7513/:7549) over the structural RtAux split plus the
      AtomBaseQ / NegSumBaseQ / AllNegTermQ / SomeNegTermQ / TrigSquare
      helpers, %mr_expon (:1239), %mr_expandToSum (:3329/:3343) with the
      2- and 3-arg call forms through the lambda rest-arg spelling,
      %mr_intPart (:2952) and %mr_fracPart (:2969) with the floor
      complement reading. The .m's TogetherSimplify is deliberately NOT
      in %mr_rt: this build's ratsimp/factor expand or factor the
      argument ((a+b)^2, x^2-1), destroying the PowerQ / non-product
      reading. LtQ[#,0] inside RtAux is the strict is(# < 0) reading,
      not Rubi's NegQ. 32 new probes; suite 452/0. Same commit fixes
      %mr_symbols on negative rationals (length 2, one part — the
      unary-minus quirk) where %mr_eqQ used to hard-error.
    - Cluster H — small remaining B-tier shims — DONE (commit 8a7a5e3).
      %mr_polyQuotient / %mr_polyRemainder / %mr_polyDivide over the
      Maxima quotient / remainder / divide builtins (fail-closed on the
      %mr_polynomialQ pair), and the unbound inverse-hyperbolic log
      shims %mr_atanh / %mr_asinh / %mr_acosh. 11 new probes; suite
      463/0.
    - Cluster I — ExpandIntegrand algebraic surface — DONE (commit
      5b0e274). The class-1 surface of the 203-use ExpandIntegrand:
      positive-integer powers of sums expand, polynomial * (a+b*x)^m
      is kept in linear-power form by %mr_expandLinearProduct (over
      %mr_coefficientList in the shifted variable (x-a)/b), and the
      3-arg form distributes over the expanded v without expanding the
      power factors. The .m's log/trig/smart-apart branches
      (ExpandExpression / SmartApart, CollectRecipTerms /
      CollectReciprocals, the F^u and Log rules, the special
      MergeMonomials bases, SimplifyTerm / NormalizeIntegrand /
      UnifySum) are deferred and the fallback is plain expand(). 9 new
      probes; suite 472/0.
    - Cluster J — remaining high-usage B-tier shims — DONE (commit
      77299cf). %mr_substFor / %mr_substPower (the algebraic surface:
      x^n and linear-v substitutions; the .m's trig / inverse-function
      branches deferred), %mr_dist over the DistributeOverTerms
      surface, %mr_normalizePseudoBinomial (:1518), %mr_cancel over
      factor() (the builtin is unbound in this build), %mr_polyGCD
      (:1668) as the monic x-dependent gcd, and
      %mr_rationalFunctionExpand (:1644) over the algebraic
      ExpandIntegrand surface. 13 new probes; suite 485/0.
    - Cluster K — last B-tier names — DONE (commit 3b1ab1e).
      %mr_root (the rational reading of the Mathematica Root object:
      k-th explicit-rational root in ascending order, false to decline),
      %mr_intSum / %mr_intTerm (:7694/:7699) over FreeTerms /
      IntTerm with the linear-power and quotient readings, and
      %mr_hold (the identity ShowStep wrapper). 16 new probes; suite
      501/0.
    - Task 7 completion gate — PASSED. Every `%mr_*` name in
      translation_table.py is now defined in maxima_rubi_utils.mac
      (the missing-name census is empty); Layer A is 501/0; the parse
      sweep and load curve are clean. Deferred fidelity branches remain
      documented in the cluster notes (the .m's log/trig/smart-apart
      ExpandIntegrand branches, the SubstFor trig/inverse-function
      branches, the RationalFunctionExpand factor split) — they are not
      reached by the Layer A surface and are revisited if the Layer B
      corpus reaches them.
    - Task 8 — Layer B corpus driver + 1.1.1.2 smoke — DONE (commit
      99624d8). test/corpus_class1_driver.py + test/mr_preload.mac; the
      driver runs rubi() in place of integrate() with the T3 per-
      subprocess noun/zero-chain mechanics, --tls-limit 100000, and the
      T5 verdict mapping. The 1.1.1.2 first-20 smoke is 20/20 after
      triaging three first-contact FAILs: (1) the generator's powered-
      form Coeff (4-arg %mr_coeff) and Expon (3-arg %mr_expon) readings
      were missing; (2) %mr_degree did not see x-free algebraic
      constants (e.g. %pi/sqrt(16-%e^2)) as degree 0; (3)
      1_2_3_5_r20 needed an n # 0 guard against Maxima's degenerate
      constant-denominator binding (local guard, pending generator
      backport). Layer A 511/0; gates clean.
    - Task 9 — IN PROGRESS. The full class-1 run (18 shards, 25,697
      entries) was launched at 2026-08-23 19:10 UTC via
      `python3 test/launch_class1_shards.py --launch`; pids in
      `test/corpus_class1.shard-pids`, per-shard .out/.log in
      `test/corpus_class1.shardNN.{out,log}`. Recursion-cap tuning:
      the 1.1.1.2 first-20 smoke had no timeouts (max wall 8.6 s
      under the 30 s cap) and the package's candidate cap is 16.
      First-contact triage already fixed two more Maxima-matcher
      degenerate-binding misfires (1_2_1_2_r134 c # 0; the earlier
      1_2_3_5_r20 n # 0).
    - Task 9 first full run (pre-fix) merged 25,697/25,697 entries:
      6,243 PASS / 19,454 FAIL (24.3%); class split error 8,866,
      unverified 7,385, timeout 3,198, no-answer 2,389, verified 2,810,
      expected 1,044, unexpected 5. Merged via test/merge_class1_shards.py
      into test/corpus_class1.out.
    - ROOT CAUSE of the mass FAILs: %mr_eqQ was the LOOSE clone-gap
      reading (%mr_possible_zeroQ(u-v)), which zero-substitutes EVERY
      variable symbol, so a generic parameter product (-10*a*b*c) read as
      "possibly zero" and the EqQ guards of the 1.1.1.x / 1.2.x rules
      fired on integrands they did not cover. Fixed (commit 312f949):
      %mr_eqQ is now strict (u-v simplifies to 0); %mr_neQ unchanged.
      Layer A 511/0, gates clean, 1.1.1.3 sample dropped from ~all-FAIL
      to 12/15 PASS.
    - Full class-1 run RE-LAUNCHED (18 shards) after the EqQ fix;
       results pending. Remaining: wait for the shards, re-merge, chase
       the residual file-by-file FAILs, write docs/corpus-baseline-uplift.md,
       and commit the acceptance record.

## Work item: Task 9 divergence loop — matcher-divergence classes (2026-08-24)

PROCESS CHANGE (HUMAN FEEDBACK 2026-08-24): the 3-h full run is a
confidence GATE, not a debug tool. KILLED the in-flight 18-shard run (its
code was non-final; its number would be superseded) and adopted a fast
inner loop: `test/canary.py` re-runs just the failing (file, entry) targets
in fresh Maxima subprocesses (~1 min/iteration) + Layer A (511) as the
regression gate. Full run only once the canary/sample is clean.

Two systemic MAXIMA-MATCHER-DEGENERATE-BINDING classes found via the
canary, both fixed in one place (no per-rule whack-a-mole):

- CRASH class: Maxima's defmatch degenerate-binds a zero coefficient (a
  monomial read as the binomial `0 + c*x`), and the affected rule's cond
  divides by it (`expt: undefined: 0 to a negative exponent`), KILLING the
  process. Fix (maxima_rubi_utils.mac %mr_dispatch): wrap `apply(r,[f,x])`
  in `errcatch` — a rule that crashes on a binding is a misfire, so it
  declines and the next rule / integrate fall-through handles the integrand.
  `errcatch` returns [value]/[] (measured); a crashing rule now declines.
  Cleared 6 of the 9 initial canary FAILs.

- WRONG-ANSWER class: the flat first-match-wins table + the loose matcher
  let a higher-form rule (quadratic/quartic) fire on a lower-form integrand
  (its leading `x^2`/`x^4` coefficient bound to 0). Fix (generator
  `nonzero_guard_caps`): for every parenthesized polynomial-in-x factor,
  the LEADING coefficient of a numeric degree >= 2, and any SYMBOLIC
  exponent (a term `b*x^n` with n=0 is the constant b), must be nonzero.
  Emitted as `%mr_neQ(<cap>, 0)` appended to the rule COND (a regular
  function, evaluated once per matched rule) — NOT as a matchdeclare
  lambda, which the e8 timing showed adds ~17 s to hard quartics (13.4 s ->
  30 s, past the cap); the cond form restores 13.6 s. `nonzero_guard_caps`
  also supersedes the two hand-patched local guards (1_2_1_2_r134 c # 0,
  1_2_3_5_r20 n # 0) — regenerated from the Rubi source now, so they are
  properly backported. Regenerated all 67 files (2710 rules, no mismatch);
  2743 guard clauses across 56 files. Probe /tmp/md4: rejects the C=0
  degenerate match, keeps the missing-middle-term case (B=0).

Validation: canary 10/10 (was 1/10 at the start of the loop), Layer A
511/0, parse sweep 67/67 clean, load curve clean. NEXT: broaden the canary
to a cross-section of all 40 files to surface any remaining class, fix, and
only then re-run the full class-1 as the acceptance gate. 

## Work item: Task 9 divergence loop — Step 1 fallback gate (2026-08-24)

The `rubi` integrate-fallback param, default false (handoff Step 1). A
top-level 0-firing is a port/matcher-gap signal (the corpus is Rubi's own
suite — rule-solvable by construction), not a job for Maxima's integrate,
which is slow on generic parameters and prompts for sign assumptions
(92 s before EOF in one standalone run, measured 2026-08-24).

Changes:
- `mr_top(f, x, fb)` gates the TWO top-level fall-throughs (recursion cap,
  no rule fired). `rubi(f, x)` = rules-only (fb false): a 0-firing returns
  the `mr_unintegrable` noun (the driver's noun detector already classifies
  it no-answer). `rubi_fallback(f, x, fb)` = the explicit integrate
  fall-through entry.
- DESIGN DECISION (the handoff's open question): the flag governs ONLY the
  top level. `mr_int(f, x)` — the entry the generated replacements call for
  NESTED sub-integrals — keeps the status-quo integrate fall-through
  (fb true): a nested 0-firing is a different case, and corpus entries
  currently verified through nested fallback must not regress.
- MEASURED Maxima landmine (this build): NO arity overloading — a second
  same-name definition with a different arg count REPLACES the first (the
  2-arg call then errors "Too few arguments supplied to rubi(f, x, fb)");
  no variadic syntax (`b...` is a parse error); `argc`/`arglist` have no
  manual entries. Hence the two modes have DISTINCT NAMES — a deviation
  from the handoff's `rubi(f, x, fb)` sketch, which is not expressible in
  this build.
- Driver (`build_text`): rules-only by default; `MR_FALLBACK=1` switches to
  `rubi_fallback(mr_f, var, true)` for A/B baseline runs.
- Layer A: `test_load_and_api` rewritten for the new contract (5 ->
  unintegrable noun; `rubi_fallback(5, x, true)` -> 5x; sin(x)^x ->
  unintegrable noun; empty table -> unintegrable noun); the `5x^2` probe is
  now explicitly full-coverage (below). TDD red first: the new probes FAILed
  + the suite died on the arity error before the implementation landed.
- Measured 0-firing facts behind the probes (full table loaded): 5 and
  sin(x)^x fire no class-1 rule; x^2 DOES fire 1.1.1.1 r2 (x^m rule); 1/x
  fires 1.1.1.1 r1 (literal pattern). 5*x^2 fires NO rule: the 1.1.1.1
  family is (a+b x)^m / x^m / 1/x forms only, and there is NO constant-
  factor pre-rule (`c_.*u_` grep over the whole pinned Rubi clone: nothing)
  — in Rubi 4 the monomial-with-coefficient cases are carried by the
  1.1.3.x (c x)^m families, not a pre-rule.

Validation (Maxima 5.50.0 / SBCL 2.6.7): Layer A 511/0, parse sweep 67/67
clean, load curve clean. Canary broad (120-target cross-section,
--parallel 10) A/B:
- OFF (new default): 76 PASS — no-answer 46, verified+expected 30,
  unverified 15, timeout 29.
- ON (MR_FALLBACK=1, status quo): 66 PASS — no-answer 21,
  verified+expected 45, unverified 19, timeout 35.
The top-level 0-firing cases converted from slow integrate (timeout or
lucky slow-verified) to fast (~6 s) no-answer PASS lines — 25 of them are
the machine-readable Step-2 gap list. Residual OFF timeouts are the
designed nested-fallback cases (top-level rule fires; its replacement's
nested mr_int falls through to a slow integrate) plus slow replacements.

NEXT (Step 2): work the 46 no-answer cases — per case, find the Rubi rule
that should cover it (expected-answer shape + family header) and trace why
the Maxima port declines. FIRST target: the a*x^n monomial-with-coefficient
form (5*x^2 class) — no rule in the ported set; decide whether the port
needs the 1.1.3.x (c x)^m coverage for it or a documented gap.

## Work item: Task 9 divergence loop — dead-rule names + verifier guard (2026-08-24)

Two independent defects found while chasing the broad canary; both fixed,
neither committed yet.

- GENERATOR DEAD-RULE BUG (real, fixed). `drop_optionals` ran POST-translate
  on the emitted pattern text and did a raw substring replace for a capture
  named `r`; that hit the `_mr_` prefix of every renamed capture
  (`_mr_1_1_2_6_r3_g` -> `_mr1_1_2_6_r3_g`). The corrupted names are never
  `matchdeclare`d, so Maxima reads them as literal symbols and the pattern
  matches no integrand. Effect: 138 dead rules across 17 files; 1.2.4.1 /
  1.2.4.2 were fully dead. Fixed in `generator/generate_class1.py` and the
  17 affected `rules/class1/*.mac` files regenerated.
- STATIC REGRESSION PROBE (new). `probes/census/01-generation-vs-inventory.py`
  now has a committed-file name-integrity half (`pattern_name_issues`): every
  `_mr*` token in a committed `defmatch` pattern must be a well-formed
  rule-local capture or a MatchQ marker for that rule. It catches the
  `_mr1_1_2_6_r3_g` corruption shape and foreign `_mr_...` tokens. Current:
  67 files, 2710 rules, 0 name-integrity bad files.
- SECOND MAXIMA-MATCHER BUG (found, NOT fixed). A behavioral "pattern matches
  its own family integrand" probe for 1.1.2.6 r3 failed even after the names
  were intact: constrained multi-factor `defmatch` / `matchdeclare` product
  patterns can under-match because Maxima's `*` matching is greedy,
  order-dependent, and does not backtrack through the constraint. Minimal
  repros show an all-`true` pattern matching with a cross-binding while a
  `freeof(x)`-constrained pattern declines a valid binding. This is a separate
  triage class from the generator name bug. The behavioral probe was removed
  from Layer A (it conflated the two bugs); a comment in `test_maxima_rubi.mac`
  points at the static census probe and records the under-match finding.
- DRIVER VERIFIER ERROR GUARD (new). The corpus driver's zero-test chain called
  `ratsimp` / `factor` unguarded; on 1.2.2.4 e165 and 1.2.2.8 e1 the
  VERIFICATION crashed with `quotient' by `zero'` before the CLASS line, so the
  entry was misclassified `error`. `zero_chain` now wraps the whole chain in
  `errcatch` (error -> 0, i.e. the zero-test did not close). 1.2.2.4 e165 is
  now `verified`; 1.2.2.8 e1 is `unverified`.

Validation (Maxima 5.50.0 / SBCL 2.6.7): Layer A 511/0; parse sweep 67/67
clean; load curve clean (2705 measured rules, c = 9.92 vars/rule); census
OK (2710 rules, name integrity clean). Broad canary (120-target cross-section,
rules-only default, --parallel 12): 77 PASS / 43 FAIL — no-answer 46,
verified 26, expected 5, timeout 25, unverified 18, error 0. The Step-1 OFF
baseline on the same cross-section was 76 PASS / 44 FAIL; the error class is
gone, and the dead-rule fix shows up as a composition shift in this sample
rather than a large total uplift.

NEXT: triage the residual broad-canary classes — the 25 timeouts first
(the designed nested-fallback / slow-replacement cases), then the 18
unverified, then the 46 no-answer Step-2 gap list. The matcher under-match
class (1.1.2.6 r3 shape) is now a named open item.

## Work item: native elliptic answer nouns (2026-08-24)

HUMAN DECISION (2026-08-24): for the elliptic cases the generator should
return the NATIVE Maxima nouns `elliptic_f/e/pi`, not the `mr_elliptic_*`
package spelling, because `diff` differentiates the native nouns (the
`mr_` spelling was a dead end for verification). Committed separately from
the dead-rule / verifier work.

- ROOT CAUSE of the old spelling: the 5.49 support audit saw
  `elliptic_f(...)` calls stay nouns and the plan chose `mr_elliptic_*`
  "package nouns" (docs/rule-translation.md:134). That over-applied the
  anti-masking house rule (package-DEFINED shims must not take native
  names) to answer-side functions the package does NOT define. A native
  answer noun never masks a builtin, so the rule does not apply.
- MEASURED on 5.50.0: `diff(elliptic_f(asin(x),1/2),x)`,
  `diff(elliptic_e(...),x)`, `diff(elliptic_pi(1,asin(x),1/2),x)` all
  close. So the native noun both differentiates and cancels against the
  corpus's native expected answers.
- CHANGE: `generator/translation_table.py` (RESTRUCTURE) and
  `generator/generate_class1.py` (the EllipticF/E/Pi special-case) now
  emit `elliptic_f/e/pi`. Regenerated 14 rule files; the diff is PURELY
  the `mr_elliptic_* -> elliptic_*` rename (spot-checked, no other drift).
- STATIC REGRESSION PROBE (new): `probes/census/01-generation-vs-inventory.py`
  gained a `native_elliptic_issues` half — no committed `rules/class1/*.mac`
  may carry an `mr_elliptic_{f,e,pi}(` call. Red before the fix (14 files),
  green after (0).
- CENSUS 02 PROBE FIX (needed to re-stamp honestly): `defined_names()`
  now also parses the `defmfun` dispatchers out of
  `maxima_rubi_dispatch.lisp`, so `%mr_binomialQ` / `%mr_intBinomialQ`
  are no longer miscounted as "pending". Re-stamped pending surface:
  full 2 (mr_appellf1 8, %mr_exponMin 2), C-tier 0.
- DOCS: rule-translation.md:134 + the §6 build-drift caveat updated
  (the elliptic entries are the one answer-side case that DID change
  native); package-architecture.md open item marked RESOLVED.

Validation (Maxima 5.50.0 / SBCL 2.6.7): Layer A 511/0; parse sweep 67/67
clean; load curve clean (2705 measured rules, c = 9.92); census OK (2710
rules, 0 name-integrity bad, 0 mr_elliptic_* files). Broad canary
(120-target, rules-only, --parallel 12): 78 PASS / 42 FAIL (up from
77/43) — no-answer 46, verified 27, expected 5, timeout 25, unverified
17, error 0.

- PROVABLE WIN the canary does not yet show: 1.3.2 e1 (integrand
  `1/((2^(2/3)+x)*sqrt(1+x^3))`) — in a CLEAN session
  `ratsimp(diff(rubi(...) - <corpus expected>, x)) = 0` (is() = true),
  i.e. the native elliptic fix DOES close that entry's expected chain.
  Yet the broad canary still labels it `unverified`.
- DRIVER BUG (found here, ROOT-CAUSED + FIXED in the next work item):
  1.3.2 e1's expected chain provably closes in a clean session, yet the
  canary labels it `unverified`. An initial read blamed the driver's fixed
  `pos$ no$` answer chain leaking into the verification `ratsimp`
  (`batch_answers_from_file` reads the next input line as a sign answer),
  but that was a RED HERRING — see the parenthesization work item below.

## Work item: driver expected-answer parenthesization bug (2026-08-24)

ROOT CAUSE (confirmed by measurement, NOT the suspected answer-leak):
`build_text` built the expected-answer zero-test as
`diff(mr_r - <e_text>, x)` by inlining the corpus expected text WITHOUT
parentheses. When the expected answer is a SUM `A + B`, that parses as
`mr_r - A + B` — every term after the first has its sign flipped — so a
CORRECT antiderivative fails the zero-test and is misclassified
`unverified` (or, worse, silently falls through to the weaker `verified`
chain). Measured on 1.3.2 e1 in one process, `mr_r` fixed identical:
  `ratsimp(diff(mr_r - <e>, x))`   -> nonzero  (the driver's exact form)
  `ratsimp(diff(mr_r - (<e>), x))` -> 0        (parenthesized)
  difference of the two -> nonzero (sign flip confirmed)
The suspected answer-leak (pos/no pool feeding the verification ratsimp)
is a SEPARATE, real-but-latent fragility of `batch_answers_from_file` + a
fixed answer sequence; it did NOT cause this misclassification and is not
fixed here.

- FIX (one-line x2): `test/corpus_class1_driver.py` — parenthesize the
  inlined expected text in both the primary and secondary expected
  zero-chains: `diff(mr_r - ({e_text}), x)` / `diff(mr_r - ({e_text2}), x)`.
  The verified chain (`diff(mr_r, x) - mr_f`) uses the `mr_f` symbol, so it
  was never affected.
- REGRESSION GUARD (new): `test/test_driver_parens.py` — (1) construction
  check (no Maxima): `build_text` must emit the parenthesized form for both
  expected chains; (2) behavior check (Maxima): the formerly-broken 1.3.2
  e1 must classify as a PASS class. Verified it FAILS (exit 1) with the fix
  reverted and PASSES (exit 0) with it.

Validation (Maxima 5.50.0 / SBCL 2.6.7): Layer A 511/0 (unchanged — the
fix is test-only). Broad canary (120-target, rules-only, --parallel 12):
82 PASS / 38 FAIL (up from 78/42), NO PASS->FAIL regressions. Class shift:
expected 5->31, verified 27->5, unverified 17->16, timeout 25->22,
no-answer 46->46, error 0->0. The 26 `verified`->`expected` moves are a
STRENGTHENING: those entries' SUM-valued expected answers now match the
corpus answer up to a constant (the expected chain closes), previously
masked by the sign flip and only caught by the weaker verified chain.

NEXT: (1) the pos/no answer-chain fragility is now a NAMED latent item —
the verification zero-test runs under `batch_answers_from_file` with a
fixed answer sequence, so a verification sign-prompt would consume
positional lines; consider isolating the verification from the answer
stream (e.g. asksign-suppressed verification or a fresh subprocess) if it
ever bites; (2) AppellF1 (`mr_appellf1`, 8 uses) — native `appellf1` exists
only as a noun and `diff` does not close on it, so keep the package noun or
add a deriv rule; (3) `%mr_exponMin` (2 uses) is a genuinely unported B-tier
helper; (4) continue the timeout / no-answer triage.

## Minor findings (triage at final whole-branch review)

- [Task 6] probes/load_wall/probe-load-wall.out part 5: the echoed
  continuation lines of the multi-line disp INPUT (+length(mr_rules_...)
  lines) leak into the .out because the input-echo filter only strips the
  first line of a wrapped statement. Cosmetic — the machine-readable
  PREFIX_TOTAL= marker is the authoritative value and is what the verdict
  checks.
- [Task 1] test_maxima_rubi.mac: Results line is not literally the last output
  before quit() — the closing `====` and the printed `run_all_tests()` return
  value (`0 = 0`) follow it. Plan-mandated (the brief's code returns
  `tests_failed = 0`). Functional intent intact (unique greppable marker; a
  mid-run death prints no Results line). Possible fix: return `true` instead of
  `tests_failed = 0` so the prose holds.
- [Task 1] test_maxima_rubi.mac: Results line renders with double spaces
  (`Results:  3  passed,  0  failed`) — inherent to Maxima `print`. All later
  "read that line" steps must use a spacing-tolerant pattern (e.g.
  `Results:.*passed.*failed`). Propagate to any task that hard-codes the literal.
- [Task 1] test_maxima_rubi.mac: only the passing paths of check/check_bool/
  check_not are exercised by the smoke suite; the FAIL branches are untested.
  Brief mandates exactly these three smoke checks. A later task that adds a
  deliberate-failure assert would cover the counters/FAIL-prints.
- [Task 2] maxima_rubi.mac:14-20 — 3-space indentation on the errcatch comment
  + ok:/if lines vs 2-space elsewhere (cosmetic, from the fix commit).
- [Task 2] maxima_rubi_utils.mac:36 — %mr_dispatch `if res # false` uses raw
  `#` in the if-condition (evaluated, so correct), not is()-wrapped. Forward
  note: Task 3's first rule should ASSERT a firing rule actually fires (not
  just that fall-through works), so this path is exercised.
- [Task 2] maxima_rubi_utils.mac:49-57 — mr_int increments global depth_level
  on entry, decrements before return; if %mr_dispatch throws, the decrement is
  skipped (budget left incremented). Robustness note for Task 3+ (real rules).
- [Task 2] maxima_rubi.mac:13 — batched path (load_pathname=false) untested;
  only the sibling-dir path is exercised. Coverage note for a later task.
- [Task 3] test_maxima_rubi.mac:130-131 — test_load_and_api's table wipe sits
  AFTER its fall-through checks, so with Task 3's top-level table the
  "fall-through x^2" check actually FIRES the power rule (a*x^m matches x^2);
  it still passes (answers coincide) but no longer tests what its name says.
  Optional fix: hoist `saved_table : mr_rule_table, mr_rule_table : []` to the
  TOP of test_load_and_api so all its checks run against a genuinely empty table.
- [Task 3] FORWARD NOTE for Task 4+: no committed assertion distinguishes the
  %mr_dispatch table-fired path from fall-through — every rubi() answer in the
  suite coincides with Maxima's own integrate on this build, the verbose line
  is printed but not asserted, and the direct firing asserts call rule
  functions (bypassing the table). A dispatch that never fired a table rule
  would pass 20/20 silently. Mitigate in Task 4+ with a rule whose answer
  differs from integrate, an assert on the verbose line, or direct firing
  asserts per generated rule (as done here for power/rec).
- [Task 3] Cosmetic: check name "recursion re-dispatches" (test) vs "recursion
  re-dispatches (end-to-end)" (plan); the vacuity rationale is stated in two
  adjacent comments. No behavior impact.
- [Task 4] DECISION (human, 2026-08-20): the emitter emits the PLAIN pattern
  only — the Power-optional D-duplication (power_dups) is NOT wired into
  emit_rule. Rules with an optional Power exponent (e.g. 1.1.1.1 rules 2,4,5)
  will not fire on the bare-exponent-1 case (Power head dropped: bare `x`,
  `(1+2x)`); those fall through to integrate (correct answer, not via the
  rule). This is a COVERAGE gap, not a correctness bug. FORWARD NOTE for Task 9:
  the divergence loop must add the Power-optional D-duplication where the corpus
  shows the coverage gap (plan step 2 updated to record the deferral).
- [Task 4] generate_class1.py:419 — `lhs, rhs, cond = split_rule(text)` sits
  OUTSIDE the try/except that wraps the other per-rule crashes. A run with `:=`
  that defeats split_rule exits 1 with a bare traceback naming no r<n>. Optional
  fix: move the split_rule call inside the try for the same GenError treatment.
- [Task 4] generate_class1.py:275-277 — a HEAD-position pattern variable
  (`v_[…]` in an lhs) bypasses both the new head check and F11 (translate_atom
  consumes `v_` as an ordinary capture, emitting a literal `_mr_…_v[…]`). No
  class-1 rule uses a head pattern (none in 1.1.1.1); the Task 6 sweep is where
  it would bite. Suggested fix: raise when a capture marker is immediately
  followed by `[`.
- [Task 4] translation_table.py — `translate()` KeyError still unreachable in
  the current call graph (harmless guard); `"Power"/"Plus"/"Times"` map to
  non-callable infix names (a noun call if ever written as an explicit head).
  Pre-existing brief-mandated table content; no 1.1.1.1 rule affected. Note only.
- [Task 5] Bug C: `%mr_termPower` (maxima_rubi_utils.mac:369) sign-strip guard is
  `not atom(t) and op(t) = "-"`, but `atom(-2)=true` in this build, so numeric
  signs are never stripped: termPower(-2,x)=[-2,1,1]. Consequence:
  removeContent(2x-2)=2x-2 (Rubi: 1-x). Masked in class 1 (consumed inside
  Log/b, a residual content is an additive constant). Fix: strip sign for any
  t with op(t)="-" (guard op per atom-first rule), or implement the source's
  a+b==0 integer pattern.
- [Task 5] Inaccurate deviation notes at maxima_rubi_utils.mac:406-414 (claim the
  .m pattern "matches a numeric base hiding in an integer"; it does not — Rubi's
  RemoveContent[4+2x,x] also returns input unchanged). Cosmetic; correct the note.
- [Task 5] `%mr_together` idiom (maxima_rubi_utils.mac:138-141) is behaviorally
  correct (verified on 9 inputs incl. cancellation) but cryptic — add one comment
  stating the measured rat-object shape so a future reader doesn't "simplify" it.
- [Task 5] Minor DRY: %mr_polyDegQ re-runs %mr_together on an already-together'd
  v; %mr_negQ's final `is(v)=true` coercion is redundant (operands already bool).
- [Task 5] FORWARD NOTE for Task 6 (F2, under-scoped in the report): the
  generator table maps ALL PolyQ arities 1:1 to the 2-arg %mr_polyQ. Beyond the
  3-arg Symbol form (~82-100 uses -> should map to %mr_polyDegQ, now correct after
  Bug B), there are ~100 TWO-ARG power-form uses `PolyQ[Pq, x^v]` (e.g. x^(n/2))
  that are a SILENT semantic error: %mr_polyQ(u, x^v) treats x^v as the variable
  -> PolyQ[x^4+1, x^2] -> false where Rubi -> true, flipping negated guards
  (Not[PolyQ[..., x^(n/2)]] in 1.1.3.7.m:41, 1.1.3.8.m:21) into wrong-answer paths.
  Task 6 FIRST STEP must add generator-side PolyQ overload dispatch:
  (u,x)->%mr_polyQ, (u,x,n)->%mr_polyDegQ, (u,x^v[,n])->a power-form port
  (polynomial in x^v) or an explicit loud generation error. MUST land before the
  67-file generation.
