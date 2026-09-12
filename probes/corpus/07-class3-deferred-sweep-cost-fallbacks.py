#!/usr/bin/env python3
"""07-class3-deferred-sweep-cost-fallbacks — the Phase-2 cost fallbacks
for the class-3 deferred campaign's pass 4 (plan Task 3 Step 3),
measured on the 37 entries probe 06 swept (the only entries whose
sweep does work).

Context: 06's committed sweep-cost line (n=37, mean 13.06 s,
p95 46.50 s) fails the plan's cost gate (p95 added <= 3 s AND mean
added <= 1 s). Plan Step 3 then offers ordered cost fallbacks and
requires the record to state which rule fired on the numbers:

  (a) k = 3 factor bound (the first 3 in stored order, both
      directions)
  (b) forward-only (d = 0) + k = 3

This probe resolves both:

  (a) is a DERIVED fact, not a measurement: 06's swept field counts
      the scans run = 2 directions x nbare bare factors. The
      committed 06 .out has max swept = 6 on all 37 swept entries
      -> nbare <= 3 everywhere -> the first-3 bound drops no scan for
      any swept entry -> the k=3 scan set is IDENTICAL to the
      full-sweep scan set -> its cost is the measured one (no new run
      can change it).

  (b) since k=3 drops nothing here, (b) == forward-only. Measured
      here: each of the 37 entries re-run with the sweep loop bound
      to d=0, under PRODUCTION semantics (sweep only — no triage
      drill, all scans run with no early stop, i.e. a strict upper
      bound on what the production %mr_pass4_scan would cost). The
      full-sweep variant (d=0..1, no drill) is re-measured on the
      same entries for an apples-to-apples production-semantics A/B
      against 06's drill-inclusive line.

Semantics notes (both variants):
  - added = dt_total - record t= (test/corpus_class3.out), the same
    definition as 06's sweep-cost line; dt_total includes the
    production rubi() run, so added = the sweep's cost on top of the
    record's package time.
  - 06's committed n=37 line INCLUDES the triage drill on the
    0-firing entries (333 pattern calls + conds — a triage-only
    artifact; production pass 4 has no drill). This probe's
    full-sweep numbers are the drill-free production upper bound.
  - a fire does not stop the harness (no early stop), so fired
    entries pay for all their scans: a strict upper bound on the
    production cost, which stops at the first fire.
  - the fwd variant's fire column shows, per FIRE4 entry, whether the
    forward direction alone rescues it (a reverse-only fire is a
    documented sacrifice of the forward-only fallback).

Usage:
  python3 probes/corpus/07-class3-deferred-sweep-cost-fallbacks.py
  (default: launch 4 worker buckets, wait, merge, write the .out)

Re-run: deterministic except wall times (the same caveat as 06's
.out)."""

import importlib.util
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SLUG = "07-class3-deferred-sweep-cost-fallbacks"
OUT = os.path.join(ROOT, "probes", "corpus", SLUG + ".out")
WORKDIR = os.path.join(ROOT, "probes", "corpus", SLUG + ".work")
SRC_OUT = os.path.join(ROOT, "probes", "corpus",
                       "06-class3-deferred-mechanisms.out")

N_BUCKETS = 4
GATE_MEAN = 1.0    # plan Task 3 Step 3: mean added <= 1 s
GATE_P95 = 3.0     # ... AND p95 added <= 3 s
EXPECTED_SWEPT = 37   # 06's committed sweep-cost line's n

# Import 06 for the entry template, the core subprocess runner, the
# output parser, and the pinned population asserts (deferred_set
# re-asserts 1033/788 whenever it is used — a records-drift guard).
_spec = importlib.util.spec_from_file_location(
    "p4mech", os.path.join(ROOT, "probes", "corpus",
                           "06-class3-deferred-mechanisms.py"))
assert _spec is not None and _spec.loader is not None, \
    "06-class3-deferred-mechanisms.py not found"
p6 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(p6)

ENTRY_CAP = p6.ENTRY_CAP   # 120 s per-entry safety cap, same as 06


