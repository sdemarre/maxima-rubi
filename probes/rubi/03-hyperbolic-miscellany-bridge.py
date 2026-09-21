#!/usr/bin/env python3
"""probes/rubi/03 — do the class-6 MISCELLANY files ride the same inert-trig
bridge as the `.7` family?

The question left open by probes/rubi/02 (and by
`.scratch/class6-residue/issues/01`, last paragraph): probe 02 settled that the
1,173-entry `.7` family is answered by SECTION 4's rules, reached through the
one bridge rule at the head of `4.1.0.1`

    Int[u_,x_Symbol] := Int[DeactivateTrig[u,x],x] /; FunctionOfTrigOfLinearQ[u,x]

It deliberately did NOT answer the same question for the seven
`Hyperbolic <fn> functions` / `6.7.1` miscellany corpus files — a further
1,480 deferred entries. Together with `.7` that is 83 % of class 6's deferred
mass, so the answer decides how much of class 6 the class-4 port + the
inert-trig substrate pays for.

WHAT IS MEASURED. The bridge's admission condition is not a guess; it is
`FunctionOfTrigOfLinearQ[u,x]` (IntegrationUtilityFunctions.m:4358-4361):

    FunctionOfTrigOfLinearQ[u_,x_Symbol] :=
      If[MatchQ[u,(c_.+d_.*x)^m_.*(a_.+b_.*trig_[e_.+f_.*x])^n_.
                  /; FreeQ[{a,b,c,d,e,f,m,n},x] && (TrigQ[trig]||HyperbolicQ[trig])],
        True,
      Not[MemberQ[{Null,False},FunctionOfTrig[u,Null,x]]] && AlgebraicTrigFunctionQ[u,x]]

This probe ports the SECOND branch — `FunctionOfTrig` (utils 4365-4392) and
`AlgebraicTrigFunctionQ` (utils 4396-4407) — to Maxima and runs it over every
class-6 corpus integrand, joined to the committed class-6 record's verdicts.

Branch 2 is ported faithfully, clause for clause. Branch 1 is a Mathematica
`MatchQ` over a flat `Times` with four `Optional` defaults; porting it exactly
would mean reproducing Mathematica's optional-argument matching, which is
guesswork here. It is therefore NOT ported, and the consequence is stated
rather than hidden: **branch 1 can only ADD admissions, so this probe's
"admitted" count is a LOWER BOUND** on what the bridge accepts. A separate,
explicitly approximate count reports the entries branch 2 rejects that carry
the `(c+d x)^m (a+b hyper)^n` shape branch 1 exists to admit.

CONTROLS. The classifier is only worth reading if it reproduces what is
already known:
  * POSITIVE — the `.7` family (6.1.7 ... 6.6.7) is known from probe 02 to
    ride the bridge. It must come back overwhelmingly admitted.
  * NEGATIVE — the `(e x)^m (a+b sinh(c+d x^n))^p` files (6.1.3, 6.2.3,
    6.5.2, 6.6.2) carry a bare `x^m` factor and a NONLINEAR hyperbolic
    argument. Both kill branch 2. They must come back essentially rejected.
If either control misses, the classifier is wrong and no other number on this
probe may be read.

Static + one Maxima process. No rule files are loaded and nothing is
integrated: Maxima is used only as the parser and expression walker.
"""

import collections
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "test"))

RUBI = os.path.join(ROOT, "reference", "rubi")
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
RULES = os.path.join(RUBI, "Rubi", "IntegrationRules")
SECTION = "6 Hyperbolic functions"
RECORD = os.path.join(ROOT, "test", "corpus_class6.out")

# The seven files the question is about: the per-function miscellany buckets
# plus 6.7.1. Named here so the report can separate them from the rest.
MISCELLANY = re.compile(r"^(6\.\d+\.\d+ Hyperbolic \w+ functions|"
                        r"6\.7\.1 Hyperbolic functions)$")
