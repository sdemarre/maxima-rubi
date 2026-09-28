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

import importlib.util
import os
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone

def _call_args(s, open_i):
    """The top-level argument texts of the call whose '(' is s[open_i], and
    the index just past its ')' -- or (None, open_i) when unbalanced.
    Commas inside (), [] or {} do not split (hypergeometric([1,1],[2],z))."""
    depth, start, args = 0, open_i + 1, []
    for i in range(open_i, len(s)):
        ch = s[i]
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
            if depth == 0:
                args.append(s[start:i])
                return args, i + 1
        elif ch == "," and depth == 1:
            args.append(s[start:i])
            start = i + 1
    return None, open_i


def _by_arity(head, table):
    """A HEAD_REWRITES replacement for `head(`, chosen by the call's
    argument count; an arity the table lacks is left as written."""
    def rep(m):
        args, _ = _call_args(m.string, m.end() - 1)
        return table.get(len(args) if args is not None else -1, m.group(0))
    rep.labels = table
    return rep


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
    # GAMMA( and Ei( are ARITY-dispatched since class 8 (2026-09-25; the
    # _by_arity rows below): section 8 is the first to carry 1-arg GAMMA
    # (Gamma[z] -> gamma, 18 uses) and 2-arg Ei (ExpIntegralE[n, z] ->
    # expintegral_e, 334 uses; probes/corpus/15-class8-answer-heads.out),
    # which the old arity-blind rows turned into gamma_incomplete(z) and
    # expintegral_ei(n, z). The class-2 readings (2-arg GAMMA, 1-arg Ei)
    # are unchanged, and the accepted sections carry no other arity
    # (classes 2/3/6 only 1-arg Ei and 2-arg GAMMA, class 1 neither).
    (re.compile(r"(?<![A-Za-z0-9_])GAMMA\("),
     _by_arity("GAMMA", {1: "gamma(", 2: "gamma_incomplete("})),
    (re.compile(r"(?<![A-Za-z0-9_])Ei\("),
     _by_arity("Ei", {1: "expintegral_ei(", 2: "expintegral_e("})),
    # Class-3 rows (2026-08-29): the "3 Logarithms" expected answers
    # carry the Rubi heads Chi( Shi( Si( Ci( Li(. Measured on 5.50.0 —
    # the committed re-runnable form:
    # probes/answer-side/02-class3-answer-side-identities (build
    # 2026-08-29 17:58:20; plan
    # docs/superpowers/plans/2026-08-29-milestone-3-class3.md §Task-2
    # "Native conventions probed"): d/dx expintegral_shi(x) = sinh(x)/x, d/dx
    # expintegral_chi(x) = cosh(x)/x, d/dx expintegral_si(x) = sin(x)/x,
    # d/dx expintegral_ci(x) = cos(x)/x, d/dx expintegral_li(x) =
    # 1/log(x) — every residue 0; all five bound and float-evaluable.
    # The short names shi/chi/si/ci are unbound nouns (naming trap);
    # lowercase li is the BOUND native polylogarithm — describe(li,
    # exact): "Function: li [<s>] (<z>) ... the polylogarithm
    # function"; ev(li[2](0.5)) = 0.5822405264650125 (measured
    # 2026-08-29 on this build) — but a distinct token (lowercase,
    # subscript-arg form li[s](z)), so the uppercase Li( row cannot
    # collide with it.
    # No polylog( row: polylog(A, B) -> li[A](B) is a STRUCTURAL rewrite
    # (rewrite_structural below), since 2026-09-26 — before, the package
    # emitted the corpus's own unknown polylog( spelling and the corpus
    # was read as written (.scratch/polylog-native-li/issues/01).
    (re.compile(r"(?<![A-Za-z0-9_])Chi\("), "expintegral_chi("),
    (re.compile(r"(?<![A-Za-z0-9_])Shi\("), "expintegral_shi("),
    (re.compile(r"(?<![A-Za-z0-9_])Si\("), "expintegral_si("),
    (re.compile(r"(?<![A-Za-z0-9_])Ci\("), "expintegral_ci("),
    (re.compile(r"(?<![A-Za-z0-9_])Li\("), "expintegral_li("),
    # Class-8 rows (2026-09-25): the "8 Special functions" answer heads onto
    # the natives the class-8 rules emit (generator/translation_table.py).
    # Each native differentiates through this driver's zero_chain and
    # float-evaluates, build branch_5_50_base_84_g4204fb669
    # (probes/answer-side/04-class8-answer-side-identities.out: fresnel_s /
    # fresnel_c A1/A2, lambert_w A7, log_gamma A10, factorial A11,
    # hypergeometric A13). Counts: probes/corpus/15-class8-answer-heads.out
    # (ProductLog( 1695, FresnelS( 424, FresnelC( 418, HypergeometricPFQ(
    # 137, lnGAMMA( 22, Factorial( 2). lnGAMMA is Mathematica's LogGamma;
    # the rules emit log(gamma(z)) for it (the class-3 decision), which
    # differentiates to the same psi[0](z). HypergeometricPFQ's list
    # arguments are already Maxima lists in the corpus text.
    (re.compile(r"(?<![A-Za-z0-9_])ProductLog\("), "lambert_w("),
    (re.compile(r"(?<![A-Za-z0-9_])FresnelS\("), "fresnel_s("),
    (re.compile(r"(?<![A-Za-z0-9_])FresnelC\("), "fresnel_c("),
    (re.compile(r"(?<![A-Za-z0-9_])lnGAMMA\("), "log_gamma("),
    (re.compile(r"(?<![A-Za-z0-9_])HypergeometricPFQ\("), "hypergeometric("),
    (re.compile(r"(?<![A-Za-z0-9_])Factorial\("), "factorial("),
]
REWRITE_STATS = {}
# The queue runner (test/run_corpus_queue.py) calls normalize_heads from its
# worker threads; the counter update takes the lock.
REWRITE_LOCK = threading.Lock()


