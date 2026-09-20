#!/bin/sh
# probes/matcher/23-timing-control.sh -- is probe 21's wall clock trustworthy?
#
# Probe 21's record (commit c28edfd) claimed a "~28 % SYSTEMATIC OFFSET"
# against probe 06's committed numbers, inferred from three loosely-matched
# pairs, and used it to conclude the section 3.8 prune is neutral on 3_5 r37
# (348.7 x 1.28 = 446).  This probe tests that claim directly and REFUTES it.
#
# Two controls on the ONE job the two probes measure identically -- rubi(big)
# on the 46dffa2 tree, which probe 06 records at 39.0 s and probe 21 at
# 50.3 s:
#   A  five identical repeats: is the job reproducible at all?
#   B  bare vs errcatch vs errcatch(lambda): does probe 21's timed() wrapper
#      (which probe 06 does not use) inflate the measurement?
#
# Usage (repo root), needs a worktree of 46dffa2:
#   sh probes/matcher/23-timing-control.sh <t0-tree> \
#       > probes/matcher/23-timing-control.out 2>&1
set -u
cd "$(dirname "$0")/../.." || exit 1
ROOT=$(pwd)
T0=${1:?usage: 23-timing-control.sh <46dffa2 worktree>}
W=${TMPDIR:-/tmp}/mr-23-timing-control
rm -rf "$W"; mkdir -p "$W"
BIG='x^2*(a+b*x)^3*(c+d*x)^4*(e+f*x)^5*(g+h*x)^6*log(x)'

cat > "$W/rep.mac" <<MAC
display2d : false\$
linel : 10000\$
print("R build", build_info()@version, build_info()@timestamp)\$
load("maxima_rubi.mac")\$
mr_load_all()\$
big : $BIG\$
t : elapsed_real_time()\$
r : rubi(big, x)\$
print("R rubi s", elapsed_real_time() - t, "chars", slength(string(r)))\$
print("R DONE")\$
MAC

cat > "$W/wrap.mac" <<MAC
display2d : false\$
linel : 10000\$
load("maxima_rubi.mac")\$
mr_load_all()\$
big : $BIG\$
t : elapsed_real_time()\$
r : rubi(big, x)\$
print("R bare s", elapsed_real_time() - t)\$
t : elapsed_real_time()\$
r : errcatch(rubi(big, x))\$
print("R errcatch s", elapsed_real_time() - t)\$
/* exactly probe 21's timed(): a lambda inside an errcatch */
f : lambda([], rubi(big, x))\$
t : elapsed_real_time()\$
r : errcatch(f())\$
print("R errcatch_lambda s", elapsed_real_time() - t)\$
print("R DONE")\$
MAC

echo "=== probes/matcher/23-timing-control  git HEAD $(git rev-parse --short HEAD)  $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "=== A  five identical repeats of rubi(big) on $T0"
i=1
while [ $i -le 5 ]; do
  ( cd "$T0" && timeout -s KILL 300 maxima --very-quiet -b "$W/rep.mac" \
      < /dev/null 2>&1 | grep -a '^R rubi' | sed "s/^/rep$i /" )
  i=$((i + 1))
done
echo "=== B  measurement wrapper A/B, same process"
( cd "$T0" && timeout -s KILL 600 maxima --very-quiet -b "$W/wrap.mac" \
    < /dev/null 2>&1 | grep -a '^R ' )
echo "=== done"
