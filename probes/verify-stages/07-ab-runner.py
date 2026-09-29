"""probes/verify-stages/07-ab-runner.py RECORD OUT [workers] -- re-run every
entry of RECORD (any merged record, or a file of its result lines) through
corpus_driver.run_entry_full, 12 threads by default, and write driver-format
result lines to OUT (compare two with test/ab_records.py) and each entry's
proof tag to OUT.proof. The core is the driver's: MR_RULES_CORE_PATH=<core>
pins one (a worktree's, built at the base commit).

Used 2026-09-28 for the two same-checker A/Bs of
handoffs/2026-09-28-checker-wrong-answers:
  07-ab-fullsimplify-class2.out  RECORD test/corpus_class2.pfs.out (965),
      base core 215918b, new core e5a9d89 (%mr_fullSimplify);
  07-ab-errata-1.1.2.6.out       RECORD = the result lines of
      test/corpus_class5.pfs.out, test/corpus_class7.pfs.out and the
      1.1.2.4/1.1.2.5/1.1.2.6 lines of test/corpus_class1.pfs.out (12,459),
      base core e5a9d89, new core 4763cab (the 1.1.2.6 r13/r14 erratum)."""
import concurrent.futures, importlib.util, os, re, sys
ROOT = "/home/serge/src/maxima-rubi"; SUITE = "reference/maxima-syntax-test-suite"
os.chdir(ROOT)
sys.path.insert(0, "test")
import ab_records
rec, out = sys.argv[1], sys.argv[2]
workers = int(sys.argv[3]) if len(sys.argv) > 3 else 12
keys = sorted(ab_records.load_record(rec).keys())
def load_driver(section):
    real = sys.argv[:]
    sys.argv = ["corpus_driver.py", section + "/", "999999", "30", SUITE]
    try:
        spec = importlib.util.spec_from_file_location("drv_" + section[0], "test/corpus_driver.py")
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
    finally:
        sys.argv = real
drv = {}
cache = {}
for rel, n in keys:
    s = rel.split("/")[0]
    if s not in drv: drv[s] = load_driver(s)
    if rel not in cache: cache[rel] = drv[s].extract_entries(os.path.join(ROOT, SUITE, rel))
def run(key):
    rel, n = key
    d = drv[rel.split("/")[0]]
    entries, line_nos = cache[rel]
    cls, line, _caps, proof = d.run_entry_full(rel, n - 1, entries[n - 1], line_nos[n - 1])
    return line, proof
with open(out, "w") as fh, open(out + ".proof", "w") as fp, concurrent.futures.ThreadPoolExecutor(workers) as ex:
    for line, proof in ex.map(run, keys):
        fh.write(line.rstrip("\n") + "\n"); fh.flush(); fp.write(f"{proof} {line.split()[-3:]}\n")
print("DONE", out)
