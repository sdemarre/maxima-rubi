#!/usr/bin/env python3
"""Baseline: run today's Maxima `integrate` over a sample of the algebraic
corpus section, one fresh Maxima subprocess per integral.

Why one subprocess per integral:
  * a single -b batch dies on the first Lisp error, so one fatal corpus
    entry (parse-time constant folding, see probe-corpus-load-sweep) would
    hide every following entry;
  * a per-process wall-clock cap is the per-integral timeout;
  * no shared state, so Maxima flags/options cannot leak between tests.

Per-integral classification (one CLASS line per integral on stdout):
  expected     answer; candidate - corpus expectation has zero derivative
               (equal up to a constant) within the zero-test chain
  verified     answer; diff(candidate, x) - integrand is zero within the chain,
               but candidate does not match the corpus expectation
  unverified   answer; neither zero-test closed within the chain
  no-answer    integrate returned its noun form; corpus also expects a noun
  unexpected   integrate returned an answer; corpus expects a noun
  error        subprocess died (Lisp error, timeout-induced kill, or a
               parse-time fatality of the integrand/expectation text)

Build notes (5.49-series dev, measured 2026-08-17):
  * a failed `integrate(f, x)` returns a noun that IS the unevaluated
    `integrate` call (measured 2026-08-18: string(op(r)) = "integrate",
    is(r = 'integrate(f, x)) -> true), but its op object compares
    unknown against the bare symbol (is(equal(op(r), integrate)) ->
    unknown), so the detector is is(string(op(r)) = "integrate").
    listp/islist/isatom on the noun stay unevaluated; atom(r) -> false.
    length(r) = 2 and part(r,1)=f, part(r,2)=x, but part/length cannot
    tell the noun from a product ANSWER of the form integrand*x
    (length(5*x) = 2), so part/length must not be used as the detector
    (see build_text). The 2026-08-17 note claiming the noun carries no
    `integrate` symbol was superseded by these measurements.
  * `=` no longer auto-evaluates to true/false on non-simplifying equations,
    so every boolean is wrapped in is().
  * the zero-test chain is ratsimp, ratsimp o expand, factor, ratsimp o
    factor: `simplify` and `together` are unbound in this build.
  * integrate() prompts "Is ... positive or negative?" from a query
    stream (not stdin) when it cannot decide a sign; the batch answers
    come from the batch file itself when batch_answers_from_file is true
    (manual: `? batch_answers_from_file`; `--batch-string` and
    run_testsuite default it to true, plain -b does not), so the
    template carries a pool of `pos` answer lines.

Usage: probe-integrate-sample.py [file-substring] [per-file N] [timeout S]
        [suite-dir] [start-file-index] [append] [skip-first-entries]
        [out-file] [stop-file-index] [section]
Defaults survey "1 Algebraic functions/", 5 entries per file, 30 s cap.
Phase-2 resume (after a killed/timeouted phase 1): pass the suite dir,
the 0-based file index to start at (see sorted file list below),
"append" to continue the same .out, and the number of entries already
recorded in .out for that first file (resume-info.py prints both); the
summary section then covers phase 2 only. stop-file-index (exclusive)
bounds the file range from the other side so several processes can run
disjoint slices of the file list in parallel, each with its own out
file (or the same one, appending).
"""

import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
SECTION = sys.argv[10] if len(sys.argv) > 10 else "1 Algebraic functions"

FILTER = sys.argv[1] if len(sys.argv) > 1 else SECTION + "/"
PER_FILE = int(sys.argv[2]) if len(sys.argv) > 2 else 5
TIMEOUT = int(sys.argv[3]) if len(sys.argv) > 3 else 30
SUITE_DIR = sys.argv[4] if len(sys.argv) > 4 else SUITE
START_INDEX = int(sys.argv[5]) if len(sys.argv) > 5 else 0
APPEND = len(sys.argv) > 6 and sys.argv[6] == "append"
SKIP_FIRST = int(sys.argv[7]) if len(sys.argv) > 7 else 0
OUT_FILE = sys.argv[8] if len(sys.argv) > 8 else None  # default below
STOP_INDEX = int(sys.argv[9]) if len(sys.argv) > 9 else None

KNOWN_CLASSES = {
    "expected", "verified", "unverified",
    "no-answer", "unexpected", "error", "timeout",
}

workdir = tempfile.mkdtemp(prefix="maxima-rubi-smp-")
mac_file = os.path.join(workdir, "i.mac")
# prompts must be answered from the batch file itself, and the
# batch_answers_from_file switch has to be set before the batch starts,
# so it goes in a --preload file (plain -b defaults it to false;
# --batch-string and run_testsuite default it to true).
preload_file = os.path.join(workdir, "preload.mac")
open(preload_file, "w", encoding="utf-8").write("batch_answers_from_file: true$\n")


