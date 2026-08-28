#!/usr/bin/env python3
"""probe-radcan-attribution — classify the OLD failure mode of every
entry that flipped FAIL->PASS in the 2026-08-28 full-corpus A/B around
the zero-chain `radcan(rat())` fallback.

For each of the 370 gains (old class in {unverified, timeout}, new
class in {verified, expected}), run a fresh maxima subprocess:

  1. rubi(f, x) with the fixed 40 pos / 20 no prompt answers
  2. replay the OLD zero-chain symbolic stages (8 stages, carried
     values) on the zero-diff that the new run closed, each stage in
     its own errcatch so a crash is DETECTED (DIED Bk) instead of
     killing the chain (CLOSED Bk = stage closed, FINISHED = no
     stage crashed and none closed)
  3. probe the fallback the way the new harness runs it (elliptic
     gated: freeof of the six elliptic_* functions, then
     errcatch(radcan(rat(D)))) and record FB=CRASH|true|false|GATED

Old failure mode = the replay result:
  DIED Bk     old chain crashed at stage Bk (crash victim)
  FINISHED    no crash, no closure (plain simplifier gap)
  CLOSED Bk   chain would have closed (budget victim — the old run
              hit its 30 s cap before the stage completed)
The crash message, where DIED, is captured from the subprocess
output (the line above the ` -- an error` line inside the chain
window).

Re-runnable (from repo root):
  sh probes/maxima/probe-radcan-attribution.run
Wall ~1-2 h at 24 parallel maxima (per-entry cap 150 s).
Writes probes/maxima/probe-radcan-attribution.out (committed,
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
OUT = os.path.join(ROOT, "probes/maxima/probe-radcan-attribution.out")

sys.argv = ["corpus_class1_driver.py", "1 Algebraic functions/", "1", "30"]
_spec = importlib.util.spec_from_file_location(
    "driver", os.path.join(ROOT, "test", "corpus_class1_driver.py"))
driver = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(driver)

OLD_REC = os.path.join(ROOT, "test/corpus_class1.pre-radcan-fallback.out")
NEW_REC = os.path.join(ROOT, "test/corpus_class1.out")
ELLIPTIC = ("elliptic_f, elliptic_e, elliptic_pi, "
            "elliptic_ec, elliptic_eu, elliptic_kc")
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
    # assignment visibility in this build (measured 2026-08-28: list
    # assigns are invisible to later list elements, second assigns to
    # a target silently dropped) and this build does not parse `;`
    # inside block parens (commas do).
    stmts = ["MR_d: MR_de"]
    for i, s in enumerate(STAGES, 1):
        stmts += [f"r: errcatch({s})",
                  f"if r = [] then return(\"DIED B{i}\")",
                  f"if is(part(r, 1) = 0) then return(\"CLOSED B{i}\")",
                  "MR_d: part(r, 1)"]
    stmts.append('return("FINISHED")')
    return "block([r, MR_d], " + ",\n  ".join(stmts) + ")"


def probe_chain(name, de):
    return (f"MR_de: {de}$\n"
            f"printf(true, \"== {name} CHAIN START~%\")$\n"
            f"MR_res: {chain_replay()}$\n"
            f"printf(true, \"== {name} CHAIN END ~a~%\", MR_res)$\n"
            f"rf: errcatch(if freeof([{ELLIPTIC}], MR_de) = true "
            f"then radcan(rat(MR_de)) else \"gate\")$\n"
            f"printf(true, \"== {name} FB ~a~%\", "
            f"if rf = [] then \"CRASH\" "
            f"else (if part(rf, 1) = \"gate\" then \"GATED\" "
            f"else string(is(part(rf, 1) = 0))))$")


def probe_one(rel, e, new_class):
    path = rel2path[rel]
    entries, _lns = driver.extract_entries(path)
    els = driver.split_elements(entries[e - 1][1:-1])
    f_text, var_text, _s, e_text = els[0], els[1], els[2], els[3]
    e_text2 = els[4] if len(els) == 5 else None
    head = (f"mr_f: {f_text}$\n"
            f"mr_r: rubi(mr_f, {var_text})$\n"
            + "pos$\n" * 40 + "no$\n" * 20)
    chains = {}
    if new_class == "verified":
        body = probe_chain("S", f"diff(mr_r, {var_text}) - mr_f")
        chains["S"] = "S"
    else:
        body = probe_chain("E", f"diff(mr_r - ({e_text}), {var_text})")
        chains["E"] = "E"
        if e_text2 is not None:
            body += probe_chain("E2", f"diff(mr_r - ({e_text2}), {var_text})")
            chains["E2"] = "E2"
    body += 'printf(true, "== DONE~%")$\n'
    out, timed_out = driver.maxima_run(head + body, PER_TIMEOUT)
    # crash message per chain: the line above ` -- an error` inside
    # the chain's [CHAIN START, CHAIN END] window
    lines = out.splitlines()
    res = {}
    for name in chains:
        rep, fb, msg = "?", "?", ""
        try:
            lo = next(i for i, l in enumerate(lines)
                      if l.strip().startswith(f"== {name} CHAIN START"))
            hi = next(i for i, l in enumerate(lines)
                      if l.strip().startswith(f"== {name} CHAIN END"))
            m = re.match(r"^== %s CHAIN END (.+)$" % name,
                         lines[hi].strip())
            rep = m.group(1).strip()
            # measured 2026-08-28 (zc_errfmt): errcatch in this build
            # prints the caught message as a bare column-0 line and NO
            # ` -- an error` anchor (and some crash classes — expt,
            # PTPTQUOTIENT — print nothing at all). Within the window,
            # column-0 lines are: the two marker echos (printf( ...),
            # the block statement echo head (MR_res: ...) and, if a
            # stage crashed, the message line(s).
            msg = " | ".join(l for l in lines[lo:hi]
                             if l and not l[0].isspace()
                             and not l.startswith(("==", "printf(",
                                                   "MR_res:")))
        except StopIteration:
            rep = "CAP" if timed_out else "ERR"
        try:
            i = next(j for j, l in enumerate(lines)
                     if l.strip().startswith(f"== {name} FB "))
            fb = re.match(r"^== %s FB (\S+)$" % name,
                          lines[i].strip()).group(1)
        except (StopIteration, AttributeError):
            pass
        res[name] = (rep, fb, msg)
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
    hdr = (f"# probe-radcan-attribution output, "
           f"{datetime.datetime.now(datetime.timezone.utc):%F %T} UTC\n"
           f"# {build.strip()}\n"
           f"# records: test/corpus_class1.pre-radcan-fallback.out "
           f"vs test/corpus_class1.out\n"
           f"# entries: {len(gains)} "
           f"(old class in {{unverified, timeout}} -> "
           f"new class in {{verified, expected}})\n"
           f"# format: <relpath> e<n> <old>-><new> "
           f"<chain>=<replay> FB=<fb> [MSG=<crash line>]\n")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(hdr)
        for rel, e, res in rows:
            oc, nc = old[(rel, e)][0], new[(rel, e)][0]
            parts = []
            for name in sorted(res):
                rep, fb, msg = res[name]
                p = f"{name}={rep} FB={fb}"
                if msg:
                    p += f" MSG={msg}"
                parts.append(p)
            f.write(f"{rel} e{e} {oc}->{nc} " + "  ".join(parts) + "\n")
    print(f"wrote {OUT}")

    # summary
    counts = {}
    for _rel, _e, res in rows:
        for name in res:
            rep = res[name][0]
            key = rep.split()[0] if rep.split() else "?"
            if key in ("DIED", "CLOSED", "FINISHED"):
                counts[key] = counts.get(key, 0) + 1
            else:
                counts["cap/err"] = counts.get("cap/err", 0) + 1
    print(f"chains: {sum(counts.values())}  by mode: {counts}")
    fb_counts = {}
    for _rel, _e, res in rows:
        for name in res:
            fb = res[name][1]
            fb_counts[fb] = fb_counts.get(fb, 0) + 1
    print(f"FB: {fb_counts}")


if __name__ == "__main__":
    main()