DOT7 = re.compile(r"^6\.[1-6]\.7 ")
# The `(c+d x)^m (a+b hyper)^n` family — branch 1's exact shape, reported
# separately because branch 1 is not ported here.
DOT1 = re.compile(r"^6\.[1-6]\.1 \(c\+d x\)\^m ")
# The negative control: nonlinear hyperbolic argument under a bare x^m.
NEGCTL = re.compile(r"^6\.\d+\.\d+ \(e x\)\^m \(a\+b \w+\(c\+d x\^n\)\)\^p$")


def head(msg):
    print()
    print("=" * 78)
    print(msg)
    print("=" * 78)


def pinned():
    out = []
    for name, path in (("rubi", RUBI), ("maxima-syntax-test-suite", SUITE)):
        p = subprocess.run(["git", "-C", path, "rev-parse", "HEAD"],
                           capture_output=True, text=True)
        out.append(f"{name}: {p.stdout.strip() or 'UNKNOWN'}")
    return out


# --------------------------------------------------------------------------
# 1. The file-level pairing: which section-4 rule file each miscellany shape
#    would be answered by, if the bridge admits it.
# --------------------------------------------------------------------------

def m1_file_pairing():
    head("1. Corpus section-6 files against the section-4 rule files")

    def rules_of(sec):
        base = os.path.join(RULES, sec)
        out = []
        for dirpath, _, names in os.walk(base):
            for n in sorted(names):
                if n.endswith(".m"):
                    out.append(os.path.relpath(os.path.join(dirpath, n), base))
        return sorted(out)

    r4, r6 = rules_of("4 Trig functions"), rules_of(SECTION)
    print(f"  Rubi section-4 rule files: {len(r4)}")
    print(f"  Rubi section-6 rule files: {len(r6)}")
    print()
    print("  Section 6 HAS a miscellany rule file — 6.7.9 Active hyperbolic")
    print("  functions — and this port generates and loads it. So the")
    print("  miscellany entries are not deferring for want of a section-6")
    print("  file; they defer because 6.7.9 covers a DIFFERENT shape.")
    n69 = len(re.findall(r"^Int\[", open(
        os.path.join(RULES, SECTION, "6.7 Miscellaneous",
                     "6.7.9 Active hyperbolic functions.m"),
        encoding="utf-8", errors="replace").read(), re.M))
    print(f"  6.7.9 is {n69} rules and every LHS carries an (e+f x)^m factor")
    print("  over a hyperbolic quotient — the x-CARRYING shapes.")
    print()
    print("  The section-4 rule files with NO section-6 counterpart are the")
    print("  pure-trig-product families — exactly what a hyperbolic")
    print("  miscellany integrand with no bare x is:")
    only4 = [f for f in r4 if re.search(
        r"4\.1\.0\.|4\.1\.5 |4\.1\.6 |4\.1\.8 |4\.7\.1 |4\.7\.2 |4\.7\.3 |"
        r"4\.7\.4 |4\.7\.5 |4\.7\.9 ", f)]
    for f in only4:
        print(f"    {f}")
    print()
    print("  FINDING (structural, not yet decisive): the shapes the class-6")
    print("  miscellany files actually contain — products and sums of")
    print("  hyperbolics of a linear argument — have their rules in section")
    print("  4 only. Whether the BRIDGE hands them over is measurement 2.")
    return r4, r6


# --------------------------------------------------------------------------
# 2. The Maxima port of the bridge's admission condition.
# --------------------------------------------------------------------------

