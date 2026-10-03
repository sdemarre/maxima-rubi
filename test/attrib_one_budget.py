#!/usr/bin/env python3
"""Attribute a native-baseline re-run's PASS -> FAIL entries to the one-budget
rule (.scratch/corpus-harness/issues/11, user decision 2026-10-03, option (b)).

Under one 30 s budget for integrate+risch, risch gets only what integrate left.
So an entry the OLD record passed through risch (`.via` line `risch ...`)
after integrate used up its own 30 s now keeps integrate's `timeout`: the
EXPECTED loss. Every other PASS -> FAIL needs a different explanation.

    python3 test/attrib_one_budget.py OLD.out OLD.via.out NEW.out NEW.via.out

OLD.via.out / NEW.via.out are merge_via.py censuses or raw .via sidecars (any
file of `.via` lines). Prints the expected set, which of it flipped, and every
PASS -> FAIL that is NOT in it with both runs' .via lines; ends
`Results: <k> expected losses, <m> unattributed, <j> expected kept` and exits 1
when <m> is nonzero.
"""

import re
import sys

RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)\s*$")
VIA = re.compile(r"^(integrate|risch) integrate=(\S+) risch=(\S+) (.*) e(\d+) L(\d+)$")
PASS = {"expected", "verified", "no-answer"}


def read_record(path):
    rec = {}
    for line in open(path, encoding="utf-8"):
        m = RESULT.match(line.rstrip("\n"))
        if m:
            rec[(m.group(3), int(m.group(4)))] = m.group(1)
    return rec


def read_via(path):
    via = {}
    for line in open(path, encoding="utf-8"):
        m = VIA.match(line.rstrip("\n"))
        if m:
            via[(m.group(4), int(m.group(5)))] = (m.group(1), m.group(2), m.group(3), line.strip())
    return via


def main(argv):
    if len(argv) != 4:
        print(__doc__.strip().splitlines()[-9], file=sys.stderr)
        return 64
    old, old_via, new, new_via = read_record(argv[0]), read_via(argv[1]), \
        read_record(argv[2]), read_via(argv[3])
    expected = {k for k, (who, i, _r, _l) in old_via.items()
                if who == "risch" and i.startswith("timeout,")}
    losses = {k for k in old if k in new and old[k] in PASS and new[k] not in PASS}
    hit = sorted(losses & expected)
    other = sorted(losses - expected)
    kept = sorted(k for k in expected if k in new and new[k] in PASS)
    print(f"expected (old: risch passed after integrate's timeout): {len(expected)}")
    print(f"PASS -> FAIL: {len(losses)}  of them expected: {len(hit)}")
    for k in hit:
        print(f"  expected  {old[k]} -> {new[k]}  {k[0]} e{k[1]}")
    for k in other:
        print(f"  UNATTRIBUTED  {old[k]} -> {new[k]}  {k[0]} e{k[1]}")
        print(f"      old: {old_via.get(k, (None,) * 4)[3]}")
        print(f"      new: {new_via.get(k, (None,) * 4)[3]}")
    for k in kept:
        print(f"  expected but kept  {old[k]} -> {new[k]}  {k[0]} e{k[1]}"
              f"  new: {new_via.get(k, (None,) * 4)[3]}")
    print(f"Results: {len(hit)} expected losses, {len(other)} unattributed, "
          f"{len(kept)} expected kept")
    return 1 if other else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
