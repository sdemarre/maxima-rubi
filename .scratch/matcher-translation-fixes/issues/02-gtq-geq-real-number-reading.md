# GtQ / LtQ / GeQ / LeQ: port Rubi's real-number reading

Status: needs-triage
Type: task (measure, then decide)
Filed: 2026-09-15 (matcher translation fixes, P5b attribution — outside the plan's four defects;
design §1 Out: "GtQ's RealNumberQ/N reading — siblings outside the four shapes are ticketed, not fixed")

## Problem

The generator translates Rubi's real comparisons to a bare Maxima `is`:
`generator/generate_rules.py:853` `CMP_OPS = {"GtQ": ">", "LtQ": "<", "LeQ": "<=", "GeQ": ">="}`, which
emits `is(A op B)`.

Rubi reads them differently (`reference/rubi/Rubi/IntegrationUtilityFunctions.m:403–453`, pinned clone):

```mathematica
GeQ[u_,v_] :=
  If[RealNumberQ[u],
    If[RealNumberQ[v], u>=v, With[{vn=N[Together[v]]}, Head[vn]===Real && u>=vn]],
  With[{un=N[Together[u]]},
  If[Head[un]===Real,
    If[RealNumberQ[v], un>=v, With[{vn=N[Together[v]]}, Head[vn]===Real && un>=vn]],
  False]]]
```

`GtQ`, `LtQ` and `LeQ` follow the same shape at :403, :421 and :457. On a symbol, `N[Together[u]]` is not
`Real`, so `GeQ[d, 0]` is **False** and `Not[GeQ[d, 0]]` is **True**. Maxima's `is(d >= 0)` on an
unassumed symbol answers `unknown`, which the dispatcher rejects (`is(r) = true`). What
`not(is(d >= 0))` answers, and whether the dispatcher accepts it, is **not measured**.

## Evidence

- P5b attribution, class 2 g3 e19 (`probes/matcher/10-p5b-attribution.mechanisms-class2-3.md:79–84`).
  Rubi's normalizing pair for `F^(c(a+bx))((d+ex)^n)^m` is `1_4_1_r43` / `r44` (`GeQ[a,0]` /
  `Not[GeQ[a,0]]`). The port emits `is(d >= 0)` / `not(is(d >= 0))`. On the fixed core neither rule
  fired and the entry is `deferred`. P0 answered through `1_4_1_r41` on a binding Mathematica does not
  make.
- Crude count of `is(… >= …)` in the generated rules: class 1 43, class 2 1, class 3 0 (grep, 2026-09-15,
  HEAD 5c26cc5). The other three heads are not counted yet.

## What to do

1. Probe: count every emitted `GtQ` / `LtQ` / `GeQ` / `LeQ` site per class from the Rubi source, as
   probe 13 does for the integer heads. Measure `is(sym >= 0)`, `not(is(sym >= 0))` and the dispatcher's
   verdict on each, and compare Rubi's reading on symbol / rational / float / `%pi`-constant / complex
   arguments.
2. Decide with the user: port the reading as named entries (`%mr_geQ(u, v)` etc., true/false, the
   design §3.1 pattern with static-gate undo exceptions), or record it as a deviation.
3. If ported: red/green probe, Layer A checks, regeneration, and a P5-style A/B of the affected entries.
