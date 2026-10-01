#!/usr/bin/env python3
"""Does test/mr_grade.lisp's mr_leaf_count reproduce Mathematica's LeafCount?

The reference (probes/leaf-size/01-scrape-reference.tsv) gives, for every
integral of the twelve independent test suites, the optimal antiderivative's
leaf size as Mathematica's LeafCount. The corpus holds the same optimal
antiderivatives in Maxima syntax (reference/maxima-syntax-test-suite/0
Independent test suites/), problem N of a report being entry eN of the file.
This probe evaluates each optimal in Maxima and counts its leaves in two arms:

  default  Maxima's default flags -- how the corpus driver evaluates it;
  mma      logexpand:false, radexpand:false -- the package's model flags,
           which keep log(u^2) and sqrt(x^2) as Mathematica writes them.

    python3 probes/leaf-size/02-leaf-count-vs-reference.py > probes/leaf-size/02-leaf-count-vs-reference.out

The story these measurements belong to: docs/grading-and-leaf-size.md.
"""

import collections
import importlib.util
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Problem N of a report is entry eN of the corpus file -- except in Welz: its
# report has 116 problems and the corpus file 93, and the two part ways after
# problem 57 (measured 2026-09-30: e1-e57 agree on the optimal text and, 5
# entries aside, on the leaf size; from e58 on the leaf sizes are a shifted
# sequence). Welz rows past 57 are left out.
ALIGNED_UPTO = {"11_Welz_Problems": 57}
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite", "0 Independent test suites")
TSV = os.path.join(ROOT, "probes", "leaf-size", "01-scrape-reference.tsv")

sys.argv = ["corpus_driver.py", "ZZ none ZZ", "1", "30"]
os.environ["MR_BASELINE"] = "1"
spec = importlib.util.spec_from_file_location("drv", os.path.join(ROOT, "test", "corpus_driver.py"))
drv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drv)


def maxima_leaves(exprs):
    """[(default, mma)] leaf counts of EXPRS, `err` where evaluation failed."""
    lines = ['load("test/mr_grade.lisp")$']
    for i, e in enumerate(exprs):
        for arm, flags in (("default", ""), ("mma", "logexpand:false, radexpand:false")):
            lines.append(f"block([errormsg:false, mr_v], mr_v: errcatch(block([{flags}], "
                         f"mr_leaf_count({e}))), print(\"LEAF\", {i}, \"{arm}\", "
                         f"if mr_v = [] then \"err\" else first(mr_v)))$")
    with tempfile.NamedTemporaryFile("w", suffix=".mac", delete=False) as fh:
        fh.write("\n".join(lines) + "\n")
    out = subprocess.run(["maxima", "--very-quiet", "-b", fh.name], capture_output=True,
                         text=True, stdin=subprocess.DEVNULL, cwd=ROOT, timeout=1800).stdout
    os.unlink(fh.name)
    res = collections.defaultdict(dict)
    for line in out.splitlines():
        m = re.match(r"^LEAF (\d+) (default|mma) (\S+)\s*$", line.strip())
        if m:
            res[int(m.group(1))][m.group(2)] = m.group(3)
    return [(res[i].get("default", "err"), res[i].get("mma", "err")) for i in range(len(exprs))]


def main():
    rows = [l.rstrip("\n").split("\t") for l in open(TSV, encoding="utf-8")][1:]
    by_suite = collections.defaultdict(list)
    for r in rows:
        by_suite[r[0]].append(r)
    print("=== mr_leaf_count against the reference's optimal leaf sizes ===")
    b = subprocess.run(["maxima", "--very-quiet", "--batch-string", "disp(build_info());"],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout
    print("\n".join("maxima: " + l.strip() for l in b.splitlines() if l.strip().startswith("Maxima")))
    total = collections.Counter()
    detail = []
    for suite, rs in by_suite.items():
        name = suite.split("_", 1)[1].replace("_", " ") + ".mac"
        entries, _ = drv.extract_entries(os.path.join(SUITE, name))
        exprs, keep = [], []
        for r in rs:
            n = int(r[1])
            if n > ALIGNED_UPTO.get(suite, n):
                total["unaligned"] += 1
                continue
            if n > len(entries):
                total["no-entry"] += 1
                continue
            els = drv.split_elements(entries[n - 1][1:-1])
            opt = els[3] if len(els) >= 4 else ""
            if opt.startswith(("Unintegrable", "CannotIntegrate")) or not opt:
                total["marker"] += 1
                continue
            exprs.append(drv.normalize_heads(opt))
            keep.append(r)
        got = maxima_leaves(exprs)
        c = collections.Counter()
        for r, (d, m) in zip(keep, got):
            ref = int(r[2])
            for arm, v in (("default", d), ("mma", m)):
                if v == "err":
                    c[arm + " err"] += 1
                    continue
                v = int(v)
                c[arm + " n"] += 1
                c[arm + " exact"] += v == ref
                c[arm + " within10"] += abs(v - ref) <= 0.1 * ref
                c[arm + " absdiff"] += abs(v - ref)
                c[arm + " refsum"] += ref
            detail.append(f"{suite} e{r[1]} ref={ref} default={d} mma={m}")
        total.update(c)
        print(f"{suite}: {len(keep)} optimals; " + "; ".join(
            f"{arm}: exact {c[arm + ' exact']}, within 10% {c[arm + ' within10']}, err {c[arm + ' err']}"
            for arm in ("default", "mma")))
    print()
    for arm in ("default", "mma"):
        n = total[arm + " n"]
        print(f"ALL {arm}: {n} counted, exact {total[arm + ' exact']} ({100 * total[arm + ' exact'] / n:.1f}%), "
              f"within 10% {total[arm + ' within10']} ({100 * total[arm + ' within10'] / n:.1f}%), "
              f"sum |diff| / sum ref {100 * total[arm + ' absdiff'] / total[arm + ' refsum']:.1f}%, "
              f"err {total[arm + ' err']}")
    print(f"skipped: marker optimal {total['marker']}, no corpus entry {total['no-entry']}, "
          f"past the aligned range {total['unaligned']}")
    print()
    print("\n".join(detail))


if __name__ == "__main__":
    main()
