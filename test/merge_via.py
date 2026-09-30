#!/usr/bin/env python3
"""Merge a native-baseline run's per-shard .via sidecars into one census
(the MR_BASELINE mode of test/corpus_driver.py, run_entry_detail).

The driver writes one line per entry

    <who> integrate=<class>,<cpu>s,<tag> risch=<class>,<cpu>s,<tag> <relpath> e<entry> L<line>

where <who> is the integrator whose verdict the record carries (`risch` only
when integrate did not pass and risch did), `risch=-` says risch was not run,
and <tag> is the checker's proof tag (test/mr_verify.mac: the symbolic stage,
`numeric`, or `none/...`) or `-` for a run that never reached the checker.

The census must be COMPLETE against the merged record: every entry of the
record has exactly one line, and the class of its <who> run is the record's
class. Anything else is refused (the test/merge_proof.py rule).

Usage:
  merge_via.py RECORD OUT SHARD-GLOB

    RECORD      the merged baseline record
    OUT         the census file to write
    SHARD-GLOB  the sidecars, relative to test/ or absolute
"""

import glob
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)$")
VIA = re.compile(r"^(integrate|risch) integrate=(\S+) risch=(\S+) (.*) e(\d+) L(\d+)$")
RUN = re.compile(r"^([\w-]+),([\d.]+)s,(\S+)$")
PASS = ("verified", "expected", "no-answer")


def kind(tag):
    """symbolic | numeric | none, of a checker tag."""
    if tag.startswith("none"):
        return "none"
    if tag.startswith("numeric"):
        return "numeric"
    return "symbolic"


def parse_run(text):
    """(class, seconds, tag) of an `integrate=`/`risch=` field, None for `-`."""
    if text == "-":
        return None
    m = RUN.match(text)
    if not m:
        raise ValueError(text)
    return m.group(1), float(m.group(2)), m.group(3)


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[-5], file=sys.stderr)
        return 64
    record, out, pattern = argv
    slug = os.path.basename(record).replace("corpus_", "").replace(".out", "")

    cls_of = {}
    order = []
    header = None
    for line in open(record, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("filter:"):
            header = line
        m = RESULT.match(line)
        if m:
            key = (m.group(3), int(m.group(4)))
            cls_of[key] = m.group(1)
            order.append(key)
    if not order:
        raise SystemExit(f"merge_via: no result lines in {record}")

    inputs = sorted(glob.glob(os.path.join(ROOT, "test", pattern)))
    if not inputs:
        raise SystemExit(f"merge_via: no sidecars match {pattern}")
    rows = {}
    problems = []
    for path in inputs:
        for line in open(path, encoding="utf-8"):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            m = VIA.match(line)
            try:
                runs = {"integrate": parse_run(m.group(2)), "risch": parse_run(m.group(3))}
            except (AttributeError, ValueError):
                raise SystemExit(f"merge_via: bad line in {os.path.basename(path)}: {line!r}")
            who = m.group(1)
            key = (m.group(4), int(m.group(5)))
            if key not in cls_of:
                problems.append(f"not in {os.path.basename(record)}: {line}")
            elif key in rows:
                problems.append(f"duplicate: {line}")
            elif runs[who] is None or runs[who][0] != cls_of[key]:
                problems.append(f"the record says {cls_of[key]}: {line}")
            else:
                rows[key] = (who, runs, line)
    for key in order:
        if key not in rows:
            problems.append(f"missing: {cls_of[key]} {key[0]} e{key[1]}")
    if problems:
        print(f"INCOMPLETE: {len(problems)} problems", file=sys.stderr)
        for p in problems[:20]:
            print(f"  {p}", file=sys.stderr)
        return 1

    final = Counter()          # (who, class)
    paths = Counter()          # (who, class, kind) of checked verdicts
    stages = Counter()         # (who, tag) of symbolic proofs
    risch_after = Counter()    # (integrate class, risch class)
    for who, runs, _line in rows.values():
        cls, _t, tag = runs[who]
        final[(who, cls)] += 1
        if tag != "-":
            paths[(who, cls, kind(tag))] += 1
            if kind(tag) == "symbolic":
                stages[(who, tag)] += 1
        if runs["risch"] is not None:
            risch_after[(runs["integrate"][0], runs["risch"][0])] += 1

    n = len(rows)
    tried = sum(risch_after.values())
    rescued = sum(v for (_i, r), v in risch_after.items() if r in PASS)
    lines = [
        f"=== maxima-rubi {slug} integrator census ({len(inputs)} sidecars merged) ===",
        f"merge date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"record: {record}",
        header or "filter: ?",
        "",
        f"entries: {n}",
    ]
    for who in ("integrate", "risch"):
        tot = sum(v for (w, _c), v in final.items() if w == who)
        ok = sum(v for (w, c), v in final.items() if w == who and c in PASS)
        lines.append(f"verdict by {who}: {tot}  (PASS {ok})")
        for (w, c), v in sorted(final.items(), key=lambda kv: (-kv[1], kv[0])):
            if w == who:
                lines.append(f"  {c:14s} {v}")
    lines.append(f"risch tried: {tried}  passed: {rescued}")
    for (i, r), v in sorted(risch_after.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"  integrate {i} -> risch {r}: {v}")
    lines.append("checker path of the recorded verdict:")
    for (w, c, k), v in sorted(paths.items()):
        lines.append(f"  {w} {c} {k}: {v}")
    for (w, tag), v in sorted(stages.items(), key=lambda kv: (kv[0][0], -kv[1], kv[0][1])):
        lines.append(f"stage {w} {tag} {v}")
    lines.append("")
    for key in order:
        lines.append(rows[key][2])
    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"OK: {n} entries ({len(inputs)} sidecars); risch tried {tried}, passed {rescued}")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
