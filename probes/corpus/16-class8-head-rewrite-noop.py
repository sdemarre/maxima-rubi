#!/usr/bin/env python3
"""Class-8 Step 7 no-op check for the head rewrites, over EVERY entry (no
Maxima): the driver's normalize_heads() as of the class-8 port against the
same function at the class-ports base commit cd0a421, entry text by entry
text (integrand, primary and secondary expected answers -- the three
texts run_entry normalizes).

For each section it prints the entry count, how many normalized texts
differ between the two drivers, and the class-8 driver's rewrite totals.
The accepted sections (1, 2, 3, 6) must show 0 differences: the class-8
rows (arity-dispatched GAMMA/Ei, the six new heads, Psi and Derivative)
are then a measured no-op there, whatever the rule set does.

  sh probes/corpus/16-class8-head-rewrite-noop.run
"""
import importlib.util
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = "cd0a421"
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
SECTIONS = ["1 Algebraic functions", "2 Exponentials", "3 Logarithms",
            "4 Trig functions", "5 Inverse trig functions",
            "6 Hyperbolic functions", "7 Inverse hyperbolic functions",
            "8 Special functions"]
os.environ["MR_RULES_CORE"] = "0"


def load(path, name):
    argv = sys.argv[:]
    sys.argv = [argv[0]]
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.argv = argv
    return mod


new = load(os.path.join(ROOT, "test", "corpus_driver.py"), "drv_new")
old_src = subprocess.run(["git", "show", f"{BASE}:test/corpus_driver.py"],
                         cwd=ROOT, capture_output=True, text=True,
                         check=True).stdout
with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                 dir=os.path.join(ROOT, "test")) as fh:
    fh.write(old_src)
    old_path = fh.name
try:
    old = load(old_path, "drv_old")
finally:
    os.unlink(old_path)

print(f"head-rewrite no-op check: normalize_heads at {BASE} vs the working tree")
for sec in SECTIONS:
    n_entries = n_texts = n_diff = 0
    new.REWRITE_STATS.clear()
    examples = []
    for dirpath, _d, fns in os.walk(os.path.join(SUITE, sec)):
        for fn in sorted(fns):
            if not fn.endswith(".mac"):
                continue
            entries, _lines = new.extract_entries(os.path.join(dirpath, fn))
            for e in entries:
                n_entries += 1
                els = new.split_elements(e[1:-1])
                for k in (0, 3, 4):
                    if k < len(els):
                        n_texts += 1
                        a, b = old.normalize_heads(els[k]), new.normalize_heads(els[k])
                        if a != b:
                            n_diff += 1
                            if len(examples) < 2:
                                examples.append((fn, a[:70], b[:70]))
    stats = dict(sorted(new.REWRITE_STATS.items()))
    print(f"\n== {sec}: {n_entries} entries, {n_texts} texts, "
          f"{n_diff} differ from {BASE}")
    print(f"   class-8 driver rewrites: {stats or '{}'}")
    for fn, a, b in examples:
        print(f"   e.g. {fn}: {a!r}\n        -> {b!r}")
