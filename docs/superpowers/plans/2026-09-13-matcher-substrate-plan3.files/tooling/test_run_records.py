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
     wall-ceiling failure.

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


def record(path, rows, switches="mr_flat_wide=false mr_cond_retry=true mr_model_flags=true"):
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


def main():
    # 1. defaults in step with the dispatcher
    lisp = open(os.path.join(ROOT, "maxima_rubi_dispatch.lisp"), encoding="utf-8").read()
    defs = {m.group(1): ("true" if m.group(2) == "t" else "false")
            for m in re.finditer(r"^\(defmvar \$(mr_\w+) (nil|t)\b", lisp, re.M)}
    check("driver switch defaults == dispatcher defmvar defaults",
          defs == rr.SWITCH_DEFAULTS, f"{defs} vs {rr.SWITCH_DEFAULTS}")

    # 2. switch_settings
    check("no MR_SWITCHES: the defaults", rr.switch_settings({}) == rr.SWITCH_DEFAULTS)
    s = rr.switch_settings({"MR_SWITCHES": "mr_model_flags=false"})
    check("one override", rr.switches_text(s)
          == "mr_flat_wide=false mr_cond_retry=true mr_model_flags=false", rr.switches_text(s))
    check("a malformed item is rejected",
          raises(ValueError, rr.switch_settings, {"MR_SWITCHES": "mr_model_flags=0"})
          and raises(ValueError, rr.switch_settings, {"MR_SWITCHES": "mr_flatwide=true"}))

    with tempfile.TemporaryDirectory() as tmp:
        # 3. record_switches / common_switches
        a, b, c = (os.path.join(tmp, n) for n in ("a.out", "b.out", "c.out"))
        record(a, [("verified", 1.0, "9 Test/f.mac", 1)])
        record(b, [("verified", 1.0, "9 Test/f.mac", 2)], switches=None)
        record(c, [("verified", 1.0, "9 Test/f.mac", 3)],
               switches="mr_flat_wide=true mr_cond_retry=true mr_model_flags=true")
        check("record_switches reads the arm",
              rr.record_switches(a) == "mr_flat_wide=false mr_cond_retry=true mr_model_flags=true")
        check("record_switches: None without the text", rr.record_switches(b) is None)
        check("common_switches: one arm", rr.common_switches([a, a]) == rr.record_switches(a))
        check("common_switches: a shard without switches is an error",
              raises(ValueError, rr.common_switches, [a, b]))
        check("common_switches: two arms are an error",
              raises(ValueError, rr.common_switches, [a, c]))

        # 4. clear_stale_shards
        names = ["corpus_class9.shard00.out", "corpus_class9.shard00.log",
                 "corpus_class9.shard01.files", "corpus_class9.shard-pids",
                 "corpus_class9.out", "corpus_class8.shard00.out"]
        for n in names:
            open(os.path.join(tmp, n), "w").close()
        removed = rr.clear_stale_shards(tmp, "class9")
        left = sorted(n for n in os.listdir(tmp) if n.startswith("corpus_"))
        check("clear_stale_shards removes the run's shard files only",
              removed == 4 and left == ["corpus_class8.shard00.out", "corpus_class9.out"],
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
          == "  switches: mr_flat_wide=false mr_cond_retry=false mr_model_flags=true",
          f"{got} {p.stderr[-400:]}")
    check("entry text assigns the switches before the rubi call",
          got is not None and got["text"].startswith(
              "mr_flat_wide : false$\nmr_cond_retry : false$\nmr_model_flags : true$\nmr_f: x^2$\n"),
          f"{got and got['text'][:160]!r}")
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

    print(f"Results: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
