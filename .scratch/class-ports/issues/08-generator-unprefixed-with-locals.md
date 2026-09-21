# The generator's With/Module locals are unprefixed in classes 1/2/3/6 (and mr_sum re-evaluates under them)

Status: open
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
