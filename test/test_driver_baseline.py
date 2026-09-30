#!/usr/bin/env python3
"""Regression guard: the corpus driver's native baseline mode (MR_BASELINE=1,
user decision 2026-09-30) -- stock Maxima's `integrate`, then `risch` when
integrate did not pass, through the driver's own cap and checker.

  header (no Maxima) -- the record states the arm `none (native
    integrate+risch baseline)`, which run_records reads back, and the
    verification budget; the old probe's arm still reads back too.
  entry text (no Maxima) -- the call is `integrate`/`risch`, no package
    switch or depth cap is touched, the no-answer noun is Maxima's
    `integrate` noun anywhere in the result.
  protocol (no Maxima; _run_once stubbed) -- risch runs exactly when
    integrate's class is a FAIL class other than `unexpected`; the record
    takes risch's verdict only when risch passes; the .via line names whose
    verdict it is and both runs.
  sidecar (no Maxima) -- the queue runner writes the .via line of every
    entry; the merger (test/merge_via.py) refuses an entry without one and a
    line that disagrees with the record.
  end to end (stock Maxima) --
      x^2                         integrate, proved symbolically;
      2*foo(x)+x                  integrate answers 2*'integrate(foo(x),x)
                                  + x^2/2, whose self-diff is exactly the
                                  integrand: contains-noun, NOT verified
                                  (the old probe's over-credit), and risch
                                  does no better;
      foo(x), expecting a marker  no-answer, risch not run.

Re-runnable:  python3 test/test_driver_baseline.py
Exits nonzero if any check fails.
"""

