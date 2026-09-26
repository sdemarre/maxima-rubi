#!/usr/bin/env python3
"""probes/class-ports/final/attribution.py -- bucket every PASS->FAIL of the final
class-ports re-measure (c2deb32, core 89bec424) with its cause.

The 182 losses (losses.tsv, `fa.py losses`): classes 1/2/3/6 against master's
promoted records (test/final_ab_master_class{1,2,3,6}.out: 85/3/5/46), classes
5/7/4 against their pre-fix class-ports records (test/final_ab_prefix_class{5,7,4}
.out: 15/19/9). Class 8: 0.

Evidence read here (all re-runnable with fa.py / the scripts named; 30 s cpu
cap, 12 processes at a time unless marked sequential; build
branch_5_50_base_84_g4204fb669, SBCL 2.6.7, 2026-09-26):
  01-noise-final.out      every loss rerun on the final core (the noise test)
  02-arm-eqqF.out         final core, mr_eqq_symbolic=false  (fix d0f0237 off)
  02-arm-substT.out       final core, mr_subst_simp=true     (fix e67e2eb off)
  02-arm-depth16.out      final core, mr_max_depth=16        (fix 2ee8fc4 off)
  02-arm-gtqIs.out        final core + ov-gtq-is.mac         (fix 39eba80 off)
  02-arm-prefix.out       the pre-fix core 4daae7ac (4ed1877), depth 16
  13-arm-revA.out         final core + ov-revert-A.mac       (fix 3bb8c4f off)
  14-arm-fixRP.out        final core + the PROPOSED fixes fix-eqq-radcan.mac +
                          fix-pseudoroot.mac
  08-bisect-<sha>.out     cores built at d0f0237 025c589 e799ea6 3bb8c4f 1ebef70
                          (each at its commit's defaults) over bisect.keys
  10-trace-fixA-final.out rubi_verbose traces of the fix-A losses (mechanism)
  11-numcheck-final.out   |dA/dx - f| of the unverified/unexpected answers (numcheck.py; two
                          parameter sets, the smaller residual is used; 1.2.1.2 e438's
                          hypergeometric at z > 1 checked with mpmath instead: 2e-15)
  12-e1035-combos.out     two-switch arms for 1.2.2.2 e1035 (sT_gI: Subst simp + is() GtQ)
  16-unattr-combos.out    6.2.5 e266 / 7.3.4 e118 with symbolic EqQ AND fix A reverted
  15-alt-timing.out       SEQUENTIAL alternating timing A/B (sample)
Prior attributions reused: class6-attribution (mr-attr, probes/class-ports/
15-attribution.out) for the class-6 losses carried from the ports.

Rules, in order:
  noise    final rerun PASS, no arm at least 2x AND 10 s faster, and the rerun
           within 2x + 5 s of the base record's time
  carried  pre-fix record FAIL and the pre-fix core rerun FAIL (the loss predates
           the fixes; family from the class-6 attribution when listed)
  cost:X / cause X   the arm(s) that recover the entry (FAIL -> PASS, or the
           final-rerun-PASS entry >= 2x and >= 10 s faster); ties broken by the
           bisect's first failing commit, else by the larger speed-up
"""
import os, re, subprocess, sys
from collections import OrderedDict, defaultdict
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
from matrix import rd, losses

P = {"verified", "expected", "no-answer"}
ARMS = OrderedDict([
    ("E", ("02-arm-eqqF.out", "symbolic EqQ/NeQ (d0f0237, mr_eqq_symbolic)")),
    ("A", ("13-arm-revA.out", "ExpandIntegrand reciprocal-atom guard (3bb8c4f, fix A)")),
    ("S", ("02-arm-substT.out", "plain Subst (e67e2eb, mr_subst_simp=false)")),
    ("D", ("02-arm-depth16.out", "depth cap 16->32 (2ee8fc4, mr_max_depth)")),
    ("G", ("02-arm-gtqIs.out", "two-valued GtQ/LtQ/GeQ/LeQ (39eba80)")),
])
BISECT = ["d0f0237", "025c589", "e799ea6", "3bb8c4f", "1ebef70"]
BISECT_TAG = {"d0f0237": "E", "025c589": "T18", "e799ea6": "T19", "3bb8c4f": "A", "1ebef70": "V"}


