# T1 — Rubi anatomy

Status: open
Doc: `docs/rubi-architecture.md`
Depends on: — (drives T2 and T4)

## Questions to answer

1. How does `Rubi.m` dispatch rules? (the `Int` head, rule order, show-steps)
2. The rule grammar: what a rule is — pattern / condition / replacement —
   with concrete examples drawn from each function class.
3. Rule counts per function class (measured on the pinned clone).
   Confirms or corrects "algebraic functions" as the milestone-1 seed class.
4. The utility-function inventory: every helper the rules call, ranked by
   frequency, with a rough porting-cost estimate per function.
   This is the support-function gap list.
5. License text verbatim + what a port must carry (attribution etc.).
6. How does Rubi verify its own answers (derivative check? simplification?)

## Evidence

(Stamped measurements land here as work proceeds: date, Maxima build string
where relevant, probe under `probes/` where the measurement is reproducible.)
