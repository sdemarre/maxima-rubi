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

## Work item: no-op rule self-match loop guard (2026-08-24)

ROOT CAUSE (the first broad-canary timeout, 1.1.1.3 e1276
`(1-2x)^2(3+5x)^3/(3x+2)^8`): the integrand is split into single-term
rationals (500 x^5/(3x+2)^8, 400 x^4/(3x+2)^8, ...). Each term SHOULD be
handled by the specific binomial-power rule, but that rule does not fire
(the known matcher-gap), so each term falls to the Rubi NORMALIZATION rule
1.4.2 r24 (`Px*z^q*u^p`, z binomial / u trinomial). Its repl is
`Px*ExpandToSum[z,x]^q*ExpandToSum[u,x]^p` — the IDENTITY when z,u are
already a binomial/trinomial, so r24 self-matches the SAME term forever.
Measured (rubi_verbose, one process): the 500 x^5/(3x+2)^8 term fired r24
14x identically (a pure 1-cycle) before the depth-16 cap; 28 firings total
across two terms. Each loop level is a full ~2705-rule scan, so it ran to
the cap and only THEN fell to `integrate`, which solves the whole integral
in <1 s — the 30s+ canary timeout was entirely the loop.

- FIX (`maxima_rubi_utils.mac`, +21): a seen-stack loop guard in `mr_top`.
  `%mr_seen` (pushed/popped around the dispatch) holds the integrands on the
  current recursion chain; if `member(f, %mr_seen)` a rule re-dispatched the
  SAME integrand (a no-op self-match) -> cut the cycle now and fall through
  (integrate nested / unintegrable top) instead of re-scanning. `member`/`=`
  is the test — `isequal` and `identical` do NOT evaluate to a boolean in
  this 5.50.0 build (they stay unevaluated nouns; measured).

Validation (Maxima 5.50.0 / SBCL 2.6.7): Layer A 511/0 (unchanged). Broad
canary (120-target, rules-only, --parallel 8): 82/38 -> 83/37, NO
PASS->FAIL. The 5 changed targets were all `timeout` before: 1 -> `expected`
(1.2.1.9 e160, now PASS), 4 -> `unverified` (1.2.1.2 e2202, 1.2.1.5 e105,
1.2.2.5 e44/e94; still FAIL, but they now TERMINATE with an answer instead
of hanging). Class shift: expected 31->32, unverified 16->20, timeout
22->17, no-answer 46->46, verified 5->5. e1276 itself: infinite hang
(>120 s) -> 32 s and CORRECT (`CLASS expected`), r24 firings 28 -> 4.

The 4 `unverified` are NOT wrong answers from the guard: spot-checked 1.2.2.5
e44, its result carries a leftover degenerate `mr_sum[0,k,0,0]` (a 0-sum
noun) so the zero-test cannot close — a PRE-EXISTING answer-quality defect
the hang had been hiding (the integral never produced an answer before).

NEXT (investigated 2026-08-24, not yet fixed; both are real handoffs):

(1) e1276 + sibling product timeouts — correct but ~32 s. CONFIRMED flow
(rubi_verbose, one process): 1.1.1.3_r17 EXPANDS `((1-2x)^2(5x+3)^3)/(3x+2)^8`
into six monomial terms over the EXPANDED `(3x+2)^8` — `500x^5, 400x^4,
235x^3, 207x^2, 27x, 27` — and each term's own cascade (1.4.1_r7 /
1.4.2_r24 / 1.3.3_r4) ENDS at the native `integrate` fall-through (~5 s
each -> ~32 s total). Native `integrate` on the WHOLE integral is <1 s
(measured). So the cost is 6 per-term integrate calls, NOT a matcher gap.
My earlier "1.1.3.2 matcher-gap" note was WRONG: 1.1.3.2's pattern is
`(c x)^m (a+b x^n)^p` — a POWER `(c x)^m` — which does NOT structurally
match the monomial `c x^k`; measured 0/115 1.1.3.2 rules fire on
`500x^5/(3x+2)^8` (all 115 patterns degenerate-match, all conds reject).
OPEN (the real fix): find the rule that should integrate a monomial over a
linear power, `c x^k (a+b x)^n` — is it absent from the port, or does a
rule decline it on a too-strict cond? OR stop 1.1.1.3_r17 from splitting
into six per-term integrates. Repro: canary target `1.1.1.3 1276`,
integrand `(1-2*x)^2*(3+5*x)^3/(2+3*x)^8`.

(2) degenerate `mr_sum[0,k,0,0]` noun (the 4 unverified). CONFIRMED:
`mr_sum` is emitted ONLY by rule repls (no utility constructs it; the only
def is the 4-arg noun); 24 rule files emit it, incl. the 1.2.2.5/1.2.2.6/
1.2.2.7 quadratic-in-x^2 rules that handle e44's shape. e44's cascade
operates ENTIRELY on `mr_sum[0,k,0,<n>]/(...)`-shaped integrands (1.3.3_r4,
1.2.2_5_r3, 1.2.1_6_r4, 1.2.2_6_r2) that never resolve the noun, so the
final answer carries `mr_sum[0,k,0,0]` -> unverified. `mr_sum[0,k,0,0]` is
`Sum[<0>,{k,0,0}]` — a sum whose range collapsed to `0..0` (empty) with a
0 summand for this integrand. OPEN: pin the EXACT 1.2.2.x rule whose repl
first emits it for e44, then either (a) have the generator emit the
CONCRETE sum when the limits are constant integers (an empty sum = 0), or
(b) add a package simplification `mr_sum[0,_,0,0]`->0 (and reduce any
constant-range mr_sum). Repro: canary target `1.2.2.5 44`, integrand
`(p1+p2*x+p3*x^2+p4*x^3)/(x^4-5*x^2+4)^3`.

(3) continue the timeout / no-answer triage.

## Work item: mr_sum concretization + capture snapshots (2026-08-25)

Follow-up (2) of the loop-guard item: the degenerate `mr_sum[0,k,0,0]`
unverified answers. TWO root causes, two fixes.