FINDINGS = """\
Findings (evidence: the files named in attribution.py's docstring)
 * 164/182 losses reproduce singly on the final core (01-noise-final.out). Of the 18 that
   pass singly, 15 are near-cap COST (>= 2x and >= 10 s faster with one fix reverted; the
   sequential alternating A/B 15-alt-timing.out confirms: 1.1.1.3 e2250 25.5 s vs fix-A-off
   0.8 s, e2436 26.0 vs 0.5, 1.1.1.2 e1007 18.4 vs EqQ-off 4.7 / proposed fix 0.1, 1.2.1.2
   e1825 22.0 vs EqQ-off 0.2 / proposed fix 22.0), 2 are class-6 ports-era slowdowns
   (6.3.7 e44/e180), 1 is noise (6.3.7 e34: 20.5 s here, prefix core 30.1 timeout).
 * Every non-carried loss is caused by one of the fixes, identified by reverting it alone on
   the final core (02-arm-*, 13-arm-revA) and confirmed by a commit bisect over cores built at
   d0f0237/025c589/e799ea6/3bb8c4f/1ebef70 (08-bisect-*): 65 first fail at 3bb8c4f (fix A),
   2 at d0f0237 (symbolic EqQ), 8 only after 1ebef70 (Subst / GtQ / depth). Tickets 18 and 19
   and the values trim (V) cause none.
 * Fix A (3bb8c4f, ExpandIntegrand reciprocal-atom guard) is correct, but the part error it
   removes had been making the calling rule misfire into a route that verified; the expansion
   now completes and 1_2_3_1 r11 (Int[(a+b x^-n+c x^n)^p_.], p defaulting to 1) refolds the
   expanded sum a^2/x+2ab+b^2x into (a^2+2abx+b^2x^2)/x, which the exact seen test cuts
   (every later rule misfires, 9_3 r67 gives up). All 65 bisected losses pass with the guard
   reverted (09-revert-A.out); 35 traces show the r11 refold (10-trace-fixA-final.out).
 * Symbolic EqQ (d0f0237) has a genuine COST DEFECT: the zero chain's factor() runs on
   differences whose kernels are radicals of symbols/numbers (1_4_1 r4/r5/r6 perfect-power
   test EqQ[Px, (Rt[a,n]+Rt[b,n] x)^n]) or `if unknown` conditionals leaked by %mr_pseudoRoot;
   probe 03: factor() > 120 s on (a+b x)^4 (c+d x)^3; probe 04: radcan answers nonzero in
   0.4 ms. PROPOSED FIX (fix-eqq-radcan.mac + fix-pseudoroot.mac, not applied) recovers 36
   of the 164 final-FAIL losses and loses none of them, none of the 29 EqQ-fix wins and none
   of a 75-entry PASS sample (14-arm-fixRP.out, 07-*); failing check 17-proposed-checks.mac
   (RED: 4/1 then no Results line at the 90 s cap; GREEN: 7/0).
 * Two-valued GtQ (39eba80, Rubi's reading) lets reductions fire whose conditions were
   unknown (e.g. 5_1_4 r23 Not[LtQ[m,-1]] on a symbolic m): 5 answers are numerically
   correct closed forms/forms the zero chain cannot close (11-numcheck-final.out), 8 end in a
   noun or time out.
 * Plain Subst (e67e2eb): 6 class-4 answers are numerically correct but unsimplified, so the
   zero chain cannot close them (S-verify); 1 timeout.
 * ONE WRONG ANSWER: 1.2.2.2 e1035, 1/(x*sqrt(a+(2+2c-2(1+c))*x^4)) -> -atanh(1)/(2 sqrt(a))
   (infinite), needs BOTH plain Subst and two-valued GtQ (12-e1035-combos.out): the
   unsimplified zero coefficient no longer raises the division-by-zero misfire that let
   9_1 r2 (EqQ[b,0]) answer log(x)/sqrt(a). A degenerate corpus input.
"""


