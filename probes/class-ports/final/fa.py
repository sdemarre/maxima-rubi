#!/usr/bin/env python3
"""probes/class-ports/final/fa.py -- the final class-ports re-measure's
PASS->FAIL attribution toolkit (runs the corpus driver's own entry text,
cap helper and classifier; every Maxima process stdin /dev/null, process
group killed on the wall backstop -- test/corpus_driver.py maxima_run).

  fa.py losses
      Writes losses.tsv: the 182 PASS->FAIL keys of test/final_ab_master_
      class{1,2,3,6}.out and test/final_ab_prefix_class{5,7,4}.out, with the
      base / pre-fix (.ports.out) / final class and t= of each.
  fa.py run ARM ENTRIES OUT [-j N] [--cap S]
      Harness verdict of every entry of ENTRIES (a file of `<rel> e<n>`
      keys, or losses.tsv) on ARM, N at a time (default 1 = sequential).
      ARM is name=CORE[:sw=v,sw=v][+overlay.mac+...]; CORE is final|prefix|
      master or a path. Appends `name class t= key` lines to OUT.
  fa.py trace ARM REL N [--cap S] [--full]
      rubi_verbose firings of one entry on ARM (top-level firing last).
"""
import concurrent.futures as cf
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DRIVER = os.path.join(ROOT, "test", "corpus_driver.py")
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
CORES = {
    "final": os.path.join(ROOT, "test", "mr_rules.core"),                 # 89bec424 c2deb32
    "prefix": "/home/serge/src/mr-gtq/test/mr_rules.core",               # 4daae7ac 4ed1877
    "master": "/home/serge/src/mr-attr-base/test/mr_rules.core",         # d251f4bf cc12ec2
}
KEY = re.compile(r"(\d [^/]+/.*\.mac) e(\d+)")
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)$")
PAT = re.compile(r"rubi: rule (\S+) r(\d+) (fired|declined|misfire[^o]*) on (.*?) with ")


def load_driver(core, cap):
    os.environ["MR_RULES_CORE_PATH"] = core    # pinned: never rebuilt, no fingerprint check
    saved = sys.argv
    sys.argv = [DRIVER, "1 Algebraic functions/", "999999", str(cap), SUITE]
    try:
        spec = importlib.util.spec_from_file_location("corpus_driver", DRIVER)
        d = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(d)
    finally:
        sys.argv = saved
    return d


def parse_arm(spec):
    name, rest = spec.split("=", 1)
    parts = rest.split("+")
    head, overlays = parts[0], parts[1:]
    sw = {}
    if ":" in head:
        head, s = head.split(":", 1)
        for kv in s.split(","):
            k, v = kv.split("=")
            sw[k] = v
    core = CORES.get(head, os.path.abspath(head))
    pre = "".join(open(os.path.join(HERE, p) if not os.path.isabs(p) else p).read() + "\n"
                  for p in overlays)
    return name, core, sw, pre


def read_record(path):
    out = {}
    for l in open(path):
        m = RESULT.match(l.rstrip("\n"))
        if m:
            out[(m.group(3), int(m.group(4)))] = (m.group(1), float(m.group(2)), int(m.group(5)))
    return out


def keys_of(path):
    ks = []
    for l in open(path):
        if l.startswith("#"):
            continue
        m = KEY.search(l)
        if m:
            ks.append((m.group(1), int(m.group(2))))
    return ks


def entry_text(d, rel, idx):
    ents, lnos = d.extract_entries(os.path.join(SUITE, rel))
    els = d.split_elements(ents[idx - 1][1:-1])
    return els, lnos[idx - 1]


def classify(d, rel, idx, cap, pre):
    els, lno = entry_text(d, rel, idx)
    f = d.normalize_heads(els[0]); var = els[1]
    e = d.normalize_heads(els[3])
    e2 = d.normalize_heads(els[4]) if len(els) == 5 else None
    cpu = []
    out, hit = d.maxima_run(pre + d.build_text(f, var, e, e2), cap, cpu)
    cls, _ = d.classify_output(out, hit)
    t = cpu[0] if cpu and cpu[0] is not None else -1
    return cls, t


