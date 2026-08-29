#!/usr/bin/env python3
"""Layer B: run the maxima-rubi package over a corpus section (the
class-1 section by default — the filter positional selects it), one
fresh Maxima subprocess per integral (the T3 probe-integrate-sample
mechanics with `rubi` in place of `integrate`).

Per-integral classification (one result line per integral in the .out,
one PASS:/FAIL: line on stdout):
  expected     answer; candidate - corpus expectation is zero-derivative
               within the zero-test chain
  verified     answer; diff(candidate, x) - integrand is zero within the
               chain, but candidate does not match the corpus expectation
  unverified   answer; neither zero-test closed within the chain
  no-answer    rubi returned a no-answer noun (the integrate fall-through
               or the package unintegrable noun); corpus also expects a noun
  deferred     rubi returned a TOP-LEVEL no-answer noun; corpus expects an
               ANSWER (a coverage gap: the ported rules did not reach this
               integrand — distinct from no-answer, which is the honest
               match on a noun-expected entry; T5's table predates this
               distinction, measured 2026-08-25: the 1.2.1.4 corpus file
               exercises Rubi's UNLOADED second 1.2.1.4 .m — 122 rules —
               so its 958 entries mass-defer and would read as PASS
               no-answer under the old class)
  unexpected   rubi returned an answer; corpus expects a noun
  error        subprocess died (Lisp error, parse-time fatality, or a
               missing CLASS line)
  timeout      per-process wall cap

Pass/fail mapping (T5 section 3): expected / verified / no-answer -> PASS;
unverified / deferred / unexpected / error / timeout -> FAIL.

The .out result line keeps the T3 shape
    <class>  t=<s>s <relpath> e<entry> L<line>
so the shard/resume line format carries over; the driver additionally
streams PASS:/FAIL: on stdout and ends with a `Results:` line.

Usage:
  corpus_driver.py [filter] [per-file] [timeout] [suite-dir]
      [start-index] [append] [skip-first] [out-file] [stop-index]
      [shard-file]

Defaults: the whole "1 Algebraic functions/" section, 5 entries per file,
30 s per-integral cap.

shard-file: a file of one whole-file index per line (indexes into the
sorted file list); when given, it REPLACES the start/stop range, so
parallel full-corpus runs can take load-balanced NON-CONTIGUOUS file
sets (measured 2026-08-25: the two giant files 1.1.1.2 / 1.1.1.3 are
1917 / 3189 entries vs a 34-entry minimum — contiguous ranges cannot
balance them).
"""

import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

HEAD_REWRITES = [
    # Corpus expected answers carry Rubi-notation special-function
    # heads; the package emits the native Maxima names (the generator
    # table). Rewrite the corpus text so both sides of the zero chain
    # carry the same (native, differentiable) head. Measured 2026-08-28
    # on 5.50.0: gamma_incomplete(a, z) is the UPPER 2-arg (d/dz =
    # -z^(a-1) %e^-z — the corpus GAMMA(a, z) convention), d/dz
    # expintegral_ei(z) = %e^z/z (probes/answer-side/
    # 01-answer-side-identities — the identities probed within the
    # harness zero chain; probes/corpus/02-class2-answer-heads
    # measures the head COUNTS only). The lookbehind keeps longer names
    # (e.g. a free function named "XEi") intact.
    (re.compile(r"(?<![A-Za-z0-9_])GAMMA\("), "gamma_incomplete("),
    (re.compile(r"(?<![A-Za-z0-9_])Ei\("), "expintegral_ei("),
    # Class-3 rows (2026-08-29): the "3 Logarithms" expected answers
    # carry the Rubi heads Chi( Shi( Si( Ci( Li(. Measured 2026-08-29 on
    # 5.50.0 (build 2026-08-29 17:58:20; plan
    # docs/superpowers/plans/2026-08-29-milestone-3-class3.md §Task-2
    # "Native conventions probed", .superpowers/sdd/task-2-report.md
    # :111-150): d/dx expintegral_shi(x) = sinh(x)/x, d/dx
    # expintegral_chi(x) = cosh(x)/x, d/dx expintegral_si(x) = sin(x)/x,
    # d/dx expintegral_ci(x) = cos(x)/x, d/dx expintegral_li(x) =
    # 1/log(x) — every residue 0; all five bound and float-evaluable,
    # the short names shi/chi/si/ci/li unbound nouns (naming trap).
    # No polylog( row: the package emits the native polylog( spelling
    # and the ACTIVE corpus expected texts are already natively
    # spelled — the PolyLog[ bracket lines in 3.5 are commented-out
    # entries the driver never reads.
    (re.compile(r"(?<![A-Za-z0-9_])Chi\("), "expintegral_chi("),
    (re.compile(r"(?<![A-Za-z0-9_])Shi\("), "expintegral_shi("),
    (re.compile(r"(?<![A-Za-z0-9_])Si\("), "expintegral_si("),
    (re.compile(r"(?<![A-Za-z0-9_])Ci\("), "expintegral_ci("),
    (re.compile(r"(?<![A-Za-z0-9_])Li\("), "expintegral_li("),
]
REWRITE_STATS = {}


