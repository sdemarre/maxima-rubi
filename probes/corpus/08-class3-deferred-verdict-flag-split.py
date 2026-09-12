#!/usr/bin/env python3
"""08-class3-deferred-verdict-flag-split — the Phase-2 record's
per-verdict-class recompute of the 788/329 target-mass split (plan
Task 3 Step 2: "the class totals must sum to 1,033; the 788/329
split recomputed per class").

Method: the four adjudication files
(probes/corpus/06-class3-deferred-mechanisms.work/adjudication-gN.md)
enumerate the entry sets of most verdict classes explicitly (some
big clusters carry "n=K" + a partial list + ellipsis — those are
transcribed as PARTIAL below and are NOT asserted complete). This
script hard-codes those enumerated sets (transcribed from the
decision record's source), joins them to the committed baseline
record's per-entry target flags, and reports, per class:
  enumerated / claimed / complete? / flag split
 / target-mass count / certain-subset (329) count.

Guards: every enumerated (rel, n) must sit in the pinned 1,033
deferred population; within a wave the class sets are pairwise
disjoint; complete classes assert enumerated == claimed; the
baseline's pinned 788 = 313+16+459 / 329 = 313+16 split is
re-asserted from the record.

Output: probes/corpus/08-class3-deferred-verdict-flag-split.out
Re-run: deterministic (no Maxima subprocess — record join only)."""

import importlib.util
import os
import sys
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SLUG = "08-class3-deferred-verdict-flag-split"
OUT = os.path.join(ROOT, "probes", "corpus", SLUG + ".out")
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")

_spec = importlib.util.spec_from_file_location(
    "p4mech", os.path.join(ROOT, "probes", "corpus",
                           "06-class3-deferred-mechanisms.py"))
assert _spec is not None and _spec.loader is not None
p6 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(p6)


def rng(*specs):
    """Ints and (a, b) inclusive ranges -> sorted list of ints."""
    out = []
    for s in specs:
        if isinstance(s, tuple):
            a, b = s
            assert a <= b, f"bad range {s}"
            out.extend(range(a, b + 1))
        else:
            out.append(s)
    return sorted(out)


# rel resolution: distinctive prefix -> the suite file (glob-checked).
REL = {}


def rel_of(prefix):
    if prefix in REL:
        return REL[prefix]
    hits = [p for p in p6.suite_map() if p.startswith("3 Logarithms/" + prefix)]
    assert len(hits) == 1, f"{prefix}: {hits}"
    REL[prefix] = hits[0]
    return hits[0]


F12 = "3.1.2 (d x)^m"
F14 = "3.1.4 (f x)^m"
F15 = "3.1.5 u (a+b log"
F21 = "3.2.1 (f+g x)^m (A+B"
F22 = "3.2.2 (f+g x)^m (h+i"
F23 = "3.2.3 u log(e"
F33 = "3.3 u (a+b log"
F34 = "3.4 u (a+b log"
F35 = "3.5 Logarithm"

