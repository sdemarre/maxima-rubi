# Matcher backtracking: feasibility investigation

Status: ready-for-agent
Type: research
Filed: 2026-08-27 (after the A+B acceptance run; the user request of the
same date — "investigate the feasibility of adding backtracking to the
matcher, maybe look at Maxima itself for inspiration")
Blocked by: (none — read-only research; does not touch the rule set or
the accepted run)

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
