#!/usr/bin/env python3
"""probes/class-ports/trace_entry.py -- run class-6 corpus entries with
rubi_verbose on, through the corpus driver's own text transform and cap
mechanism (maxima_run: stdin /dev/null, cpu cap helper, process-group kill
on the wall backstop), on one or more cores; print the rule firings (key rN,
integrand truncated) and the answer.

Single entry:
    MR_RULES_CORE_PATH=<core> python3 probes/class-ports/trace_entry.py \
        '<file rel to the section dir>' <entry 1-based> [cap] [--full] [--cond]
Batch (one Maxima process at a time; for each entry the cores in the order
given, i.e. ref then new alternating):
    python3 probes/class-ports/trace_entry.py --batch ENTRIES CAP CORE [CORE..]
  ENTRIES is a record-format file (result lines); output to stdout.

Lines: `fired K rN <integrand>` (a nested dispatch prints BEFORE its parent,
so the top-level firing is last), `cond`-mode adds every cond rejection.
The switches are the driver's shipping arm (SWITCH_SETTINGS).
"""
import importlib.util, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DRIVER = os.path.join(ROOT, "test", "corpus_driver.py")
SECTION = "6 Hyperbolic functions"
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
PAT = re.compile(r"rubi: rule (\S+) r(\d+) (fired|declined|misfire[^o]*) on (.*?) with ")
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)")


def load_driver(cap):
    saved = sys.argv
    sys.argv = [DRIVER, SECTION + "/", "999999", str(cap), SUITE]
    try:
        spec = importlib.util.spec_from_file_location("corpus_driver", DRIVER)
        d = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(d)
    finally:
        sys.argv = saved
    return d


def trace(d, rel, idx, cap, core, full=False, cond=False, width=160, pre_text=""):
    """Trace entry IDX of REL (relative to the section dir) on CORE."""
    d.RULES_CORE = core           # maxima_run reads the module global
    if rel.startswith(SECTION + "/"):
        rel = rel[len(SECTION) + 1:]
    entries, _ = d.extract_entries(os.path.join(SUITE, SECTION, rel))
    els = d.split_elements(entries[idx - 1][1:-1])
    f_text = d.normalize_heads(els[0]); var = els[1]
    switches = "".join(f"{k} : {v}$\n" for k, v in d.SWITCH_SETTINGS.items())
    text = (switches + "display2d : false$\nlinel : 100000$\nrubi_verbose : true$\n"
            + f"mr_f : {f_text}$\n"
            + "mr_t0 : elapsed_run_time()$\n"
            + f"mr_r : rubi(mr_f, {var})$\n"
            + 'print("RUBI-CPU", elapsed_run_time() - mr_t0)$\n'
            + 'print("ANSWER-LEN", slength(string(mr_r)), "UNINT", not freeof(unintegrable, mr_r))$\n'
            + 'print("ANSWER", string(mr_r))$\n'
            + "pos$\n" * 40 + "no$\n" * 20)
    cpu = []
    out, hit = d.maxima_run(pre_text + text, cap, cpu)
    lines = [f"# entry {rel} e{idx}  integrand {f_text}",
             f"# core {core}  cap {cap}  hit_cap {hit}  cpu {cpu}"]
    for line in out.splitlines():
        m = PAT.search(line)
        if m:
            f = m.group(4)
            if not full and len(f) > width:
                f = f[:width] + "..."
            lines.append(f"{m.group(3):8s} {m.group(1)} r{m.group(2)}  {f}")
        elif cond and "rubi: rule" in line:
            lines.append("    " + line[:300])
        elif line.startswith("RUBI-CPU") or line.startswith("ANSWER"):  # ANSWER-LEN too
            lines.append(line if full or len(line) < 600 else line[:600] + "...")
    return "\n".join(lines)


def classify(d, rel, idx, cap, core, pre_text):
    """The harness verdict (driver build_text + classify_output) of entry IDX
    of REL on CORE, with PRE_TEXT (runtime overlays) loaded first. Returns a
    record-format result line (t= is the entry's CPU seconds, overlay load
    included)."""
    d.RULES_CORE = core
    if rel.startswith(SECTION + "/"):
        rel = rel[len(SECTION) + 1:]
    entries, lnos = d.extract_entries(os.path.join(SUITE, SECTION, rel))
    els = d.split_elements(entries[idx - 1][1:-1])
    f_text = d.normalize_heads(els[0]); var = els[1]
    e_text = d.normalize_heads(els[3])
    e_text2 = d.normalize_heads(els[4]) if len(els) == 5 else None
    cpu = []
    out, hit = d.maxima_run(pre_text + d.build_text(f_text, var, e_text, e_text2), cap, cpu)
    cls, _caps = d.classify_output(out, hit)
    t = cpu[0] if cpu and cpu[0] is not None else -1
    return f"{cls:14s} t={t:6.1f}s {SECTION}/{rel} e{idx} L{lnos[idx - 1]}"


def main():
    if sys.argv[1] == "--classify":
        # --classify PRE[,PRE..]|- ENTRIES CAP CORE
        pres, path, cap, core = sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
        pre_text = "" if pres == "-" else "".join(
            open(p).read() + "\n" for p in pres.split(","))
        d = load_driver(cap)
        for l in open(path):
            m = RESULT.match(l)
            if m:
                print(classify(d, m.group(3), int(m.group(4)), cap,
                               os.path.abspath(core), pre_text), flush=True)
        return
    if sys.argv[1] == "--batch":
        path, cap, cores = sys.argv[2], int(sys.argv[3]), sys.argv[4:]
        d = load_driver(cap)
        for l in open(path):
            m = RESULT.match(l)
            if not m:
                continue
            for core in cores:
                print(trace(d, m.group(3), int(m.group(4)), cap, os.path.abspath(core)),
                      flush=True)
                print(flush=True)
        return
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    rel, idx = args[0], int(args[1])
    cap = int(args[2]) if len(args) > 2 else 30
    d = load_driver(cap)
    pre = [a[6:] for a in sys.argv if a.startswith("--pre=")]
    pre_text = "".join(open(p).read() + "\n" for p in (pre[0].split(",") if pre else []))
    print(trace(d, rel, idx, cap, d.RULES_CORE, "--full" in sys.argv, "--cond" in sys.argv,
                pre_text=pre_text))


if __name__ == "__main__":
    main()
