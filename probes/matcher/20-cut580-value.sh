#!/bin/sh
# probes/matcher/20-cut580-value.sh -- spec 3.8's VALUE gate: re-run 0.5's 580
# expandIntegrand-cut timeouts at the 30 s cap and count how many stop timing
# out.  (The cost gate is probe 19; this is the other half.)
#
# Usage (repo root):
#   sh probes/matcher/20-cut580-value.sh > probes/matcher/20-cut580-value.out 2>&1
#
# MR_BASE=<commit> additionally re-runs the entries that did NOT time out
# through a core pinned at that commit, which is what attributes the change to
# the matcher rather than to everything else that landed since 0.5 measured the
# list.  It builds that core in a throwaway worktree (~2 min, ~113 MB).
#
# ~25 min at 12 workers.  Wants an otherwise idle machine: every verdict here is
# a cap decision, and entries near the cap flip with contention (AGENTS.md).
set -u
cd "$(dirname "$0")/../.." || exit 1
ROOT=$(pwd)
W=${TMPDIR:-/tmp}/mr-20-cut580-value
rm -rf "$W"; mkdir -p "$W/run"
BASE=${MR_BASE:-}
WORKERS=${MR_WORKERS:-12}
CUTLIST=.superpowers/sdd/2026-09-15-matcher-seen-test-intpart/prototype/outputs/cutlist-805.out

echo "=== probes/matcher/20-cut580-value  git HEAD $(git rev-parse --short HEAD)  $(date -u '+%Y-%m-%d %H:%M UTC')"
[ -f "$CUTLIST" ] || { echo "MISSING $CUTLIST"; exit 1; }

# 0.5's list -> a record the queue runner's --entries-from accepts
python3 - "$CUTLIST" "$W/cut580.record" <<'PY'
import sys, pathlib, collections
src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
n, lines = collections.Counter(), []
for line in src.read_text().splitlines():
    if line.startswith("#") or not line.strip():
        continue
    f = line.split("\t")
    if len(f) < 6:
        continue
    cls, secs, rel, entry = f[0], f[1], f[4], f[5]
    n[cls] += 1
    if cls == "timeout":
        lines.append(f"{cls} t= {secs}s {rel} {entry} L1")
out.write_text("\n".join(lines) + "\n")
print("R cutlist classes %s" % dict(n))
print("R timeout entries %d" % len(lines))
PY

run_arm() { # <out-dir> [<pinned core>]
  dir=$1
  mkdir -p "$dir"
  env ${2:+MR_RULES_CORE_PATH="$2"} \
    python3 "$ROOT/test/run_corpus_queue.py" "1 Algebraic functions" \
      --entries-from "$W/cut580.record" --class timeout \
      --out-dir "$dir" --workers "$WORKERS" --cap 30 --launch \
      > "$dir/launch.log" 2>&1 || return 1
  while kill -0 "$(head -1 "$dir/pids")" 2>/dev/null; do sleep 10; done
}

echo "=== arm: the tree"
run_arm "$W/run" || exit 1
python3 - "$W/run" "$ROOT" <<'PY'
import sys, glob, collections
sys.path.insert(0, sys.argv[2] + "/test")
import run_corpus_queue as q
rec = {}
for f in sorted(glob.glob(sys.argv[1] + "/shard*.out")):
    rec.update(q.read_record(f))
c = collections.Counter(cl for cl, _ in rec.values())
print("R entries %d  %s" % (len(rec), ", ".join(f"{k} {v}" for k, v in c.most_common())))
print("R PASS %d/%d" % (sum(v for k, v in c.items() if k in {"verified", "expected", "no-answer"}), len(rec)))
for (rel, e), (cl, t) in sorted(rec.items()):
    if cl != "timeout":
        print("R kept %-14s t=%5.1fs %s e%d" % (cl, t, rel.split("/")[-1], e))
PY

if [ -n "$BASE" ]; then
  echo "=== arm: pinned core at $BASE (attribution of the non-timeouts)"
  WT=$W/base-wt
  git worktree add -q --detach "$WT" "$BASE" || exit 1
  ( cd "$WT" && sh test/build_rules_core.sh ) > "$W/base-build.log" 2>&1 || exit 1
  grep -h '^fingerprint' "$WT/test/mr_rules.core.stamp" | sed 's/^/R base core /'
  # only the entries the tree arm did NOT time out
  python3 - "$W/run" "$ROOT" "$W/five.record" <<'PY'
import sys, glob
sys.path.insert(0, sys.argv[2] + "/test")
import run_corpus_queue as q
rec = {}
for f in sorted(glob.glob(sys.argv[1] + "/shard*.out")):
    rec.update(q.read_record(f))
keep = [f"timeout t= 30.0s {rel} e{e} L1" for (rel, e), (cl, _t) in sorted(rec.items()) if cl != "timeout"]
open(sys.argv[3], "w").write("\n".join(keep) + "\n")
print("R attribution entries %d" % len(keep))
PY
  cp "$W/five.record" "$W/cut580.record"
  run_arm "$W/base" "$WT/test/mr_rules.core" || exit 1
  run_arm "$W/tree5" || exit 1
  python3 - "$W/base" "$W/tree5" "$ROOT" <<'PY'
import sys, glob
sys.path.insert(0, sys.argv[3] + "/test")
import run_corpus_queue as q
def read(d):
    rec = {}
    for f in sorted(glob.glob(d + "/shard*.out")):
        rec.update(q.read_record(f))
    return rec
base, tree = read(sys.argv[1]), read(sys.argv[2])
for k in sorted(set(base) | set(tree)):
    rel, e = k
    b, t = base.get(k), tree.get(k)
    fmt = lambda v: ("%s t=%5.1fs" % v) if v else "-"
    same = "SAME" if (b and t and b[0] == t[0]) else "DIFFER"
    print("R attr %-6s base %-24s tree %-24s  %s e%d" % (same, fmt(b), fmt(t), rel.split("/")[-1], e))
PY
  git worktree remove --force "$WT" 2>/dev/null
fi
echo "=== done"