_DERIVATIVE = re.compile(r"(?<![A-Za-z0-9_%])Derivative\(")
_PSI = re.compile(r"(?<![A-Za-z0-9_%])Psi\(")
_H2F1 = re.compile(r"(?<![A-Za-z0-9_%])Hypergeometric2F1\(")
_POLYLOG = re.compile(r"(?<![A-Za-z0-9_%])polylog\(")


def rewrite_structural(text):
    """The class-8 STRUCTURAL rewrites (not table rows: the head's argument
    list changes shape), applied before the rows. Returns (text, counts).

    - Derivative(A)(B)(C) -> %mr_derivative(A, B, C): Mathematica's formal
      derivative Derivative[A][B][C] as the corpus spells it. The package
      function builds Maxima's own derivative noun 'diff(B(C), C, A) (order
      0: B(C)) -- the class-8 design, .scratch/class-ports/issues/01
      ("DESIGN"); the zero-chain identities it relies on are
      probes/answer-side/04-class8-answer-side-identities.out N1-N17.
      Nested derivatives inside the groups are rewritten too. A
      Derivative( not followed by exactly three groups is left as written.
    - Psi(A, B) -> psi[A](B): PolyGamma[A, B] (A the order, negative ones
      included) as Maxima's subscripted polygamma, which differentiates
      (probe 04 A8/A9). Only the 2-argument form.
    - Hypergeometric2F1(A, B, C, Z) -> hypergeometric([A, B], [C], Z)
      (class 4, 2026-09-25): Gauss's 2F1 as the native generalized
      hypergeometric the rules emit for it (generator/generate_rules.py's
      Hypergeometric2F1 case; the class-8 HypergeometricPFQ row's target,
      which differentiates -- probes/answer-side/04 A13). Only the
      4-argument form; three occurrences over two corpus entries, both in 4.1.1.3
      (probes/corpus/14-class4-answer-heads.out).
    - polylog(A, B) -> li[A](B) (2026-09-26, .scratch/polylog-native-li/
      issues/01): the corpus spells Rubi's PolyLog[A, B] as polylog(A, B),
      an operator Maxima does not know (no diff, no float); li[A](B) is
      Maxima's native subscripted polylogarithm, which the rules emit.
      Every class that carries it (2-8), integrands and expected answers
      alike. Only the 2-argument form."""
    counts = {}

    def inner(t):
        r, c = rewrite_structural(t)
        for k, v in c.items():
            counts[k] = counts.get(k, 0) + v
        return r.strip()

    out, i = [], 0
    while True:
        md, mp = _DERIVATIVE.search(text, i), _PSI.search(text, i)
        mh, ml = _H2F1.search(text, i), _POLYLOG.search(text, i)
        m = min((x for x in (md, mp, mh, ml) if x), key=lambda x: x.start(),
                default=None)
        if m is None:
            out.append(text[i:])
            break
        out.append(text[i:m.start()])
        j = m.end() - 1
        if m is md:
            groups = []
            while len(groups) < 3 and j < len(text) and text[j] == "(":
                args, k = _call_args(text, j)
                if args is None or len(args) != 1:
                    break
                groups.append(args[0])
                j = k
            if len(groups) == 3:
                out.append("%mr_derivative("
                           + ", ".join(inner(g) for g in groups) + ")")
                counts["%mr_derivative("] = counts.get("%mr_derivative(", 0) + 1
                i = j
                continue
        elif m is mh:
            args, k = _call_args(text, j)
            if args is not None and len(args) == 4:
                a, b, c, z = (inner(x) for x in args)
                out.append(f"hypergeometric([{a},{b}],[{c}],{z})")
                counts["hypergeometric(2F1)"] = counts.get("hypergeometric(2F1)", 0) + 1
                i = k
                continue
        elif m is ml:
            args, k = _call_args(text, j)
            if args is not None and len(args) == 2:
                a, b = (inner(x) for x in args)
                out.append(f"li[{a}]({b})")
                counts["li["] = counts.get("li[", 0) + 1
                i = k
                continue
        else:
            args, k = _call_args(text, j)
            if args is not None and len(args) == 2:
                a, b = (inner(x) for x in args)
                out.append(f"psi[{a}]({b})")
                counts["psi["] = counts.get("psi[", 0) + 1
                i = k
                continue
        out.append(m.group(0))
        i = m.end()
    return "".join(out), counts


