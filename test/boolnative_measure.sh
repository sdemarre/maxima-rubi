#!/bin/sh
# test/boolnative_measure.sh -- the full-corpus A/B of ticket 21 step 1 (the
# native boolean-leak check, f80724a), chained in ONE detached script (the
# harness of test/pfs_measure.sh):
#   1. every class, queue runner, 24 workers, 30 s cpu cap, on this tree's
#      core -> test/corpus_class<N>.boolnative.out;
#   2. A/B each against the promoted baseline test/corpus_class<N>.out
#      (8de7080: e4311e6's code, 43abba9 comment-only)
#      -> test/boolnative_ab_class<N>.out (--all);
#   3. every transition re-run at 12 workers on BOTH cores: this tree's and
#      HEAD_CORE (the pre-change core, built at 8de7080);
#      test/boolnative_attr_class<N>.out has the per-entry verdicts, FIX = the
#      two cores disagree (the change's effect).
# The change must be invisible to verdicts except through time: expected
# transitions are timeout -> PASS; every PASS -> FAIL is a defect until
# attributed.
#   HEAD_CORE=<dir with mr_rules.core + .stamp> \
#   setsid sh test/boolnative_measure.sh > test/boolnative_measure.log 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")/.." || exit 1
: "${HEAD_CORE:?set HEAD_CORE to the directory holding master's mr_rules.core}"
[ -f "$HEAD_CORE/mr_rules.core" ] && [ -f "$HEAD_CORE/mr_rules.core.stamp" ] || { echo "no core in $HEAD_CORE"; exit 2; }
echo "$(date '+%F %T %Z') host check"; uptime
LOAD1=$(awk '{print int($1)}' /proc/loadavg)
if [ "$LOAD1" -gt 3 ]; then echo "REFUSING: 1-minute load $LOAD1 > 3"; exit 3; fi
sh test/build_rules_core.sh || exit 4
echo "$(date '+%F %T %Z') variant core: $(awk '/^fingerprint /{print $2}' test/mr_rules.core.stamp) ($(awk '/^rules /{print $2}' test/mr_rules.core.stamp) rules, $(git rev-parse --short HEAD))"
echo "$(date '+%F %T %Z') head core:    $(awk '/^fingerprint /{print $2}' "$HEAD_CORE/mr_rules.core.stamp") ($(awk '/^git_rev /{print $2}' "$HEAD_CORE/mr_rules.core.stamp"))"

run_class() {  # $1 section  $2 prev  $3 out
  slug="class$(echo "$1" | cut -d' ' -f1)"
  echo "$(date '+%F %T %Z') start $1 -> $3"
  python3 test/run_corpus_queue.py "$1" --prev "$2" --workers 24 --launch || return 1
  sh test/wait_and_merge.sh "test/corpus_$slug.shard-pids" test/merge_class_shards.py \
     "test/boolnative_merge_$slug.out" "$1" "$3" test/corpus_driver.py "corpus_$slug.shard*.out" || return 1
  echo "$(date '+%F %T %Z') merged $3"; grep "Results:" "$3"
}

CLASSES="2 Exponentials|8 Special functions|3 Logarithms|5 Inverse trig functions|6 Hyperbolic functions|7 Inverse hyperbolic functions|4 Trig functions|1 Algebraic functions"

IFS='|'
for spec in $CLASSES; do
  unset IFS
  n=$(echo "$spec" | cut -d' ' -f1)
  run_class "$spec" "test/corpus_class$n.out" "test/corpus_class$n.boolnative.out" || { echo "FAILED class $n"; IFS='|'; continue; }
  python3 test/ab_records.py "test/corpus_class$n.out" "test/corpus_class$n.boolnative.out" --all \
    > "test/boolnative_ab_class$n.out" 2>&1
  echo "== class $n vs promoted"; sed -n 5,9p "test/boolnative_ab_class$n.out"
  IFS='|'
done

for spec in $CLASSES; do
  unset IFS
  n=$(echo "$spec" | cut -d' ' -f1)
  new="test/corpus_class$n.boolnative.out"
  [ -f "$new" ] || { IFS='|'; continue; }
  src="test/corpus_class$n.boolnative.tr.out"
  # every transition vs the promoted record, relabelled `recheck`
  python3 - "test/corpus_class$n.out" "$new" "$src" <<'PY'
