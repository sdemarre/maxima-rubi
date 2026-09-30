#!/bin/sh
# test/checker2_measure.sh -- ONE full-corpus arm after the two checker fixes
# found on arm 1's losses (breadth-first stages, 477f2d2; every function's
# arguments rectformed in the numeric check, 648c6a4; probes/verify-stages/
# 13-15). Same rules as test/checker_measure.sh's arm 2 (coeff-together), so
# the A/B against its records isolates the checker change:
#   arm "chk2-head": this tree -> test/corpus_class<N>.chk2-head.out, A/B vs
#          test/corpus_class<N>.chk-head.out -> test/chk2_ab_class<N>.out;
#          proof census -> test/corpus_class<N>.chk2-head.proof.out;
#   every PASS->FAIL re-run at 12 workers on the same setup
#          -> test/chk2_attr_class<N>.out (reproduces / noise).
# 24 workers (user decision 2026-09-29). Resumes like checker_measure.sh.
#   setsid sh test/checker2_measure.sh > test/checker2_measure.log 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")/.." || exit 1
echo "$(date '+%F %T %Z') host check"; uptime
LOAD1=$(awk '{print int($1)}' /proc/loadavg)
if [ "$LOAD1" -gt 3 ]; then echo "REFUSING: 1-minute load $LOAD1 > 3"; exit 3; fi
sh test/build_rules_core.sh || exit 4
echo "$(date '+%F %T %Z') core: $(awk '/^fingerprint /{print $2}' test/mr_rules.core.stamp) ($(git rev-parse --short HEAD))"

CLASSES="2 Exponentials|8 Special functions|3 Logarithms|5 Inverse trig functions|6 Hyperbolic functions|7 Inverse hyperbolic functions|4 Trig functions|1 Algebraic functions"

run_class() {  # $1 section  $2 prev  $3 out  $4 arm
  slug="class$(echo "$1" | cut -d' ' -f1)"
  # RESUME: a merged record is only ever written complete (the merger refuses
  # otherwise), so one that exists is kept; its census is made if missing
  # (the shards stay until the next launch of the same class).
  if [ -f "$3" ]; then
    echo "$(date '+%F %T %Z') keep $4 $1: $3 exists"
    [ -f "${3%.out}.proof.out" ] || python3 test/merge_proof.py "$3" "${3%.out}.proof.out" \
      > "test/chk_proofmerge_${4}_$slug.out" 2>&1 || echo "PROOF MERGE FAILED $4 $slug"
    return 0
  fi
  echo "$(date '+%F %T %Z') start $4 $1 -> $3"
  if [ "$4" = chk-master ]; then
    MR_RULES_CORE_PATH="$MASTER_CORE/mr_rules.core" python3 test/run_corpus_queue.py "$1" --prev "$2" --workers 24 --launch || return 1
  else
    python3 test/run_corpus_queue.py "$1" --prev "$2" --workers 24 --launch || return 1
  fi
  sh test/wait_and_merge.sh "test/corpus_$slug.shard-pids" test/merge_class_shards.py \
     "test/chk_merge_${4}_$slug.out" "$1" "$3" test/corpus_driver.py "corpus_$slug.shard*.out" || return 1
  python3 test/merge_proof.py "$3" "${3%.out}.proof.out" > "test/chk_proofmerge_${4}_$slug.out" 2>&1 \
    || echo "PROOF MERGE FAILED $4 $slug"
  echo "$(date '+%F %T %Z') merged $3"; grep "Results:" "$3"
}

subset() {  # $1 old  $2 new  $3 out  $4 only-losses
  python3 - "$1" "$2" "$3" "$4" <<'PY'
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
    if not m:
        continue
    was, now = old.get((m.group(3), m.group(4))) in PASS, m.group(1) in PASS
    if was != now and (sys.argv[4] != "1" or was):
        out.append("recheck" + m.group(2))
hdr[0] += " -- transition subset vs %s (%d lines)" % (sys.argv[1], len(out))
open(sys.argv[3], 'w').write('\n'.join(hdr) + '\n' + '\n'.join(out) + '\n')
PY
}