def normalize_heads(text):
    text, counts = rewrite_structural(text)
    stats = dict(counts)
    for rx, rep in HEAD_REWRITES:
        if callable(rep):
            hits = []
            text = rx.sub(lambda m: hits.append(rep(m)) or hits[-1], text)
            for h in hits:
                if h in rep.labels.values():
                    stats[h] = stats.get(h, 0) + 1
        else:
            text, n = rx.subn(rep, text)
            if n:
                stats[rep] = stats.get(rep, 0) + n
    if stats:
        with REWRITE_LOCK:
            for k, v in stats.items():
                REWRITE_STATS[k] = REWRITE_STATS.get(k, 0) + v
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
# MR_RULES_CORE_PATH=<core> pins a core built elsewhere (an A/B against a
# pinned worktree's core — replaces the hand-edited driver copies of the
# class-3 deferred campaign): its stamp is <core>.stamp, the fingerprint
# check against THIS tree's rules is skipped (the pinned core is
# deliberately different), and a missing pinned core is fatal — never
# rebuilt, never bypassed by the standard load path (guarded by
# test/test_driver_core_pin.py).
RULES_CORE_PIN = os.environ.get("MR_RULES_CORE_PATH") or None
RULES_CORE = (os.path.abspath(RULES_CORE_PIN) if RULES_CORE_PIN
              else os.path.join(ROOT, "test", "mr_rules.core"))
RULES_CORE_STAMP = RULES_CORE + ".stamp"
SBCL = os.environ.get("MR_SBCL") or subprocess.run(
    ["sh", "-c", "command -v sbcl"], capture_output=True, text=True
).stdout.strip() or None

USAGE = """usage: corpus_driver.py [FILTER [PER_FILE [TIMEOUT [SUITE_DIR
                        [START_INDEX [APPEND [SKIP_FIRST [OUT_FILE
                        [STOP_INDEX [SHARD_FILE]]]]]]]]]]

Ten positionals, no options. FILTER is a path substring selecting suite
files (default the whole class-1 section); SUITE_DIR is REQUIRED for any
non-class-1 section, or file_list() bounds the walk to class 1 and
silently resolves 0 files; APPEND is the literal word `append`.

Without OUT_FILE the record goes to test/corpus_driver.scratch.out (and
its .caps sidecar), which is gitignored: a committed record can only be
written by naming it. See .scratch/corpus-harness/issues/02.
"""

# A dash-led first argument is never a FILTER. Before this guard the
# reflex `corpus_driver.py --help` ran a 0-file corpus run and wrote its
# stub over a committed record (.scratch/corpus-harness/issues/02, hit 1).
if len(sys.argv) > 1 and sys.argv[1].startswith("-"):
    sys.stderr.write(USAGE)
    sys.exit(2)

FILTER = sys.argv[1] if len(sys.argv) > 1 else SECTION + "/"
PER_FILE = int(sys.argv[2]) if len(sys.argv) > 2 else 5
TIMEOUT = int(sys.argv[3]) if len(sys.argv) > 3 else 30
SUITE_DIR = sys.argv[4] if len(sys.argv) > 4 else SUITE
START_INDEX = int(sys.argv[5]) if len(sys.argv) > 5 else 0
APPEND = len(sys.argv) > 6 and sys.argv[6] == "append"
SKIP_FIRST = int(sys.argv[7]) if len(sys.argv) > 7 else 0
OUT_FILE = sys.argv[8] if len(sys.argv) > 8 else None
# Where a run with no OUT_FILE writes. Gitignored and untracked, so an
# exploratory slice cannot destroy a committed record — it used to default
# to test/corpus_class1_driver.out, which it destroyed three times
# (.scratch/corpus-harness/issues/02). Guarded by
# test/test_driver_out_default.py.
DEFAULT_OUT_FILE = os.path.join(ROOT, "test", "corpus_driver.scratch.out")
STOP_INDEX = int(sys.argv[9]) if len(sys.argv) > 9 else None
SHARD_FILE = sys.argv[10] if len(sys.argv) > 10 else None

KNOWN_CLASSES = {
    "expected", "verified", "unverified", "contains-noun",
    "no-answer", "deferred", "unexpected", "error", "timeout",
}
PASS_CLASSES = {"expected", "verified", "no-answer"}