def swept_keys():
    """The (rel, n) keys with swept > 0 in the committed 06 .out, in
    06's line order, with per-key (label, dt, swept, fire)."""
    deferred, _flags = p6.deferred_set()
    expected = {(rel, n) for (rel, n), _t in deferred}
    files = sorted({k[0] for k in expected}, key=len, reverse=True)
    mech_re = re.compile(
        r"^MECH (\S+)\s+t=\s*([\d.]+)s\s+(" +
        "|".join(re.escape(f) for f in files) +
        r") e(\d+) L(\d+)\s+npat=(\d+) swept=(\d+)\s+(.*)$")
    keys = []
    for line in open(SRC_OUT, encoding="utf-8"):
        m = mech_re.match(line.rstrip("\n"))
        if not m:
            continue
        swept = int(m.group(7))
        if swept > 0:
            keys.append({"key": (m.group(3), int(m.group(4))),
                         "label": m.group(1), "dt06": float(m.group(2)),
                         "swept": swept,
                         "fire": m.group(8).split()
                         if m.group(8).startswith("fire=") else None})
    assert len(keys) == EXPECTED_SWEPT, \
        f"06 swept count moved: {len(keys)} != {EXPECTED_SWEPT}"
    assert all(k["key"] in expected for k in keys), "swept key drift"
    assert all(k["swept"] in (4, 6) for k in keys), \
        f"unexpected swept values: {sorted({k['swept'] for k in keys})}"
    return keys


def swept_stats():
    """The 06 swept-field distribution + the committed sweep-cost line
    (parsed from SRC_OUT, not hard-coded)."""
    keys = swept_keys()
    by_swept = Counter(k["swept"] for k in keys)
    m = re.search(r"^n=\d+  mean=.*$",
                  "\n".join(open(SRC_OUT, encoding="utf-8")), re.M)
    assert m, "06 sweep-cost line not found"
    return keys, by_swept, m.group(0)


def entry_text(rel, n):
    """(f_text, var_text) from the suite — 06's gen_entries logic.
    Requires p6.load_ln() to have been called (run_bucket/main do)."""
    suite = p6.suite_map()
    assert rel in suite, f"{rel} not in the suite"
    ents, line_nos = suite[rel]
    assert n <= len(ents), f"{rel} e{n} out of range"
    els = p6.split_elements(ents[n - 1][1:-1])
    assert len(els) in (4, 5), f"{rel} e{n}: bad entry shape"
    return els[0], els[1]


def run_entry(k, variant, d_max, t_of):
    """One entry under one variant; returns the per-entry fact dict.
    Production semantics: the sweep only (no drill), all scans, no
    early stop."""
    rel, n = k["key"]
    f_text, var_text = entry_text(rel, n)
    mac = os.path.join(WORKDIR, "entries",
                       f"{variant}-{os.path.basename(rel)[:16]}-{n:04d}.mac")
    os.makedirs(os.path.dirname(mac), exist_ok=True)
    with open(mac, "w", encoding="utf-8") as fh:
        fh.write(p6.entry_mac(f_text, var_text, [], [],
                              d_max=d_max, drill=False))
    text, timed_out, dt = p6.run_mac(mac, ENTRY_CAP)
    assert not timed_out, \
        f"{rel} e{n} {variant}: hit the {ENTRY_CAP} s cap — re-run it"
    info = p6.parse_output(text)
    assert info["done"], f"{rel} e{n} {variant}: subprocess died"
    assert info["prod"] in p6.NUONOUN, \
        f"{rel} e{n} {variant}: prod={info["prod"]} — record drift " \
        "(the entry no longer 0-fires in production)"
    nbare_expected = k["swept"] // 2
    census = info["census"] or (0, False)
    assert census == (nbare_expected, False), \
        f"{rel} e{n} {variant}: census={census} != " \
        f"({nbare_expected}, False) — census drift"
    exp_scan = nbare_expected * (1 if d_max == 0 else 2)
    assert info["nscan"] == exp_scan, \
        f"{rel} e{n} {variant}: nscan={info["nscan"]} != {exp_scan}"
    # Rescue semantics = 06's label_entry: a fire is a RESCUE iff its
    # answer op is non-noun and non-bool (the harness runs ALL scans —
    # no early stop — so an early noun fire does not preclude a later
    # rescuing fire; 06's MECH label keys off the same test).
    rescued = [f for f in info["fires"] if f[2] not in p6.NONRESCUE]
    return {"key": f"{rel} e{n}", "label06": k["label"],
            "swept06": k["swept"], "fire06": k["fire"],
            "fires": [",".join(str(x) for x in f) for f in info["fires"]],
            "rescued": bool(rescued),
            "rescue_op": rescued[0][2] if rescued else None,
            "dt": dt, "t_rec": t_of[(rel, n)],
            "added": dt - t_of[(rel, n)]}


