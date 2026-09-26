#!/bin/sh
# probes/corpus/27-class-ports-fixes-slice-select.sh -- see the .mac header.
# Usage (repo root), one phase per run:
#   sh probes/corpus/27-class-ports-fixes-slice-select.sh eqq > probes/corpus/27-class-ports-fixes-slice-select.eqq.out 2>&1
#   sh probes/corpus/27-class-ports-fixes-slice-select.sh hit > probes/corpus/27-class-ports-fixes-slice-select.hit.out 2>&1
set -u
cd "$(dirname "$0")/../.." || exit 1
ROOT=$(pwd)
PHASE=${1:?usage: $0 eqq|hit}
W=${TMPDIR:-/tmp}/mr-27-slice-select-$PHASE
rm -rf "$W"; mkdir -p "$W"
# the HIT scans' entries, extracted with the driver's own parser
python3 - "$W/hit_entries.mac" <<'PY'
import importlib.util, sys
out = sys.argv[1]
sys.argv = ["corpus_driver.py", "3 Logarithms/", "999999", "30", "reference/maxima-syntax-test-suite"]
spec = importlib.util.spec_from_file_location("cd", "test/corpus_driver.py")
d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
S = "reference/maxima-syntax-test-suite/"
files = ["2 Exponentials/2.3 Exponential functions.mac",
         "3 Logarithms/3.1.4 (f x)^m (d+e x^r)^q (a+b log(c x^n))^p.mac",
         "3 Logarithms/3.1.5 u (a+b log(c x^n))^p.mac",
         "5 Inverse trig functions/5.3 Inverse tangent/5.3.2 (d x)^m (a+b arctan(c x^n))^p.mac"]
rows = []
for f in files:
    es, _ = d.extract_entries(S + f)
    for i, e in enumerate(es, 1):
        t = d.normalize_heads(d.split_elements(e[1:-1])[0]).replace("\\", "\\\\").replace('"', '\\"')
        rows.append('["%s", %d, "%s"]' % (f, i, t))
open(out, "w").write("mr_hit_entries : [\n" + ",\n".join(rows) + "]$\n")
PY
printf 'mr_sel_phase : "%s"$\nload("%s")$\nload("%s/probes/corpus/27-class-ports-fixes-slice-select.mac")$\n' "$PHASE" "$W/hit_entries.mac" "$ROOT" > "$W/run.mac"
echo "=== probes/corpus/27-class-ports-fixes-slice-select $PHASE  git HEAD $(git rev-parse --short HEAD)  $(TZ=Europe/Brussels date '+%Y-%m-%d %H:%M %Z')"
timeout -s KILL 3600 setsid -w maxima --very-quiet -b "$W/run.mac" < /dev/null 2>&1 | grep -a '^\(R\|EQQ\|HIT\) '
echo "=== done $(TZ=Europe/Brussels date '+%H:%M %Z')"
