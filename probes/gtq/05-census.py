#!/usr/bin/env python3
"""probes/gtq/05-census.py CORE ENTRIES [CAP] > probes/gtq/05-census.out

The GtQ-family disagreement census.  CORE is the census core
(probes/gtq/build_census_core.sh: the rules core with every emitted
GtQ/LtQ/GeQ/LeQ site routed through %mr_gtq_W).  For every entry of ENTRIES
(record-format lines, probes/gtq/04-select-entries.py) and every arm in the
order cur, F, R (alternating per entry, one Maxima process at a time) the
entry runs through the driver's own entry text (build_text: the switches, the
rubi call, the classification) and cap mechanism (maxima_run: cpu cap helper,
stdin /dev/null, process-group kill), with `%mr_gtq_arm : "<arm>"$` prepended
and `%mr_gtq_summary()$` appended.  Output per run:

  RUN <arm> <class> t=<cpu>s <label> | GTQSUM ... (or `no-summary` when killed)
  DIS <arm> <label> | <handle> | op | u | v | cur=.. F=.. R=..   (every GTQDIS)

The arm value is the only difference between the three runs of an entry.

Build the core, then run (one Maxima process at a time; ~1 h for 295 entries):
  sh probes/gtq/build_census_core.sh <work>/census.core
  python3 probes/gtq/05-census.py <work>/census.core probes/gtq/census.entries 30 \
      > probes/gtq/05-census.out
  python3 probes/gtq/06-summarize.py probes/gtq/05-census.out > probes/gtq/06-summary.out"""
import importlib.util, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)")


def load_driver(core, cap):
    os.environ["MR_RULES_CORE_PATH"] = core
    saved = sys.argv
    sys.argv = [os.path.join(ROOT, "test", "corpus_driver.py"), "1 Algebraic functions/",
                "999999", str(cap), SUITE]
    try:
        spec = importlib.util.spec_from_file_location("corpus_driver", sys.argv[0])
        d = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(d)
    finally:
        sys.argv = saved
    return d


def main():
    core, entries = os.path.abspath(sys.argv[1]), sys.argv[2]
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    # --resume PREV: skip the entries PREV (an earlier, interrupted output of
    # this script) already holds all three arms of; print only the rest.
    done = set()
    if "--resume" in sys.argv:
        arms = {}
        for l in open(sys.argv[sys.argv.index("--resume") + 1]):
            m = re.match(r"^RUN (\S+)\s+\S+\s+t=\s*[-\d.]+s (.*?) \| ", l)
            if m:
                arms.setdefault(m.group(2), set()).add(m.group(1))
        done = {k for k, v in arms.items() if len(v) == 3}
    d = load_driver(core, cap)
    import datetime, subprocess
    print(f"# run {datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d %H:%M UTC}  "
          f"tree {subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True, cwd=ROOT).stdout.strip()}  "
          f"maxima {' | '.join(d.build_info_lines())}", flush=True)
    print(f"# core {core}  cap {cap} {d.CAP_KIND}  switches {d.SWITCH_SETTINGS}", flush=True)
    for l in open(entries):
        m = RESULT.match(l)
        if not m:
            continue
        rel, idx = m.group(3), int(m.group(4))
        ents, lnos = d.extract_entries(os.path.join(SUITE, rel))
        els = d.split_elements(ents[idx - 1][1:-1])
        f_text = d.normalize_heads(els[0]); var = els[1]
        e_text = d.normalize_heads(els[3])
        e_text2 = d.normalize_heads(els[4]) if len(els) == 5 else None
        label = f"{rel} e{idx} L{lnos[idx - 1]}"
        if label in done:
            continue
        for arm in ("cur", "F", "R"):
            text = (f'%mr_gtq_arm : "{arm}"$\n' + d.build_text(f_text, var, e_text, e_text2)
                    + "%mr_gtq_summary()$\n")
            cpu = []
            out, hit = d.maxima_run(text, cap, cpu)
            cls, _ = d.classify_output(out, hit)
            t = cpu[0] if cpu and cpu[0] is not None else -1
            summ = [x.strip() for x in out.splitlines() if x.strip().startswith("GTQSUM")]
            floor = [x.strip() for x in out.splitlines() if x.strip().startswith("GTQN")]
            tail = summ[0] if summ else ("no-summary" + (f" last {floor[-1]}" if floor else ""))
            print(f"RUN {arm:3s} {cls:14s} t={t:6.1f}s {label} | {tail}", flush=True)
            for x in out.splitlines():
                if x.startswith("GTQDIS "):
                    print(f"DIS {arm:3s} {label} | {x[7:]}", flush=True)


if __name__ == "__main__":
    main()