# The inert-head leak guard (inert-trig substrate design 3.1 invariant, 3.4;
# Task 10). The bridge rule (4.1.0.1 r1) deactivates a trig integrand into
# these six heads, and a section-4 rule must activate them again before it
# answers. An answer still carrying one is a PACKAGE DEFECT: diff() cannot
# see through an inert head, so the entry would otherwise sink silently into
# deferred / contains-noun / unverified. It is classified `error` -- a class
# the mergers already know; a new class would break their agreement with
# KNOWN_CLASSES -- and run_entry names the heads on stderr. The test runs
# FIRST, before the noun and zero-chain tests. Guarded by
# test/test_driver_inert_leak.py.
INERT_HEADS = ("%mr_isin", "%mr_icos", "%mr_itan",
               "%mr_icot", "%mr_isec", "%mr_icsc")
INERT_LEAK_TAG = "INERT-LEAK"


def inert_leak_heads(out):
    """The inert heads an entry run's output reports leaked (the Maxima text
    prints `INERT-LEAK <heads>` beside its `CLASS error` line); [] if none."""
    for line in out.splitlines():
        line = line.strip()
        if line.startswith(INERT_LEAK_TAG + " "):
            return [h for h in line[len(INERT_LEAK_TAG):].split()
                    if h in INERT_HEADS]
    return []


def _core_fingerprint_files():
    """The files test/build_rules_core.sh bakes into the image, as sorted
    RELATIVE paths: loader + utils + dispatch lisp + matcher lisp +
    converter lisp + every rules/*/*.mac (all rule classes AND rules/utils,
    whose inert-trig rewrite tables mr_load_all also loads). One general
    glob, not a per-class list: a new rules/ subdirectory is covered the
    day it appears, and a superset can only make a core look stale (a
    rebuild), never a stale core look fresh."""
    import glob
    # Canonical order: sorted RELATIVE paths (must match
    # test/build_rules_core.sh's C-locale sort exactly — an order difference
    # makes every freshly built core look stale, measured 2026-08-26).
    # Guarded by test/test_driver_core_pin.py (the two fingerprints agree).
    return sorted(["maxima_rubi.mac", "maxima_rubi_utils.mac",
                   "maxima_rubi_dispatch.lisp",
                   "maxima_rubi_match.lisp",
                   "maxima_rubi_tree.lisp"] +
                  [os.path.relpath(p, ROOT) for p in
                   glob.glob(os.path.join(ROOT, "rules", "*", "*.mac"))])


