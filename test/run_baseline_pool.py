#!/usr/bin/env python3
"""Step 8 (native-`integrate` baseline) as ONE command: one shard per corpus
file of SECTION, run through a pool of WORKERS processes (default 12 -- the
host's PHYSICAL core count, the 2026-09-20 baseline re-run's setting), then
the completeness-checked merge.

    python3 test/run_baseline_pool.py "8 Special functions" test/corpus_class8.baseline.out [WORKERS]

Each shard is `probes/corpus/probe-integrate-sample.py` over exactly one file
(start index i, stop i+1, the relative suite-dir form), writing
test/corpus_class<N>.baseline.shard<kk>.out / .log -- the naming
merge_class_shards.py's SHARD_GLOB reads. Blocks until the merge is done and
exits with the merger's code.
"""

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROBE = os.path.join(ROOT, "probes", "corpus", "probe-integrate-sample.py")
SUITE_REL = "reference/maxima-syntax-test-suite"


def main():
    section, out = sys.argv[1], sys.argv[2]
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    n = section.split()[0]
    suite = os.path.join(ROOT, SUITE_REL)
    nfiles = sum(1 for dp, _d, fs in os.walk(os.path.join(suite, section))
                 for f in fs if f.endswith(".mac"))
    for f in os.listdir(HERE):
        if f.startswith(f"corpus_class{n}.baseline.shard"):
            os.remove(os.path.join(HERE, f))

    def shard(i):
        base = os.path.join(HERE, f"corpus_class{n}.baseline.shard{i:02d}")
        with open(base + ".log", "w") as log:
            return subprocess.call(
                [sys.executable, PROBE, section + "/", "999999", "30", SUITE_REL,
                 str(i), "", "0", base + ".out", str(i + 1), section],
                cwd=ROOT, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)

    print(f"{section}: {nfiles} files, {workers} workers", flush=True)
    with ThreadPoolExecutor(workers) as ex:
        rcs = list(ex.map(shard, range(nfiles)))
    bad = [i for i, rc in enumerate(rcs) if rc != 0]
    print(f"shards done, nonzero exits: {bad}", flush=True)
    rc = subprocess.call(
        [sys.executable, os.path.join(HERE, "merge_class_shards.py"), section, out,
         os.path.join(HERE, "corpus_driver.py"), f"corpus_class{n}.baseline.shard*.out"],
        cwd=ROOT)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
