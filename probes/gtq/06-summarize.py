#!/usr/bin/env python3
"""probes/gtq/06-summarize.py probes/gtq/05-census.out -- the census tables.

  * calls: the GtQ-family site calls per section (the cur arm's GTQSUM; a run
    the cap killed has no summary and contributes its GTQN floor), and the
    current emission's value on them (true / false / unknown / error);
  * disagreements (F) vs (R): calls, per section; the distinct (op, u, v)
    with their (F, R, cur) values and handles, most frequent first;
  * verdicts: the per-entry class under cur / F / R, the PASS counts
    (PASS = verified / expected / no-answer, test/corpus_driver.py
    PASS_CLASSES), and every entry whose verdicts differ between arms."""
import collections, re, sys

PASS = {"expected", "verified", "no-answer"}
RUN = re.compile(r"^RUN (\S+)\s+(\S+)\s+t=\s*([-\d.]+)s (.*?) \| (.*)$")
DIS = re.compile(r"^DIS (\S+)\s+(.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| cur=(\S+) F=(\S+) R=(\S+)$")


def num(s, k):
    m = re.search(k + r"=(\d+)", s)
    return int(m.group(1)) if m else 0


def main():
    runs = collections.OrderedDict()
    dis = collections.defaultdict(list)
    for l in open(sys.argv[1]):
        m = RUN.match(l.rstrip("\n"))
        if m:
            arm, cls, t, label, tail = m.groups()
            runs.setdefault(label, {})[arm] = (cls, float(t), tail)
            continue
        m = DIS.match(l.rstrip("\n"))
        if m:
            dis[(m.group(1), m.group(2))].append(m.groups()[2:])
    sec = lambda lab: lab.split(" ", 1)[0]
    print(f"entries: {len(runs)}  (runs: {sum(len(v) for v in runs.values())})\n")

    print("== calls (cur arm; killed runs contribute their GTQN floor)")
    print(f"{'sec':>3} {'entries':>7} {'calls':>8} {'true':>7} {'false':>7} {'unknown':>7} {'err':>5} {'F#R calls':>9} {'entries w/ F#R':>14} {'no-summary':>10}")
    T = collections.Counter()
    for s in sorted({sec(l) for l in runs}):
        c = collections.Counter()
        for lab, arms in runs.items():
            if sec(lab) != s or "cur" not in arms:
                continue
            c["entries"] += 1
            tail = arms["cur"][2]
            if tail.startswith("GTQSUM"):
                for k in ("calls", "cur_true", "cur_false", "cur_unknown", "cur_err", "dis"):
                    c[k] += num(tail, k)
                if num(tail, "dis"):
                    c["ent_dis"] += 1
            else:
                c["nosum"] += 1
                m = re.search(r"GTQN (\d+) (\d+)", tail)
                if m:
                    c["calls"] += int(m.group(1)); c["dis"] += int(m.group(2))
                if dis.get(("cur", lab)):
                    c["ent_dis"] += 1
        for k, v in c.items():
            T[k] += v
        print(f"{s:>3} {c['entries']:>7} {c['calls']:>8} {c['cur_true']:>7} {c['cur_false']:>7} {c['cur_unknown']:>7} {c['cur_err']:>5} {c['dis']:>9} {c['ent_dis']:>14} {c['nosum']:>10}")
    print(f"{'all':>3} {T['entries']:>7} {T['calls']:>8} {T['cur_true']:>7} {T['cur_false']:>7} {T['cur_unknown']:>7} {T['cur_err']:>5} {T['dis']:>9} {T['ent_dis']:>14} {T['nosum']:>10}")

    print("\n== distinct disagreeing calls (cur arm log), by (op, u, v, cur, F, R): count, sections, handles")
    d = collections.defaultdict(lambda: [0, set(), set()])
    for (arm, lab), rows in dis.items():
        if arm != "cur":
            continue
        for h, op, u, v, c, f, r in rows:
            k = (op, u, v, c, f, r)
            d[k][0] += 1; d[k][1].add(sec(lab)); d[k][2].add(h)
    for k, (n, ss, hs) in sorted(d.items(), key=lambda kv: -kv[1][0]):
        op, u, v, c, f, r = k
        hs = sorted(hs)
        print(f"{n:5d}  {op:2s} u={u}  v={v}  cur={c} F={f} R={r}  sec {','.join(sorted(ss))}  "
              f"handles {len(hs)}: {', '.join(hs[:6])}{' ..' if len(hs) > 6 else ''}")
    print(f"distinct: {len(d)}")

    print("\n== verdicts by arm (PASS = verified/expected/no-answer)")
    print(f"{'sec':>3} {'cur PASS':>8} {'F PASS':>7} {'R PASS':>7}  F#R entries  cur#F  cur#R")
    P = collections.Counter()
    for s in sorted({sec(l) for l in runs}):
        c = collections.Counter()
        for lab, arms in runs.items():
            if sec(lab) != s or len(arms) < 3:
                continue
            for a in ("cur", "F", "R"):
                c[a] += arms[a][0] in PASS
            c["FR"] += arms["F"][0] != arms["R"][0]
            c["cF"] += arms["cur"][0] != arms["F"][0]
            c["cR"] += arms["cur"][0] != arms["R"][0]
        for k, v in c.items():
            P[k] += v
        print(f"{s:>3} {c['cur']:>8} {c['F']:>7} {c['R']:>7}  {c['FR']:>11}  {c['cF']:>5}  {c['cR']:>5}")
    print(f"{'all':>3} {P['cur']:>8} {P['F']:>7} {P['R']:>7}  {P['FR']:>11}  {P['cF']:>5}  {P['cR']:>5}")

    print("\n== every entry whose verdict differs between arms: cur / F / R (cpu s), and its F#R calls (cur arm)")
    for lab, arms in runs.items():
        if len(arms) < 3:
            continue
        v = [arms[a][0] for a in ("cur", "F", "R")]
        if len(set(v)) > 1:
            ts = "/".join(f"{arms[a][1]:.1f}" for a in ("cur", "F", "R"))
            print(f"{v[0]:>13} / {v[1]:<13} / {v[2]:<13} ({ts})  {lab}")
            seen = collections.Counter((h, op, u, vv, c, f, r) for h, op, u, vv, c, f, r in dis.get(("cur", lab), []))
            for (h, op, u, vv, c, f, r), n in seen.most_common(8):
                print(f"      {n:3d}x {h}: {op} u={u} v={vv} cur={c} F={f} R={r}")


if __name__ == "__main__":
    main()
