#!/usr/bin/env python3
"""integrate-beats-rubi issue 02, stage 2: the corpus driver run with the
integrand parsed under radexpand:false, on the entries stage 1
(04-radexpand-parse-set.py) found affected plus a seeded control sample of
unaffected entries. Three arms, same entries, same driver (run_entry), same
worker count, run one after another:

  stock  the driver as is (radexpand:true everywhere outside the dispatch,
         which mr_model_flags binds false itself);
  whole  `radexpand:false$` at the head of the entry text: the integrand, the
         expected answer and the verification all run under false (harness
         option 1 of the handoff);
  parse  radexpand:false only while `mr_f: <integrand>$` is parsed, true again
         right after: the expected answer and verification as stock.

Each arm writes probes/integrate-beats-rubi/04-radexpand-ab.<arm>.out in the
driver's result-line format (compare with test/ab_records.py).
    python3 probes/integrate-beats-rubi/04-radexpand-ab.py [--workers N] [--arms stock,whole,parse]
"""
import argparse, collections, concurrent.futures as cf, importlib.util, os, random, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
HERE = os.path.join(ROOT, "probes", "integrate-beats-rubi")
DRIVER = os.path.join(ROOT, "test", "corpus_driver.py")
SUITE_REL = "reference/maxima-syntax-test-suite"
SECTIONS = ["1 Algebraic functions", "2 Exponentials", "3 Logarithms", "4 Trig functions",
            "5 Inverse trig functions", "6 Hyperbolic functions",
            "7 Inverse hyperbolic functions", "8 Special functions"]
CONTROL = {"1": 400, "2": 50, "3": 50, "4": 300, "5": 50, "6": 150, "7": 50, "8": 50}
SEED = 20260928


def load_driver(section):
    saved = sys.argv
    sys.argv = [DRIVER, section + "/", "999999", "30", SUITE_REL]
    try:
        spec = importlib.util.spec_from_file_location("corpus_driver", DRIVER)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.argv = saved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--arms", default="stock,whole,parse")
    a = ap.parse_args()
    os.chdir(ROOT)
    affected = set()
    with open(os.path.join(HERE, "04-radexpand-parse-set.tsv"), encoding="utf-8") as fh:
        for line in fh:
            f = line.rstrip("\n").split("\t")
            affected.add((f[3], int(f[4][1:])))
    rng = random.Random(SEED)
    jobs = []  # (rel, idx0, entry_text, line_no, group)
    drv = None
    for sec in SECTIONS:
        d = load_driver(sec)
        drv = drv or d
        pool = []
        for path, rel in d.file_list():
            entries, line_nos = d.extract_entries(path)
            for i, (e, ln) in enumerate(zip(entries, line_nos)):
                job = (rel, i, e, ln)
                if (rel, i + 1) in affected:
                    jobs.append(job + ("affected",))
                else:
                    pool.append(job)
        jobs += [j + ("control",) for j in rng.sample(pool, CONTROL[sec.split()[0]])]
    print(f"entries: {len(jobs)} ({collections.Counter(j[4] for j in jobs)}), workers {a.workers}", flush=True)
    if not drv.ensure_rules_core():
        raise SystemExit("no rules core")
    orig = drv.build_text

    def arm_text(arm):
        def build(f_text, var_text, e_text, e_text2=None):
            t = orig(f_text, var_text, e_text, e_text2)
            if arm == "stock":
                return t
            t = "radexpand : false$\n" + t
            if arm == "parse":
                line = f"mr_f: {f_text}$\n"
                assert line in t
                t = t.replace(line, line + "radexpand : true$\n", 1)
            return t
        return build

    for arm in a.arms.split(","):
        drv.build_text = arm_text(arm)
        t0 = time.time()
        out = os.path.join(HERE, f"04-radexpand-ab.{arm}.out")
        with open(out, "w", encoding="utf-8") as fh, cf.ThreadPoolExecutor(a.workers) as ex:
            fh.write(f"=== 04-radexpand-ab arm {arm} ({time.strftime('%F %T %Z')}, "
                     f"{len(jobs)} entries, {a.workers} workers, cap {drv.TIMEOUT}s {drv.CAP_KIND}) ===\n")
            for line in drv.build_info_lines():
                fh.write(line + "\n")
            futs = {ex.submit(drv.run_entry, *j[:4]): j for j in jobs}
            cnt = collections.Counter()
            for f in cf.as_completed(futs):
                cls, line, _caps = f.result()
                cnt[cls] += 1
                fh.write(line + "\n")
                fh.flush()
        passed = cnt["verified"] + cnt["expected"]
        print(f"arm {arm}: {dict(cnt)} PASS {passed} wall {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
