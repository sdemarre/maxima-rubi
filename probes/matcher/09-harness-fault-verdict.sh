#!/bin/sh
# probes/matcher/09-harness-fault-verdict.sh -- the corpus harness's verdict
# on an entry whose Maxima process meets a fatal SBCL error (matcher
# substrate plan 3, Task 1: the carried "crash-class counts vs P0" item;
# probe 07 found control-stack exhaustion inside mr-match:match fatal).
# The shape is probe 07's matchq_cond_named: a runaway recursion in a
# MatchQ condition.
#   A  plain load (the substrate files loaded with load(), as probe 07),
#      stdin /dev/null
#   B  plain load, stdin an open pipe (what a driver subprocess inherits
#      when nothing redirects its stdin)
#   C  the rules core (test/mr_rules.core, the image the harness runs),
#      stdin /dev/null
#   D  test/corpus_driver.py on a one-file synthetic suite (e1 the shape,
#      e2 the control x^2), standard-load path (MR_RULES_CORE=0), stdin an
#      open pipe
#   E  the same through the rules core
# Usage (repo root; needs a current core: sh test/build_rules_core.sh):
#   sh probes/matcher/09-harness-fault-verdict.sh > probes/matcher/09-harness-fault-verdict.out 2>&1
set -u
cd "$(dirname "$0")/../.." || exit 1
export LC_ALL=C
W=${TMPDIR:-/tmp}/mr-09-harness-fault
rm -rf "$W"; mkdir -p "$W/suite/crash"
cat > "$W/cond.mac" <<'EOF'
display2d : false$
t_r1(a) := t_r1(a)$
w0(a) := t_r1(a)$
t_c1(b) := w0(1)$
print("R result", %mr_matchQ(x, "(Pattern |_u| (Blank))", [], t_c1))$
print("R SURVIVED")$
EOF
{ printf 'load("maxima_rubi_match.lisp")$\nload("maxima_rubi_tree.lisp")$\nload("maxima_rubi_utils.mac")$\nload("maxima_rubi_dispatch.lisp")$\n'
  cat "$W/cond.mac"; } > "$W/plain.mac"
cat > "$W/suite/crash/c.mac" <<'EOF'
/* probe 09 synthetic suite: e1 probe 07's matchq_cond_named shape, e2 a control */
lst: '[
[(t_r1(a) := t_r1(a), w0(a) := t_r1(a), t_c1(b) := w0(1), %mr_matchQ(x, "(Pattern |_u| (Blank))", [], t_c1)),x,0,x],
[x^2,x,1,x^3/3]]$
EOF
now() { date +%s.%N; }
row() { # label out-file rc start end
  printf '%-32s rc=%-4s wall=%5.1fs survived=%s fatal-pseudo=%s ldb=%s guard-page=%s\n' "$1" "$3" \
    "$(echo "$5 - $4" | bc)" "$(grep -ac '^R SURVIVED' "$2")" "$(grep -ac 'while pseudo-atomic' "$2")" \
    "$(grep -ac 'ldb>' "$2")" "$(grep -ac 'guard page unprotected' "$2")"
}
echo "=== probes/matcher/09-harness-fault-verdict  git HEAD $(git rev-parse --short HEAD)  $(date -u '+%Y-%m-%d %H:%M UTC')"
timeout -s KILL 60 maxima --very-quiet --batch-string='print("R build", build_info()@version, build_info()@timestamp)$' < /dev/null 2>&1 | grep -a '^R build'
echo "R core $(head -1 test/mr_rules.core.stamp)"
s=$(now); timeout -s KILL 60 maxima --very-quiet -b "$W/plain.mac" < /dev/null > "$W/A.out" 2>&1; rc=$?
row "A plain load, stdin /dev/null" "$W/A.out" $rc "$s" "$(now)"
s=$(now); bash -c "timeout -s KILL 40 maxima --very-quiet -b $W/plain.mac < <(sleep 60)" > "$W/B.out" 2>&1; rc=$?
row "B plain load, stdin open pipe" "$W/B.out" $rc "$s" "$(now)"
s=$(now); timeout -s KILL 60 sbcl --tls-limit 100000 --core test/mr_rules.core --noinform --very-quiet -b "$W/cond.mac" < /dev/null > "$W/C.out" 2>&1; rc=$?
row "C rules core, stdin /dev/null" "$W/C.out" $rc "$s" "$(now)"
for mode in D E; do
  case $mode in
    D) core=0; label="D driver, standard load, pipe" ;;
    E) core=1; label="E driver, rules core, pipe" ;;
  esac
  MR_RULES_CORE=$core bash -c "python3 test/corpus_driver.py crash/ 999999 30 $W/suite 0 '' 0 $W/$mode.drv.out < <(sleep 60)" > "$W/$mode.drv.log" 2>&1
  printf '%-32s %s\n' "$label" "$(grep -a 'crash/c.mac' "$W/$mode.drv.out" | tr -s ' ' | tr '\n' '|')"
done
echo "=== done"
