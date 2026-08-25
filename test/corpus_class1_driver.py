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
    "expected", "verified", "unverified", "contains-noun",
    "no-answer", "unexpected", "error", "timeout",
}
PASS_CLASSES = {"expected", "verified", "no-answer"}

workdir = tempfile.mkdtemp(prefix="maxima-rubi-corpus-")
mac_file = os.path.join(workdir, "i.mac")


def maxima_run(mac_text, timeout):
    # A unique per-call file (mkstemp) so parallel canary workers don't
    # clobber each other's batch; the driver's sequential use is unaffected.
    fd, fpath = tempfile.mkstemp(prefix="mr-", suffix=".mac", dir=workdir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(mac_text)
        r = subprocess.run(
            ["maxima", "--very-quiet", "-X", "--tls-limit 100000",
             "-p", PRELOAD, "-b", fpath],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, timeout=timeout, cwd=ROOT,
        )
        return r.stdout, False
    except subprocess.TimeoutExpired as e:
        out = e.stdout
        if isinstance(out, bytes):
            out = out.decode("utf-8", "replace")
        return out or "", True
    finally:
        try:
            os.unlink(fpath)
        except OSError:
            pass


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
    """Statement list whose value is 1 iff the zero-test closes.

    The whole chain is errcatch'd: a ratsimp/factor crash inside the
    VERIFICATION (measured 2026-08-24: `quotient' by `zero' on 1.2.2.4
    e165 / 1.2.2.8 e1) is an unverified zero-test, not a subprocess
    fatality — without the guard the error kills Maxima before the CLASS
    line and the entry is misclassified `error`. errcatch in this build
    returns [value] on success and [] on error (probe-errcatch-semantics).

    Stage order (measured 2026-08-25, 5.50.0/SBCL): TWO full chains —
    factor-first, then ratsimp-first — because closure is ORDER-
    DEPENDENT and no single order is uniformly cheap:
      - radical diffs (correct package answer): factor closes in ~2 s,
        ratsimp hangs >50 s (1.2.2.7 e1);
      - 1.2.2.3 e1's expected-diff: factor-first chain = 47 s,
        ratsimp-first chain = 9 s;
      - 1.2.2.4 e165's self-diff closes only under the ratsimp-first
        order (ratsimp(expand(ratsimp(D))) = 0; the same stages after a
        leading factor do not close).
    Each chain keeps the errcatch-crash semantics; a crash in either
    chain is an unverified zero-test, not a fatality. The canary cap
    is 60 s (test/canary.py) to hold both chains.
    """
    inner = (
        f"MR_d: factor({d_expr}), if is(MR_d=0) then 1 "
        "else (MR_d: ratsimp(MR_d), if is(MR_d=0) then 1 "
        "else (MR_d: ratsimp(expand(MR_d)), if is(MR_d=0) then 1 "
        "else (MR_d: ratsimp(factor(MR_d)), if is(MR_d=0) then 1 "
        "else (MR_d: ratsimp(" + d_expr + "), if is(MR_d=0) then 1 "
        "else (MR_d: ratsimp(expand(MR_d)), if is(MR_d=0) then 1 "
        "else (MR_d: factor(MR_d), if is(MR_d=0) then 1 "
        "else (MR_d: ratsimp(factor(MR_d)), if is(MR_d=0) then 1 else 0)))))))"
    )
    return (
        "block([MR_zr], MR_zr : errcatch(" + inner + "), "
        "if MR_zr = [] then 0 else part(MR_zr, 1))"
    )


def build_text(f_text, var_text, e_text, e_text2=None):
    # mr_/MR_ template variables: the pasted corpus text is re-parsed in
    # their scope, so the names must not collide with corpus symbols.
    # Noun detector: the rubi fall-through is the integrate noun; the
    # package's explicit no-answer noun is `unintegrable`.
    # Default mode is rules-only (2-arg rubi — a 0-firing top level is
    # the fast no-answer noun, the Step-2 gap list); MR_FALLBACK=1
    # restores the status-quo top-level integrate fall-through (A/B
    # baseline runs). Maxima has no arity overloading, so the fallback
    # mode is the distinct entry rubi_fallback (utils file, measured
    # 2026-08-24).
    if os.environ.get("MR_FALLBACK") == "1":
        call = f"rubi_fallback(mr_f, {var_text}, true)"
    else:
        call = f"rubi(mr_f, {var_text})"
    noun = ("block([], if atom(mr_r) then 0 else "
            "if is(string(op(mr_r)) = \"integrate\") "
            "or is(string(op(mr_r)) = \"unintegrable\") "
            "then 1 else 0)")
    # Contains-noun sub-classification: an answer that CONTAINS Rubi's
    # CannotIntegrate marker (port: the `unintegrable` subscript noun —
    # 1.1.1.4.m:47 and the sibling family catch-alls port it faithfully;
    # Rubi 4 itself returns the inert Int there, so the cascade result
    # legitimately carries it) or a native `integrate` noun somewhere in
    # its interior. diff() evaluates such heads to 0, so the zero chains
    # can never verify the answer — an honest FAIL sub-class, not an
    # unexplained `unverified`. The check is one freeof() call (cheap)
    # and runs BEFORE the zero chains, which would otherwise burn the
    # whole per-target budget on a noun-laden diff (measured 2026-08-25:
    # 1.1.1.7 e30). Only the `unintegrable` marker is poison: an
    # `integrate[g, x]` head inside an answer is a LEGITIMATE explicit
    # integral term — Maxima's diff knows d/dx ∫g dx = g, so such
    # answers verify normally (measured: 1.2.2.7 e1 carries a ∫-term
    # and its self-diff closes).
    has_noun = "not is(freeof(unintegrable, mr_r))"
    head = (f"mr_f: {f_text}$\n"
            f"mr_r: {call}$\n"
            + "pos$\n" * 6 + "no$\n" * 6)
    if e_text.startswith(("Unintegrable", "CannotIntegrate")):
        body = (f"if is({noun} = 1) then disp(concat(\"CLASS no-answer\")) "
                f"else disp(concat(\"CLASS unexpected\"))")
    else:
        # The corpus expected text is inlined into the subtraction and MUST
        # be parenthesized: an expected answer that is a SUM `A + B` would
        # otherwise parse as `mr_r - A + B` (the sign of every term after
        # the first is flipped), so a correct antiderivative fails the
        # zero-test and is misclassified `unverified` (measured 2026-08-24
        # on 1.3.2 e1: `mr_r - <e>` residual nonzero, `mr_r - (<e>)` zero).
        # The SELF-diff (zv) is checked FIRST: for a correct answer it
        # closes on the cheap factor stage, and a non-closing expected-
        # diff (the package's right answer in a different radical form)
        # would otherwise burn the whole per-target budget and starve
        # the self-diff (measured 2026-08-25: 1.1.2.4 e983 / 1.1.4.2
        # e182, both numerically correct, timed out under ze-first).
        # "verified" and "expected" are both PASS classes, so the
        # reordering is classification-safe.
        ze = zero_chain(f"diff(mr_r - ({e_text}), {var_text})")
        zv = zero_chain(f"diff(mr_r, {var_text}) - mr_f")
        if e_text2 is not None:
            ze2 = zero_chain(f"diff(mr_r - ({e_text2}), {var_text})")
            body = (f"if is({noun} = 1) then disp(concat(\"CLASS no-answer\")) "
                    f"else if is({has_noun}) then disp(concat(\"CLASS contains-noun\")) "
                    "else block([MR_z, MR_z2, MR_w], MR_w: (" + zv + "), "
                    "if is(MR_w=1) then disp(concat(\"CLASS verified\")) "
                    "else (MR_z: (" + ze + "), MR_z2: (" + ze2 + "), "
                    "if is(MR_z=1) or is(MR_z2=1) "
                    "then disp(concat(\"CLASS expected\")) "
                    "else disp(concat(\"CLASS unverified\"))))")
        else:
            body = (f"if is({noun} = 1) then disp(concat(\"CLASS no-answer\")) "
                    f"else if is({has_noun}) then disp(concat(\"CLASS contains-noun\")) "
                    "else block([MR_z, MR_w], MR_w: (" + zv + "), "
                    "if is(MR_w=1) then disp(concat(\"CLASS verified\")) "
                    "else (MR_z: (" + ze + "), "
                    "if is(MR_z=1) then disp(concat(\"CLASS expected\")) "
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
        lo = SKIP_FIRST if fi == 0 else 0
        hi = min(lo + PER_FILE, len(entries))
        for idx in range(lo, hi):
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
