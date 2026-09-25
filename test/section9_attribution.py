#!/usr/bin/env python3
"""Section-9 port, Task 14: attribute every PASS->FAIL of the Task-13
measurement to one cause, from committed records only (no Maxima).

    python3 test/section9_attribution.py [> test/section9_attribution.out]

Inputs, all committed under test/:

  corpus_class<N>.s9-ref.out      the reference arm (core 0182d32c, 3,911 rules,
                                  worktree ../mr-s9-ref at master c95c6ed)
  corpus_class<N>.s9.out          the branch arm (core 434c241a, 3,997 rules)
  section9_paired_class<N>.{ref,new}/section9_changed_class<N>.timeout30s.out
                                  the paired rerun of every changed entry, both
                                  cores concurrently at 12 workers each
  section9_paired_class6.new/queue.log
                                  the branch arm's driver stderr; the inert-head
                                  leak classification prints `inert-leak <entry>:
                                  the answer carries <heads>` there
  section9_giveup_arm_class<N>.out
                                  the branch core re-run over exactly the
                                  PASS->FAIL entries with mr_giveup_last=false
                                  (12 workers, 30 s cpu cap) -- the experiment
                                  that isolates the give-up ordering cause
and one probe output:

  ../probes/section9/05-timing-ab.out
                                  the ALTERNATING SEQUENTIAL timing A/B (one
                                  entry at a time, one process at a time, ref
                                  core then branch core, 120 s cpu cap) of the
                                  entries that stay `timeout` on the branch at
                                  12 workers, written by
                                  `sh probes/section9/05-timing-ab.run`.
                                  Concurrent runs never carry a timing claim
                                  (timing-ab-alternate-not-concurrent).

Buckets, applied in this order (a `timeout` is decided on TIMING evidence
first, so the give-up experiment -- which also changes how much of the table
is walked -- never claims an entry the cap decided):

  cap          the branch verdict is `timeout` on an entry the reference
               VERIFIED, and the sequential A/B shows the branch still
               finishing inside the 30 s cap at under 1.2x the reference cost
               (or, with no timing row, the branch core PASSes it at 12 workers
               in the paired rerun, or the REFERENCE core already fails it
               there).
  cost         the same, but the sequential A/B puts the branch at or over the
               30 s cap, or at 1.2x the reference or more.
  inert-leak   the branch answer carries one of the six inert trig heads
               (%mr_isin .. %mr_icsc), which the driver classifies `error`.
  give-up      the entry is PASS again on the BRANCH core once the give-up
               reordering is off, i.e. what lost it is that mr_giveup_last
               defers class-1/2/3's Unintegrable marker rules behind 9.3's
               non-give-up bare-`u_` records.
  route        everything else: a 9.x rule answers first and its answer
               carries an interior noun.

NOTE on the `cap` bucket: every entry in it ALSO returns to a PASS class in the
give-up experiment, but that arm ran at 12 workers rather than the record's 24,
so it cannot separate the switch from the lower contention and is not used for
them. What is claimed for a `cap` entry is only what its own row shows.

The script also prints the OVERLAP between the last two: entries the give-up
experiment recovers although they are primarily bucketed as inert-leak.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import ab_records as ab  # noqa: E402
from corpus_driver import PASS_CLASSES  # noqa: E402

CLASSES = (1, 2, 3, 6)
LEAK = re.compile(r"^inert-leak (.*) e(\d+) L\d+: the answer carries (.*)$")


def read(path):
    return ab.load_record(os.path.join(ROOT, path))


def leak_set():
    """{(rel, entry): heads} from the branch arm's driver stderr."""
    out = {}
    path = os.path.join(ROOT, "test", "section9_paired_class6.new", "queue.log")
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = LEAK.match(line.rstrip("\n"))
            if m:
                out[(m.group(1), int(m.group(2)))] = m.group(3).strip()
    return out


def timing():
    """{(rel, entry): {arm: seconds}} from the alternating sequential A/B."""
    out = {}
    path = os.path.join(ROOT, "probes", "section9", "05-timing-ab.out")
    if not os.path.exists(path):
        return out
    rx = re.compile(r"^(ref|new)\s+(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L\d+\s*$")
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = rx.match(line.rstrip("\n"))
            if m:
                out.setdefault((m.group(4), int(m.group(5))), {})[m.group(1)] = (
                    m.group(2), float(m.group(3)))
    return out


