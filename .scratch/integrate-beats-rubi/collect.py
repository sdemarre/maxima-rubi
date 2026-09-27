#!/usr/bin/env python3
"""The corpus entries native `integrate` PASSES and `rubi` FAILS, one list
grouped by class and then by rubi's failure class, with the integrand.

    python3 .scratch/integrate-beats-rubi/collect.py [CLASS ...] > .scratch/integrate-beats-rubi/list.md

Per class N it compares test/corpus_classN.baseline.out (the native-integrate
baseline) with test/corpus_classN.out (the current rubi record) through
test/ab_records.py, so PASS/FAIL is the driver's own mapping. Default classes:
every N that has both records.
"""

import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "test"))
import ab_records  # noqa: E402

SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")


def corpus_lines(record):
    """{(relpath, entry): corpus line number} from RECORD's result lines."""
    out = {}
    with open(record, encoding="utf-8") as fh:
        for line in fh:
            m = ab_records.RESULT.match(line.rstrip("\n"))
            if m:
                out[(m.group(3), int(m.group(4)))] = int(m.group(5))
    return out


def integrand(rel, lineno, cache={}):
    """The first element of the corpus entry [integrand, x, steps, answer]."""
    if rel not in cache:
        with open(os.path.join(SUITE, rel), encoding="utf-8") as fh:
            cache[rel] = fh.read().split("\n")
    text = cache[rel][lineno - 1].strip()
    if text.startswith("["):
        text = text[1:]
    depth = 0
    for i, c in enumerate(text):
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == "," and depth == 0:
            return text[:i]
    return text


def main(argv):
    classes = argv or [n for n in "12345678"
                       if os.path.exists(os.path.join(ROOT, "test", f"corpus_class{n}.baseline.out"))
                       and os.path.exists(os.path.join(ROOT, "test", f"corpus_class{n}.out"))]
    passes = ab_records.driver_pass_classes()
    sections, total = [], 0
    for n in classes:
        base_p = os.path.join(ROOT, "test", f"corpus_class{n}.baseline.out")
        new_p = os.path.join(ROOT, "test", f"corpus_class{n}.out")
        res = ab_records.compare(ab_records.load_record(base_p),
                                 ab_records.load_record(new_p), passes)
        lines = corpus_lines(new_p)
        groups = defaultdict(list)
        for key, a, b in res["pass_fail"]:
            groups[b[0]].append((key, a, b))
        total += len(res["pass_fail"])
        sections.append((n, res["pass_fail"], groups, lines))

    print("# Entries native integrate passes and rubi fails\n")
    print(f"{total} entries over classes {', '.join(classes)}. Baseline "
          "`test/corpus_classN.baseline.out` (native integrate, 30 s wall cap) "
          "against `test/corpus_classN.out` (rubi, 30 s cpu cap), compared with "
          "`test/ab_records.py`. Regenerate with "
          "`python3 .scratch/integrate-beats-rubi/collect.py > .scratch/integrate-beats-rubi/list.md`.\n")
    print("| class | entries | rubi failure classes |")
    print("|---|---|---|")
    for n, rows, groups, _ in sections:
        counts = ", ".join(f"{k} {len(v)}" for k, v in
                           sorted(groups.items(), key=lambda kv: -len(kv[1])))
        print(f"| {n} | {len(rows)} | {counts} |")
    for n, rows, groups, lines in sections:
        print(f"\n## Class {n} ({len(rows)})")
        for cls, items in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            print(f"\n### rubi {cls} ({len(items)})\n")
            print("| file | entry | integrate | rubi | integrand |")
            print("|---|---|---|---|---|")
            for (rel, e), a, b in items:
                f = rel.split("/")[-1].removesuffix(".mac")
                ln = lines.get((rel, e))
                itg = integrand(rel, ln).replace("|", "\\|") if ln else "?"
                print(f"| {f} | e{e} | {a[0]} {a[1]:.1f}s | {b[1]:.1f}s | `{itg}` |")


if __name__ == "__main__":
    main(sys.argv[1:])