CLASSIFIER = r"""
/* ------------------------------------------------------------------ *
 * probes/rubi/03 — FunctionOfTrigOfLinearQ branch 2, ported from
 * reference/rubi/Rubi/IntegrationUtilityFunctions.m clause for clause.
 *   FunctionOfTrig          utils 4365-4392
 *   AlgebraicTrigFunctionQ  utils 4396-4407
 *   LinearQ = PolyQ[u,x,1]  utils 1373-1376  (degree EXACTLY 1)
 * `mr_false` / `mr_null` stand for Mathematica's False / Null sentinels,
 * which must stay distinct from a returned linear form.
 *
 * EVERY bound name here — parameter, block local and `for` variable — wears
 * the `mr_` prefix. Maxima re-evaluates a value when it is used, so a local
 * named `a` or `v` CAPTURES the corpus's own `a` or `v` inside the integrand
 * being walked. Measured: with a loop variable named `a`,
 * `cosh(a+b*x)*sinh(a+b*x)` classified `non-algebraic`, because the loop
 * binding of `a` was substituted back into the argument `a+b*x`.
 * ------------------------------------------------------------------ */

/* Maxima's `op`/`args` report the DISPLAY form by default: `op(2/(1+x))` is
 * `/` and `op(a-b)` is `-`, so a walk keyed on "*" / "+" / "^" misses them.
 * `inflag:true` switches inspection to the INTERNAL form — 2*(1+x)^-1,
 * a+(-1)*b — which is the Times/Plus/Power structure Rubi's own clauses are
 * written against. Measured: without it, `2/(-1+3*cosh(4+6*x))` classified
 * `non-algebraic`. */
inflag: true$

MR_TRG: [sin, cos, tan, cot, sec, csc]$
MR_HYP: [sinh, cosh, tanh, coth, sech, csch]$
MR_ALL: append(MR_TRG, MR_HYP)$
/* CalculusQ: the heads Rubi refuses to descend into. */
MR_CALC: [nounify('integrate), nounify('diff), nounify('sum),
          nounify('product), nounify('limit), 'integrate, 'diff,
          'sum, 'product, 'limit, 'at]$

/* LinearQ = PolyQ[u,x,1]: degree in x is EXACTLY 1.  d/dx u free of x and
 * nonzero is that condition — u' = c (c free of x, c # 0) implies u = c x + k
 * — and unlike `polynomialp` it does not reject a SYMBOLIC coefficient:
 * measured, polynomialp(a+b*x,[x]) is false, because its default coefficient
 * test is constantp, while Rubi's PolyQ tests FreeQ[...,x].
 *
 * The nonzero test is `is(mr_d = 0)` — SYNTACTIC equality — and not
 * `is(equal(mr_d,0))`. Measured: `is(equal(b,0))` is `unknown` for a free
 * symbol, and the unknown propagates through the `and`, so mr_linq(a+b*x,x)
 * returned `unknown` and every downstream `if` silently took its else arm.
 * Rubi has the same semantics on purpose: PolyQ never tries to PROVE a
 * symbolic coefficient nonzero, it reads the expression's shape. */
mr_linq(mr_u, mr_x) := block([mr_d],
  if freeof(mr_x, mr_u) then false
  else (mr_d: ratsimp(diff(mr_u, mr_x)),
        freeof(mr_x, mr_d) and not is(mr_d = 0)))$

mr_trigp(mr_u) := not atom(mr_u) and member(op(mr_u), MR_ALL)
                  and length(args(mr_u)) = 1$

/* AlgebraicTrigFunctionQ[u,x] */
mr_algtq(mr_u, mr_x) :=
  if atom(mr_u) then true
  else if mr_trigp(mr_u) and mr_linq(first(args(mr_u)), mr_x) then true
  else if op(mr_u) = "^" and freeof(mr_x, second(args(mr_u)))
       then mr_algtq(first(args(mr_u)), mr_x)
  else if op(mr_u) = "*" or op(mr_u) = "+"
       then block([mr_r: true],
              for mr_k in args(mr_u) do
                (if not mr_algtq(mr_k, mr_x) then (mr_r: false) else false),
              mr_r)
  else false$

/* The v-consistency arm of FunctionOfTrig: all trig arguments must be the
 * same linear form up to a RATIONAL ratio (utils 4374-4385). `mr_m` is 1 for
 * a trig head and %i for a hyperbolic one — the imaginary-argument carry. */
mr_fot_merge(mr_v, mr_arg, mr_x, mr_m) :=
  block([mr_a, mr_b, mr_c, mr_d, mr_q],
    mr_a: ratcoef(mr_v, mr_x, 0),   mr_b: ratcoef(mr_v, mr_x, 1),
    mr_c: mr_m*ratcoef(mr_arg, mr_x, 0),
    mr_d: mr_m*ratcoef(mr_arg, mr_x, 1),
    if not is(ratsimp(mr_a*mr_d - mr_b*mr_c) = 0) then mr_false
    else (mr_q: ratsimp(mr_b/mr_d),
          if not ratnump(mr_q) then mr_false
          else mr_a/num(mr_q) + mr_b*mr_x/num(mr_q)))$

/* FunctionOfTrig[u,v,x] */
mr_fot(mr_u, mr_v, mr_x) :=
  if atom(mr_u) then (if mr_u = mr_x then mr_false else mr_v)
  else if mr_trigp(mr_u) and member(op(mr_u), MR_TRG)
          and mr_linq(first(args(mr_u)), mr_x)
       then (if mr_v = mr_null then first(args(mr_u))
             else mr_fot_merge(mr_v, first(args(mr_u)), mr_x, 1))
  else if mr_trigp(mr_u) and member(op(mr_u), MR_HYP)
          and mr_linq(first(args(mr_u)), mr_x)
       then (if mr_v = mr_null then %i*first(args(mr_u))
             else mr_fot_merge(mr_v, first(args(mr_u)), mr_x, %i))
  else if member(op(mr_u), MR_CALC) then mr_false
  else block([mr_w: mr_v],
         catch(for mr_k in args(mr_u) do
                 (mr_w: mr_fot(mr_k, mr_w, mr_x),
                  if mr_w = mr_false then throw(mr_false) else false),
               mr_w))$

/* FunctionOfTrigOfLinearQ branch 2 */
mr_fotlq2(mr_u, mr_x) := block([mr_v: mr_fot(mr_u, mr_null, mr_x)],
  not (mr_v = mr_null or mr_v = mr_false) and mr_algtq(mr_u, mr_x))$

/* Why branch 2 rejected, for the report. First matching reason wins. */
mr_reason(mr_u, mr_x) := block([mr_v: mr_fot(mr_u, mr_null, mr_x)],
  if mr_v = mr_null then "no-trig"
  else if mr_v = mr_false then
    (if not mr_algtq(mr_u, mr_x) then "non-algebraic" else "bare-x-or-angle")
  else if not mr_algtq(mr_u, mr_x) then "non-algebraic"
  else "admitted")$

/* An entry the report counts separately: branch 2 rejects it, but it carries
 * the (c+d x)^m (a+b hyper[e+f x])^n shape that branch 1 exists to admit.
 * APPROXIMATE — see the module docstring. */
mr_br1_shape(mr_u, mr_x) :=
  block([mr_fl, mr_poly: 0, mr_tb: 0, mr_ok: true, mr_b, mr_xs, mr_t],
    mr_fl: if not atom(mr_u) and op(mr_u) = "*" then args(mr_u) else [mr_u],
    for mr_k in mr_fl do (
      if freeof(mr_x, mr_k) then false
      else (
        if not atom(mr_k) and op(mr_k) = "^"
           and freeof(mr_x, second(args(mr_k)))
          then (mr_b: first(args(mr_k)))
          else (mr_b: mr_k),
        if mr_linq(mr_b, mr_x) then (mr_poly: mr_poly + 1)
        else if mr_trigp(mr_b) and mr_linq(first(args(mr_b)), mr_x)
             then (mr_tb: mr_tb + 1)
        else if not atom(mr_b) and op(mr_b) = "+" and length(args(mr_b)) = 2
                and (freeof(mr_x, first(args(mr_b)))
                     or freeof(mr_x, second(args(mr_b))))
             then (
               mr_xs: if freeof(mr_x, first(args(mr_b)))
                        then second(args(mr_b)) else first(args(mr_b)),
               if not atom(mr_xs) and op(mr_xs) = "*"
                 then (mr_t: [],
                       for mr_g in args(mr_xs) do
                         (if not freeof(mr_x, mr_g)
                            then (mr_t: cons(mr_g, mr_t)) else false),
                       if length(mr_t) = 1 then (mr_xs: first(mr_t))
                       else false)
                 else false,
               if mr_trigp(mr_xs) and mr_linq(first(args(mr_xs)), mr_x)
                 then (mr_tb: mr_tb + 1) else (mr_ok: false))
        else (mr_ok: false))),
    mr_ok and mr_poly <= 1 and mr_tb = 1)$
"""


