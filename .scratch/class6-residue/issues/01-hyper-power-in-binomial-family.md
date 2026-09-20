# Class-6 residue: the `.7` family reaches no rule at all — 1,173 entries

Status: open
Type: task (rule coverage)
Filed: 2026-09-20 (class-6 Step-10 close)

## Scope

Six corpus files defer at ~100 %:

| corpus file | N | FAIL | dominant |
|---|---:|---:|---|
| 6.1.7 `hyper^m (a+b sinh^n)^p` | 525 | 525 (100 %) | deferred 521 |
| 6.3.7 `(d hyper)^m (a+b (c tanh)^n)^p` | 263 | 263 (100 %) | deferred 262 |
| 6.5.7 `(d hyper)^m (a+b (c sech)^n)^p` | 220 | 220 (100 %) | deferred 219 |
| 6.2.7 `hyper^m (a+b cosh^n)^p` | 85 | 85 (100 %) | deferred 85 |
| 6.4.7 `(d hyper)^m (a+b (c coth)^n)^p` | 53 | 53 (100 %) | deferred 53 |
| 6.6.7 `(d hyper)^m (a+b (c csch)^n)^p` | 27 | 27 (100 %) | deferred 26 |
| **total** | **1173** | **1173** | |

**23 % of the section and 37 % of all its `deferred`.** These are the
single largest recoverable block in class 6 and the first thing to look
at for an uplift.

## What is already known

- **NOT an unloaded-file artifact.** The pinned clone has exactly 13
  section-6 `.m` files and all 13 are generated and loaded
  (`docs/corpus-class6-baseline-uplift.md` §1). Nothing was skipped.
- The shape is a power of one hyperbolic inside a binomial of another.
- **Likely cause, stated as a GUESS:** Rubi reaches these through
  machinery outside section 6 — substitution into the algebraic or trig
  sections — which this port has not yet ported. Not verified.

## First moves

1. Take ~5 entries from 6.1.7 and trace what Rubi 4 actually does with
   them (which rule fires, in which section). That decides whether this
   is a section-6 gap or a cross-section dependency.
2. If it is a cross-section dependency on class 4 (trig), it is a reason
   to sequence class 4 earlier than its corpus size alone suggests.

## Why it matters beyond class 6

If the answer is "hyperbolic integrands are reached through the trig
rules", the same will hold for class 7 (inverse hyperbolic, 6,552
entries) against class 5 (inverse trig), and the porting ORDER should
be reconsidered on that basis.