# The decision record's enumerated entry sets, per (wave, class).
# (prefix, [entries]) pairs; a class is a list of such pairs.
# complete=True  -> the enumeration IS the class (asserted).
# complete=False -> partial (the wave file carries the cluster's
#                   full count with an ellipsis; only the listed
#                   entries join here).
SETS = {
    "g1": {
        "A": (True, [(F15, rng(5, 91, 209, 215))]),
        "B-port": (True, [(F14, rng(275, 317))]),
        "C-in-Rubi": (False, [
            (F12, rng(65, 66, 67)),
            (F14, rng(1, 172, 2, 178, 9, 10, 11, 19, 20, 21, 171, 177,
                      183, 184, 185, 189, 190, 196, 197, 198, 202, 203,
                      367, 368, 373, 374, 379, 380, 381, 385, 386,
                      392, 393, 394, 398, 399,
                      130, 131, 137, 138, 139, 251, 252, 256, 257,
                      263, 264, 265, 268, 387, 400, 446,
                      14, 15, 16, 24, 25, 26,
                      17, 18, 28, 29, 30, 36,
                      132, 135, 142, 143, 148,
                      136, 149, 150, 156,
                      144, 145, 146, 153,
                      186, 187, 188, 192, 193, 194,
                      253,
                      254, 255, 260, 261, 262, 266,
                      259, 270, 271, 281, 292, 303,
                      370, 371, 372, 376, 377, 378)),
            (F15, rng(90, 95, 115,
                      92, 93, 94, 97, 98, 99, 118, 119, 120, 121,
                      141, 147)),
        ]),
        "D": (False, [
            (F12, rng(162, 163, 164, 165, 166, 191)),
            (F14, rng(5, 6, 7, 8, 174, 175,
                      31, 32, 33, 41, 48,
                      282)),
            (F15, rng(194, 195, 196, 197,
                      1, 249, 96, 243, 244, 247, 248,
                      13, 20, 54, 59, 123, 128, 74, 80, 86,
                      180)),
        ]),
        "PENDING": (True, [(F15, rng(47))]),
    },
    "g2": {
        "A": (True, [(F21, rng(122, 150, 204, 265, 296))]),
        "B-port": (True, [
            (F21, rng(156, 157, 158, 164, 165, 166, 303, 304, 309, 310,
                      159, 160, 161, 162, 163, 167, 168, 169, 170, 171,
                      172, 229, 306, 307, 308, 312, 313, 314)),
            (F22, rng(226, 227, 228, 229, 232, 233, 234, 235, 240, 249,
                      250, 251, 253, 254,
                      236, 259, 260, 262, 263)),
        ]),
        "C-in-Rubi": (True, [
            (F21, rng(93, 101, 102, 103, 104, 105,
                      178, 186, 187, 188, 189, 190,
                      236, 244, 245, 246, 247, 248,
                      124, 131, 274, (210, 218), 268)),
            (F22, rng(10, 11, (14, 21), (24, 30), 31, 32, (35, 40),
                      (43, 48), (51, 54), 42,
                      (59, 63), (68, 73), (78, 83), (84, 107),
                      214, 220)),
            (F23, rng(104, 107)),
        ]),
        "C-absent": (True, [
            (F21, rng(112, 113, 117, 118, 194, 195, 199, 200, 222, 223,
                      227, 228)),
            (F22, rng(243, 247)),
            (F23, rng(89, 102, 106)),
        ]),
        "D": (True, [
            (F21, rng(249, 91, 176, 233, 97, 98, 99, 100,
                      182, 183, 184, 185, 240, 241, 242)),
            (F22, rng(1, 2, (3, 9), 12, 22, 33, 41, 49, (113, 116), 119,
                      129, 137, 145, 153, 230, 252, 261,
                      (55, 58), (64, 67), (74, 77))),
            (F23, rng(21, 22, 23, 24, 40, 41, 42, 1, 2, 4, 5, 6,
                      76, 80, 58, 64, 70,
                      69, 78, 86, 72, 73, 90, 91, 103, 105, 108)),
        ]),
        "PENDING": (True, [(F23, rng(82, 83, 84, 87))]),
    },
    "g3": {
        "A": (True, [(F33, rng(360))]),
        "B-port": (False, [(F34, rng(392))]),
        "C-in-Rubi": (False, []),
        "C-absent": (False, [
            (F34, rng(123, 124, 125, 126, 127, 128, 535, 547, 548, 549,
                      559, 585, 586, 587)),
        ]),
        "D": (True, [
            (F33, rng(234, 283, 284, 285, 286, 293, 294, 295,
                      329, 330, 332, 347, 348, 350, 371, 372)),
        ]),
        "PENDING": (True, [
            (F33, rng(287, 288, 289, 290, 291, 292, 296, 297, 298, 299,
                      301, 302, 351, 352, 353, 355, 356, 357)),
            (F34, rng(100, 292, 343, 354, 618)),
        ]),
    },
    "g4": {
        "B-port": (True, [
            (F35, rng(116, 126, 193, 207, 211, 234, 294, 295, 297, 298)),
            (F35, rng(94, 95, 276, 278, 279)),
            (F35, rng(113, 114, 115, 154, 155, 156, 157, 158, 159,
                      179, 182, 184, 188, 189, 190, 191, 192, 194,
                      195, 196, 197, 198, 199, 200, 284, 285)),
        ]),
        "C-in-Rubi": (True, [
            (F35, rng(11, 49, 139)),
            (F35, rng(56, 58)),
            (F35, rng(266)),
            (F35, rng(92, 93)),
            (F35, rng(103, 106, 107)),
            (F35, rng(134, 135, 136, 140, 143, 149, 150, 151, 152,
                      225, 258, 261)),
            (F35, rng(180, 181, 183, 186, 187)),
            (F35, rng(98)),
            (F35, rng(243, 244)),
        ]),
        "C-absent": (True, [(F35, rng(19, 34, 272, 300))]),
        "D": (True, [
            (F35, rng(13, 251, 252, 253, 301, 302)),
            (F35, rng(40, 41, 42, 43, 44, 45, 238, 273, 259, 280, 281)),
        ]),
    },
}

# The post-reclassification claimed class totals (the four wave files'
# Reconciliation tables; machine-checked 2026-08-31 to 1,033).
CLAIMED = {
    "g1": {"A": 4, "B-port": 2, "C-in-Rubi": 212, "D": 61, "PENDING": 1},
    "g2": {"A": 5, "B-port": 47, "C-in-Rubi": 112, "C-absent": 17,
           "D": 80, "PENDING": 4},
    "g3": {"A": 1, "B-port": 207, "C-in-Rubi": 128, "C-absent": 20,
           "D": 16, "PENDING": 23},
    "g4": {"B-port": 41, "C-in-Rubi": 31, "C-absent": 4, "D": 17},
}
GRAND = {"A": 10, "B-port": 297, "C-in-Rubi": 483, "C-absent": 41,
         "D": 174, "PENDING": 28}


