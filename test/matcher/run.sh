#!/bin/sh
# test/matcher/run.sh -- the matcher regression suite (matcher substrate spec
# section 4, P1/P2 gates).  From anywhere:  sh test/matcher/run.sh
# Tree leg ~1 min wall with 20 shards.  Writes test/matcher/roundtrip.out,
# test/matcher/controls.out, test/matcher/gate.out; prints the gate's Results line.
# Env: MR_LEGS (default tree), MR_WORK (work dir, default ${TMPDIR:-/tmp}/mr-matcher-suite).
set -u
cd "$(dirname "$0")/../.."
N=20
LEGS=${MR_LEGS:-tree}
WORK=${MR_WORK:-${TMPDIR:-/tmp}/mr-matcher-suite}
mkdir -p "$WORK"
rm -f "$WORK"/shard*.tsv "$WORK"/shard*.log
python3 probes/matcher/02-roundtrip.py gen "$WORK/cases.tsv" > "$WORK/gen.log" || exit 1
i=0
while [ "$i" -lt "$N" ]; do
  MR_CASES="$WORK/cases.tsv" MR_NSHARDS=$N MR_SHARD=$i MR_RESULTS="$WORK/shard$i.tsv" \
    MR_MODES=narrow,wide MR_LEGS=$LEGS \
    timeout 3600 maxima --very-quiet -b test/matcher/roundtrip.mac > "$WORK/shard$i.log" 2>&1 &
  i=$((i + 1))
done
wait
{
  echo "=== test/matcher round trip  legs: $LEGS  judged: $(date -u '+%Y-%m-%d %H:%M UTC')"
  echo "git HEAD: $(git rev-parse HEAD)"
  MR_MODES=narrow,wide MR_LEGS=$LEGS python3 probes/matcher/02-roundtrip.py judge "$WORK" "$N"
} > test/matcher/roundtrip.out
python3 probes/matcher/02-roundtrip.py controls > "$WORK/controls-data.lisp" || exit 1
MR_CONTROLS="$WORK/controls-data.lisp" timeout 600 maxima --very-quiet -b test/matcher/controls.mac 2>&1 \
  | grep '^CONTROL' > test/matcher/controls.out
python3 test/matcher/gate.py --report test/matcher/roundtrip.out --controls test/matcher/controls.out \
  > test/matcher/gate.out
tail -1 test/matcher/gate.out
