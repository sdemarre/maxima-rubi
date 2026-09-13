#!/bin/sh
# probes/matcher/07-fault-survival.sh -- does a Maxima process survive
# control-stack exhaustion (a runaway recursion) raised in Maxima code that
# the matcher substrate calls?  (matcher substrate plan 2, Tasks 4 and 7;
# spec section 3.5 step 5.)  Each variant runs in its own process (a fatal
# SBCL error kills it) with stdin from /dev/null (SBCL's ldb monitor would
# otherwise wait for input) and a KILL timeout.  No rule files are loaded.
# Usage (repo root):
#   sh probes/matcher/07-fault-survival.sh > probes/matcher/07-fault-survival.out 2>&1
set -u
cd "$(dirname "$0")/../.." || exit 1
W=${TMPDIR:-/tmp}/mr-07-fault-survival
rm -rf "$W"; mkdir -p "$W"
N=${MR_FAULT_RUNS:-2}

cat > "$W/head.mac" <<'EOF'
display2d : false$
t_r1(a) := t_r1(a)$
w0(a) := t_r1(a)$
w1(a) := w0(a)$
w2(a) := w1(a)$
t_r2(mm, x) := t_r2(mm, x)$
EOF
cat > "$W/load.mac" <<'EOF'
load("maxima_rubi_match.lisp")$
load("maxima_rubi_tree.lisp")$
load("maxima_rubi_utils.mac")$
load("maxima_rubi_dispatch.lisp")$
t_true(mm, x) := true$
t_7(mm, x) := 7$
p : "(Int (Power (Pattern x (Blank)) (Optional (Pattern |_t_m| (Blank)))) (Pattern x (Blank Symbol)))"$
h7 : %mr_defrule("t", 2, p, t_true, t_7)$
EOF

variant() { # <name> <needs-substrate 0|1>; body on stdin
  { cat "$W/head.mac"; [ "$2" = 1 ] && cat "$W/load.mac"; cat; echo 'print("R SURVIVED")$'; } > "$W/$1.mac"
}
variant top_w0 0 <<'EOF'
print("R result", errcatch(w0(1)))$
EOF
variant top_w2 0 <<'EOF'
print("R result", errcatch(w2(1)))$
EOF
variant top_2arg 0 <<'EOF'
print("R result", errcatch(t_r2([a = 1], x)))$
EOF
variant top_mfuncall 0 <<'EOF'
print("R result", errcatch(?mfuncall('t_r1, 1)))$
EOF
variant dispatch_cond_named 1 <<'EOF'
t_c(mm, x) := w0(1)$
hc : %mr_defrule("t", 1, p, t_c, t_7)$
print("R result", %mr_dispatch_tree(x^3, x, [hc, h7], 1))$
EOF
variant dispatch_cond_2arg 1 <<'EOF'
t_c(mm, x) := t_r2(mm, x)$
hc : %mr_defrule("t", 1, p, t_c, t_7)$
print("R result", %mr_dispatch_tree(x^3, x, [hc, h7], 1))$
EOF
variant dispatch_cond_lambda 1 <<'EOF'
hc : %mr_defrule("t", 1, p, lambda([mm, x], w0(1)), t_7)$
print("R result", %mr_dispatch_tree(x^3, x, [hc, h7], 1))$
EOF
variant dispatch_repl 1 <<'EOF'
t_rp(mm, x) := w0(1)$
hr : %mr_defrule("t", 1, p, t_true, t_rp)$
print("R result", %mr_dispatch_tree(x^3, x, [hr, h7], 1))$
EOF
variant accept_cond_named 1 <<'EOF'
t_c(mm, x) := w0(1)$
hc : %mr_defrule("t", 1, p, t_c, t_7)$
print("R result", %mr_rule_accept(hc, x^3, x))$
EOF
variant matchq_cond_lambda 1 <<'EOF'
print("R result", %mr_matchQ(x, "(Pattern |_u| (Blank))", [], lambda([b], w0(1))))$
EOF
variant matchq_cond_named 1 <<'EOF'
t_c1(b) := w0(1)$
print("R result", %mr_matchQ(x, "(Pattern |_u| (Blank))", [], t_c1))$
EOF

echo "=== probes/matcher/07-fault-survival  git HEAD $(git rev-parse --short HEAD)  $(date -u '+%Y-%m-%d %H:%M UTC')  runs per variant: $N"
timeout -s KILL 60 maxima --very-quiet --batch-string='print("R build", build_info()@version, build_info()@timestamp)$' < /dev/null 2>&1 | grep -a '^R build'
printf '%-22s %3s  %-8s %-14s %-12s %s\n' variant run survived fatal-pseudo caught-top result
for f in "$W"/*.mac; do
  name=$(basename "$f" .mac)
  case $name in head|load) continue ;; esac
  i=1
  while [ "$i" -le "$N" ]; do
    out="$W/$name.$i.out"
    timeout -s KILL 120 maxima --very-quiet -b "$f" < /dev/null > "$out" 2>&1
    printf '%-22s %3s  %-8s %-14s %-12s %s\n' "$name" "$i" \
      "$(grep -a -c '^R SURVIVED' "$out")" "$(grep -a -c 'while pseudo-atomic' "$out")" \
      "$(grep -a -c 'Automatically continuing' "$out")" \
      "$(grep -a '^R result' "$out" | tr -s ' ' | cut -c1-40)"
    i=$((i + 1))
  done
done
echo "=== done"