def _core_fingerprint():
    """md5 over _core_fingerprint_files(), concatenated in that order."""
    import hashlib
    rels = _core_fingerprint_files()
    h = hashlib.md5()
    for rel in rels:
        with open(os.path.join(ROOT, rel), "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()


def rules_core_state():
    """'off' | 'on' | 'stale' | 'missing' | 'pinned' for the core vs
    current rules."""
    if os.environ.get("MR_RULES_CORE", "1") == "0":
        return "off"
    if not (os.path.exists(RULES_CORE) and os.path.exists(RULES_CORE_STAMP)):
        return "missing"
    if RULES_CORE_PIN:
        return "pinned"
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
    if RULES_CORE_PIN:
        if st != "pinned":
            raise SystemExit(f"MR_RULES_CORE_PATH={RULES_CORE_PIN}: core is "
                             f"{st} (a pinned core needs the image and its "
                             ".stamp; it is never built or bypassed)")
        return True
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


# The matcher substrate switches (spec section 3.6): the arm this process
# runs, from MR_SWITCHES (test/run_records.py), assigned at the head of
# every entry text and stated on the record's filter: line.
_rr_spec = importlib.util.spec_from_file_location(
    "run_records", os.path.join(ROOT, "test", "run_records.py"))
run_records = importlib.util.module_from_spec(_rr_spec)
_rr_spec.loader.exec_module(run_records)
try:
    SWITCH_SETTINGS = run_records.switch_settings(os.environ)
except ValueError as exc:
    raise SystemExit(str(exc))


def switch_header():
    """Suffix for the record's `filter:` line: the switch arm."""
    return "  switches: " + run_records.switches_text(SWITCH_SETTINGS)


def zc_header():
    """Suffix for the record's `filter:` line when the zero chain's
    radcan(rat()) fallback is OFF. Empty in every normal run, so a normal
    record's header is byte-identical to before this switch existed."""
    return "" if ZC_FALLBACK else "  zc-fallback: off"


def verify_header():
    """Suffix for the record's `filter:` line: the verification budget. A
    record without it predates the budget (and the symbolic-first checker)."""
    return f"  verify: {VERIFY_CAP}s {CAP_KIND}, stage {STAGE_CAP:g}s"


def core_header():
    """Suffix for the record's `filter:` header line: names a pinned core
    (the shard merge accepts any `filter:` line), empty otherwise."""
    return f"  core: pinned {RULES_CORE}" if RULES_CORE_PIN else ""


USE_RULES_CORE = ensure_rules_core()

workdir = tempfile.mkdtemp(prefix="maxima-rubi-corpus-")
mac_file = os.path.join(workdir, "i.mac")


# The per-entry cap: CPU seconds (the default) or wall seconds.
#
# A WALL cap measures the machine as much as the code. MEASURED 2026-09-17/18:
# the class-1 run launched 33 processes on 24 vCPUs, so early entries ran
# contended and late ones ran alone and an entry's verdict depended on WHEN it
# was scheduled; and 2 Exponentials e527/e528, at 26.8/26.9 s against the 30 s
# wall cap, verify at 12 workers and time out at 24 on identical code. A CPU
# cap counts the seconds the entry's process actually consumed, so the same
# entry gets the same budget whatever else is running, and a record becomes
# reproducible across machines and worker counts.
#
# MR_CAP_KIND=wall restores the old behaviour, which is how a pre-2026-09-18
# record is reproduced on its own terms. The two are NOT comparable: a
# contended entry does more work inside 30 CPU-seconds than inside 30 wall-
# seconds, so records state the kind on their filter: line and any A/B must
# hold it fixed.
CAP_KIND = os.environ.get("MR_CAP_KIND", "cpu")
# MR_ZC_FALLBACK=0 drops the zero chain's radcan(rat()) fallback stage for the
# whole run. It exists for ONE measurement — the fallback-off arm that answers
# "does the fallback still rescue anything" by A/B against a normal record
# (probes/maxima/probe-radcan-fallback-live). It is NOT a tuning knob: a record
# taken with it is not comparable to one taken without, exactly as a cpu record
# is not comparable to a wall one, which is why the header states it (below).
ZC_FALLBACK = os.environ.get("MR_ZC_FALLBACK", "1") != "0"
# Verification's own budget (user decision 2026-09-28,
# .scratch/corpus-harness/issues/06). rubi keeps TIMEOUT; the checker gets
# VERIFY_CAP more on top, so the process cap is TIMEOUT + VERIFY_CAP, and
# the entry's ANSWERED line says how much of it rubi used: rubi over TIMEOUT
# is a timeout even when it answered, and a process killed after ANSWERED
# was killed while verifying (classify_entry). STAGE_CAP bounds each checker
# stage (test/mr_verify.mac mr_stage_cap), so one runaway stage cannot eat
# the whole verification budget. Both are CPU seconds under a cpu cap.
VERIFY_CAP = int(os.environ.get("MR_VERIFY_CAP", "30"))
STAGE_CAP = float(os.environ.get("MR_STAGE_CAP", "5"))
if CAP_KIND not in ("cpu", "wall"):
    raise SystemExit(f"corpus_driver: MR_CAP_KIND must be cpu or wall, not {CAP_KIND!r}")


# test/mr_cpu_cap.py enforces the per-entry CPU budget and reports the CPU
# used. Its exit code when it stopped the child for going over:
CPU_CAP_HELPER = os.path.join(ROOT, "test", "mr_cpu_cap.py")
CPU_CAP_RC = 200


def _cpu_limited(cmd, cap, cpu_path):
    """CMD under a CPU budget of CAP seconds, writing its CPU to CPU_PATH.

    The enforcement lives in test/mr_cpu_cap.py — read its docstring for why
    this is NOT `ulimit -t`: RLIMIT_CPU signals SIGXCPU, whose default action
    dumps core, and on this host `ulimit -c 0` cannot stop that because
    core_pattern pipes to systemd-coredump and the kernel ignores RLIMIT_CORE
    for a piped dump. A cap hit is a normal outcome here, thousands per run.

    The helper forks, so the group holds two processes; maxima_run starts the
    group with start_new_session and the wall backstop kills the GROUP."""
    return [sys.executable, CPU_CAP_HELPER, str(cap), cpu_path] + cmd


def _read_cpu(path):
    """The CPU seconds test/mr_cpu_cap.py recorded, or None."""
    try:
        with open(path, encoding="utf-8") as fh:
            return float(fh.read().strip())
    except (OSError, ValueError):
        return None


def maxima_run(mac_text, timeout, cpu_out=None):
    """Run MAC_TEXT in a fresh Maxima at the per-entry cap: (output, hit_cap).

    hit_cap is True when the entry used up its budget, whichever cap kind is in
    force, so classify_output reads it as `timeout` either way. CPU_OUT, when a
    list is passed, receives the entry's CPU seconds under a CPU cap (an
    optional out-parameter so the committed probes that unpack the pair keep
    working)."""
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
        # stdin from /dev/null: a fatal SBCL error (control-stack
        # exhaustion inside mr-match:match, probes/matcher/07) drops into
        # the ldb monitor, which reads stdin — an inherited open stdin
        # holds the process to the cap and the entry reads `timeout`;
        # with /dev/null ldb exits and the entry reads `error`. The batch
        # answers its prompts from the batch file
        # (batch_answers_from_file), never from stdin.
        # Under a CPU cap the wall timeout stays as a BACKSTOP only: a
        # process blocked on something rather than computing burns no CPU and
        # would otherwise never hit its limit.
        cpu_path = fpath + ".times"
        if CAP_KIND == "cpu":
            cmd = _cpu_limited(cmd, timeout, cpu_path)
            wall = max(4 * timeout, 120)
        else:
            wall = timeout
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, cwd=ROOT, start_new_session=True,
        )
        try:
            out, _err = proc.communicate(timeout=wall)
            hit_cap = CAP_KIND == "cpu" and proc.returncode == CPU_CAP_RC
        except subprocess.TimeoutExpired:
            # The wall backstop. Kill the GROUP: under a CPU cap the direct
            # child is the shell, and killing it alone would orphan Maxima.
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                proc.kill()
            out, _err = proc.communicate()
            hit_cap = True
        if cpu_out is not None:
            cpu_out.append(_read_cpu(cpu_path) if CAP_KIND == "cpu" else None)
        try:
            os.unlink(cpu_path)
        except OSError:
            pass
        return out or "", hit_cap
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


