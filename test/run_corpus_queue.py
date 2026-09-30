#!/usr/bin/env python3
"""Layer B corpus runs through one work queue (exact seen test design,
docs/superpowers/specs/2026-09-15-matcher-seen-test-intpart-design.md 3.3).

The sharded launchers (test/launch_class_shards.py, launch_timeout_rerun.py)
pack entries into fixed shards by the previous record's per-entry times;
when routes change, those estimates go stale and a run ends with a long tail
of a few busy shards (P5b run 4, class 1: shards finished between +6 and
+87 min, all 24 busy for about 53 % of the wall). Here one manager process
runs N worker threads that pull single entries from one queue. Every entry
is already its own Maxima subprocess (corpus_driver.run_entry), so a worker
is idle only when the queue is empty.

Worker k writes its own shard file: the driver's header, one result line per
finished entry, the driver's summary block. The existing mergers read the
output unchanged.

  full section  test/corpus_<slug>.shard<kk>.out; pids file
                test/corpus_<slug>.shard-pids (one line `queue <pid> -`);
                log test/corpus_<slug>.shard-queue.log
                -> setsid sh test/wait_and_merge.sh test/corpus_<slug>.shard-pids \\
                     test/merge_class_shards.py <merge-log> "<SECTION>" <record> \\
                     test/corpus_driver.py "corpus_<slug>.shard*.out"
  subset        --entries-from RECORD --class CLS --out-dir DIR (the 100 s
                timeout re-check): DIR/shard<kk>.out, DIR/pids, DIR/source
                (RECORD), DIR/queue.log
                -> setsid sh test/wait_timeout_rerun.sh DIR >> DIR/wait.log 2>&1 &

Usage:
  run_corpus_queue.py SECTION [--prev RECORD] [--workers N] [--cap S]
                      [--entries-from RECORD --class CLS --out-dir DIR]
                      [--launch]

Without --launch: a dry run (entries, workers, estimated core-seconds and
wall). --launch clears the previous run's files (refusing while its pid is
alive), starts the manager detached (stdin /dev/null) and writes the pids
file. The queue runs the longest previous time first (--prev; entries the
previous record does not time go first of all), so the 30 s timeouts do not
gather at the end. Env: MR_SWITCHES (the arm) and MR_RULES_CORE_PATH (a
pinned core), read by the driver as for every run; MR_N_PROCS (the default
worker count).
"""

import argparse
import importlib.util
import os
import queue
import re
import subprocess
import sys
import threading
import time
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUITE_REL = "reference/maxima-syntax-test-suite"
DRIVER = os.path.join(ROOT, "test", "corpus_driver.py")
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)\s*$")
UNTIMED = float("inf")


