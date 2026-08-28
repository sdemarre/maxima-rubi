#!/usr/bin/env python3
"""probe-radcan-attribution-v2 — re-decompose the 370 FAIL->PASS
gains of the 2026-08-28 full-corpus A/B around the zero-chain
radcan(rat()) fallback, with the CORRECTED elliptic gate and the
driver's numeric stage included (both absent from v1).

Why v2 (measured 2026-08-28, 5.50.0/SBCL):
  - v1's "23 crash victims" framing was wrong: 18 of the 23 had
    pre-run times of 0.6-5.6 s (a ratsimp zero-divisor crash takes
    ~20 s on the minimal repro and <1 s on these diffs — either way,
    the pre run never spent crash time on them), and all 23 have
    post-run times of 0.6-6.0 s (the post run never spent crash time
    either). v1 replayed the symbolic chain on today's zero-diff but
    omitted the numeric stage that leads the driver's zero chain, and
    it mirrored the harness gate as it ran (the list-first-arg
    freeof — a no-op, see below).
  - The A/B baseline (test/corpus_class1.pre-radcan-fallback.out,
    2026-08-27 13:02 UTC) was run on pre-89054b0 rules; 89054b0
    (13:22 UTC, 20 min after the pre-record merge) changed 1.1.3.8
    and related behavior. Today's answer (current rules) is what the
    post run and this probe see; the pre run saw a different answer
    on the affected entries. A flip is therefore a rule-change and/or
    fallback effect, and this probe separates them.

Per entry (fresh subprocess on the rules core, rubi with the fixed
40 pos / 20 no prompts), for each zero-diff the post run could have
closed (self-diff for verified entries; expected diff(s) for
expected entries), in the driver's check order:

  NUM   the driver's leading numeric stage: float ev under the sweep
        subs (a=0.9, b=1.3, c=0.5, d=0.9, e=1.1, f=0.8, g=1.7,
        h=0.3, A=0.6, B=1.4, C=0.4, D=0.9, p=2) at x=0.35 and
        x=0.65, resid < 1e-9 at both points -> CLOSES | decline
  ELL   apply(freeof, [the six elliptic_* symbols, MR_de]) — the
        CORRECTED gate (documented variadic freeof spliced over the
        symbol list; the v1-era list-first-arg form is not a
        documented freeof call and returned true on elliptic-
        carrying diffs): true = gate admits, false = gate blocks
  CHAIN the 8 symbolic stages replayed with per-stage errcatch ->
        DIED Bk | CLOSED Bk | FINISHED, crash message captured
  FB    errcatch(radcan(rat(MR_de))) run UNGATED (the post run's
        broken gate let the fallback run on every diff) -> CRASH |
        true (closed) | false (returned nonzero)

Per-chain classification (the post run's actual flow: numeric
leads, then chain, then ungated fallback):
  MECH   = NUM if NUM=CLOSES
         | CHAIN Bk if NUM=decline and CHAIN=CLOSED Bk
         | FB if NUM=decline, CHAIN in {DIED Bk, FINISHED},
           FB=true
         | INCONSISTENT otherwise (the post run could not have
           verified this entry on today's diff)
  KEPT   = no if MECH=FB and ELL=false (the corrected gate would
           block the fallback and the entry reverts to unverified),
           yes otherwise

Re-runnable (from repo root):
  sh probes/maxima/probe-radcan-attribution-v2.run
Wall ~15-40 min at 24 parallel maxima (per-entry cap 150 s).
Writes probes/maxima/probe-radcan-attribution-v2.out (committed,
stamped). Needs the two A/B records:
  test/corpus_class1.pre-radcan-fallback.out   (2026-08-27 13:02 UTC)
  test/corpus_class1.out                       (2026-08-28 10:03 UTC)
"""

import concurrent.futures
import datetime
import importlib.util
import os
import re
import subprocess
import sys

ROOT = "/home/serge/src/maxima-rubi"
WORKERS = 24
PER_TIMEOUT = 150
OUT = os.path.join(ROOT, "probes/maxima/probe-radcan-attribution-v2.out")

sys.argv = ["corpus_class1_driver.py", "1 Algebraic functions/", "1", "30"]
_spec = importlib.util.spec_from_file_location(
    "driver", os.path.join(ROOT, "test", "corpus_class1_driver.py"))
driver = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(driver)

OLD_REC = os.path.join(ROOT, "test/corpus_class1.pre-radcan-fallback.out")
NEW_REC = os.path.join(ROOT, "test/corpus_class1.out")
ELLIPTIC = ("elliptic_f, elliptic_e, elliptic_pi, "
            "elliptic_ec, elliptic_eu, elliptic_kc")
