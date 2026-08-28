# 2.3 `Miscellaneous exponentials.m`: 5 commented-out rules as a candidate coverage source for the deferred mass

Status: needs-triage
Type: research (+ possible port)
Filed: 2026-08-28 (from the class-2 A/B residue review; the 154 genuine
2.3 `deferred` declines of `docs/corpus-class2-baseline-uplift.md` §4)

## Observation

The pinned Rubi 4 source (`reference/rubi` @
`61e9c18ea248061cd83c67882f7c91a73cef912d`), file
`Rubi/IntegrationRules/2 Exponentials/2.3 Miscellaneous exponentials.m`,
is 115 lines: **107 active `Int[… ] := …` rules** (what the generator
ports into `rules/class2/2_3.mac` — the port is faithful, 107/107,
consistent with the T1 census), plus:

- lines 1–3: blank line + `(* ::Subsection::Closed:: *)` front matter
  + section title comment;
- **5 commented-out (disabled) rules** at lines 39, 40, 67, 68, 102.

The five disabled rules:

- L39: `Int[u_.*F_^(a_.+b_.*v_^n_),x] := Int[u*F^(a+b*ExpandToSum[v,x]^n),x] /; FreeQ[{F,a,b,n},x] && PolynomialQ[u,x] && LinearQ[v,x] && Not[LinearMatchQ[v,x]]`
- L40: the binomial twin of L39 (`BinomialQ[u,x] && Not[BinomialMatchQ[u,x]]`);
- L67: `Int[(c_.+d_.*x_)^m_.*F_^(g_.*(e_.+f_.*x_))/(a_+b_.*F_^(h_.*(e_.+f_.*x_))),x] := 1/b*Int[(c+d*x)^m*F^((g-h)*(e+f*x)),x] - a/b*Int[…same…/(a+b*F^(h*(e+f*x))),x] /; FreeQ[{F,a,b,c,d,e,f,g,h,m},x] && LeQ[0,g/h-1,g/h]`
- L68: the dual of L67 with `LeQ[g/h,g/h+1,0]`;
- L102: `Int[u_.*(a_.*F_^v_)^n_,x] := a^n*Int[u*F^(n*v),x] /; FreeQ[{F,a},x] && IntegerQ[n]`.

Commenting out a rule is Rubi's way of keeping a known-broken or
incomplete rule in the file without loading it; `LoadRules` (and our
generator) pick up live lines only. The file does not say *why* these
five are disabled.

## Hypothesis (count-level, untraced)

L67/L68 are recursive reduction rules for the **quotient-of-exponentials
head** `(c+d·x)^m · F^(g(e+f·x)) / (a+b·F^(h(e+f·x)))` — the same head
family as (a) the deferred 2.3 mass (774 shapes, mixed
`Ei`/`GAMMA`/`polylog`/`erfi`/`hypergeometric` expected answers) and
(b) the reproducible heap-exhaustion entries 2.3 e56/e57
(`x^2/(b/f^x+a·f^x)`, `x^3/(b/f^x+a·f^x)` — quotients of exponentials
after normalization). If part of the 154 genuine 2.3 declines (or the
18 in 2.2, whose deferred shapes include powered denominators
`(a+b·F^(…))^k`) matches a disabled rule's LHS, those entries are a
port-and-unblock candidate rather than a permanent coverage gap.

No per-entry rule trace was performed for any deferred entry
(uplift §5: count-level inference only); the L102/L39/L40 overlap with
the deferred set is not assessed at all.

## Directions (to be triaged)

1. **Why disabled** — the reference clone has full git history:
   `git -C reference/rubi log --follow -p -- <file>` / `git blame` on
   the 5 lines to find when and why Rubi upstream commented them out.
   A rule disabled for a soundness reason must not be ported as-is
   (the decline-safe-semantics rule of `docs/class-porting.md` applies
   to any unblock, and the L39/L40 `ExpandToSum`/`LinearQ`/`BinomialQ`
   predicates are not all in the ported predicate table).
2. **Shape overlap** — per-entry match of the 154 genuine 2.3 deferreds
   (plus the 18 2.2 and 6 2.1 declines, list in uplift §4) against the
   5 disabled LHS shapes; commit the trace as a probe under `probes/`
   per the research-discipline rule.
3. **If overlap is measured** — port the implicated rules (generated,
   never hand-edited), re-run the class-2 A/B, and record the flip
   count against `test/corpus_class2.out` as the acceptance.

## Interactions to watch

- L67/L68 are **recursive** (both sides carry `Int[… ]`): an unblock
  feeds the `%mr_max_depth : 16` recursion cap and the
  cascade/recursion machinery — the same region as the ticket-02
  matcher-state finding.
- The heap-exhaustion trio (e56/e57/e68) sits in the same head family;
  a rule that fires on those integrands could convert `error` entries
  into long cascades. The heap ticket's outcome should be read
  alongside any unblock measurement.

## Acceptance (when worked)

- The 5-line git-history answer is recorded here (when/why disabled).
- A committed probe with the per-entry overlap census (or a measured
  zero overlap, which closes this ticket as wontfix-with-evidence).
- If any rule is ported: class-2 A/B re-run with the flip count
  recorded; no new `error` entries; Layer A unchanged.

## Comments
