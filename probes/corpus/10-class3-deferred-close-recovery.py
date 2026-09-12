#!/usr/bin/env python3
"""10-class3-deferred-close-recovery — the class-3 deferred campaign
close's record join (docs/corpus-class3-deferred-uplift.md §5-§6): the
class-3 A/B at the deferred-population level and the 788/329
target-mass recovery, per file, per verdict class and per fix row.

Inputs (committed records only — no Maxima subprocess):
  test/corpus_class3.campaign-baseline.out   pre-campaign package record
      (the milestone-3 accepted run, merged 2026-08-30, core 00e05dca;
      holds the 1,033-entry deferred population — the plan's Task 5
      Step 1 backup of the record the 06/07/08 probes triaged)
  test/corpus_class3.baseline.out            the integrate baseline
      (the target flags: verified/expected/unverified = target mass)
  test/corpus_class3.out                     the campaign-close record
      (merged 2026-09-04 15:06 UTC, core 5ef9b3bc)
  test/corpus_class3_c6base.out / test/corpus_class3_c6post.out
      the committed mid-campaign records (2026-09-02; C5/C6 cores)
Entry sets: probe 08's transcription of the decision record (SETS;
PARTIAL classes join only their enumerated entries, flagged as such).

Sections 9-10 (added in the acceptance record's review round 1): the
close class of every fix row's unrecovered entries, and the target
residue per file x verdict class (the §6.3 why-not counts, measured
inside the residue rather than as pre-campaign file categories).

Output: probes/corpus/10-class3-deferred-close-recovery.out
Re-run: deterministic."""

import hashlib
import importlib.util
import os
import subprocess
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SLUG = "10-class3-deferred-close-recovery"
OUT = os.path.join(ROOT, "probes", "corpus", SLUG + ".out")


def T(name):
    return os.path.join(ROOT, "test", name)


PRE = T("corpus_class3.campaign-baseline.out")
FINAL = T("corpus_class3.out")
INTEG = T("corpus_class3.baseline.out")
MID = [("c6base", T("corpus_class3_c6base.out")),
       ("c6post", T("corpus_class3_c6post.out"))]

# The imported probes import the driver (module-level core resolution);
# this join uses no core — force the driver's standard-load state so the
# import never builds or pins one.
os.environ.pop("MR_RULES_CORE_PATH", None)
os.environ["MR_RULES_CORE"] = "0"