def run_variant(variant, d_max, keys, t_of):
    out = []
    for k in keys:
        r = run_entry(k, variant, d_max, t_of)
        out.append(r)
        print(f"  {variant:7s} {r['key']:60s} dt={r['dt']:6.1f}s "
              f"added={r['added']:6.1f}s fires={len(r['fires'])} "
              f"rescue={'Y' if r['rescued'] else '-'}",
              flush=True)
    return out


def run_bucket(b):
    """Worker: run both variants over keys[b::N_BUCKETS], append the
    JSONL to WORKDIR/bucket-b.jsonl."""
    keys, _by, _line = swept_stats()
    p6.load_ln()
    _items, pkg = p6.load_record(p6.PKG_RECORD)
    t_of = {k: t for k, _c, t in _items}
    mine = keys[b::N_BUCKETS]
    with open(os.path.join(WORKDIR, f"bucket-{b}.jsonl"), "a",
              encoding="utf-8") as of:
        for variant, d_max in (("full", 1), ("fwd-k3", 0)):
            for r in run_variant(variant, d_max, mine, t_of):
                of.write(json.dumps({"variant": variant, **r}) + "\n")
                of.flush()
    print(f"bucket {b}: done ({len(mine)} entries x 2 variants)",
          flush=True)


def pct(sorted_vals, p):
    if not sorted_vals:
        return 0.0
    i = min(len(sorted_vals) - 1, int(len(sorted_vals) * p))
    return sorted_vals[i]


def build_out(keys, by_swept, line06, results):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"=== class-3 deferred sweep-cost fallbacks ({SLUG}) ===",
        f"run date: {now}",
    ] + p6.build_info_lines() + [
        f"core fingerprint: {p6.driver._core_fingerprint()} "
        f"(rules core, test/mr_rules.core)",
        f"source: probes/corpus/06-class3-deferred-mechanisms.out "
        f"(the 37 swept entries)",
        "semantics: production pass-4 shape (sweep only, no triage "
        "drill, all scans, no early stop — a strict upper bound on "
        "the production cost)",
        "added = dt_total - record t= (test/corpus_class3.out), the "
        "same definition as the 06 sweep-cost line",
        "build note: this run is on the 2026-08-31 13:27:47 maxima "
        "binary (same branch hash, same SBCL, core fingerprint "
        "unchanged); the 06 committed line above is on the "
        "2026-08-29 17:58:20 binary — the two lines are quoted under "
        "their own stamps",
        "",
        "--- 06 committed sweep-cost line (drill-inclusive; the "
        "original gate input) ---",
        line06,
        "",
        "--- k=3 factor bound (fallback a) ---",
        f"06 swept field: n={len(keys)}, distribution "
        + " ".join(f"swept={s}: {by_swept[s]}"
                   for s in sorted(by_swept)),
        f"max swept = {max(by_swept)} = 2 directions x 3 bare factors "
        "-> nbare <= 3 on every swept entry",
        "k=3 (the first 3 factors in stored order, both directions) "
        "drops NO scan on this population",
        "-> the k=3 scan set is identical to the full-sweep scan "
        "set; its cost is the measured full-sweep cost (derived, not "
        "a new measurement)",
        "",
    ]
    for variant, title in (("full",
                            "full sweep, both directions "
                            "(production semantics, no drill)"),
                           ("fwd-k3",
                            "forward-only d=0 + k=3 (fallback b; "
                            "k=3 drops nothing here, so b == "
                            "forward-only)")):
        rows = sorted(results[variant],
                      key=lambda r: (r["key"].rsplit(" ", 1)[0],
                                     int(r["key"].rsplit(" ", 1)[1][1:])))
        adds = sorted(r["added"] for r in rows)
        n = len(adds)
        assert n == EXPECTED_SWEPT, f"{variant}: {n} != {EXPECTED_SWEPT}"
        mean = sum(adds) / n
        p50, p95 = pct(adds, 0.50), pct(adds, 0.95)
        gate = "PASS" if (mean <= GATE_MEAN and p95 <= GATE_P95) \
            else "FAIL"
        lines += [
            f"--- {title} ---",
            f"n={n}  mean={mean:6.2f}  p50={p50:6.2f}  "
            f"p95={p95:6.2f}  max={adds[-1]:6.2f}   gate: {gate}",
            f"{'entry':60s} {'06':12s} {'swept':>5s}  {'rescue':10s} "
            f"{'fires (d,i,op)':30s} {'dt':>7s} {'t_rec':>7s} {'added':>7s}",
        ]
        for r in rows:
            rc = ("Y " + str(r["rescue_op"])) if r["rescued"] else "-"
            fires = "; ".join(r["fires"]) if r["fires"] else "-"
            lines.append(
                f"{r['key']:60s} {r['label06']:12s} {r['swept06']:5d}  "
                f"{rc:10s} {fires:30s} {r['dt']:7.1f} {r['t_rec']:7.1f} "
                f"{r['added']:7.1f}")
        lines.append("")
    # Gate summary over all three cost statements.
    lines.append("--- gate (plan Task 3 Step 3: p95 added <= 3 s AND "
                 "mean added <= 1 s) ---")
    m = re.search(r"n=(\d+)  mean=\s*([\d.]+).*p95=\s*([\d.]+)", line06)
    if m:
        mean06, p9506 = float(m.group(2)), float(m.group(3))
        v06 = ("clears" if (mean06 <= GATE_MEAN and p9506 <= GATE_P95)
               else "fails")
        lines.append(f"06 line  n={m.group(1)} mean={mean06:6.2f}  "
                     f"p95={p9506:6.2f}  -> {v06} the gate (drill-"
                     "inclusive, 2026-08-29 binary)")
    for variant in ("full", "fwd-k3"):
        adds = sorted(r["added"] for r in results[variant])
        n = len(adds)
        mean = sum(adds) / n
        p95 = pct(adds, 0.95)
        verdict = ("clears" if (mean <= GATE_MEAN and p95 <= GATE_P95)
                   else "fails")
        lines.append(f"{variant:8s} mean={mean:6.2f}  p95={p95:6.2f}  "
                     f"-> {verdict} the gate")
    # The rescue delta over the 17 first-run FIRE4 entries (06 label),
    # per variant: rescue = a sweep fire with a non-noun, non-bool
    # answer op (06's label_entry test). The full variant re-confirms
    # the first-run 17/17; the fwd variant's losses are the
    # reverse-direction-only fires the forward-only fallback sacrifices.
    fire4 = [k for k in keys if k["label"] == "FIRE4"]

    def rescue_set(variant):
        return {r["key"] for r in results[variant] if r["rescued"]}
    full_r, fwd_r = rescue_set("full"), rescue_set("fwd-k3")
    key_str = {f"{k['key'][0]} e{k['key'][1]}": k for k in fire4}
    lost = sorted(set(key_str) & (full_r - fwd_r))
    gained = sorted((fwd_r - full_r) & set(key_str))
    lines += [
        "",
        "--- rescue delta over the 17 first-run FIRE4 entries ---",
        f"full sweep rescues {len(full_r & set(key_str))} of "
        f"{len(fire4)} (first-run cross-check: 17 expected)",
        f"forward-only rescues {len(fwd_r & set(key_str))} of "
        f"{len(fire4)}",
    ]
    if lost:
        lines.append("sacrificed by forward-only (a non-noun sweep fire "
                     "exists only in the reverse direction): "
                     + ", ".join(lost))
    if gained:
        lines.append("fwd-only rescues (full-sweep missed these — "
                     "unexpected): " + ", ".join(gained))
    lines.append("")
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