SUBS = ("a=0.9, b=1.3, c=0.5, d=0.9, e=1.1, f=0.8, g=1.7, h=0.3, "
        "A=0.6, B=1.4, C=0.4, D=0.9, p=2")
STAGES = ["factor(MR_de)", "ratsimp(MR_d)", "ratsimp(expand(MR_d))",
          "ratsimp(factor(MR_d))", "ratsimp(MR_de)", "ratsimp(expand(MR_d))",
          "factor(MR_d)", "ratsimp(factor(MR_d))"]


def load(p):
    d = {}
    for line in open(p, encoding="utf-8"):
        m = re.match(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*?)\s+e(\d+)\s+L(\d+)\s*$",
                     line.rstrip())
        if m:
            d[(m.group(3), int(m.group(4)))] = (
                m.group(1), float(m.group(2)))
    return d


def chain_replay():
    # block() with comma-statements: top-level comma lists have broken
    # assignment visibility in this build (measured 2026-08-28) and
    # this build does not parse `;` inside block parens (commas do).
    stmts = ["MR_d: MR_de"]
    for i, s in enumerate(STAGES, 1):
        stmts += [f"r: errcatch({s})",
                  f"if r = [] then return(\"DIED B{i}\")",
                  f"if is(part(r, 1) = 0) then return(\"CLOSED B{i}\")",
                  "MR_d: part(r, 1)"]
    stmts.append('return("FINISHED")')
    return "block([r, MR_d], " + ",\n  ".join(stmts) + ")"


def probe_chain(name, de, var):
    # printf in this build does not force a top-level `=` relation to
    # a boolean (measured 2026-08-28: printf("~a", 1 = 1) prints
    # `1 = 1`); pass values or if-expressions instead.
    return (
        f"MR_de: {de}$\n"
        f"MR_z1 : errcatch(float(ev(MR_de, [{SUBS}, {var}=0.35])))$\n"
        f"MR_z2 : errcatch(float(ev(MR_de, [{SUBS}, {var}=0.65])))$\n"
        f"printf(true, \"== {name} NUM ~a~%\", "
        f"if (MR_z1 # [] and MR_z2 # [] "
        f"and is(abs(part(MR_z1, 1)) < 1e-9) = true "
        f"and is(abs(part(MR_z2, 1)) < 1e-9) = true) "
        f"then \"CLOSES\" else \"decline\")$\n"
        f"printf(true, \"== {name} ELL ~a~%\", "
        f"apply(freeof, [{ELLIPTIC}, MR_de]))$\n"
        f"printf(true, \"== {name} CHAIN START~%\")$\n"
        f"MR_res: {chain_replay()}$\n"
        f"printf(true, \"== {name} CHAIN END ~a~%\", MR_res)$\n"
        f"rf: errcatch(radcan(rat(MR_de)))$\n"
        f"printf(true, \"== {name} FB ~a~%\", "
        f"if rf = [] then \"CRASH\" "
        f"else string(is(part(rf, 1) = 0)))$\n")


def classify(num, rep, fb):
    """The post run's mechanism for this chain (numeric leads, then
    chain, then ungated fallback)."""
    if num == "CLOSES":
        return "NUM"
    m = re.match(r"^CLOSED (B\d)$", rep)
    if m:
        return "CHAIN " + m.group(1)
    if fb == "true":
        return "FB"
    return "INCONSISTENT"


