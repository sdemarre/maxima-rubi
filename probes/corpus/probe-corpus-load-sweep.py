#!/usr/bin/env python3
"""Load-sweep the MaximaSyntaxTestSuite: for every .mac file, load it in a
fresh Maxima batch subprocess, collect per-file statistics, and for files
whose load is fatal (a Maxima Lisp error aborts the batch) locate the fatal
entries by fragment bisection.

Why per-file subprocesses: in Maxima (5.49-series dev build) a single Lisp
error aborts the entire -b batch run, so one fatal corpus entry would
otherwise hide all following files. Parse-time constant folding also runs on
quoted list elements: an entry whose text folds to a zero denominator
(e.g. (1+(-1)^(1/3)) with this build's real-root folding of (-1)^(1/3) -> -1)
kills the load of its whole file.

Output: one line per file, then a summary block. See the header comment
block we emit for the run stamp.
"""

import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

ROOT = "/home/serge/src/maxima-rubi"
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
MAXIMA_TIMEOUT = 300  # seconds per subprocess

STAT_RE = re.compile(r"^STAT (\d+) (\d+) (\d+) (\d+)$")

stats_file = os.path.join(tempfile.mkdtemp(prefix="maxima-rubi-sweep-"), "s.mac")
frag_dir = os.path.join(tempfile.mkdtemp(prefix="maxima-rubi-frag-"))


def maxima_run(mac_text, timeout=MAXIMA_TIMEOUT):
    open(stats_file, "w", encoding="utf-8").write(mac_text)
    try:
        r = subprocess.run(
            ["maxima", "--very-quiet", "-b", stats_file],
            capture_output=True, text=True, timeout=timeout, cwd=ROOT,
        )
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def stat_template(path):
    return (
        f'load("{path}")$\n'
        "nu1: 0;\n"
        "nu2: 0;\n"
        "bad: 0;\n"
        "for T in lst do block([e], e: part(T,4), "
        "if not freeof(Unintegrable, e) then nu1: nu1 + 1 "
        "else if not freeof(CannotIntegrate, e) then nu2: nu2 + 1 "
        "else nu2: nu2);\n"
        "for T in lst do block([k], k: part(T,3), "
        "if not (integerp(k) and k >= 0) then bad: bad + 1 else bad: bad);\n"
        'disp(concat("STAT ", string(length(lst)), " ", string(nu1), " ", '
        'string(nu2), " ", string(bad)));\n'
    )


def parse_stat(stdout):
    for line in stdout.splitlines():
        m = STAT_RE.match(line.strip())
        if m:
            return tuple(int(g) for g in m.groups())
    return None


def extract_entries(path):
    """Return (entries, line_nos): entry texts (brackets balanced, no
    trailing comma/$) and the 1-based source line number of each."""
    lines = open(path, encoding="utf-8").read().splitlines()
    entries, line_nos = [], []
    for i, l in enumerate(lines, 1):
        if l.strip().startswith("["):
            t = l.rstrip()
            if t.endswith("$"):
                t = t[:-1]
            if t.endswith(","):
                t = t[:-1]
            entries.append(t)
            line_nos.append(i)
    # in the well-formed corpus the last entry line also closes the list
    assert entries[-1].endswith("]]"), f"last entry of {path} does not close list"
    entries[-1] = entries[-1][:-1]
    return entries, line_nos


def frag_loads(entries_subset):
    frag = os.path.join(frag_dir, "f.mac")
    open(frag, "w", encoding="utf-8").write(
        "lst: '[\n" + ",\n".join(entries_subset) + "\n]\n$\n"
    )
    rc, out, _ = maxima_run(f'load("{frag}")$\ndisp("FRAGOK",length(lst))$\n')
    return "FRAGOK" in out


def fatal_report(path):
    """Bisect a fatal file down to its fatal entries.
    Returns (kind, detail): kind in {'entries', 'range', 'nonsingle', 'unparsed'}."""
    try:
        entries, line_nos = extract_entries(path)
    except (AssertionError, UnicodeDecodeError):
        return "unparsed", "entry extraction failed (not a single-list file?)"
    # sanity: full-set fragment must reproduce the fatality
    if frag_loads(entries):
        return "nonsingle", "reconstructed full fragment loads fine"
    lo, hi = 0, len(entries)
    while hi - lo > 1:
        mid = lo + (hi - lo) // 2
        if not frag_loads(entries[lo:mid]):
            hi = mid
        else:
            lo = mid
    found, line_found = [], []
    for i in range(lo, hi):
        if not frag_loads([entries[i]]):
            found.append(i + 1)
            line_found.append(line_nos[i])
    if found:
        return "entries", ",".join(f"{e}:{ln}" for e, ln in zip(found, line_found))
    return "range", (f"indices {lo + 1}..{hi}, lines {line_nos[lo]}..{line_nos[hi - 1]}")


def main():
    files = []
    for dirpath, _dirnames, filenames in os.walk(SUITE):
        for fn in filenames:
            if fn.endswith(".mac"):
                files.append(os.path.join(dirpath, fn))
    files.sort()
    # optional filter: substring matched against the suite-relative path
    if len(sys.argv) > 1:
        want = sys.argv[1]
        files = [p for p in files if want in os.path.relpath(p, SUITE)]

    out_lines = []
    out_lines.append("=== maxima-rubi corpus load sweep ===")
    out_lines.append(f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    rc, out, _ = maxima_run('disp(build_info());', timeout=120)
    for line in out.splitlines():
        line = line.strip()
        if line.startswith(("Maxima", "Lisp ", "Host ")):
            out_lines.append(f"maxima: {line}")
    out_lines.append(f"files: {len(files)}")
    out_lines.append("columns: status entries uni cannot badsteps [fatal entry lines]")

    n_ok = n_fatal = n_timeout = 0
    tot_entries = tot_uni = tot_cannot = tot_bad = 0
    t0 = time.time()
    for path in files:
        rel = os.path.relpath(path, SUITE)
        rc, out, err = maxima_run(stat_template(path))
        st = parse_stat(out)
        if st and rc == 0:
            n_ok += 1
            tot_entries += st[0]
            tot_uni += st[1]
            tot_cannot += st[2]
            tot_bad += st[3]
            out_lines.append(f"OK    entries={st[0]:4d} uni={st[1]:4d} "
                             f"cannot={st[2]:4d} badsteps={st[3]:3d}  {rel}")
        elif "timeout" in err:
            n_timeout += 1
            out_lines.append(f"TIMEO {rel}")
        else:
            n_fatal += 1
            kind, detail = fatal_report(path)
            out_lines.append(f"FATAL {rel} [{kind}] {detail}")
    dt = time.time() - t0

    out_lines.append("=== summary ===")
    out_lines.append(f"ok={n_ok} fatal={n_fatal} timeout={n_timeout} of {len(files)}")
    out_lines.append(f"total entries={tot_entries} Unintegrable={tot_uni} "
                     f"CannotIntegrate={tot_cannot} bad-steps={tot_bad}")
    out_lines.append(f"sweep wall time: {dt:.1f} s")

    text = "\n".join(out_lines) + "\n"
    print(text)
    out_path = os.path.join(ROOT, "probes", "corpus", "probe-corpus-load-sweep.out")
    open(out_path, "w", encoding="utf-8").write(text)


if __name__ == "__main__":
    main()
