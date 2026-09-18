#!/usr/bin/env python3
"""Regression guard for the P5 run tooling (matcher substrate plan 3):
test/run_records.py, test/p5_gate.py and the driver's switch plumbing.

No Maxima. Checks:
  1. the driver-side switch defaults equal the dispatcher's defmvar
     defaults (maxima_rubi_dispatch.lisp);
  2. switch_settings: defaults, one override, a malformed item rejected;
  3. record_switches / common_switches: one arm, a shard without the
     switches text, two arms;
  4. clear_stale_shards: removes the run's shard files only, and refuses
     while a pid of the previous run is alive;
  5. the driver (imported in a child with MR_RULES_CORE=0, so no core is
     built) states MR_SWITCHES on its header and assigns the switches
     ahead of the rubi call in every entry text; a bad MR_SWITCHES exits
     nonzero;
  6. winning_value: every-class win, tie, split; the mr_model_flags tie
     takes Maxima's defaults;
  7. gate on synthetic records: green, then a PASS-floor and a
     wall-ceiling failure;
  8. the driver's run_entry and the queue runner (test/run_corpus_queue.py),
     in a child on a synthetic suite with a stubbed maxima_run: main()'s
     result lines, run_entry's line, the queue order and subset, shards the
     merger reads (every entry once, one arm, the cap on the filter: line),
     a harness exception written as `error` and counted.

Re-runnable:  python3 test/test_run_records.py
"""

