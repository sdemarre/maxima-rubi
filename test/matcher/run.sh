#!/bin/sh
# test/matcher/run.sh -- the matcher regression suite (matcher substrate spec
# section 4, P1/P2 gates).  From anywhere:  sh test/matcher/run.sh
# Env:
#   MR_LEGS         tree (default) | tree,maxima
#   MR_MODEL_FLAGS  1: the Maxima leg simplifies under radexpand:false and
#                   logexpand:false; outputs are roundtrip.flags.out / gate.flags.out
#   MR_SPIKE        1: also run the spike-01 cases (test/matcher/spike01.out) and gate them
#   MR_WORK         work dir (default ${TMPDIR:-/tmp}/mr-matcher-suite[.flags])
# Prints the gate's Results line.
set -u
cd "$(dirname "$0")/../.."
N=20
LEGS=${MR_LEGS:-tree}
FLAGS=${MR_MODEL_FLAGS:-0}
SUFFIX=""
[ "$FLAGS" = 1 ] && SUFFIX=".flags"
WORK=${MR_WORK:-${TMPDIR:-/tmp}/mr-matcher-suite$SUFFIX}
mkdir -p "$WORK"
rm -f "$WORK"/shard*.tsv "$WORK"/shard*.log
python3 probes/matcher/02-roundtrip.py gen "$WORK/cases.tsv" > "$WORK/gen.log" || exit 1
i=0
while [ "$i" -lt "$N" ]; do
  MR_CASES="$WORK/cases.tsv" MR_NSHARDS=$N MR_SHARD=$i MR_RESULTS="$WORK/shard$i.tsv" \
    MR_MODES=narrow,wide MR_LEGS=$LEGS MR_MODEL_FLAGS=$FLAGS \
    timeout 3600 maxima --very-quiet -b test/matcher/roundtrip.mac > "$WORK/shard$i.log" 2>&1 &
  i=$((i + 1))
done
wait
{
  echo "=== test/matcher round trip  legs: $LEGS  model flags: $FLAGS  judged: $(date -u '+%Y-%m-%d %H:%M UTC')"
  echo "git HEAD: $(git rev-parse HEAD)"
  MR_MODES=narrow,wide MR_LEGS=$LEGS python3 probes/matcher/02-roundtrip.py judge "$WORK" "$N"
} > "test/matcher/roundtrip$SUFFIX.out"
python3 probes/matcher/02-roundtrip.py controls > "$WORK/controls-data.lisp" || exit 1
MR_CONTROLS="$WORK/controls-data.lisp" timeout 600 maxima --very-quiet -b test/matcher/controls.mac 2>&1 \
  | grep '^CONTROL' > test/matcher/controls.out
GATE="--report test/matcher/roundtrip$SUFFIX.out --controls test/matcher/controls.out"
case "$LEGS" in *maxima*) GATE="$GATE --maxima" ;; esac
if [ "${MR_SPIKE:-0}" = 1 ]; then
  timeout 600 maxima --very-quiet -b test/matcher/spike01.mac 2>&1 | grep '^SPIKE' > test/matcher/spike01.out
  GATE="$GATE --spike test/matcher/spike01.out"
fi
python3 test/matcher/gate.py $GATE > "test/matcher/gate$SUFFIX.out"
tail -1 "test/matcher/gate$SUFFIX.out"