# The classifier's own unit set. It is run FIRST, in measurement 0, and a
# single miss aborts the probe: three real defects were found with it while
# the classifier was being written, each of which had produced plausible but
# wrong numbers —
#   * a `for` variable named `a` CAPTURED the corpus's own `a`, so
#     cosh(a+b*x)*sinh(a+b*x) came back `non-algebraic`;
#   * Maxima's `op` reports the DISPLAY form, so 2/(-1+3*cosh(4+6*x)) had
#     head `/` and no walk clause matched it (fixed with `inflag:true`);
#   * `is(equal(b,0))` is `unknown` for a free symbol and the unknown
#     propagated through the `and`, so mr_linq(a+b*x,x) was neither true nor
#     false and every downstream `if` quietly took its else arm.
SELFTEST = [
    # (integrand, branch-2 verdict, branch-1 shape)
    ("cosh(a+b*x)*sinh(a+b*x)", "admit", "-"),
    ("cosh(a+b*x)^m*sinh(a+b*x)^n", "admit", "-"),
    ("sech(2+3*x)^2/(1+2*tanh(2+3*x)^2)", "admit", "-"),
    ("2/(-1+3*cosh(4+6*x))", "admit", "br1"),
    ("csch(2+3*x)^2/(2+coth(2+3*x)^2)", "admit", "-"),
    ("cosh(a+b*x)^2*sinh(a+b*x)^2", "admit", "-"),
    ("1/(cosh(2+3*x)^2+2*sinh(2+3*x)^2)", "admit", "-"),
    ("sinh(x)*sinh(3*x)", "admit", "-"),
    ("sqrt(a+b*sinh(c+d*x))", "admit", "br1"),
    ("tanh(a+b*x)^3*sech(a+b*x)", "admit", "-"),
    # Rejects, with the reason each one exists to pin down.
    ("x*sinh(x)", "reject", "br1"),                    # bare x
    ("(c+d*x)^2*(a+b*sinh(e+f*x))^3", "reject", "br1"),  # branch 1's shape
    ("x^3*tanh(a+b*x)", "reject", "br1"),
    ("sinh(x^2)", "reject", "-"),                      # nonlinear argument
    ("x^2*(a+b*sinh(c+d*x^3))^2", "reject", "-"),
    ("sinh(x)*sinh(x^2)", "reject", "-"),
    ("sinh(x)*sin(3*x)", "reject", "-"),               # trig x hyperbolic: b/d = I/3
    ("log(x)*sinh(x)", "reject", "-"),                 # not algebraic
    ("%e^x*sinh(x)", "reject", "-"),
    ("a+b", "reject", "-"),                            # no trig at all
    ("v*sinh(w)", "reject", "-"),                      # free of x
    ("x*sinh(x)*cosh(x)", "reject", "-"),
    ("sinh(a+b*x)*cosh(c+d*x)", "reject", "-"),        # inconsistent angles
]


