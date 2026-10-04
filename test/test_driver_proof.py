#!/usr/bin/env python3
"""Regression guard: the corpus driver records HOW each answer was proved,
tries symbolic proof before the numeric check, and gives verification its
own CPU budget (.scratch/corpus-harness/issues/06; user decisions
2026-09-28).

The checker itself (test/mr_verify.mac) has its own Maxima suite,
test/test_mr_verify.mac. This guard covers the driver around it:

  classify (no Maxima) -- classify_entry reads the entry's output:
    ANSWERED <cpu>   rubi returned, after <cpu> seconds of CPU;
    NUMERIC <which> <outcome>
                     the numeric check of the self-diff (verified) or the
                     expected-diff (expected), printed BEFORE the symbolic
                     stages run, so it survives a kill;
    CLASS <class> / PROOF <tag>.
    A process killed after ANSWERED was killed while VERIFYING: it is not
    a rubi timeout. rubi over its own cap is a timeout even if it answered.
  header (no Maxima) -- the record's filter: line states the verification
    budget, and the merger carries it into the merged record.
  stage order (no Maxima but the last) -- MR_PROOF_STAGES reorders or
    narrows the checker's stages for a whole run (the rectform-last A/B,
    probes/verify-stages/08): the entry text assigns the list, the verify:
    field states it and the merger keeps it, an unknown or repeated stage
    name is refused; end to end, the first proving stage in the given order
    names the proof (within a phase: the chain stages of every residual run
    before the radcan family since the breadth-first order, so the witness
    orders two radcan-family stages).
  sidecar (no Maxima) -- the queue runner writes one `<tag> <label>` line
    per entry that reached the checker into the shard's .proof file.
  entry text (no Maxima) -- the rubi call line is unchanged, the ANSWERED
    marker and the checker's load come after it.
  end to end (Maxima) -- synthetic answers in place of the rubi call (the
    test_driver_radcan_fallback lesson: corpus witnesses rot):
      logarc      a symbolic proof by a stage the old chain never had;
      numeric     no symbolic stage proves it, the numeric check does;
      expected    the self-diff is not provable, the expected-diff is --
                  symbolic proof of either beats a numeric one;
      mismatch    a wrong answer;
      killed      verification runs past the process cap: the ANSWERED
                  and NUMERIC lines were flushed and the verdict reads
                  them.

Re-runnable:  python3 test/test_driver_proof.py
Exits nonzero if any check fails.
"""

import importlib.util
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _load(name, argv=None):
    real = sys.argv[:]
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


def _load_env(name, env):
    """_load with ENV set in os.environ for the import (the driver reads its
    knobs at import time), restored afterwards."""
    saved = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    try:
        return _load(name, ["corpus_driver.py", "ZZ no such section ZZ", "1", "30"])
    finally:
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


def classify_checks(drv):
    cap = drv.TIMEOUT

    def c(out, timed_out):
        r = drv.classify_entry(out, timed_out)
        return (r.cls, r.proof, r.rubi_cpu)

    check("classify: proved symbolically",
          c("ANSWERED 1.25\nNUMERIC verified ok\nCLASS verified\nPROOF logarc\n", False),
          ("verified", "logarc", 1.25))
    check("classify: rubi over its own cap is a timeout even if it answered",
          c(f"ANSWERED {cap + 0.5}\nCLASS verified\nPROOF chainA.1\n", False),
          ("timeout", None, cap + 0.5))
    check("classify: killed before ANSWERED is a rubi timeout",
          c("", True), ("timeout", None, None))
    check("classify: no ANSWERED and not killed is an error",
          c("some lisp error\n", False), ("error", None, None))
    check("classify: killed while verifying, numeric ok -> verified (numeric)",
          c("ANSWERED 2.0\nNUMERIC verified ok\n", True),
          ("verified", "numeric/verify-timeout", 2.0))
    check("classify: killed while verifying, expected-diff numeric ok -> expected",
          c("ANSWERED 2.0\nNUMERIC verified mismatch\nNUMERIC expected ok\n", True),
          ("expected", "numeric/verify-timeout", 2.0))
    check("classify: killed while verifying, nothing ok -> unverified",
          c("ANSWERED 2.0\nNUMERIC verified mismatch\n", True),
          ("unverified", "none/numeric-mismatch/verify-timeout", 2.0))
    check("classify: killed before any numeric line -> unverified",
          c("ANSWERED 2.0\n", True),
          ("unverified", "none/verify-timeout", 2.0))
    check("classify: a class that never reaches the checker has no proof",
          c("ANSWERED 0.4\nCLASS deferred\n", False),
          ("deferred", None, 0.4))
    check("classify_output keeps its (class, caps) shape",
          drv.classify_output("ANSWERED 1.0\nCLASS verified\nPROOF radcan\nDEPTHCAP 3\n", False),
          ("verified", 3))


