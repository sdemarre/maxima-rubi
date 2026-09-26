#!/bin/sh
# test/class_ports_final.sh -- the final re-measure of all eight classes on
# class-ports after class-ports-fixes (fixes V/E/D/B, EqQ, tickets 18/19,
# A/C) and the master merge, chained in ONE detached script:
#   1. every class, queue runner, 24 workers, 30 s cpu cap -> the plain
#      record names (test/corpus_class<N>.out);
#   2. A/B each against its pre-fix class-ports record (.ports.out) and the
#      earlier classes against master's promoted baselines;
#   3. baseline vs package A/B for the four new classes;
#   4. the 100 s timeout re-check of the four new classes (class 4 on a
#      seeded 600-entry sample when it has more than 1,500 timeouts).
#   setsid sh test/class_ports_final.sh > test/class_ports_final.log 2>&1 < /dev/null &
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
     "test/final_merge_$slug.out" "$1" "$3" test/corpus_driver.py "corpus_$slug.shard*.out" || return 1
  echo "$(date '+%F %T %Z') merged $3"; grep "Results:" "$3"
}

for spec in "2 Exponentials" "8 Special functions" "3 Logarithms" "5 Inverse trig functions" \
            "6 Hyperbolic functions" "7 Inverse hyperbolic functions" "4 Trig functions" "1 Algebraic functions"; do
  n=$(echo "$spec" | cut -d' ' -f1)
  run_class "$spec" "test/corpus_class$n.ports.out" "test/corpus_class$n.final.out" || { echo "FAILED class $n"; continue; }
  python3 test/ab_records.py "test/corpus_class$n.ports.out" "test/corpus_class$n.final.out" --all \
    > "test/final_ab_prefix_class$n.out" 2>&1
  case $n in
    1|2|3|6) python3 test/ab_records.py "test/corpus_class$n.out" "test/corpus_class$n.final.out" --all \
               > "test/final_ab_master_class$n.out" 2>&1
             echo "== class $n vs master baseline"; sed -n 5,9p "test/final_ab_master_class$n.out";;
    *)       python3 test/ab_records.py "test/corpus_class$n.baseline.out" "test/corpus_class$n.final.out" \
               > "test/final_ab_baseline_class$n.out" 2>&1
             echo "== class $n vs native baseline"; sed -n 5,9p "test/final_ab_baseline_class$n.out";;
  esac
done

for spec in "8 Special functions" "5 Inverse trig functions" "7 Inverse hyperbolic functions" "4 Trig functions"; do
  n=$(echo "$spec" | cut -d' ' -f1)
  src="test/corpus_class$n.final.out"
  nt=$(grep -cE "^timeout +t=" "$src")  # entry lines only: "^timeout " also matched the Results summary (off by one, 2026-09-26)
  [ "$nt" -gt 0 ] || { echo "class $n: no timeouts"; continue; }
  if [ "$nt" -gt 1500 ]; then
    python3 - "$src" "test/corpus_class$n.final.timeout-sample.out" <<'PY'
import random, sys
lines = open(sys.argv[1]).read().splitlines()
hdr = lines[:lines.index('') + 1]
to = [l for l in lines if l.startswith('timeout ')]
random.seed(20260925)
idx = {l: i for i, l in enumerate(lines)}
s = sorted(random.sample(to, 600), key=idx.get)
hdr[0] += " -- SEEDED SAMPLE (random.seed(20260925)) of 600 of its %d timeout lines" % len(to)
open(sys.argv[2], 'w').write('\n'.join(hdr) + '\n' + '\n'.join(s) + '\n')
PY
    src="test/corpus_class$n.final.timeout-sample.out"
  fi
  dir="test/corpus_class$n.final.timeout-rerun"
  rm -rf "$dir"; mkdir -p "$dir"
  python3 test/run_corpus_queue.py "$spec" --entries-from "$src" --class timeout \
    --out-dir "$dir" --cap 100 --workers 12 --launch || { echo "FAILED re-check launch $n"; continue; }
  for pid in $(awk '{print $2}' "$dir/pids"); do while kill -0 "$pid" 2>/dev/null; do sleep 30; done; done
  sh test/wait_timeout_rerun.sh "$dir" >> "$dir/wait.log" 2>&1
  echo "$(date '+%F %T %Z') re-check class $n done ($nt timeouts)"; tail -12 "$dir/merge.out" 2>/dev/null
done
echo "$(date '+%F %T %Z') ALL DONE"
