#!/bin/sh
# probes/dispatch-index/02-cond-functions.sh -- ticket 21, step 1 follow-up:
# probe 01 puts ~95 % of a dispatch in the conditions of attempts that match
# but whose condition fails.  Which Maxima functions is that time spent in?
# (.scratch/class-ports/issues/21-dispatch-index-skip-impossible-records.md)
#
# Maxima's own timer, two arms per entry, sequential:
#   excl  timer(all), timer_devalue : true -- every user function (16,516:
#         utilities, rule conds, rule repls), SELF time (a timed callee's time
#         is subtracted from its caller)
#   incl  timer_devalue : false on the %mr_* functions the rule conditions
#         call directly (read from rules/class*/*.mac) -- INCLUSIVE time, so
#         nested predicates overlap
# runtime is get(f, 'runtime) in microseconds.  timer adds per-call overhead
# (the "R cpu s" line against probe 01's plain run shows how much), heaviest
# on the functions called most, so read the excl ranking with the call counts.
#
# Usage (repo root):
#   sh probes/dispatch-index/02-cond-functions.sh > probes/dispatch-index/02-cond-functions.out 2>&1
set -u
cd "$(dirname "$0")/../.." || exit 1
ROOT=$(pwd)
W=${TMPDIR:-/tmp}/mr-dispatch-index-02
rm -rf "$W"; mkdir -p "$W"
CORE=$ROOT/test/mr_rules.core
SBCL=$(command -v sbcl)
CAP=${CAP:-400}

echo "== core stamp"; cat "$CORE.stamp"; echo

CONDFNS=$(python3 - <<'EOF'
import re, glob
fns = set()
for f in glob.glob('rules/class*/*.mac'):
    s = open(f).read()
    for m in re.finditer(r'^_mr_cond_\w+\(mm, x\) :=(.*?)\)\$\s*$', s, re.S | re.M):
        fns |= set(re.findall(r'(%mr_\w+)\(', m.group(1)))
print(','.join(sorted(fns)))
EOF
)
echo "cond-called %mr_ functions: $(echo "$CONDFNS" | tr ',' '\n' | wc -l)"

run() { # label integrand arm top
  f="$W/e.mac"
  {
    echo 'display2d : false$ linel : 10000$'
    echo 'print("R build", build_info()@version, build_info()@timestamp)$'
    if [ "$3" = excl ]; then
      echo 'timer_devalue : true$ timer(all)$'
    else
      echo "timer_devalue : false\$ timer($CONDFNS)\$"
    fi
    echo 'print("R timed functions", length(timer()))$'
    echo "mr_f : $2\$"
    echo 't0 : elapsed_run_time()$'
    echo 'r : errcatch(rubi(mr_f, x))$'
    echo 'print("R cpu s", elapsed_run_time() - t0, "answered", is(r # [] and freeof(unintegrable, r)))$'
    echo "rows : sublist(map(lambda([f], [f, get(f, 'calls), get(f, 'runtime)]), timer()), lambda([r], r[2] # false and r[2] > 0))\$"
    echo 'rows : sort(rows, lambda([a, b], a[3] > b[3]))$'
    echo 'print("R total timed us", lsum(r[3], r, rows))$'
    echo "for r in firstn(rows, min($4, length(rows))) do print(\"T\", r[1], \"calls\", r[2], \"us\", r[3])\$"
  } > "$f"
  echo "== $1 arm=$3"
  setsid "$SBCL" --core "$CORE" --noinform --very-quiet -b "$f" < /dev/null > "$W/out" 2>&1 &
  pid=$!
  i=0
  while kill -0 $pid 2>/dev/null; do
    i=$((i + 1)); [ $i -gt $CAP ] && { kill -KILL -$pid; echo "KILLED at ${CAP}s"; break; }
    sleep 1
  done
  grep -E '^(R |T )' "$W/out"
  grep -c 'Lisp error' "$W/out" | sed 's/^/lisp-errors: /'
}

entry() { # label integrand
  run "$1" "$2" excl 30
  run "$1" "$2" incl 20
}

entry "c4 4.1.2.2 e88" '(g*cos(e+f*x))^(3/2)*(c-c*sin(e+f*x))^(7/2)*sqrt(a+a*sin(e+f*x))'
entry "c4 4.2.4.2 e18" 'cos(c+d*x)^2*(a+a*cos(c+d*x))^3*(A+C*cos(c+d*x)^2)'
entry "c4 4.2.4.2 e912 (timeout)" '(a+b*cos(c+d*x))^(5/2)*(B*cos(c+d*x)+C*cos(c+d*x)^2)/sqrt(cos(c+d*x))'
entry "c1 1.1.1.2 e1170" '1/((6-3*e*x)^(1/4)*(2+e*x)^(3/4))'
