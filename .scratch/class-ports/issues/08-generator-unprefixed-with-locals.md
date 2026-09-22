# The generator's With/Module locals are unprefixed in classes 1/2/3/6 (and mr_sum re-evaluates under them)

Status: fixed (branch fix-mr-sum-capture); one follow-up open (the slowdown below)
Type: bug (silently wrong antiderivatives)
Label: needs-triage
Filed: 2026-09-21 (inert-trig substrate final fix wave, item I2, ruling R28)

## The finding

A generated repl binds its Rubi `With`/`Module` locals in a Maxima `block` under
their SOURCE names and often runs a nested `mr_int` inside that block:

```
block([d], d : %mr_freeFactors(...), %mr_dist(..., mr_int(...)))
```

Maxima binds block locals DYNAMICALLY. While the block is live, any evaluation
of an expression containing the symbol `d`, however deep in the nested
integration, reads the local's value instead of the integrand's own `d`. The
nested integration does re-evaluate: `mr_sum` (maxima_rubi_utils.mac, the Sum
handler, ~L53) evaluates an atom summand TWICE, `ev(subst(i, var, ev(fun)))`,
and its plain-expression branch once more, `ev(subst(i, var, fun))`.

Measured (`sh probes/maxima/probe-class4-with-capture.run`, build
`branch_5_50_base_84_g4204fb669`, 2026-09-21, full `mr_load_all` table):

- **Section C, the mechanism with no class-4 rule involved:**
  `mr_int(1/(c+d*x^5), x)` verifies (residual 1.7e-16); the same call inside
  `block([d], d : 1, ...)` answers with residual 8.5e-4.
- **Section E, the class-4 instance (fixed in the wave):** before commit
  `de51845`, 4.7.5 r47's `block([d], d : 1, ...)` turned
  `rubi(cos(x)/(d*sin(x)^7+1), x)` into an answer with residual 1.08e-3 /
  6.7e-2 at two points, and `sin(x)/(c+d*cos(x)^5)` 2.0e-2 / 9.5e-4.
- **Section D, `mr_sum`'s OWN locals, no With involved at all:** `mr_sum`
  is `block([a, b, i, s, t], ...)`, and its double `ev` re-evaluates the
  summand under them. `rubi(1/(a+b*x^5), x)` answers with residual **0.035**
  (`a` read as `ceiling(lo)`, `b` as `floor(hi)`); `1/(1+t*x^5)` 0.30;
  `1/(1+i*x^5)` 0.012; `1/(1+s*x^5)` printed `expt: undefined: 0 to a negative
  exponent` on the way. `1/(p+q*x^5)` verifies (1.7e-16). This is PRE-EXISTING
  on `master`: every 1.1.3.1 / 1.1.3.2 Sum rule with a corpus-named `a`/`b`
  answers through it. The corpus driver verifies by differentiation, so such
  entries read as FAIL (`unverified`), not as a wrong PASS -- but a user of
  `rubi()` gets a wrong antiderivative with no warning.

## The exposure (re-measured from the generated files, 2026-09-21, commit `de51845`)

Blocks whose locals list holds a name not beginning `_mr_` (cond and repl
copies both counted), and how many of them contain a nested `mr_int(`:

| class | unprefixed-local blocks | with a nested `mr_int` | rule functions |
|---|---|---|---|
| 1 | 862 | 579 | 544 |
| 2 | 29 | 16 | 16 |
| 3 | 99 | 73 | 73 |
| 4 | 0 (fixed, `de51845`) | 0 | 0 |
| 6 | 15 | 15 | 15 |

Most frequent shapes: class 1 `block([q])` x323, `block([k])` x54,
`block([A, B, C])` x48, `block([r])` x40, `block([r, s])` x27,
`block([q, f])` x22, `block([g])` x19, `block([a, b, c, d])` x13; class 3
`block([u])` x60, `block([k])` x12, `block([f, g, h])` x2; class 2
`block([m])`/`block([z])` x6; class 6 `block([k])` x8, `block([u])` x5.

Two aggravating shapes: (1) the 8 `mr_sum(u, k, ...)` calls with an ATOM
summand (1.1.3.1 r13/14/21/22, 1.1.3.2 r35-38) take the double-`ev` path;
(2) the 40 lambda-summand calls run `apply(fun, [i])` INSIDE `mr_sum`'s
`block([a, b, i, s, t])`, so a lambda body naming a With local `s` or `t`
(class 1 has 27 `block([r, s])`) reads `mr_sum`'s running sum instead --
unmeasured, check it first.

## The fix (not done in the wave: it needs a P3 exception and a 4-class A/B)

1. **Generator:** the class-4 switch of `de51845` (`_push_scope_locals`,
   `ctx["prefix_locals"]`, generator/generate_rules.py) is the emitter for
   every class: drop the `CLASS == 4` condition. It is a pure alpha-renaming
   of the emitted block (the wave checked it by reversing the renaming
   against the pre-fix file, byte for byte). The P3 static gate
   (`test/check_generated_rules.py`) needs a closed exception: "every
   With/Module local renamed `_mr_<key>_r<n>_<name>`", checked as that exact
   text transformation, as the translation-fix exceptions are.