def short(k):
    m = re.search(r"/([0-9.]+[0-9a-z]*) [^/]*\.mac e(\d+)$", k)
    return f"{m.group(1)} e{m.group(2)}" if m else k


def prior_class6():
    """short key -> family header, from the class-6 attribution of the ports."""
    try:
        txt = subprocess.run(["git", "-C", "/home/serge/src/mr-attr", "show",
                              "class6-attribution:probes/class-ports/15-attribution.out"],
                             capture_output=True, text=True, check=True).stdout
    except Exception:
        return {}
    fam, out = None, {}
    for l in txt.splitlines():
        m = re.match(r"^\s{2,4}(\d+)\s{2}(\S.*)$", l)
        if m and not re.match(r"^\s+6\.\d", l):
            fam = m.group(2).split("[")[0].strip()
            continue
        for sk in re.findall(r"(6\.\d+\.\d+) (e\d+)", l):
            out.setdefault(f"{sk[0]} {sk[1]}", fam)
    return out


def rd_arm(path, name):
    """key -> (class, t) of one arm's rows in a multi-arm fa.py run file."""
    out = {}
    for l in open(path):
        m = re.match(r"(\S+)\s+(\S+)\s+t=\s*([\d.-]+)s (.*)$", l.rstrip())
        if m and m.group(1) == name:
            out[m.group(4)] = (m.group(2), float(m.group(3)))
    return out


