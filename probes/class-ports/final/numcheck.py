#!/usr/bin/env python3
"""numcheck.py ARM KEYS OUT [-j N] -- is an unverified answer WRONG? For each entry,
rubi's answer A on ARM (fa.py arm syntax) and the residual |dA/dx - f| (float,
rectform-abs) at three points: every parameter drawn from {0.37, 1.3, 2.1, ...}
(fixed per parameter, positive) and x in {0.3, 0.55, 0.7} (--small: parameters in (0.29, 0.83), x in {0.1, 0.2, 0.3}, keeping
inverse-trig and hypergeometric arguments inside their real/unit ranges); also the same residual
for the corpus's expected answer E. Rows: `max|A'-f|  max|E'-f|  key`.
A tiny A residual = the answer is right and only the zero chain failed to close."""
import sys, os, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fa
arm, keysf, out = sys.argv[1:4]
j = int(sys.argv[sys.argv.index("-j") + 1]) if "-j" in sys.argv else 1
name, core, sw, pre = fa.parse_arm(arm)
VALS = "[0.37, 1.3, 2.1, 0.83, 1.7, 0.61, 2.9, 1.1]"; XS = "[0.3, 0.55, 0.7]"
if "--small" in sys.argv:
    VALS = "[0.37, 0.61, 0.83, 0.29, 0.53, 0.71, 0.45, 0.33]"; XS = "[0.1, 0.2, 0.3]"
d = fa.load_driver(core, 60)
d.SWITCH_SETTINGS.update(sw)
TPL = """
display2d:false$ linel:100000$
mr_f : %F$
mr_r : rubi(mr_f, %V)$
mr_e : %E$
mr_pv : sort(delete(%V, listofvars([mr_f, mr_r, mr_e])))$
mr_vals : %VALS$
mr_res(g) := block([mr_m : 0, mr_d, mr_s, mr_sub],
  mr_d : diff(g, %V) - mr_f,
  for xv in %XS do (
    mr_sub : append([%V = xv], makelist(mr_pv[i] = mr_vals[1 + mod(i - 1, 8)], i, 1, length(mr_pv))),
    mr_s : errcatch(abs(rectform(float(ev(subst(mr_sub, mr_d), nouns))))),
    if mr_s = [] or not numberp(first(mr_s)) then mr_m : 'err
    else if mr_m # 'err then mr_m : max(mr_m, first(mr_s))),
  mr_m)$
print("RESA", mr_res(mr_r))$
print("RESE", mr_res(mr_e))$
print("NOUN", not freeof(unintegrable, mr_r))$
"""
def one(k):
    els, _ = fa.entry_text(d, k[0], k[1])
    t = TPL.replace("%VALS", VALS).replace("%XS", XS).replace("%F", d.normalize_heads(els[0])).replace("%V", els[1]).replace("%E", d.normalize_heads(els[3]))
    text = pre + "".join(f"{a} : {b}$\n" for a, b in d.SWITCH_SETTINGS.items()) + t + "pos$\n" * 40 + "no$\n" * 20
    o, hit = d.maxima_run(text, 60, [])
    g = lambda tag: next((l.split(None, 1)[1].strip() for l in o.splitlines() if l.startswith(tag)), "n/a" if not hit else "cap")
    return f"{name:8s} A'-f={g('RESA'):>24s}  E'-f={g('RESE'):>24s}  noun={g('NOUN'):5s}  {k[0]} e{k[1]}\n"
with open(out, "a") as fh, cf.ThreadPoolExecutor(j) as ex:
    fh.write(f"# numcheck arm {arm} params {VALS} x {XS}\n")
    for line in ex.map(one, fa.keys_of(keysf)):
        fh.write(line); fh.flush()
