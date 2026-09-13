#!/usr/bin/env python3
"""Probe 11 -- matcher substrate P5: noise re-check of the entries that
change PASS/FAIL between a base-arm and a flipped-arm full corpus run
(spec docs/superpowers/specs/2026-09-12-matcher-substrate-design.md
section 4 P5; the plan-3 run-1-vs-run-2 A/B for `mr_flat_wide`, ledger
`.superpowers/sdd/2026-09-13-matcher-substrate-plan3/`).

Problem this answers: a per-switch A/B (test/p5_gate.py `winner`) reads
the PASS COUNT delta at face value, but most of the changed entries sit
at the 30 s per-entry cap (`timeout t=30.0s -> verified t=28.1s`), which
is exactly where a busy machine's load can flip the verdict without the
rule table changing at all. This probe re-runs every entry that changed
PASS<->FAIL between the two records, REPS times under EACH arm,
interleaved so load drift hits both arms equally, and calls the same
`winning_value()` the gate uses, but fed noise-filtered per-class PASS
counts (reproducible base-wins vs. reproducible flip-wins) instead of
the raw full-corpus counts.

Generic over the three migration switches (mr_flat_wide, mr_cond_retry,
mr_model_flags): pass the switch name and the six records (base/flip x
class 1/2/3) and it works the same way for run 3 and run 4.

Design (read before changing):

  * Selection and the arm check reuse test/ab_records.py (load_record,
    compare, driver_pass_classes) and test/run_records.py
    (record_switches, switches_text, SWITCHES) exactly as
    test/p5_gate.py's `winner` command does: the base and flip record
    triples must each state ONE arm (record_switches on all three
    class records), and the two arms must differ in SWITCH only, or
    the probe exits nonzero (SystemExit) before touching Maxima.
  * `test/p5_gate.py`'s `winning_value(switch, base_value, flip_value,
    base_pass, flip_pass)` is CALLED (not re-implemented) for the
    final noise-filtered verdict.
  * Two arms, one entry mechanics: the corpus driver
    (test/corpus_driver.py) computes its SWITCH_SETTINGS from
    MR_SWITCHES at IMPORT time (a module-level global read by
    build_text's closure), so one imported driver module can only ever
    run one arm. This probe imports test/corpus_driver.py TWICE, by
    path, under two distinct module names (`corpus_driver_base`,
    `corpus_driver_flip`), setting os.environ["MR_SWITCHES"] to the
    base arm's text immediately before the first exec_module call and
    to the flip arm's text immediately before the second, restoring
    the prior MR_SWITCHES afterwards. Each resulting module object
    freezes its own SWITCH_SETTINGS in its own globals dict at import
    time, so `corpus_driver_base.build_text(...)` and
    `corpus_driver_flip.build_text(...)` thereafter always build text
    for their own arm regardless of the live environment -- THE JOB
    TEXT COMES FROM CALLING THE DRIVER'S OWN build_text/maxima_run, so
    it is byte-identical to what a real corpus run under that
    MR_SWITCHES would send to Maxima, by construction, not assertion.
    An assertion still checks the three switch-assignment lines these
    functions bake in against an arm-independent recomputation
    (switch_head(), below) for both arms, as a belt-and-braces check.
  * sys.argv: corpus_driver.py reads sys.argv[1..10] at import time for
    its FILTER/PER_FILE/... globals (none of which this probe's job
    loop uses -- entries are resolved by joining the record's `rel`
    key onto the driver's own SUITE constant, verified 2026-09-13 to
    recover the exact original file for every sampled key). sys.argv
    is therefore overridden to a short, harmless placeholder list
    (mirroring the plan-3 attachment
    docs/superpowers/plans/2026-09-13-matcher-substrate-plan3.files/probes/10-p5-attribution.py)
    before each import, so this probe's own argv (whose element 1 is
    an output path, not an integer) cannot make corpus_driver's
    guarded `int(sys.argv[N])` conversions raise at import time.
  * Classification is never re-implemented: PASS_CLASSES / KNOWN_CLASSES
    and the "no CLASS line -> timeout/error" fallback are the imported
    driver module's own attributes and the same few lines
    test/corpus_driver.py's main loop and probe 10 both use to read a
    subprocess's stdout.
  * --dry-run imports NEITHER corpus_driver copy (so it cannot trigger
    ensure_rules_core()'s build-if-stale path, which can spawn a
    minutes-long sbcl build) and never calls `maxima`: entry selection
    and the switch-assignment head are pure Python/text-record work
    reachable from ab_records.py/run_records.py alone.

Per-entry re-run: REPS repetitions under the base arm and REPS under
the flip arm, WORKERS concurrent subprocesses (a single thread pool
across every class and both arms -- Maxima subprocesses, so the GIL is
not the bottleneck), CAP seconds per subprocess, stdin /dev/null
(inherited from corpus_driver.maxima_run). Jobs are ordered round-robin
base/flip within each repetition generation, across every selected
entry of every class, so a load spike at any point in the run lands on
both arms' reps of that generation rather than skewing one arm's reps
toward the machine's early (or late) load.

PASS-stable / FAIL-stable: all REPS reps landed in a PASS class / all
REPS reps landed in a (non-None) non-PASS class (driver_pass_classes()
membership; the reps need not be the SAME class -- expected one rep,
verified the next, is still PASS-stable). A rep with no result at all
(the job's try/except caught a Python-level exception before
maxima_run could even run -- a harness failure, never observed in
practice but guarded for) blocks both stability checks, so its entry
reads `noise`.

  repro-flip-better  flip PASS-stable AND base FAIL-stable
  repro-base-better  base PASS-stable AND flip FAIL-stable
  noise              anything else (incl. the original A/B direction
                     not reproducing, or reversing)

Results: line -- "timeout" and "error" are driver CLASSES (KNOWN_
CLASSES), not harness failures: a rep that hits the CAP-second wall or
a Lisp/SBCL crash still produced a CLASS and counts toward n (passed
in the Results: sense); only a rep whose Python job wrapper raised
before even calling maxima_run counts toward m (failed).

Usage (repo root):
  python3 probes/matcher/11-arm-noise-recheck.py SWITCH OUT \\
      --base  <class1-rec> <class2-rec> <class3-rec> \\
      --flip  <class1-rec> <class2-rec> <class3-rec> \\
      [--reps 3] [--cap 30] [--workers 24] [--dry-run]

SWITCH is one of mr_flat_wide, mr_cond_retry, mr_model_flags. The three
--base / --flip records are class 1, 2, 3 in that order (the
test/p5_gate.py `winner` convention). --dry-run does no Maxima work at
all (see above) and exits 0.
"""