import importlib.util
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _load(name, argv=None, env=None):
    real = sys.argv[:]
    saved = {k: os.environ.get(k) for k in (env or {})}
    os.environ.update(env or {})
    if argv is not None:
        sys.argv = argv
    try:
        spec = importlib.util.spec_from_file_location(
            name, os.path.join(HERE, name + ".py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.argv = real
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


passed = 0
failures = []


def check(name, actual, expected):
    global passed
    if actual == expected:
        passed += 1
        print(f"PASS [{name}]")
    else:
        failures.append(name)
        print(f"FAIL [{name}]\n    expected: {expected!r}\n    actual:   {actual!r}")


def header_checks(drv):
    rr = drv.run_records
    line = drv.header_lines("T", "D", [])[-2]
    with tempfile.NamedTemporaryFile("w", suffix=".out", delete=False) as fh:
        fh.write(line + "\n")
    try:
        check("header: the arm reads back", rr.record_switches(fh.name),
              "none (native integrate+risch baseline)")
    finally:
        os.unlink(fh.name)
    check("header: the verification budget is stated",
          "verify: 30s cpu, stage 5s" in line, True)
    with tempfile.NamedTemporaryFile("w", suffix=".out", delete=False) as fh:
        fh.write(f"filter: 'x'  switches: {rr.BASELINE_ARM}\n")
    try:
        check("header: the old probe's arm still reads back",
              rr.record_switches(fh.name), rr.BASELINE_ARM)
    finally:
        os.unlink(fh.name)
    check("header: a .via shard file is a shard file",
          bool(rr.SHARD_FILE_RE.search("corpus_class2.baseline.shard03.via")), True)


def text_checks(drv):
    for name in ("integrate", "risch"):
        text = drv.build_text("sin(x)", "x", "-cos(x)", None, name)
        check(f"text: the call is {name}", f"mr_r: {name}(mr_f, x)$" in text, True)
        check(f"text ({name}): no package switch, no depth cap",
              any(w in text for w in ("mr_flat_wide", "mr_depth_cap_hits", "rubi(")),
              False)
        check(f"text ({name}): the integrate noun anywhere is no answer",
              "not is(freeof(integrate, mr_r))" in text, True)
    check("text: a package run is untouched by the integrator argument",
          drv.build_text("sin(x)", "x", "-cos(x)"),
          drv.build_text("sin(x)", "x", "-cos(x)", None, None))


def protocol_checks(drv):
    real = drv._run_once
    calls = []

    def case(integrate, risch):
        """Run one entry with the two runs stubbed to (class, tag)."""
        del calls[:]

        def stub(label, f, v, e, e2, integrator=None):
            calls.append(integrator)
            cls, tag = integrate if integrator == "integrate" else risch
            return (drv.EntryResult(cls, 0, tag, 0.5, ("5", "1"), ("A", "5", "1")),
                    (0.5 if integrator == "integrate" else 1.5))
        drv._run_once = stub
        try:
            cls, line, _caps, proof, sides = drv.run_entry_detail(
                "9 T/f.mac", 0, "[x,x,1,x^2/2]", 7)
            via = sides["via"]
        finally:
            drv._run_once = real
        return cls, line.split()[1:3], proof, via, list(calls)

    check("protocol: integrate passes, risch is not run",
          case(("verified", "radcan"), None),
          ("verified", ["t=", "0.5s"], "radcan",
           "integrate integrate=verified,0.5s,radcan risch=- 9 T/f.mac e1 L7",
           ["integrate"]))
    check("protocol: integrate fails, risch passes -- risch's verdict, time and tag",
          case(("timeout", None), ("verified", "numeric")),
          ("verified", ["t=", "1.5s"], "numeric",
           "risch integrate=timeout,0.5s,- risch=verified,1.5s,numeric 9 T/f.mac e1 L7",
           ["integrate", "risch"]))
    check("protocol: both fail -- integrate's verdict stays",
          case(("unverified", "none/numeric-mismatch"), ("deferred", None)),
          ("unverified", ["t=", "0.5s"], "none/numeric-mismatch",
           "integrate integrate=unverified,0.5s,none/numeric-mismatch "
           "risch=deferred,1.5s,- 9 T/f.mac e1 L7",
           ["integrate", "risch"]))
    for cls in sorted(drv.KNOWN_CLASSES):
        retry = cls not in drv.PASS_CLASSES and cls != "unexpected"
        check(f"protocol: integrate {cls} -> risch {'runs' if retry else 'does not run'}",
              case((cls, None), ("deferred", None))[4],
              ["integrate", "risch"] if retry else ["integrate"])


def sidecar_checks(drv, queue_mod, merge_via):
    class Stub:
        PASS_CLASSES = {"verified"}
        FILTER = "x"
        BASELINE = True

        def header_lines(self, title, detail, build):
            return [title, "filter: x", ""]

        def run_entry_detail(self, rel, idx, text, line_no):
            if idx == 0:
                return ("verified", f"verified       t=   0.1s {rel} e1 L{line_no}", 0,
                        "logarc", {"via": f"integrate integrate=verified,0.1s,logarc risch=- {rel} e1 L{line_no}"})
            return ("deferred", f"deferred       t=   0.1s {rel} e2 L{line_no}", 0, None,
                    {"via": f"integrate integrate=deferred,0.1s,- risch=deferred,0.2s,- {rel} e2 L{line_no}"})

    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "corpus_class9.baseline.shard00.out")
        jobs = [("f.mac", 0, "[]", 7, 1.0), ("f.mac", 1, "[]", 8, 1.0)]
        queue_mod.run_queue(Stub(), jobs, 1, [out], lambda k: "T", lambda k: "D", [],
                            log=lambda m: None)
        via = os.path.join(tmp, "corpus_class9.baseline.shard00.via")
        text = open(via).read() if os.path.exists(via) else None
        check("sidecar: one .via line per entry",
              text,
              "integrate integrate=verified,0.1s,logarc risch=- f.mac e1 L7\n"
              "integrate integrate=deferred,0.1s,- risch=deferred,0.2s,- f.mac e2 L8\n")
        census = os.path.join(tmp, "census.out")
        rc = merge_via.main([out, census, via])
        body = open(census).read() if rc == 0 else ""
        check("merger: a complete census is written",
              (rc, "verdict by integrate: 2  (PASS 1)" in body,
               "risch tried: 1  passed: 0" in body,
               "stage integrate logarc 1" in body,
               "  integrate verified symbolic: 1" in body),
              (0, True, True, True, True))
        open(via, "w").write("integrate integrate=verified,0.1s,logarc risch=- f.mac e1 L7\n")
        check("merger: an entry without a line is refused",
              _quiet(merge_via.main, [out, census, via]), 1)
        open(via, "w").write(
            "integrate integrate=verified,0.1s,logarc risch=- f.mac e1 L7\n"
            "risch integrate=deferred,0.1s,- risch=verified,0.2s,radcan f.mac e2 L8\n")
        check("merger: a line that disagrees with the record is refused",
              _quiet(merge_via.main, [out, census, via]), 1)


def _quiet(fn, argv):
    saved = sys.stderr
    sys.stderr = open(os.devnull, "w")
    try:
        return fn(argv)
    finally:
        sys.stderr.close()
        sys.stderr = saved


def maxima_checks(drv):
    def run(entry):
        cls, _line, _caps, proof, sides = drv.run_entry_detail("9 T/f.mac", 0, entry, 7)
        who, integ, risch = sides["via"].split()[:3]
        return (cls, proof, who, integ.split("=")[1].split(",")[0],
                risch.split("=")[1].split(",")[0])

    check("end to end: integrate, proved symbolically",
          run("[x^2,x,1,x^3/3]"), ("verified", "chainA.1", "integrate", "verified", "-"))
    check("end to end: an answer carrying the integrate noun is not verified",
          run("[2*foo(x)+x,x,1,x^2/2+2*bar(x)]"),
          ("contains-noun", None, "integrate", "contains-noun", "deferred"))
    check("end to end: a noun where the corpus expects none is no-answer",
          run("[foo(x),x,1,Unintegrable(foo(x),x)]"),
          ("no-answer", None, "integrate", "no-answer", "-"))


def main():
    argv = ["corpus_driver.py", "ZZ no such section ZZ", "1", "30"]
    drv = _load("corpus_driver", argv, {"MR_BASELINE": "1"})
    queue_mod = _load("run_corpus_queue")
    merge_via = _load("merge_via")
    check("mode: MR_BASELINE uses no rules core", (drv.BASELINE, drv.USE_RULES_CORE),
          (True, False))
    header_checks(drv)
    text_checks(drv)
    protocol_checks(drv)
    sidecar_checks(drv, queue_mod, merge_via)
    maxima_checks(drv)
    print(f"Results: {passed} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
