#!/usr/bin/env python3
"""Regression guard for test/merge_proof.py, the merger of the checker's
per-shard `.proof` sidecars (.scratch/corpus-harness/issues/06).

A sidecar line is `<tag> <relpath> e<entry> L<line>`, one per entry that
reached the checker. The merged census must be complete against the merged
record: exactly the record's verified / expected / unverified entries carry
a tag, no other entry does, and no label names an entry the record lacks.
Synthetic record and sidecars in a temporary directory; no Maxima.

Re-runnable:  python3 test/test_merge_proof.py
Exits nonzero if any check fails.
"""

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MERGER = os.path.join(HERE, "merge_proof.py")

RECORD = """=== maxima-rubi class9 corpus run (full, 2 shards merged) ===
filter: '9 T/'  full run  timeout: 30s cpu  switches: none  verify: 30s cpu, stage 5s

verified       t=   0.1s 9 T/f.mac e1 L1
verified       t=   0.1s 9 T/f.mac e2 L2
expected       t=   0.1s 9 T/f.mac e3 L3
unverified     t=   0.1s 9 T/f.mac e4 L4
deferred       t=   0.1s 9 T/f.mac e5 L5
timeout        t=  30.0s 9 T/f.mac e6 L6

Results: 3 passed, 3 failed
"""

SHARD0 = """radcan 9 T/f.mac e2 L2
none/numeric-mismatch/timeout:radcan 9 T/f.mac e4 L4
"""
SHARD1 = """numeric 9 T/f.mac e1 L1
chainA.1 9 T/f.mac e3 L3
"""

passed = 0
failures = []


def check(name, ok, detail=""):
    global passed
    if ok:
        passed += 1
        print(f"PASS [{name}]")
    else:
        failures.append(name)
        print(f"FAIL [{name}] {detail}")


def run(tmp, shards):
    rec = os.path.join(tmp, "corpus_class9.x.out")
    with open(rec, "w") as fh:
        fh.write(RECORD)
    for k, text in enumerate(shards):
        with open(os.path.join(tmp, f"s.shard{k:02d}.proof"), "w") as fh:
            fh.write(text)
    out = os.path.join(tmp, "merged.proof")
    p = subprocess.run([sys.executable, MERGER, rec, out,
                        os.path.join(tmp, "s.shard*.proof")],
                       capture_output=True, text=True)
    text = open(out).read() if p.returncode == 0 and os.path.exists(out) else ""
    return p.returncode, text, p.stdout + p.stderr


def main():
    with tempfile.TemporaryDirectory() as tmp:
        rc, text, log = run(tmp, [SHARD0, SHARD1])
        check("complete sidecars merge", rc == 0, log)
        body = [l for l in text.splitlines() if " e" in l and not l.startswith(("=", "record:", "filter:"))]
        check("entries in record order, one tag each",
              body[-4:] == ["numeric 9 T/f.mac e1", "radcan 9 T/f.mac e2",
                            "chainA.1 9 T/f.mac e3",
                            "none/numeric-mismatch/timeout:radcan 9 T/f.mac e4"], body)
        check("census: symbolic / numeric / not proved per class",
              "verified: symbolic 1  numeric 1  none 0" in text
              and "expected: symbolic 1  numeric 0  none 0" in text
              and "unverified: symbolic 0  numeric 0  none 1" in text, text)
        check("census: count per closing stage",
              "stage radcan 1" in text and "stage chainA.1 1" in text, text)
        check("census: the verification budget is carried from the record",
              "verify: 30s cpu, stage 5s" in text, text)
    with tempfile.TemporaryDirectory() as tmp:
        rc, _t, log = run(tmp, [SHARD0])
        check("a checked entry without a tag is refused", rc != 0 and "missing" in log, log)
    with tempfile.TemporaryDirectory() as tmp:
        rc, _t, log = run(tmp, [SHARD0, SHARD1, "numeric 9 T/f.mac e5 L5\n"])
        check("a tag on an entry that never reached the checker is refused",
              rc != 0 and "not checked" in log, log)
    with tempfile.TemporaryDirectory() as tmp:
        rc, _t, log = run(tmp, [SHARD0, SHARD1, "radcan 9 T/f.mac e9 L9\n"])
        check("a tag for an entry the record lacks is refused",
              rc != 0 and "not in" in log, log)
    print(f"Results: {passed} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