import argparse
import concurrent.futures
import importlib.util
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TEST_DIR = os.path.join(ROOT, "test")
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
CLASS_LABELS = ("class1", "class2", "class3")


def _module(name, path=None):
    path = path or os.path.join(TEST_DIR, name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Lightweight, no-Maxima: safe to import unconditionally (dry-run included).
ab = _module("ab_records")
rr = _module("run_records")
p5 = _module("p5_gate")  # for winning_value(); its own top-level re-imports ab/rr harmlessly.

DRIVER_PATH = os.path.join(TEST_DIR, "corpus_driver.py")


def parse_args(argv):
    p = argparse.ArgumentParser(
        description="Re-run the PASS<->FAIL entries of a switch A/B under "
                    "both arms, several times, to separate a real winner "
                    "from 30s-cap noise.")
    p.add_argument("switch", choices=rr.SWITCHES)
    p.add_argument("out")
    p.add_argument("--base", nargs=3, required=True,
                   metavar=("CLASS1", "CLASS2", "CLASS3"))
    p.add_argument("--flip", nargs=3, required=True,
                   metavar=("CLASS1", "CLASS2", "CLASS3"))
    p.add_argument("--reps", type=int, default=3)
    p.add_argument("--cap", type=int, default=30)
    p.add_argument("--workers", type=int, default=24)
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args(argv)


def arm_dict(paths):
    """{switch: value} the three PATHS (one class each) all state; SystemExit
    if any lacks a switches: line or they don't all agree (mirrors
    test/p5_gate.py winner's `_arm`)."""
    texts = {rr.record_switches(p) for p in paths}
    if None in texts or len(texts) != 1:
        raise SystemExit(f"records do not state one arm: {paths} -> {sorted(map(str, texts))}")
    return dict(item.split("=") for item in texts.pop().split())


def check_arms(switch, base_arm, flip_arm):
    differ = sorted(s for s in rr.SWITCHES if base_arm[s] != flip_arm[s])
    if differ != [switch]:
        raise SystemExit(f"the base/flip arms differ in {differ}, not in [{switch!r}] only "
                         f"(base {base_arm}, flip {flip_arm})")


def switch_head(arm):
    """The switch-assignment lines corpus_driver.build_text prepends to
    every entry text under ARM -- an arm-independent recomputation of its
    `switches = "".join(f"{name} : {value}$\\n" for name, value in
    SWITCH_SETTINGS.items())` line (SWITCH_SETTINGS starts from
    run_records.SWITCH_DEFAULTS, whose key order IS rr.SWITCHES order and
    is never reordered by an override), used both for the dry-run
    printout and as the real run's belt-and-braces assertion target."""
    return "".join(f"{name} : {arm[name]}$\n" for name in rr.SWITCHES)


def git_head():
    r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT)
    return r.stdout.strip() or "(unknown)"