def m0_selftest(work):
    head("0. Classifier self-test — the port of the admission condition")
    path = os.path.join(work, "selftest.mac")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(CLASSIFIER)
        for i, (u, _w, _b) in enumerate(SELFTEST):
            fh.write(
                f"block([MR_U: {u}, MR_X: x],\n"
                f"  printf(true, \"ST ~a ~a ~a~%\", {i},\n"
                "         if mr_fotlq2(MR_U, MR_X) then \"admit\" "
                "else \"reject\",\n"
                "         if mr_br1_shape(MR_U, MR_X) then \"br1\" "
                "else \"-\"))$\n")
        fh.write('printf(true, "== DONE~%")$\n')
    out = run_maxima(path)
    got = {}
    for line in out.splitlines():
        m = re.match(r"^ST (\d+) (\S+) (\S+)\s*$", line.strip())
        if m:
            got[int(m.group(1))] = (m.group(2), m.group(3))
    misses = 0
    for i, (u, w, b) in enumerate(SELFTEST):
        g = got.get(i)
        ok = g == (w, b)
        if not ok:
            misses += 1
            print(f"  MISS  want {w}/{b}  got {g}   {u}")
    print(f"  {len(SELFTEST) - misses} / {len(SELFTEST)} self-test cases "
          f"reproduce the hand-derived verdict")
    if misses:
        print("  *** the classifier is broken; no number on this probe may "
              "be read ***")
    return misses == 0


