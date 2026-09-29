#!/usr/bin/env python3
"""probes/verify-stages/07-sympy-check.py -- an independent CAS check (SymPy)
of the answers the 2026-09-28 fixes produced (handoffs/2026-09-28-checker-
wrong-answers): 7.2.4b e96 and 7.2.5 e50 (the 1.1.2.6 r13/r14 erratum),
4.7.7 e865 (the 4.1.0.2 r18 erratum). rubi's answers come from the rules
core (build it first: sh test/build_rules_core.sh) as Maxima strings and are
parsed into SymPy. For each: simplify(diff(r, x) - f), and the residual at
exact rational parameters and points evaluated with N(..., 40). Also the
1.1.2.6 r13 split identity itself, with f/g^2 and with the source's f/e^2,
and SymPy's own integrate on e96/e50 (60 s cap each).

Usage (repo root):
  python3 probes/verify-stages/07-sympy-check.py > probes/verify-stages/07-sympy-check.out
"""
import multiprocessing, os, subprocess, sys, tempfile, time
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
a, b, c, d, e, x = sp.symbols("a b c d e x")
LOCALS = {"a": a, "b": b, "c": c, "d": d, "e": e, "x": x, "pi": sp.pi,
          "acosh": sp.acosh, "atanh": sp.atanh, "atan": sp.atan, "sqrt": sp.sqrt,
          "log": sp.log, "tan": sp.tan, "sin": sp.sin, "csc": sp.csc,
          "elliptic_e": sp.elliptic_e, "elliptic_f": sp.elliptic_f}
H = sp.Rational(1, 2)
ENTRIES = [
    ("e96", "(a+b*acosh(c*x))/(d+e*x^2)^(5/2)",
     (a + b*sp.acosh(c*x))/(d + e*x**2)**sp.Rational(5, 2)),
    ("e50", "acosh(a*x)/(c+d*x^2)^(5/2)",
     sp.acosh(a*x)/(c + d*x**2)**sp.Rational(5, 2)),
    ("e865", "sqrt(csc(x))*(x*cos(x)-4*sec(x)*tan(x))",
     sp.sqrt(sp.csc(x))*(x*sp.cos(x) - 4*sp.sec(x)*sp.tan(x))),
]
PARAMS = [{a: sp.Rational(9, 10), b: sp.Rational(13, 10), c: H, d: sp.Rational(9, 10),
           e: sp.Rational(11, 10)},
          {a: 2, b: 3, c: 3, d: 5, e: 7}]
POINTS = [sp.Rational(7, 20), sp.Rational(13, 20), sp.Rational(3, 2), sp.Rational(5, 2)]


def rubi_answers():
    mac = "display2d:false$\n" + "".join(
        f'printf(true, "ANS {k} ~a~%", string(rubi({t}, x)))$\n' for k, t, _ in ENTRIES)
    with tempfile.NamedTemporaryFile("w", suffix=".mac", delete=False) as fh:
        fh.write(mac)
    try:
        out = subprocess.run(["sbcl", "--tls-limit", "100000", "--core",
                              os.path.join(ROOT, "test", "mr_rules.core"), "--noinform",
                              "--very-quiet", "-b", fh.name], cwd=ROOT, stdin=subprocess.DEVNULL,
                             capture_output=True, text=True, timeout=600).stdout
    finally:
        os.unlink(fh.name)
    return dict(l.split(" ", 2)[1:] for l in out.splitlines() if l.startswith("ANS "))


def _integrate(f_, conn):
    r = sp.integrate(f_, x)
    conn.send("unevaluated Integral" if r.has(sp.Integral) else "closed form: " + str(r)[:200])


def integrate_capped(f_, cap):
    rd, wr = multiprocessing.Pipe(False)
    pr = multiprocessing.Process(target=_integrate, args=(f_, wr))
    pr.start()
    pr.join(cap)
    if pr.is_alive():
        pr.kill()
        return f"no result within {cap} s"
    return rd.recv() if rd.poll() else "no result"


def main():
    stamp = open(os.path.join(ROOT, "test", "mr_rules.core.stamp")).read().splitlines()
    print(f"# {time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())}, sympy {sp.__version__}, "
          f"rules core {stamp[0]}, {stamp[1]}")
    # positive symbols: (g*x)^m = g^m*x^m only then, as for the rule's real use
    A, B, C, D, E, F, G, M, P, Q, X = sp.symbols("a b c d e f g m p q x", positive=True)
    base = (G*X)**M*(A + B*X**2)**P*(C + D*X**2)**Q
    for name, coef in (("f/g^2", F/G**2), ("f/e^2 (Rubi source)", F/E**2)):
        diff_ = E*base + coef*(G*X)**(M + 2)*(A + B*X**2)**P*(C + D*X**2)**Q - base*(E + F*X**2)
        s = sp.simplify(sp.powsimp(sp.expand_power_base(diff_, force=True), force=True))
        print(f"1.1.2.6 r13 split minus integrand, {name}: {s}")
    ans = rubi_answers()
    for key, _text, f_ in ENTRIES:
        r = parse_expr(ans[key].replace("^", "**").replace("%pi", "pi"), local_dict=LOCALS)
        res = sp.diff(r, x) - f_
        print(f"\n== {key}  f = {f_}")
        print(f"   rubi: {ans[key][:300]}{' ...' if len(ans[key]) > 300 else ''}")
        for vals in (PARAMS if res.free_symbols - {x} else PARAMS[:1]):
            for x0 in POINTS:
                v = sp.N(abs(res.subs(vals).subs(x, x0)), 40)
                pv = {str(k): str(w) for k, w in vals.items() if k in res.free_symbols}
                print(f"   |res| at {pv} x = {x0}: {v}")
        s = sp.simplify(res)
        print(f"   simplify(residual) = 0: {s == 0}")
        if key != "e865":
            print(f"   sympy integrate: {integrate_capped(f_, 60)}")


if __name__ == "__main__":
    main()
