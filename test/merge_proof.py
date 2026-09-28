#!/usr/bin/env python3
"""Merge a run's per-shard proof sidecars into one census file (the
checker's tags, .scratch/corpus-harness/issues/06).

The driver writes one line

    <tag> <relpath> e<entry> L<line>

per entry that reached the checker (test/mr_verify.mac mr_check_entry) into
the shard's .proof file next to its .out. A tag is the symbolic stage that
proved the entry (`radcan`, `chainA.1`, ...), `numeric` when only the
numeric check closed it, or `none/numeric-<outcome>` when nothing did; any of
them may carry `/timeout:<stages>` or `/verify-timeout`.

The census must be COMPLETE against the merged record: exactly its verified,
expected and unverified entries carry a tag. A checked entry without one, a
tag on an entry of another class, or a label the record lacks is refused --
the census would otherwise describe a run that never happened (the
test/merge_caps.py rule).

Usage:
  merge_proof.py RECORD OUT [SHARD-GLOB]

    RECORD      the merged record this census belongs to
    OUT         the census file to write
    SHARD-GLOB  the sidecars, relative to test/ or absolute
                (default: corpus_<slug>.shard*.proof)
"""

import glob
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)$")
PROOF = re.compile(r"^(\S+)\s+(.*) e(\d+) L(\d+)$")
CHECKED = ("verified", "expected", "unverified")


def kind(tag):
    """symbolic | numeric | none."""
    if tag.startswith("none"):
        return "none"
    if tag.startswith("numeric"):
        return "numeric"
    return "symbolic"


def main(argv):
    if len(argv) not in (2, 3):
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 64
    record, out = argv[0], argv[1]
    slug = os.path.basename(record).split(".")[0].replace("corpus_", "")
    pattern = argv[2] if len(argv) > 2 else f"corpus_{slug}.shard*.proof"

    cls_of = {}
    order = []
    verify = None
    for line in open(record, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("filter:"):
            m = re.search(r"\bverify: ([^ ]+ \w+, stage [\d.]+s)", line)
            verify = m.group(1) if m else None
        m = RESULT.match(line)
        if m:
            key = (m.group(3), int(m.group(4)))
            cls_of[key] = m.group(1)
            order.append(key)
    if not order:
        raise SystemExit(f"merge_proof: no result lines in {record}")
    pos = {k: i for i, k in enumerate(order)}

    inputs = sorted(glob.glob(os.path.join(ROOT, "test", pattern)))
    if not inputs:
        raise SystemExit(f"merge_proof: no sidecars match {pattern}")
    tags = {}
    problems = []
    for path in inputs:
        for line in open(path, encoding="utf-8"):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            m = PROOF.match(line)
            if not m:
                raise SystemExit(f"merge_proof: bad line in {os.path.basename(path)}: {line!r}")
            key = (m.group(2), int(m.group(3)))
            if key not in cls_of:
                problems.append(f"not in {os.path.basename(record)}: {line}")
            elif cls_of[key] not in CHECKED:
                problems.append(f"not checked ({cls_of[key]}): {line}")
            elif key in tags:
                problems.append(f"duplicate: {line}")
            else:
                tags[key] = m.group(1)
    for key in order:
        if cls_of[key] in CHECKED and key not in tags:
            problems.append(f"missing a tag: {cls_of[key]} {key[0]} e{key[1]}")
    if problems:
        print(f"INCOMPLETE: {len(problems)} problems", file=sys.stderr)
        for p in problems[:20]:
            print(f"  {p}", file=sys.stderr)
        return 1

    by_class = {c: Counter() for c in CHECKED}
    stages = Counter()
    for key, tag in tags.items():
        by_class[cls_of[key]][kind(tag)] += 1
        if kind(tag) == "symbolic":
            stages[tag] += 1
    lines = [
        f"=== maxima-rubi {slug} proof census ({len(inputs)} sidecars merged) ===",
        f"merge date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"record: {record}",
        f"verify: {verify}",
    ]
    for c in CHECKED:
        n = by_class[c]
        lines.append(f"{c}: symbolic {n['symbolic']}  numeric {n['numeric']}  none {n['none']}")
    for st, n in sorted(stages.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"stage {st} {n}")
    lines.append("")
    for key in sorted(tags, key=lambda k: pos[k]):
        lines.append(f"{tags[key]} {key[0]} e{key[1]}")
    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"OK: {len(tags)} tags ({len(inputs)} sidecars)")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
