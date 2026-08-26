#!/bin/bash
# Appends one status line every 10 minutes to test/run_status.log while the
# class-1 shards run; stops when the last shard exits. Fully detached
# (setsid), independent of any agent session.

cd "$(dirname "$0")/.." || exit 1   # this script lives in test/
LOG=test/run_status.log
echo "$(date -u '+%F %T UTC') logger started" >> "$LOG"
while true; do
  total=0
  for f in test/corpus_class1.shard*.out; do
    n=$(grep -cE '^[a-z-]+ +t=' "$f" 2>/dev/null)
    total=$((total+n))
  done
  alive=0
  for pid in $(awk '{print $2}' test/corpus_class1.shard-pids); do
    kill -0 "$pid" 2>/dev/null && alive=$((alive+1))
  done
  nshard=$(awk '{print $2}' test/corpus_class1.shard-pids | wc -l | tr -d ' ')
  echo "$(date -u '+%F %T UTC') done=$total/25697 shards_alive=$alive/$nshard" >> "$LOG"
  if [ "$alive" -eq 0 ]; then
    echo "$(date -u '+%F %T UTC') all shards done — watcher will merge" >> "$LOG"
    break
  fi
  sleep 600
done