def zero_chain(d_expr, var, fallback=True):
    """Statement list whose value is 1 iff the checker proves D_EXPR zero,
    symbolically or by the numeric check (test/mr_verify.mac mr_proof).

    The corpus run itself no longer calls this: build_text hands the whole
    verdict to mr_check_entry. It is kept, with its signature, for the
    committed probes that build their own zero tests from it.
    FALLBACK=False drops the rat-radcan stage (the MR_ZC_FALLBACK arm).

    The stage list, the numeric check and their measured history (the
    two chain orders, the elliptic gate, the numeric parameter values,
    the errcatch-per-stage lesson) live in test/mr_verify.mac since
    .scratch/corpus-harness/issues/06; git history has the previous
    string-built chain."""
    stages = "mr_proof_stages" if fallback \
        else 'delete("rat-radcan", mr_proof_stages)'
    return ("block([MR_zd, MR_zt], "
            "(if mr_verify_loaded # true then load(\"test/mr_verify.mac\")), "
            "MR_zd : errcatch(" + d_expr + "), "
            "if MR_zd = [] then 0 else ("
            "MR_zt : mr_proof(part(MR_zd, 1), " + var + ", " + stages + "), "
            "if substring(MR_zt, 1, 5) = \"none\" then 0 else 1))")


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
    # CannotIntegrate marker (port: the `unintegrable` noun —
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
    # The inert-head leak test (INERT_HEADS above): first, in both
    # branches. freeof on an operator symbol tests whether that operator
    # occurs (freeof(%mr_isin, %mr_isin(x)) is false).
    heads = ", ".join(INERT_HEADS)
    leak = (f"if not apply(freeof, [{heads}, mr_r]) then ("
            "disp(concat(\"CLASS error\")), "
            f"disp(concat(\"{INERT_LEAK_TAG}\", "
            f"apply(concat, map(lambda([MR_h], concat(\" \", string(MR_h))), "
            f"sublist([{heads}], lambda([MR_h], not freeof(MR_h, mr_r)))))))) "
            "else ")
    # Every switch is assigned at the head of the entry text, and the
    # depth-cap counter is reset with them, so the DEPTHCAP line below
    # counts this entry's cap hits only (exact seen test design 3.3).
    switches = "".join(f"{name} : {value}$\n"
                       for name, value in SWITCH_SETTINGS.items())
    # ANSWERED <cpu> is rubi's own CPU, printed and flushed once it has
    # returned and before the checker is even loaded: the process cap is
    # TIMEOUT + VERIFY_CAP, and a process killed after this line was killed
    # while VERIFYING, which is not a rubi timeout (classify_entry). It comes
    # after the queued prompt answers, which must directly follow the call
    # whose sign questions they answer.
    head = (switches + "mr_depth_cap_hits : 0$\n"
            + f"mr_f: {f_text}$\n"
            + "mr_t0 : elapsed_run_time()$\n"
            f"mr_r: {call}$\n"
            + "pos$\n" * 40 + "no$\n" * 20
            + 'printf(true, "ANSWERED ~,3f~%", elapsed_run_time() - mr_t0)$\n'
            + "?finish\\-output()$\n"
            + 'load("test/mr_verify.mac")$\n'
            + f"mr_stage_cap : {STAGE_CAP}$\n"
            + ("" if ZC_FALLBACK
               else 'mr_proof_stages : delete("rat-radcan", mr_proof_stages)$\n'))
    if e_text.startswith(("Unintegrable", "CannotIntegrate")):
        # Interior-marker check FIRST (the other branch's has_noun): the
        # top-level noun detector only sees op(mr_r), so a partial
        # reduction whose interior carries the `unintegrable` catch-all
        # marker is NOT a top-level noun and would misclassify `unexpected`
        # — it is contains-noun (measured 2026-08-27: 1.1.2.5 e103/e107/
        # e110, the pinned Rubi's r30 p<0,q>0 reduction whose nested
        # integrals fall to the file catch-all; their zero chains cannot
        # close because the markers' integrands survive diff).
        body = (leak + f"if is({noun} = 1) then disp(concat(\"CLASS no-answer\")) "
                f"else if is({has_noun}) then disp(concat(\"CLASS contains-noun\")) "
                f"else disp(concat(\"CLASS unexpected\"))")
    else:
        # The verdict is test/mr_verify.mac's mr_check_entry: symbolic proof
        # of the self-diff, then of each expected-diff, and only then the
        # numeric check (user decision 2026-09-28: symbolic first). It prints
        # the NUMERIC lines, CLASS and PROOF. The corpus answers are passed
        # as list elements -- each is its own expression, so a
        # SUM-valued answer can no longer lose the sign of its later terms
        # the way the inlined `mr_r - <e>` did (1.3.2 e1, 2026-08-24;
        # test/test_driver_parens.py).
        # Each answer is simplified inside its own errcatch: a corpus answer
        # can fail to simplify (4.2.7 e80: `expt: undefined: 0 to a negative
        # exponent'), which the old inlined chain caught and which must not
        # take the entry down; mr_check_entry skips an [] element.
        es = (f"[errcatch({e_text})"
              + (f", errcatch({e_text2})" if e_text2 is not None else "") + "]")
        body = (leak + f"if is({noun} = 1) then disp(concat(\"CLASS deferred\")) "
                f"else if is({has_noun}) then disp(concat(\"CLASS contains-noun\")) "
                f"else mr_check_entry(mr_r, mr_f, {var_text}, {es})")
    # This entry's depth-cap count, printed AFTER the CLASS line (the
    # driver's CLASS scan takes the first match, so the order is
    # classification-safe) and before the trailing queued answers. The
    # entry loop parses it into the shard's .caps sidecar, which
    # test/merge_caps.py merges into the run's census (exact seen test
    # design 3.3).
    depthcap = 'disp(concat("DEPTHCAP ", string(mr_depth_cap_hits)))'
    return (head + body + "$\n" + depthcap + "$\n"
            + "pos$\n" * 40 + "no$\n" * 20)


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


