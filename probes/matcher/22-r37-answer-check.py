#!/usr/bin/env python3
"""probes/matcher/22-r37-answer-check.py -- are probe 21's two rubi(big)
answers CORRECT, and are they the same function?

Probe 21 measured that 04d95a9 changes rubi(big)'s answer: T0 (46dffa2)
returns a 44,862-character expression, T1/T2 a 22,636-character one.  Probe
21's `sig` is a ROUTE fingerprint (head + string length) and says nothing
about value -- two antiderivatives of one integrand may differ by a constant,
or only by algebraic form Maxima will not collapse unasked.

Three zero-tests, all through test/corpus_driver.zero_chain -- the harness's
own measured stage order (numeric two-point stage first, then factor-first
and ratsimp-first symbolic chains, then the elliptic-gated radcan(rat())
fallback), so this probe grades the answers by exactly the standard the
corpus records use:

  V0   diff(A0, x) - big == 0      is the T0 answer an antiderivative?
  V2   diff(A2, x) - big == 0      is the HEAD answer an antiderivative?
  EQ   diff(A0 - A2, x) == 0       do they differ by a constant only?

V0 and V2 both closing implies EQ; EQ is run anyway because it is the cheap
one and it separates "both right, different form" from "both wrong the same
way".  A chain that does not close is NOT a disproof -- it is `unverified`,
the corpus harness's own third verdict.

Usage (repo root), needs a worktree of 46dffa2 for A0:
  python3 probes/matcher/22-r37-answer-check.py --t0-tree <dir> \
      > probes/matcher/22-r37-answer-check.out 2>&1
"""
import argparse
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "test"))
# corpus_driver reads sys.argv AT IMPORT TIME (its FILTER / PER_FILE module
# globals), so this probe's own argv reaches it as a shard spec and dies with
# "invalid literal for int()".  Hide argv across the import.
_ARGV = sys.argv[:]
sys.argv = sys.argv[:1]
import corpus_driver  # noqa: E402
sys.argv = _ARGV

BIG = "x^2*(a+b*x)^3*(c+d*x)^4*(e+f*x)^5*(g+h*x)^6*log(x)"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def maxima(text, cwd, cap, work, tag):
    """Run one maxima batch; return its stdout."""
    path = os.path.join(work, tag + ".mac")
    with open(path, "w") as fh:
        fh.write(text)
    t0 = time.time()
    try:
        p = subprocess.run(["timeout", "-s", "KILL", str(cap),
                            "maxima", "--very-quiet", "-b", path],
                           cwd=cwd, stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True)
        out = p.stdout
    except Exception as exc:                       # pragma: no cover
        out = "R EXCEPTION %s" % exc
    print("CASE %s (tree %s) wall %.1f s" % (tag, cwd, time.time() - t0))
    for line in out.splitlines():
        if line.startswith("R "):
            print(line)
    sys.stdout.flush()
    return out


def answer_job(out_mac, name):
    """Compute rubi(big, x) and write it as a loadable `<name> : <expr>$`.

    printf ~a, not print: print wraps at linel and a 45,000-character
    answer would come back as fragments."""
    return (
        'display2d : false$\nlinel : 10000$\n'
        'load("maxima_rubi.mac")$\nmr_load_all()$\n'
        'big : %s$\n'
        'MR_t : elapsed_real_time()$\n'
        'MR_a : rubi(big, x)$\n'
        'print("R answer s", elapsed_real_time() - MR_t, "chars",'
        ' slength(string(MR_a)))$\n'
        'with_stdout("%s", printf(true, "%s : ~a$~%%", string(MR_a)))$\n'
        'print("R DONE")$\n' % (BIG, out_mac, name)
    )


def check_job(a0_mac, a2_mac):
    """The three zero-tests.  No rule files: this is Maxima only."""
    v0 = corpus_driver.zero_chain("diff(MR_A0, x) - big", "x")
    v2 = corpus_driver.zero_chain("diff(MR_A2, x) - big", "x")
    eq = corpus_driver.zero_chain("diff(MR_A0 - MR_A2, x)", "x")
    return (
        'display2d : false$\nlinel : 10000$\n'
        'big : %s$\n'
        'load("%s")$\nload("%s")$\n'
        'print("R chars A0", slength(string(MR_A0)), "A2", slength(string(MR_A2)))$\n'
        'MR_t : elapsed_real_time()$\n'
        'print("R V0 diff(A0,x)-big zero", %s, "s", elapsed_real_time() - MR_t)$\n'
        'MR_t : elapsed_real_time()$\n'
        'print("R V2 diff(A2,x)-big zero", %s, "s", elapsed_real_time() - MR_t)$\n'
        'MR_t : elapsed_real_time()$\n'
        'print("R EQ diff(A0-A2,x) zero", %s, "s", elapsed_real_time() - MR_t)$\n'
        'print("R DONE")$\n' % (BIG, a0_mac, a2_mac, v0, v2, eq)
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t0-tree", required=True,
                    help="a checkout of 46dffa2 (probe 21's T0)")
    ap.add_argument("--cap", type=int, default=1800)
    args = ap.parse_args()

    work = os.environ.get("TMPDIR", "/tmp") + "/mr-22-answer-check"
    subprocess.run(["rm", "-rf", work], check=False)
    os.makedirs(work)

    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                          stdout=subprocess.PIPE, text=True).stdout.strip()
    print("=== probes/matcher/22-r37-answer-check  git HEAD %s  %s"
          % (head, time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())))

    a0 = os.path.join(work, "a0.mac")
    a2 = os.path.join(work, "a2.mac")
    print("=== A0 = rubi(big, x) on T0 (46dffa2)")
    maxima(answer_job(a0, "MR_A0"), args.t0_tree, args.cap, work, "answer-t0")
    print("=== A2 = rubi(big, x) on HEAD")
    maxima(answer_job(a2, "MR_A2"), ROOT, args.cap, work, "answer-head")
    for p in (a0, a2):
        if not os.path.exists(p):
            print("R FAIL no answer file %s" % p)
            return 1
    print("=== zero-tests (test/corpus_driver.zero_chain)")
    maxima(check_job(a0, a2), ROOT, args.cap, work, "check")
    print("=== done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