def main():
    fin = rd(os.path.join(H, "01-noise-final.out"))
    pre = rd(os.path.join(H, "02-arm-prefix.out"))
    arm = {a: rd(os.path.join(H, f)) for a, (f, _) in ARMS.items()}
    fix = rd(os.path.join(H, "14-arm-fixRP.out"))
    bis = {c: rd(os.path.join(H, f"08-bisect-{c}.out")) for c in BISECT}
    combos = rd_arm(os.path.join(H, "12-e1035-combos.out"), "sT_gI")
    combos2 = rd_arm(os.path.join(H, "16-unattr-combos.out"), "eqqF_revA")
    num = {}
    for l in open(os.path.join(H, "11-numcheck-final.out")):
        m = re.match(r"\S+\s+A'-f=\s*(\S+)\s+E'-f=\s*(\S+)\s+noun=\S+\s+(.*)$", l.rstrip())
        if m:   # two runs (default and --small parameter sets): keep the smaller residual
            v, prev = m.group(1), num.get(m.group(3))
            isnum = lambda z: z is not None and z not in ("err", "cap", "n/a")
            if prev is None or (isnum(v) and (not isnum(prev) or float(v) < float(prev))):
                num[m.group(3)] = v
    tr = {}
    for b in open(os.path.join(H, "10-trace-fixA-final.out")).read().split("\n\n"):
        m = re.match(r"# arm final (.*? e\d+) integrand", b)
        if m:
            tr[m.group(1)] = ("r11" if re.search(r"fired\s+1_2_3_1 r11 ", b) else
                              "cap" if "hit True" in b else "route")
    c6 = prior_class6()

    rows = []
    for r in losses():
        k = r["key"]; f = fin[k]
        fP = f[0] in P
        p = pre[k]
        why, note, first = None, "", None
        fast = any(arm[a][k][0] in P and arm[a][k][1] * 2 <= f[1] and f[1] - arm[a][k][1] >= 10 for a in ARMS)
        if fP and not fast and f[1] <= 2 * r["bt"] + 5:
            why = "noise"
            note = f"final rerun {f[0]} {f[1]:.1f}s (record {r['fin']} {r['ft']:.1f}s)"
        elif fP and not fast and r["pre"] not in P:
            why = "carried"
            fam = c6.get(short(k))
            note = (f"class-6 attribution: {fam}" if fam else "pre-fix record FAIL") + \
                f" -- the ports-era slowdown; now passes singly near the cap ({f[1]:.1f}s, base {r['bt']:.1f}s)"
        elif r["pre"] not in P and p[0] not in P:
            why = "carried"
            fam = c6.get(short(k))
            note = f"class-6 attribution: {fam}" if fam else "pre-fix record FAIL"
        else:
            rec = {}
            for a in ARMS:
                v = arm[a][k]
                if not fP and v[0] in P:
                    rec[a] = f[1] / max(v[1], 0.1)
                elif fP and v[0] in P and v[1] * 2 <= f[1] and f[1] - v[1] >= 10:
                    rec[a] = f[1] / max(v[1], 0.1)
            seq = [pre[k]] + [bis[c][k] for c in BISECT if k in bis[c]]
            if len(seq) == 1 + len(BISECT):
                for i, c in enumerate(BISECT):
                    if seq[i][0] in P and seq[i + 1][0] not in P:
                        first = BISECT_TAG[c]; break
            if fP and not rec:
                why = "noise"
            elif not rec:
                if k in combos and combos[k][0] in P:
                    why = "S+G"
                elif k in combos2 and combos2[k][0] in P:
                    why = "E+A"
                else:
                    why = "unattributed"
            else:
                if first in rec:
                    why = first
                else:
                    why = max(rec, key=rec.get)
                others = sorted(set(rec) - {why})
                if others:
                    note = "also recovered by " + ",".join(others)
        n = num.get(k)
        if short(k) == "1.2.1.2 e438":
            n = "2.97e-15"   # 18-e438-mpmath.out: the 2F1 at z > 1, checked with mpmath
        if n is not None:
            ok = n not in ("err", "cap", "n/a") and float(n) < 1e-6
            note = (note + "; " if note else "") + f"answer |dA/dx-f| {n} ({'correct' if ok else 'not shown correct'})"
        if first:
            note = (note + "; " if note else "") + f"bisect: first FAIL at {first}"
        if why == "E":
            fixfast = fix[k][0] in P and fix[k][1] * 2 <= f[1]
            sub = (("E-cost near cap: passes singly; symbolic-EqQ-free run much faster, the proposed fix too" if fixfast else
                    "E-route near cap: passes singly; symbolic-EqQ-free run much faster (a different, Rubi-divergent route), the proposed fix does not help") if fP else
                   "E-cost: zero chain factor() on radical/`if unknown` kernels -- the proposed fix recovers it"
                   if fix[k][0] in P else
                   "E-route: Rubi's EqQ reading (identically-zero condition) opens a route that times out / ends in a noun")
        elif why == "A":
            sub = ("A-cost near cap: passes singly, fix-A-free run ~20-30x faster" if fP else
                   {"r11": "A-refold: the now-completing ExpandIntegrand sum is refolded by 1_2_3_1 r11 (p_. = 1) into a quotient the seen test cuts; ends in a noun",
                    "cap": "A-cost: the now-completing ExpandIntegrand route runs past the cap",
                    "route": "A-route: the now-completing expansion ends in a partial answer (noun) / unverified form"}
                   .get(tr.get(k), "A-route: the now-completing expansion ends in a partial answer (noun) / unverified form"))
        elif why == "E+A":
            sub = "E+A: needs both the symbolic EqQ and fix A reverted"
        elif why == "G":
            sub = ("G-answer: two-valued GtQ fires a reduction Rubi's corpus answer does not take (answer correct, not Rubi's)"
                   if r["fin"] in ("unverified", "unexpected") else
                   "G-route: two-valued GtQ (Rubi's reading) fires a reduction that ends in a noun / times out")
        elif why == "S":
            sub = ("S-verify: plain Subst leaves an unsimplified but correct answer the zero chain cannot close"
                   if r["fin"] == "unverified" else "S-cost: plain Subst route runs past the cap")
        elif why == "S+G":
            sub = "S+G WRONG ANSWER: degenerate integrand (x^4 coefficient 2+2c-2(1+c) = 0) reaches 1_1_3_2 r8"
        elif why == "carried":
            sub = "carried: " + note
            note = ""
        else:
            sub = why
        rows.append((r, why, sub or why, note, f))

    print("# final class-ports re-measure: PASS->FAIL attribution (182 losses)")
    print("# core 89bec424 (c2deb32), build branch_5_50_base_84_g4204fb669, 2026-09-26")
    print("# bucket = the change that caused the loss (see attribution.py for the rules)\n")
    print(FINDINGS)
    by = defaultdict(lambda: defaultdict(list))
    for r, why, sub, note, f in rows:
        by[r["cls"]][sub].append((r, note, f))
    tot = defaultdict(int)
    for c in (1, 2, 3, 6, 5, 7, 4):
        n = sum(len(v) for v in by[c].values())
        base = "master" if c in (1, 2, 3, 6) else "pre-fix class-ports"
        print(f"=== class {c}: {n} losses (vs {base} record)")
        for sub, lst in sorted(by[c].items(), key=lambda t: -len(t[1])):
            print(f"  {len(lst):3d}  {sub}")
            tot[sub] += len(lst)
            for r, note, f in lst:
                arms = " ".join(f"{a}:{'P' if arm[a][r['key']][0] in P else 'F'}{arm[a][r['key']][1]:.0f}" for a in ARMS)
                print(f"       {short(r['key']):16s} {r['base']:>13s} {r['bt']:5.1f}s -> {r['fin']:13s} {r['ft']:5.1f}s | rerun {f[0]} {f[1]:.1f}s | pre {pre[r['key']][0][:4]} {pre[r['key']][1]:.1f}s | {arms} | fixRP {'P' if fix[r['key']][0] in P else 'F'} {('| ' + note) if note else ''}")
        print()
    print("=== all classes, by bucket")
    for sub, n in sorted(tot.items(), key=lambda t: -t[1]):
        print(f"  {n:3d}  {sub}")
    print(f"  {sum(tot.values()):3d}  TOTAL")