def header_checks(drv):
    lines = drv.header_lines("T", "detail", [])
    flt = [l for l in lines if l.startswith("filter:")][0]
    check("header: the filter line states the verification budget",
          bool(re.search(rf"verify: {drv.VERIFY_CAP}s {drv.CAP_KIND}, "
                         rf"stage {drv.STAGE_CAP:g}s", flt)), True)
    check("header: the filter line states the timing mode, ending it "
          "(corpus-harness 11)", flt.endswith("  timing: printf-free+ms"), True)
    check("result line: t= carries milliseconds",
          drv.result_line("verified", 0.0123, "1 T/f.mac e1 L1"),
          "verified       t=  0.012s 1 T/f.mac e1 L1")


def merge_checks(drv):
    """merge_class_shards carries the verify: field into the merged record."""
    check("merge: the merged filter line keeps verify:",
          merge_filter_verify(drv, "30s cpu, stage 5s"), "30s cpu, stage 5s")


def merge_filter_verify(drv, verify):
    """The verify: field of the record merge_class_shards makes from two
    synthetic shards stating VERIFY, or the merger's output when it made
    none. The shards cover the REAL class-2 key set (the merger asserts
    completeness against the corpus), written into test/ under a name no
    run uses, and removed again."""
    real = open(os.path.join(HERE, "corpus_class2.pfs.out"), encoding="utf-8").read()
    flt = [l for l in real.splitlines() if l.startswith("filter:")][0]
    # The record predates later run switches (mr_ifold, 2026-10-02); the
    # mergers require the current switch list, so state the default arm.
    flt = re.sub(r"switches: .*$", "switches: " + drv.run_records.switches_text(
        drv.run_records.SWITCH_DEFAULTS), flt)
    flt += f"  verify: {verify}"
    suite = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
    rels = []
    for dirpath, _dn, names in os.walk(os.path.join(suite, "2 Exponentials")):
        for fn in names:
            if fn.endswith(".mac"):
                path = os.path.join(dirpath, fn)
                n = len(drv.extract_entries(path)[0])
                rel = os.path.relpath(path, suite)
                rels += [f"verified       t=   0.1s {rel} e{i} L{i}" for i in range(1, n + 1)]
    tag = f"tmp_proofguard_{os.getpid()}"
    shards = [os.path.join(HERE, f"{tag}.shard{k:02d}.out") for k in (0, 1)]
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "merged.out")
        try:
            for k, path in enumerate(shards):
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(f"=== w{k} ===\ndate: x\n{flt}\n\n")
                    fh.write("\n".join(rels[k::2]) + "\n")
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "merge_class_shards.py"),
                 "2 Exponentials", out, "test/corpus_driver.py", f"{tag}.shard*.out"],
                capture_output=True, text=True, cwd=ROOT)
            text = (open(out, encoding="utf-8").read() if os.path.exists(out)
                    else r.stdout + r.stderr)
        finally:
            for path in shards:
                if os.path.exists(path):
                    os.unlink(path)
    mflt = [l for l in text.splitlines() if l.startswith("filter:")]
    m = re.search(r"\bverify: (.*)$", mflt[0]) if mflt else None
    return m.group(1) if m else text


def stage_order_checks(drv):
    order = "logarc,radcan"
    sdrv = _load_env("corpus_driver", {"MR_PROOF_STAGES": order})
    text = sdrv.build_text("sin(x)", "x", "-cos(x)")
    check("stages: the entry text assigns the given order",
          'mr_proof_stages : ["logarc", "radcan"]$' in text, True)
    check("stages: the default run leaves the checker's own list alone",
          "mr_proof_stages :" in drv.build_text("sin(x)", "x", "-cos(x)"), False)
    lines = sdrv.header_lines("T", "detail", [])
    flt = [l for l in lines if l.startswith("filter:")][0]
    check("stages: the verify: field states the order",
          f"verify: {sdrv.VERIFY_CAP}s {sdrv.CAP_KIND}, stage {sdrv.STAGE_CAP:g}s, "
          f"stages {order}" in flt, True)
    for bad in ("logarc,nosuch", "logarc,logarc", ""):
        try:
            _load_env("corpus_driver", {"MR_PROOF_STAGES": bad})
            refused = False
        except SystemExit:
            refused = True
        check(f"stages: {bad!r} is refused", refused, True)
    check("stages: the merger keeps a stated order",
          merge_filter_verify(drv, "30s cpu, stage 5s, stages rectform,radcan"),
          "30s cpu, stage 5s, stages rectform,radcan")
    check("end to end: the first proving stage in the given order names the proof",
          _run(sdrv, "sin(x)", "-cos(x)", "-cos(x)"), ("verified", "logarc"))