recheck() {  # $1 section  $2 subset  $3 dir  $4 core-or-empty
  rm -rf "$3"; mkdir -p "$3"
  if [ -n "$4" ]; then
    MR_RULES_CORE_PATH="$4" python3 test/run_corpus_queue.py "$1" --entries-from "$2" \
      --class recheck --out-dir "$3" --workers 12 --launch || { echo "FAILED re-check launch $3"; return 1; }
  else
    python3 test/run_corpus_queue.py "$1" --entries-from "$2" \
      --class recheck --out-dir "$3" --workers 12 --launch || { echo "FAILED re-check launch $3"; return 1; }
  fi
  for pid in $(awk '{print $2}' "$3/pids"); do while kill -0 "$pid" 2>/dev/null; do sleep 20; done; done
  rm -f "$3/pids"
}

attr() {  # $1 old  $2 new  $3 dir-a  $4 dir-b-or-empty
  python3 - "$1" "$2" "$3" "$4" <<'PY'
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
ra = rec(sorted(glob.glob(sys.argv[3] + "/shard*.out")))
rb = rec(sorted(glob.glob(sys.argv[4] + "/shard*.out"))) if sys.argv[4] else None
P = lambda v: "PASS" if v in PASS else ("FAIL" if v else "----")
buckets, rows = Counter(), []
for k in sorted(ra.keys() | (rb.keys() if rb else set())):
    o, nv, a = old.get(k), new.get(k), ra.get(k)
    b = rb.get(k) if rb is not None else None
    direction = "P->F" if P(o) == "PASS" else "F->P"
    if rb is None:
        why = ("incomplete" if a is None else
               "reproduces (the new verdict)" if P(a) == P(nv) else "noise (agrees with the old record)")
    elif a is None or b is None: why = "incomplete"
    elif P(a) != P(b): why = "FIX " + ("gain" if P(a) == "PASS" else "loss")
    elif P(a) == P(o): why = "noise (both cores agree with the old record)"
    else: why = "drift (both cores agree with the new run)"
    buckets[(direction, why)] += 1
    rows.append("%s  %-44s old=%-12s new=%-12s re-a=%-12s re-b=%-12s %s e%s" % (
        direction, why, o, nv, a, b, k[0], k[1]))
print("# re-a: the new record's own setup; re-b: the other core (arm 2 only)")
print("# FIX = the two cores disagree on the same entry at the same load (the rule fixes' effect)")
for (d, w), c in sorted(buckets.items()): print("%5d  %s  %s" % (c, d, w))
print()
print("\n".join(rows))
PY
}

arm=chk2-head
IFS='|'
for spec in $CLASSES; do
  unset IFS
  n=$(echo "$spec" | cut -d' ' -f1)
  base="test/corpus_class$n.chk-head.out"; new="test/corpus_class$n.$arm.out"
  run_class "$spec" "$base" "$new" "$arm" || {
    echo "$(date '+%F %T %Z') RETRY $arm class $n; queue log tail:"
    tail -2 "test/corpus_class$n.shard-queue.log"
    run_class "$spec" "$base" "$new" "$arm"; } || { echo "FAILED $arm class $n"; IFS='|'; continue; }
  ab="test/chk2_ab_class$n.out"
  [ -f "$ab" ] || python3 test/ab_records.py "$base" "$new" --all > "$ab" 2>&1
  echo "== $arm class $n vs $base"; sed -n 5,9p "$ab"
  IFS='|'
done
unset IFS

IFS='|'
for spec in $CLASSES; do
  unset IFS
  n=$(echo "$spec" | cut -d' ' -f1)
  b="test/corpus_class$n.chk-head.out"; h="test/corpus_class$n.chk2-head.out"
  if [ -f "$h" ]; then
    subset "$b" "$h" "test/corpus_class$n.chk2-head.tr.out" 1
    if [ "$(grep -c '^recheck ' "test/corpus_class$n.chk2-head.tr.out")" -gt 0 ]; then
      recheck "$spec" "test/corpus_class$n.chk2-head.tr.out" "test/corpus_class$n.chk2-head.recheck" "" \
        && attr "$b" "$h" "test/corpus_class$n.chk2-head.recheck" "" > "test/chk2_attr_class$n.out"
      echo "$(date '+%F %T %Z') == class $n losses re-checked"; sed -n '3,/^$/p' "test/chk2_attr_class$n.out"
    else echo "class $n: no PASS->FAIL"; fi
  fi
  IFS='|'
done
unset IFS
echo "$(date '+%F %T %Z') ALL DONE"
