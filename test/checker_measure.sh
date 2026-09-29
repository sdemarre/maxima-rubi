#!/bin/sh
# test/checker_measure.sh -- the full-corpus re-run after the checker work of
# .scratch/corpus-harness/issues/06 and the coeff-together rule fixes,
# chained in ONE detached script (the harness of test/geteqr_measure.sh).
# User decisions 2026-09-29: two arms, 24 workers, numeric-only passes stay
# PASS (the .proof census keeps the split).
#   arm 1 "chk-master": MASTER's rules (the pinned core in $MASTER_CORE,
#          b62d6d7, fingerprint f2cb4fc6 -- the core of the geteqr records)
#          with THIS tree's checker -> test/corpus_class<N>.chk-master.out;
#          A/B against test/corpus_class<N>.geteqr.out isolates the CHECKER
#          (-> test/chk_ab_master_class<N>.out);
#   arm 2 "chk-head": THIS tree's rules and checker
#          -> test/corpus_class<N>.chk-head.out; A/B against arm 1 isolates the
#          RULE fixes (-> test/chk_ab_head_class<N>.out);
#   each merged record gets its proof census (test/merge_proof.py,
#          -> test/corpus_class<N>.chk-<arm>.proof.out);
#   re-checks, 12 workers:
#     arm 1 PASS->FAIL vs geteqr, re-run on arm 1's setup (a loss that does
#          not reproduce is noise; one that does is the checker's verdict)
#          -> test/chk_attr_master_class<N>.out;
#     every arm 2 vs arm 1 transition, re-run on BOTH cores (FIX = the two
#          cores disagree: the rule fixes' effect)
#          -> test/chk_attr_head_class<N>.out.
# The arms run one after the other, never concurrently. Re-launching resumes:
# a class whose merged record exists is kept, and a class that fails is tried
# once more.
#   MASTER_CORE=<dir with mr_rules.core + .stamp> \
#   setsid sh test/checker_measure.sh > test/checker_measure.log 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")/.." || exit 1
: "${MASTER_CORE:?set MASTER_CORE to the directory holding master's mr_rules.core}"
[ -f "$MASTER_CORE/mr_rules.core" ] && [ -f "$MASTER_CORE/mr_rules.core.stamp" ] || { echo "no core in $MASTER_CORE"; exit 2; }
echo "$(date '+%F %T %Z') host check"; uptime
LOAD1=$(awk '{print int($1)}' /proc/loadavg)
if [ "$LOAD1" -gt 3 ]; then echo "REFUSING: 1-minute load $LOAD1 > 3"; exit 3; fi
sh test/build_rules_core.sh || exit 4
echo "$(date '+%F %T %Z') head core:   $(awk '/^fingerprint /{print $2}' test/mr_rules.core.stamp) ($(git rev-parse --short HEAD))"
echo "$(date '+%F %T %Z') master core: $(awk '/^fingerprint /{print $2}' "$MASTER_CORE/mr_rules.core.stamp") ($(awk '/^git_rev /{print $2}' "$MASTER_CORE/mr_rules.core.stamp"))"

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

for arm in chk-master chk-head; do
  IFS='|'
  for spec in $CLASSES; do
    unset IFS
    n=$(echo "$spec" | cut -d' ' -f1)
    if [ "$arm" = chk-master ]; then base="test/corpus_class$n.geteqr.out"; else base="test/corpus_class$n.chk-master.out"; fi
    new="test/corpus_class$n.$arm.out"
    # ONE retry: 2026-09-29 15:00 the class-1 queue manager of arm 1 died
    # silently mid-run (no traceback, no OOM, no core; 18,757 entries missing)
    run_class "$spec" "$base" "$new" "$arm" || {
      echo "$(date '+%F %T %Z') RETRY $arm class $n; queue log tail:"
      tail -2 "test/corpus_class$n.shard-queue.log"
      run_class "$spec" "$base" "$new" "$arm"; } || { echo "FAILED $arm class $n"; IFS='|'; continue; }
    ab="test/chk_ab_${arm#chk-}_class$n.out"
    [ -f "$ab" ] || python3 test/ab_records.py "$base" "$new" --all > "$ab" 2>&1
    echo "== $arm class $n vs $base"; sed -n 5,9p "$ab"
    IFS='|'
  done
done
unset IFS

# the transition subset of NEW vs OLD as a record whose lines read `recheck`;
# ONLY_LOSSES=1 keeps the PASS->FAIL lines only
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

# per-entry verdicts of the re-checks against the two records they came from
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

IFS='|'
for spec in $CLASSES; do
  unset IFS
  n=$(echo "$spec" | cut -d' ' -f1)
  m="test/corpus_class$n.chk-master.out"; h="test/corpus_class$n.chk-head.out"; g="test/corpus_class$n.geteqr.out"
  if [ -f "$m" ]; then
    subset "$g" "$m" "test/corpus_class$n.chk-master.tr.out" 1
    if [ "$(grep -c '^recheck ' "test/corpus_class$n.chk-master.tr.out")" -gt 0 ]; then
      recheck "$spec" "test/corpus_class$n.chk-master.tr.out" "test/corpus_class$n.chk-master.recheck" "$MASTER_CORE/mr_rules.core" \
        && attr "$g" "$m" "test/corpus_class$n.chk-master.recheck" "" > "test/chk_attr_master_class$n.out"
      echo "$(date '+%F %T %Z') == arm 1 class $n losses re-checked"; sed -n '3,/^$/p' "test/chk_attr_master_class$n.out"
    else echo "class $n: arm 1 has no PASS->FAIL"; fi
  fi
  if [ -f "$m" ] && [ -f "$h" ]; then
    subset "$m" "$h" "test/corpus_class$n.chk-head.tr.out" 0
    if [ "$(grep -c '^recheck ' "test/corpus_class$n.chk-head.tr.out")" -gt 0 ]; then
      recheck "$spec" "test/corpus_class$n.chk-head.tr.out" "test/corpus_class$n.chk-head.recheck-head" "" \
        && recheck "$spec" "test/corpus_class$n.chk-head.tr.out" "test/corpus_class$n.chk-head.recheck-master" "$MASTER_CORE/mr_rules.core" \
        && attr "$m" "$h" "test/corpus_class$n.chk-head.recheck-head" "test/corpus_class$n.chk-head.recheck-master" > "test/chk_attr_head_class$n.out"
      echo "$(date '+%F %T %Z') == arm 2 class $n transitions re-checked"; sed -n '3,/^$/p' "test/chk_attr_head_class$n.out"
    else echo "class $n: arm 2 has no transitions"; fi
  fi
  IFS='|'
done
unset IFS
echo "$(date '+%F %T %Z') ALL DONE"
