#!/usr/bin/env python3
"""tracebatch.py ARM KEYS OUT [-j N] [--cap S] -- fa.py trace for every entry of KEYS
(rubi_verbose firings + answer), N at a time; blocks separated by blank lines."""
import sys, os, subprocess, concurrent.futures as cf
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
import fa
arm, keysf, out = sys.argv[1:4]
j = int(sys.argv[sys.argv.index("-j") + 1]) if "-j" in sys.argv else 1
cap = sys.argv[sys.argv.index("--cap") + 1] if "--cap" in sys.argv else "30"
def one(k):
    r = subprocess.run([sys.executable, os.path.join(H, "fa.py"), "trace", arm, k[0], str(k[1]), "--cap", cap],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    return r.stdout + "\n"
with open(out, "a") as fh, cf.ThreadPoolExecutor(j) as ex:
    for s in ex.map(one, fa.keys_of(keysf)):
        fh.write(s); fh.flush()