def core_stamp_line():
    path = os.path.join(TEST_DIR, "mr_rules.core.stamp")
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.readline().strip()
    except OSError:
        return "(no core stamp)"


def maxima_build_lines():
    r = subprocess.run(["maxima", "--very-quiet", "--batch-string", "disp(build_info());"],
                       capture_output=True, text=True, timeout=120)
    return [f"maxima: {s.strip()}" for s in r.stdout.splitlines()
            if s.strip().startswith(("Maxima", "Lisp ", "Host "))]


def select_changed(base_path, flip_path, pass_classes):
    """[(key, base_entry, flip_entry, direction), ...] sorted by key, for one
    class's base/flip record pair -- the PASS<->FAIL entries only. key is
    (rel, entry_number); base_entry/flip_entry are (class, seconds)."""
    base_rec, flip_rec = ab.load_record(base_path), ab.load_record(flip_path)
    r = ab.compare(base_rec, flip_rec, pass_classes)
    changed = [(k, a, b, "PASS->FAIL") for k, a, b in r["pass_fail"]]
    changed += [(k, a, b, "FAIL->PASS") for k, a, b in r["fail_pass"]]
    changed.sort(key=lambda t: t[0])
    return changed


def build_header(args, base_arm_text, flip_arm_text, base_arm, flip_arm, dry):
    lines = [f"=== probes/matcher/11-arm-noise-recheck  git HEAD {git_head()}  "
             f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"]
    if not dry:
        lines += maxima_build_lines()
    lines.append(f"core stamp: {core_stamp_line()}")
    lines.append(f"switch: {args.switch}")
    lines.append(f"base arm: {base_arm_text}")
    lines.append(f"flip arm: {flip_arm_text}")
    lines.append(f"reps: {args.reps}  cap: {args.cap}s  workers: {args.workers}"
                 + ("  (dry-run)" if dry else ""))
    lines.append("records:")
    for label, bp, fp in zip(CLASS_LABELS, args.base, args.flip):
        lines.append(f"  {label}  base: {bp}  flip: {fp}")
    lines.append("")
    lines.append("base arm switch head (as build_text prepends to every entry text):")
    lines += [f"  {ln}" for ln in switch_head(base_arm).splitlines()]
    lines.append("flip arm switch head:")
    lines += [f"  {ln}" for ln in switch_head(flip_arm).splitlines()]
    return lines


def _fmt_reps(reps):
    return ",".join(f"{(c or 'harness-error')}/{t:.1f}s" for c, t in reps)


def import_driver(module_name, switches_text, cap):
    """Import test/corpus_driver.py fresh under MODULE_NAME with its
    SWITCH_SETTINGS baked to SWITCHES_TEXT (see module docstring). Restores
    sys.argv and MR_SWITCHES afterwards; the returned module keeps its own
    frozen globals regardless."""
    saved_argv, saved_switches = sys.argv, os.environ.get("MR_SWITCHES")
    sys.argv = ["corpus_driver.py", "", "999999", str(cap), SUITE]
    os.environ["MR_SWITCHES"] = switches_text
    try:
        return _module(module_name, DRIVER_PATH)
    finally:
        sys.argv = saved_argv
        if saved_switches is None:
            os.environ.pop("MR_SWITCHES", None)
        else:
            os.environ["MR_SWITCHES"] = saved_switches


def run_job(job, driver_of, cap):
    """One (entry, arm, rep) job: build the entry's text under ARM's driver
    and run it through that driver's own maxima_run -- the exact mechanics
    a real corpus run under that arm would use. Returns
    (entry_key, arm, rep, cls_or_None, wall, ok) -- ok is False only for a
    Python-level exception before/around maxima_run (a harness failure,
    not a Maxima timeout/error, which are themselves valid classes)."""
    entry, arm, rep = job
    driver = driver_of[arm]
    ts = time.time()
    try:
        text = driver.build_text(entry["f_text"], entry["var_text"],
                                 entry["e_text"], entry["e_text2"])
        out, timed_out = driver.maxima_run(text, cap)
        cls = None
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("CLASS "):
                cls = line[6:].strip()
                break
        if cls is None:
            cls = "timeout" if timed_out else "error"
        if cls not in driver.KNOWN_CLASSES:
            cls = "error"
        return (entry["key"], arm, rep, cls, time.time() - ts, True)
    except Exception:
        return (entry["key"], arm, rep, None, time.time() - ts, False)


def main(argv):
    args = parse_args(argv)
    base_arm, flip_arm = arm_dict(args.base), arm_dict(args.flip)
    check_arms(args.switch, base_arm, flip_arm)
    base_arm_text, flip_arm_text = rr.switches_text(base_arm), rr.switches_text(flip_arm)

    pass_classes = ab.driver_pass_classes()
    selections = {label: select_changed(bp, fp, pass_classes)
                 for label, bp, fp in zip(CLASS_LABELS, args.base, args.flip)}
    total_entries = sum(len(v) for v in selections.values())
    n_jobs = 2 * args.reps * total_entries

    header = build_header(args, base_arm_text, flip_arm_text, base_arm, flip_arm, args.dry_run)

    if args.dry_run:
        lines = list(header)
        lines.append("")
        for label in CLASS_LABELS:
            changed = selections[label]
            n_pf = sum(1 for _k, _a, _b, d in changed if d == "PASS->FAIL")
            n_fp = sum(1 for _k, _a, _b, d in changed if d == "FAIL->PASS")
            lines.append(f"=== {label}: selected {len(changed)} "
                         f"({n_pf} PASS->FAIL + {n_fp} FAIL->PASS) ===")
            for (rel, en), a, b, direction in changed:
                lines.append(f"  {direction:10s} {a[0]:<13} t={a[1]:.1f}s -> "
                             f"{b[0]:<13} t={b[1]:.1f}s  {rel} e{en}")
        lines.append("")
        lines.append(f"jobs: {n_jobs} (2 arms x {args.reps} reps x {total_entries} entries)")
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        print("\n".join(lines))
        return 0

    # --- real run ---
    d_base = import_driver("corpus_driver_base", base_arm_text, args.cap)
    d_flip = import_driver("corpus_driver_flip", flip_arm_text, args.cap)
    assert d_base.build_text("1", "x", "1").startswith(switch_head(base_arm)), \
        "base driver's build_text head does not match the recomputed base switch head"
    assert d_flip.build_text("1", "x", "1").startswith(switch_head(flip_arm)), \
        "flip driver's build_text head does not match the recomputed flip switch head"
    driver_of = {"base": d_base, "flip": d_flip}

    # Resolve every selected entry's file text once (arm-independent: the
    # corpus text does not depend on SWITCH_SETTINGS, only the head the
    # driver's own build_text prepends does).
    entries = []
    file_cache = {}
    for label in CLASS_LABELS:
        for (rel, en), a, b, direction in selections[label]:
            path = os.path.join(SUITE, rel)
            if path not in file_cache:
                file_cache[path] = d_base.extract_entries(path)
            file_entries, line_nos = file_cache[path]
            els = d_base.split_elements(file_entries[en - 1][1:-1])
            entries.append({
                "key": (label, rel, en), "label": label, "rel": rel, "n": en,
                "line": line_nos[en - 1], "base_cls": a[0], "base_t": a[1],
                "flip_cls": b[0], "flip_t": b[1], "direction": direction,
                "f_text": d_base.normalize_heads(els[0]), "var_text": els[1],
                "e_text": d_base.normalize_heads(els[3]),
                "e_text2": d_base.normalize_heads(els[4]) if len(els) == 5 else None,
            })

    jobs = []
    for rep in range(args.reps):
        for entry in entries:
            jobs.append((entry, "base", rep))
            jobs.append((entry, "flip", rep))

    t0 = time.time()
    reps_by_key = {e["key"]: {"base": [None] * args.reps, "flip": [None] * args.reps}
                  for e in entries}
    ok_count = fail_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for key, arm, rep, cls, wall, ok in pool.map(
                lambda j: run_job(j, driver_of, args.cap), jobs):
            reps_by_key[key][arm][rep] = (cls, wall)
            if ok:
                ok_count += 1
            else:
                fail_count += 1
    wall_total = time.time() - t0

    out_lines = list(header)
    out_lines.append("")
    counts = {label: {"selected": 0, "repro-flip-better": 0,
                      "repro-base-better": 0, "noise": 0} for label in CLASS_LABELS}
    entry_rows = {label: [] for label in CLASS_LABELS}
    for entry in entries:
        key = entry["key"]
        base_reps = reps_by_key[key]["base"]
        flip_reps = reps_by_key[key]["flip"]
        base_classes = [c for c, _t in base_reps]
        flip_classes = [c for c, _t in flip_reps]
        base_pass_stable = all(c in pass_classes for c in base_classes)
        base_fail_stable = all(c is not None and c not in pass_classes for c in base_classes)
        flip_pass_stable = all(c in pass_classes for c in flip_classes)
        flip_fail_stable = all(c is not None and c not in pass_classes for c in flip_classes)
        if flip_pass_stable and base_fail_stable:
            verdict = "repro-flip-better"
        elif base_pass_stable and flip_fail_stable:
            verdict = "repro-base-better"
        else:
            verdict = "noise"
        counts[entry["label"]]["selected"] += 1
        counts[entry["label"]][verdict] += 1
        entry_rows[entry["label"]].append(
            f"  {entry['direction']:10s} {entry['base_cls']:<13} t={entry['base_t']:.1f}s -> "
            f"{entry['flip_cls']:<13} t={entry['flip_t']:.1f}s  {entry['rel']} e{entry['n']}\n"
            f"    base: {_fmt_reps(base_reps)}\n"
            f"    flip: {_fmt_reps(flip_reps)}\n"
            f"    verdict: {verdict}")

    for label in CLASS_LABELS:
        out_lines.append(f"=== {label} entries ===")
        out_lines += entry_rows[label]

    out_lines.append("")
    out_lines.append("=== per-class summary ===")
    for label in CLASS_LABELS:
        c = counts[label]
        out_lines.append(f"{label}  selected={c['selected']}  "
                         f"repro-flip-better={c['repro-flip-better']}  "
                         f"repro-base-better={c['repro-base-better']}  "
                         f"noise={c['noise']}")

    out_lines.append("")
    out_lines.append("=== re-applied winner (noise-filtered) ===")
    base_pass_list, flip_pass_list = [], []
    for label in CLASS_LABELS:
        c = counts[label]
        base_pass_list.append(c["repro-base-better"])
        flip_pass_list.append(c["repro-flip-better"])
        out_lines.append(f"{label}  base_pass={c['repro-base-better']} "
                         f"({args.switch}={base_arm[args.switch]})  |  "
                         f"flip_pass={c['repro-flip-better']} "
                         f"({args.switch}={flip_arm[args.switch]})")
    value, reason = p5.winning_value(args.switch, base_arm[args.switch], flip_arm[args.switch],
                                     base_pass_list, flip_pass_list)
    winner_line = f"WINNER (noise-filtered) {args.switch}={value} ({reason})"
    out_lines.append(winner_line)

    out_lines.append("")
    out_lines.append(f"wall time: {wall_total:.1f}s")
    out_lines.append(f"Results: {ok_count} passed, {fail_count} failed")

    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out_lines) + "\n")
    print(winner_line)
    print(f"Results: {ok_count} passed, {fail_count} failed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
