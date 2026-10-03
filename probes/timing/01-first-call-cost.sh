#!/bin/bash
# probes/timing/01-first-call-cost.sh -- where does the native baseline's
# 0.24 s floor come from? (.scratch/corpus-harness/issues/11)
#
# Every native-baseline t= is >= 0.3 s, even for integrate(x, x); rubi's start
# at 0.0 s. The ticket first blamed integrate/risch loading parts of
# themselves on first use and proposed a warm-up call (or, user suggestion
# 2026-10-03, one saved image carrying the rules AND a warmed integrate/risch
# for both arms). This probe measures:
#
#   A. the driver's own timed text (corpus_driver.build_text, MR_BASELINE=1)
#      for integrate and risch, as is and with load(stringproc) before mr_t0;
#   B. the first timed expression of a stock batch being 1+1, not integrate;
#   C. saved images: stock + warmed integrate/risch, the rules core, and the
#      rules core + warmed integrate/risch (the combined-core suggestion);
#   D. cold vs warmed (integrate(x,x) / risch(x,x) first) first-call CPU over
#      ten integrands, timed WITHOUT printf in the window, 3 fresh processes
#      each, medians.
#
# Run from the repo root, machine otherwise idle:
#   bash probes/timing/01-first-call-cost.sh > probes/timing/01-first-call-cost.out 2>&1 < /dev/null
set -u
cd "$(dirname "$0")/../.." || exit 1
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
echo "date $(date -u '+%F %T UTC')"
maxima --very-quiet --batch-string='build_info()$ print(build_info()@version, build_info()@timestamp)$' 2>&1 | tail -1

echo; echo "== A. the driver's timed text (ANSWERED = the record's t=)"
MR_BASELINE=1 python3 - <<'EOF' 2>&1
import sys; sys.argv = ["corpus_driver.py"]; sys.path.insert(0, "test")
import corpus_driver as d
for I in ("integrate", "risch"):
    t = d.build_text("x", "x", "x^2/2", None, I)
    pre = t.replace("mr_t0 : elapsed_run_time()$",
                    "load(stringproc)$\nmr_t0 : elapsed_run_time()$", 1)
    for name, text in (("as is", t), ("load(stringproc) first", pre)):
        for i in range(3):
            out, _ = d.maxima_run(text, 60, [])
            ans = [l for l in out.splitlines() if l.startswith("ANSWERED")]
            print(f"{I:9s} {name:24s} run {i + 1}: {ans[-1] if ans else 'no ANSWERED'}")
EOF

TM='tm(e) ::= buildq([e], block([t0: elapsed_run_time(), r], r: e, printf(true, "T ~a ~,3f~%", string('"'"'e), elapsed_run_time() - t0)))$'
cat > "$T/b.mac" <<EOF
$TM
tm(1+1)\$
tm(expand((x+1)^5))\$
tm(integrate(x, x))\$
tm(risch(x, x))\$
tm(rubi(x, x))\$
EOF

echo; echo "== B/C. first timed expressions per image (printf-timed, as the driver)"
save() { printf ':lisp (setq maxima::*maxima-started* nil)$\n:lisp (sb-ext:save-lisp-and-die "%s" :toplevel (symbol-function (quote cl-user::run)))\n' "$1"; }
WARM='integrate(x,x)$
risch(x,x)$'
{ printf 'batch_answers_from_file: true$\n%s\n' "$WARM"; save "$T/stock_warm.core"; } \
  | maxima -X "--tls-limit 100000" > "$T/b1.log" 2>&1
{ printf 'batch_answers_from_file: true$\nload("maxima_rubi.mac")$\nmr_load_all()$\n%s\n' "$WARM"; save "$T/combined.core"; } \
  | maxima -X "--tls-limit 100000" > "$T/b2.log" 2>&1
[ -f test/mr_rules.core ] || sh test/build_rules_core.sh
run_img() { # label, command...
  for i in 1 2; do echo "[$1, run $i]"; "${@:2}" -b "$T/b.mac" < /dev/null 2>&1 | grep '^T '; done; }
run_img "stock maxima" maxima --very-quiet
run_img "stock + warmed integrate/risch image" sbcl --core "$T/stock_warm.core" --noinform --very-quiet
run_img "rules core (test/mr_rules.core)" sbcl --core test/mr_rules.core --noinform --very-quiet
run_img "rules core + warmed integrate/risch" sbcl --core "$T/combined.core" --noinform --very-quiet
echo "(rubi(x,x) in the stock images is the unevaluated function call)"

echo; echo "== D. cold vs warmed first call, no printf in the window (CPU s, median of 3)"
: > "$T/fc.out"
while read -r f; do for I in integrate risch; do for w in cold warm; do
  pre=""; [ "$w" = warm ] && pre="$I(x,x)\$"
  printf 'load(stringproc)$\nbatch_answers_from_file:true$\n%s\nt0:elapsed_run_time()$\nr:%s(%s,x)$\nt1:elapsed_run_time()$\nr:%s(%s,x)$\nt2:elapsed_run_time()$\nprintf(true,"FC ~a ~a ~a first=~,4f again=~,4f~%%","%s","%s","%s",t1-t0,t2-t1)$\n' \
    "$pre" "$I" "$f" "$I" "$f" "$I" "$w" "$f" > "$T/fc.mac"
  for i in 1 2 3; do maxima --very-quiet -b "$T/fc.mac" < /dev/null 2>&1 | grep '^FC' >> "$T/fc.out"; done
done; done; done <<'EOF'
x*sin(x)
1/(1+x^3)
sqrt(1+x^2)
x*exp(x)
log(x)^2
atan(x)
1/sqrt(1-x^4)
exp(-x^2)
sin(x)^3*cos(x)^2
x^2/(a+b*x)^3
EOF
python3 - "$T/fc.out" <<'EOF'
import sys, statistics as st, collections
d = collections.defaultdict(list)
for l in open(sys.argv[1]):
    _, I, w, *f, a, b = l.split()
    d[(I, " ".join(f), w)].append((float(a[6:]), float(b[6:])))
for k in sorted(d):
    v = d[k]
    print(f"{k[0]:9s} {k[1]:22s} {k[2]:4s} first {st.median(x[0] for x in v):.4f}"
          f"  again {st.median(x[1] for x in v):.4f}  (n={len(v)})")
EOF
echo "DONE"