def build_batch(items, path):
    """One Maxima batch: classify every integrand, one RES line each."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(CLASSIFIER)
        fh.write("\n")
        for key, integrand, var in items:
            fh.write(
                "block([MR_U, MR_X, MR_R],\n"
                "  MR_R: errcatch(\n"
                f"    MR_X: {var},\n"
                f"    MR_U: {integrand},\n"
                "    printf(true, \"RES ~a ~a ~a ~a~%\",\n"
                f"           \"{key}\",\n"
                "           if mr_fotlq2(MR_U, MR_X) then \"admit\" "
                "else \"reject\",\n"
                "           mr_reason(MR_U, MR_X),\n"
                "           if mr_fotlq2(MR_U, MR_X) then \"-\" "
                "else (if mr_br1_shape(MR_U, MR_X) then \"br1shape\" "
                "else \"-\"))),\n"
                "  if MR_R = [] then\n"
                f"    printf(true, \"RES {key} error maxima-error -~%\"))$\n")
        fh.write('printf(true, "== DONE~%")$\n')


def run_maxima(path):
    p = subprocess.run(
        ["maxima", "--very-quiet", "-b", path],
        capture_output=True, text=True, timeout=3600,
        stdin=subprocess.DEVNULL)
    return p.stdout + p.stderr


# --------------------------------------------------------------------------
# Corpus + record plumbing
# --------------------------------------------------------------------------

def corpus_entries():
    """{relfile: [(idx, integrand_text, var_text)]} for the class-6 files."""
    # The driver parses sys.argv at import time; give it a benign one, the
    # way test/test_driver_radcan_fallback.py does.
    real = sys.argv[:]
    sys.argv = ["corpus_driver.py", SECTION + "/", "1", "30",
                os.path.join(SUITE, SECTION)]
    try:
        import corpus_driver as drv
    finally:
        sys.argv = real
    base = os.path.join(SUITE, SECTION)
    out = {}
    for dirpath, _, names in os.walk(base):
        for n in sorted(names):
            if not n.endswith(".mac"):
                continue
            path = os.path.join(dirpath, n)
            rel = os.path.relpath(path, base)
            entries, _lines = drv.extract_entries(path)
            rows = []
            for i, txt in enumerate(entries, 1):
                els = drv.split_elements(txt[1:-1])
                if len(els) < 4:
                    continue
                rows.append((i, drv.normalize_heads(els[0]),
                             drv.normalize_heads(els[1])))
            out[rel] = rows
    return out


def record_verdicts():
    """{(short_file, idx): verdict} from the committed class-6 record."""
    out = {}
    rx = re.compile(r"^(\S+)\s+t=\s*\S+\s+" + re.escape(SECTION) +
                    r"/[^/]+/([^/]+)\.mac e(\d+) ")
    for line in open(RECORD, encoding="utf-8", errors="replace"):
        m = rx.match(line)
        if m:
            out[(m.group(2), int(m.group(3)))] = m.group(1)
    return out


def short(rel):
    return os.path.splitext(os.path.basename(rel))[0]


# --------------------------------------------------------------------------

def m2_classify(work):
    head("2. The bridge's admission condition over every class-6 integrand")
    entries = corpus_entries()
    verdicts = record_verdicts()
    items, meta = [], {}
    for rel, rows in sorted(entries.items()):
        sf = short(rel)
        for idx, integrand, var in rows:
            key = f"K{len(items)}"
            items.append((key, integrand, var))
            meta[key] = (sf, idx, verdicts.get((sf, idx), "MISSING"))
    print(f"  class-6 corpus entries read: {len(items)}")
    print(f"  record verdicts joined:      "
          f"{sum(1 for k in meta if meta[k][2] != 'MISSING')}")
    batch = os.path.join(work, "classify.mac")
    build_batch(items, batch)
    print(f"  Maxima batch: {batch}")
    out = run_maxima(batch)
    open(os.path.join(work, "classify.raw"), "w", encoding="utf-8").write(out)
    got = {}
    for line in out.splitlines():
        m = re.match(r"^RES (K\d+) (\S+) (\S+) (\S+)\s*$", line.strip())
        if m:
            got[m.group(1)] = (m.group(2), m.group(3), m.group(4))
    print(f"  classified:                  {len(got)}")
    if "== DONE" not in out:
        print("  WARNING: the batch did not reach its DONE marker")
    missing = len(items) - len(got)
    if missing:
        print(f"  WARNING: {missing} entries produced no RES line")
    return meta, got


def m3_report(meta, got):
    head("3. Result, per corpus file")
    per = collections.defaultdict(collections.Counter)
    reasons = collections.defaultdict(collections.Counter)
    for key, (sf, _idx, verdict) in meta.items():
        if key not in got:
            per[sf]["no-result"] += 1
            continue
        adm, reason, br1 = got[key]
        per[sf]["total"] += 1
        if verdict == "deferred":
            per[sf]["deferred"] += 1
            if adm == "admit":
                per[sf]["deferred-admitted"] += 1
            else:
                reasons[sf][reason] += 1
                if br1 == "br1shape":
                    per[sf]["deferred-br1shape"] += 1
    print(f"  {'corpus file':52s} {'defer':>6s} {'admit':>6s} {'%':>5s} "
          f"{'+br1':>5s}")
    groups = collections.Counter()
    for sf in sorted(per):
        d = per[sf]["deferred"]
        a = per[sf]["deferred-admitted"]
        b = per[sf]["deferred-br1shape"]
        pct = f"{100 * a / d:5.1f}" if d else "    -"
        print(f"  {sf[:52]:52s} {d:6d} {a:6d} {pct} {b:5d}")
        g = ("dot7" if DOT7.match(sf) else
             "misc" if MISCELLANY.match(sf) else
             "negctl" if NEGCTL.match(sf) else
             "dot1" if DOT1.match(sf) else "other")
        groups[(g, "deferred")] += d
        groups[(g, "admitted")] += a
        groups[(g, "br1shape")] += b

    head("4. The two controls")
    for g, label, want in (
            ("dot7", "POSITIVE — the `.7` family (probe 02: rides the bridge)",
             "high"),
            ("negctl", "NEGATIVE — (e x)^m (a+b hyper(c+d x^n))^p "
                       "(bare x, nonlinear arg)", "low")):
        d = groups[(g, "deferred")]
        a = groups[(g, "admitted")]
        pct = 100 * a / d if d else 0.0
        verdict = ("OK" if (want == "high" and pct >= 90)
                   or (want == "low" and pct <= 10) else "*** CONTROL MISS ***")
        print(f"  {label}")
        print(f"    {a} / {d} deferred admitted = {pct:.1f} %   [{verdict}]")
    ok = (groups[("dot7", "deferred")]
          and 100 * groups[("dot7", "admitted")] / groups[("dot7", "deferred")] >= 90
          and (not groups[("negctl", "deferred")]
               or 100 * groups[("negctl", "admitted")]
               / groups[("negctl", "deferred")] <= 10))

    head("5. THE ANSWER — the seven miscellany files")
    d = groups[("misc", "deferred")]
    a = groups[("misc", "admitted")]
    b = groups[("misc", "br1shape")]
    print(f"  deferred entries in the miscellany files: {d}")
    print(f"  admitted by the bridge (branch 2, exact): {a}  "
          f"({100 * a / d if d else 0:.1f} %)")
    print(f"  further entries carrying the branch-1 shape (approximate): {b}")
    print(f"  LOWER BOUND on the bridge's reach here:   {a} of {d}")
    print()
    print("  A THIRD bridge-dependent family, falling out of the same table:")
    d1 = groups[("dot1", "deferred")]
    a1 = groups[("dot1", "admitted")]
    b1 = groups[("dot1", "br1shape")]
    print(f"    6.x.1 (c+d x)^m (a+b hyper)^n: {d1} deferred, {a1} admitted by")
    print(f"    branch 2 and {b1} more carrying branch 1's EXACT shape —")
    print(f"    {a1 + b1} of {d1}. Branch 1 exists for precisely this shape (it")
    print("    is the one branch that admits a polynomial factor), so these")
    print("    are bridge entries too; this probe does not port branch 1 and")
    print("    so does not close them.")
    print()
    print("  Rejection reasons, per file (branch 2):")
    for sf in sorted(reasons):
        if MISCELLANY.match(sf):
            print(f"    {sf[:50]:50s} " +
                  "  ".join(f"{k} {v}" for k, v in reasons[sf].most_common()))
    return groups, ok


def main():
    print("probes/rubi/03 — do the class-6 miscellany files ride the "
          "inert-trig bridge?")
    print("Static + one Maxima process (parser and walker only; no rule "
          "files, no integration).")
    for l in pinned():
        print("  " + l)
    if not os.path.exists(RECORD):
        print(f"MISSING {RECORD}")
        return 2
    work = tempfile.mkdtemp(prefix="mr-probe03-")
    print(f"  work dir: {work}")

    if not m0_selftest(work):
        return 1
    m1_file_pairing()
    meta, got = m2_classify(work)
    groups, controls_ok = m3_report(meta, got)

    head("CONCLUSION")
    if not controls_ok:
        print("A CONTROL MISSED. The classifier does not reproduce what probe "
              "02 already\nestablished, so none of its other numbers may be "
              "read. Fix the port of\nFunctionOfTrig / AlgebraicTrigFunctionQ "
              "before quoting anything here.")
        return 1
    d = groups[("misc", "deferred")]
    a = groups[("misc", "admitted")]
    b = groups[("misc", "br1shape")]
    d7, a7 = groups[("dot7", "deferred")], groups[("dot7", "admitted")]
    dm, am = d, a
    d1 = groups[("dot1", "deferred")]
    a1, b1 = groups[("dot1", "admitted")], groups[("dot1", "br1shape")]
    alldef = sum(v for (g, k), v in groups.items() if k == "deferred")
    tot = a7 + am + a1 + b1
    pct = 100 * tot / alldef if alldef else 0.0
    print(f"""\