def main():
    leaks = leak_set()
    times = timing()
    grand = {}
    overlap = []
    for n in CLASSES:
        base = read(f"test/corpus_class{n}.s9-ref.out")
        new = read(f"test/corpus_class{n}.s9.out")
        gl = read(f"test/section9_giveup_arm_class{n}.out")
        pref = read(f"test/section9_paired_class{n}.ref/"
                    f"section9_changed_class{n}.timeout30s.out")
        pnew = read(f"test/section9_paired_class{n}.new/"
                    f"section9_changed_class{n}.timeout30s.out")
        pf = sorted(k for k in base
                    if k in new and base[k][0] in PASS_CLASSES
                    and new[k][0] not in PASS_CLASSES)
        buckets = {}
        print(f"=== class {n}: PASS {sum(1 for v in base.values() if v[0] in PASS_CLASSES)}"
              f" -> {sum(1 for v in new.values() if v[0] in PASS_CLASSES)}"
              f"  (PASS->FAIL {len(pf)},"
              f" FAIL->PASS {sum(1 for k in base if k in new and base[k][0] not in PASS_CLASSES and new[k][0] in PASS_CLASSES)})")
        for k in pf:
            b, w = base[k][0], new[k][0]
            gl_pass = k in gl and gl[k][0] in PASS_CLASSES
            # An entry the reference ANSWERED and verified, now `timeout`, is a
            # timing question and is decided on timing evidence. An entry whose
            # corpus answer is Unintegrable/CannotIntegrate (base `no-answer`)
            # times out because it took a route at all, so the give-up
            # experiment decides it even when the symptom is a timeout.
            timing_case = w == "timeout" and b in ("verified", "expected")
            if timing_case and k in times:
                # The alternating sequential A/B decides: `cost` when the branch
                # no longer finishes inside the standing 30 s cap uncontended, or
                # when it costs 1.2x the reference or more; `cap` otherwise.
                tr, tn = times[k]["ref"][1], times[k]["new"][1]
                cause = ("cost" if tn >= 30.0 or tn >= 1.2 * tr else "cap")
            elif timing_case and (
                    (k in pnew and pnew[k][0] in PASS_CLASSES)
                    or (k in pref and pref[k][0] not in PASS_CLASSES)):
                cause = "cap"
            elif timing_case:
                cause = "cost"
            elif k in leaks and w == "error":
                cause = "inert-leak"
                if gl_pass:
                    overlap.append(k)
            elif gl_pass:
                cause = "give-up"
            else:
                cause = "route"
            buckets.setdefault(cause, []).append(k)
            grand[cause] = grand.get(cause, 0) + 1
        for cause in ("cap", "cost", "inert-leak", "give-up", "route"):
            ks = buckets.get(cause, [])
            if not ks:
                continue
            print(f"  {cause:<11} {len(ks)}")
            if cause in ("cost", "route", "cap") or len(ks) <= 6:
                for k in ks:
                    extra = ""
                    if cause in ("cost", "cap") and k in times:
                        t = times[k]
                        extra = ("  [probe 05, sequential 120 s cap: ref "
                                 f"{t.get('ref', ('?', 0))[1]}s {t.get('ref', ('?',))[0]},"
                                 f" branch {t.get('new', ('?', 0))[1]}s"
                                 f" {t.get('new', ('?',))[0]}]")
                    if cause == "inert-leak":
                        extra = f"  [{leaks[k]}]"
                    print(f"      {base[k][0]} {base[k][1]}s -> {new[k][0]}"
                          f" {new[k][1]}s  {k[0]} e{k[1]}{extra}")
        print()
    print("=== all four classes ===")
    for cause in ("cap", "cost", "inert-leak", "give-up", "route"):
        print(f"  {cause:<11} {grand.get(cause, 0)}")
    print(f"  {'TOTAL':<11} {sum(grand.values())}")
    print(f"  overlap: {len(overlap)} of the inert-leak entries are also"
          " recovered by the give-up experiment")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