def normalize_heads(text):
    for rx, rep in HEAD_REWRITES:
        text, n = rx.subn(rep, text)
        if n:
            REWRITE_STATS[rep] = REWRITE_STATS.get(rep, 0) + n
    return text


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
SECTION = "1 Algebraic functions"
PRELOAD = os.path.join("test", "mr_preload.mac")

# Option D (2026-08-26): the rules core — a saved Maxima image carrying the
# full loaded class-1 rule table, so each integral's subprocess starts from
# the image instead of re-running load + mr_load_class1_all (~6.2 s warm /
# ~9.4 s cold — measured probes/image/probe-rule-image.out, where the whole
# 25k run's 69.2 CPU-h was ~67 h of exactly this load). Built by
# test/build_rules_core.sh; the fingerprint sidecar must match the current
# rule files or the core is STALE (it bakes the rules in — using it after a
# rule edit without a rebuild would silently run the pre-edit rules).
# MR_RULES_CORE=0 forces the standard load path (A/B baseline).
RULES_CORE = os.path.join(ROOT, "test", "mr_rules.core")
RULES_CORE_STAMP = os.path.join(ROOT, "test", "mr_rules.core.stamp")
SBCL = os.environ.get("MR_SBCL") or subprocess.run(
    ["sh", "-c", "command -v sbcl"], capture_output=True, text=True
).stdout.strip() or None

FILTER = sys.argv[1] if len(sys.argv) > 1 else SECTION + "/"
PER_FILE = int(sys.argv[2]) if len(sys.argv) > 2 else 5
TIMEOUT = int(sys.argv[3]) if len(sys.argv) > 3 else 30
SUITE_DIR = sys.argv[4] if len(sys.argv) > 4 else SUITE
START_INDEX = int(sys.argv[5]) if len(sys.argv) > 5 else 0
APPEND = len(sys.argv) > 6 and sys.argv[6] == "append"
SKIP_FIRST = int(sys.argv[7]) if len(sys.argv) > 7 else 0
OUT_FILE = sys.argv[8] if len(sys.argv) > 8 else None
STOP_INDEX = int(sys.argv[9]) if len(sys.argv) > 9 else None
SHARD_FILE = sys.argv[10] if len(sys.argv) > 10 else None

KNOWN_CLASSES = {
    "expected", "verified", "unverified", "contains-noun",
    "no-answer", "deferred", "unexpected", "error", "timeout",
}
PASS_CLASSES = {"expected", "verified", "no-answer"}