def load_mod(name, fn):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(ROOT, "probes", "corpus", fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


p8 = load_mod("p8split", "08-class3-deferred-verdict-flag-split.py")
p6 = p8.p6
PASSC = p6.driver.PASS_CLASSES
TARGET = set(p6.FLAG_CLASSES)
CERTAIN = {"verified", "expected"}

# g4 C-in-Rubi sub-lists, in probe 08's order (record §2 wave 4 table).
C6_GROUPS = ["M-implicit1", "M-plus-identity", "M-barelog-optional",
             "M-cas-simp", "M-factored-quad", "M-functionoflog",
             "M-class4", "M-multistep", "M-323"]
C6_SIZES = [3, 2, 1, 2, 3, 12, 5, 1, 2]
C4_NUMS = {124, 131, 274, 268} | set(range(210, 219))


def keys_of(pairs):
    out = []
    for prefix, nums in pairs:
        rel = p8.rel_of(prefix)
        out.extend((rel, n) for n in nums)
    return out


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def results(path):
    return next(ln.strip() for ln in open(path) if ln.startswith("Results:"))


def short(rel):
    return rel.split("/", 1)[1].split(" ", 1)[0]


def main():
    assert os.path.abspath(p6.PKG_RECORD) == PRE, p6.PKG_RECORD
    deferred, flags = p6.deferred_set()   # asserts 1033 / 788 / 313+16+459
    dkeys = [k for k, _t in deferred]
    _i, pre = p6.load_record(PRE)
    _i, fin = p6.load_record(FINAL)
    _i, integ = p6.load_record(INTEG)
    mids = {n: p6.load_record(p)[1] for n, p in MID}
    assert set(pre) == set(fin) == set(integ) and len(pre) == 3085
    for n in mids:
        assert set(mids[n]) == set(pre)

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()
    L = [f"=== class-3 deferred campaign close — record join ({SLUG}) ===",
         f"run date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
         f"  git HEAD: {head or 'n/a'}  (no Maxima subprocess)"]
    for label, path in [("pre ", PRE), ("final", FINAL), ("integ", INTEG)] + \
            [(n, p) for n, p in MID]:
        L.append(f"record {label:6s} {os.path.relpath(path, ROOT)}  md5 {md5(path)}  "
                 f"{results(path)}")
    L.append("")

    # 1. whole-record PASS/FAIL 2x2 (pre -> final); must agree with
    #    test/ab_records.py on the same two records.
    tab = Counter((pre[k][0] in PASSC, fin[k][0] in PASSC) for k in pre)
    L += ["--- 1. whole record, pre -> final (PASS = expected/verified/no-answer) ---",
          f"PASS->PASS {tab[(True, True)]:5d}",
          f"PASS->FAIL {tab[(True, False)]:5d}",
          f"FAIL->PASS {tab[(False, True)]:5d}",
          f"FAIL->FAIL {tab[(False, False)]:5d}", ""]
    pf = sorted(k for k in pre if pre[k][0] in PASSC and fin[k][0] not in PASSC)
    fp = sorted(k for k in pre if pre[k][0] not in PASSC and fin[k][0] in PASSC)
    L.append(f"FAIL->PASS from the deferred population: "
             f"{sum(1 for k in fp if pre[k][0] == 'deferred')} of {len(fp)}")
    L.append("")

    # 2. the deferred population (1,033) by target flag -> final class.
    groups = [
        ("all deferred", dkeys),
        ("target (788)", [k for k in dkeys if flags[k] in TARGET]),
        ("certain (329)", [k for k in dkeys if flags[k] in CERTAIN]),
        ("unverified (459)", [k for k in dkeys if flags[k] == "unverified"]),
        ("non-target (245)", [k for k in dkeys if flags[k] not in TARGET]),
    ]
    L.append("--- 2. deferred population (pre record) -> final class ---")
    for name, ks in groups:
        c = Counter(fin[k][0] for k in ks)
        rec = sum(v for cl, v in c.items() if cl in PASSC)
        L.append(f"{name:17s} n={len(ks):4d} recovered={rec:4d} "
                 f"still-deferred={c['deferred']:4d}  final: "
                 + " ".join(f"{cl}={c[cl]}" for cl in sorted(c)))
    L.append("")

    # 3. per file: target / certain recovery + the residue by final class.
    L.append("--- 3. per file (deferred population) ---")
    files = sorted({k[0] for k in dkeys})
    for rel in files:
        for gname, gset in [("target", TARGET), ("certain", CERTAIN)]:
            ks = [k for k in dkeys if k[0] == rel and flags[k] in gset]
            c = Counter(fin[k][0] for k in ks)
            rec = sum(v for cl, v in c.items() if cl in PASSC)
            resid = " ".join(f"{cl}={c[cl]}" for cl in sorted(c)
                             if cl not in PASSC)
            L.append(f"{short(rel):6s} {gname:7s} n={len(ks):4d} "
                     f"recovered={rec:4d} residue: {resid or '-'}")
        ks = [k for k in dkeys if k[0] == rel]
        c = Counter(fin[k][0] for k in ks)
        rec = sum(v for cl, v in c.items() if cl in PASSC)
        L.append(f"{short(rel):6s} all     n={len(ks):4d} recovered={rec:4d} "
                 f"still-deferred={c['deferred']}")
    L.append("")

    # 4. the final record's own deferred mass, flagged the same way
    #    (the new "788" / "329").
    fdef = [k for k in fin if fin[k][0] == "deferred"]
    new_t = [k for k in fdef if integ[k][0] in TARGET]
    new_c = [k for k in fdef if integ[k][0] in CERTAIN]
    newly = [k for k in fdef if pre[k][0] != "deferred"]
    L += ["--- 4. final record deferred mass (flags from the integrate baseline) ---",
          f"deferred={len(fdef)}  target={len(new_t)}  certain={len(new_c)}  "
          f"unverified-flag={sum(1 for k in new_t if integ[k][0] == 'unverified')}",
          f"of which deferred in the pre record: {len(fdef) - len(newly)}; "
          f"newly deferred (pre class != deferred): {len(newly)} "
          + str(dict(Counter(pre[k][0] for k in newly))),
          f"newly deferred per file: "
          + str(dict(Counter(short(k[0]) for k in newly))), ""]

    # 5. per verdict class (probe 08 enumerated sets).
    def row(name, ks, complete, claim):
        c = Counter(fin[k][0] for k in ks)
        rec = sum(v for cl, v in c.items() if cl in PASSC)
        tks = [k for k in ks if flags[k] in TARGET]
        cks = [k for k in ks if flags[k] in CERTAIN]
        trec = sum(1 for k in tks if fin[k][0] in PASSC)
        crec = sum(1 for k in cks if fin[k][0] in PASSC)
        return (f"{name:34s} enum={len(ks):4d}/{claim:<4d} "
                f"{'complete' if complete else 'PARTIAL '} "
                f"recovered={rec:4d} target={trec:3d}/{len(tks):<3d} "
                f"certain={crec:3d}/{len(cks):<3d} "
                f"still-deferred={c['deferred']:3d}")

    L.append("--- 5. per verdict class x wave (probe 08 sets) ---")
    for wave in ("g1", "g2", "g3", "g4"):
        for cls in sorted(p8.CLAIMED[wave]):
            complete, pairs = p8.SETS[wave].get(cls, (False, []))
            L.append(row(f"{wave} {cls}", keys_of(pairs), complete,
                         p8.CLAIMED[wave][cls]))
    L.append("")

    # 6. per fix row (record §3.2 B1-B4 / §3.3 C1-C6), enumerated portions.
    g1c = p8.SETS["g1"]["C-in-Rubi"][1]
    g2c = keys_of(p8.SETS["g2"]["C-in-Rubi"][1])
    f21 = p8.rel_of(p8.F21)
    c4 = [k for k in g2c if k[0] == f21 and k[1] in C4_NUMS]
    c3 = [k for k in g2c if k not in c4]
    assert len(c4) == 13 and len(c3) == 99, (len(c4), len(c3))
    c2 = keys_of([pr for pr in g1c if pr[0] == p8.F12])
    c1 = keys_of([pr for pr in g1c if pr[0] != p8.F12])
    assert len(c2) == 3
    b1 = keys_of(p8.SETS["g1"]["B-port"][1]) + keys_of(p8.SETS["g4"]["B-port"][1])
    b2 = keys_of(p8.SETS["g2"]["B-port"][1])
    b4 = keys_of(p8.SETS["g3"]["B-port"][1])
    c6 = keys_of(p8.SETS["g4"]["C-in-Rubi"][1])
    a10 = (keys_of(p8.SETS["g1"]["A"][1]) + keys_of(p8.SETS["g2"]["A"][1])
           + keys_of(p8.SETS["g3"]["A"][1]))
    f33 = p8.rel_of(p8.F33)
    f34 = p8.rel_of(p8.F34)
    L.append("--- 6. per fix row (enumerated portions; B3/C5 and the 81 3_4 "
             "spurious-freeof rows are not enumerated — file rows) ---")
    fixrows = [
        ("B1 (g1 2 + g4 41 enumerated)", b1, True, 124),
        ("B2 (g2 B-port)", b2, True, 47),
        ("B4 (e392)", b4, True, 1),
        ("C1 (g1 M1, enumerated part)", c1, False, 209),
        ("C2 (g1 M6)", c2, True, 3),
        ("C3 (g2 D2)", c3, True, 99),
        ("C4 (g2 D3/D4)", c4, True, 13),
        ("C6+C6b (g4 C-in-Rubi, 9 groups)", c6, True, 31),
        ("A (pass-4 NO-GO, 10)", a10, True, 10),
        ("file 3.3 (B3 125 + D16 + A1 + P18)",
         [k for k in dkeys if k[0] == f33], True, 160),
        ("file 3.4 (B 82 + C5 128 + CA 20 + P5)",
         [k for k in dkeys if k[0] == f34], True, 235),
    ]
    for name, ks, complete, claim in fixrows:
        L.append(row(name, ks, complete, claim))
    L.append("")

    # 7. the C6 mechanism groups, per entry (+ e47 PENDING, A-shaped).
    L.append("--- 7. C6 groups per entry (pre class / c6post / final; flag) ---")
    assert [len(nums) for _p, nums in p8.SETS["g4"]["C-in-Rubi"][1]] == C6_SIZES
    for gname, (prefix, nums) in zip(C6_GROUPS, p8.SETS["g4"]["C-in-Rubi"][1]):
        rel = p8.rel_of(prefix)
        cells = []
        for n in nums:
            k = (rel, n)
            cells.append(f"e{n}:{pre[k][0]}/{mids['c6post'][k][0]}/"
                         f"{fin[k][0]}({flags[k]})")
        L.append(f"{gname:19s} " + "  ".join(cells))
    k47 = (p8.rel_of(p8.F15), 47)
    L.append(f"e47 (3.1.5 PENDING, A-shaped): pre={pre[k47][0]} "
             f"t={pre[k47][1]}  final={fin[k47][0]} t={fin[k47][1]}  "
             f"flag={flags[k47]}")
    L.append("")

    # 8. the PASS->FAIL list against the committed mid-campaign records.
    L.append("--- 8. PASS->FAIL (pre -> final) x mid-campaign records "
             "(c6base mostly C5 core, c6post C6 core; P/F) ---")
    cnt = Counter()
    for k in pf:
        s = "".join("P" if mids[n][k][0] in PASSC else "F"
                    for n in ("c6base", "c6post"))
        cnt[(short(k[0]), pre[k][0], fin[k][0], s)] += 1
    for (fn, a, b, s), v in sorted(cnt.items()):
        L.append(f"{v:4d}  {fn:6s} {a:10s} -> {b:14s} c6base/c6post={s}")
    L.append(f"total PASS->FAIL {len(pf)}")
    L.append("")

    # 9. per fix row: the close-record class of the entries NOT recovered
    #    (record §6.2 readings), all and target-flagged, per file.
    L.append("--- 9. per fix row: close class of the unrecovered entries "
             "(file:class=n) ---")
    for name, ks, _complete, _claim in fixrows:
        un = [k for k in ks if fin[k][0] not in PASSC]
        for lab, sel in (("all", un), ("target", [k for k in un if flags[k] in TARGET])):
            c = Counter((short(k[0]), fin[k][0]) for k in sel)
            L.append(f"{name:34s} {lab:6s} unrecovered={len(sel):4d}  "
                     + (" ".join(f"{fn}:{cl}={v}" for (fn, cl), v in sorted(c.items()))
                        or "-"))
    L.append("")

    # 10. the target residue per file x verdict class (record §6.3 why-not).
    #     residue = target-flagged deferred-population entries whose close
    #     class is not PASS. Per class: the file's claimed count (record §2
    #     per-family tables), the enumerated count (probe 08 SETS), and the
    #     residue entries inside the enumeration (close class + entry
    #     numbers). Residue entries in no enumerated set are counted once;
    #     when only one class has an unenumerated remainder in the file,
    #     they belong to that class by elimination.
    FILE_CLAIMED = {  # A, B-port, C-in-Rubi, C-absent, D, PENDING
        "3.1.2": (0, 0, 3, 0, 6, 0), "3.1.4": (0, 2, 194, 0, 34, 0),
        "3.1.5": (4, 0, 15, 0, 21, 1), "3.2.1": (5, 28, 31, 12, 15, 0),
        "3.2.2": (0, 19, 79, 2, 38, 0), "3.2.3": (0, 0, 2, 3, 27, 4),
        "3.3": (1, 125, 0, 0, 16, 18), "3.4": (0, 82, 128, 20, 0, 5),
        "3.5": (0, 41, 31, 4, 17, 0)}
    CLS = ["A", "B-port", "C-in-Rubi", "C-absent", "D", "PENDING"]
    SUB = {  # sub-list labels for the multi-mechanism enumerations
        ("g1", "C-in-Rubi"): lambda pr, i: "C2 M6" if pr == p8.F12 else "C1 M1",
        ("g2", "C-in-Rubi"): None,   # split C3/C4 by C4_NUMS below
        ("g4", "C-in-Rubi"): lambda pr, i: C6_GROUPS[i],
        ("g4", "B-port"): lambda pr, i: ["r31_u", "r35_u", "r37_u"][i],
    }
    member = {}
    for wave in ("g1", "g2", "g3", "g4"):
        for cls, (_c, pairs) in p8.SETS[wave].items():
            for i, (prefix, nums) in enumerate(pairs):
                rel = p8.rel_of(prefix)
                for n in nums:
                    k = (rel, n)
                    assert k not in member, k
                    f = SUB.get((wave, cls))
                    if (wave, cls) == ("g2", "C-in-Rubi"):
                        sub = "C4 D3/D4" if (rel == f21 and n in C4_NUMS) else "C3 D2"
                    elif f is not None:
                        sub = f(prefix, i)
                    else:
                        sub = ""
                    member[k] = (cls, sub)
    L.append("--- 10. target residue per file x verdict class (probe 08 sets; "
             "record §2 per-family claims) ---")
    for rel in files:
        fn = short(rel)
        allf = [k for k in dkeys if k[0] == rel]
        assert len(allf) == sum(FILE_CLAIMED[fn]), (fn, len(allf))
        res = [k for k in allf if flags[k] in TARGET and fin[k][0] not in PASSC]
        cres = Counter(fin[k][0] for k in res)
        L.append(f"{fn} target residue n={len(res)} ("
                 + " ".join(f"{cl}={cres[cl]}" for cl in sorted(cres)) + ")")
        remainder = {}
        for ci, cls in enumerate(CLS):
            claimed = FILE_CLAIMED[fn][ci]
            enum = [k for k in allf if member.get(k, ("",))[0] == cls]
            assert len(enum) <= claimed, (fn, cls, len(enum), claimed)
            if claimed - len(enum):
                remainder[cls] = claimed - len(enum)
            if not claimed:
                continue
            inres = [k for k in res if member.get(k, ("",))[0] == cls]
            subs = Counter(member[k][1] for k in inres)
            L.append(f"  {cls:9s} claimed={claimed:3d} enum={len(enum):3d} "
                     f"target-in-enum={sum(1 for k in enum if flags[k] in TARGET):3d} "
                     f"residue-in-enum={len(inres):3d}"
                     + (" [" + " ".join(f"{s}={v}" for s, v in sorted(subs.items()) if s)
                        + "]" if any(subs) else ""))
            for cl in sorted({fin[k][0] for k in inres}):
                nums = sorted(k[1] for k in inres if fin[k][0] == cl)
                L.append(f"      {cl:10s} {len(nums):3d}: " + " ".join(f"e{n}" for n in nums))
        unen = [k for k in res if k not in member]
        cun = Counter(fin[k][0] for k in unen)
        who = ("=> " + next(iter(remainder)) + " (by elimination)"
               if len(remainder) == 1 else
               "mixed: " + " ".join(f"{c}+{v}" for c, v in remainder.items())
               if remainder else "-")
        L.append(f"  not enumerated: residue={len(unen):3d} ("
                 + (" ".join(f"{cl}={cun[cl]}" for cl in sorted(cun)) or "-")
                 + f")  unenumerated claimed remainder: {who}")
    L.append("")

    txt = "\n".join(L) + "\n"
    open(OUT, "w", encoding="utf-8").write(txt)
    print(txt, end="")


if __name__ == "__main__":
    main()
