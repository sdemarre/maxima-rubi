#!/bin/sh
# probes/dispatch-index/01-profile.sh -- ticket 21 step 1: profile a dispatch.
# (.scratch/class-ports/issues/21-dispatch-index-skip-impossible-records.md)
#
# For a few slow-but-verified class-4 reduction-chain entries and a class-1
# control: dispatches per entry, attempts per dispatch, the category of every
# attempt (no binding / condition fails / repl declines / fired), the time in
# the matcher vs the condition, and what two static index oracles (root head,
# required heads) would have skipped -- with a soundness count.  See
# 01-profile.lisp for the definitions.
#
# Each entry runs TWICE, sequentially (never concurrently): plain, then
# profiled, so the instrumentation's overhead is visible.  Runs on the rules
# core test/mr_rules.core (its stamp is printed).
#
# Usage (repo root):
#   sh probes/dispatch-index/01-profile.sh > probes/dispatch-index/01-profile.out 2>&1
set -u
cd "$(dirname "$0")/../.." || exit 1
ROOT=$(pwd)
W=${TMPDIR:-/tmp}/mr-dispatch-index-01
rm -rf "$W"; mkdir -p "$W"
CORE=$ROOT/test/mr_rules.core
SBCL=$(command -v sbcl)
CAP=${CAP:-240}

echo "== core stamp"; cat "$CORE.stamp"; echo

run() { # label integrand profiled(0/1)
  f="$W/e.mac"
  {
    echo 'display2d : false$ linel : 10000$'
    echo 'print("R build", build_info()@version, build_info()@timestamp)$'
    [ "$3" = 1 ] && echo "load(\"$ROOT/probes/dispatch-index/01-profile.lisp\")\$ pf_reset()\$"
    [ "$3" = 1 ] && [ -n "${4:-}" ] && echo "pf_report_after($4, \"$1\")\$"
    echo "mr_f : $2\$"
    echo 't0 : elapsed_run_time()$'
    echo 'r : errcatch(rubi(mr_f, x))$'
    echo 'print("R cpu s", elapsed_run_time() - t0, "answered", is(r # [] and freeof(unintegrable, r)))$'
    [ "$3" = 1 ] && echo "pf_report(\"$1\")\$"
  } > "$f"
  echo "== $1 profiled=$3"
  setsid "$SBCL" --core "$CORE" --noinform --very-quiet -b "$f" < /dev/null > "$W/out" 2>&1 &
  pid=$!
  i=0
  while kill -0 $pid 2>/dev/null; do
    i=$((i + 1)); [ $i -gt $CAP ] && { kill -KILL -$pid; echo "KILLED at ${CAP}s"; break; }
    sleep 1
  done
  grep -E '^(R |PROFILE|  )' "$W/out"
  grep -c 'Lisp error' "$W/out" | sed 's/^/lisp-errors: /'
}

entry() { # label integrand [cut-seconds: profiled run reports and exits then]
  run "$1" "$2" 0
  run "$1" "$2" 1 "${3:-}"
}

entry "c1 1.1.1.2 e1170" '1/((6-3*e*x)^(1/4)*(2+e*x)^(3/4))'
entry "c4 4.2.4.2 e18" 'cos(c+d*x)^2*(a+a*cos(c+d*x))^3*(A+C*cos(c+d*x)^2)'
entry "c4 4.5.4.2 e108" 'cos(c+d*x)^4*(a+a*sec(c+d*x))^3*(A+C*sec(c+d*x)^2)'
entry "c4 4.1.2.2 e88" '(g*cos(e+f*x))^(3/2)*(c-c*sin(e+f*x))^(7/2)*sqrt(a+a*sin(e+f*x))'
# current `timeout`s (test/corpus_class4.out, 30 s cpu cap); their outcome in
# the 100 s re-check of the previous record
# (test/corpus_class4.final.timeout-rerun/): verified 25.1 s, 34.6 s, 91.4 s,
# and still timeout at 100 s -- that one is cut at 120 s and reports partially
entry "c4 4.2.4.2 e912 (timeout)" '(a+b*cos(c+d*x))^(5/2)*(B*cos(c+d*x)+C*cos(c+d*x)^2)/sqrt(cos(c+d*x))'
entry "c4 4.5.4.2 e1328 (timeout)" '(A+B*sec(c+d*x)+C*sec(c+d*x)^2)/(cos(c+d*x)^(5/2)*(a+b*sec(c+d*x))^2)'
entry "c4 4.1.2.2 e1470 (timeout)" 'csc(c+d*x)^3*sec(c+d*x)^2/(a+b*sin(c+d*x))^2'
entry "c4 4.1.2.2 e1403 (timeout at 100 s)" 'sin(e+f*x)^3/((g*cos(e+f*x))^(5/2)*(a+b*sin(e+f*x)))' 120
