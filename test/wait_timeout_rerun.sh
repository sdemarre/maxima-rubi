#!/bin/bash
# Wait for a timeout re-check's driver processes (pids from
# <run-dir>/pids) to exit, then run the subset merge
# (test/merge_timeout_rerun.py) into
# <run-dir>/<basename of the source record minus .out>.timeout<cap>s.out,
# where the cap suffix is read from a driver shard header (the cap
# actually run — standing value 100 s; the earlier 300 s re-checks kept
# the .timeout5m.out name).
# Launched detached (setsid) by the session that started the run:
#   setsid sh test/wait_timeout_rerun.sh <run-dir> >> <run-dir>/wait.log 2>&1 &
# Merge transcript: <run-dir>/merge.out.

cd "$(dirname "$0")/.." || exit 1   # this script lives in test/
RUN_DIR="${1:-/tmp/opencode/timeout_recheck}"
SRC=$(cat "$RUN_DIR/source" 2>/dev/null || echo test/corpus_class1.out)
# All shards have finished by here, so the header (and hence the cap)
# is available; the fallback is the standing value.
FIRST_SHARD=$(ls "$RUN_DIR"/shard*.out 2>/dev/null | head -1)
CAP=$(sed -n 's/^.*timeout: \([0-9][0-9]*\)s.*/\1/p' "$FIRST_SHARD" 2>/dev/null | head -1)
OUT_NAME=$(basename "$SRC" .out).timeout${CAP:-100}s.out
pids=$(awk '{print $2}' "$RUN_DIR/pids")
echo "$(date -u '+%F %T UTC') watcher: run-dir: $RUN_DIR"
echo "$(date -u '+%F %T UTC') watcher: source record: $SRC"
echo "$(date -u '+%F %T UTC') watcher: out-name: $OUT_NAME (cap: ${CAP:-fallback-100} s)"
echo "$(date -u '+%F %T UTC') watcher: waiting for pids: $pids"
for pid in $pids; do
  while kill -0 "$pid" 2>/dev/null; do sleep 120; done
done
echo "$(date -u '+%F %T UTC') watcher: all shards exited; merging"
python3 test/merge_timeout_rerun.py "$RUN_DIR/shard*.out" \
    "$RUN_DIR/$OUT_NAME" "$SRC" > "$RUN_DIR/merge.out" 2>&1
rc=$?
echo "$(date -u '+%F %T UTC') watcher: merge rc=$rc" >> "$RUN_DIR/merge.out"
exit $rc
