#!/usr/bin/env python3
"""probes/corpus/27-class-ports-fixes-slice-ab.py -- one arm of the
class-ports-fixes slice A/B: run the selected corpus entries through
corpus_driver.run_entry (the queue runner's path) in ONE thread, one entry
at a time, and write a record in the driver's format.

The arm is the environment, as for every driver run: MR_RULES_CORE_PATH (a
pinned core) and MR_SWITCHES. Usage (repo root):

    python3 probes/corpus/27-class-ports-fixes-slice-ab.py OUT SELECT_OUT...

The selection: SLICE below (class 1 g12, the ticket-18 answer sites picked
by an atanh/asinh expected answer, controls) plus the EQQ / HIT lines of
probes/corpus/27-class-ports-fixes-slice-select.{eqq,hit}.out (EQQ thinned
per file). See probes/corpus/27-class-ports-fixes-slice-ab.run.
"""
import importlib.util
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DRIVER = os.path.join(ROOT, "test", "corpus_driver.py")
SUITE_REL = "reference/maxima-syntax-test-suite"

SLICE = [
    # (section, file-name stem, entry numbers)
    # EqQ/NeQ, class 1 g12 (NeQ[c d^2 - b d e + a e^2, 0] on a factorable
    # quadratic: 1_2_1_2 r107 divided by an expression that expands to 0);
    # the select probe's EQQ hits are added by load_extra
    ("1 Algebraic functions", "1.2.1.2 (d+e x)^m (a+b x+c x^2)^p",
     [1926, 1940, 1941, 2033, 2034, 2035, 2042, 2044, 2051, 2055]),
    # ticket 18: answers that were log-form shims (class-1 rules)
    ("1 Algebraic functions", "1.1.2.2 (c x)^m (a+b x^2)^p", [226, 228, 230, 235, 242]),
    ("1 Algebraic functions", "1.1.2.3 (a+b x^2)^p (c+d x^2)^q", [48, 50]),
    ("3 Logarithms", "3.1.4 (f x)^m (d+e x^r)^q (a+b log(c x^n))^p", [130, 131, 132, 133]),
    ("6 Hyperbolic functions", "6.7.1 Hyperbolic functions", [5, 7, 25]),
    # controls
    ("6 Hyperbolic functions", "6.1.5 Hyperbolic sine functions", [2, 3]),
    ("7 Inverse hyperbolic functions", "7.3.7 Inverse hyperbolic tangent functions", [1, 2, 3, 4]),
]
# at most this many EQQ hits per file, evenly spaced over the file's hits
# (1.2.1.2 alone has 319); every HIT line is taken
EQQ_PER_FILE = {"1.2.1.2 (d+e x)^m (a+b x+c x^2)^p": 14}
EQQ_DEFAULT = 8


def load_extra(paths):
    """{(section, file stem): {entries}} from the select probe's EQQ / HIT
    lines, EQQ hits thinned per EQQ_PER_FILE."""
    eqq, out = {}, {}
    for path in paths:
        for line in open(path, encoding="utf-8"):
            if not line.startswith(("EQQ ", "HIT ")):
                continue
            body = line[4:]
            i = body.index(".mac ")
            rel = body[:i + 4]
            ent = int(body[i + 5:].split()[0][1:])
            key = (rel.split("/")[0], rel.split("/")[-1][:-4])
            if line.startswith("EQQ "):
                eqq.setdefault(key, []).append(ent)
            else:
                out.setdefault(key, set()).add(ent)
    for key, ents in eqq.items():
        ents = sorted(set(ents))
        k = EQQ_PER_FILE.get(key[1], EQQ_DEFAULT)
        if len(ents) > k:
            ents = [ents[(j * len(ents)) // k] for j in range(k)]
        out.setdefault(key, set()).update(ents)
    return out


def load_driver(section, cap=30):
    saved = sys.argv
    sys.argv = [DRIVER, section + "/", "999999", str(cap), SUITE_REL]
    try:
        spec = importlib.util.spec_from_file_location("corpus_driver_" + str(abs(hash(section))), DRIVER)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.argv = saved
    return mod


def main(out_path, select_outs):
    os.chdir(ROOT)
    want = {}
    for section, stem, ents in SLICE:
        want.setdefault((section, stem), set()).update(ents)
    for k, v in load_extra(select_outs).items():
        want.setdefault(k, set()).update(v)
    sections = sorted({s for s, _ in want})
    lines, counts, t0 = [], {}, time.time()
    header = None
    for section in sections:
        drv = load_driver(section)
        if header is None:
            header = drv.header_lines("# class-ports-fixes slice A/B arm", "slice",
                                      drv.build_info_lines())
        for path, rel in drv.file_list():
            stem = os.path.basename(rel)[:-4]
            ents = want.pop((section, stem), None)
            if not ents:
                continue
            entries, line_nos = drv.extract_entries(path)
            for n in sorted(ents):
                cls, line, _caps = drv.run_entry(rel, n - 1, entries[n - 1], line_nos[n - 1])
                counts[cls] = counts.get(cls, 0) + 1
                lines.append(line)
                print(line, flush=True)
    if want:
        raise SystemExit("slice entries not found in the corpus: %r" % sorted(want))
    passed = sum(v for k, v in counts.items() if k in ("expected", "verified", "no-answer"))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(header + lines) + "\n")
        fh.write(f"\nwall time: {time.time() - t0:.1f}s\n"
                 f"Results: {passed} passed, {len(lines) - passed} failed\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
