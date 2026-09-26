#!/bin/sh
# test/polylog_li_measure.sh -- the full-corpus measure of the native
# polylogarithm (.scratch/polylog-native-li/issues/01), chained in ONE
# detached script:
#   1. classes 2-8 (every class whose corpus or rules carry PolyLog), queue
#      runner, 24 workers, 30 s cpu cap -> test/corpus_class<N>.li.out;
#   2. A/B each against the promoted record test/corpus_class<N>.out
#      (test/li_ab_class<N>.out, --all);
#   3. a noise re-check of every PASS->FAIL entry: the same entries again on
#      the same core at 12 workers (test/corpus_class<N>.li.recheck/).
#   setsid sh test/polylog_li_measure.sh > test/polylog_li_measure.log 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")/.." || exit 1
echo "$(date '+%F %T %Z') host check"; uptime
LOAD1=$(awk '{print int($1)}' /proc/loadavg)
if [ "$LOAD1" -gt 3 ]; then echo "REFUSING: 1-minute load $LOAD1 > 3"; exit 3; fi
sh test/build_rules_core.sh || exit 4
echo "$(date '+%F %T %Z') core: $(awk '/^fingerprint /{print $2}' test/mr_rules.core.stamp) ($(awk '/^rules /{print $2}' test/mr_rules.core.stamp) rules, $(git rev-parse --short HEAD))"

run_class() {  # $1 section  $2 prev  $3 out
  slug="class$(echo "$1" | cut -d' ' -f1)"
  echo "$(date '+%F %T %Z') start $1 -> $3"
  python3 test/run_corpus_queue.py "$1" --prev "$2" --workers 24 --launch || return 1
  sh test/wait_and_merge.sh "test/corpus_$slug.shard-pids" test/merge_class_shards.py \
     "test/li_merge_$slug.out" "$1" "$3" test/corpus_driver.py "corpus_$slug.shard*.out" || return 1
  echo "$(date '+%F %T %Z') merged $3"; grep "Results:" "$3"
}

for spec in "2 Exponentials" "8 Special functions" "3 Logarithms" "5 Inverse trig functions" \
            "6 Hyperbolic functions" "7 Inverse hyperbolic functions" "4 Trig functions"; do
  n=$(echo "$spec" | cut -d' ' -f1)
  run_class "$spec" "test/corpus_class$n.out" "test/corpus_class$n.li.out" || { echo "FAILED class $n"; continue; }
  python3 test/ab_records.py "test/corpus_class$n.out" "test/corpus_class$n.li.out" --all \
    > "test/li_ab_class$n.out" 2>&1
  echo "== class $n vs promoted"; sed -n 5,9p "test/li_ab_class$n.out"
done

for spec in "2 Exponentials" "8 Special functions" "3 Logarithms" "5 Inverse trig functions" \
            "6 Hyperbolic functions" "7 Inverse hyperbolic functions" "4 Trig functions"; do
  n=$(echo "$spec" | cut -d' ' -f1)
  [ -f "test/corpus_class$n.li.out" ] || continue
  src="test/corpus_class$n.li.pf.out"
  # the new record's PASS->FAIL lines, relabelled `recheck` for the subset mode
  python3 - "test/corpus_class$n.out" "test/corpus_class$n.li.out" "$src" <<'PY'
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
    if m and old.get((m.group(3), m.group(4))) in PASS and m.group(1) not in PASS:
        out.append("recheck" + m.group(2))
hdr[0] += " -- PASS->FAIL subset vs %s (%d lines)" % (sys.argv[1], len(out))
open(sys.argv[3], 'w').write('\n'.join(hdr) + '\n' + '\n'.join(out) + '\n')
print(len(out))
PY
  npf=$(grep -c '^recheck ' "$src")
  [ "$npf" -gt 0 ] || { echo "class $n: no PASS->FAIL"; continue; }
  dir="test/corpus_class$n.li.recheck"
  rm -rf "$dir"; mkdir -p "$dir"
  python3 test/run_corpus_queue.py "$spec" --entries-from "$src" --class recheck \
    --out-dir "$dir" --workers 12 --launch || { echo "FAILED re-check launch $n"; continue; }
  for pid in $(awk '{print $2}' "$dir/pids"); do while kill -0 "$pid" 2>/dev/null; do sleep 20; done; done
  echo "$(date '+%F %T %Z') re-check class $n done ($npf PASS->FAIL)"
  cat "$dir"/shard*.out | grep -E '^[a-z-]+ +t=' | awk '{print $1}' | sort | uniq -c
done
echo "$(date '+%F %T %Z') ALL DONE"
