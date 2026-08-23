#!/usr/bin/env python3
"""Layer B: run the maxima-rubi package over the class-1 corpus, one fresh
Maxima subprocess per integral (the T3 probe-integrate-sample mechanics
with `rubi` in place of `integrate`).

Per-integral classification (one result line per integral in the .out,
one PASS:/FAIL: line on stdout):
  expected     answer; candidate - corpus expectation is zero-derivative
               within the zero-test chain
  verified     answer; diff(candidate, x) - integrand is zero within the
               chain, but candidate does not match the corpus expectation
  unverified   answer; neither zero-test closed within the chain
  no-answer    rubi returned a no-answer noun (the integrate fall-through
               or the package unintegrable noun); corpus also expects a noun
  unexpected   rubi returned an answer; corpus expects a noun
  error        subprocess died (Lisp error, parse-time fatality, or a
               missing CLASS line)
  timeout      per-process wall cap

Pass/fail mapping (T5 section 3): expected / verified / no-answer -> PASS;
unverified / unexpected / error / timeout -> FAIL.

The .out result line keeps the T3 shape
    <class>  t=<s>s <relpath> e<entry> L<line>
so the shard/resume line format carries over; the driver additionally
streams PASS:/FAIL: on stdout and ends with a `Results:` line.

Usage:
  corpus_class1_driver.py [filter] [per-file] [timeout] [suite-dir]
      [start-index] [append] [skip-first] [out-file] [stop-index]

Defaults: the whole "1 Algebraic functions/" section, 5 entries per file,
30 s per-integral cap.
"""

import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
SECTION = "1 Algebraic functions"
PRELOAD = os.path.join("test", "mr_preload.mac")

FILTER = sys.argv[1] if len(sys.argv) > 1 else SECTION + "/"
PER_FILE = int(sys.argv[2]) if len(sys.argv) > 2 else 5
TIMEOUT = int(sys.argv[3]) if len(sys.argv) > 3 else 30
SUITE_DIR = sys.argv[4] if len(sys.argv) > 4 else SUITE
START_INDEX = int(sys.argv[5]) if len(sys.argv) > 5 else 0
APPEND = len(sys.argv) > 6 and sys.argv[6] == "append"
SKIP_FIRST = int(sys.argv[7]) if len(sys.argv) > 7 else 0
OUT_FILE = sys.argv[8] if len(sys.argv) > 8 else None
STOP_INDEX = int(sys.argv[9]) if len(sys.argv) > 9 else None

KNOWN_CLASSES = {
    "expected", "verified", "unverified",
    "no-answer", "unexpected", "error", "timeout",
}
PASS_CLASSES = {"expected", "verified", "no-answer"}

workdir = tempfile.mkdtemp(prefix="maxima-rubi-corpus-")
mac_file = os.path.join(workdir, "i.mac")


def maxima_run(mac_text, timeout):
    open(mac_file, "w", encoding="utf-8").write(mac_text)
    try:
        r = subprocess.run(
            ["maxima", "--very-quiet", "-X", "--tls-limit 100000",
             "-p", PRELOAD, "-b", mac_file],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, timeout=timeout, cwd=ROOT,
        )
        return r.stdout, False
    except subprocess.TimeoutExpired as e:
        out = e.stdout
        if isinstance(out, bytes):
            out = out.decode("utf-8", "replace")
        return out or "", True


def split_elements(entry_text):
    """Depth-aware split at top-level commas; keeps all delimiters."""
    parts, depth, cur = [], 0, ""
    for ch in entry_text:
        if ch in "[(":
            depth += 1
        elif ch in "])":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts]


def extract_entries(path):
    """Entry texts (outer brackets, no trailing comma/$) + source line numbers."""
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
    assert entries and entries[-1].endswith("]]"), path
    entries[-1] = entries[-1][:-1]
    return entries, line_nos


def zero_chain(d_expr):
    """Statement list whose value is 1 iff the zero-test closes."""
    return (
        f"MR_d: ratsimp({d_expr}), if is(MR_d=0) then 1 "
        "else (MR_d: ratsimp(expand(MR_d)), if is(MR_d=0) then 1 "
        "else (MR_d: factor(MR_d), if is(MR_d=0) then 1 "
        "else (MR_d: ratsimp(factor(MR_d)), if is(MR_d=0) then 1 else 0)))"
    )


