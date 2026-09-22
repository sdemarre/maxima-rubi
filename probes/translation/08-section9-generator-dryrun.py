#!/usr/bin/env python3
"""probes/translation/08-section9-generator-dryrun.py -- what the unchanged
generator needs before it can emit 9.2 + 9.3 (spec
docs/superpowers/specs/2026-09-22-section9-port-design.md, amendment A2).
No Maxima; `sbcl` on the PATH for part D. Emits ONLY into a temporary
directory -- never into rules/ (generate_rules.main() re-runs configure(),
which resets OUT to rules/<class>; this probe calls _emit_source directly).

A. The unchanged emitter over the two files, one error at a time: each
   `unlisted head` is recorded and stood in with a placeholder RENAME row,
   so the walk reaches the next rule; any other error stops the walk.
B. The same walk with the four stand-ins the port replaces with real fixes:
   (1) whole-line (* *) comments dropped before comment stripping,
   (2) the multi-line If[TrueQ[$LoadShowSteps], <ShowStep rule>,
       <plain rule>] wrapper reduced to its plain branch,
   (3) 9.3's `v=!=u` read as UnsameQ[v,u],
   (4) 9.3's `Int[u_,x_]` read as `Int[u_,x_Symbol]`.
   Prints the per-file totals and each file's _tail list.
C. Stand-in (1) alone over the committed classes 1/2/3/6: every regenerated
   file compared byte-for-byte with rules/ (the fix is neutral there).
   Stand-in (2) is NOT applied here: class 1's 1_4_1.mac carries both
   branches of the same wrapper (r7/r8), so (2) is scoped to class 9.
D. Every pattern string of B's output prepared in MR-MATCH.
"""
import contextlib, io, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "generator"))
sys.argv = [sys.argv[0]]
import generate_rules as g  # noqa: E402
import translation_table as tt  # noqa: E402

ORIG_STRIP = g.strip_comments


def drop_comment_lines(text):
    return "\n".join(l for l in text.split("\n")
                     if not re.fullmatch(r"\s*\(\*.*\*\)\s*", l))


def unwrap_multiline(text):
    lines, out, i = text.split("\n"), [], 0
    while i < len(lines):
        if lines[i].strip() == "If[TrueQ[$LoadShowSteps],":
            i += 1
            while not lines[i].strip().startswith("SimplifyFlag"):
                i += 1
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            blk = []
            while i < len(lines) and lines[i].strip():
                blk.append(lines[i]); i += 1
            assert blk[-1].rstrip().endswith("]"), blk[-1]
            blk[-1] = blk[-1].rstrip()[:-1]
            out += blk
            continue
        out.append(lines[i]); i += 1
    return "\n".join(out)


def walk(files, outdir, stand_ins):
    g.CLASS, g.CLASS_PREFIX, g.OUT = 9, "9 ", outdir
    if stand_ins:
        g.strip_comments = lambda t: ORIG_STRIP(unwrap_multiline(drop_comment_lines(t))) \
            .replace("v=!=u", "UnsameQ[v,u]").replace("Int[u_,x_] :=", "Int[u_,x_Symbol] :=")
        tt.RENAME["UnsameQ"] = "%mr_unsameQ"
    else:
        g.strip_comments = ORIG_STRIP
    heads, other = [], None
    while True:
        err, total, ll = io.StringIO(), 0, []
        try:
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                for f in files:
                    total = g._emit_source(f, g.key_of(f), None, total, ll)
            return heads, None, total
        except SystemExit:
            msg = err.getvalue().strip().splitlines()[-1]
            m = re.search(r"(\w+ r\d+): unlisted head '(\w+)'", msg)
            if not m:
                return heads, msg, None
            heads.append(m.groups())
            tt.RENAME[m.group(2)] = "%mr_placeholder"


def main():
    g.CLASS, g.CLASS_PREFIX = 9, "9 "
    files = [f for f in g.load_class_files(g.RUBI) if "Derivative" not in f]
    print("# section-9 generator dry run; files:")
    for f in files:
        print("  " + f)
    saved = dict(tt.RENAME)
    with tempfile.TemporaryDirectory() as td:
        print("\n== A. unchanged emitter")
        heads, other, _ = walk(files, Path(td) / "a", False)
        for rid, h in heads:
            print("  unlisted head %-44s first at %s" % (h, rid))
        print("  stopped: %s" % other)
        tt.RENAME.clear(); tt.RENAME.update(saved)

        print("\n== B. with the four stand-ins")
        heads, other, total = walk(files, Path(td) / "b", True)
        for rid, h in heads:
            print("  unlisted head %-44s first at %s" % (h, rid))
        print("  unlisted heads: %d; other error: %s" % (len(heads), other))
        print("  TOTAL emitted: %s" % total)
        pats = []
        for p in sorted((Path(td) / "b").glob("*.mac")):
            t = p.read_text()
            n = len(re.findall(r"^_mr_rule_\w+ : %mr_defrule", t, re.M))
            tail = re.search(r"^mr_rules_\w+_tail : \[(.*)\]\$", t, re.M)
            names = [s.strip() for s in tail.group(1).split(",") if s.strip()] if tail else []
            print("  %s: %d records, %d in _tail: %s" % (p.name, n, len(names), " ".join(names)))
            pats += ["%s r%s\t%s" % m for m in re.findall(
                r'^_mr_rule_\w+ : %mr_defrule\("([0-9a-z_]+)", (\d+), "([^"]*)"', t, re.M)]
            pats += ["matchq\t%s" % m for m in re.findall(r'%mr_matchQ\([^"]*?, "([^"]*)"', t)]
        tt.RENAME.clear(); tt.RENAME.update(saved)

        print("\n== C. stand-in (1) alone over classes 1/2/3/6, byte comparison")
        g.strip_comments = lambda t: ORIG_STRIP(drop_comment_lines(t))
        for cls in (1, 2, 3, 6):
            g.configure(cls)
            g.OUT = Path(td) / ("c%d" % cls)
            rels = list(g.load_class_files(g.RUBI))
            if cls == 1:
                rels += [(r, g.key_of(r) + "b") for r in g.EXTRA_CLASS1] + [(g.NINE_ONE, "9_1")]
            same = diff = 0
            for r in rels:
                rel, key = (r if isinstance(r, tuple) else (r, g.key_of(r)))
                with contextlib.redirect_stdout(io.StringIO()):
                    g._emit_source(rel, key, None, 0, [])
                new = (g.OUT / (key + ".mac")).read_text()
                old = (ROOT / "rules" / ("class%d" % cls) / (key + ".mac")).read_text()
                if new == old:
                    same += 1
                else:
                    diff += 1
                    print("  DIFFERS: class%d/%s.mac" % (cls, key))
            print("  class %d: %d files identical, %d differ" % (cls, same, diff))
        g.strip_comments = ORIG_STRIP

        print("\n== D. pattern strings of B prepared in MR-MATCH")
        tsv = Path(td) / "p.tsv"
        tsv.write_text("\n".join(pats) + "\n")
        r = subprocess.run(["sbcl", "--script", str(ROOT / "test/matcher/prepare_patterns.lisp"),
                            str(ROOT / "maxima_rubi_match.lisp"), str(tsv)],
                           capture_output=True, text=True)
        print("  " + (r.stdout.strip().splitlines() or [r.stderr[-200:]])[-1])


if __name__ == "__main__":
    main()