def _core_fingerprint():
    """md5 over exactly the files test/build_rules_core.sh bakes into the
    image (loader + utils + dispatch lisp + implicit-1 lisp + every
    class-1, class-2 AND class-3 rule file)."""
    import glob
    import hashlib
    # Canonical order: sorted RELATIVE paths (must match
    # test/build_rules_core.sh exactly — an order difference makes every
    # freshly built core look stale, measured 2026-08-26).
    rels = sorted(["maxima_rubi.mac", "maxima_rubi_utils.mac",
                   "maxima_rubi_dispatch.lisp",
                   "maxima_rubi_implicit1.lisp"] +
                  [os.path.relpath(p, ROOT) for p in
                   glob.glob(os.path.join(ROOT, "rules", "class1", "*.mac"))] +
                  [os.path.relpath(p, ROOT) for p in
                   glob.glob(os.path.join(ROOT, "rules", "class2", "*.mac"))] +
                  [os.path.relpath(p, ROOT) for p in
                   glob.glob(os.path.join(ROOT, "rules", "class3", "*.mac"))])
    h = hashlib.md5()
    for rel in rels:
        with open(os.path.join(ROOT, rel), "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()


def rules_core_state():
    """'off' | 'on' | 'stale' | 'missing' for the core vs current rules."""
    if os.environ.get("MR_RULES_CORE", "1") == "0":
        return "off"
    if not (os.path.exists(RULES_CORE) and os.path.exists(RULES_CORE_STAMP)):
        return "missing"
    fp = None
    with open(RULES_CORE_STAMP, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("fingerprint "):
                fp = line.split()[1]
    if fp is None:
        return "stale"
    return "on" if fp == _core_fingerprint() else "stale"


def ensure_rules_core():
    """Make the rules core available; True iff the core path will be used.
    Builds (single-flight via a flock) when missing or stale; a failed build
    falls back to the standard load path rather than blocking the run."""
    st = rules_core_state()
    if st == "on":
        return True
    if st == "off" or SBCL is None:
        return False
    import fcntl
    lock = open(RULES_CORE + ".lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if rules_core_state() == "on":  # built while we waited
            return True
        r = subprocess.run(
            ["sh", os.path.join(ROOT, "test", "build_rules_core.sh")],
            capture_output=True, text=True, timeout=300, cwd=ROOT)
        if r.returncode != 0:
            sys.stderr.write("rules-core build failed; using standard load:\n"
                             + r.stdout[-800:] + r.stderr[-800:])
            return False
        return rules_core_state() == "on"
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)


USE_RULES_CORE = ensure_rules_core()

workdir = tempfile.mkdtemp(prefix="maxima-rubi-corpus-")
mac_file = os.path.join(workdir, "i.mac")


def maxima_run(mac_text, timeout):
    # A unique per-call file (mkstemp) so parallel canary workers don't
    # clobber each other's batch; the driver's sequential use is unaffected.
    fd, fpath = tempfile.mkstemp(prefix="mr-", suffix=".mac", dir=workdir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(mac_text)
        if USE_RULES_CORE:
            # Option D: start from the rules image (rules + batch_answers_
            # from_file baked in — no -p preload). The image's SAVED
            # toplevel is cl-user::run (set at build time), so no --eval is
            # needed; the bare maxima options after the sbcl options become
            # the toplevel args the image's arg parser reads, giving a clean
            # arg context (the stock-wrapper form with --eval/--end-
            # toplevel-options leaks sbcl meta-args into maxima's parser and
            # prints "Warning: argument ... not recognized" — measured
            # 2026-08-26, this minimal form is byte-clean). --tls-limit is
            # TWO argv tokens for sbcl (one quoted token for maxima -X).
            cmd = [SBCL, "--tls-limit", "100000", "--core", RULES_CORE,
                   "--noinform", "--very-quiet", "-b", fpath]
        else:
            cmd = ["maxima", "--very-quiet", "-X", "--tls-limit 100000",
                   "-p", PRELOAD, "-b", fpath]
        r = subprocess.run(
            cmd,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, timeout=timeout, cwd=ROOT,
        )
        return r.stdout, False
    except subprocess.TimeoutExpired as e:
        out = e.stdout
        if isinstance(out, bytes):
            out = out.decode("utf-8", "replace")
        return out or "", True
    finally:
        try:
            os.unlink(fpath)
        except OSError:
            pass


def split_elements(entry_text):
    """Depth-aware split at top-level commas; keeps all delimiters."""
    parts, depth, cur = [], 0, ""
    for ch in entry_text:
        if ch in "[(":
            depth += 1
        elif ch in "])":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts]


def extract_entries(path):
    """Entry texts (outer brackets, no trailing comma/$) + source line numbers."""
    lines = open(path, encoding="utf-8").read().splitlines()
    entries, line_nos = [], []
    for i, l in enumerate(lines, 1):
        if l.strip().startswith("["):
            t = l.rstrip()
            if t.endswith("$"):
                t = t[:-1]
            if t.endswith(","):
                t = t[:-1]
            entries.append(t)
            line_nos.append(i)
    assert entries and entries[-1].endswith("]]"), path
    entries[-1] = entries[-1][:-1]
    return entries, line_nos


def zero_chain(d_expr, var):
    """Statement list whose value is 1 iff the zero-test closes.

    The whole chain is errcatch'd: a ratsimp/factor crash inside the
    VERIFICATION (measured 2026-08-24: `quotient' by `zero' on 1.2.2.4
    e165 / 1.2.2.8 e1) is an unverified zero-test, not a subprocess
    fatality — without the guard the error kills Maxima before the CLASS
    line and the entry is misclassified `error`. errcatch in this build
    returns [value] on success and [] on error (probe-errcatch-semantics).

    Stage order (measured 2026-08-25, 5.50.0/SBCL): TWO full chains —
    factor-first, then ratsimp-first — because closure is ORDER-
    DEPENDENT and no single order is uniformly cheap:
      - radical diffs (correct package answer): factor closes in ~2 s,
        ratsimp hangs >50 s (1.2.2.7 e1);
      - 1.2.2.3 e1's expected-diff: factor-first chain = 47 s,
        ratsimp-first chain = 9 s;
      - 1.2.2.4 e165's self-diff closes only under the ratsimp-first
        order (ratsimp(expand(ratsimp(D))) = 0; the same stages after a
        leading factor do not close).
    Each chain keeps the errcatch-crash semantics; a crash in either
    chain is an unverified zero-test, not a fatality. The canary cap
    is 60 s (test/canary.py) to hold both chains.

    Fallback (measured 2026-08-28, 5.50.0/SBCL): when the chain did
    not close, an elliptic-gated, errcatched `radcan(rat(MR_de))`
    attempt runs — it closes zero-diffs of the `quotient' by 'zero'
    zero-divisor class that no ratsimp/factor stage closes (1.1.3.8
    e541/e543/e544, 1.2.1.4 e764). The gate skips elliptic-carrying
    diffs (radcan(rat()) burns 30-100 s crashing on them — see the
    measured note in the code below); a chain that closed returns 1
    without running the fallback.
    """
    # Stage list: (expr to assign to MR_d, ...) — each stage reworks the
    # previous MR_d; stage 1 of chain 2 restarts from the raw diff
    # (MR_de — materialized ONCE: ev'd over a still-unevaluated
    # diff(mr_r, x) substitutes x into the diff's variable argument and
    # errors "second argument must be a variable; found 0.35", measured
    # 2026-08-25). Stages are built programmatically so the
    # nested-paren count can never drift (the hand-nested string
    # miscounted twice, measured 2026-08-25).
    stages = ["factor(MR_de)",
              "ratsimp(MR_d)",
              "ratsimp(expand(MR_d))",
              "ratsimp(factor(MR_d))",
              "ratsimp(MR_de)",
              "ratsimp(expand(MR_d))",
              "factor(MR_d)",
              "ratsimp(factor(MR_d))"]
    # FIRST numeric stage (measured 2026-08-25, 5.50.0/SBCL): correct
    # Prompt budget (measured 2026-08-25, 5.50.0/SBCL): integrate's sign
    # prompts are answered from the batch input stream, and a target that
    # asks MORE questions than queued lines exhausts the stream — the
    # reader hits EOF ("RETRIEVE: End of file encountered."), the batch
    # dies before the CLASS line, and the entry misclassifies `error`
    # (1.2.1.6 e77: the substring-fatality fix let its cascade reach the
    # integrate fallback, which asked 13-20 questions vs the old 6/6
    # budget). 40 pos + 20 no per stage covers the deepest cascade
    # measured so far; an exhausted budget now degrades to `no` answers
    # (graceful, classification-safe) rather than an EOF death. The pos-
    # first order keeps Rubi's all-parameters-positive convention for as
    # many questions as the budget reaches.
    # answers whose diff carries elliptic_f/elliptic_e terms close under
    # NO symbolic stage — 1.2.1.3 e1058 (after the SubstPower sqrt-head
    # fix) is numerically exact (resid ~1e-15) but ratsimp/expand/factor
    # all fail on its elliptic diff, and one of the symbolic stages
    # CRASHES on it, so the single outer errcatch swallows the chain
    # before a trailing numeric stage could run — the numeric stage
    # therefore leads. Evaluate the diff at two points under the sweep
    # parameter values (the same substitution the wrong-answer triage
    # sweep uses); a float eval that still carries a symbolic parameter
    # returns a float NOUN, whose is(abs(.) < 1e-9) is false — so
    # symbolic-parameter targets are unaffected. A domain error (sqrt
    # of negative, /0) at a test point is caught by the stage's OWN
    # errcatch (measured 2026-08-25: letting such a domain error reach
    # the OUTER errcatch kills the whole chain — 5 previously-verified
    # targets, incl. 1.3.1 e1, regressed to unverified) and reads as
    # "numeric stage declined, try the symbolic stages". Leading also
    # saves the 60 s budget-eaters (1.1.2.4 e983 / 1.1.4.2 e182, both
    # measured numerically correct) from burning the cap on the
    # symbolic stages.
    # NOTE: errcatch WRAPS its success value in a list (measured
    # 2026-08-25: errcatch([f1, f2]) returns [[v1, v2]], so the
    # two-point list form double-wraps and the condition dies) — each
    # point gets its own errcatch, unwrapped with part(., 1).
    # a = 0.9 (not 0.7): the quadratic-family reductions carry
    # sqrt(4*a*c-b^2)-type branch terms, and 4*0.7*0.5-1.3^2 < 0 made
    # the float eval take the COMPLEX branch of a branch-dependent
    # (otherwise correct) answer, reading as a huge residual — measured
    # 2026-08-25: 1.2.2.2 e957 and 1.2.1.5 e105 are numerically exact
    # under 4ac-b^2 > 0 (resid ~1e-16) but "wrong" (resid 0.6-1.6 /
    # exactly d) under 4ac-b^2 < 0. 4*0.9*0.5-1.3^2 = 0.11 > 0 and
    # a+b*x+c*x^2 > 0 at both test points.
    # p = 2: generic-exponent targets (free p, e.g. 1.2.1.4 e383
    # x^3(d+e x)(a+b x^2)^p) otherwise defeat the stage — a float eval
    # carrying the free p returns a float NOUN and the stage declines —
    # while their formal zero chain cannot close the p-dependent diff
    # (measured 2026-08-25: e383's answer is CORRECT, verified by
    # instance at p = 2 / -3 / 5, resid ~1e-17). Substituting p = 2
    # checks the p=2 instance (same standard as every other numeric
    # verification); a target whose p=2 instance hits a domain error
    # declines via the stage's own errcatch exactly as today, and a
    # target with NO free p is untouched (its 3/2-style exponents are
    # concrete, not the symbol p). p = 2 avoids the reduction-family
    # 1/(p+1) / 1/(2p+3) coefficient singularities (p+1 = 3, 2p+3 = 7).
    subs = ("a=0.9, b=1.3, c=0.5, d=0.9, e=1.1, f=0.8, g=1.7, h=0.3, "
            "A=0.6, B=1.4, C=0.4, D=0.9, p=2")
    symbolic = "0"
    for s in reversed(stages):
        symbolic = f"MR_d: {s}, if is(MR_d=0) then 1 else (" + symbolic + ")"
    numeric = ("MR_de: " + d_expr + ", "
               "MR_z1 : errcatch(float(ev(MR_de, [" + subs + ", "
               + var + "=0.35]))), "
               "if MR_z1 = [] then (" + symbolic + ") else ("
               "MR_z2 : errcatch(float(ev(MR_de, [" + subs + ", "
               + var + "=0.65]))), "
               "if MR_z2 = [] then (" + symbolic + ") else ("
               "if is(abs(part(MR_z1, 1)) < 1e-9) = true "
               "and is(abs(part(MR_z2, 1)) < 1e-9) = true "
               "then 1 else (" + symbolic + ")))")
    inner = numeric
    # Fallback (measured 2026-08-28, 5.50.0/SBCL): if the chain above
    # did not close, try `radcan(rat(MR_de))` — a different algorithm
    # (full rational-function reduction over the algebraic extension +
    # radical normalization). The redundant algebraic-generator
    # zero-divisor bug (`quotient' by 'zero' in ratsimp's gcd
    # reduction; minimal hand-typed repro:
    # probes/maxima/probe-ratsimp-zero-divisor.mac) defeats every
    # ratsimp/factor stage on some zero-diffs while radcan(rat())
    # closes the same diff: measured 2026-08-28, 1.1.3.8 e541/e543/
    # e544 and 1.2.1.4 e764 (`unverified` in the 2026-08-27 record)
    # close under the fallback. Gated on a no-elliptic diff:
    # measured 2026-08-28 — radcan(rat()) crashes with
    # `PTPTQUOTIENT: Polynomial quotient is not exact' after
    # burning 30-100 s on elliptic-family zero-diffs (1.2.1.3
    # e455-e484 family). Trade measured by probe v2 (docs/corpus-
    # radcan-fallback-attribution.md): the gate also blocks 35 A/B
    # gains whose elliptic-carrying diffs radcan(rat()) DOES close
    # in 1-2 s (22 crash entries of 1.1.3.x/1.2.2.x/1.3.2 plus 13
    # chain-FINISHED entries) — a static elliptic gate cannot
    # separate the fast-closers from the 30-100 s burners. The
    # other crash classes measured on `unverified`-entry zero-diffs
    # are immediate and errcatched:
    # `expt: undefined: 0 to a negative exponent' (1.3.1 e147) and
    # the zero-divisor bug via the fallback itself (1.1.1.2 e1501).
    # The gate is apply(freeof, [syms..., MR_de]) — the documented
    # variadic form `freeof(x1, ..., xn, expr)` == `freeof(x1, expr)
    # and ... and freeof(xn, expr)` (freeof manual entry, 5.50.0),
    # spliced over the symbol list. The earlier list-first-arg form
    # freeof([syms], expr) is NOT a documented freeof call: it is read
    # as "does the LIST occur in expr" and returned true on
    # elliptic-carrying diffs (measured 2026-08-28: freeof(
    # [elliptic_f], elliptic_f(x, -4)) = true) — a silently no-op
    # gate that let radcan(rat()) run on elliptic-diffs, burning the
    # 30 s cap on 28 entries (18 of them 1.2.1.3 e440-e484
    # unverified->timeout) in the 2026-08-28 A/B.
    fallback = ("if apply(freeof, [elliptic_f, elliptic_e, elliptic_pi, "
                "elliptic_ec, elliptic_eu, elliptic_kc, MR_de]) = true "
                "then block([MR_fb], "
                "MR_fb : errcatch(radcan(rat(MR_de))), "
                "if MR_fb = [] then 0 "
                "else (MR_fb : part(MR_fb, 1), "
                "if is(MR_fb = 0) then 1 else 0)) "
                "else 0")
    return (
        "block([MR_zr, MR_zf], MR_zr : errcatch(" + inner + "), "
        "if MR_zr # [] and part(MR_zr, 1) = 1 then 1 "
        "else (MR_zf : errcatch(" + fallback + "), "
        "if MR_zf = [] then 0 else part(MR_zf, 1)))"
    )


def build_text(f_text, var_text, e_text, e_text2=None):
    # mr_/MR_ template variables: the pasted corpus text is re-parsed in
    # their scope, so the names must not collide with corpus symbols.
    # Noun detector: the rubi fall-through is the integrate noun; the
    # package's explicit no-answer noun is `unintegrable`.
    # Default mode is rules-only (2-arg rubi — a 0-firing top level is
    # the fast no-answer noun, the Step-2 gap list); MR_FALLBACK=1
    # restores the status-quo top-level integrate fall-through (A/B
    # baseline runs). Maxima has no arity overloading, so the fallback
    # mode is the distinct entry rubi_fallback (utils file, measured
    # 2026-08-24).
    if os.environ.get("MR_FALLBACK") == "1":
        call = f"rubi_fallback(mr_f, {var_text}, true)"
    else:
        call = f"rubi(mr_f, {var_text})"
    noun = ("block([], if atom(mr_r) then 0 else "
            "if is(string(op(mr_r)) = \"integrate\") "
            "or is(string(op(mr_r)) = \"unintegrable\") "
            "then 1 else 0)")
    # Contains-noun sub-classification: an answer that CONTAINS Rubi's
    # CannotIntegrate marker (port: the `unintegrable` subscript noun —
    # 1.1.1.4.m:47 and the sibling family catch-alls port it faithfully;
    # Rubi 4 itself returns the inert Int there, so the cascade result
    # legitimately carries it) or a native `integrate` noun somewhere in
    # its interior. diff() evaluates such heads to 0, so the zero chains
    # can never verify the answer — an honest FAIL sub-class, not an
    # unexplained `unverified`. The check is one freeof() call (cheap)
    # and runs BEFORE the zero chains, which would otherwise burn the
    # whole per-target budget on a noun-laden diff (measured 2026-08-25:
    # 1.1.1.7 e30). Only the `unintegrable` marker is poison: an
    # `integrate[g, x]` head inside an answer is a LEGITIMATE explicit
    # integral term — Maxima's diff knows d/dx ∫g dx = g, so such
    # answers verify normally (measured: 1.2.2.7 e1 carries a ∫-term
    # and its self-diff closes).
    has_noun = "not is(freeof(unintegrable, mr_r))"
    head = (f"mr_f: {f_text}$\n"
            f"mr_r: {call}$\n"
            + "pos$\n" * 40 + "no$\n" * 20)
    if e_text.startswith(("Unintegrable", "CannotIntegrate")):
        # Interior-marker check FIRST (the other branch's has_noun): the
        # top-level noun detector only sees op(mr_r), so a partial
        # reduction whose interior carries the `unintegrable` catch-all
        # marker is NOT a top-level noun and would misclassify `unexpected`
        # — it is contains-noun (measured 2026-08-27: 1.1.2.5 e103/e107/
        # e110, the pinned Rubi's r30 p<0,q>0 reduction whose nested
        # integrals fall to the file catch-all; their zero chains cannot
        # close because the markers' integrands survive diff).
        body = (f"if is({noun} = 1) then disp(concat(\"CLASS no-answer\")) "
                f"else if is({has_noun}) then disp(concat(\"CLASS contains-noun\")) "
                f"else disp(concat(\"CLASS unexpected\"))")
    else:
        # The corpus expected text is inlined into the subtraction and MUST
        # be parenthesized: an expected answer that is a SUM `A + B` would
        # otherwise parse as `mr_r - A + B` (the sign of every term after
        # the first is flipped), so a correct antiderivative fails the
        # zero-test and is misclassified `unverified` (measured 2026-08-24
        # on 1.3.2 e1: `mr_r - <e>` residual nonzero, `mr_r - (<e>)` zero).
        # The SELF-diff (zv) is checked FIRST: for a correct answer it
        # closes on the cheap factor stage, and a non-closing expected-
        # diff (the package's right answer in a different radical form)
        # would otherwise burn the whole per-target budget and starve
        # the self-diff (measured 2026-08-25: 1.1.2.4 e983 / 1.1.4.2
        # e182, both numerically correct, timed out under ze-first).
        # "verified" and "expected" are both PASS classes, so the
        # reordering is classification-safe.
        ze = zero_chain(f"diff(mr_r - ({e_text}), {var_text})", var_text)
        zv = zero_chain(f"diff(mr_r, {var_text}) - mr_f", var_text)
        if e_text2 is not None:
            ze2 = zero_chain(f"diff(mr_r - ({e_text2}), {var_text})", var_text)
            body = (f"if is({noun} = 1) then disp(concat(\"CLASS deferred\")) "
                    f"else if is({has_noun}) then disp(concat(\"CLASS contains-noun\")) "
                    "else block([MR_z, MR_z2, MR_w], MR_w: (" + zv + "), "
                    "if is(MR_w=1) then disp(concat(\"CLASS verified\")) "
                    "else (MR_z: (" + ze + "), MR_z2: (" + ze2 + "), "
                    "if is(MR_z=1) or is(MR_z2=1) "
                    "then disp(concat(\"CLASS expected\")) "
                    "else disp(concat(\"CLASS unverified\"))))")
        else:
            body = (f"if is({noun} = 1) then disp(concat(\"CLASS deferred\")) "
                    f"else if is({has_noun}) then disp(concat(\"CLASS contains-noun\")) "
                    "else block([MR_z, MR_w], MR_w: (" + zv + "), "
                    "if is(MR_w=1) then disp(concat(\"CLASS verified\")) "
                    "else (MR_z: (" + ze + "), "
                    "if is(MR_z=1) then disp(concat(\"CLASS expected\")) "
                    "else disp(concat(\"CLASS unverified\"))))")
    return head + body + "$\n" + "pos$\n" * 40 + "no$\n" * 20


def file_list():
    """Sorted (path, relpath) of every .mac matching FILTER."""
    if SUITE_DIR == SUITE:
        walk_root = os.path.join(SUITE, SECTION)
        rel_root = SUITE
    else:
        walk_root = SUITE_DIR
        rel_root = SUITE_DIR
    files = []
    for dirpath, _dn, filenames in os.walk(walk_root):
        for fn in filenames:
            if fn.endswith(".mac"):
                p = os.path.join(dirpath, fn)
                rel = os.path.relpath(p, rel_root)
                if FILTER in rel:
                    files.append((p, rel))
    files.sort(key=lambda t: t[1])
    return files


def main():
    all_files = file_list()
    bounds = None
    if SHARD_FILE:
        # Each line is a whole file ("idx") or a chunk of one file
        # ("idx skip per" -> process entries skip..skip+per-1). Chunks let a
        # shard hold a slice of a big file together with whole files, which
        # is what cost-aware balancing needs (the plain start/stop range can
        # only cap the FIRST file).
        specs = []
        for ln in open(SHARD_FILE):
            ln = ln.strip()
            if not ln:
                continue
            parts = ln.split()
            idx = int(parts[0])
            if len(parts) == 1:
                specs.append((idx, 0, None))
            elif len(parts) == 3:
                skip = int(parts[1])
                specs.append((idx, skip, skip + int(parts[2])))
            else:
                raise SystemExit(f"bad shard file line: {ln!r}")
        specs.sort(key=lambda t: t[0])
        assert all(0 <= i < len(all_files) for i, _lo, _hi in specs), \
            "shard file index out of range"
        files = [all_files[i] for i, _lo, _hi in specs]
        bounds = [(lo, hi) for _i, lo, hi in specs]
    else:
        files = all_files[START_INDEX:STOP_INDEX]

    out_lines = [
        (f"=== maxima-rubi corpus driver (filter {FILTER!r}, "
         f"resume at file index {START_INDEX}) ==="
         if APPEND else
         f"=== maxima-rubi corpus driver (filter {FILTER!r}) ==="),
        f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
    ]
    if not APPEND:
        r = subprocess.run(
            ["maxima", "--very-quiet", "--batch-string",
             "disp(build_info());"],
            capture_output=True, text=True, timeout=120, cwd=ROOT,
        )
        for line in r.stdout.splitlines():
            line = line.strip()
            if line.startswith(("Maxima", "Lisp ", "Host ")):
                out_lines.append(f"maxima: {line}")
    out_lines.append(f"filter: {FILTER!r}  per-file: {PER_FILE}  "
                     f"timeout: {TIMEOUT}s  files: {len(files)}"
                     + (f"  shard: {SHARD_FILE}" if SHARD_FILE else ""))
    out_lines.append("")

    counts = {}
    t0 = time.time()
    out_path = (OUT_FILE or os.path.join(ROOT, "test",
                                         "corpus_class1_driver.out"))
    outf = open(out_path, "a" if APPEND else "w", encoding="utf-8")
    outf.write("\n".join(out_lines) + "\n")
    outf.flush()
    for fi, (path, rel) in enumerate(files):
        try:
            entries, line_nos = extract_entries(path)
        except (AssertionError, UnicodeDecodeError, IndexError):
            out_lines.append(f"SKIP-BADFILE {rel}")
            continue
        if bounds is not None:
            lo, hi = bounds[fi]
            hi = len(entries) if hi is None else min(hi, len(entries))
        else:
            lo = SKIP_FIRST if fi == 0 else 0
            hi = min(lo + PER_FILE, len(entries))
        for idx in range(lo, hi):
            els = split_elements(entries[idx][1:-1])
            label = f"{rel} e{idx + 1} L{line_nos[idx]}"
            if len(els) not in (4, 5):
                cls = "error"
                counts[cls] = counts.get(cls, 0) + 1
                line = f"{'error':14s} t=0.0s {label} bad-entry-shape({len(els)})"
                out_lines.append(line)
                outf.write(line + "\n")
                outf.flush()
                print(f"FAIL: {line}")
                continue
            f_text = normalize_heads(els[0])
            var_text = els[1]
            _steps = els[2]
            e_text = normalize_heads(els[3])
            e_text2 = normalize_heads(els[4]) if len(els) == 5 else None
            t_start = time.time()
            out, timed_out = maxima_run(
                build_text(f_text, var_text, e_text, e_text2), TIMEOUT)
            dt = time.time() - t_start
            cls = None
            for line in out.splitlines():
                line = line.strip()
                if line.startswith("CLASS "):
                    cls = line[6:].strip()
                    break
            if cls is None:
                cls = "timeout" if timed_out else "error"
            if cls not in KNOWN_CLASSES:
                cls = "error"
            counts[cls] = counts.get(cls, 0) + 1
            pf = "PASS" if cls in PASS_CLASSES else "FAIL"
            line = f"{cls:14s} t={dt:6.1f}s {label}"
            out_lines.append(line)
            outf.write(line + "\n")
            outf.flush()
            print(f"{pf}: {line}")
    total = sum(counts.values())
    passed = sum(v for k, v in counts.items() if k in PASS_CLASSES)
    failed = total - passed

    out_lines.append("")
    out_lines.append("=== summary ===")
    # AFTER the entry loop: the header is built before any
    # normalize_heads() ran, so the line would read {} there even when
    # rewrites fired (measured 2026-08-28, review of a3ee89c).
    out_lines.append(f"head rewrites: {REWRITE_STATS or '{}'}")
    for k in sorted(counts):
        out_lines.append(f"{k:14s} {counts[k]}")
    out_lines.append(f"total integrals: {total}")
    out_lines.append(f"wall time: {time.time() - t0:.1f}s")
    out_lines.append(f"Results: {passed} passed, {failed} failed")

    outf.write("\n".join(out_lines[out_lines.index("=== summary ==="):]) + "\n")
    outf.close()
    print("\n".join(out_lines[-8:]) + "\n")


if __name__ == "__main__":
    main()