def parse_args(argv):
    ap = argparse.ArgumentParser(description="Layer B corpus run through one work queue")
    ap.add_argument("section", help='e.g. "2 Exponentials"')
    ap.add_argument("--prev", help="a record whose t= fields order the queue, longest first")
    ap.add_argument("--workers", type=int,
                    default=int(os.environ.get("MR_N_PROCS") or os.cpu_count() or 24))
    ap.add_argument("--cap", type=int, default=30, help="per-entry cap in seconds")
    ap.add_argument("--job-seconds", dest="job_seconds", type=float, default=0.0,
                    help="dispatch unit size in ESTIMATED seconds of work "
                         "(default 0 = one entry per unit, which is what the "
                         "2026-09-17 simulation measured as best; see "
                         "build_units)")
    ap.add_argument("--entries-from", dest="entries_from")
    ap.add_argument("--class", dest="cls")
    ap.add_argument("--out-dir", dest="out_dir")
    ap.add_argument("--launch", action="store_true")
    ap.add_argument("--run", action="store_true", help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    subset = (a.entries_from, a.cls, a.out_dir)
    if any(subset) and not all(subset):
        ap.error("--entries-from, --class and --out-dir go together")
    if a.launch and a.run:
        ap.error("--launch and --run exclude each other")
    for name in ("prev", "entries_from", "out_dir"):
        if getattr(a, name):
            setattr(a, name, os.path.abspath(getattr(a, name)))
    return a


def load_driver(section, cap):
    """The corpus driver module for SECTION at CAP (it reads its argv at import)."""
    saved = sys.argv
    sys.argv = [DRIVER, section + "/", "999999", str(cap), SUITE_REL]
    try:
        spec = importlib.util.spec_from_file_location("corpus_driver", DRIVER)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.argv = saved
    return mod


def read_record(path):
    """{(rel, entry): (class, seconds)} of a record's result lines."""
    rec = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = RESULT.match(line.rstrip("\n"))
            if m:
                rec[(m.group(3), int(m.group(4)))] = (m.group(1), float(m.group(2)))
    return rec


def build_jobs(driver, prev=None, subset=None):
    """[(rel, idx, entry_text, line_no, cost)] over the driver's section, IDX
    0-based. Ordered by PREV's time, longest first, with the entries PREV does
    not time before all others. SUBSET, a set of (rel, entry) keys, keeps only
    those; a key the section does not have exits."""
    jobs = []
    for path, rel in driver.file_list():
        entries, line_nos = driver.extract_entries(path)
        for idx, text in enumerate(entries):
            key = (rel, idx + 1)
            if subset is not None and key not in subset:
                continue
            cost = prev[key][1] if prev and key in prev else UNTIMED
            jobs.append((rel, idx, text, line_nos[idx], cost))
    if subset is not None:
        missing = sorted(subset - {(j[0], j[1] + 1) for j in jobs})
        if missing:
            raise SystemExit(f"run_corpus_queue: {len(missing)} entries are not in the "
                             f"section, e.g. {missing[:3]}")
    jobs.sort(key=lambda j: (-j[4], j[0], j[1]))
    return jobs


def build_units(jobs, job_seconds):
    """JOBS (already longest-estimate-first) grouped into dispatch units.

    JOB_SECONDS = 0 gives one entry per unit, which is the default and the
    measured-best. MEASURED 2026-09-17 on the 25,697 per-entry walls of the
    faithful-pair class-1 run, dynamic pull, 24 workers (floor 116 min):

        per-entry, corpus order                116.2 min   0.2 % idle
        per-entry, longest-first on STALE est. 116.1 min   0.1 % idle
        per-entry, perfect foresight           115.9 min   0.0 % idle
        units of ~10 estimated min             120.3 min   3.6 % idle
        units of ~30 estimated min             126.3 min   8.2 % idle

    Makespan >= floor + the largest unit, so the unit size IS the tail bound.
    Every entry is already its own Maxima subprocess, so a larger unit
    amortises nothing — there is no per-entry startup to save — while it
    raises that bound. And the estimates that size a unit are the ones that
    go stale: built from the PREVIOUS record, a 10-minute target produced a
    35-minute actual unit and a 30-minute target a 91-minute one (the same
    staleness that made the sharded launcher miss its predicted max job by
    13.6x). At one entry per unit the bound is the per-entry cap, 30 s,
    however wrong the estimates are — note the three per-entry rows above sit
    within 0.3 min of each other, i.e. the cost model stops mattering.

    JOB_SECONDS > 0 is kept so the trade-off can be re-measured, not because
    it is expected to win. Entries the previous record does not time have an
    infinite estimate and always form their own unit; with no --prev every
    entry does, so chunking is then a no-op."""
    if job_seconds <= 0:
        return [[j] for j in jobs]
    units = []
    cur = []
    cost = 0.0
    for j in jobs:
        cur.append(j)
        cost += j[4]
        if cost >= job_seconds:
            units.append(cur)
            cur = []
            cost = 0.0
    if cur:
        units.append(cur)
    return units


def summary_lines(driver, counts, wall):
    """The driver's summary block over one worker's COUNTS."""
    total = sum(counts.values())
    passed = sum(v for k, v in counts.items() if k in driver.PASS_CLASSES)
    with driver.REWRITE_LOCK:
        stats = dict(driver.REWRITE_STATS)
    return (["", "=== summary ===", f"head rewrites: {stats or '{}'}"]
            + [f"{k:14s} {counts[k]}" for k in sorted(counts)]
            + [f"total integrals: {total}", f"wall time: {wall:.1f}s",
               f"Results: {passed} passed, {total - passed} failed"])


def run_queue(driver, jobs, workers, out_paths, title, detail, build_lines,
              log=print, job_seconds=0.0):
    """Run JOBS on WORKERS threads; worker k writes OUT_PATHS[k] with the header
    TITLE(k) / DETAIL(k), and its depth-cap sidecar OUT_PATHS[k] with .caps for
    the suffix (the driver's own convention, so test/merge_caps.py finds them)
    and its proof sidecar with .proof (the checker's tag per entry).
    JOB_SECONDS sizes the dispatch unit (see build_units). A Python exception
    around one entry writes it as `error` and counts a harness failure.
    Returns (counts by class, harness failures, wall seconds)."""
    q = queue.Queue()
    units = build_units(jobs, job_seconds)
    for unit in units:
        q.put(unit)
    lock = threading.Lock()
    totals = {}
    failures = [0]
    t0 = time.time()

    def worker(k):
        counts = {}
        tw = time.time()
        caps_path = os.path.splitext(out_paths[k])[0] + ".caps"
        proof_path = os.path.splitext(out_paths[k])[0] + ".proof"
        try:
            with open(out_paths[k], "w", encoding="utf-8") as outf, \
                 open(caps_path, "w", encoding="utf-8") as capsf, \
                 open(proof_path, "w", encoding="utf-8") as prooff:
                outf.write("\n".join(driver.header_lines(title(k), detail(k), build_lines)) + "\n")
                outf.flush()
                while True:
                    try:
                        unit = q.get_nowait()
                    except queue.Empty:
                        break
                    for rel, idx, text, line_no, _cost in unit:
                        ts = time.time()
                        caps = 0
                        proof = None
                        try:
                            cls, line, caps, proof = driver.run_entry_full(
                                rel, idx, text, line_no)
                        except Exception:
                            cls = "error"
                            line = (f"{'error':14s} t={time.time() - ts:6.1f}s "
                                    f"{rel} e{idx + 1} L{line_no}")
                            with lock:
                                failures[0] += 1
                                log(f"HARNESS FAILURE worker {k:02d}: {rel} e{idx + 1}\n"
                                    + traceback.format_exc())
                        counts[cls] = counts.get(cls, 0) + 1
                        outf.write(line + "\n")
                        outf.flush()
                        if caps > 0:
                            capsf.write(f"{caps} {rel} e{idx + 1} L{line_no}\n")
                            capsf.flush()
                        if proof is not None:
                            prooff.write(f"{proof} {rel} e{idx + 1} L{line_no}\n")
                            prooff.flush()
                        with lock:
                            totals[cls] = totals.get(cls, 0) + 1
                            log(f"{'PASS' if cls in driver.PASS_CLASSES else 'FAIL'}: {line}")
                outf.write("\n".join(summary_lines(driver, counts, time.time() - tw)) + "\n")
        except Exception:
            with lock:
                failures[0] += 1
                log(f"HARNESS FAILURE worker {k:02d} died\n" + traceback.format_exc())

    threads = [threading.Thread(target=worker, args=(k,)) for k in range(workers)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    wall = time.time() - t0
    left = q.qsize()
    if left:
        failures[0] += 1
        log(f"HARNESS FAILURE: {left} units left in the queue")
    log(f"queue wall: {wall:.1f}s  entries: {len(jobs)}  units: {len(units)}  "
        f"workers: {workers}  harness failures: {failures[0]}")
    return totals, failures[0], wall


def clear_subset_dir(rr, out_dir):
    """clear_stale_shards for a subset run directory."""
    pidfile = os.path.join(out_dir, "pids")
    if os.path.exists(pidfile):
        with open(pidfile, encoding="utf-8") as fh:
            for line in fh:
                parts = line.split()
                if len(parts) >= 2 and parts[1].isdigit() and rr._alive(int(parts[1])):
                    raise SystemExit(f"{pidfile}: {parts[0]} (pid {parts[1]}) is still running; "
                                     "wait for it or kill it before a new launch")
    removed = 0
    for name in sorted(os.listdir(out_dir)):
        if re.fullmatch(r"shard\d+\.(?:out|log|files|caps|proof)|pids|source|queue\.log|merge\.out|wait\.log", name):
            os.unlink(os.path.join(out_dir, name))
            removed += 1
    return removed


def child_argv(a):
    out = [a.section, "--workers", str(a.workers), "--cap", str(a.cap),
           "--job-seconds", str(a.job_seconds), "--run"]
    if a.prev:
        out += ["--prev", a.prev]
    if a.entries_from:
        out += ["--entries-from", a.entries_from, "--class", a.cls, "--out-dir", a.out_dir]
    return out


def main(argv):
    a = parse_args(argv)
    os.chdir(ROOT)
    driver = load_driver(a.section, a.cap)
    slug = "class" + a.section.split()[0]
    subset = None
    if a.entries_from:
        subset = {k for k, (c, _t) in read_record(a.entries_from).items() if c == a.cls}
        if not subset:
            raise SystemExit(f"run_corpus_queue: no `{a.cls}` entries in {a.entries_from}")
    jobs = build_jobs(driver, read_record(a.prev) if a.prev else None, subset)
    workers = max(1, min(a.workers, len(jobs)))
    if subset is not None:
        outs = [os.path.join(a.out_dir, f"shard{k:02d}.out") for k in range(workers)]
        pidfile = os.path.join(a.out_dir, "pids")
        logfile = os.path.join(a.out_dir, "queue.log")
    else:
        test_dir = os.path.join(ROOT, "test")
        outs = [os.path.join(test_dir, f"corpus_{slug}.shard{k:02d}.out") for k in range(workers)]
        pidfile = os.path.join(test_dir, f"corpus_{slug}.shard-pids")
        logfile = os.path.join(test_dir, f"corpus_{slug}.shard-queue.log")
    timed = [j[4] for j in jobs if j[4] != UNTIMED]
    core_sec = sum(timed)
    units = build_units(jobs, a.job_seconds)
    unit_costs = [sum(j[4] for j in u if j[4] != UNTIMED) for u in units]
    # Makespan >= core_sec/workers + the largest unit: the unit size is the
    # tail bound, which is why the default is one entry per unit.
    est = core_sec / workers + max(unit_costs, default=0.0)
    cores = os.cpu_count() or 0
    plan = [
        f"=== {slug} queue plan ===",
        f"entries: {len(jobs)}  units: {len(units)}  workers: {workers}  cap: {a.cap}s  "
        f"timed by {a.prev or '(no --prev)'}: {len(timed)}  untimed (run first): {len(jobs) - len(timed)}",
        f"job-seconds: {a.job_seconds:g}"
        + ("  (one entry per unit)" if a.job_seconds <= 0 else
           f"  largest unit: {max(unit_costs, default=0.0) / 60:.1f} estimated min"),
        f"estimated core-seconds: {core_sec:.0f}  estimated wall: {est / 60:.1f} min "
        f"(= core-seconds/workers + largest unit; timed entries only)",
        f"switches: {driver.run_records.switches_text(driver.SWITCH_SETTINGS)}",
        f"outputs: {outs[0]} .. {os.path.basename(outs[-1])}  pids: {pidfile}  log: {logfile}",
    ]
    if cores and workers > cores:
        # Over-subscription is a FIDELITY problem, not just a speed one: every
        # entry then runs contended, its wall depends on how many others happen
        # to be running, and the 30 s cap is a WALL cap, so it decides verdicts.
        # The 2026-09-17 class-1 run launched 33 processes on 24 vCPUs.
        plan.append(f"WARNING: {workers} workers > {cores} cores — entries will run "
                    f"contended and their walls are not comparable with an "
                    f"uncontended record (the 30 s cap is a wall cap)")
    if a.run:
        print("\n".join(plan), flush=True)
        subset_text = f"  subset: {a.cls} of {a.entries_from}" if subset is not None else ""
        _counts, failures, _wall = run_queue(
            driver, jobs, workers, outs,
            lambda k: f"=== maxima-rubi corpus queue worker {k:02d} (filter {driver.FILTER!r}) ===",
            lambda k: (f"queue worker {k:02d} of {workers}  "
                       f"timeout: {driver.TIMEOUT}s {driver.CAP_KIND}  "
                       f"entries: {len(jobs)}" + subset_text),
            driver.build_info_lines(),
            log=lambda msg: print(msg, flush=True),
            job_seconds=a.job_seconds)
        return 1 if failures else 0
    print("\n".join(plan))
    if not a.launch:
        return 0
    if subset is not None:
        os.makedirs(a.out_dir, exist_ok=True)
        removed = clear_subset_dir(driver.run_records, a.out_dir)
    else:
        try:
            removed = driver.run_records.clear_stale_shards(os.path.join(ROOT, "test"), slug)
        except RuntimeError as exc:
            raise SystemExit(f"run_corpus_queue: {exc}")
    print(f"removed {removed} files of the previous run")
    with open(logfile, "w", encoding="utf-8") as lf:
        p = subprocess.Popen([sys.executable, os.path.abspath(__file__)] + child_argv(a),
                             cwd=ROOT, stdin=subprocess.DEVNULL, stdout=lf,
                             stderr=subprocess.STDOUT, start_new_session=True)
    with open(pidfile, "w", encoding="utf-8") as pf:
        pf.write(f"queue {p.pid} -\n")
    if subset is not None:
        with open(os.path.join(a.out_dir, "source"), "w", encoding="utf-8") as fh:
            fh.write(a.entries_from + "\n")
    print(f"launched the queue: pid {p.pid}; pids in {pidfile}; log {logfile}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
