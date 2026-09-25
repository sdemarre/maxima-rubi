#!/usr/bin/env python3
"""Section-9 measurement (task-13 brief): the changed-verdict entries
between two merged corpus records, as a synthetic record
`run_corpus_queue.py --entries-from ... --class ...` can select for the
paired rerun (task-13 brief step 4: attribute every verdict flip between
the reference core and the branch core by re-running both cores on
exactly the entries that moved).

Reads both records with test/ab_records.py's own parser (`load_record`)
-- not reimplemented -- and prints one result line, in the shared T3
result-line format
    <class>  t=<s>s <relpath> e<entry> L<line>
per shared entry whose verdict CLASS differs between BASE and NEW
(ab_records.py's own definition of "changed": `a[0] != b[0]` over the
shared key set -- the same test its `classes` transition counter and
`--all` PASS<->FAIL listing use, so this is not a narrower notion than
what the A/B report already calls out). An entry present in only one of
the two records (a key-set mismatch, which ab_records.py's own exit
code 2 already flags separately) is not "changed" here -- there is
nothing to pair it against.

The verdict field of every printed line is the literal string
`timeout`, NOT a `changed` label. This is deliberate, not a mislabelling
bug: the merger this helper's output is designed to feed, through
run_corpus_queue.py's `--entries-from/--class/--out-dir` subset path
(test/wait_timeout_rerun.sh -> test/merge_timeout_rerun.py), hardcodes
its own completeness check to the literal class `timeout`
    expected = {k for k, m in accepted.items() if m.group(1) == "timeout"}
with no parameter to override it (it was written for the one existing
caller, the 30s-cap timeout re-check). Printing any other label (e.g.
`changed`) here would make merge_timeout_rerun.py see every re-run
entry as "extra" against an empty expected set and refuse the merge as
INCOMPLETE. Labelling every line `timeout` is what BOTH
run_corpus_queue.py's own `--class timeout` filter (`c == a.cls`,
string equality, no fixed vocabulary) AND merge_timeout_rerun.py's
hardcoded check expect, so the existing, already-tested wait/merge path
runs completely unmodified. The records this helper writes
(test/section9_changed_class<N>.out) are a private, uncommitted
intermediate of the paired-rerun step, not one of Task 13's committed
records -- nothing downstream reads the label as an actual per-entry
timeout.

Usage:
  python3 test/section9_changed.py BASE NEW
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ab_records as ab  # noqa: E402 (path insert must precede this import)


def changed_lines(base_path, new_path):
    """One T3-format line per shared (relpath, entry) whose class differs
    between BASE and NEW, class field forced to `timeout` (see module
    docstring); the NEW record's own seconds are reported."""
    base = ab.load_record(base_path)
    new = ab.load_record(new_path)
    shared = sorted(base.keys() & new.keys())
    for rel, entry in shared:
        a, b = base[(rel, entry)], new[(rel, entry)]
        if a[0] != b[0]:
            yield f"{'timeout':14s} t={b[1]:6.1f}s {rel} e{entry} L0"


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 64
    for line in changed_lines(argv[0], argv[1]):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
