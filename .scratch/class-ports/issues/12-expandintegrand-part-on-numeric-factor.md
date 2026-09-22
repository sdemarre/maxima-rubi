# %mr_expandIntegrand errors on a factored denominator with a numeric lead factor (pre-existing)

Status: needs-triage
Type: bug (rule misfire — the rule is skipped, so a route is silently lost)
Filed: 2026-09-22 (found by the section-9 port's Task 12 end-to-end gate, branch `section9-port`)

## The finding

`%mr_expandIntegrand` raises `part: argument must be a non-atomic expression`
when the expression it is given contains a `factor()` result whose leading
factor is a plain number. MEASURED 2026-09-22, build
`branch_5_50_base_84_g4204fb669`, `load("maxima_rubi.mac")` only (no rules):

```maxima
Px : 2*x^3 + 4*x/3 - 68/27$
Qx : factor(Px)$                     /* => 2*(27*x^3+18*x-34)/27 */
%mr_expandIntegrand((2*x - 8/3)*Qx^-1, x)$
```

```
part: argument must be a non-atomic expression; found 2
```

`errcatch` returns `[]`. The `2` in the message is `factor`'s numeric lead
factor: something on the expand path indexes into it with `part` without first
checking that it is non-atomic.

**Identical on `master`** (worktree `/home/serge/src/mr-s9-ref`, `c95c6ed`) and
on `section9-port` (`346c513`) — a pre-existing defect, independent of class 9.

## Where it bites

Rule `1_3_3` r12 (`rules/class1/1_3_3.mac:99-101`) is
`Int[u_*Px_^p_, x] := Int[ExpandIntegrand[u*Factor[Px]^p, x], x]`: its repl
factors `Px` and calls `%mr_expandIntegrand` on the result, so any `Px` whose
factorisation carries a rational content hits this. The dispatcher catches it
and logs

```
rubi: rule 1_3_3 r12 misfire (repl error) on (2*x-8/3)/(2*x^3+(4*x)/3-68/27) with [...]
```

so it is contained — but the rule is then skipped and the route is lost, and the
bare `part:` line is printed to the terminal in the middle of an otherwise clean
run (that is how it was noticed: two such lines in
`test/test_section9_e2e.mac`'s output while the spec-A4 integrand
`1/(x + sqrt((1+x)/(1-x)))` ground on — see issue 11).

## Reproduce

```sh
cd /home/serge/src/maxima-rubi
cat > /tmp/pei.mac <<'EOF'
load("maxima_rubi.mac")$
print(errcatch(%mr_expandIntegrand((2*x-8/3)*factor(2*x^3+4*x/3-68/27)^-1, x)))$
EOF
maxima --very-quiet -b /tmp/pei.mac < /dev/null
```
