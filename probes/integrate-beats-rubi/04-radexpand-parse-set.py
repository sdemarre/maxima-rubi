#!/usr/bin/env python3
"""integrate-beats-rubi issue 02, stage 1: which corpus integrands does
Maxima's default radexpand:true rewrite AT PARSE TIME?

Every entry's integrand (after the driver's normalize_heads) is parsed with
parse_string twice in one Maxima per class: once under radexpand:false, once
under the default true. An entry is AFFECTED when the two simplified forms
differ; ABS when the default form carries `abs` and the false form does not
(the sqrt(c*x^2) -> sqrt(c)*abs(x) case). Joined with the verdicts of
test/corpus_class<N>.pfs.out (master's measured state, e4311e6).

Writes probes/integrate-beats-rubi/04-radexpand-parse-set.tsv (one line per
affected entry: class, verdict, abs flag, key, integrand) and prints a
summary. Run from anywhere: python3 probes/integrate-beats-rubi/04-radexpand-parse-set.py
"""
import collections, importlib.util, os, re, signal, subprocess, sys, tempfile, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
HERE = os.path.join(ROOT, "probes", "integrate-beats-rubi")
DRIVER = os.path.join(ROOT, "test", "corpus_driver.py")
SUITE_REL = "reference/maxima-syntax-test-suite"
SECTIONS = ["1 Algebraic functions", "2 Exponentials", "3 Logarithms", "4 Trig functions",
            "5 Inverse trig functions", "6 Hyperbolic functions",
            "7 Inverse hyperbolic functions", "8 Special functions"]
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)\s*$")
PASS = {"verified", "expected"}


def load_driver(section):
    saved, cwd = sys.argv, os.getcwd()
    os.chdir(ROOT)
    sys.argv = [DRIVER, section + "/", "999999", "30", SUITE_REL]
    try:
        spec = importlib.util.spec_from_file_location("corpus_driver", DRIVER)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.argv = saved
        os.chdir(cwd)


def record(n):
    out = {}
    with open(os.path.join(ROOT, "test", f"corpus_class{n}.pfs.out"), encoding="utf-8") as fh:
        for line in fh:
            m = RESULT.match(line.rstrip("\n"))
            if m:
                out[(m.group(3), int(m.group(4)))] = m.group(1)
    return out


def mstr(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def parse_class(section):
    d = load_driver(section)
    keys, texts = [], []
    os.chdir(ROOT)
    for path, rel in d.file_list():
        entries, _lines = d.extract_entries(path)
        for i, e in enumerate(entries):
            els = d.split_elements(e[1:-1])
            if len(els) in (4, 5):
                keys.append((rel, i + 1))
                texts.append(d.normalize_heads(els[0]))
    lines = ["display2d:false$", "linel:100000$",
             "mr_one(k, s) := block([f, t, errormsg:false],"
             " f: errcatch(block([radexpand:false], string(parse_string(s)))),"
             " t: errcatch(string(parse_string(s))),"
             " if f = [] or t = [] then print(\"R\", k, \"ERR\")"
             " else if f[1] # t[1] then print(\"R\", k, \"DIFF\","
             " if ssearch(\"abs(\", t[1]) # false and ssearch(\"abs(\", f[1]) = false then 1 else 0))$"]
    for k, t in enumerate(texts):
        lines.append(f"mr_one({k}, {mstr(t)})$")
    lines.append('print("DONE")$')
    with tempfile.NamedTemporaryFile("w", suffix=".mac", delete=False) as fh:
        fh.write("\n".join(lines) + "\n")
        mac = fh.name
    p = subprocess.Popen(["maxima", "--very-quiet", "-b", mac], stdin=subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         start_new_session=True)
    try:
        out, _ = p.communicate(timeout=1800)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        raise
    finally:
        os.unlink(mac)
    assert "DONE" in out, out[-2000:]
    diff, err = {}, set()
    for line in out.splitlines():
        f = line.split()
        if len(f) >= 3 and f[0] == "R":
            if f[2] == "ERR":
                err.add(keys[int(f[1])])
            elif f[2] == "DIFF":
                diff[keys[int(f[1])]] = f[3] == "1"
    return keys, texts, diff, err


def main():
    print("# date:", time.strftime("%Y-%m-%d"), " build:",
          subprocess.run(["maxima", "--version"], capture_output=True, text=True).stdout.strip(),
          " records: test/corpus_class<N>.pfs.out")
    rows = []
    print("| class | entries | parse errors | affected | of which abs | affected PASS | affected FAIL | abs FAIL |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|")
    for sec in SECTIONS:
        n = sec.split()[0]
        keys, texts, diff, err = parse_class(sec)
        rec = record(n)
        by = dict(zip(keys, texts))
        vp = collections.Counter()
        for k, isabs in diff.items():
            v = rec.get(k, "missing")
            vp["pass" if v in PASS else "fail"] += 1
            if isabs and v not in PASS:
                vp["absfail"] += 1
            rows.append((n, v, int(isabs), k[0], k[1], by[k]))
        print(f"| {n} | {len(keys)} | {len(err)} | {len(diff)} | {sum(diff.values())} | "
              f"{vp['pass']} | {vp['fail']} | {vp['absfail']} |", flush=True)
    rows.sort(key=lambda r: (r[0], r[3], r[4]))
    with open(os.path.join(HERE, "04-radexpand-parse-set.tsv"), "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\te{r[4]}\t{r[5]}\n")
    fails = collections.Counter(r[1] for r in rows if r[1] not in PASS)
    print("affected FAIL verdicts:", dict(fails.most_common()))
    files = collections.Counter(r[3].split("/")[-1].split(" ")[0] for r in rows if r[1] not in PASS)
    print("affected FAIL by file (top 12):", files.most_common(12))


if __name__ == "__main__":
    main()
