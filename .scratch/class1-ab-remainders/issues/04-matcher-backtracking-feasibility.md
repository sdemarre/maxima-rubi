# Matcher backtracking: feasibility investigation

Status: partially answered by docs/corpus-class3-deferred-uplift.md
Type: research
Filed: 2026-08-27 (after the A+B acceptance run; the user request of the
same date — "investigate the feasibility of adding backtracking to the
matcher, maybe look at Maxima itself for inspiration")
Blocked by: (none — read-only research; does not touch the rule set or
the accepted run)

## Partial answer — class-3 deferred campaign (closed 2026-09-12)

The class-3 deferred campaign (spec
`docs/superpowers/specs/2026-08-30-class3-deferred-campaign-design.md`
§5.4; record `docs/corpus-class3-deferred-uplift.md`) executed this
ticket's question 3 and option (ii) on the class-3 mass, with the full
population instead of a sample:

- **Question 3 (how much does backtracking recover) — answered on the
  class-3 deferred population (1,033 entries; target mass 788 =
  verified 313 + expected 16 + unverified 459).** The per-candidate
  implicit-1 sweep (a backtracking reading of the single-candidate
  `findfun` selection) fires on **17 entries (FIRE4; 13 of them target
  mass)**; a further **181 entries (0FIRE-EXPL)** carry binding evidence
  (a pass-4 factor pick) but no firing — 77 of them baseline-verified,
  81 unverified (record §1, probe `probes/corpus/06-class3-deferred-
  mechanisms`). Adjudicated, the backtracking-rescue class (A) is 10
  entries (+ e47 pending); the mass is dominated by port and
  expressibility gaps (B-port 297, C-in-Rubi 483; record §2–§3).
- **Option (ii) (a backtracking findfun shadow) — implemented, NOT
  shipped.** Implemented as pass 4, the shadow-index form
  (`maxima_rubi_pass4.lisp`, commits 30815e1 + ab7ad93). Production
  wiring was gated on p95 added ≤ 3 s AND mean added ≤ 1 s; measured on
  the 37 swept entries the full sweep costs mean 8.78 s / p95 34.69 s
  and the forward-only k=3 fallback 3.51 s / 15.25 s — the cost clause
  fails on every variant, so pass 4 stays unwired (record §3.1, probe
  `probes/corpus/07-class3-deferred-sweep-cost-fallbacks`).
- **What recovered the mass instead** — rule/utility port fixes (record
  §4): of the 788 target entries 366 now PASS (329 certain subset: 222);
  the class-3 record moved 1,736 → 2,058 / 3,085 (record §5–§6, probe
  `probes/corpus/10-class3-deferred-close-recovery`).
- **Direction since:** user decision 2026-09-11 replaces Maxima's
  `defmatch` with a Lisp matcher with Mathematica semantics (spec
  `docs/superpowers/specs/2026-09-12-matcher-substrate-design.md` §0.1),
  which supersedes options (i)–(iv) as the route for the class-1
  deferred mass.

Still open (not measured by the campaign): question 1 (the annotated
file:line match-path map); question 2(b) (whether the loss propagates
past `findfun` into the `matmatch` recursion) and 2(c) (the backtracking
cost on the class-1 heavy targets); question 3 on the **class-1** 4,361
deferred; question 4 (the `../maxima-lists` prior-art search, existing
hooks in the installed source, the upstream patch sketch); question 5's
ranked costs for class 1.

## Why

The A+B acceptance run (core f1f0611f, commit 45fc9b8) passes 19,731 /
25,697 of the class-1 corpus. The dominant failure class is
`deferred` — 4,361 entries (73% of the 5,966 failures): the ported
rule set has a rule for these (the 2018 .m pipeline integrated them),
but Maxima's matcher 0-fires the chain. This is the known residual
matcher gap: Maxima's commutative-product matcher has **no
backtracking** where the .m matcher does, and has two further measured
structural differences (exponent-1 stripping, factor-order
dependence). Two prior mechanisms already exist as stopgaps, both
built at the lisp level:

- **Pass 2** (`maxima_rubi_dispatch.lisp`, `%MR_DISPATCH_REV`): flips
  the lisp global `matchreverse` (nil = reverse factor scan) and
  rescans the table — recovers the factor-ORDER class (commit
  3b057dd, run-4 -> run-5 uplift).
- **Pass 3** (`maxima_rubi_implicit1.lisp`): shadows `findfun`
  (matrun.lisp) behind a `*mr-implicit1-active*` flag and rescans with
  an implicit-exponent-1 reading — recovers the BARE-FACTOR class
  (commit 9d9a3e7, run-5 -> A uplift).

Both are per-shape rescans, not general backtracking. The 4,361
deferred are what remains after both passes. A backtracking matcher
(or a generalization of the shadow technique) is the single biggest
lever on the corpus pass rate.

## Known ground (measured, with references — do not re-derive)

- Factor-order gap: `findfun` (matrun.lisp) picks, for a pattern
  factor with a non-atomic base, the FIRST `^`-factor of the target in
  the REVERSED stored order, no backtracking; the stored order is
  Maxima's canonical sort (data-dependent). `matchreverse` is a
  defmvar whose Maxima-level value does NOT reach the lisp global in
  the installed 5.50.0 build (measured 2026-08-26) — hence the lisp
  flip. See `%MR_DISPATCH_REV`'s header comment.
- Implicit-1 gap: Maxima strips exponent 1 at construction and never
  restores it in matching (`matcom.lisp` compilematch head check;
  `matrun.lisp` findfun explicit-head search) — measured 2026-08-27,
  see `maxima_rubi_implicit1.lisp` header.
- Pattern recompilation is the cost center: the rejected global pass-
  gate lift looped in pattern recompilation past 900 s on 1.1.2.6 e20
  (measured 2026-08-27, ledger). Any matcher surgery must keep the
  compiled-pattern cache warm or the corpus run cost explodes.
- Matcher state is fragile: loading the 29 section-9.1 patterns
  perturbs the matchreverse rescan on specific family chains (7
  entries, ticket 02) — the installed matcher's compiled state is
  load-order/state-sensitive. Any change here must re-verify ticket 02
  and the 9 slow-form entries (ticket 01) afterwards.
- TLS wall: each defmatch/matchdeclare slot costs ~9.6 special vars;
  the process runs at `--tls-limit 100000` (AGENTS.md, probes/load_
  wall/). Matcher work that adds per-pattern state must budget this.

## Research questions

1. **Where exactly does the installed matcher lose backtracking?**
   Read the installed Maxima source (the build is on this box; find
   `matrun.lisp`, `matcom.lisp` in the source tree / build dir —
   `build_info()` for the build stamp). Pin the exact functions and
   line numbers for: candidate selection in commutative product
   matching, the head-check at match time, the pattern compilation
   cache (what gets compiled, what gets invalidated). Deliverable: a
   short annotated map (file:line) of the match path for a
   product-of-powers pattern.
2. **How reachable is a backtracking insertion point?**
   (a) Is `findfun` (or its successor in 5.50) called through a
   rebindable symbol — i.e., can a shadow replace it the way
   `maxima_rubi_implicit1.lisp` already shadows it? (b) Does a
   backtracking `findfun` (try all candidate factors, not just the
   first) suffice for the factor-order class, or does the loss
   propagate deeper (the whole `matmatch` recursion)? (c) What does a
   backtracking findfun cost on the heavy targets (measure on a
   50-entry sample of the 4,361 deferred: per-entry time with/without)?
3. **How much of the 4,361 does backtracking actually recover?**
   Stratified sample (>= 100 entries across families): run each
   through (i) the current 3-pass pipeline, (ii) the pipeline plus a
   prototype backtracking findfun shadow (if question 2 says it is
   reachable). Report the recovered count per family. This number —
   not the mechanism — is the go/no-go input.
4. **Prior art and upstream path.** Search the `../maxima-lists`
   archive (grep the index.tsv files) for matcher backtracking /
   `matchfix` / findfun discussion; check the installed source for
   existing (unused or partial) backtracking hooks. If the clean path
   is an upstream Maxima patch, sketch it and flag it for the mailing
   list (the ticket 02 repro may share the report).
5. **Ranked options with costs**, at the end of the report:
   (i) lisp-global flag additions (matchreverse-style, cheap/narrow);
   (ii) a backtracking findfun shadow (the implicit1 precedent,
   medium); (iii) a custom matcher for the product-of-powers shape
   family (the slot-hybrid direction of commit 9f5ccef generalized,
   bounded per-family effort); (iv) upstream Maxima patch (long-term).
   For each: expected corpus recovery (from question 3), implementation
   cost, risk to the accepted 19,731 (regression surface: the whole
   verified set, since every match path changes).

## Deliverables

- `docs/matcher-backtracking-feasibility.md` — the report: annotated
  match-path map, reachability verdict, the sampled recovery number,
  the ranked options, a go/no-go recommendation for an implementation
  ticket. Every non-trivial claim cites a probe.
- The probes under `probes/matcher/` (re-runnable batch scripts,
  build-stamped per the AGENTS.md research discipline).
- A ledger entry in `.superpowers/sdd/progress.md` pointing at the
  report.

## Acceptance

- The report answers questions 1-5 with measurements (not reasoning
  from source alone — at least the sample re-run of question 3).
- No change to `test/mr_rules.core`, the rule files, or the accepted
  run outputs (this ticket is read-only w.r.t. the acceptance state;
  a prototype shadow lives in probes/ only).
- Ticket 01 / 02 / 03 untouched and still accurate.