def main():
    deferred, flags = p6.deferred_set()
    deferred_keys = {(rel, n) for (rel, n), _t in deferred}
    split = Counter(flags[k] for k in deferred_keys
                    if flags[k] in p6.FLAG_CLASSES)
    assert sum(split.values()) == 788, dict(split)
    assert split["verified"] + split["expected"] == 329, dict(split)

    lines = [
        f"=== class-3 deferred verdict x target-flag split ({SLUG}) ===",
        f"run date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"baseline record: test/corpus_class3.baseline.out "
        f"(re-asserted 788 = 313+16+459, 329 = 313+16)",
        "method: the decision record's enumerated entry sets "
        "(adjudication-g1..g4.md, transcribed) joined to the "
        "baseline per-entry flags; PARTIAL classes enumerate only "
        "the explicitly listed entries (wave file carries the "
        "cluster count + ellipsis) and are not asserted complete",
        "",
    ]
    class_tot = Counter()
    flagged = Counter()
    certain = Counter()
    for wave in ("g1", "g2", "g3", "g4"):
        seen = {}
        for cls in sorted(CLAIMED[wave]):
            complete, pairs = SETS[wave].get(cls, (False, []))
            keys = []
            for prefix, nums in pairs:
                full = rel_of(prefix)
                for n in nums:
                    keys.append((full, n))
            for k in keys:
                assert k in deferred_keys, \
                    f"{wave}/{cls}: {k} not in the deferred population"
                assert k not in seen, \
                    f"{wave}/{cls}: {k} duplicated across class sets"
                seen[k] = cls
            n_enum = len(keys)
            n_claim = CLAIMED[wave][cls]
            if complete:
                assert n_enum == n_claim, \
                    f"{wave}/{cls}: enumerated {n_enum} != claimed {n_claim}"
            else:
                assert n_enum <= n_claim, \
                    f"{wave}/{cls}: enumerated {n_enum} > claimed {n_claim}"
            fl = Counter(flags[k] for k in keys)
            tgt = sum(fl[g] for g in p6.FLAG_CLASSES)
            cert = fl.get("verified", 0) + fl.get("expected", 0)
            class_tot[cls] += n_enum
            flagged[cls] += tgt
            certain[cls] += cert
            rem = (fl.get("no-answer", 0) + fl.get("timeout", 0)
                   + fl.get("error", 0))
            lines.append(
                f"{wave} {cls:11s} enum={n_enum:4d} claim={n_claim:4d} "
                f"{'complete' if complete else 'PARTIAL '}  "
                f"verified={fl.get('verified', 0):3d} "
                f"expected={fl.get('expected', 0):2d} "
                f"unverified={fl.get('unverified', 0):3d} "
                f"target={tgt:4d} certain={cert:3d} remainder={rem:3d}")
        lines.append("")
    lines += [
        "--- totals (enumerated portion) ---",
        f"{'class':11s} {'enum':>5s} {'claim':>5s} {'target(788)':>12s} "
        f"{'certain(329)':>13s}",
    ]
    claim_tot = Counter()
    for wave in ("g1", "g2", "g3", "g4"):
        for cls, n in CLAIMED[wave].items():
            claim_tot[cls] += n
    for cls in sorted(GRAND):
        lines.append(
            f"{cls:11s} {class_tot[cls]:5d} {claim_tot[cls]:5d} "
            f"{flagged[cls]:12d} {certain[cls]:13d}")
    lines += [
        f"{'total':11s} {sum(class_tot.values()):5d} "
        f"{sum(claim_tot.values()):5d} {sum(flagged.values()):12d} "
        f"{sum(certain.values()):13d}",
        "",
        "claim totals must equal the post-reclassification grand "
        f"total {dict(sorted(GRAND.items()))} summing to 1033",
    ]
    assert dict(claim_tot) == GRAND, dict(claim_tot)
    assert sum(claim_tot.values()) == 1033
    # The 788/329 cross-check against the committed triage record's
    # label x flag table (the handoff's verification line): the .out's
    # own total row.
    out6 = open(os.path.join(ROOT, "probes", "corpus",
                             "06-class3-deferred-mechanisms.out"),
                encoding="utf-8").read()
    tot_row = [l for l in out6.splitlines()
               if l.startswith("total              1033")]
    assert len(tot_row) == 1, "06 total row moved"
    cols = tot_row[0].split()
    nums = [int(c) for c in cols[2:8]]
    assert nums == [313, 16, 459, 150, 76, 19], nums
    assert nums[0] + nums[1] + nums[2] == 788
    assert nums[0] + nums[1] == 329
    lines.append("06 record total row verified: "
                 f"{' '.join(str(n) for n in nums)} "
                 "(313+16+459=788 target, 313+16=329 certain)")
    lines.append("")
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