def maxima_run(mac_text, timeout):
    open(mac_file, "w", encoding="utf-8").write(mac_text)
    try:
        r = subprocess.run(
            ["maxima", "--very-quiet", "-p", preload_file, "-b", mac_file],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, timeout=timeout, cwd=ROOT,
        )
        return r.stdout, False
    except subprocess.TimeoutExpired as e:
        return (e.stdout or b"").decode("utf-8", "replace") if e.stdout else "", True


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
    # Template variables are mr_/MR_-prefixed and must NOT collide with
    # corpus symbols: the pasted f_text/e_text text is re-parsed and
    # re-evaluated in scope of these bindings, so a template name that a
    # corpus entry also uses (f and r are common coefficients/exponents in
    # class 1) gets substituted into the pasted text, corrupting the
    # comparison (measured 2026-08-18: noun r with is(part(r,1)=<f_text>)
    # -> false while is(part(r,1)=mr_f) -> true).
    # noun-test value: 1 iff mr_r is a failed-integrate noun [f, x].
    # atom() is checked first because length() on an atom is a hard error;
    # atom() must be used, not isatom() -- isatom() on a noun object stays
    # unevaluated in this build, which would freeze the whole condition.
    # Detector: string(op(mr_r)) = "integrate". Measured 2026-08-18:
    # a failed integrate's noun has op printing "integrate" but is NOT the
    # bare symbol (is(equal(op(r), integrate)) -> unknown), so symbol
    # comparison fails; string() comparison works. part()/length() are
    # useless here: length(5*x) = 2 and part match the noun- shape, so a
    # product answer of the form integrand*x (constant integrands) was
    # misdetected as a noun. Quoted 'integrate(f_text, x) equality is also
    # useless: is(5*x = 'integrate(5, x)) -> true.
    noun = ("block([], if atom(mr_r) then 0 else "
            "if is(string(op(mr_r)) = \"integrate\") then 1 else 0)")
    # integrate() prompts "Is ... positive or negative?" (asksign) or
    # "Is ... equal to ...?" (askequal), read from a query stream, not
    # stdin. With batch_answers_from_file (set in the --preload file) the
    # batch file itself supplies the answers (manual: `? batch_answers_
    # from_file`). Each pool line is consumed as a prompt answer if one
    # fires, and is a harmless bare statement otherwise. askequal accepts
    # yes/no (generic answer: no); asksign domains accept pos/neg (generic
    # answer: pos). The pool alternates so a mistyped-format line is
    # rejected and the following line still fits the open prompt.
    head = (f"mr_f: {f_text}$\n"
            f"mr_r: integrate(mr_f, {var_text})$\n"
            + "pos$\n" * 6 + "no$\n" * 6)
    # corpus noun expectations appear as `CannotIntegrate(f, x)` (Maxima
    # call form, e.g. class 1.3.2) and as `Unintegrable[...]` (Rubi form,
    # other sections) -- detect both, by name, not by bracket style.
    if e_text.startswith(("Unintegrable", "CannotIntegrate")):
        body = (f"if is({noun} = 1) then disp(concat(\"CLASS no-answer\")) "
                f"else disp(concat(\"CLASS unexpected\"))")
    else:
        # e_text is pasted verbatim into this (block-local) scope: it must
        # not contain template names (mr_f/mr_r/MR_*), see the note above.
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
    walk_root = os.path.join(SUITE, SECTION) if len(sys.argv) <= 4 else SUITE_DIR
    rel_root = SUITE if len(sys.argv) <= 4 else SUITE_DIR
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
        ("=== maxima-rubi integrate sample baseline (phase 2, "
         f"resume at file index {START_INDEX}) ==="
         if APPEND else
         "=== maxima-rubi integrate sample baseline ==="),
        f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
    ]
    if not APPEND:
        r = subprocess.run(
            ["maxima", "--very-quiet", "--batch-string",
             "disp(build_info());"],
            capture_output=True, text=True, timeout=120,
        )
        for line in r.stdout.splitlines():
            line = line.strip()
            if line.startswith(("Maxima", "Lisp ", "Host ")):
                out_lines.append(f"maxima: {line}")
    out_lines.append(f"filter: {FILTER!r}  per-file: {PER_FILE}  "
                     f"timeout: {TIMEOUT}s")
    out_lines.append("")

    counts = {}
    t_integrate = 0.0
    t0 = time.time()
    out_lines_head = list(out_lines)
    out_path = (OUT_FILE or os.path.join(ROOT, "probes", "corpus",
                                         "probe-integrate-sample.out"))
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
                counts["error"] = counts.get("error", 0) + 1
                out_lines.append(f"{'error':14s} t=0.0s {label} "
                                 f"bad-entry-shape({len(els)})")
                outf.write(f"{'error':14s} t=0.0s {label} "
                           f"bad-entry-shape({len(els)})\n")
                outf.flush()
                continue
            f_text, var_text, _steps, e_text = els[0], els[1], els[2], els[3]
            e_text2 = els[4] if len(els) == 5 else None
            t_start = time.time()
            out, timed_out = maxima_run(
                build_text(f_text, var_text, e_text, e_text2), TIMEOUT)
            dt = time.time() - t_start
            t_integrate += dt
            # the result line stands alone; the batch input-echo also
            # contains CLASS strings inside concat("...")
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
            out_lines.append(f"{cls:14s} t={dt:6.1f}s {label}")
            outf.write(f"{cls:14s} t={dt:6.1f}s {label}\n")
            outf.flush()
    out_lines.append("")
    out_lines.append("=== summary ===")
    for k in sorted(counts):
        out_lines.append(f"{k:14s} {counts[k]}")
    out_lines.append(f"total integrals: {sum(counts.values())}")
    out_lines.append(f"wall time: {time.time() - t0:.1f}s   "
                     f"integrate time: {t_integrate:.1f}s")

    outf.write("\n".join(out_lines[out_lines.index("=== summary ==="):]) + "\n")
    outf.close()
    print("\n".join(out_lines[-8:]) + "\n")


if __name__ == "__main__":
    main()
