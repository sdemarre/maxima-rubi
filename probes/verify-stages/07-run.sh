#!/bin/sh
# probes/verify-stages/07-run.sh -- runs the two Maxima probes of 07 on the
# rules core (build it first: sh test/build_rules_core.sh) and stamps the
# build and core. From the repo root:
#   sh probes/verify-stages/07-run.sh
# writes 07-e466-bigfloat.out and 07-e1000-legacy-9_1-first.out. The SymPy
# probe runs on its own: python3 probes/verify-stages/07-sympy-check.py
set -u
D=probes/verify-stages
stamp() {
  maxima --very-quiet --batch-string='printf(true, "# build ~a~%", build_info()@version)$' < /dev/null | grep '^# build'
  echo "# $(date -u +%Y-%m-%dT%H:%MZ), rules core $(head -1 test/mr_rules.core.stamp), $(sed -n 2p test/mr_rules.core.stamp)"
}
for p in 07-e466-bigfloat 07-e1000-legacy-9_1-first; do
  { stamp
    timeout -k 5 600 sbcl --tls-limit 100000 --core test/mr_rules.core --noinform --very-quiet \
        -b $D/$p.mac < /dev/null 2>&1 | grep -E '^E(466|1000) '
  } > $D/$p.out
done