def probe_one(rel, e, new_class):
    path = rel2path[rel]
    entries, _lns = driver.extract_entries(path)
    els = driver.split_elements(entries[e - 1][1:-1])
    f_text, var_text, _s, e_text = els[0], els[1], els[2], els[3]
    e_text2 = els[4] if len(els) == 5 else None
    head = (f"mr_f: {f_text}$\n"
            f"mr_r: rubi(mr_f, {var_text})$\n"
            + "pos$\n" * 40 + "no$\n" * 20)
    # driver order: self-diff first (verified if it closes), then
    # expected diff(s) — record every chain; classification uses the
    # first closing mechanism in this order.
    if new_class == "verified":
        chains = [("S", f"diff(mr_r, {var_text}) - mr_f")]
    else:
        chains = [("E", f"diff(mr_r - ({e_text}), {var_text})")]
        if e_text2 is not None:
            chains.append(("E2", f"diff(mr_r - ({e_text2}), {var_text})"))
    body = "".join(probe_chain(n, de, var_text) for n, de in chains)
    body += 'printf(true, "== DONE~%")$\n'
    out, timed_out = driver.maxima_run(head + body, PER_TIMEOUT)
    lines = out.splitlines()
    res = {}
    for name, _de in chains:
        row = {"num": "?", "ell": "?", "rep": "?", "fb": "?", "msg": ""}
        try:
            lo = next(i for i, l in enumerate(lines)
                      if l.strip().startswith(f"== {name} CHAIN START"))
            hi = next(i for i, l in enumerate(lines)
                      if l.strip().startswith(f"== {name} CHAIN END"))
            m = re.match(r"^== %s CHAIN END (.+)$" % name,
                         lines[hi].strip())
            row["rep"] = m.group(1).strip()
            # errcatch in this build prints the caught message as a
            # bare column-0 line and NO ` -- an error` anchor (and
            # some crash classes print nothing) — v1's capture logic.
            row["msg"] = " | ".join(
                l for l in lines[lo:hi]
                if l and not l[0].isspace()
                and not l.startswith(("==", "printf(", "MR_res:")))
        except StopIteration:
            row["rep"] = "CAP" if timed_out else "ERR"
        for key, pat in (("num", r"^== %s NUM (\S+)$"),
                         ("ell", r"^== %s ELL (\S+)$"),
                         ("fb", r"^== %s FB (\S+)$")):
            try:
                i = next(j for j, l in enumerate(lines)
                         if re.match(pat % name, l.strip()))
                row[key] = re.match(pat % name, lines[i].strip()).group(1)
            except StopIteration:
                pass
        row["mech"] = classify(row["num"], row["rep"], row["fb"])
        row["kept"] = ("no" if row["mech"] == "FB" and row["ell"] == "false"
                       else "yes")
        res[name] = row
    return (rel, e, res)


def main():
    global rel2path
    rel2path = {rel: path for path, rel in driver.file_list()}
    old, new = load(OLD_REC), load(NEW_REC)
    gains = sorted(k for k in old if k in new
                   and old[k][0] in ("unverified", "timeout")
                   and new[k][0] in ("verified", "expected"))
    print(f"gains: {len(gains)}", flush=True)

    rows = [None] * len(gains)
    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(probe_one, rel, e, new[(rel, e)][0]): i
                for i, (rel, e) in enumerate(gains)}
        for fut in concurrent.futures.as_completed(futs):
            i = futs[fut]
            rows[i] = fut.result()
            done += 1
            if done % 25 == 0:
                print(f"  {done}/{len(gains)}", flush=True)

    build = subprocess.run(
        ["maxima", "--version"], capture_output=True, text=True).stdout
    hdr = (f"# probe-radcan-attribution-v2 output, "
           f"{datetime.datetime.now(datetime.timezone.utc):%F %T} UTC\n"
           f"# {build.strip()}\n"
           f"# records: test/corpus_class1.pre-radcan-fallback.out "
           f"(pre-89054b0 rules) vs test/corpus_class1.out\n"
           f"# entries: {len(gains)} (old class in {{unverified, timeout}} "
           f"-> new class in {{verified, expected}})\n"
           f"# per chain (driver order S/E/E2): NUM={{CLOSES,decline}} "
           f"ELL={{true, false}} CHAIN replay FB={{CRASH,true,false}} "
           f"MECH={{NUM, CHAIN Bk, FB, INCONSISTENT}} KEPT-FIXED-GATE="
           f"{{yes, no}} [MSG=<crash line>]\n")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(hdr)
        for rel, e, res in rows:
            oc, nc = old[(rel, e)][0], new[(rel, e)][0]
            parts = []
            for name in sorted(res):
                r = res[name]
                p = (f"{name}: NUM={r['num']} ELL={r['ell']} "
                     f"CH={r['rep']} FB={r['fb']} MECH={r['mech']} "
                     f"KEPT={r['kept']}")
                if r["msg"]:
                    p += f" MSG={r['msg']}"
                parts.append(p)
            f.write(f"{rel} e{e} {oc}->{nc} " + "  ".join(parts) + "\n")
    print(f"wrote {OUT}")

    # summary
    mech = {}
    kept = {}
    for _rel, _e, res in rows:
        # entry mechanism = first closing chain in driver order
        for name in ("S", "E", "E2"):
            if name in res:
                r = res[name]
                mech[r["mech"].split()[0] if r["mech"].split()
                     else "?"] = mech.get(r["mech"].split()[0], 0) + 1
                kept[r["kept"]] = kept.get(r["kept"], 0) + 1
                break
    print(f"entry MECH (first closing chain in driver order): {mech}")
    print(f"KEPT under corrected gate: {kept}")


if __name__ == "__main__":
    main()