ROOT CAUSE 1 — eager summand evaluation. Maxima evaluates call
arguments eagerly: a repl's `mr_sum(%mr_coeff(Pq,x,2*k)*x^(2*k), k, 0,
q/2)` evaluates the summand ONCE with k free; the total %mr_coeff
returns 0 for a symbolic exponent, so every even/odd-split sum is born
the contentless noun `mr_sum[0,k,0,3/2]`; the same rule family re-fires
on it, drains the bounds, and the answer carries `mr_sum[0,k,0,0]`.

FIX 1 — `mr_sum` is now a CONCRETIZING function (maxima_rubi_utils.mac):
numeric bounds -> per-integer i over ceiling(lo)..floor(hi): a lambda
summand is applied per index (`apply(fun,[i])`); a bare-identifier
summand resolves through its value (`ev(subst(i,var,ev(fun)))` — the
Rubi Module-local-u shape of 1.1.3.1 r13; a lambda body of one bare
symbol does NOT get the index bound into its value — measured
mech_decisive D1); an already-evaluated expression gets the index
substituted + re-ev'd; empty range -> 0; symbolic bounds keep the noun.
The generator lambda-wraps every NON-identifier summand
(`mr_sum(lambda([var], <summand>), var, lo, hi)`); the 8 bare
identifier summand sites (1.1.3.1/1.1.3.2 r13 family) stay bare.

ROOT CAUSE 2 — capture corruption under nested dispatch. Found when
FIX 1 let the 1.2.2.5 r3 repl run to completion for the first time:
e44 then returned a NON-antiderivative. Maxima block scoping is
DYNAMIC, and a defmatch matcher assigns the pattern symbols as a side
effect of every match attempt. The even/odd-split repl evaluates its
SECOND mr_int argument (the odd part) AFTER the first mr_int (the even
part) has re-dispatched the whole rule list — which re-matches r3's
own pattern on the even cascade's intermediate integrands and clobbers
the repl's live capture bindings. Measured on e44: the even cascade
rebound `_mr_1_2_2_5_r3_b`/`_mr_1_2_2_5_r3_c` to -240/348 (a matched
intermediate quartic `348x^4-240x^2+4`) and the odd integrand was
built from the wrong quartic. Previously masked: with contentless sums
the repl's cascade never reached the corrupting integrand; and once the
lambda branch below was dead, the repl FATAL'd inside mr_sum and
errcatch made r3 DECLINE, so a different (clean) rule handled e44.

FIX 2 — capture snapshots (generate_class1.py emit_rule): the repl
binds each capture from the immutable matchlist `mm` into a fresh
`<cap>__s` local (a name no matcher can assign) and the body is
rewritten to those locals. The cond keeps the capture names (it runs
before any nested dispatch). Regeneration is purely mechanical: every
changed rule line is a repl line (verified: all added lines carry
`__s`, none removed).

MEASURED BUILD TRAP (the lambda-branch bug that hid ROOT CAUSE 2 for a
session): in this build `op(lam) = "lambda"` (STRING) is FALSE for a
lambda form — op returns a symbol for special forms while the string
idiom holds for ordinary operators, and symbols never compare equal to
strings (`a = "a"` -> false, all measured 2026-08-25, op_cmp/
op_typeof probes). A dead lambda branch fell to `ev(subst(i,var,fun))`,
which descends into the lambda and fatals replacing its parameter
("parameter must be a symbol ... found: 0"). The branch test is now
`op(fun) = lambda or op(fun) = "lambda"` (both forms; robust across
builds).

Validation (Maxima 5.50.0 / SBCL 2.6.7): new regression guard
`test/test_mr_sum_concrete.py` (sweep: every generated mr_sum call is
lambda-wrapped or a bare identifier; semantics SEM1-SEM7 on the public
mr_sum contract; behavior: 1.2.2.5 e44 classifies as a PASS class) —
RED before both fixes, GREEN after. Layer A 511/0, per-test lines
byte-identical to baseline. Broad canary (120 targets, --parallel 8):
83/37 -> 85/35, NO PASS->FAIL; the only classification changes are
1.2.2.5 e44/e94 FAIL:unverified -> PASS:expected; every other target
unchanged in kind. `test/canary.broad.out` regenerated.

REMAINING (separate bugs — now exposed by the concretization, not
caused by it): 1.2.1.2 e2202, 1.2.1.5 e105, 1.2.2.6 e123 are still
FAIL:unverified but their answers carry NO mr_sum anymore — they now
return monstrous (323 KB - 2 MB) non-antiderivatives from a different
sub-rule path the concretized cascade reaches; 1.2.2.7 e1/e17 still
timeout (the e1276-class slowness, follow-up (1)). Also observed,
separate gap: Rubi's 2-arg `Simp[u, x]` (IntegrationUtilityFunctions.m
:2265) translates to a 1-arg `%mr_simp` call — "Too many arguments"
error at repl evaluation, errcatched -> those rules silently decline
(coverage gap, not wrong answers).

## Work item: e1276 speedup — ExpandIntegrand quotient linear-power factor + constant-factor fix (2026-08-25)

Follow-up (1) of the loop-guard item: 1.1.1.3 e1276
`(1-2*x)^2*(3+5*x)^3/(2+3*x)^8` — correct but ~33 s wall, over the 30 s
canary cap (FAIL:timeout).

ROOT CAUSE (measured: rubi_verbose trace + shell-side timing, since
`time()` returns `[]` and `lisp(get-universal-time)` is constant in this
build): 1.1.1.3_r17 fires on the three linear powers and calls
`%mr_expandIntegrand`, whose linear-power scan reads factors through the
SHARED `%mr_product_factors` — which treats a `/` node as one opaque
factor. In this build `(3*x+2)^-8` stores as the `/` node
`1/(3*x+2)^8` (MEASURED: op = "/"), so the negative-power factor is
invisible; the scan finds no linear power and falls to plain `expand(u)`
— the denominator (3*x+2)^8 expands to the 9-term P8 and the six
monomial terms each hit the 1.4.2_r24 / 1.3.3_r4 re-dispatch -> loop
guard -> native integrate, ~5 s x 6 ~= 32 s. (Rubi's own
TrinomialParts accepts P8 — it only checks the top two and the middle
coefficient — so the r24 match is faithful, not a port bug.)

FIRST ATTEMPT (rejected): five edits incl. three to SHARED helpers
(%mr_product_factors, %mr_term_xexp/%mr_term_coeff, %mr_coeff3). Fixed
e1276 (DIFF = 0, 6.8 s) but regressed the broad canary 85/35 -> 84/36:
1.1.2.3 e294 PASS:verified -> FAIL:unverified; 1.2.2.8 e2
PASS:no-answer -> FAIL:error (`Control stack exhausted`, infinite
recursion); plus three fail-kind timeout -> unverified. Reverted
`git checkout` and reworked confined to the ExpandIntegrand-local
functions.

FINAL FIX (all maxima_rubi_utils.mac, all local to the ExpandIntegrand
path):
 1. New `%mr_ei_factors` — like %mr_product_factors but a `/` node splits
    into numerator factors + each denominator factor as a reciprocal;
    used ONLY by the %mr_ei_linear_power scan (%mr_product_factors and
    its other consumers are untouched).
 2. `%mr_ei_linear_power_at` "power" mode also reads a reciprocal
    quotient 1/(a+b*x)^m (num = 1, den a `^` node, m a positive integer,
    base linear); the rest-must-be-polynomial gate is unchanged.
 3. `%mr_expandLinearProduct` reads the shifted form through
    `r : rat(w)` and scales each coefficient by 1/den
    (`den : expand(denom(r))`, `L : %mr_coefficientList(expand(num(r)), x)`)
    — the .m CoefficientList[Expand[w], x] reading, which KEEPS the
    constant (x-free) denominator. The old `num(rat(w))` read dropped
    it: measured 243x answer error on e1276 (ratsimp DIFF numerator
    exactly 242 * the integrand numerator).

TWO STORAGE TRAPS measured while landing fix 3:
 - `together` is a NOUN in this build (op(together(x/2+x/3)) = 'together,
   with no preload) — `rat` is the combining step.
 - `denom(rat(…))` returns a gcrat object: `is(d = 243)` is true yet
   dividing by `d` (vs the literal 243) makes Maxima run the rat
   simplifier and EXPAND (3*x+2)^k to its polynomial, silently
   re-creating the P8-denominator form the fix exists to avoid;
   `expand(denom(r))` reifies the plain number.

BONUS (latent bug fixed by fix 3): 1.2.1.2 r20 calls
%mr_expandLinearProduct directly (v = (b/2+c*x)^(2*p), u = (d+e*x)^m,
a = b/2, b = c) under b^2-4ac = 0 / m-2p+1 = 0 / !integerp(p) — with
the quadratic = (b/2+c*x)^2/c the shifted form carries a constant c^m
denominator the old read dropped. Unit check (a = 1/2, b = 2, c = 2,
d = 1, e = 1, p = 3/2, m = 2, T := (d+e*x)^m*(b/2+c*x)^(2*p)): the new
read gives ratsimp(ELP - T) = 0, while the old read (same L, no /den)
gives ratsimp(ELP_old - 4*T) = 0 — off by exactly c^m. So any r20 fire
with c ≠ 1 previously produced an answer whose derivative is c^m times
the integrand; it is now Rubi-faithful. (The full-rubi DIFF = 0 probe on
that integrand ran through 1.2.1.6_r1's cascade, not r20 — rule order
reaches r20 only where earlier rules decline.) No broad-canary target
changed kind, so no corpus target's classification moved.

VALIDATION (Maxima 5.50.0 / SBCL 2.6.7):
 - 1.1.1.3 e1276: ratsimp(diff(F,x)-f) = 0 (answer = 6-term
   c/(3*x+2)^k sum); canary PASS:expected t=9.8 s (was FAIL:timeout).
 - e2 (1.2.2.8): PASS:no-answer t=7.5 s — baseline restored (no stack
   overflow, no timeout); e294 (1.1.2.3): PASS:verified t=6.1 s —
   baseline restored.
 - Broad canary (120 targets, --parallel 8): 85/35 -> 86/34, ZERO
   PASS->FAIL; the ONLY classification change is e1276
   FAIL:timeout -> PASS:expected; zero fail-kind changes elsewhere.
   `test/canary.broad.out` regenerated.
 - Layer A: 511/0, per-test lines byte-identical to baseline.

## Work item: Simp 2-arg port + 1.2.1.1 e1 silent-batch-kill investigation (2026-08-25)

Two coupled outcomes. (A) the Rubi `Simp[u_,x_]` 2-arg port was missing:
all 39 two-arg `%mr_simp(…, x)` call sites (32 rules: 1.1.1.4, 1.1.2.7,
1.1.2.9, 1.2.1.1, 1.2.1.2, 1.2.1.3, 1.2.1.5, 1.2.2.3, 1.2.2.4, 1.2.3.4,
1.4.1) fataled "Too many arguments" at repl evaluation — errcatched, so
the rules silently DECLINED. (B) activating r4 (1.2.1.1,
perfect-discriminant) moved e1 from the r5 ExpandIntegrand path to the
Rubi-faithful r4 product-decomposition path, whose cascade (1.1.1.2
r39/r38) surfaced a "silent batch-kill": rc=0, no error text, batch dies
at the next statement read, two `RETRIEVE: End of file encountered.`
lines.

Simp fix (COMMITTED THIS ITEM): `%mr_simp(e, [v])` — Maxima optional-arg
idiom (`[v]` collects the extra arg into a list, `[]` when absent —
MEASURED; distinct from the documented "no b... variadic" trap); the
arg is accepted and ignored, the 1-arg zero-chain runs (Rubi's 2-arg
Simp is a value-preserving NormalizeSumFactors — value parity is the
hard requirement).

The e1 "kill" is RESOLVED AS UNDERSTOOD, NOT CODE-FIXED. Measured facts
(this build, 5.50.0/SBCL 2.6.7):
1. The prompt is a DESIGNED input channel: the harness runs
   `batch_answers_from_file: true` (via -p preload — setting it inside
   the batch is too late, MEASURED) and pre-queues six `pos$` + six
   `no$` lines; retrieve() reads the next batch line as the answer.
   Under the driver, integrate returns assumption-conditional results
   the formal diff check verifies. In a batch with NO queued answers
   the first prompt hits input EOF — the uncatchable Lisp-level
   RETRIEVE death. Vanilla `integrate` on the same integrand dies
   identically (A/B'd): the kill is not a package regression.
2. The mr_top fb=true branches' BARE `integrate(f, x)` (no errcatch) is
   LOAD-BEARING: (a) an erroring integrate must PROPAGATE so the repl
   dies and the rule declines for the next rule; errcatching it bakes
   the no-answer noun into answers and regressed 5 targets (88/32 ->
   86/34, e.g. 1.1.4.3 e119 A/B'd: old true, errcatched false). (b) The
   seen-guard branch is the same bare call — productive loop
   resolution: e119's verified answer is BUILT from ten seen-guard
   integrate results; an ERROR there instead (decline) also regressed
   (same 88/32 -> 86/34, canary is deterministic — re-run of identical
   code gives 0 flips). `mr_int(f,x) := mr_top(f,x,TRUE)` — the
   fb=true branches run on EVERY nested sub-integral, not just the
   top-level fallback.
3. A no_questions-style noninteractive throw (maxima_rubi_ni.lisp,
   deleted) regressed harder: 88/32 -> 82/38, 10 expected->unverified —
   it suppresses the assumption-conditional answers the harness
   verifies (global even when toggled only around integrate: 82/38
   unchanged — the loss is in the integrate result itself).
4. Naming trap that masked all of the above for hours: lisp
   `$mr_ni_loaded` is the Maxima name `mr_ni_loaded`, NOT
   `%mr_ni_loaded` (that maps to lisp `|%mr_ni_loaded|`, never bound) —
   a "failing lisp load" was a broken witness test all along.

FINAL STATE: mr_top branches restored to HEAD (net code change this item
= the %mr_simp signature + measured-behavior comments in
maxima_rubi_utils.mac / maxima_rubi.mac). Broad canary 88/32,
PER-TARGET IDENTICAL to the pre-investigation Simp-baseline run (0
regressions / 0 improvements / 0 fail-kind changes); Layer A 511/0
byte-identical. e1 = FAIL:unverified (honest): the r4 path's answer is
the Rubi-identity hypergeometric form but fails Maxima's formal diff
under the queued assumptions — a RULE-QUALITY divergence (r4 path vs
the old r5 path that verified), tracked as a separate work item with
the wrong-answer family.

## Work item: broad-canary timeout targets — triage + harness zero-chain fix (2026-08-25)

14 FAIL:timeout targets. The timeouts were a VERIFICATION-cost problem,
not a package-speed problem: the 30 s per-target cap (test/canary.py)
conflated the package call (7.5 s on 1.1.1.6 e1, well within budget)
with the zero-chain verification of the answer.

NUMERIC TRIAGE (sweep: diff(mr_r, x) - mr_f evaluated numerically at
x=0.1, all-positive parameters, g/h added; /tmp/opencode/num_sweep*.py):
- numerically CORRECT (residual <= 3e-10): 1.1.1.7 e14, 1.1.2.4 e983,
  1.1.4.2 e182, 1.2.2.7 e1, 1.2.2.7 e17, 1.2.4.2 e119;
- diff() itself errors on the answer (noun-laden structure): 1.1.2.3
  e138, 1.1.4.3 e253, 1.2.2.8 e3;
- numerically NONZERO (wrong-answer family): 1.1.1.6 e1, 1.1.1.6 e31,
  1.1.1.7 e30 (residual = -integrand: the answer is a CONSTANT),
  1.2.1.3 e1058, 1.2.1.6 e1 (1.2.1.6 e1 later verified formally — the
  numeric miss was a domain/branch artifact of the test assignment).

ZERO-CHAIN ORDER DEPENDENCE (measured): no single stage order is
uniformly cheap — radical diffs close on factor in ~2 s where ratsimp
hangs >50 s (1.2.2.7 e1); 1.2.2.3 e1's expected-diff: 47 s
factor-first vs 9 s ratsimp-first; 1.2.2.4 e165's self-diff closes
only under the ratsimp-first order (ratsimp(expand(ratsimp(D))) = 0;
the same stages after a leading factor do not close).

FIX (committed 3c0451b, test/corpus_class1_driver.py + test/canary.py):
(1) zero_chain runs BOTH stage orders — factor-first chain, then
ratsimp-first chain (same errcatch-crash semantics; a crash is an
unverified zero-test, not a fatality); (2) build_text checks the
self-diff (zv) BEFORE the expected-diff (ze) — a non-closing
expected-diff (right answer, different radical form) must not starve
the cheap self-diff closure (1.1.2.4 e983 / 1.1.4.2 e182 timed out
under ze-first); "verified" and "expected" are both PASS classes, so
the reorder is classification-safe; (3) canary cap 30 s -> 60 s to
hold both chains (full-corpus driver stays 30 s for now).

BROAD CANARY: 88/32 -> 93/27, ZERO regressions, zero fail-kind
changes: +1.1.1.7 e14, +1.2.1.6 e1 (expected); +1.2.2.7 e1, +1.2.2.7
e17, +1.2.2.8 e3 (verified).

REMAINING 7 timeouts (60 s budget exhausted — all verification cost or
wrong answers, none package-speed): 1.1.1.6 e1/e31 (numeric nonzero —
wrong-answer family), 1.1.1.7 e30 (constant answer), 1.1.2.3 e138 +
1.1.4.3 e253 (diff errors on the answer structure — noun-laden),
1.1.2.4 e983 + 1.1.4.2 e182 (numerically correct; formal closure of
the self-diff exceeds 60 s — assumption-branch forms: the queued
prompt assumptions are cleared before verification, so the formal
zero-test needs sign info the chain can't derive — candidates for a
numeric-fallback stage or an assumption-aware verification).

## Work item: contains-noun sub-class (2026-08-25, committed 2a0ff92)

1.1.1.7 e30's "constant answer" is a faithful port, not a bug: its
cascade hits 1.1.1.4.m:47 — Rubi's OWN CannotIntegrate catch-all for
the 4-binomial family (ported as rule r42 whose repl IS the
`unintegrable` noun). Rubi 4 returns the inert Int there too; the
corpus expects a closed form the rule set cannot produce.

HARNESS GAP: such answers diff to a constant (noun heads evaluate to 0),
so the zero chains burn the budget and the target misclassifies
timeout/unverified. FIX: build_text checks freeof(unintegrable, mr_r)
(cheap, BEFORE the chains) and emits CLASS contains-noun (new FAIL
sub-class). POISON SET MEASURED: only `unintegrable` — an
`integrate[g, x]` head in an answer is a LEGITIMATE explicit integral
term (Maxima diff knows d/dx int(g,x) = g): 1.2.2.7 e1 carries a
integral term and VERIFIES; 1.1.2.3 e138 carries one too but its
self-diff does not close (separate open item, stays FAIL:timeout).

CANARY: 93/27 unchanged, zero regressions; 4 honest reclassifications:
1.1.1.7 e30 (timeout -> contains-noun, 6.8 s), 1.1.2.5 e46, 1.2.2.3
e165, 1.2.2.8 e1 (unverified -> contains-noun).

## Work item: wrong-answer family — 1.2.1.3 e1058 root cause (2026-08-25, committed a87fbc8)

1.2.1.3 e1058 `f = (2-5 x) x^(3/2) / sqrt(2+5 x+3 x^2)` (corpus
expects elliptic_f/elliptic_e). TWO package bugs found by bisecting
the r34 (1.4.1 Euler) cascade:

1. `%mr_substPower` (SubstPower port) fell through to `else u` on
   `sqrt(e)`: **sqrt is its OWN head in Maxima** (op = "sqrt", not
   "^") — SubstPower[., x, 2] left sqrt(3 x^2+5 x+2) untouched where
   r34's back-substitution needs sqrt(3 x^4+5 x^2+2) (quartic). The
   inner integrand was (2 x^4-5 x^6)/sqrt(3 x^2+5 x+2) instead of
   /sqrt(3 x^4+5 x^2+2). FIX: generic args() walk fallback (Rubi's
   Map semantics).
2. `%mr_term_xexp` / `%mr_term_coeff` had no "/" case:
   `expand(3/4*x^3) = 3*x^3/4` is a QUOTIENT node, so %mr_degree /
   %mr_expon of rational-coefficient polynomials returned the -1
   sentinel — the 1.2.1.6 r5 reduction (Expon/Coeff-driven) produced
   garbage nested integrands (measured: an r5 loop 15+ levels deep
   with coefficient 3^15 shrinking 1/9 per level).

DEAD-END AVOIDED: `subst` itself is NOT broken — an early probe
batch called it with the arguments reversed (subst(a, b, c) = "a for
b IN c"); all "subst is broken" evidence was a test-code artifact.
The 1.2.1.6-r1 degenerate-binding cascade (g=0 reading x^(3/2) as
(0+x)^(3/2)) is a red herring — family bisect (1.2.1.3, 1.2.1.6,
1.4.1) isolated the path to 1.4.1 r34's inner call.

HARNESS: zero_chain now leads with a two-point numeric stage (sweep
parameter values, x=0.35/0.65; per-point errcatch; `= true` coercion
— `is()` on a float-noun residual returns `unknown`, which ERRORS in
this build's if; diff materialized once in MR_de — ev over an
unevaluated diff(mr_r, x) substitutes x into the variable argument).
Stage builder is now programmatic (the hand-nested paren string
miscounted twice this session).

GATES: Layer A 511/0; canary 93/27 -> **109/11**, 16 FAIL->PASS,
0 regressions. Fixed: 1.1.1.4 e135, 1.1.1.6 e1/e31, 1.1.2.2 e428/
e910, 1.1.2.4 e983, 1.1.2.8 e1, 1.1.4.2 e182, 1.1.4.3 e253,
1.2.1.1 e1/e57, 1.2.1.2 e1036, 1.2.1.3 e1058/e2249, 1.2.1.5 e1,
1.2.4.2 e119.

REMAINING 11 canary failures: 4 contains-noun (faithful
CannotIntegrate markers — 1.1.1.7 e30, 1.1.2.5 e46, 1.2.2.3 e165,
1.2.2.8 e1 — documented, not bugs); 1 timeout (1.1.2.3 e138 —
answer carries a legitimate `integrate[g, x]` term whose formal
diff won't close; numeric stage declines on the noun); 6 unverified
wrong-answer/verify-gap candidates: 1.2.1.2 e2202, 1.2.1.4 e383,
1.2.1.5 e105, 1.2.2.2 e450, 1.2.2.2 e957, 1.2.2.6 e123.

## Work item: wrong-answer family — 1.2.1.2 e2202 root cause (2026-08-25, committed 2547162)

1.2.1.2 e2202 `(d+e x)^4/(a+b x+c x^2)^3` (resid 3.19/1.96). The
cascade (1.2.1.6 r4 p=−3 -> r4 p=−2 -> r1 p=−1 -> native integrate,
the last step verified correct) reduced to a broken 1.2.1.6 r4
reduction. THREE stacked predicate bugs:

1. BUILT-IN FRACTION PARTS: for a non-monic divisor with symbolic
   coefficients, `quotient`/`remainder`/`divide` return the parts as
   FRACTIONS — op(remainder((e x+d)^4, a+b x+c x^2, x)) = "/" with
   the symbolic content c^3 in the DENOMINATOR (Mathematica's
   PolynomialQuotient/Remainder return true polynomials). Fix:
   %mr_polyQuotient/%mr_polyRemainder/%mr_polyDivide expand() the
   result.
2. RAT CONTENT EXTRACTION: %mr_coeff3's `expand(num(rat(u)))`
   rescaled u — rat() puts the symbolic content below the line for
   symbolic polynomials, so num(rat(u)) was a c^3-scaled copy;
   coefficients came back c^3-wrong. Fix: `expand(u)` (Rubi's Coeff
   is Coefficient[expr,x,n] directly; Together only as fallback).
3. SYMBOL-POWER CONSTANTS DROPPED: %mr_term_xexp returned false for
   a power with an x-free base (d^2) instead of 0 — every
   symbol-power constant term vanished from coefficient walks
   (%mr_coeff(d^2 - a e^2/c, x, 0) lost the d^2). Fix: the ^ branches
   of %mr_term_xexp/%mr_term_coeff read an x-free base as a
   degree-0 monomial. Regression probe: the 1.2.1.6 r4 reduction
   identity, verified symbolically in general p for (e x+d)^2 and
   (e x+d)^4 (it was -d^2*qu^p / -d^4*qu^p before).

GATES: Layer A 511/0; canary 109/11 -> 111/9 (e2202 + 1.2.2.2 e450
-> verified, 0 regressions). Session total: 88/32 -> 111/9.

## Work item: 1.2.2.6 e123 false-arithmetic + branch-artifact targets (2026-08-25, committed 5cd442e, 6d6ef5d)

1.2.2.6 e123 `(4+x^2+3x^4+5x^6)/(x^2(3+2x^2+x^4)^3)`: answer carried
literal `false` factors. Root cause: 1.2.2.6 r8 (.m ILtQ[m/2,0]) fired
with m = -2 where x^m*Pq is LAURENT, not polynomial —
%mr_polyRemainder's `false` sentinel reached %mr_coeff, which returned
the boolean as the "coefficient"; Maxima keeps `126*false` as a factor
(booleans don't collapse to 0/1). The .m rule is vacuous at such
bindings in Mathematica (PolynomialRemainder stays a noun). Fix:
runner-level boolean-leak misfire check in %mr_dispatch
(%mr_containsBoolean, %mr_boolcheck kill-switch). Walk gotchas
measured: part()-reified false is an atom string-"false" unequal to
both the boolean and the symbol (string test only); control heads are
opaque (repls contain legal `else false` code — misfired e1058);
negation nodes crash on part(e,2) (descend part 1 only — its crash
silently derailed e1058 outside the errcatch). e123 now: honest
no-answer (expected answer needs an unported rule chain — coverage
gap, not a bug).

1.2.2.2 e957 + 1.2.1.5 e105: answers CORRECT but unverified — the
driver's fixed numeric-stage subs (a=0.7) give 4ac-b^2 < 0, sending
the float eval down the COMPLEX branch of branch-dependent answers
(resid 0.6-1.6 / exactly d). a=0.9 (4ac-b^2 = 0.11 > 0) -> both
verify (resid ~1e-16). 6d6ef5d.

1.2.1.4 e383 `x^3(d+e x)(a+b x^2)^p`: answer CORRECT (instance
residuals ~1e-17 at p = 2 / -3 / 5, measured 2026-08-25) but
unverifiable by the stage — free p -> float NOUN decline, and the
formal chain cannot close the p-dependent diff. Fixed by p = 2 in the
numeric-stage subs (instance check; p = 2 avoids the 1/(p+1) /
1/(2p+3) reduction singularities) — 5405f31.

GATES: Layer A 511/0; canary 113/7 -> 114/6 (e123 -> no-answer, e957
+ e105 -> verified, e1058 stays verified, 0 regressions) -> 115/5
(e383 -> verified, 0 regressions). Remaining canary FAILs are all
known/honest: 4 contains-noun markers (1.1.1.7 e30, 1.1.2.5 e46,
1.2.2.3 e165, 1.2.2.8 e1 — faithful CannotIntegrate) and 1.1.2.3
e138 timeout (legitimate integrate term, self-diff doesn't close).
The wrong-answer family is DONE. Session total: 88/32 -> 115/5.

## Work item: the five corpus-tested dead 1.2.1 sibling files (2026-08-25, committed e345c38 + ddc88ef)

Full-corpus prep exposed a generator key collision: key_of() keys .m
files by leading number; Rubi.m's LoadRules carries a DIFFERENT file
for five 1.2.1 numbers, so the loaded sibling won the key and the
corpus-tested sibling was silently never ported. The Maxima corpus
files name-match exactly five DEAD .m files (not in LoadRules):
1.2.1.3 (82 r), 1.2.1.4 (122 r), 1.2.1.5 (31 r), 1.2.1.6 (48 r),
1.2.1.9 (33 r) = 316 rules (2710 -> 3026). Ported under `b`-suffixed
keys, table position after the sibling. Also: a harness gap — a
top-level no-answer noun on an ANSWER-expected entry read as PASS
no-answer (T5's table only defines no-answer for noun-expected
entries); new FAIL class `deferred` (ddc88ef). 1.2.1.4 e1 was
deferred, now verified; family-A integrand (d+e x)^4(f+g x)^2/
(d^2-e^2 x^2) residual ~1e-14. Layer A 511/0 at 3026 rules. Other
dead class-1 files (1.2.1.7/1.2.1.8 siblings, 1.3.x x4, 1.1.2.x/.y)
have NO corpus file — unported until the run shows deferral that
needs them. Full 25,697-integral run in flight (12 LPT shards).

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

## Work item: matchfix name-ordered binding — 1.1.1.4 four-sqrt remap (2026-08-25, committed be729a6)

1.1.1.7 family triage (23/35 contains-noun in the in-flight full run).
e4's poisoned sub-integral (extracted from the `unintegrable` noun in
the answer): S = 1/((a+b x) Sqrt[c+d x] Sqrt[e+f x] Sqrt[g+h x]).
Traced: 1.1.1.7 r27's catch-all (FreeQ+PolyQ — fires in Rubi too, its
EqQ[m,-1] sibling .m:31 has the identical repl) decomposes P=(A+B x)
into rem/quot and must integrate S — so the divergence is in S itself.
Pinned Rubi 4 CANNOT integrate S: 1.1.1.4 .m:31 needs
GtQ[(de-cf)/d,0] (undecidable) and .m:32's Not[SimplerQ] guard hits
the SimplerQ atom tie-break — and OrderedQ is NEVER DEFINED anywhere
in the pinned clone (whole-clone + whole-git-history grep): upstream
bug; in Mathematica the tie-break is an unevaluated noun, the rule
declines, the .m:47 CannotIntegrate marker fires — the corpus was
generated by a Rubi build with a WORKING OrderedQ (its e4 expected
answer exists only if .m:32 fires). The corpus is the acceptance
target, so the sort() tie-break (the documented deviation) is the
corpus-target reading; a "faithful-noun" variant was tried and
reverted (it kills even the correct binding).

ROOT CAUSE: Maxima's matchfix binds commutatively-similar pattern
factors by VARIABLE-NAME order, not in-text order — ascending-sorted
pattern vars get descending-sorted target factors (three defmatch
probes; written order irrelevant, names decisive: the (g,h)-named
slot always receives the first target sqrt). The .m formula for S is
slot-specific: (c,d) is the Subst point — chain-rule difference
verified ~1e-19 iff (c,d) holds the .m-named first factor, ~1e-2
otherwise; (e,f)/(g,h) interchangeable (measured 2026-08-25,
invar5/invar6 probes).

FIX: generator CAP_REMAP — per-(key,rule) capture relabel so the
(c,d) slot's names sort last: 1_1_1_4 r28/r29 get
{c:g, d:h, g:c, h:d} (applied in cap_name, all emit paths funnel
through it). Pure relabel — formulas unchanged in value.
RESULTS: 1.1.1.7 e4 FAIL contains-noun -> PASS verified (12.1 s);
family run 13/35 verified (was 12); Layer A 511/0; broad canary
0/0 vs the true pre-remap baseline under the new driver
(canary_p2.out's 115/5 predates the deferred class — re-measured
baseline 71/49, all 49 pre-existing deferred coverage gaps, not
regressions). REMAINING 22 family fails are other shapes: e5 =
(a+b x)^-2 (r18 .m:23 LtQ[m,-1] rule's defmatch does not match the
integrand — matchfix backtracking, next probe), e18/e29 = quadratic
P — post-run family triage.

WORK ITEM: MatchQ marker name-shape scan -> load-time registry
(commit 6fab44f)
2026-08-25, 5.50.0/SBCL. The full run's 19 `error` entries
(1.2.1.6 e77/e78/e80/e84/e85/e87/e94 + 1.1.1.6 e42 + others) traced
to %mr_isMQMarker_name's char-by-char substring scan: the COMPILED
substring ERRORS on out-of-range (interpreted clamps — clamp.mac
probe: interpreted substring("ab",1,5)="ab", the same call in a
compiled (:=) errors; the length scan and the L-1 mq_hit probe both
go one past the end), and in the nested compiled context of a
matchfix defmatch the condition is FATAL — errcatch cannot catch it
(e77hb probe: no CLASS line, batch ends "RETRIEVE: End of file";
a shallower probe catches the identical error, so depth decides).
FIX: membership, not name-shape — the generator mints marker names,
so each rule file emits a trailing %mr_register_markers([...]) and
%mr_isMQMarker is a registry scan (utils registers its own 43
inline markers; Layer A registers its synthetic unit markers).
REVERTED along the way: a CL handler-case defmfun in
maxima_rubi_dispatch.lisp — an added defmfun is SILENTLY dropped by
load() in this build (call stays a noun; the file's two existing
dispatchers work; defmfun = (defprop + defun) per commac.lisp:254;
no load error is printed — cause not identified, documented in the
.lisp history only via this entry).
SECOND BUG, same symptom: the driver's sign-prompt budget (6 pos +
6 no per stage) — with the fatality gone the 1.2.1.6 cascade reaches
the integrate fallback, which asks 13-20 questions; an exhausted
stream EOF-kills the batch identically (e77n probe: N=12 dies,
N=20 completes). Raised to 40/20 per stage; exhausted budget now
degrades to `no` answers, not death.
PARSE QUIRKS measured (test-file edits): block-body statements are
COMMA-separated — a $ mid-body breaks the parse; a (:=) definition
line caps at ~256 chars (longline probes); top-level .mac lines
carry 700+ chars fine.
RESULTS: the 8 formerly-erroring entries: 7 PASS verified (e80 a
pre-existing 60 s timeout); Layer A 511/0; broad canary 71/49,
0 regressions / 0 improvements vs canary_pre_remap.out (canary_cmp).

WORK ITEM: e5-class diagnosis completed — matchfix limit, not a
rule-set gap (probe probes/rubi/01-1114-e5-gap-census.py, doc
corpus-baseline.md §4.1)
2026-08-25, 5.50.0/SBCL. The static census of the pinned .m
1.1.1.4 (48 rule runs) shows the e5 shape (a+b x)^m/(Sqrt Sqrt
Sqrt) IS covered: the LeQ[m,-2] rule (probe class A4; ported as
1_1_1_4 r32, cond integerp(2*m) and is(m <= -2)) plus its GeQ[m,2]
twin — the "version gap" hypothesis of the previous session is
retracted (the corpus expectations match the pinned rule set).
The deferral is the matchfix pattern limit: free-exponent power
factor + sibling fixed-FRACTIONAL-exponent or Sqrt factor never
matches (r32fix/r32bis/pq probes: A=false, B=false, P4=false,
Q1=false, Q4/Q5=false; all-fixed P1=true, free+free P3=true,
fixed-integer-in-denominator Q3=true — same family as the r18
finding of the OrderedQ work item). Fix = custom matcher for the
m/(Sqrt Sqrt Sqrt) shape and the sibling permutation rules
(r20/r21/r22/r24/r27/r34); scoping deferred to the clean full
run's failure count on this pattern family.

WORK ITEM: 1.1.1.4 e99 diagnosed — Group-2 sqrt(linear/linear) open
family (post-run batch triage)
2026-08-25, 5.50.0/SBCL. e99 = (a+b x)^(1/2)*sqrt(c+d x)/(sqrt(e+f
x)*sqrt(g+h x)); canary: FAIL contains-noun. Trace (rubi_verbose):
fires 1_1_1_4 r30 (the elliptic-Subst .m:28 rule — the right rule),
then r25/r36/r33 on cascade sub-integrals; the answer = elliptic_e +
elliptic_f terms + a residue term subscript(unintegrable, ...) whose
content is a sqrt(linear/linear) product — the SAME shape family as
the 1.1.1.7 Group-2 P-shapes (P6/P8/P11/P13/P21/P22/P31/P32/P33):
the 1.2.x cascade reduces the Subst integrand
1/((h-b x^2)*sqrt(1+c x^2)*sqrt(1+d x^2)) down to a
sqrt(linear/linear) product for which NO class-1 rule exists in the
current table. Numeric sanity (e99z8 probe): the residue is a
genuine nonzero sub-integral (W1 = 3.85e-44 * 'unintegrable[...]'
term — the diff does not close because of it). Family-level triage
(which 1.2.x rule emits the sqrt(linear/linear) form, and which .m
rule owns it — candidates 1.1.3.3 / 1.1.1.2) deferred to the
post-full-run batch; e99 joins that family's ticket, it is not a
standalone bug.

WORK ITEM: manual structural matcher for the free-n binpow family
(1.1.3.3 / 1.1.3.1) — implemented, gated, committed c109cf4
2026-08-25, 5.50.0/SBCL. matchfix cannot match (a + b*x_^n_): it
binds (a + b*x^3) degenerately as n := 0 with B := b*x^3, and the
freeof(x) predicate that kills the degenerate binding kills the
whole match (no backtracking) — probes n1133/n1133b. The 32 class-1
rules of the shape (26 in 1.1.3.3, 6 in 1.1.3.1) declined every
integrand. Generator now detects the whitespace-free .m shape
(_binpow_factor / binpow_manual_match) and emits a rule that calls
the structural matcher %mr_mbp2 (utils) and builds the matchlist
itself, trying the canonical and swapped factor-to-slot
assignments. Five 5.50.0/SBCL build quirks measured and honored:
op() on an atom is FATAL (atom()-guarded); op(t)="sqrt" never
evaluates in a compiled if (string(op(t)) test); return() inside a
for-loop is LOOP-level (flag + is() bail-outs); `var = false` stays
unevaluated in a compiled if (is() comparisons); a bare
`if ... then false else ...` as a block value evaluates to
UNDEFINED (assign-to-res idiom). The first draft silently dropped
non-matching factors inside the for-loop (the loop-level return
never escaped) and misfired on 1.1.1.5 e1 / 1.2.1.3 e2249
(canary 2 regressions) before the rewrite. Gated: Layer A 511/0,
broad canary 71/49 = baseline (0/0 vs canary_pre_remap). e4
(1.1.3.3 smoke) now verifies. The 3+-factor free-n families
(1.1.3.2/4/6/8, 1.2.3.x, 1.4.x — 922 rules) need the N-factor
matcher extension: deferred to post-run triage on the full run's
failure data. NOTE: the clean 12-shard full run started before
this fix is now MIXED-state (entries started mid-fix see the
buggy matcher) — restart it clean after the 1.1.3.3 family run.

WORK ITEM: %mr_polyDivide contract fix — committed 9279f9f
2026-08-25, 5.50.0/SBCL. Rubi PolynomialDivide[u,v,x] = quo + rem/v as
ONE expression; the 8 class-1 repl call sites do mr_int(that, x). The
old port returned [Q, R] — integrating a list (garbage). Measured
consequences: (1) Maxima `divide(u, 1/w, x)` is broken in this build
(it multiplies by w and drops the remainder — the "remainder" came
back b*d*x^6+(a*d+b*c)*x^3+a*c); (2) this build's expand distributes
a sum over a denominator term (x + (1-x)/(x^2+1) -> -x/(x^2+1) +
1/(x^2+1) + x) — so the port returns the UNEXPANDED Q + R/v. New
Layer A test checks the identity u = v*PolyDivide[u,v,x] (syntactic =
fails on sum-term canonical order). e5 (1.1.3.3, (a+b x^3)/(c+d
x^3)) verified, resid 5.5e-17. Gated 511/0 + canary 71/49 (0/0).

WORK ITEM: AppellF1 corpus-head fix — committed 9c87a3f
2026-08-25, 5.50.0/SBCL. translation_table mapped AppellF1 ->
mr_appellf1 (unbound) while the corpus expected answers carry the
AppellF1 head; mismatched heads never cancel in the zero-test. Now
emits AppellF1 (identical answer -> identical nouns -> diff closes
symbolically to 0). Measured build quirk: this build's diff KNOWS the
bracket-list form AppellF1[...] (= AppellF1 applied to a list) and
SILENTLY DROPS its x-dependence (diff(AppellF1[...,-b*x,...],x) = 0;
diff(e1 + x^2, x) = 2*x) — the parenthesized form stays a noun diff
(no false closure). FOLLOW-UP: driver-side normalization of the
corpus's AppellF1[...] -> AppellF1(...) in the inlined expected text
(latent hazard; only matters once AppellF1 answers verify). Gated
511/0 + 71/49 (0/0). 5 rule files regenerated. The in-flight full run
kept running (only AppellF1-answer entries affected; census usable —
recorded as mixed-state caveat).

CONTEXT (measured): the corpus suite is pinned at 60295e2 (2018-10-25,
predates our pinned Rubi 61e9c18); its expected answers for
free-exponent entries (e.g. 1.1.3.3 e34: (a+b x^3)^m (c+d x^3)^p ->
AppellF1) are produced under conditions our faithful port cannot
decide symbolically (r61 cond IntegerQ[m]||GtQ[a,0] is false for
symbolic m even in Mathematica) — the 97 1.1.3.3 deferred entries are
a suite-generation vs faithful-port gap, not a rule bug. Triage
decision pending the full-run census.

2026-08-25 (5.50.0/SBCL): SLOT-MATCHER HYBRID + BOOLEAN MATCHLIST GUARD
+ NORMALIZATION-SEEN GUARD. The bare-factor wall (probe 89e8b22: a
free-exponent slot (lin)^pm declines a bare (lin) target; (lin)^1
re-canonicalizes so no explicit unit exponent exists on the target
side) is fixed for the 1.1.1.4/5/6/7 families by a HYBRID rule: the
defmatch path is unchanged and tried first; on decline the structural
fallback decomposes the integrand with %mr_binpowfactors (78b8095)
into [c, M, rest, L-factors] and a generated _mr_slots backtracker
assigns factors to the .m slot model (binpow/monom/barevar/polypow/
quadvar) with backtracking + shared-n equality + the .m condition on
bound values. 1_3_2 was expected to join but its pattern (P_^p_*Q_^q_.)
parses no slot (P/Q are polypow with the exponent INSIDE the base
pattern — parser returns None — defmatch-only for now). MEASURED:
1.1.1.4 e1/e2 went timeout->deferred/error (the bare wall is GONE:
r1 now fires on the 4-bare-linear target and returns the expanded
polynomial antiderivative; the residual gap is the cascade coverage
of the expanded sub-integrals — e2's symbolic form also runs a bare-
integrate prompt flood that exhausts the 60 queued answers: RETRIEVE
EOF). NEW BUG CLASS FOUND + FIXED (all 3026 rules regenerated): this
build's defmatch BINDS UNFILLED PATTERN SLOTS TO `false` (1.1.1.7 r25
Px*(lin)^m*(lin)^n*(lin)^p*(lin)^q on a 3-factor target: freeof(x,
false) = true sails the .m condition; the repl rebuilds
(false*x+false)^false garbage whose own mr_int sub-dispatch re-fires
r25 with fresh false bindings — an unbounded cascade the result-level
leak check only catches after stack exhaustion, measured: SBCL
"Control stack exhausted" on 1.1.1.4 e1, 2.5M-line trace). FIX:
every generated rule body now rejects matchlists containing a boolean
(%mr_containsBoolean(mm) before the cond; the hybrid variant is
mm # false and ... so a legitimate declination still opens the
fallback). SEPARATELY: the seen guard (mr_top) was exact-member only
and missed the measured float/rat normalization cycle
((104*(3/10*x+17/10)^4)/3 vs (104*(0.3*x+1.7)^4)/3: member false,
is(f2=f1) false, ratsimp(f2-f1) = 0) — the r25/r7 chain walked it
lap after lap; %mr_seenp now ratsimp-compares against the dispatch
path (O(depth<=16) ratsimps; errcatch per probe-errcatch-semantics:
[value]/[]). BUILD QUIRKS MEASURED THIS SESSION: (1) redefining a
function that captured the old function via `g0 : g` INFINITELY
RECURSES (the capture re-resolves to the new definition at call time)
— never wrap-override a package function in a probe; (2) `for s :
list do` / `for s from list do` HANG in this build — use the
indexed `for i : 1 thru length(L) do part(L, i)` idiom. CANARY:
69/51 vs 71/49 baseline — the 3 diffs are NOT attributable to this
change: 1.1.1.7 e1 (verified->noun) reproduces on the LAST COMMIT
(stash-tested; the corpus expected answer is also COMPLEX-valued:
realpart(diff) = 18.98 at x=0.35, so it can only have closed
symbolically via a radical-form identity under earlier code),
1.1.1.4 e135 (verified->unverified: the new answer is NUMERICALLY
correct, V1/V2 ~ 1e-16, the zero chain just no longer closes the
different radical form), 1.1.1.4 e1 (deferred->timeout: the fallback
cascade takes ~190 s > the canary's 60 s cap). GATED 511/0. The
in-flight 12-shard full run saw the regenerated files mid-run
(mixed-state caveat #2 — the final clean re-run remains planned).

## Work item: slot-matcher fallback — the four build traps + consumption check (2026-08-26)

The hybrid fallback from 9f5ccef was verified BROKEN end-to-end
(r1 on 1.1.1.4 e1 returned false; e3/e4/e5 "verified" came from
OTHER rules). Root causes, all MEASURED this session
(probes in /tmp/opencode: retprobe, jtest/jtest3, forif, mapprobe,
forcnt, termclean/termpois, remcmp/remmap2-4, remg, e2slots2,
bttrace/cleantrace, consump):
(1) return() inside a for body terminates the LOOP and its value is
DISCARDED — the backtracker's `if is(r2 # false) then return(r2)`
was dead code; rewrote as r2-flag + next-iteration guard
(`if is(r2 = false) and is(member(i, used) = false) then (...)`)
with the branch ending in a BLOCK-level return(r2).
(2) `if C then <value>, NEXT` in a block SWALLOWS NEXT into the
then-branch (whole j-chain collapses to the tail value);
`if C then <statement>, NEXT` separates correctly — every j-group
must END IN A STATEMENT (hence the return(r2) placement).
(3) A DECLINED defmatch that PARTIALLY matched commits its capture
bindings as GLOBALS (3/1-quotient shape: 3 slots bound, 4th
unmatched): the fallback's acc equations then auto-evaluate
(`_mr_.._a = 1.1` -> `1.7 = 1.1`), geteqR finds no capture, cond
degrades to unknown, every terminal declines. Fix: unquoted
`remvalue(name)` per capture at the top of the fallback — quoted
remvalue('sym) does NOT unbind in this build, and
map(lambda([v],remvalue(v)),[sym]) evaluates the argument to its
value first (both measured). This also explains the apparent
"pool-order dependence": it was call-order pollution from a prior
cascade's defmatch.
(4) FULL-CONSUMPTION CHECK: without it a k-slot rule's fallback
accepts any integrand containing a valid k-factor subset — a
4-slot 1.1.1.4 rule fired on a 5-factor 1.1.1.7 e14 quotient and
integrated the wrong integrand (canary PASS->FAIL). Terminal now
requires is(length(used) = length(pool)) = true.
REVERTED: the sqrt-product _slot_factor branch (1.1.1.7 r16-class)
and 1_1_1_7 from SLOT_KEYS_PHASE1 — the 1.1.1.7 hybrid fallbacks
returned a WRONG answer on the symbolic m/(sqrt sqrt sqrt) cascade
(V1 = 0.48, /tmp/opencode/e17v; driver e1/e2 150 s timeouts,
e17drv) and canary e1/e14/e30 regressed; 1.1.1.7 is back to
defmatch-only (baseline behavior). Revisit with a cascade budget.
NOTE: 1.1.1.7 e1's verified->timeout also reproduces on the last
pre-slot-matcher commit (prior session's stash test) — pre-existing
since ~78b8095, separate from the slot work; still open.
GATES (post-revert + consumption): Layer A 511/0; canary 71/49 =
BASELINE, with 1.1.1.4 e1 FAIL->PASS (deferred->verified, the only
improvement) and 1.1.1.4 e135 verified->unverified (the known
artifact: answer numerically correct V1 -1.18e-16, zero chain no
longer closes the different radical form). 1.1.1.4 driver 6/6
verified; 1.1.1.5 3/4 (e4 deferred); 1.1.1.6 4/4. Committed 93e3fa0.

CONTINUATION (2026-08-26, committed 98b8036): the first 12-shard
full run COMPLETED 25697/25697 (mixed-state — 9f5ccef landed
mid-run; numbers below are directional, not acceptance): pass
14282/25697 (55.6%), by class verified 14220 / deferred 10488 /
timeout 461 / unverified 340 / contains-noun 109 / expected 34 /
no-answer 28 / error 14 / unexpected 3; T3 baseline was 12,798
verified+expected, so uplift ~ +1,456. Top failing families
(mixed-state): 1.2.1 Quadratic 3575, 1.1.3 General 2577, 1.1.1
Linear 1508, 1.1.2 Quadratic 1266, 1.2.2 Quartic 643, 1.2.3 General
689, 1.3.2 590. UNVERIFIED triage (correctness): sampled entries
are mostly zero-chain artifacts (1.1.1.3 e799 V1 2.2e-15, 1.1.3.2
e826 V1 -2.2e-15 — answers numerically correct, chain doesn't close
the elliptic/atanh form); 1.1.1.7 e1 (the earlier regression)
VERIFIED again in the driver (25.2 s) once the 1.1.1.7 hybrid was
reverted — it was the hybrid's, not a pre-existing, fault. 1.3.2
e151 class (x^2 (a+b x)^n (c+d x^3), n symbolic) = genuine pinned-
Rubi-4 rule-set gap (no rule covers linear-free-n times cubic-free-p;
the corpus's expected answer predates the pin — same class as the e5
gap). NEW BUG FIXED along the way: the walker classifies ANY
(A+B x^n)^E as an L entry (needed for 1.1.3 free-n), so a cubic
(0.5+0.9 x^3) came back [0.5,0.9,3,1] and would fill a linear
phase-1 slot on an E match (wrong-integrand risk); the fallback pool
loop now tracks linok and declines on the first n # 1 L factor.
ALSO: 1.1.1.5 e4 (cubic P / sqrt, P in rest) triaged = legit .m
cond declination (rule-set gap, defmatch matched clean); 4 hung
Maxima probes from prior sessions (4-34 h elapsed, timeout wrappers
defeated) were found eating CPU and killed. FIRST full2 re-run on
93e3fa0 was killed at ~1.5 h when the linok regeneration made it
mixed-state again; DEFINITIVE full2 relaunched 2026-08-26 05:00 UTC
on 98b8036 (12 shards, /tmp/opencode/full2/), ETA ~7 h. Gates at
98b8036: Layer A 511/0; canary 71/49 = baseline + 1.1.1.4 e1
FAIL->PASS (same single e135 artifact as before).

## Work item: option-D rules core + cost-aware 24-shard planner + final clean full run (2026-08-26, committed 3ff58bd + 85b7585)

RUN 3 COMPLETED (correction to the relaunch note above: the definitive
full2 used the committed planner's N_SHARDS = 18 — the "(12 shards)" was
stale text carried from the first full2 attempt): 18 count-balanced
shards, 2026-08-26 05:00 -> 18:12:09 UTC, 13.2 h wall (the ~7 h ETA was
for balanced shards; count balancing on the load-bound run left a ~2.1x
spread). Merged 25697/25697 rc=0 (test/full_run3_merge.out):
Results 16103 passed / 9594 failed — verified 16041 / expected 34 /
no-answer 28 PASS; deferred 8671 / timeout 438 / unverified 359 /
contains-noun 111 / error 12 / unexpected 3 FAIL. Entry-time total
249,000 s (avg 9.69 s/entry; ~6.2 s of it the per-entry rule load — one
fresh maxima process per entry, so EVERY entry paid the full load).
Both attack costs (load tax + imbalance) motivated the harness rework
below; both commits are test-only (test/ + .gitignore + probes/ — zero
package code), so the package under test is unchanged from 98b8036.

Option D (3ff58bd) — preloaded rules image:
- test/build_rules_core.sh: loads package + all 72 class-1 files (3026
  rules) under --tls-limit 100000, resets maxima::*maxima-started*
  (a missing reset prints a spurious "Maxima restarted." on every
  restore — measured), saves with :toplevel cl-user::run (mechanism per
  the installed core, maxima-build.lisp:24) + a fingerprint sidecar
  (md5 over maxima_rubi.mac / maxima_rubi_utils.mac /
  maxima_rubi_dispatch.lisp / rules/class1/*.mac, C-locale-sorted
  relative paths; clean-tree value
  5998e8712f69f016a2baa67efc0c546c). Core 153,841,824 B; build ~8 s.
- Driver (USE_RULES_CORE): state off|on|stale|missing; stale ->
  auto-rebuild (flock single-flight); fallback to the standard load on
  build failure; MR_RULES_CORE=0 escape hatch. Clean launch form
  (MEASURED): `sbcl --tls-limit 100000 --core <core> --noinform
  --very-quiet -b <file>` — NO --eval: the image's saved toplevel IS
  cl-user::run, and the stock wrapper form leaks sbcl meta-args into
  maxima's arg parser (spurious "argument eval not recognized").
  Restore 0.03 s; driver entry via core 0.02 s (vs ~6.2 s load).
- probes/image/probe-rule-image.run (+.out) -> VERDICT OK
  (TABLE_AT_BUILD/RESTORE 3026; rubi(x^3,x) = x^4/4; rubi(1/x,x) =
  log(x)). Staleness guard exercised end-to-end: mutate a rule file ->
  stale -> auto-rebuild 8.2 s -> on, byte-identical restore.

Cost-aware planner (85b7585):
- test/launch_class1_shards.py: N_PROCS = MR_N_PROCS or os.cpu_count()
  (24); per-entry cost from run 3's merged .out (entry_cost =
  max(t - 6.2, 0.05), 3.5 s fallback when no measurement); files over
  the per-proc target split into contiguous chunks; LPT packs chunks +
  whole files (one chunk per proc). Plan: 24 jobs, balance spread 1.03x
  (count balancing was ~2.1x), max job estimate 3847 s, total estimate
  89,652 s; coverage-verified (all 25,697 keys, 0 dupes/missing/extra).
- Driver: the shard file now accepts `idx skip per` chunk lines
  (backward-compatible with bare `idx`). Merge script: shard count
  from the .files glob (was hardcoded 18). wait_and_merge.sh /
  status_logger.sh path-portable + shard-count-generic.
- PARITY GATE (120-target broad canary, core vs standard, --parallel):
  ZERO classification diffs (71 verified / 43 deferred / 4
  contains-noun / 1 unverified / 1 timeout; ~10x faster on core).
  Pre-existing flaky note: 1.2.1.6 e77 (prompt-heavy) fails IDENTICALLY
  on both paths — the cascade exhausts the queued pos/no answers ->
  RETRIEVE EOF, no CLASS line. Not D-specific; named, not fixed.

FINAL RUN (rules core, 24 procs, cost-balanced; 20:24 -> 21:11 UTC,
46 min wall vs run 3's 13.2 h): 25697/25697 merged OK
(test/full_core_merge.out, rc=0). Results 16103 passed / 9594 failed.
Category delta vs run 3: timeout 438 -> 433, unverified 359 -> 362,
error 12 -> 14; the other SIX classes IDENTICAL (verified 16041 =
16041). Reading: with the 6.2 s load out of each entry's 30 s budget,
5 borderline timeouts finish (3 unverified, 2 error) — no semantic
movement anywhere. Entry-time total 45,275 s (avg 1.76 s) = 5.5x run 3;
wall 17x. Heaviest shard 2752 s wall vs the 3847 s estimate (model
conservative, as intended).

ERROR SET CHURN (12 -> 14): stable 8 = 1.1.1.2 e1723, 1.1.3.4
e156/e164/e172, 1.2.1.2 e2530/e2537/e2538, 1.2.2.3 e111; gone from run
3 = 1.2.1.2 e2531/e2544, 1.3.2 e870/e871; new = 1.1.1.2 e1700/e1702/
e1712, 1.2.1.2 e1163/e1165/e2545. Maxima lisp errors in deep
evaluation, partially timing-sensitive (not rule mismatches) — the
triage list is the 14 above.

Build quirk (measured, recorded nowhere else): string + concatenation
is a NOUN in this build ("A "+"B" -> B + A); only concat() works (the
driver / package already use concat).

GATES: Layer A 511/0 (re-measured on 85b7585); canary parity zero-diff;
merge completeness OK. Acceptance record: docs/corpus-baseline-uplift.md.
Run artifacts (test/corpus_class1.shard*, pids, run_status.log) remain
untracked/disposable; the merged record (test/corpus_class1.out) and
its transcript (test/full_core_merge.out) are committed.

---

## matchreverse pass-2 rescan — the (c x)^m factor-order fix (run 5)

User direction 2026-08-27: fix the remaining failures; the corpus's own
4th element is the reference (25,666 of 25,697 should integrate; 31 have
a noun as reference answer — 11 CannotIntegrate + 20 Unintegrable, 7
files).

ROOT CAUSE (measured, probes in-session): Maxima's commutative product
matcher, for a pattern factor with a non-atomic base, picks the FIRST
^-factor of the target in the REVERSED stored-factor order, with NO
backtracking (matrun.lisp findfun; gated on the lisp global
matchreverse, nil = reverse the factor scan). A defmatch port of a Rubi
rule whose product pattern carries a monomial-power factor (c x)^m
therefore 0-fires whenever the monomial power is NOT stored last —
Maxima's canonical sort, data-dependent. Measured: (_c*x)^_m*_r matches
(d*x)^m*(c+e*x)^3 iff the monomial power sorts last (PB/PC probes);
the two-power-factor shapes (1.1.3.x / 1.2.x (c x)^m classes) are dead
on a data-dependent subset. Not a storage-distribution issue (the corpus
has zero (product*x)^integer factors — 0 of 25,697; the 7,774 loose
regex hits were all sum bases, which Maxima keeps as powers), not a
§9.1 gap, and matchreverse is unreachable from Maxima level in this
build (defmvar; assigning matchreverse in Maxima leaves the lisp global
NIL — measured).

FIX (3 files, additive): maxima_rubi_dispatch.lisp gains
%mr_dispatch_rev (defmfun |$%MR_DISPATCH_REV| — &rest, since fixed-param
defmfun is not callable in this build, and ALL-UPPERCASE, since an
all-lowercase Maxima name's canonical lisp symbol is uppercased; both
measured, see the file comments) that sets matchreverse, rescans the
whole table via the mlambda call primitive, and restores it in
unwind-protect. mr_top (maxima_rubi_utils.mac) runs it ONLY after a
TOP-LEVEL (fb=false) 0-firing — nested 0-firings keep the integrate
fall-through, pass 1 is bit-identical, so nothing currently passing can
regress. maxima_rubi.mac witness extended to call it (empty table ->
false).

GATES (all green): Layer A 511/0; 120-target broad canary 77 pass / 43
fail vs the run-4 split 71/49 — per-target A/B: all 71 previously
verified STILL verified, 6 deferred -> verified, ZERO regressions.
1.2.1.2 family A/B (2,590 entries, 8-way parallel): 617 deferred ->
verified, 0 regressions, PASS 1453 -> 2071.

RUN 5 (rules core rebuilt, fingerprint f1deb0c9..., 24 procs; 2026-08-26
22:45 -> 2026-08-27 00:38 UTC, 113 min wall vs run 4's 46 min — pass-2
doubles the 0-fire cost and the new answers add verification time):
25,697/25,697 merged OK. Results 18,588 passed (72.3%) / 7,109 failed,
vs run 4 16,103 (62.7%) = +2,485. Categories: verified 16,041 -> 18,503
(+2,462), expected 34 -> 57 (+23), deferred 8,671 -> 5,655 (-3,016),
unverified 362 -> 595 (+233), timeout 433 -> 701 (+268), contains-noun
111 -> 138 (+27), error 14 -> 17 (+3), no-answer 28 / unexpected 3
unchanged. Entry-time total 64,018 s (avg 2.49 s vs 1.76 s).
Transition matrix: 16,040 verified->verified; the ONLY pass->fail flip
is 1.2.1.2 e92 verified->timeout — a 29.4 s borderline entry (0.6 s
under the 30 s cap in run 4); re-run under the canary's 60 s budget
verifies in 17.5 s quiet: load-sensitive borderline, not semantic. ZERO
semantic regressions.

KNOWN REMAINDER: the +233 unverified / +268 timeout / +27 contains-noun
are all FAIL->FAIL (a rule now fires where there was a noun; the answer
then fails the zero-chain, usually radical-form closure, or burns the
30 s budget). They are the next quality work-stream (verification-chain
forms + per-entry budget), not a defect of this fix. Top recovery
families: 1.2.1.3 +641, 1.2.1.2 +617, 1.2.1.4 +229, 1.1.3.2 +190,
1.2.2.4 +159, 1.2.1.9 +155, 1.1.2.4 +96, 1.1.3.4 +87, 1.3.2 +60.

Uplift vs the T3 integrate() baseline (12,798 verified+expected, 49.8%):
18,560 (72.2%) = +5,762 (+22.4 pp).

UNEXPECTED TRIAGE (the 3 of 3, all 1.1.2.5 e103/e107/e110 — the "Not
sure this is not integrable" corpus entries): the user asked whether
they verify. No — the full zero chain (both stage orders) does NOT
close on any of the three, by construction: our answer is the pinned
Rubi's own partial reduction. Rule r30 (source rule 31, the p<0,q>0
triple-quadratic reduction d/b*Int[..^(p+1)..^(q-1)..] + (bc-ad)/b*
Int[..]) fires; its two nested sub-integrals are uncovered (the
dedicated Sqrt-form rules cover only p=1/2, these are p=3/2) and fall
to the file catch-all (source rule 40, Unintegrable marker = our r39).
Port completeness re-verified on 1.1.2.5: source has 40 Code cells =
39 live rules + 1 COMMENTED-OUT rule (the front-end keeps a disabled
duplicate of the PosQ[d/c] elliptic-pi rule); the port has 39 = all
live rules, r38 = source 39 (ExpandIntegrand/SumQ), r39 = source 40
(catch-all). The 2018 corpus says Unintegrable because the 2018 Rubi
pre-dates the r30 reduction (corpus steps=0); the pinned 2026 Rubi
returns the partial reduction + markers — neither version has a closed
form. So: not false answers, not verifiable, faithful to the pin.

Driver fix (corpus_class1_driver.py): the noun-reference branch
classified "not a top-level noun" -> unexpected WITHOUT the interior
freeof(unintegrable, ...) check (that check only ran in the
non-noun-reference branch), so interior-marker answers misclassified.
Now: noun -> no-answer; interior marker -> contains-noun; else
unexpected. Both reclassifying classes are FAIL, so PASS counts are
unaffected; the 28 no-answer PASS entries re-verified unchanged
(1.1.2.5 e112/e115 spot-checked).

## Work item: Phase A implicit-1 matcher fix + Phase B section-9.1 port (2026-08-27)

Two work-streams closed in one session: Phase A (the Maxima-vs-
Mathematica power-storage gap) and Phase B (the legacy 9.1 Integrand
simplification rules, dropped from the pinned Rubi.m's LoadRules in
2023-12, hence a manual port).

PHASE A (maxima_rubi_implicit1.lisp, uncommitted): Maxima strips a
power's exponent 1 at construction and the match compiler hard-rejects
a top-level MEXPT pattern against a bare target (measured: x^pm vs x
-> false; (a+b*x)^pm vs (a+b*x) -> false; the factor path finds only
explicit mexpt factors). Fix: a findfun shadow, gated by
*mr-implicit1-active*, that wraps the first eligible non-mexpt factor
in a raw (MEXPT f 1) when the original search 0-fires; the emitted
(mquotient e (car p)) division strips F with the bound exponent.
Single-candidate semantics inherited (no backtracking added). The
shadow is active ONLY in the top-level pass-3 rescan (mr_top,
fb=false, after passes 1-2 0-fire): nested mr_int dispatches run with
the gate off (unwind-protected), so nothing currently passing can
change. GATES: Layer A 511/0; canary broad 120: 85/35 vs run-5 77/43;
per-target A/B vs run-5: 120/120 matched, ZERO regressions, 8
improvements (all deferred->verified).

PHASE B (rules/class1/9_1.mac, uncommitted): 29 rules (r1-r29, source
L4-L35) appended at the END of mr_rule_table (faithful file order).
Structural ports where the matcher cannot express the .m pattern:
r13 const-factor split (a_*u_ fills the unfilled factor slot with 1),
r15 monomial-power x sum ((c_*x_)^m_*u_ 0-fires systematically —
p6.out). r17-r25 dead in Maxima (shared-v power slots return clean
false), ported 1:1 as zero-fire. MEASURED regression fixes (the
degenerate-binding class — the matcher's 0-fill on short sums has no
Mathematica equivalent):
 - r1 (L4): plus-pattern vs atomic base binds v := 0 (zero-fill) ->
   self-repl loop; guard is(v # 0).
 - r2/r3/r5/r6 (L5-L9): the .m's purpose (a stored base with a
   literal 0 term) is UNREPRESENTABLE — Maxima simplifies it at
   construction. The only reachable reading is the degenerate
   atomic-base one (measured on the 1.4.3 r19 T4-cascade sub-integral
   x^(n-1)/(2e), reverse scan: a := e, b := 0, n := 0 — cond passes,
   repl is the integrand verbatim, and the firing blocks the
   load-bearing native fall-through on mquot sub-integrals the family
   0-fires). Guard is(op(base reconstruction) = "+") on all four.
 - r4 (L7): the .m's repl is the stored integrand verbatim on its
   only reachable shape (measured: (2 x^2 + 3 x)^2 binds a := 0,
   b := 3, n := 1, c := 2, j := 2) — a loop in the .m world too
   (CannotIntegrate residue); here the equivalent rescue is the
   pass-3 lift, which a pass-1 terminal would block -> the rule
   DECLINES (false).
 - r11 (L14): -u_ on a positive target synthesizes u := -f as a UNARY
   MINUS NODE (op "-"), not mtimes(-1, f) — the original op(u) # "*"
   guard missed it; cycle via the -f re-dispatch; guard op(u) # "-".
 - Re-dispatch entry: every re-dispatching replacement calls
   rubi_hybrid (new, maxima_rubi_utils.mac) — the mr_top mirror with
   the pass gates lifted and the integrate fall-through on both the
   seen-guard hit and the 0-firing. No existing entry had both halves
   the .m's nested Int had: mr_int (fb=true) keeps native but drops
   passes 2-3 (1.1.2.6 e20 regressed exactly that way); rubi (fb=
   false) keeps passes 2-3 but yields the mr_unintegrable noun (1.1.2.
   6 e43's r16 re-dispatch regressed to contains-noun on it). The .m's
   Int was self-contained (Rubi.m:490 CannotIntegrate := Defer[Int])
   but the corpus acceptance standard is the run-5 pipeline, whose
   nested native answers are load-bearing.
 - REJECTED: lifting the fb pass gate globally (mr_top passes 2-3 on
   nested dispatches too) — measured HANG: 1.1.2.6 e20 retest looped
   in pattern recompilation past 900 s (2.6M-line output).
GATES: Layer A 511/0; canary broad 120: 89/31; per-target A/B vs
run-5: 120/120 matched, ZERO regressions, 12 improvements (all
deferred->verified); the four canary-regression targets (1.1.2.6
e20/e43, 1.2.2.4 e351, 1.3.2 e354) all verified (3.1/6.3/4.1/2.8 s).

RUN-6 CONTAMINATION (the 07:22-08:24 UTC full run, discarded): the
run was launched before the 9_1 work finished, and test/mr_rules.core
was SWAPPED MID-RUN (the experimental 9_1 build 256942d1 went in at
~08:1x while the 24 shard drivers were still writing). The driver's
fingerprint check is at DRIVER START, but each entry launches a FRESH
sbcl that reloads test/mr_rules.core from disk at entry start — so
entries after the swap ran on the broken pre-guard 9_1 core. The 7,052
verified->deferred "regressions" (t=0.0-0.1s — the degenerate-binding
self-loops) are the contamination signature: they ramp with in-file
entry position (per-decile counts 54, 52, 225, 560, 1126, 1184, 1172,
1087, 741, 851 — ~0 in the first two deciles), and a 40-target
stratified sample re-ran 40/40 VERIFIED on a reconstructed Phase-A
core (9_1 wiring excised, built to /tmp) + current driver. LESSON:
never modify test/mr_rules.core or any rule file while a sharded run
is in flight.

SECOND LESSON: the 120-target canary broad is biased toward currently-
FAILING targets (few verified members) — it cannot gate verified-
target regressions; the full-run A/B is the real gate. (The run-6
contamination was found by the full A/B, not the canary.)

First clean A+B full run (09:15-11:23 UTC, core 9ce4bad1, 3055
rules): 19,665 passed / 6,032 failed vs run-5 18,588/7,109
(verified 19,585 vs 18,503). Per-target A/B: 25,697 matched,
1,162 improvements, 85 regressions. Regression anatomy:
 - 49 verified->timeout + 13 in the 1.1.3.8/1.3.1 clusters:
   CORRECT-BUT-SLOW — the 9.1 rules (r16/r11) changed the quartic-
   radical answer FORM; the new form's zero chain runs 23-26 s
   solo, over the 30 s budget under 24-way load (canary 60 s
   verifies them: e125/e127/e129/e485/e491, 1.3.1 e110/e394/e408
   all verified 23-26 s).
 - ~26 in the 1.2.1.2/1.2.1.3 clusters + 1.1.3.8 e156-class:
   TWO real mechanisms, both measured:
   (a) r11 (the .m L14 sign rule) fires on NEGATED mid-cascade
       forms in nested dispatches; the .m's full table handles the
       stripped form, our partial table mishandles it three ways
       (1.2.1.2 e313: stripped form hits the 1.1.1.4 slot catch-
       all -> embedded Unintegrable marker; 1.2.1.2 e825:
       unverified radical form; 1.1.3.8 e156: the cascade
       terminates in a CONSTANT — sub-answer differentiates to
       exactly 0, numerically wrong). Unpeeled, the negated form
       0-fires to the native fall-through (the verifiable explicit-
       integral residue run-5 builds verified answers from).
   (b) the COLLAPSE rules (r7 like-term combine, r22-r26
       proportional-linear, r28/r29 perfect-discriminant) re-
       dispatch a form algebraically EQUAL to the calling
       integrand (different stored form); the normalization-aware
       seen guard (891240b) ratsimp-compares and false-positives a
       loop -> native noun (1.2.1.3 e839: x^m(A+B x)/(a+b x)^2
       stored expanded; r28 collapses factored; the family 1.1.1.3
       r8 would handle the factored form — measured directly).

FIXES (committed in the 9d9a3e7 lineage, core f1f0611f):
 - r11: cond gains is(depth_level = 1) — TOP-LEVEL ONLY. Nested
   peels restored the Phase-A/run-5 0-fire->native path.
 - rubi_hybrid split into %mr_hybrid_body(f, x, mode) + entries:
   rubi_hybrid (mode "alg", the full seen check — load-bearing
   drift guard) and rubi_hybrid_exact (mode "exact", exact member
   check only) — the 8 collapse rules re-dispatch via the exact
   entry. The collapse rules are one-shot on their own output
   (the collapsed form cannot re-trigger the pattern), so exact
   cannot self-cycle; the depth cap bounds foreign cycles; the
   measured drift chain (family rules on mr_int) never routes
   through them, so the drift guard stays intact everywhere it
   matters.
Gate re-run on f1f0611f: Layer A 511/0; canary broad 120: 120/120
matched, ZERO regressions, same 12 improvements; the 12 sampled
regressions (e839/e840/e313/e825/e156/e158/e164/e166/e125/e127/
e394/e408) all verified — the 23-26 s slow cluster now runs 6.8-
7.7 s (the r11 gate removed the deep cascade); 5/5 no-answer
spot-check unchanged.

Clean A+B full run #2 (11:40-13:02 UTC, core f1f0611f, 3055
rules): 19,731 passed / 5,966 failed (run-5: 18,588/7,109; verified
19,644 vs 18,503). Per-target A/B: 25,697 matched, 1,162
improvements, 19 regressions — the 85-regression pre-fix set is down
to 19. Anatomy of the 19:
 - 9 verified->timeout, CORRECT-BUT-SLOW: canary (60 s cap)
   verifies them at 25-35 s solo (1.1.4.3 e228 26.1 s; 1.2.1.3
   e1979 35.2 s; 1.2.1.4 e686/e687 28-30 s; 1.2.1.5 e59/e66/e73
   29-32 s; 1.2.1.9 e308 26.3 s; 1.2.2.3 e149 25.3 s) — the 9.1
   rules changed the quartic/trinomial radical answer FORM; the
   zero chain on the new form runs 25-35 s, over the 30 s budget
   under 24-way load. Several were borderline in run-5 already
   (t5 = 23.8-27.8 s). Known remainder: the zero-chain-form /
   per-entry-budget quality workstream.
 - 7 verified->timeout-or-deferred, MATCHER-STATE: the 9.1 PATTERN
   LOAD changes the Maxima compiled matcher's behavior on a small
   set of family patterns, which then 0-fire (1.2.2.4 e223 —
   1.2.2.6 r3's matchreverse pass-2 rescan firing; 1.2.1.2
   e2514/e2567/e2568/e2569/e2572/e2573 — the 1.2.1.2 r134
   (a+b x+c x^2)^p/(d+e x)^k chain with 1.4.2 r9). Bisected with
   three control cores built the same day, same Maxima/SBCL, same
   utils except the 9.1 wiring: no-9.1 core (3026 rules) fires
   both chains (r3 via the matchreverse pass-2 rescan; r134+r9);
   a second no-9.1 core with the CURRENT utils (the rubi_hybrid
   split) also fires them — ruling out the utils edit; the A+B
   core (3055) 0-fires all of them (20-60 s of clean scanning,
   no misfire/BOOLWALK lines with rubi_verbose on); a 9.1-FIRST-
   HALF-only core (r1-r14 loaded, 3040 rules) CHANGES the result
   again (a different rule fires first and embeds an
   _mr_rule_9_1_r12 noun) — so ANY 9.1 pattern load perturbs the
   rescan. Load-ORDER cannot fix it (a 9.1-first build, family
   patterns compiled in the 9.1 state, still 0-fires). The
   interaction is in the installed Maxima's compiled matcher /
   matchfix state — not reachable from Maxima-level rule code; a
   mailing-list repro (minimal defmatch/matchdeclare count +
   matchreverse flip) is the follow-up.
 - 3 no-answer->unexpected (1.2.3.4 e86/e155/e156): the corpus
   expects Unintegrable; the package now returns an answer that is
   NUMERICALLY CORRECT (sampled |diff(ans)-f| <= 3e-10 at three
   points each) — improvements the 2018 corpus cannot accept
   (its PASS class for these entries is no-answer only).

Net position: 25,697 entries, +1,162 improvements, 16 PASS->FAIL
remainders (9 slow-form + 7 matcher-state) out of 18,503 run-5
verifies (0.09%), 3 corpus-limitation improvements. Phase A+B
accepted at 19,731/5,966.

Remainder tickets (per-entry details, mechanisms, directions):
.scratch/class1-ab-remainders/ — spec.md + issues/01 slow zero-chain
forms (9), issues/02 matcher-state 9.1 pattern load (7, Maxima
boundary, mailing-list repro), issues/03 corpus Unintegrable now
integrated (3, numerically verified).

## Work item: 300 s timeout re-check — the 787 accepted-run timeouts (2026-08-27)

Re-ran EXACTLY the 787 entries the accepted A+B run (45fc9b8, core
f1f0611f) classified `timeout` at a 300 s per-entry cap (24 shards,
same core, 14:13-16:47 UTC; test/merge_timeout_rerun.py +
test/wait_timeout_rerun.sh, commit 8de89bf; record test/
corpus_class1.timeout5m.out + test/timeout_rerun_merge.out; 787/787
complete, no dupes/missing/extra).

Transitions (all were `timeout` at 30 s):
  - 90 now-PASS (88 verified + 2 expected), 11.4%;
  - 555 still timeout at 300 s, 70.5% — GENUINE non-terminators,
    not budget starvation (the 300 s cap barely shrinks the class);
  - 88 unverified (an answer was found; the zero chain did not close
    in budget — the second lever is the verification chain, not the
    rule set);
  - 47 error (subprocess deaths — full census below);
  - 5 deferred, 2 contains-noun.
Cross vs run-5 on the same 787 (only 15 were PASS in run-5):
  - ALL 9 ticket-01 slow-correct forms RECOVER to verified at
    31-71 s under 24-way load (300 s is a sufficient budget for them;
    1.1.4.3 e228 40.3 s; 1.2.1.3 e1979 71.4 s; 1.2.1.4 e686/e687
    49.1/53.0 s; 1.2.1.5 e59/e66/e73 51.8-54.3 s; 1.2.1.9 e308
    44.2 s; 1.2.2.3 e149 31.3 s);
  - ALL 6 ticket-02 matcher-state entries (1.2.1.2 e2514/e2567/
    e2568/e2569/e2572/e2573) still FAIL: 4 deferred after 44-127 s
    of wild cascade, 2 (e2572/e2573) non-terminating at 300 s.
    Budget does not touch them — structural (the lost r134+r9 chain),
    confirming the ticket-02 reading.
Still-timeout hotspots (555, by family): 1.2.1.2 (85), 1.1.2.4 (75),
1.2.1.3 (67), 1.1.3.8 (42), 1.2.2.2 (41), 1.1.1.3 (30), 1.1.3.2
(30), 1.1.1.2 (29), 1.1.2.2 (24) — the input set for the ticket-04
question-3 stratified sample (probes/matcher/).

ERROR CENSUS (all 47 re-run individually with full capture, 8-way
parallel; captures /tmp/opencode/timeout_recheck/errtriage/, per-
entry table in ticket 05):
  - 38 heap-exhausted: "Heap exhausted during garbage collection"
    -> "fatal error encountered in SBCL ... game over". Per-process
    OOM at the SBCL DEFAULT 1 GB dynamic-space cap (the core is built
    without --dynamic-space-size; the GC dump at death shows
    dynamic_space_size = 1073741824; the box had 53 GB free, no
    OOM-killer in dmesg). A candidate's ratsimp/factor working set
    holds >1 GB of live data. The knob exists (raise the cap; budget
    24 procs x N GB of 62 GB); probe = ticket 05.
  - 6 control-stack: "Control stack exhausted (no more space for
    function call frames)" after "Control stack guard page
    temporarily disabled: proceed with caution" — recursion depth,
    deep and fast (deaths at 4.4-13.8 s). They cluster near the
    ticket-02 1.2.1.2 matcher-state region (e2521/e2531/e2540/e2545)
    and 1.1.1.2 (e1702/e1712) — a possible interaction with the lost
    chain (a lost rule chain leaves the cascade recursing where the
    .m pipeline would have stopped); to check against a no-9.1 core
    (ticket 05).
  - 3 verify-integrate-fatal: a HARNESS bug, not a matcher one — the
    numeric zero-chain stage ev(diff, x=0.35) substitutes 0.35 into
    the variable slot of an INTERIOR integrate(g, x) term of the
    answer -> "integrate: variable must not be a number; found:
    0.35". The first occurrence is caught by errcatch (message
    printed, chain continues); the second is uncatchable in this
    build and kills the batch before the CLASS line. 1.1.3.8
    e517/e521, 1.2.1.2 e683. The driver already guards the DIFF
    analog (materialize MR_de once — driver comment at
    test/corpus_class1_driver.py:270); the integrate-term analog is
    unguarded. Fix = zero_chain guard (skip the numeric stage when
    the answer carries an interior integrate(., x) term); ticket 05.

## Decision: 30 s per-entry cap stays; the re-check is the verification (2026-08-27)

User decision: the driver's 30 s per-entry cap REMAINS the standard.
The route for the slow-correct entries is matcher speed (the ticket-04
workstream), not budget. When "is 30 s just at the limit?" is live
again, the standing verification is the timeout re-check: re-run ONLY
a record's `timeout` entries at a larger cap and read the transitions.
The procedure is now fully in-tree and re-runnable (the 2026-08-27
first use was launched ad hoc; the launcher is its replacement):
  python3 test/launch_timeout_rerun.py [record] [cap] [run-dir] --launch
  setsid sh test/wait_timeout_rerun.sh <run-dir> >> <run-dir>/wait.log 2>&1 &
The launcher deals the record's timeout set round-robin into N driver
shards at the cap (dry run without --launch; prints the core
fingerprint so a stale-core comparison is caught); the watcher waits
for the pids and runs test/merge_timeout_rerun.py <run-dir>/shard*.out
<out> <record> (all three parameterized; completeness asserted
against the record's timeout class; cap read from the shard headers,
not assumed). Validated by re-merging the 2026-08-27 run-dir: 787/787,
body byte-identical to the committed test/corpus_class1.timeout5m.out.

## Milestone 1 close — acceptance confirmed, Task 10 executed (2026-08-27)

User confirmed the acceptance reading (19,731/25,697 = 76.8 % vs the
T3 49.8 %; all 16 PASS->FAIL remainders triaged; no unexplained
regressions) and left all follow-up workstreams (ticket 04, the
section-9.3 port, the ticket-02 mailing-list repro, ticket 05)
POST-milestone.

Task 10 deliverables:
- docs/corpus-baseline-uplift.md refreshed to the accepted state
  (trajectory 49.8 -> 62.7 -> 72.3 -> 76.8; class table from the
  record's summary block; A/B anatomy 1,162 improvements / 19
  regressions all triaged; the 300 s re-check summary; the 31
  noun-expected entries per-entry joined: 25 no-answer + 3
  contains-noun (1.1.2.5 e103/e107/e110) + 3 unexpected; 30 s cap
  policy) — commit a1524f4.
- README.md created (package, the four load paths, rubi/rubi_fallback/
  rubi_verbose API, the --tls-limit requirement, the measured state,
  the two-layer protocol, the Rubi MIT notice per Global Constraint 14).
- AGENTS.md: ## Tests replaced with the live two-layer protocol +
  timeout re-check; the Maxima-version section updated to the installed
  5.50.0 (the 5.49 expectation is superseded; `version` verified
  unbound on 5.50.0, 2026-08-27).
- handoff/2026-08-27-milestone-1-complete.md (where everything lives,
  measured state, T5 open measurements closed with values, the
  post-milestone open items in priority order, the
  %mr_possible_zeroQ clone-gap note).
- todo/TODO.md: milestone state + T5's four open measurements closed
  (load wall: TLS cap unchanged on 5.50.0, tls-limit + rules core the
  resolution; recursion cap 16; zero chain final state; 30 s cap stays).
- Plan checkboxes Tasks 1-10 ticked (49 step boxes).

Final gate: fresh Layer A `Results: 511 passed, 0 failed`; milestone
code review dispatched (whole-branch, 131 commits + close artifacts).
REVIEW OUTCOME: no Critical; 1 Important + 9 Minor, all addressed:
- Important: the handoff's acceptance narrative said "6 matcher-state
  entries" — the measured A/B decomposition is 9 slow + 7
  matcher-state (the 7th, 1.2.2.4 e223, is verified 7.0 s run-5 ->
  deferred 29.6 s accepted, re-verified against both records by the
  reviewer's independent A/B recomputation, which reconciles exactly:
  1,162 improvements; 15 verified->timeout + 1 verified->deferred + 3
  no-answer->unexpected). Fixed in the handoff; the uplift doc's
  re-check sentence now says "6 of the 7" (e223 was deferred, not
  timeout, so it was not in the 300 s re-check set); ticket 02's table
  row e223 corrected (timeout 30.0 s -> deferred 29.6 s, matching the
  record and the ticket's own comment).
- Minor fixes: the loader's stale 5.49-era load-wall comment rewritten
  (5.50.0 re-probe, the tls-limit resolution, 72 -> 73 terms —
  comment-only); README 67 -> 73 files + the 9_1 manual-port
  exception; the plan's elliptic translation-table row superseded
  (2026-08-24 native-noun decision); test/build_rules_core.sh stamp
  gains git_tree + git_dirty fields (the accepted core's stamp
  git_rev had mislabeled a build from a dirty tree — the fix was
  committed 7 min after the build); .gitignore now covers the
  sharded-run artifacts (83 untracked files under test/); Layer A's
  trailing `0 = 0` (run_all_tests's value printing under the Results:
  line) suppressed with `$`.
- Re-review after fixes: n/a (fixes were one-line doc/stamp edits;
  Layer A re-run green).
- Known and out of scope (review item 11, ticketed): the driver
  zero_chain interior-integrate bug (ticket 05), the generator's
  head-position pattern-variable gap (absent in class 1), mr_top's
  depth_level decrement on dispatcher throw (bounded by the per-entry
  subprocesses).

Post-close core rebuild: the comment-only maxima_rubi.mac edit changed
the fingerprint inputs, so test/mr_rules.core was rebuilt (3055 rules,
new fingerprint 70074f52d31471ec2ecc89405f3834c3; the accepted run's
fingerprint f1f0611f803b7b8799853e28e2e1793b is recorded in the
acceptance docs and git history). Layer A re-run after the rebuild:
511/0.

MILESTONE 1 CLOSED.

## Plan: 2026-08-28 milestone-2 class-2 pilot (11 tasks; branch base b78d5aa)
# NOTE: the "Task N: complete" lines above this header belong to an EARLIER
# plan (milestone-1 era) — do not confuse them with this plan's tasks.

Task 1: complete (commits b78d5aa..bd0fa70, review clean after 1 fix round — spec ✅, quality Approved)
  - Fix round 1 addressed: census .run/.out reproducibility + date stamps,
    true uses= occurrence counts (re-captured class-1 + class-2 records),
    deterministic tie order, answer-heads guards (atom-charset lookbehind,
    hard-fail on empty section, section-total native lines).
  - Class-1 record change anatomy verified: stamp + 62 uses= increases +
    tie reorders only; headline 67/2710/2709 and AUTO 2032/MANUAL 678 unchanged.
  - Controller adjudications (recorded in plan): Task-1 Step-2 byte gate
    structurally unattainable -> standing gate = same-day .run re-capture
    byte-identical + headline/token-set unchanged; census closure: Expand =
    builtin passthrough (no table entry), F = extractor artifact (pattern
    var in InverseFunctionQ[F[x]]) -> class-2 token set CLOSED.
  - Minor (carried to final review): task-1-report.md:173 per-table split
    "Erf cond 1 / repl 2" is wrong (record: cond 0 / repl 3; total 3 correct);
    answer-heads self-stamp is minute-precision (brief-mandated, accepted —
    re-run stable except the stamp's minute field).
  - Pre-existing census script "uses" column bug (milestone-1 d8abbb4) fixed
    in this task as part of the fix round; docs/rule-translation.md citations
    (rule counts) unaffected.
Task 2: complete (commits bd0fa70..ae20582, review clean — spec ✅, quality Approved)
  - generate_rules.py = drift-free copy + 6 brief edit sites (mechanically
    verified old->new diff); shim generate_class1.py (12 lines, --only +
    no-arg preserved); class-1 byte-identity gate green (3026 rules, 67
    files, empty git status); class-2 smoke fails at table boundary on
    'TrueQ' (Task-3 table token, plan line 573).
  - Brief conflict resolved + reviewer-endorsed: generated-header
    Regenerate line class-gated (class 1 keeps the committed
    `generate_class1.py --only {key}` command verbatim; other classes get
    the `--class` form).
  - Minor (carried to final review): (1) generate_rules.py:2-10 module
    docstring still describes the old class-1 tool; (2) GenError prefix
    still reads `generate_class1:`; (4) bare trailing `--class` gives a
    raw IndexError (brief-verbatim); (5) a failed class-N run leaves an
    empty rules/classN/ dir (benign, git ignores it). Reviewer Minor 3
    (unused import sys in shim) is a FALSE POSITIVE — sys.path.insert at
    line 8 uses it.
Task 3: complete (commits 2ad70cc..70e6f58, review clean after controller
adjudication — spec ✅, quality Approved)
  - r96 BLOCKER adjudication (2026-08-28): defmatch in 5.50.0 REJECTS
    pattern variables in head position ("defmatch: some pattern variables
    are not atoms" — predicate never defined) -> the fix is a new pattern
    form in the CUSTOM %mr_matchQ matcher (runtime of all 16 class-1
    MatchQ rules), not Maxima's matcher. Plan amended f8178f0 (Task 3
    gains Step 4: generator emission + matcher case + Layer A tests).
  - Marker-head semantics: op(P) a registered marker -> E non-atomic,
    op(E) atomic, strict arity, ordered args (no permutation). Documented
    deviation: Maxima unary-minus storage ("-" 1-arg node vs .m
    Times[-1,u]) — a multi-slot marker head cannot match -u; no pilot
    rule needs it (r96's 1-slot case fails closed to the same Not[false]).
  - Reviewer-endorsed deviations: (1) the cond-side marker guard landed
    in emit_head (both cond routes converge there; the brief's nested-
    head branch site is subsumed); (2) the brief's verbatim
    %mr_mq_seqargs_search hard-errors at i = length(P) — part() off the
    end ERRORS in this build ("part: fell off the end.") — implemented
    with a seqargs_tail helper (one "match" goal per remaining arg; no
    %mr_mq_apply_goal change).
  - Class-2 generated: 14/4/107 = 125; Step-6 statics all match (9
    mr_use_gamma_flag, 8 gamma_incomplete|expintegral_ei, part() sites,
    no \$[A-Za-z]). Controller-verified independently: class-1 gate
    clean (generate --class 1, empty git status), Layer A 519/0 (511+8
    new marker-head checks).
  - Minor (carried to final review): (1) utils:810-817 "load-bearing"
    comment miscounts the trigger (the off-end part() needs a 0-arg
    call; the real latent hazard is silent trailing-arg drop) — comment
    accuracy only, implementation correct at all arities; (2) Layer A
    test 5 re-types the r96 pattern instead of extracting it from
    2_3.mac (character-identical today; future-emission drift risk);
    (3) whitespace churn on unrelated test lines; (4) the match-variant
    case comment omits the unary-minus deviation note (search variant
    has it).

Task 4: complete (commits 77da405..0850fb5, TDD red-green; reviewer
APPROVED, spec + quality; fix round 0850fb5; controller-verified
independently: Layer A 542/0, no trailers)
  - RED: 519 passed / 20 failed (all 20 = new checks) -> GREEN:
    539 passed / 0 failed.
  - Brief defects found by measurement (each probed before fixing,
    documented in-code with date/build): (1) lambda colon form is not
    Maxima syntax ("lambda: no body present" — comma form); (2)
    `for e : lst` parses as `for e from lst` (whole list as one
    element) -> `for e in lst`; (3) a power's op is the STRING "^"
    (is(op(x^2) = power) false; house idiom op(u) = "^"); (4) a noun's
    op is an internal symbol NOT the function symbol (member over
    function symbols never matches; string() of the op is the head
    name — calculusQ tests string(op(u)) over a string list; the diff
    noun DISPLAYS as `derivative` but string()s to "diff"); (5)
    powerOfLinearQ's x-freeness check is freeof(x, part(u, 2)) — the
    base is linear-in-x by construction, the brief's part(u,1) form was
    dead (always false).
  - Design corrections (controller-verified against the .m): (6)
    PowerOfLinearMatchQ is the STRICT stored-power test, NOT an alias
    of PowerOfLinearQ — the alias makes 2.3 r38's (.m:38) condition
    `PowerOfLinearQ[v,x] && Not[PowerOfLinearMatchQ[v,x]]`
    unsatisfiable (dead rule); the strict reading fires exactly for
    implicit-exponent v (bare linear / sqrt-linear) and matches the
    class-1 LinearQ/LinearMatchQ duality (2.1 r17/r18 exclusion).
    (7) sqrt-of-linear branch: (linear)^(1/2) stores as a 'sqrt node
    (house precedent %mr_mq_power_exp); unreachable from current
    patterns — contract faithfulness, flagged for final-review triage.
  - Plan corrected to the committed code (plan commit after 4cc259e) so
    Tasks 5-7 don't re-derive the defects.
  - Controller-verified: is() trichotomy (is(true)/is(false)/is(noun)
    = true/false/unknown), member(op(noun), [symbols]) false +
    string(op) route, integrate(f,x) EVALUATES to f*x (true nouns need
    x-dependent summand), op storage shapes (integrate noun = integrate,
    diff noun string = "diff", sqrt node = "sqrt").
  - Minor (carried to final review): the sqrt branch is currently
    unreachable from committed patterns (contract faithfulness, not
    behavior — remove if judged speculative at final review); r35/r38
    self-refire cost for implicit-exponent v is bounded by the runner
    depth cap (watch for timeout mass in the class-2 run).

  - Fix round (0850fb5): reviewer minor-1 — regression anchors for the
    new branches: powerOfLinearQ sqrt-linear true / atom false,
    powerOfLinearMatchQ sqrt-false (the 2.3 r38 firing case). Layer A
    539 -> 542. Plan test block + counts updated (20 -> 23).
  - Reviewer minors closed/recorded: report stat corrected (+31/0);
    check name "free of X" misnomer (plan-mandated, cosmetic, recorded);
    everyQ unknown-handling theoretical (plan-mandated, recorded);
    sqrt-branch reachability question -> carried to final review
    (unreachable from committed patterns today; contract faithfulness).

Task 5: complete (commits 1c15bab..4a31b8d, TDD red-green; reviewer
APPROVED conditional on plan amendment — resolved; fix round 4a31b8d;
controller-verified independently: Layer A 561/0, zero deletions,
minus-wrap storage probes, no trailers)
  - RED 545/11 (NOT the predicted 542/14 — M1 collision, see below);
    GREEN 556/0; fix round -> 561/0 (controller re-ran both).
  - M1 collision (decided: drop the brief's definition):
    %mr_numericFactor ALREADY EXISTS in M1 (utils line 1547, Rubi
    :1100) and passes all three spec tests (sum branch = direct gcd of
    term factors — no ContentFactor round-trip, which Maxima's
    auto-expansion breaks: 2*((4+6x)/2) -> 6x+4). Redefining would
    shadow M1 consumers (%mr_nonnumericFactors, sumSimplerQ family).
    Pure-addition diff (0 deletions) verified.
  - 6 systemic build defects applied (lambda comma x8, for-in,
    %mr_powerQ for all power tests, cons() (no prepend in Maxima),
    apply("*",map) (no prod(list)), direct-gcd numericFactor).
  - 7 measured new findings, each stamped: return()-in-for does not
    escape (probe recorded); while is(undecidable) ERRORS vs if-is
    no-op NOUN; negative products store as unary-minus node (op "-",
    args [3 X]) -> signOfFactor minus-wrap branch; 2*(-a-bX) STAYS a
    product (brief's design note refuted by measurement); A+B*X
    binomial / A+B*X+C*X^2 NOT a trinomial in the .m's own definition
    (quadratic base -> PolynomialQ/degree<=4 branch, as in .m);
    .m SimplifyTerm active in both branches (LeafCount choice
    commented upstream); brief's .m line citations corrected against
    pinned 61e9c18e.
  - Fix round (4a31b8d, reviewer findings): (1) FactorBase last
    branch apply("+",...) was HEAD-DESTROYING (measured: sqrt(a+bX)
    -> a+bX, minus-wrapped power -> expanded sum, minus lost) ->
    apply(op(u), ...) (M1 precedent line 3811); (2) monomialExponent
    missed bare-x factors (Maxima strips x^1) -> is(f=x)/is(u=x)
    arms; (3) minus-wrap regression test added. 5 new checks, 561/0.
  - TRIAGE FLAG (pre-existing M1 defect, out of scope): M1
    %mr_trinomial_parts misclassifies some shapes (zero-check inverted
    + under-ranged vs .m TrinomialParts :929-:937) — surfaced via the
    fix-round shape -(x^2+3*x)^3 routing to the trinomial branch;
    carried to final review; class-1 record accepted with it.
  - Minor carried: unifyTerm %mr_simp hot path may be slow on large
    sums (watch in the class-2 corpus run); layer-B run is the real
    gate for the chain's untested branches.

Task 6: complete (commits ed6d413..0028d82, TDD red-green; reviewer
NEEDS-FIXES -> fix round 0028d82; controller-verified independently:
Layer A 578/0, ifactor-unbound probe, hunk region audit, no trailers)
  - RED 561/14; GREEN 575/0; fix round -> 578/0 (controller re-ran).
  - CONTROLLER PREFLIGHT WAS WRONG on FreeQ (corrected by the
    implementer against the pinned .m and re-verified by the
    controller): Q (:4264-4266) = Test && $exponFlag$ — NO FreeQ arm;
    Test(x-free) = true but flag stays false -> Q(x-free) = FALSE;
    the non-Q .m functions return Null^Null garbage for x-free input
    -> the port declines with u (documented). Brief's test corrected
    to `= false`.
  - 9 deviations: 1 colon-lambda; for-in; if/or decidability
    verified (all conditions structural/literal/rational-gated; the
    if-unknown->NOUN quirk documented); FreeQ per .m; check-3
    not-atom -> listp (RED false-green hazard); local expon -> exn
    (Maxima option-variable collision); Maxima NESTS comments
    (/* inside a comment kills the draft); branch A uses the
    STORED-expon coefficient (.m :4336-4340, sign-flip test same);
    IGtQ base-swap DROPPED per brief (reachable for positive integer
    bases; correctness preserved — any valid t works —
    canonicalization lost; layer-B flag).
  - Fix round (0028d82, reviewer findings, all controller-verified):
    (i) ratsimp CANNOT reduce log-identities (ratsimp(log(4)/log(2))
    stays unreduced — brief's FullSimplify=ratsimp claim false) ->
    TestAux declined commensurable integer-base products (2^X*4^X)
    where the .m accepts; fixed with %mr_logRatio (positive integers
    only; ifactor UNBOUND in 5.50.0 — factor + re-factoring step,
    MEASURED) at both tmp sites; pinned
    functionOfExponential(2^X*4^X, X) = 2^X (.m's value for the
    stored order [2^X, 4^X]; Denominator[2] = 1). (ii)
    foEFunctionAux final arm was head-restricted to */+ (silent
    WRONG rewrite for Q-true inputs; r104 is Q-gated alone) ->
    .m-faithful apply(op(u), map(...)) (M1 precedent :3811); pinned
    foEF(sin(F^(B*X)), X) = sin(X). (iii) branch B sign-flip
    (:4346-4349) added on the stored-value test. (iv)
    functionOfExponential atom(st) decline guard. (v) stamps
    normalized to date + build.
  - Reviewer's branch-B %e example auto-combines in Maxima
    (%e^a*%e^b -> one power) — branch B probed with non-combining
    integer bases instead (2^(1-2X)*4^(-1/2+X) -> [true, 2, 2X-1],
    matches independent .m trace).
  - Layer-B flags (carried): swap drop (integer-base multi-factor
    integrands — form difference, zero-chain still verifies);
    commensurable shapes beyond positive integers remain declined;
    sinh pin (X^2 - 1)/(2*X) is the deterministic A/B form.

Task 7: complete (commit d964fdb, reviewer APPROVED — no Critical/
Important; controller-verified independently: 7 files, no trailers,
probe .out genuine + TABLE_AT_LOAD 3180, Layer A 581/0, flatten line
semantically intact)
  - mr_load_all() (76-term flatten, 3180 = 3055 + 125); TLS probe
    triplet (TABLE_AT_LOAD 3180, .out committed, 4247 lines);
    build_rules_core.sh FP list + image script (mr_load_all) + header
    NOTE; driver _core_fingerprint class-2 glob + docstring; core
    rebuilt (160659304 bytes, rules=3180, fingerprint
    aa53741f…, rules_core_state() = on — the shell/python sync proof);
    census spot check (2_2 count 4, witness, 1.1.1.1 still 5).
  - Brief defect (controller preflight): Step 7 commit list wrongly
    included the GITIGNORED core + stamp (disposable 154 MB image;
    ensure_rules_core auto-rebuilds) — excluded per controller;
    plan corrected.
  - Minor recorded: maxima_rubi.mac:190 flatten line re-indented 3
    spaces (cosmetic, semantically identical); probe .out header is a
    bare echo line (sibling records use # headers — spec-compliant,
    style note).
  - Re-entrance note (no action): mr_load_all twice re-runs all 76
    loads — same posture as M1's mr_load_class1_all (package-accepted).

Task 8: complete (commits 222ebc6..c00b5d9; reviewer NEEDS-FIXES ->
fix round c00b5d9 verified; controller-verified independently: 9
files, no trailers, unit 7/0, launcher dry-run through the shim,
Layer A 581/0 (a3ee89c), test_merge_classes 2/0 after re-point)
  - corpus_driver.py = class-1 copy + 4 deltas (import re +
    HEAD_REWRITES/normalize_heads; normalization at integrand +
    primary + secondary expected texts — els[2] steps excluded,
    display-only, never reaches Maxima; head-rewrites summary line;
    fingerprint already class1+class2 from Task 7).
  - Shims: driver shim re-exports 7 attrs (brief named 2 — audit A
    found 3 more consumers: canary.py, test_driver_parens.py,
    test_mr_sum_concrete.py) + PEP 562 __getattr__ that fails loudly
    on typos (reviewer live-verified: identity re-exports, clean
    AttributeError); launcher/merger shims argv-forward with class-1
    defaults; wait_and_merge.sh parameterized (POSIX, AGENTS.md
    no-arg invocation byte-identical).
  - launch/merge_class_shards.py: parameterized SECTION/MERGED/DRIVER
    (+SHARD_GLOB for the merger), SLUG = "class" + section.split()[0],
    cost model / completeness / verdict logic line-identical
    (reviewer-verified — no class-1 drift possible).
  - Evidence: head-rewrites unit 7/0; 50/50 (file,entry)->class
    identical to test/corpus_class1.out (dict diff; the brief's
    Step-7 commands omitted stop-index — re-run with 1/2/3 for the
    intended 17+17+16=50); launcher dry run 40 files/25697 entries.
  - Audit B (implementer, controller-confirmed in review): the
    merger's skip tuple did NOT skip the new header line (3/3
    records would have been INCOMPLETE) — prefix added, re-measured.
  - Fix round (c00b5d9, reviewer's single Important): the
    `head rewrites:` line was frozen at {} (f-string evaluated in the
    header block, before the loop mutated REWRITE_STATS — a
    BRIEF-DESIGN flaw in Delta 3) -> moved to the post-loop summary
    block; both polarities proven: class-1 slice -> {}, class-2
    slice -> {'gamma_incomplete(': 1} (the entry classified
    `expected` — two-sided normalization closing its zero chain
    live). Plan Delta 3 corrected.
  - Controller fix (7afde83, flagged by implementer as out-of-scope):
    test_merge_classes.py AST guard re-pointed to the generalized
    driver/merger (the shims lost the set literals).
  - Minor recorded: run-header style drift `class-1` -> `class1`
    (brief-specified); build_rules_core.sh:15,19,33,45 comments still
    name corpus_class1_driver.py (comment-only, out of scope);
    merge_class1_shards.py --help now dies at the no-shards assert
    (safer than the old full-merge-on-help; brief's || fallback).

Task 9: complete (commits 3b843fc..a2f54c1; reviewer Approved, 2
minors; controller-verified: both dry runs, merge-classes 2/0,
record tally re-counted)
  - Class-2 integrate baseline: 965 entries, 30 s cap, 3 per-file
    shards (walls 5.6/38.2/46.3 s — the maxima launch here is ~29 ms,
    image build; per-entry cost is solve-dominated).
  - BASELINE (the Task-10 A/B yardstick): Results 593 passed,
    372 failed. expected 123 / verified 186 / no-answer 284 /
    unverified 357 / unexpected 14 / timeout 1 (2.2 e58 L75, t=30.1s).
  - probe-integrate-sample.py: derived ROOT + section as 10th
    positional (brief Step 1, verbatim).
  - Merger fix (ec62741, the brief anticipated this file): the
    in-process driver needs the suite-dir positional (5th) — with the
    default, file_list() (corpus_driver.py:477) walks
    SUITE/<hardcoded class-1 SECTION> regardless of FILTER (the
    SUITE_DIR == SUITE branch); relative form required (an absolute
    equal to SUITE string-equals and re-triggers it). Pre-fix
    measured: 0 files / 965 extras.
  - LAUNCHER bug (found by controller preflight after the commit,
    fixed a2f54c1): launch_class_shards.py had the same missing
    suite-dir — the class-2 package run would have resolved 0 files /
    0 jobs and CRASHED (ZeroDivisionError in the balance-spread
    print at :268-269). Fix: SUITE_REL appended to the argv rewrite;
    class-1 plan byte-identical (40 files / 25697, rel sets
    byte-compared); tiny 5-entry class-2 shard through the fixed
    launcher: 5 real T3 lines.
  - Carried minor 1 (Task-10 A/B readout margin note): baseline =
    probe mechanics (4-stage symbolic chain, no head rewrites,
    noun-on-answer-expected = PASS no-answer); Task-10 run = driver
    mechanics (8-stage + numeric chain, head rewrites,
    deferred/contains-noun FAIL classes). Net: the yardstick errs
    slightly CONSERVATIVE for the package (2 of 3 asymmetries flatter
    it). A stricter comparison = re-run the native baseline through
    the driver harness.
  - Carried minor 2 (nit): task-9-report.md:191 cites a pre-fix line
    number (262; final-tree 268-269) — the measurement was pre-fix,
    left as-is.

Task 10: complete (commits db89195..50cce22; reviewer Approved, 2
minors — one fixed (50cce22), one carried; controller-verified:
A/B script re-run, record tallies, re-check merge.out, sh -n,
dump-tested the watcher pass-through)
  - Class-2 PACKAGE run: 965/965, 26 shards / 24 procs, wall
    8 min 07 s. Results: 500 passed, 465 failed.
    Tally: expected 116 / verified 320 / no-answer 64 / unverified
    125 / deferred 314 / contains-noun 14 / unexpected 4 / timeout 7 /
    error 1.
  - A/B vs the Task-9 integrate baseline: 500/965 (51.8%) vs
    593/965 (61.5%). Entry-level (reviewer-verified arithmetic):
    PASS->FAIL 309 = 178 GENUINE declines (baseline expected/verified
    -> package, ALL `deferred`: the rules return a top-level noun
    where native integrate had an answer) + 131 yardstick
    reclassification (baseline no-answer = PASS under the probe;
    FAIL deferred/unverified/timeout/contains-noun under the driver);
    FAIL->PASS 216. The margin note (probe-vs-driver asymmetry)
    applies — see the plan's Task-10 note.
  - 300 s timeout re-check (7 entries): 7/7 re-checked; transitions
    error 2 + unverified 5; now-PASS 0 — the 30 s cap is NOT the
    limit for class 2.
  - FINDING (triage candidate): reproducible SBCL HEAP EXHAUSTION on
    quotient-of-exponentials integrands — 2.3 e56/e57 (timeout at 30 s
    -> error 71.4s/95.4s at 300 s) + 2.3 e68 (error 17.4s in the run).
    Matcher/rule bug candidate; the pilot's findings input.
  - Brief defects fixed (measured): D1 the brief's ${@:4} is
    dash-incompatible (/bin/sh = dash; Bad substitution) AND the
    controller-proposed while-loop was off-by-one — final form =
    three guarded shifts (dump-tested both polarities, class-1
    merge line byte-identical); D2 launch_timeout_rerun.py's
    in-process driver exec gained the relative suite-dir positional
    (subprocess cmd already had it; class-1 walk unchanged — full
    suite walk + FILTER yields the same rel set); D3
    wait_timeout_rerun.sh derives the merge output name from the
    source basename (class-1 name byte-identical, dash-verified);
    D4 DRIVER stays an absolute path (the brief's bare name would
    break the spec load + subprocess argv).
  - Fix round 2 (50cce22, reviewer minor): merge_timeout_rerun.py
    hard-coded "class-1" in the re-check record header -> SLUG
    derived from the source basename (corpus_classN.out -> class-N;
    the class1->class-1 hyphen insertion was caught by the string
    check); record regenerated (header + merge-date lines only;
    7/7 entry lines byte-identical); class-1 no-regression proven
    by a REAL re-merge of the still-on-disk class-1 shards
    (787/787, all lines identical).
  - Carried minor: the MERGED record carries no `head rewrites:`
    aggregate (the merger skips per-shard stats lines — pre-existing
    Task-8 behavior; class-1 merged record has the same property).
    Per-shard lines remain on disk (e.g. {'gamma_incomplete(': 9,
    'expintegral_ei(': 9}); a merge-header aggregate is an optional
    future improvement for A/B margin work.

Task 11: complete (commits bb74cb6..b2b4cb7; reviewer Needs-fixes ->
fix round b2b4cb7; controller re-verified the two Important fixes
against the records before closing)
  - docs/corpus-class2-baseline-uplift.md (433 lines) — the
    measured acceptance record: header (build stamps, 3,180 rules,
    fingerprint, branch), rule set (125 = 14/4/107, census), the two
    head rewrites + class-1 no-op, baseline 593/965 (61.5 %), package
    500/965 (51.8 %), per-file A/B table (2.1 59.2->31.6, 2.2
    35.5->35.5, 2.3 64.9->56.3; total -9.6 pts), entry-level split
    (309 = 178 deferred genuine + 131 reclassification; 216
    FAIL->PASS), residues by file with example entries, class-1
    stands (byte-identity + spot check + no-op), ledger flags with
    per-commit no-regression evidence.
  - docs/class-porting.md (357 lines) — the runbook: 10 steps as
    executed for class 2 (census -> table -> generator -> utils ->
    generate -> loader/core -> driver rewrites -> baseline -> package
    run -> close) + standing constraints. Reviewer: a class-3 porter
    is unblocked by the runbook alone (two one-line clarifications
    added in the fix round).
  - todo/TODO.md — Milestone-2 (pilot) closed section (the two %
    lines, record paths, follow-ups: classes 3-8 as runbook tickets
    in spec order, polylog/AppellF1 deferred, PowerOfLinear revisit
    conditional, the SBCL heap-exhaustion bug as its own item).
  - Final gates: Layer A 581/0; class-1 regen byte-identical (empty
    porcelain); head-rewrites 7/0.
  - Reviewer findings (all fixed in b2b4cb7, controller-reverified):
    F1 (Important) the 2.2 squared/cubed-denominator examples — the
    original "e56-e63" was false (e56/e57 unexpected, e58/e59
    unverified, e60 timeout, e61 verified, e62/e63 unexpected — zero
    deferred); the deferred set is e9-e12, e15-e20, e23-e24 (12) +
    the e64-e66 numerator powers; e13/e14/e21/e22 are the
    no-answer expected-Unintegrable entries (controller re-listed
    the 2.2 record: matches). F2 (Important) the 2.1 attribution —
    e20-e22 bases are stored expanded, so they decline at the
    stored-form %mr_powerOfLinearQ (utils:4638) before r12/r13's
    clauses are reached; split 8 PoL-gated (e16-e18, e20-e22,
    e25-e26) + 23 coverage gaps (e55, e60-e64, e69-e73, e78-e89)
    (controller re-listed the 2.1 deferred set: matches). F3 the
    total delta -9.7 -> -9.6 pts (exact). F4 e68 numerator c->f
    (suite 2.3 L85: F^(e*(f+d*x)) numerator, c+d*x denominator).
    F5 "67 files" -> "72 generated files" (67 T1 + 5 EXTRA b; 73 on
    disk incl. the manual 9_1.mac) in 3 places. F6/F7 runbook
    clarifications: the (rel,entry) join is a method (no committed
    script) with the worked example; shard bounds are START/STOP
    file indices, STOP exclusive.
  - Note: controller's own first verification pass of F1/F2 briefly
    read the 2.3 record (the heap-exhaustion e56/e57 share their
    entry numbers with 2.2's e56/e57) — the docs and the fix round
    were correct; the bullet's entry numbers are 2.2's.

## Plan: 2026-08-29 milestone-3 class-3 port (11 tasks; branch base b9fecd0)

Branch: milestone-3. Plan: docs/superpowers/plans/2026-08-29-milestone-3-class3.md
(the runbook docs/class-porting.md instantiated for class 3). NOTE: the
installed Maxima was REBUILT 2026-08-29 17:58 (same source rev
branch_5_50_base_84_g4204fb669, same SBCL 2.6.7; build date field
2026-08-29 17:58:20 supersedes the AGENTS.md 2026-08-20 stamp — Layer A
re-verified 581/0 on the new core, 2.1 s). All class-3 measurements
stamp the current build; the class-3 A/B yardstick is the Task-9
baseline measured on this build.

Task 1: complete (commit 8e92841..5f93a97, review clean — spec ✅,
quality Approved; reviewer independently re-ran both probes: census
byte-identical, answer-heads count-identical)
  - CONTROLLER RECON ERROR found by the implementer (NEEDS_CONTEXT):
    the plan's "PolyLog 10" grep counted COMMENTED-OUT bracket-notation
    lines (PolyLog[2,z]) the driver never reads. Plan corrected in
    place (8e92841). Measured truth: the active class-3 expected texts
    carry the NATIVE polylog( spelling — 1,195 of 3,085 entries (38.7
    %), 2,793 occurrences (orders 2: 2081, 3: 518, 4: 138, 5: 21, 6:
    1, 1: 1, symbolic k/n offsets: 33), per-file 0/187/179/91/106/65/
    243/237/87. Adjudication (binding): PolyLog -> 1:1 RENAME polylog
    (build's diff(polylog(.,.)) AND polylog(.,numeric) are nouns —
    probed; identical-form differences cancel before the diff —
    probed — so polylog entries close only via the two-sided expected
    chain on form-identical answers; self-diff/numeric stages cannot).
    The 1,195-entry mass is the Task-11 ceiling-decision input.
  - Committed: probes/translation/04-class3-syntax-census.{run,out}
    (11/333/332, AUTO 241/MANUAL 92, 13/13 U tokens), probes/corpus/
    03-class3-answer-heads.{py,run,out} (entries 3085; GAMMA {2:304},
    Ei {1:220}, Chi/Shi/Si/Ci {1:8}, Li {1:22}; NATS polylog( 2793,
    erf( 14, erfi( 137, %e^ 790; PolyLog in HEADS at 0 documenting the
    Rubi-paren absence).
  - Minor (carried): the "1 rules" histogram grammar is inherited from
    the shared 01-class1-syntax-census.py formatter (class-1/2 records
    have it too); answer-heads minute-precision stamp on re-run is by
    design (brief-mandated, M2 precedent).

Task 2: complete (commit daf3d79..0f92fd7, review clean — spec ✅,
quality Approved; reviewer re-ran the byte-identity gate fresh at HEAD:
`--class 1` and `--class 2` regeneration left `git status --porcelain
rules/` EMPTY after each, whole tree clean)
  - Generator changes: translation_table.py +56/-1 (14 RENAME rows:
    Chi/Shi/Si/Ci/LogIntegral -> expintegral_* answer natives, PolyLog
    -> polylog 1:1, eight %mr_ port names per the brief's list),
    RESTRUCTURE row LogGamma -> "loggamma" handler; generate_rules.py
    +31 (LogGamma emitter case emitting log(gamma(v)); Gamma arity
    dispatch mirroring the PolyQ emitter pattern: 1-arg -> gamma,
    2-arg -> gamma_incomplete, other arity -> GenError).
  - Loud failures reproduced by the reviewer (14/14): Gamma[] -> "Gamma
    arity 0", Gamma[a,b,c] -> "Gamma arity 3", LogGamma[a,b] ->
    "LogGamma arity 2"; GenError subclasses SystemExit(1) with the
    file/rule/token named on stderr.
  - Class-2 surface verified: class 1 has ZERO Gamma occurrences; class
    2 has 5/5 two-arg Gamma (2.1 x2, 2.3 x3) taking the 2-arg branch —
    committed class-2 output holds exactly 5 gamma_incomplete( and no
    bare gamma(. LogGamma appears only in class 3 (3.5).
  - 3026 vs 3,055 RECONCILED (not an error): 3,026 is the generator's
    --class 1 TOTAL (72 emitted files, self-checked by
    EXPECTED_TOTAL, generate_rules.py:2126); the accepted class-1
    table is 3,055 = 3,026 + the 29-rule hand-ported
    rules/class1/9_1.mac (by design not generator-regenerable); core
    3,180 = 3,055 + 125 — the Task-7 fingerprint target stays
    3,180 + 333 = 3,513.
  - Minor (carried for Task 7): task-2-report.md quotes the generator's
    "TOTAL: 3026 rules" line unannotated; a Task-7 reader reconciling
    against the 3,055 record needs the 3,026 + 29 + 125 = 3,180
    arithmetic (reviewer finding 1). The Gamma RENAME table value
    ("gamma_incomplete") is now reached only by the bare-atom path —
    the accepted PolyQ precedent, documented in the row comment
    (reviewer finding 2).