def main():
    ap = __import__("argparse").ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--run", action="store_true",
                   help="launch the buckets, wait, merge, write the .out")
    g.add_argument("--bucket", type=int, metavar="B",
                   help="worker: run both variants over keys[B::N]")
    a = ap.parse_args()
    if a.bucket is not None:
        run_bucket(a.bucket)
        return
    keys, by_swept, line06 = swept_stats()
    print(f"07: {len(keys)} swept entries; launching {N_BUCKETS} "
          f"buckets", flush=True)
    for old in os.listdir(WORKDIR) if os.path.isdir(WORKDIR) else []:
        p = os.path.join(WORKDIR, old)
        if old.startswith("bucket-") and old.endswith(".jsonl"):
            os.remove(p)
    procs = [subprocess.Popen(
        [sys.executable, os.path.abspath(__file__),
         "--bucket", str(b)], cwd=ROOT)
        for b in range(N_BUCKETS)]
    rc = [p.wait() for p in procs]
    assert all(r == 0 for r in rc), f"worker rc={rc}"
    results = {"full": [], "fwd-k3": []}
    for b in range(N_BUCKETS):
        for line in open(os.path.join(WORKDIR, f"bucket-{b}.jsonl"),
                         encoding="utf-8"):
            r = json.loads(line)
            results[r["variant"]].append(r)
    for variant in results:
        assert len(results[variant]) == EXPECTED_SWEPT, \
            f"{variant}: {len(results[variant])} != {EXPECTED_SWEPT}"
    build_out(keys, by_swept, line06, results)


if __name__ == "__main__":
    main()
