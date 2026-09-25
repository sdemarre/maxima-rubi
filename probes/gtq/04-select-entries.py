#!/usr/bin/env python3
"""probes/gtq/04-select-entries.py RECORD [RECORD ...] > probes/gtq/census.entries

The census slice: about 40 entries per corpus section 1-8 (there is no
section-9 corpus; the 9.x rules fire from the others), weighted to the
corpus files whose rule files carry the most emitted GtQ-family sites.

  * a corpus file's weight = the emitted sites (make_census_overlay.py's
    reading) of the rule files mapped to it: by the Rubi file's TITLE when a
    same-section corpus file has that title (the suite renumbers some
    sections: Rubi 6.1.12 is the suite's 6.1.3), else by number (1_2_1_4b ->
    1.2.1.4; no same-numbered corpus file -> its parent);
  * per section, the top 8 files by weight give 5 entries each (a short file's
    remainder goes to the next file), picked evenly spaced over the file's
    entries whose record t= is at most MAXT seconds (bounds the 3-arm run);
  * RECORDs are merged driver records (their verdicts/t are only used to pick,
    and are echoed in the output as rec=<class>).
Deterministic.  Output lines are record-format result lines."""
import collections, glob, os, re, sys, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "probes", "gtq"))
import importlib.util
spec = importlib.util.spec_from_file_location("ov", os.path.join(ROOT, "probes", "gtq", "make_census_overlay.py"))
ov = importlib.util.module_from_spec(spec); spec.loader.exec_module(ov)
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)")
PER_SECTION, FILES, PER_FILE, MAXT = 40, 8, 5, 10.0


def site_counts():
    """(key, Rubi file title) -> emitted sites."""
    c = collections.Counter()
    for path in glob.glob(os.path.join(ROOT, "rules", "class*", "*.mac")):
        key = os.path.basename(path)[:-4]
        text = open(path).read()
        m = re.search(r"IntegrationRules/(.*?)\.m\s*$", text[:2000], re.M)
        title = os.path.basename(m.group(1)).split(" ", 1)[-1] if m else ""
        n = [0]
        ov.rewrite(text, key, n)
        c[(key, title)] += n[0]
    return c


def main():
    recs = collections.defaultdict(list)       # corpus rel file -> [(line, t)]
    for r in sys.argv[1:]:
        for l in open(r):
            m = RESULT.match(l)
            if m:
                recs[m.group(3)].append((l.rstrip("\n"), float(m.group(2)), int(m.group(4))))
    num, byt = {}, {}                            # "1.2.1.4" / (sec, title) -> rel file
    for rel in recs:
        b = os.path.basename(rel)[:-4]
        num[b.split(" ")[0]] = rel
        byt[(rel[0], b.split(" ", 1)[-1])] = rel
    w = collections.Counter()
    for (key, title), n in site_counts().items():
        if (key[0], title) in byt:               # the suite renumbers some
            w[byt[(key[0], title)]] += n         # sections (6.1.12 -> 6.1.3)
            continue
        d = re.sub(r"[a-z]+$", "", key).replace("_", ".")
        while d and d not in num:
            d = d.rsplit(".", 1)[0] if "." in d else ""
        if d:
            w[num[d]] += n
    print(f"# census slice: {PER_SECTION}/section, top {FILES} files by emitted GtQ-family sites, "
          f"record t<={MAXT}s, evenly spaced")
    for r in sys.argv[1:]:
        print(f"# record {r} md5 {hashlib.md5(open(r, 'rb').read()).hexdigest()}")
    for sec in "12345678":
        files = sorted((f for f in recs if f.startswith(sec + " ")), key=lambda f: (-w[f], f))
        want, got = PER_SECTION, []
        for f in files[:FILES * 2]:
            if len(got) >= PER_SECTION:
                break
            ok = sorted((e for e in recs[f] if e[1] <= MAXT), key=lambda e: e[2])
            k = min(len(ok), PER_FILE + max(0, files.index(f) * PER_FILE - len(got)),
                    PER_SECTION - len(got))
            if k <= 0 or not ok:
                continue
            step = len(ok) / k
            pick = [ok[int(i * step + step / 2)] for i in range(k)]
            print(f"# section {sec}: {f}  weight {w[f]}  picked {k} of {len(ok)}")
            got += pick
        for l, _t, _e in got:
            print(l)


if __name__ == "__main__":
    main()
