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
  * a failed `integrate(f, x)` is a list-structured noun: listp is false but
    length = 2, part(r,1) = f, part(r,2) = x. freeof(integrate, r) does NOT
    detect it (the noun carries no `integrate` symbol). isatom(r) on the
    noun stays unevaluated; atom(r) -> false and is the safe atom guard.
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
Defaults survey "1 Algebraic functions/", 5 entries per file, 30 s cap.
"""

import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

ROOT = "/home/serge/src/maxima-rubi"
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
SECTION = "1 Algebraic functions"

FILTER = sys.argv[1] if len(sys.argv) > 1 else SECTION + "/"
PER_FILE = int(sys.argv[2]) if len(sys.argv) > 2 else 5
TIMEOUT = int(sys.argv[3]) if len(sys.argv) > 3 else 30
SUITE_DIR = sys.argv[4] if len(sys.argv) > 4 else SUITE

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
        f"d: ratsimp({d_expr}), if is(d=0) then 1 "
        "else (d: ratsimp(expand(d)), if is(d=0) then 1 "
        "else (d: factor(d), if is(d=0) then 1 "
        "else (d: ratsimp(factor(d)), if is(d=0) then 1 else 0)))"
    )


def build_text(f_text, var_text, e_text, e_text2=None):
    # noun-test value: 1 iff r is a failed-integrate noun [f, x]. atom() is
    # checked first because length() on an atom is a hard error; atom() must
    # be used, not isatom() -- isatom() on a noun object stays unevaluated
    # in this build, which would freeze the whole condition.
    noun = ("block([L], if atom(r) then 0 else "
            f"(L: length(r), if is(L=2) and is(part(r,1)={f_text}) and "
            f"is(part(r,2)={var_text}) then 1 else 0))")
    # integrate() prompts "Is ... positive or negative?" (asksign) or
    # "Is ... equal to ...?" (askequal), read from a query stream, not
    # stdin. With batch_answers_from_file (set in the --preload file) the
    # batch file itself supplies the answers (manual: `? batch_answers_
    # from_file`). Each pool line is consumed as a prompt answer if one
    # fires, and is a harmless bare statement otherwise. askequal accepts
    # yes/no (generic answer: no); asksign domains accept pos/neg (generic
    # answer: pos). The pool alternates so a mistyped-format line is
    # rejected and the following line still fits the open prompt.
    head = (f"f: {f_text}$\n"
            f"r: integrate(f, {var_text})$\n"
            + "pos$\n" * 6 + "no$\n" * 6)
    if e_text.startswith(("Unintegrable[", "CannotIntegrate[")):
        body = (f"if is({noun} = 1) then disp(concat(\"CLASS no-answer\")) "
                f"else disp(concat(\"CLASS unexpected\"))")
    else:
        ze = zero_chain(f"diff(r - {e_text}, {var_text})")
        zv = zero_chain(f"diff(r, {var_text}) - f")
        if e_text2 is not None:
            ze2 = zero_chain(f"diff(r - {e_text2}, {var_text})")
            body = (f"if is({noun} = 1) then disp(concat(\"CLASS no-answer\")) "
                    "else block([d, dv, z, z2, w], z: (" + ze + "), "
                    "z2: (" + ze2 + "), "
                    "if is(z=1) or is(z2=1) "
                    "then disp(concat(\"CLASS expected\")) "
                    "else (w: (" + zv + "), "
                    "if is(w=1) then disp(concat(\"CLASS verified\")) "
                    "else disp(concat(\"CLASS unverified\"))))")
        else:
            body = (f"if is({noun} = 1) then disp(concat(\"CLASS no-answer\")) "
                    "else block([d, dv, z, w], z: (" + ze + "), "
                    "if is(z=1) then disp(concat(\"CLASS expected\")) "
                    "else (w: (" + zv + "), "
                    "if is(w=1) then disp(concat(\"CLASS verified\")) "
                    "else disp(concat(\"CLASS unverified\"))))")
    return head + body + "$\n" + "pos$\n" * 6 + "no$\n" * 6


def main():
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

    out_lines = [
        "=== maxima-rubi integrate sample baseline ===",
        f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
    ]
    r = subprocess.run(
        ["maxima", "--very-quiet", "--batch-string", "disp(build_info());"],
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
    for path, rel in files:
        try:
            entries, line_nos = extract_entries(path)
        except (AssertionError, UnicodeDecodeError, IndexError):
            out_lines.append(f"SKIP-BADFILE {rel}")
            continue
        for idx in range(min(PER_FILE, len(entries))):
            els = split_elements(entries[idx][1:-1])
            label = f"{rel} e{idx + 1} L{line_nos[idx]}"
            if len(els) not in (4, 5):
                counts["error"] = counts.get("error", 0) + 1
                out_lines.append(f"{'error':14s} t=0.0s {label} "
                                 f"bad-entry-shape({len(els)})")
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
    out_lines.append("")
    out_lines.append("=== summary ===")
    for k in sorted(counts):
        out_lines.append(f"{k:14s} {counts[k]}")
    out_lines.append(f"total integrals: {sum(counts.values())}")
    out_lines.append(f"wall time: {time.time() - t0:.1f}s   "
                     f"integrate time: {t_integrate:.1f}s")

    text = "\n".join(out_lines) + "\n"
    print(text)
    out_path = os.path.join(ROOT, "probes", "corpus", "probe-integrate-sample.out")
    open(out_path, "w", encoding="utf-8").write(text)


if __name__ == "__main__":
    main()