Both controls hold, so the classifier reproduces the known case and the
miscellany number can be read.

The seven `Hyperbolic <fn> functions` / `6.7.1` files carry {d} deferred
entries. {a} of them ({100 * a / d if d else 0:.1f} %) satisfy
FunctionOfTrigOfLinearQ's exact branch-2 condition, so the bridge rule at the
head of 4.1.0.1 fires on them and hands them to section 4 in the inert
representation — the SAME route probe 02 measured for the `.7` family. A
further {b} carry the shape branch 1 exists to admit, which this probe does not
decide; {a} is therefore a lower bound.

WHAT THIS DOES AND DOES NOT SAY. It says the bridge ADMITS them: after
DeactivateTrig they are section-4 problems. It does NOT say section 4 answers
them — that depends on section 4's rule files covering the shapes, which is a
separate question and is what the class-4 port measures. The two claims must
not be conflated in a planning number.

CONSEQUENCE. The inert-trig substrate is load-bearing for more of class 6 than
probe 02 established: the `.7` family AND the admitted share of the miscellany
files ride the one bridge rule. Neither is reachable by porting section 6
alone, and both are already paid for once the substrate and section 4 land.

The bridge-dependent mass of class 6, added up from the table above:

  `.7`        {d7} deferred, {a7} admitted (branch 2, exact)
  miscellany  {dm} deferred, {am} admitted (branch 2, exact)
  `.1`        {d1} deferred, {a1} admitted + {b1} carrying branch 1's shape

  = {tot} of class 6's {alldef} deferred entries, {pct:.1f} %, turn on one rule.""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