def cmd_losses():
    rows = []
    specs = [(c, f"test/final_ab_master_class{c}.out", f"test/corpus_class{c}.out") for c in (1, 2, 3, 6)]
    specs += [(c, f"test/final_ab_prefix_class{c}.out", f"test/corpus_class{c}.ports.out") for c in (5, 7, 4)]
    for c, ab, base in specs:
        keys, sec = [], False
        for l in open(os.path.join(ROOT, ab)):
            if l.startswith("=== PASS->FAIL"):
                sec = True; continue
            if sec and l.startswith("==="):
                break
            m = re.match(r"\s*\S+\s+->\s+\S+\s+t=\S+\s+->\s+t=\S+\s+(.*) e(\d+)\s*$", l)
            if sec and m:
                keys.append((m.group(1), int(m.group(2))))
        b = read_record(os.path.join(ROOT, base))
        p = read_record(os.path.join(ROOT, f"test/corpus_class{c}.ports.out"))
        n = read_record(os.path.join(ROOT, f"test/corpus_class{c}.final.out"))
        for k in keys:
            rows.append(f"{c}\t{b[k][0]}\t{b[k][1]}\t{p[k][0]}\t{p[k][1]}\t{n[k][0]}\t{n[k][1]}\t{k[0]} e{k[1]}\n")
    with open(os.path.join(HERE, "losses.tsv"), "w") as fh:
        fh.write("#class\tbase\tbase_t\tprefix\tprefix_t\tfinal\tfinal_t\tkey\n")
        fh.writelines(rows)
    print(len(rows))


def cmd_run(argv):
    arm, path, out = argv[0], argv[1], argv[2]
    j = int(argv[argv.index("-j") + 1]) if "-j" in argv else 1
    cap = int(argv[argv.index("--cap") + 1]) if "--cap" in argv else 30
    name, core, sw, pre = parse_arm(arm)
    d = load_driver(core, cap)
    for k, v in sw.items():
        d.SWITCH_SETTINGS[k] = v
    keys = keys_of(path)
    fh = open(out, "a")
    fh.write(f"# arm {name} core {core} switches {sw} overlays {arm.split('+')[1:]} cap {cap} j {j}\n")
    fh.flush()

    def one(k):
        cls, t = classify(d, k[0], k[1], cap, pre)
        return f"{name:10s} {cls:14s} t={t:6.1f}s {k[0]} e{k[1]}\n"
    with cf.ThreadPoolExecutor(max_workers=j) as ex:
        for line in ex.map(one, keys):
            fh.write(line); fh.flush()


def cmd_trace(argv):
    arm, rel, idx = argv[0], argv[1], int(argv[2])
    cap = int(argv[argv.index("--cap") + 1]) if "--cap" in argv else 30
    name, core, sw, pre = parse_arm(arm)
    d = load_driver(core, cap)
    for k, v in sw.items():
        d.SWITCH_SETTINGS[k] = v
    els, _ = entry_text(d, rel, idx)
    f = d.normalize_heads(els[0]); var = els[1]
    switches = "".join(f"{k} : {v}$\n" for k, v in d.SWITCH_SETTINGS.items())
    text = (pre + switches + "display2d : false$\nlinel : 100000$\nrubi_verbose : true$\n"
            + f"mr_f : {f}$\nmr_t0 : elapsed_run_time()$\nmr_r : rubi(mr_f, {var})$\n"
            + 'print("RUBI-CPU", elapsed_run_time() - mr_t0)$\n'
            + 'print("ANSWER-LEN", slength(string(mr_r)), "UNINT", not freeof(unintegrable, mr_r))$\n'
            + 'print("ANSWER", string(mr_r))$\n' + "pos$\n" * 40 + "no$\n" * 20)
    cpu = []
    out, hit = d.maxima_run(text, cap, cpu)
    full = "--full" in argv
    print(f"# arm {name} {rel} e{idx} integrand {f}\n# core {core} sw {sw} cap {cap} hit {hit} cpu {cpu}")
    for line in out.splitlines():
        m = PAT.search(line)
        if m:
            s = m.group(4)
            print(f"{m.group(3):8s} {m.group(1)} r{m.group(2)}  {s if full else s[:160]}")
        elif line.startswith(("RUBI-CPU", "ANSWER")):
            print(line if full or len(line) < 600 else line[:600] + "...")
        elif "error" in line.lower() and "errormsg" not in line:
            print("  !! " + line[:300])


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "losses":
        cmd_losses()
    elif c == "run":
        cmd_run(sys.argv[2:])
    elif c == "trace":
        cmd_trace(sys.argv[2:])
