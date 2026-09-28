#!/bin/sh
# probes/verify-stages/06-principal-branch-4.1.0.sh -- runs
# 06-principal-branch-4.1.0.mac on the seven 4.1.0 entries (category 2 of
# handoffs/2026-09-28-checker-wrong-answers), one process each, in parallel,
# on the rules core (build it first: sh test/build_rules_core.sh).
# From the repo root:
#   sh probes/verify-stages/06-principal-branch-4.1.0.sh > probes/verify-stages/06-principal-branch-4.1.0.out
set -u
D=probes/verify-stages
W=$(mktemp -d)
while read -r lab gg; do
  sed "s/LABEL/$lab/; s|GG|$gg|" $D/06-principal-branch-4.1.0.mac > "$W/$lab.mac"
  ( timeout -k 5 1200 sbcl --tls-limit 100000 --core test/mr_rules.core --noinform --very-quiet \
      -b "$W/$lab.mac" < /dev/null > "$W/$lab.out" 2>&1 ) &
done <<'LIST'
e304 cos(e+f*x)^4*(b*sin(e+f*x))^(1/3)
e305 cos(e+f*x)^2*(b*sin(e+f*x))^(1/3)
e309 cos(e+f*x)^4*(b*sin(e+f*x))^(5/3)
e310 cos(e+f*x)^2*(b*sin(e+f*x))^(5/3)
e314 cos(e+f*x)^4/(b*sin(e+f*x))^(1/3)
e315 cos(e+f*x)^2/(b*sin(e+f*x))^(1/3)
e320 cos(e+f*x)^2/(b*sin(e+f*x))^(5/3)
LIST
wait
maxima --very-quiet --batch-string='printf(true, "# build ~a~%", build_info()@version)$' < /dev/null | grep '^# build'
echo "# $(date -u +%Y-%m-%dT%H:%MZ), rules core $(cat test/mr_rules.core.stamp 2>/dev/null | head -1)"
for lab in e304 e305 e309 e310 e314 e315 e320; do
  grep "^$lab " "$W/$lab.out" || echo "$lab NO OUTPUT"
done
rm -rf "$W"
