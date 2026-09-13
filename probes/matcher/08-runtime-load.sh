#!/bin/sh
# probes/matcher/08-runtime-load.sh -- the runtime measurements of the matcher
# substrate P4 gate (spec section 3.5 "TLS", section 4 P4): does the package
# load and pass Layer A WITHOUT -X "--tls-limit 100000" (the defmatch slots
# that exhausted SBCL's special-variable pool are gone), how long does
# mr_load_all take, and how long does the rules core build take.
# Sequential; run it on an otherwise idle machine.
# Usage (repo root):
#   sh probes/matcher/08-runtime-load.sh > probes/matcher/08-runtime-load.out 2>&1
# Leaves test/mr_rules.core and its .stamp rebuilt.
set -u
cd "$(dirname "$0")/../.." || exit 1
W=${TMPDIR:-/tmp}/mr-08-runtime-load
rm -rf "$W"; mkdir -p "$W"
TLS='--tls-limit 100000'
now() { date +%s.%N; }
since() { python3 -c "print(round($(now) - $1, 1))"; }

cat > "$W/load.mac" <<'EOF'
display2d : false$
linel : 10000$  /* print does not wrap: every R line stays whole for grep */
t0 : elapsed_real_time()$
load("maxima_rubi.mac")$
t1 : elapsed_real_time()$
mr_load_all()$
t2 : elapsed_real_time()$
print("R load maxima_rubi.mac s", t1 - t0, "mr_load_all s", t2 - t1, "rules", length(mr_rule_table))$
r : rubi(x^3*(a+b*x^2)^(5/2), x)$
print("R smoke answered", is(string(op(r)) # "unintegrable"),
      "radcan zero-chain", is(radcan(diff(r, x) - x^3*(a+b*x^2)^(5/2)) = 0))$
EOF

echo "=== probes/matcher/08-runtime-load  git HEAD $(git rev-parse --short HEAD)  $(date -u '+%Y-%m-%d %H:%M UTC')"
timeout -s KILL 60 maxima --very-quiet --batch-string='print("R build", build_info()@version, build_info()@timestamp)$' < /dev/null 2>&1 | grep -a '^R build'
for arm in flagless flag; do
  if [ $arm = flag ]; then set -- -X "$TLS"; else set --; fi
  t=$(now); timeout -s KILL 300 maxima --very-quiet "$@" -b "$W/load.mac" < /dev/null > "$W/load.$arm.out" 2>&1
  echo "LOAD $arm wall $(since $t) s; TLS lines $(grep -a -c 'Thread local storage' "$W/load.$arm.out")"
  grep -a '^R ' "$W/load.$arm.out"
  t=$(now); timeout -s KILL 900 maxima --very-quiet "$@" -b test_maxima_rubi.mac < /dev/null > "$W/layerA.$arm.out" 2>&1
  echo "LAYER-A $arm wall $(since $t) s; TLS lines $(grep -a -c 'Thread local storage' "$W/layerA.$arm.out"): $(grep -a '^Results' "$W/layerA.$arm.out" | tail -1)"
done
t=$(now); timeout -s KILL 300 maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null > "$W/dispatch.out" 2>&1
echo "DISPATCH-SUITE flagless wall $(since $t) s: $(grep -a '^Results' "$W/dispatch.out" | tail -1)"
t=$(now); sh test/build_rules_core.sh > "$W/core.out" 2>&1; rc=$?
echo "CORE-BUILD wall $(since $t) s exit $rc: $(grep -a 'built' "$W/core.out" | tail -1)"
echo "=== done"