def build_info_lines():
    """The record header's `maxima:` lines (build_info of the installed maxima)."""
    r = subprocess.run(
        ["maxima", "--very-quiet", "--batch-string", "disp(build_info());"],
        capture_output=True, text=True, timeout=120, cwd=ROOT,
        stdin=subprocess.DEVNULL,
    )
    return [f"maxima: {line.strip()}" for line in r.stdout.splitlines()
            if line.strip().startswith(("Maxima", "Lisp ", "Host "))]


def header_lines(title, detail, build_lines):
    """A record's header: TITLE, the date, BUILD_LINES, the filter: line
    (DETAIL, the switch arm, a pinned core) and a blank line."""
    return ([title,
             f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"]
            + list(build_lines)
            + [f"filter: {FILTER!r}  {detail}" + switch_header()
               + core_header() + zc_header() + verify_header(), ""])


class EntryResult:
    """What one entry's output states: CLS, CAPS (depth-cap hits), PROOF (the
    checker's tag, None when the entry never reached the checker) and
    RUBI_CPU (the ANSWERED seconds, None when rubi never returned)."""
    __slots__ = ("cls", "caps", "proof", "rubi_cpu")

    def __init__(self, cls, caps, proof, rubi_cpu):
        self.cls, self.caps, self.proof, self.rubi_cpu = cls, caps, proof, rubi_cpu


def classify_entry(out, timed_out):
    """Read an entry run's output (see build_text / test/mr_verify.mac).

    - no ANSWERED line: rubi never returned -- `timeout` if the process hit
      its cap, `error` otherwise;
    - ANSWERED above TIMEOUT: `timeout` -- rubi overran its own budget, even
      though the verification budget let it finish;
    - a CLASS line: that class, with its PROOF tag;
    - killed after ANSWERED with no CLASS line: killed while verifying. The
      NUMERIC lines printed so far decide it the way mr_check_entry would
      have had the symbolic stages all failed: self-diff ok -> `verified`,
      an expected-diff ok -> `expected`, else `unverified`; the tag ends
      `/verify-timeout`."""
    cls = proof = rubi_cpu = None
    caps = 0
    numeric = []
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("ANSWERED ") and rubi_cpu is None:
            try:
                rubi_cpu = float(line[9:].strip())
            except ValueError:
                pass
        elif line.startswith("NUMERIC "):
            parts = line.split()
            if len(parts) == 3:
                numeric.append((parts[1], parts[2]))
        elif cls is None and line.startswith("CLASS "):
            cls = line[6:].strip()
        elif line.startswith("PROOF ") and proof is None:
            proof = line[6:].strip()
        elif line.startswith("DEPTHCAP "):
            try:
                caps = int(line[9:].strip())
            except ValueError:
                caps = 0
    if rubi_cpu is None:
        return EntryResult("timeout" if timed_out else "error", caps, None, None)
    if rubi_cpu > TIMEOUT:
        return EntryResult("timeout", caps, None, rubi_cpu)
    if cls is None and timed_out:
        verified = [o for w, o in numeric if w == "verified"]
        expected = [o for w, o in numeric if w == "expected"]
        if "ok" in verified:
            cls, proof = "verified", "numeric/verify-timeout"
        elif "ok" in expected:
            cls, proof = "expected", "numeric/verify-timeout"
        else:
            cls = "unverified"
            proof = (f"none/numeric-{verified[0]}/verify-timeout" if verified
                     else "none/verify-timeout")
        return EntryResult(cls, caps, proof, rubi_cpu)
    if cls is None or cls not in KNOWN_CLASSES:
        return EntryResult("error", caps, None, rubi_cpu)
    return EntryResult(cls, caps, proof, rubi_cpu)


def classify_output(out, timed_out):
    """(class, depth-cap hits) an entry run's output states -- the committed
    probes' view of classify_entry."""
    r = classify_entry(out, timed_out)
    return r.cls, r.caps


def run_entry_full(rel, idx, entry_text, line_no):
    """One corpus entry (ENTRY_TEXT as extract_entries returns it, IDX
    0-based) through a fresh Maxima subprocess at the TIMEOUT + VERIFY_CAP
    process cap: (class, result line, depth-cap hits, proof tag or None).
    main() and test/run_corpus_queue.py both call it, so the two paths
    cannot drift."""
    els = split_elements(entry_text[1:-1])
    label = f"{rel} e{idx + 1} L{line_no}"
    if len(els) not in (4, 5):
        return ("error", f"{'error':14s} t=0.0s {label} bad-entry-shape({len(els)})",
                0, None)
    f_text = normalize_heads(els[0])
    var_text = els[1]
    e_text = normalize_heads(els[3])
    e_text2 = normalize_heads(els[4]) if len(els) == 5 else None
    t_start = time.time()
    cpu_out = []
    out, timed_out = maxima_run(
        build_text(f_text, var_text, e_text, e_text2), TIMEOUT + VERIFY_CAP, cpu_out)
    # The record's t= is RUBI's CPU seconds (the ANSWERED line) -- the
    # quantity the TIMEOUT cap bounds since verification got its own budget.
    # Without an ANSWERED line it is the process's CPU seconds (under a CPU
    # cap), or its wall (a wall-backstop kill leaves no `times` dump).
    dt = time.time() - t_start
    if cpu_out and cpu_out[0] is not None:
        dt = cpu_out[0]
    r = classify_entry(out, timed_out)
    if r.rubi_cpu is not None:
        dt = r.rubi_cpu
    if r.cls == "error":
        leaked = inert_leak_heads(out)
        if leaked:
            sys.stderr.write(f"inert-leak {label}: the answer carries "
                             f"{', '.join(leaked)} (classified error)\n")
    return r.cls, f"{r.cls:14s} t={dt:6.1f}s {label}", r.caps, r.proof


def run_entry(rel, idx, entry_text, line_no):
    """run_entry_full without the proof tag: (class, result line, depth-cap
    hits), the shape the committed probes unpack."""
    cls, line, caps, _proof = run_entry_full(rel, idx, entry_text, line_no)
    return cls, line, caps


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

    out_lines = header_lines(
        (f"=== maxima-rubi corpus driver (filter {FILTER!r}, "
         f"resume at file index {START_INDEX}) ==="
         if APPEND else
         f"=== maxima-rubi corpus driver (filter {FILTER!r}) ==="),
        f"per-file: {PER_FILE}  timeout: {TIMEOUT}s {CAP_KIND}  files: {len(files)}"
        + (f"  shard: {SHARD_FILE}" if SHARD_FILE else ""),
        [] if APPEND else build_info_lines())

    counts = {}
    t0 = time.time()
    out_path = OUT_FILE or DEFAULT_OUT_FILE
    # The depth-cap sidecar sits next to this process's .out and takes one
    # `<hits> <label>` line per entry that hit the cap; test/merge_caps.py
    # merges a run's sidecars into its census, and run_records.
    # clear_stale_shards deletes them with the other shard files (exact
    # seen test design 3.3).
    caps_path = os.path.splitext(out_path)[0] + ".caps"
    outf = open(out_path, "a" if APPEND else "w", encoding="utf-8")
    capsf = open(caps_path, "a" if APPEND else "w", encoding="utf-8")
    # The checker's proof sidecar: one `<tag> <label>` line per entry that
    # reached the checker (.scratch/corpus-harness/issues/06).
    proofs_path = os.path.splitext(out_path)[0] + ".proof"
    prooff = open(proofs_path, "a" if APPEND else "w", encoding="utf-8")
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
            cls, line, caps, proof = run_entry_full(rel, idx, entries[idx],
                                                    line_nos[idx])
            if caps > 0:
                capsf.write(f"{caps} {rel} e{idx + 1} L{line_nos[idx]}\n")
                capsf.flush()
            if proof is not None:
                prooff.write(f"{proof} {rel} e{idx + 1} L{line_nos[idx]}\n")
                prooff.flush()
            counts[cls] = counts.get(cls, 0) + 1
            out_lines.append(line)
            outf.write(line + "\n")
            outf.flush()
            print(f"{'PASS' if cls in PASS_CLASSES else 'FAIL'}: {line}")
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
    capsf.close()
    prooff.close()
    print("\n".join(out_lines[-8:]) + "\n")


if __name__ == "__main__":
    main()