2. **`mr_sum`:** prefix its locals (`%mr_sum_a`, ...), and drop the double
   `ev` -- evaluate the atom summand ONCE (`subst(i, var, fun)` then one
   `ev`), or better, have the generator emit a lambda for the 8 atom
   summands. Hand-written utilities: audit every other `ev(` in
   maxima_rubi_utils.mac for the same re-evaluation under unprefixed locals.
3. **Measure:** full A/B of classes 1, 2, 3 and 6 against their accepted
   records (`python3 test/ab_records.py`); expect FAIL->PASS on the entries
   the trap made `unverified`, and attribute every PASS->FAIL.

## Probe recipe

```sh
sh probes/maxima/probe-class4-with-capture.run   # sections C and D are the all-class evidence
```

A one-integrand check of any rule: compare `rubi(f, x)` with
`subst(q=d, rubi(subst(d=q, f), x))` (rename the suspect symbol to one no
generated block binds); a difference, or a non-zero numeric residual
`float(rectform(subst([x=0.37, ...], diff(r, x) - f)))`, is the trap.
The final-review probes (`/tmp/claude-1000/final-review/capture*.mac`,
not committed) ran the same comparison over class-6 corpus integrands.

## Resolution (2026-09-22)

- `afabf04` mr_sum's locals are `%mr_sum_*` (fix step 2). The audit found no
  other `ev(` or `''` in the hand-written utilities. The double `ev` is kept:
  with the locals prefixed it no longer captures anything.
- `c69826d` the generator prefixes With/Module locals in every class (fix
  step 1). 74 files regenerated; undoing the renaming reproduces the previous
  files byte for byte (the local `D` was emitted as `diff` before). The P3
  gate has the closed exception `undo_local_prefix`, 1,602 declarations, 22/0.
  Layer A 1179/0 (7 new targets, each RED before its fix).
- Probe re-run: section D residuals 0.035 / 0.30 / 0.012 -> 1.7e-16. Section
  C is the bare mechanism (a hand-written block([d])) and still captures, by
  design.

### Measurement (fix step 3)

Full runs, queue runner, 30 s cpu, 2026-09-21/22, named records
`test/corpus_class{1,2,3,6}.locals-prefix.out` (12 workers; class 1 24).
The host ran an Android emulator (~6.5 cores) throughout, so entries near the
cap moved with the load: CPU per entry was 1.13-1.21x the accepted records' on
entries the fix cannot reach. The full-run A/B against the accepted records is
therefore NOT the attribution:

| class | accepted -> new PASS | P->F | F->P |
|---|---|---|---|
| 1 | 18,114 -> 18,094 | 68 | 48 |
| 2 | 708 -> 716 | 0 | 8 |
| 3 | 1,673 -> 1,673 | 0 | 0 |
| 6 | 1,636 -> 1,629 | 7 | 0 |

The attribution is a PAIRED rerun of every entry whose verdict changed (238),
the pre-fix core (`5ca6126`, fingerprint `3d08a28a`, the accepted records'
core) and the new core running concurrently, 6 workers each, same load:

| class | changed | old -> new core, same load |
|---|---|---|
| 2 | 8 | 8 F->P (unverified -> verified) |
| 3 | 13 | same PASS/FAIL on every entry (4 flip timeout <-> contains-noun at 29.5-30.1 s, both directions) |
| 6 | 24 | identical verdicts on all 24 -- its 7 P->F were load |
| 1 | 193 | 51 F->P, 9 P->F, 46 P->P (load), 87 F->F |

Then the 60 class-1 entries whose PASS differed between the cores, at a 100 s
cap, both cores: all 60 verify on the new core.
- 47 are the trap: on the old core 40 RAN AWAY past 100 s (e.g. 1.1.1.2
  e1772-e1833, 1.1.3.4 e156-e178) and 7 answered wrong (unverified); the new
  core verifies each in < 5 s.
- 13 straddle the cap and verify on BOTH cores, but the new core is slower on
  all 13: 1.02-1.25x, median ~1.07x (1.2.1.2 e602 24.4 -> 30.6 s, e1519
  25.5 -> 30.3 s, e479 25.4 -> 29.1 s; 1.2.1.4 e831 28.4 -> 32.5 s). 9 of them
  cross 30 s.

Net on the same load: class 1 +51 / -9, class 2 +8, classes 3 and 6 0.

## Follow-up: the 13-entry slowdown (open)

Systematic (13/13 in one direction), small, unexplained. Hypothesis, NOT
measured: a renamed local that is a Sum index or lambda parameter
(`k` -> `_mr_<key>_r<n>_k`) survives into expressions, and Maxima orders terms
by symbol name, so later rules see a differently ordered expression and take a
different (valid, slower) path. Check first: `rubi_verbose` rule traces of
1.2.1.2 e602 on the two cores (`MR_RULES_CORE_PATH`), diffed.