def build_text(f_text, var_text, e_text, e_text2=None):
    # mr_/MR_ template variables: the pasted corpus text is re-parsed in
    # their scope, so the names must not collide with corpus symbols.
    # Noun detector: the rubi fall-through is the integrate noun; the
    # package's explicit no-answer noun is `unintegrable`.
    noun = ("block([], if atom(mr_r) then 0 else "
            "if is(string(op(mr_r)) = \"integrate\") "
            "or is(string(op(mr_r)) = \"unintegrable\") "
            "then 1 else 0)")
    head = (f"mr_f: {f_text}$\n"
            f"mr_r: rubi(mr_f, {var_text})$\n"
            + "pos$\n" * 6 + "no$\n" * 6)
    if e_text.startswith(("Unintegrable", "CannotIntegrate")):
        body = (f"if is({noun} = 1) then disp(concat(\"CLASS no-answer\")) "
                f"else disp(concat(\"CLASS unexpected\"))")
    else:
        ze = zero_chain(f"diff(mr_r - {e_text}, {var_text})")
        zv = zero_chain(f"diff(mr_r, {var_text}) - mr_f")
        if e_text2 is not None:
            ze2 = zero_chain(f"diff(mr_r - {e_text2}, {var_text})")
            body = (f"if is({noun} = 1) then disp(concat(\"CLASS no-answer\")) "
                    "else block([MR_z, MR_z2, MR_w], MR_z: (" + ze + "), "
                    "MR_z2: (" + ze2 + "), "
                    "if is(MR_z=1) or is(MR_z2=1) "
                    "then disp(concat(\"CLASS expected\")) "
                    "else (MR_w: (" + zv + "), "
                    "if is(MR_w=1) then disp(concat(\"CLASS verified\")) "
                    "else disp(concat(\"CLASS unverified\"))))")
        else:
            body = (f"if is({noun} = 1) then disp(concat(\"CLASS no-answer\")) "
                    "else block([MR_z, MR_w], MR_z: (" + ze + "), "
                    "if is(MR_z=1) then disp(concat(\"CLASS expected\")) "
                    "else (MR_w: (" + zv + "), "
                    "if is(MR_w=1) then disp(concat(\"CLASS verified\")) "
                    "else disp(concat(\"CLASS unverified\"))))")
    return head + body + "$\n" + "pos$\n" * 6 + "no$\n" * 6


def file_list():
    """Sorted (path, relpath) of every .mac matching FILTER."""
    if SUITE_DIR == SUITE:
        walk_root = os.path.join(SUITE, SECTION)
        rel_root = SUITE
    else:
        walk_root = SUITE_DIR
        rel_root = SUITE_DIR
    files = []
    for dirpath, _dn, filenames in os.walk(walk_root):
        for fn in filenames:
            if fn.endswith(".mac"):
                p = os.path.join(dirpath, fn)
                rel = os.path.relpath(p, rel_root)
                if FILTER in rel:
                    files.append((p, rel))
    files.sort(key=lambda t: t[1])
    return files


def main():
    files = file_list()[START_INDEX:STOP_INDEX]

    out_lines = [
        ("=== maxima-rubi class-1 corpus driver (phase 2, "
         f"resume at file index {START_INDEX}) ==="
         if APPEND else
         "=== maxima-rubi class-1 corpus driver ==="),
        f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
    ]
    if not APPEND:
        r = subprocess.run(
            ["maxima", "--very-quiet", "--batch-string",
             "disp(build_info());"],
            capture_output=True, text=True, timeout=120, cwd=ROOT,
        )
        for line in r.stdout.splitlines():
            line = line.strip()
            if line.startswith(("Maxima", "Lisp ", "Host ")):
                out_lines.append(f"maxima: {line}")
    out_lines.append(f"filter: {FILTER!r}  per-file: {PER_FILE}  "
                     f"timeout: {TIMEOUT}s")
    out_lines.append("")

    counts = {}
    t0 = time.time()
    out_path = (OUT_FILE or os.path.join(ROOT, "test",
                                         "corpus_class1_driver.out"))
    outf = open(out_path, "a" if APPEND else "w", encoding="utf-8")
    outf.write("\n".join(out_lines) + "\n")
    outf.flush()
    for fi, (path, rel) in enumerate(files):
        try:
            entries, line_nos = extract_entries(path)
        except (AssertionError, UnicodeDecodeError, IndexError):
            out_lines.append(f"SKIP-BADFILE {rel}")
            continue
        lo = SKIP_FIRST if (fi == 0 and APPEND) else 0
        for idx in range(lo, min(PER_FILE, len(entries))):
            els = split_elements(entries[idx][1:-1])
            label = f"{rel} e{idx + 1} L{line_nos[idx]}"
            if len(els) not in (4, 5):
                cls = "error"
                counts[cls] = counts.get(cls, 0) + 1
                line = f"{'error':14s} t=0.0s {label} bad-entry-shape({len(els)})"
                out_lines.append(line)
                outf.write(line + "\n")
                outf.flush()
                print(f"FAIL: {line}")
                continue
            f_text, var_text, _steps, e_text = els[0], els[1], els[2], els[3]
            e_text2 = els[4] if len(els) == 5 else None
            t_start = time.time()
            out, timed_out = maxima_run(
                build_text(f_text, var_text, e_text, e_text2), TIMEOUT)
            dt = time.time() - t_start
            cls = None
            for line in out.splitlines():
                line = line.strip()
                if line.startswith("CLASS "):
                    cls = line[6:].strip()
                    break
            if cls is None:
                cls = "timeout" if timed_out else "error"
            if cls not in KNOWN_CLASSES:
                cls = "error"
            counts[cls] = counts.get(cls, 0) + 1
            pf = "PASS" if cls in PASS_CLASSES else "FAIL"
            line = f"{cls:14s} t={dt:6.1f}s {label}"
            out_lines.append(line)
            outf.write(line + "\n")
            outf.flush()
            print(f"{pf}: {line}")
    total = sum(counts.values())
    passed = sum(v for k, v in counts.items() if k in PASS_CLASSES)
    failed = total - passed

    out_lines.append("")
    out_lines.append("=== summary ===")
    for k in sorted(counts):
        out_lines.append(f"{k:14s} {counts[k]}")
    out_lines.append(f"total integrals: {total}")
    out_lines.append(f"wall time: {time.time() - t0:.1f}s")
    out_lines.append(f"Results: {passed} passed, {failed} failed")

    outf.write("\n".join(out_lines[out_lines.index("=== summary ==="):]) + "\n")
    outf.close()
    print("\n".join(out_lines[-8:]) + "\n")


if __name__ == "__main__":
    main()
