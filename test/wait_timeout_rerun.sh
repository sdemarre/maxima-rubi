#!/bin/bash
# Wait for the 300 s timeout re-check driver processes (pids from
# /tmp/opencode/timeout_recheck/pids) to exit, then run the subset
# merge (test/merge_timeout_rerun.py). Launched detached (setsid) by
# the session that started the run.
# Merge transcript: test/timeout_rerun_merge.out

cd "$(dirname "$0")/.." || exit 1   # this script lives in test/
pids=$(awk '{print $2}' /tmp/opencode/timeout_recheck/pids)
echo "$(date -u '+%F %T UTC') watcher: waiting for pids: $pids"
for pid in $pids; do
  while kill -0 "$pid" 2>/dev/null; do sleep 120; done
done
echo "$(date -u '+%F %T UTC') watcher: all shards exited; merging"
python3 test/merge_timeout_rerun.py > test/timeout_rerun_merge.out 2>&1
rc=$?
echo "$(date -u '+%F %T UTC') watcher: merge rc=$rc" >> test/timeout_rerun_merge.out
exit $rc
