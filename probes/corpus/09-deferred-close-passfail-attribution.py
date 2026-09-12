#!/usr/bin/env python3
"""Probe 09 — class-3 deferred campaign close: per-entry attribution of the
record A/B PASS->FAIL transitions (docs/corpus-class3-deferred-uplift.md §5).

For each entry named by a chunk shard file (the driver's shard-file format,
one `idx skip 1` line per entry), run the driver's EXACT per-entry text
(test/corpus_driver.py build_text: the record harness — same zero chain,
same classification, same answers filler) on the core named by
MR_RULES_CORE_PATH, with two additions that cannot change the class:

  * `rubi_verbose : true$` prepended — %mr_dispatch prints one
    `rubi: rule <name> fired on <f>` line per pass-1 fire (top-level and
    nested mr_int dispatches), so the fired-rule sequence comes from the
    same run that produced the class. Pass-2/pass-3 fires run in Lisp and
    are NOT traced (an answer with an empty fire list fired there).
  * for noun-expected entries only (corpus answer Unintegrable /
    CannotIntegrate — driver classes no-answer / contains-noun /
    unexpected), the self-diff zero chain on the returned answer is
    appended AFTER the CLASS line, so an `unexpected` answer's correctness
    is measured (`self=1` closes, `self=0` does not close, `self=cut` the
    cap hit before it finished, `self=n/a` the answer is a noun).

One maxima subprocess at a time (sequential by construction).

Usage (from the repo root):
  MR_RULES_CORE_PATH=<core> python3 probes/corpus/09-deferred-close-passfail-attribution.py \
      <section> <shard-file> <out-file> [cap-seconds]

<section> is the corpus section ("3 Logarithms", "1 Algebraic functions",
"2 Exponentials"); cap defaults to 30 (the record cap).
"""

import importlib.util
import os
import re
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if len(sys.argv) < 4:
    raise SystemExit(__doc__)
SECTION, SHARD, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
CAP = int(sys.argv[4]) if len(sys.argv) > 4 else 30
SHARD = os.path.abspath(SHARD)
OUT = os.path.abspath(OUT)
if not os.environ.get("MR_RULES_CORE_PATH"):
    raise SystemExit("MR_RULES_CORE_PATH must name the core to measure")

# Import the driver as a module with the launcher's argv shape (filter,
# per-file, cap, suite-rel) so file_list() walks exactly the record's file
# order and the pinned core is resolved by the driver's own code.
os.chdir(ROOT)
DRIVER = os.path.join(ROOT, "test", "corpus_driver.py")
sys.argv = [DRIVER, SECTION + "/", "999999", str(CAP),
            "reference/maxima-syntax-test-suite"]
spec = importlib.util.spec_from_file_location("corpus_driver", DRIVER)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
assert d.USE_RULES_CORE and d.RULES_CORE_PIN, "pinned core not in use"

FILLER = "pos$\n" * 40 + "no$\n" * 20
NOUN = ("block([], if atom(mr_r) then 0 else "
        "if is(string(op(mr_r)) = \"integrate\") "
        "or is(string(op(mr_r)) = \"unintegrable\") "
        "then 1 else 0)")
FIRE_RX = re.compile(r"rubi: rule\s+(\S+)\s+fired on")


def entry_text(f_text, var_text, e_text, e_text2):
    t = d.build_text(f_text, var_text, e_text, e_text2)
    assert t.endswith(FILLER)
    if e_text.startswith(("Unintegrable", "CannotIntegrate")):
        zv = d.zero_chain(f"diff(mr_r, {var_text}) - mr_f", var_text)
        self_stmt = (f"if is({NOUN} = 1) then disp(concat(\"SELF n/a\")) "
                     f"else disp(concat(\"SELF \", string({zv})))$\n")
        t = t[:-len(FILLER)] + self_stmt + FILLER
    return "rubi_verbose : true$\n" + t


def main():
    files = d.file_list()
    specs = []
    for ln in open(SHARD):
        parts = ln.split()
        if parts:
            specs.append((int(parts[0]), int(parts[1]), int(parts[2])))
    stamp = open(d.RULES_CORE_STAMP).read().split("\n")
    fp = next((s.split()[1] for s in stamp if s.startswith("fingerprint ")),
              "?")
    head = [f"=== probe 09 — per-entry PASS->FAIL attribution "
            f"(section {SECTION!r}) ===",
            f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"]
    r = d.subprocess.run(["maxima", "--very-quiet", "--batch-string",
                          "disp(build_info());"],
                         capture_output=True, text=True, timeout=120)
    head += [f"maxima: {s.strip()}" for s in r.stdout.splitlines()
             if s.strip().startswith(("Maxima", "Lisp ", "Host "))]
    head += [f"core: {d.RULES_CORE}  fingerprint {fp}",
             f"shard: {SHARD}  entries: {len(specs)}  cap: {CAP}s", ""]
    outf = open(OUT, "w", encoding="utf-8")
    outf.write("\n".join(head) + "\n")
    outf.flush()
    counts = {}
    t0 = time.time()
    for idx, lo, per in specs:
        path, rel = files[idx]
        entries, line_nos = d.extract_entries(path)
        for k in range(lo, lo + per):
            els = d.split_elements(entries[k][1:-1])
            f_text = d.normalize_heads(els[0])
            var_text = els[1]
            e_text = d.normalize_heads(els[3])
            e_text2 = d.normalize_heads(els[4]) if len(els) == 5 else None
            ts = time.time()
            out, timed_out = d.maxima_run(
                entry_text(f_text, var_text, e_text, e_text2), CAP)
            dt = time.time() - ts
            cls = None
            selfv = "-"
            for s in out.splitlines():
                s = s.strip()
                if cls is None and s.startswith("CLASS "):
                    cls = s[6:].strip()
                elif s.startswith("SELF "):
                    selfv = s[5:].strip()
            if cls is None:
                cls = "timeout" if timed_out else "error"
            if cls not in d.KNOWN_CLASSES:
                cls = "error"
            if e_text.startswith(("Unintegrable", "CannotIntegrate")) \
                    and selfv == "-":
                selfv = "cut"
            fires = FIRE_RX.findall(out)
            seen = []
            for name in fires:
                if name not in seen:
                    seen.append(name)
            counts[cls] = counts.get(cls, 0) + 1
            line = (f"{cls:14s} t={dt:6.1f}s {rel} e{k + 1} L{line_nos[k]}"
                    f"  self={selfv}  nfires={len(fires)}"
                    f"  fires={','.join(seen[:20]) or '-'}"
                    + (",..." if len(seen) > 20 else ""))
            outf.write(line + "\n")
            outf.flush()
            pf = "PASS" if cls in d.PASS_CLASSES else "FAIL"
            print(f"{pf}: {line}", flush=True)
    total = sum(counts.values())
    passed = sum(v for c, v in counts.items() if c in d.PASS_CLASSES)
    tail = ["", "=== summary ==="]
    tail += [f"{c:14s} {counts[c]}" for c in sorted(counts)]
    tail += [f"total integrals: {total}",
             f"wall time: {time.time() - t0:.1f}s",
             f"Results: {passed} passed, {total - passed} failed"]
    outf.write("\n".join(tail) + "\n")
    outf.close()
    print("\n".join(tail))


if __name__ == "__main__":
    main()