def sidecar_checks(queue_mod):
    class Stub:
        PASS_CLASSES = {"verified"}
        FILTER = "x"

        def header_lines(self, title, detail, build):
            return [title, "filter: x", ""]

        def run_entry_detail(self, rel, idx, text, line_no):
            if idx == 0:
                return ("verified", f"verified       t=   0.1s {rel} e1 L{line_no}",
                        0, "logarc", {})
            return ("deferred", f"deferred       t=   0.1s {rel} e2 L{line_no}", 0, None,
                    {})

    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "corpus_class9.shard00.out")
        jobs = [("f.mac", 0, "[]", 7, 1.0), ("f.mac", 1, "[]", 8, 1.0)]
        queue_mod.run_queue(Stub(), jobs, 1, [out], lambda k: "T", lambda k: "D", [],
                            log=lambda m: None)
        proof = os.path.join(tmp, "corpus_class9.shard00.proof")
        text = open(proof).read() if os.path.exists(proof) else None
        check("sidecar: one <tag> <label> line per entry that reached the checker",
              text, "logarc f.mac e1 L7\n")


def text_checks(drv):
    text = drv.build_text("sin(x)", "x", "-cos(x)")
    call = "mr_r: rubi(mr_f, x)$"
    i_call = text.find(call)
    i_ans = text.find("ANSWERED")
    i_load = text.find('load("test/mr_verify.mac")')
    check("entry text: the rubi call line is unchanged", text.count(call), 1)
    check("entry text: ANSWERED and the checker's load come after the call",
          0 <= i_call < i_ans and i_call < i_load, True)


def _run(drv, f_text, answer, e_text, cap=120):
    text = drv.build_text(f_text, "x", e_text)
    text = text.replace("mr_r: rubi(mr_f, x)$", f"mr_r: {answer}$")
    out, timed_out = drv.maxima_run(text, cap)
    r = drv.classify_entry(out, timed_out)
    return (r.cls, r.proof)


def maxima_checks(drv):
    # d = %e^asinh(x)/sqrt(x^2+1) - 1 - x/sqrt(x^2+1): only logarc proves it
    check("end to end: a logarc proof",
          _run(drv, "1+x/sqrt(x^2+1)", "%e^asinh(x)", "x+sqrt(x^2+1)"),
          ("verified", "logarc"))
    # x*(li[2] reflection): the self-diff is the reflection formula
    refl = "x*(li[2](x)+li[2](1-x)+log(x)*log(1-x))"
    check("end to end: numeric only",
          _run(drv, "%pi^2/6", refl, "%pi^2*x/6"),
          ("verified", "numeric"))
    check("end to end: a symbolic expected-diff beats a numeric self-diff",
          _run(drv, "%pi^2/6", refl, refl),
          ("expected", "chainA.1"))
    # a corpus answer that fails to simplify (4.2.7 e80, 2026-09-28: `expt:
    # undefined: 0 to a negative exponent') must not take the entry down
    check("end to end: an expected answer that errors is skipped",
          _run(drv, "sin(x)", "-cos(x)", "x + 0^(-1)"),
          ("verified", "chainA.1"))
    check("end to end: a wrong answer",
          _run(drv, "sin(x)", "x^2", "-cos(x)"),
          ("unverified", "none/numeric-mismatch"))
    # verification that cannot finish inside a 5 s process cap: the stages
    # on the 120th power take ~16 s of CPU (measured 2026-09-28; the 60th
    # power took 3.05 s, too close to a cap to be a stable witness), and y, z
    # make the numeric check decline. ANSWERED and NUMERIC were flushed
    # before the kill.
    check("end to end: killed while verifying",
          _run(drv, "0", "(x+y+z+1)^120", "0", cap=5),
          ("unverified", "none/numeric-declined/verify-timeout"))


def main():
    drv = _load("corpus_driver", ["corpus_driver.py", "ZZ no such section ZZ", "1", "30"])
    queue_mod = _load("run_corpus_queue")
    classify_checks(drv)
    header_checks(drv)
    merge_checks(drv)
    stage_order_checks(drv)
    sidecar_checks(queue_mod)
    text_checks(drv)
    maxima_checks(drv)
    print(f"Results: {passed} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
