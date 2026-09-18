#!/usr/bin/env python3
"""Merge a run's per-shard depth-cap sidecars into one census file (exact
seen test design
docs/superpowers/specs/2026-09-15-matcher-seen-test-intpart-design.md 3.3).

The driver writes one line

    <hits> <relpath> e<entry> L<line>

per entry whose dispatch hit the depth cap (mr_max_depth), into
test/corpus_<slug>.shard<kk>.caps next to that shard's .out. This script
concatenates them, in the record's canonical (file, entry) order, under a
header naming the run, the cap arm and the three figures the design asks
for: how many entries hit the cap, the total number of hits, and the
largest per-entry count.

Every label MUST be an entry of the merged record: a label that is not is
a sidecar from another run (or a stale shard), which would make the census
describe a run that never happened, so the merge refuses.

Usage:
  merge_caps.py RECORD OUT [SHARD-GLOB]

    RECORD      the merged record this census belongs to
                (test/corpus_class1.p5c-run1.out)
    OUT         the census file to write
                (test/corpus_class1.p5c-run1.caps)
    SHARD-GLOB  the sidecars, relative to test/
                (default: derived from RECORD's slug,
                 corpus_<slug>.shard*.caps)
"""

import glob
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)$")
CAPS = re.compile(r"^(\d+)\s+(.*) e(\d+) L(\d+)$")


def record_entries(path):
    """The (relpath, entry) keys of a merged record, in file order."""
    keys = []
    for line in open(path, encoding="utf-8"):
        m = RESULT.match(line.rstrip("\n"))
        if m:
            keys.append((m.group(3), int(m.group(4))))
    if not keys:
        raise SystemExit(f"merge_caps: no result lines in {path}")
    return keys


def record_switches_text(path):
    for line in open(path, encoding="utf-8"):
        if line.startswith("filter:"):
            m = re.search(r"\bswitches: (.*?)(?:\s\s|$)", line.rstrip("\n"))
            return m.group(1) if m else None
    return None


def main(argv):
    if len(argv) not in (2, 3):
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 64
    record, out = argv[0], argv[1]
    slug = os.path.basename(record).split(".")[0].replace("corpus_", "")
    pattern = argv[2] if len(argv) > 2 else f"corpus_{slug}.shard*.caps"

    keys = record_entries(record)
    order = {k: i for i, k in enumerate(keys)}
    inputs = sorted(glob.glob(os.path.join(ROOT, "test", pattern)))
    if not inputs:
        raise SystemExit(f"merge_caps: no sidecars match {pattern}")

    hits = {}
    unknown = []
    for path in inputs:
        for line in open(path, encoding="utf-8"):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            m = CAPS.match(line)
            if not m:
                raise SystemExit(f"merge_caps: bad line in "
                                 f"{os.path.basename(path)}: {line!r}")
            key = (m.group(2), int(m.group(3)))
            if key not in order:
                unknown.append((os.path.basename(path), line))
                continue
            hits[key] = hits.get(key, 0) + int(m.group(1))
    if unknown:
        print(f"INCOMPLETE: {len(unknown)} cap lines name an entry that is not "
              f"in {os.path.basename(record)}", file=sys.stderr)
        for name, line in unknown[:10]:
            print(f"  {name}: {line}", file=sys.stderr)
        return 1

    total = sum(hits.values())
    biggest = max(hits.values()) if hits else 0
    lines = [
        f"=== maxima-rubi {slug} depth-cap census ({len(inputs)} sidecars merged) ===",
        f"merge date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"record: {record}",
        f"switches: {record_switches_text(record)}",
        f"entries with cap hits: {len(hits)} of {len(keys)}  "
        f"total hits: {total}  max per entry: {biggest}",
        "",
    ]
    for key in sorted(hits, key=lambda k: order[k]):
        lines.append(f"{hits[key]} {key[0]} e{key[1]}")
    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"OK: {len(hits)} entries with cap hits, {total} hits, "
          f"max {biggest} (of {len(keys)} entries, {len(inputs)} sidecars)")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