import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _module(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rr = _module("run_records")
gate_mod = _module("p5_gate")
passed = 0
failed = 0


def check(label, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"PASS: {label}")
    else:
        failed += 1
        print(f"FAIL: {label} {detail}")


def raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return True
    return False


# Derived, not spelled out: adding a switch must not silently leave these
# fixtures describing an arm the driver no longer writes. The literal text
# is pinned once, by the "driver header states the arm" check below.
DEFAULT_ARM = rr.switches_text(rr.SWITCH_DEFAULTS)


def record(path, rows, switches=DEFAULT_ARM):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("=== synthetic ===\n")
        fh.write("filter: '9 Test/'  full run  timeout: 30s"
                 + (f"  switches: {switches}" if switches else "") + "\n\n")
        for cls, t, rel, e in rows:
            fh.write(f"{cls:14s} t={t:6.1f}s {rel} e{e} L{e + 10}\n")


CHILD = r"""
import importlib.util, json, sys
sys.argv = ["corpus_driver.py", "1 Algebraic functions/", "1", "30"]
spec = importlib.util.spec_from_file_location("drv", DRIVER)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
print(json.dumps({"header": d.switch_header(),
                  "text": d.build_text("x^2", "x", "x^3/3")}))
"""


def child(switches):
    env = {k: v for k, v in os.environ.items() if k not in ("MR_SWITCHES", "MR_RULES_CORE_PATH")}
    env["MR_RULES_CORE"] = "0"
    if switches is not None:
        env["MR_SWITCHES"] = switches
    code = CHILD.replace("DRIVER", repr(os.path.join(HERE, "corpus_driver.py")))
    return subprocess.run([sys.executable, "-c", code], env=env, cwd=ROOT,
                          capture_output=True, text=True, timeout=60)


QUEUE_CHILD = r"""
import importlib.util, json, os, re, sys, tempfile
HERE = os.path.join(ROOTDIR, "test")
tmp = tempfile.mkdtemp(prefix="mr-queue-guard-")
suite = os.path.join(tmp, "suite")
os.makedirs(os.path.join(suite, "9 Test"))
with open(os.path.join(suite, "9 Test", "f.mac"), "w") as fh:
    fh.write("test9:[\n[x,x,1,x^2/2],\n[x^2,x,1,x^3/3],\n[x^3,x,1],\n[x^4,x,1,x^5/5]]$\n")
main_out = os.path.join(tmp, "main.out")
sys.argv = ["corpus_driver.py", "9 Test/", "999999", "30", suite, "0", "", "0", main_out]
spec = importlib.util.spec_from_file_location("drv", os.path.join(HERE, "corpus_driver.py"))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
def stub(text, timeout):
    if "mr_f: x$" in text:
        return "CLASS expected\n", False
    if "mr_f: x^2$" in text:
        return "CLASS verified\n", False
    return "", True
d.maxima_run = stub
d.build_info_lines = lambda: ["maxima: stub"]
d.main()
T = re.compile(r"t=\s*[\d.]+s")
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)")
def norm(line):
    return " ".join(T.sub("t=Ts", line).split())
main_lines = [norm(l) for l in open(main_out, encoding="utf-8") if RESULT.match(l)]
entries, line_nos = d.extract_entries(os.path.join(suite, "9 Test", "f.mac"))
entry_line = norm(d.run_entry("9 Test/f.mac", 1, entries[1], line_nos[1])[1])
qspec = importlib.util.spec_from_file_location("rcq", os.path.join(HERE, "run_corpus_queue.py"))
q = importlib.util.module_from_spec(qspec)
qspec.loader.exec_module(q)
rel = "9 Test/f.mac"
prev = {(rel, 4): ("timeout", 30.0), (rel, 1): ("expected", 0.1)}
order = [j[1] for j in q.build_jobs(d, prev)]
subset = [j[1] for j in q.build_jobs(d, None, {(rel, 2)})]
try:
    q.build_jobs(d, None, {(rel, 9)})
    missing_exits = False
except SystemExit:
    missing_exits = True
outs = [os.path.join(tmp, "corpus_class9.shard%02d.out" % k) for k in range(2)]
title = lambda k: "=== guard queue worker %02d ===" % k
detail = lambda k: "queue worker %02d of 2  timeout: 30s  entries: 4" % k
counts, failures, _w = q.run_queue(d, q.build_jobs(d, prev), 2, outs, title, detail,
                                   ["maxima: stub"], log=lambda m: None)
ALLOWED = ("=", "date:", "merge date:", "filter:", "head rewrites:", "maxima:", "total",
           "wall", "Results:", "SKIP")
queue_lines, unparsed = [], []
for p in outs:
    for l in open(p, encoding="utf-8"):
        l = l.rstrip("\n")
        if RESULT.match(l):
            queue_lines.append(norm(l))
        elif l.strip() and not re.match(r"^\S+\s+\d+$", l) and not l.startswith(ALLOWED):
            unparsed.append(l)
rspec = importlib.util.spec_from_file_location("rr", os.path.join(HERE, "run_records.py"))
rr = importlib.util.module_from_spec(rspec)
rspec.loader.exec_module(rr)
try:
    switches = rr.common_switches(outs)
except ValueError as exc:
    switches = "ERROR " + str(exc)
cap_ok = all(any(l.startswith("filter:") and "timeout: 30s" in l for l in open(p)) for p in outs)
def boom(text, timeout):
    if "mr_f: x^4$" in text:
        raise RuntimeError("guard: injected harness failure")
    return stub(text, timeout)
d.maxima_run = boom
outs2 = [os.path.join(tmp, "fail.shard%02d.out" % k) for k in range(2)]
_c, failures2, _w = q.run_queue(d, q.build_jobs(d, prev), 2, outs2, title, detail, [],
                                log=lambda m: None)
fail_lines = [norm(l) for p in outs2 for l in open(p) if RESULT.match(l) and " e4 " in l]
print(json.dumps({"main_lines": main_lines, "entry_line": entry_line, "order": order,
                  "subset": subset, "missing_exits": missing_exits,
                  "queue_lines": sorted(queue_lines), "unparsed": unparsed,
                  "switches": switches, "cap_ok": cap_ok, "counts": counts,
                  "failures": failures, "failures2": failures2, "fail_lines": fail_lines}))
"""


def queue_child():
    env = {k: v for k, v in os.environ.items() if k not in ("MR_SWITCHES", "MR_RULES_CORE_PATH")}
    env["MR_RULES_CORE"] = "0"
    code = QUEUE_CHILD.replace("ROOTDIR", repr(ROOT))
    return subprocess.run([sys.executable, "-c", code], env=env, cwd=ROOT,
                          capture_output=True, text=True, timeout=120)


def main():
    # 1. defaults in step with the dispatcher. Booleans are the Lisp nil/t;
    #    an integer switch (mr_max_depth) carries its literal (design 3.3).
    lisp = open(os.path.join(ROOT, "maxima_rubi_dispatch.lisp"), encoding="utf-8").read()
    defs = {m.group(1): {"t": "true", "nil": "false"}.get(m.group(2), m.group(2))
            for m in re.finditer(r"^\(defmvar \$(mr_\w+) (nil|t|\d+)\b", lisp, re.M)}
    check("driver switch defaults == dispatcher defmvar defaults",
          defs == rr.SWITCH_DEFAULTS, f"{defs} vs {rr.SWITCH_DEFAULTS}")
    check("mr_max_depth is the integer switch",
          rr.INT_SWITCHES == ("mr_max_depth",)
          and rr.valid_value("mr_max_depth", "16")
          and not rr.valid_value("mr_max_depth", "0")
          and not rr.valid_value("mr_max_depth", "true")
          and rr.valid_value("mr_nested_fallback", "false")
          and not rr.valid_value("mr_nested_fallback", "16"))
    check("an integer override is accepted, a bad one rejected",
          rr.switch_settings({"MR_SWITCHES": "mr_max_depth=32"})["mr_max_depth"] == "32"
          and raises(ValueError, rr.switch_settings, {"MR_SWITCHES": "mr_max_depth=-1"})
          and raises(ValueError, rr.switch_settings, {"MR_SWITCHES": "mr_max_depth=abc"}))

    # 2. switch_settings
    check("no MR_SWITCHES: the defaults", rr.switch_settings({}) == rr.SWITCH_DEFAULTS)
    s = rr.switch_settings({"MR_SWITCHES": "mr_model_flags=false"})
    check("one override", rr.switches_text(s)
          == DEFAULT_ARM.replace("mr_model_flags=true", "mr_model_flags=false"),
          rr.switches_text(s))
    check("a malformed item is rejected",
          raises(ValueError, rr.switch_settings, {"MR_SWITCHES": "mr_model_flags=0"})
          and raises(ValueError, rr.switch_settings, {"MR_SWITCHES": "mr_flatwide=true"}))

    with tempfile.TemporaryDirectory() as tmp:
        # 3. record_switches / common_switches
        a, b, c = (os.path.join(tmp, n) for n in ("a.out", "b.out", "c.out"))
        record(a, [("verified", 1.0, "9 Test/f.mac", 1)])
        record(b, [("verified", 1.0, "9 Test/f.mac", 2)], switches=None)
        record(c, [("verified", 1.0, "9 Test/f.mac", 3)],
               switches=rr.switches_text(
                   dict(rr.SWITCH_DEFAULTS, mr_flat_wide="true")))
        check("record_switches reads the arm", rr.record_switches(a) == DEFAULT_ARM)
        check("record_switches: None without the text", rr.record_switches(b) is None)
        check("common_switches: one arm", rr.common_switches([a, a]) == rr.record_switches(a))
        check("common_switches: a shard without switches is an error",
              raises(ValueError, rr.common_switches, [a, b]))
        check("common_switches: two arms are an error",
              raises(ValueError, rr.common_switches, [a, c]))

        # 4. clear_stale_shards (the .caps sidecars go with the shard files:
        #    a stale census would describe a run that never happened)
        names = ["corpus_class9.shard00.out", "corpus_class9.shard00.log",
                 "corpus_class9.shard01.files", "corpus_class9.shard00.caps",
                 "corpus_class9.shard-pids",
                 "corpus_class9.out", "corpus_class8.shard00.out"]
        for n in names:
            open(os.path.join(tmp, n), "w").close()
        removed = rr.clear_stale_shards(tmp, "class9")
        left = sorted(n for n in os.listdir(tmp) if n.startswith("corpus_"))
        check("clear_stale_shards removes the run's shard files only",
              removed == 5 and left == ["corpus_class8.shard00.out", "corpus_class9.out"],
              f"{removed} {left}")
        with open(os.path.join(tmp, "corpus_class9.shard-pids"), "w") as fh:
            fh.write(f"shard00 {os.getpid()} test/corpus_class9.shard00.out\n")
        check("clear_stale_shards refuses while a pid is alive",
              raises(RuntimeError, rr.clear_stale_shards, tmp, "class9"))

        # 7. gate on synthetic records
        rel = "9 Test/f.mac"
        p0 = os.path.join(tmp, "p0.out")
        record(p0, [("verified", 2.0, rel, 1), ("timeout", 30.0, rel, 2),
                    ("deferred", 1.0, rel, 3)], switches=None)
        good = os.path.join(tmp, "good.out")
        record(good, [("verified", 1.0, rel, 1), ("verified", 5.0, rel, 2),
                      ("error", 0.5, rel, 3)])
        slow = os.path.join(tmp, "slow.out")
        record(slow, [("verified", 9.0, rel, 1), ("timeout", 30.0, rel, 2),
                      ("deferred", 3.0, rel, 3)])
        worse = os.path.join(tmp, "worse.out")
        record(worse, [("unverified", 1.0, rel, 1), ("timeout", 30.0, rel, 2),
                       ("deferred", 1.0, rel, 3)])
        for path, want, label in ((good, 0, "gate green"), (slow, 1, "gate: wall ceiling fails"),
                                  (worse, 1, "gate: pass floor fails")):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = gate_mod.gate(p0, path)
            out = buf.getvalue()
            check(label, rc == want, out)
        buf = io.StringIO()
        with redirect_stdout(buf):
            gate_mod.gate(p0, good)
        check("gate lists a crash verdict new in the record",
              "INFO: crash (error) P0 0 -> new 1; error in new only: 1" in buf.getvalue()
              and "deferred      t=1.0s -> error t=0.5s 9 Test/f.mac e3" in buf.getvalue(),
              buf.getvalue())

    # 5. the driver's switch plumbing
    p = child("mr_cond_retry=false")
    try:
        got = json.loads(p.stdout.strip().splitlines()[-1])
    except (IndexError, ValueError):
        got = None
    check("driver header states the arm",
          got is not None and got["header"]
          == ("  switches: mr_flat_wide=false mr_cond_retry=false "
              "mr_model_flags=true mr_nested_fallback=false "
              "mr_giveup_last=true mr_max_depth=16"),
          f"{got} {p.stderr[-400:]}")
    check("entry text assigns the switches before the rubi call",
          got is not None and got["text"].startswith(
              "mr_flat_wide : false$\nmr_cond_retry : false$\nmr_model_flags : true$\n"
              "mr_nested_fallback : false$\nmr_giveup_last : true$\n"
              "mr_max_depth : 16$\n"
              "mr_depth_cap_hits : 0$\nmr_f: x^2$\n"),
          f"{got and got['text'][:200]!r}")
    check("the entry text prints the depth-cap count",
          got is not None and 'disp(concat("DEPTHCAP ", string(mr_depth_cap_hits)))'
          in got["text"], f"{got and got['text'][-200:]!r}")
    p = child("mr_cond_retry=off")
    check("a bad MR_SWITCHES exits nonzero naming it",
          p.returncode != 0 and "MR_SWITCHES" in p.stderr, f"{p.returncode} {p.stderr[-300:]!r}")

    # 6. winning_value
    wv = gate_mod.winning_value
    check("flip wins with more PASS in every class",
          wv("mr_flat_wide", "false", "true", [10, 5, 7], [11, 6, 8])[0] == "true")
    check("base wins with more PASS in every class",
          wv("mr_model_flags", "true", "false", [11, 6, 8], [10, 5, 7])[0] == "true")
    check("a tie keeps the documented default",
          wv("mr_cond_retry", "true", "false", [10, 5, 7], [10, 6, 8])[0] == "true")
    check("a split keeps the documented default",
          wv("mr_flat_wide", "false", "true", [10, 5, 7], [11, 4, 8])[0] == "false")
    check("mr_model_flags on a split takes Maxima's defaults",
          wv("mr_model_flags", "true", "false", [11, 5, 7], [10, 6, 8])[0] == "false")

    # 8. run_entry and the queue runner
    p = queue_child()
    try:
        g = json.loads(p.stdout.strip().splitlines()[-1])
    except (IndexError, ValueError):
        g = None
    err = p.stderr[-600:]
    want = ["expected t=Ts 9 Test/f.mac e1 L2", "verified t=Ts 9 Test/f.mac e2 L3",
            "error t=Ts 9 Test/f.mac e3 L4 bad-entry-shape(3)", "timeout t=Ts 9 Test/f.mac e4 L5"]
    check("driver main() writes its result lines through run_entry",
          g is not None and g["main_lines"] == want, f"{g and g['main_lines']} {err}")
    check("run_entry returns main's line", g is not None and g["entry_line"] == want[1],
          f"{g and g['entry_line']}")
    check("queue order: untimed entries first, then the longest previous time",
          g is not None and g["order"] == [1, 2, 3, 0], f"{g and g['order']}")
    check("queue subset: only the given keys; a key not in the section exits",
          g is not None and g["subset"] == [1] and g["missing_exits"],
          f"{g and (g['subset'], g['missing_exits'])}")
    check("queue shards: every entry once with main's line, merger-readable, one arm, the cap",
          g is not None and g["queue_lines"] == sorted(want) and not g["unparsed"]
          and g["switches"] == rr.switches_text(rr.SWITCH_DEFAULTS)
          and g["cap_ok"] and g["failures"] == 0, f"{g}")
    # build_units: the dispatch-unit size IS the tail bound (makespan >=
    # core-seconds/workers + largest unit), so the default must stay one
    # entry per unit — see build_units' docstring for the measurement.
    qmod = _module("run_corpus_queue")
    jobs = [("f", i, "t", i, c) for i, c in enumerate([10.0, 6.0, 5.0, 1.0])]
    check("build_units: job-seconds 0 is one entry per unit",
          [len(u) for u in qmod.build_units(jobs, 0)] == [1, 1, 1, 1])
    check("build_units: a unit closes once the estimate reaches the target",
          [[j[4] for j in u] for u in qmod.build_units(jobs, 11.0)]
          == [[10.0, 6.0], [5.0, 1.0]])
    check("build_units: an untimed entry is its own unit",
          [len(u) for u in qmod.build_units(
              [("f", 0, "t", 0, qmod.UNTIMED)] + jobs, 11.0)] == [1, 2, 2])
    check("queue: a harness exception is an error line and a counted failure",
          g is not None and g["failures2"] == 1
          and g["fail_lines"] == ["error t=Ts 9 Test/f.mac e4 L5"],
          f"{g and (g['failures2'], g['fail_lines'])}")

    print(f"Results: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
