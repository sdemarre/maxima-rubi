# Zero-chain verification-stage OOMs (+ one matching control-stack overflow) in the class-3 run

Status: needs-triage
Type: research
Filed: 2026-08-30 (milestone-3 close — the Task-10 death census,
reviewer-corrected: 15 deaths = 13 heap-exhausted OOMs + 2
control-stack-exhausted)

## The measured basis (build 2026-08-29 17:58:20 / SBCL 2.6.7;
sources: `docs/corpus-class3-baseline-uplift.md` §4/§5,
`.superpowers/sdd/task-10-report.md` §6/§7/§12)

**13 heap-exhausted OOMs, all in the driver's zero-chain
VERIFICATION stage:**

- Package run (30 s cap): 3.2.1 e74 (t=29.2 s), 3.3 e233 (12.8 s),
  3.3 e327 (8.7 s), 3.3 e494 (21.5 s).
- 100 s re-check: 3.1.5 e30, 3.2.1 e73/e75, 3.3 e151/e328/e534,
  3.5 e9/e169/e172 (each re-run at the 100 s cap to capture the raw
  subprocess output).
- All 13 are the reproducible SBCL "Heap exhausted, game over"
  (the 1 GiB dynamic space exhausts, `bytes_allocated` 99.8 %).
  **The blowup is in the VERIFICATION stage, not the matching**:
  `rubi()` alone answers e233/e74/e30 (the reviewer re-ran 3.3 e233
  at 12.7 s, 3.2.1 e74 at 16.4 s, 3.1.5 e30 at 48.1 s — the
  package answers exist), while the 8-stage zero chain dies.
  Matcher-speed work must not be misdirected at matching.

**1 matching control-stack overflow:** 3.2.3 e79
(`log(e*((a+b*x)/(c+d*x))^n)/(f-g*x^2)`, reproduced at 2.1 s in the
run, "Control stack exhausted while pseudo-atomic" in the matcher).
The other control-stack death (3.3 e492) is the reproducible
rule-generation arity bug, ticketed separately and ready-for-agent
(`.scratch/class3-algebraicfunctionq-arity/issues/01`) — out of
scope here except as the census context.

**Polylog-family concentration:** all 6 package-run `error`s and 8
of the 9 re-check OOMs sit in the polylog families
(`.superpowers/sdd/task-10-report.md` §8) — the verification-stage
blowup is worst where polylog verification is attempted (the
`diff(polylog(·,·),·)`-noun mass, see the sibling ticket
`.scratch/class3-polylog-ceiling/issues/01`).

## Directions (to be triaged, not yet decided)

1. **Heap-size probe.** Does a larger SBCL `--heap-size` close the
   13? This is memory, not budget — **the 30 s per-entry cap policy
   STAYS** (user decision 2026-08-27); a heap-size change would be a
   harness/driver launch-flag change (the driver's maxima
   subprocess args), measured on the 13 reproducers. If a larger
   heap closes them, record the cost (wall, the TLS-limit
   interaction — the `--tls-limit 100000` flag takes two argv
   tokens, AGENTS.md) and decide whether the driver carries the
   flag by default.
2. **Stage isolation.** Which stage of the 8-stage chain blows up
   (numeric / ratsimp-first / factor-first / radcan-fallback /
   the two-sided expected subtraction)? Re-run the 13 with the
   chain stages gated one at a time (the Task-9 review's S1/S2/S3
   cascade idiom), recording `bytes_allocated` per stage — a
   committed re-runnable probe under `probes/`.
3. **The polylog interaction.** Triage together with the polylog-
   shim ticket: a shim that closes polylog diffs EARLIER in the
   chain may shrink the blowup (the heavy stages are never
   reached); the 8/9 re-check OOM concentration is the evidence.
4. **e79's matching overflow.** The integrand is a quotient-of-
   log-ratio shape; reproduce at the matcher (the 2.1 s repro),
   check whether a runner depth/recursion cap
   (`%mr_max_depth : 16`) or the seen-guard bounds it, and whether
   the M2 class-2 heap-exhaustion family (2.3 e56/e57/e68 —
   quotient-of-exponentials, M2 TODO, still open, matching-locus)
   is the same root cause under a different integrand family.

## Acceptance (for the research phase)

- A committed re-runnable probe set (build-stamped) reproducing all
  13 + e79, with the heap-size and stage-isolation measurements;
  the locus/mechanism recorded; a fix ticket (driver launch flag /
  stage order / matcher guard) or a wontfix-with-ceiling filed from
  the measurement. The class-3 record's death census (15 = 13 + 2)
  is the before-state and must be cited in the after-state.

## Comments