import re, sys
R = re.compile(r"^(\S+)(\s+t=\s*[\d.]+s\s+(.*) e(\d+) L(\d+)\s*)$")
PASS = {"verified", "expected"}
def rec(p):
    return {(m.group(3), m.group(4)): m.group(1) for m in map(R.match, open(p).read().splitlines()) if m}
old = rec(sys.argv[1])
lines = open(sys.argv[2]).read().splitlines()
hdr = lines[:lines.index('') + 1]
out = []
for l in lines:
    m = R.match(l)
    if m and ((old.get((m.group(3), m.group(4))) in PASS) != (m.group(1) in PASS)):
        out.append("recheck" + m.group(2))
hdr[0] += " -- transition subset vs %s (%d lines)" % (sys.argv[1], len(out))
open(sys.argv[3], 'w').write('\n'.join(hdr) + '\n' + '\n'.join(out) + '\n')
PY
  ntr=$(grep -c '^recheck ' "$src")
  [ "$ntr" -gt 0 ] || { echo "class $n: no transitions"; IFS='|'; continue; }
  for arm in variant head; do
    dir="test/corpus_class$n.boolnative.recheck-$arm"
    rm -rf "$dir"; mkdir -p "$dir"
    if [ "$arm" = head ]; then
      MR_RULES_CORE_PATH="$HEAD_CORE/mr_rules.core" python3 test/run_corpus_queue.py "$spec" --entries-from "$src" \
        --class recheck --out-dir "$dir" --workers 12 --launch || { echo "FAILED re-check launch $n $arm"; continue; }
    else
      python3 test/run_corpus_queue.py "$spec" --entries-from "$src" \
        --class recheck --out-dir "$dir" --workers 12 --launch || { echo "FAILED re-check launch $n $arm"; continue; }
    fi
    for pid in $(awk '{print $2}' "$dir/pids"); do while kill -0 "$pid" 2>/dev/null; do sleep 20; done; done
    echo "$(date '+%F %T %Z') re-check class $n $arm done ($ntr transitions)"
  done
  python3 - "test/corpus_class$n.out" "$new" "test/corpus_class$n.boolnative.recheck-variant" \
            "test/corpus_class$n.boolnative.recheck-head" > "test/boolnative_attr_class$n.out" <<'PY'
import glob, re, sys
from collections import Counter
R = re.compile(r"^(\S+)\s+t=\s*[\d.]+s\s+(.*) e(\d+) L(\d+)\s*$")
PASS = {"verified", "expected"}
def rec(paths):
    d = {}
    for p in paths:
        for l in open(p).read().splitlines():
            m = R.match(l)
            if m: d[(m.group(2), m.group(3))] = m.group(1)
    return d
old, new = rec([sys.argv[1]]), rec([sys.argv[2]])
rv = rec(sorted(glob.glob(sys.argv[3] + "/shard*.out")))
rh = rec(sorted(glob.glob(sys.argv[4] + "/shard*.out")))
P = lambda v: "PASS" if v in PASS else ("FAIL" if v else "----")
buckets = Counter()
rows = []
for k in sorted(rv.keys() | rh.keys()):
    o, nv, a, b = old.get(k), new.get(k), rv.get(k), rh.get(k)
    direction = "P->F" if P(o) == "PASS" else "F->P"
    if a is None or b is None: why = "incomplete"
    elif P(a) != P(b): why = "FIX " + ("loss" if P(b) == "PASS" else "gain")
    elif P(b) == P(o): why = "noise (both cores agree with promoted)"
    else: why = "drift (both cores agree with the variant run)"
    buckets[(direction, why)] += 1
    rows.append("%s  %-44s promoted=%-12s variant=%-12s re-variant=%-12s re-head=%-12s %s e%s" % (
        direction, why, o, nv, a, b, k[0], k[1]))
print("# columns: direction vs promoted; attribution; verdicts")
print("# FIX = the two cores disagree on the same entry at the same load (the fix's effect)")
for (d, w), c in sorted(buckets.items()): print("%5d  %s  %s" % (c, d, w))
print()
print("\n".join(rows))
PY
  echo "== class $n attribution"; sed -n '3,/^$/p' "test/boolnative_attr_class$n.out"
  IFS='|'
done
unset IFS
echo "$(date '+%F %T %Z') ALL DONE"