def recheck():
    """The four 100 s timeout re-checks of the final records (test/corpus_class<N>
    .final.timeout-rerun/): transitions of the record's timeout class."""
    R = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)$")
    root = os.path.dirname(os.path.dirname(os.path.dirname(H)))
    print("\n=== 100 s timeout re-checks of the final records (same core, same switches)")
    for c in (8, 5, 7, 4):
        fin, rr = {}, {}
        for l in open(os.path.join(root, f"test/corpus_class{c}.final.out")):
            m = R.match(l.rstrip())
            if m:
                fin[(m.group(3), m.group(4))] = m.group(1)
        for l in open(os.path.join(root, f"test/corpus_class{c}.final.timeout-rerun/corpus_class{c}.final.timeout100s.out")):
            m = R.match(l.rstrip())
            if m:
                rr[(m.group(3), m.group(4))] = m.group(1)
        nt = sum(1 for v in fin.values() if v == "timeout")
        assert all(fin[k] == "timeout" for k in rr)
        cnt = defaultdict(int)
        for v in rr.values():
            cnt[v] += 1
        now = sum(v for kk, v in cnt.items() if kk in P)
        oth = {kk: v for kk, v in cnt.items() if kk not in P and kk != "timeout"}
        print(f"  class {c}: {len(rr)}/{nt} record timeouts re-checked -> now-PASS {now} (slow-correct: "
              + ", ".join(f"{kk} {v}" for kk, v in sorted(cnt.items()) if kk in P)
              + f"); still timeout {cnt['timeout']}; other {sum(oth.values())} ("
              + ", ".join(f"{kk} {v}" for kk, v in sorted(oth.items())) + ")")


if __name__ == "__main__":
    main()
    recheck()
