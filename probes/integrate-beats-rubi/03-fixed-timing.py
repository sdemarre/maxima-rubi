#!/usr/bin/env python3
"""integrate-beats-rubi issue 01: the three class-1 timeout entries after the
fix (B2 TrinomialParts scan, B1 NormalizeIntegrand quotient, A SimplifyTerm
no-larger guard). Same harness as 02 (arm "stock" = the tree as is).
Run from the repo root: python3 probes/integrate-beats-rubi/03-fixed-timing.py"""
import os, signal, subprocess, time
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MAC = "probes/integrate-beats-rubi/02-timeout-arms.mac"
cases = ["1/((a+b*x)^2*(c+d*x)^3)", "x^7/((a+b*x)^2*(c+d*x)^3)", "1/((a+b*x)*(c+d*x)^8)"]
print("# date:", time.strftime("%Y-%m-%d"), " build:", subprocess.run(["maxima", "--version"], capture_output=True, text=True).stdout.strip())
for arm in ("stock",):
    for fs in cases:
        t = time.time()
        p = subprocess.Popen(["maxima", "--very-quiet", f'--batch-string=arm:"{arm}"$ fs:"{fs}"$ batchload("{MAC}")$'],
                             stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, start_new_session=True)
        try:
            out, _ = p.communicate(timeout=90)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL); out, _ = p.communicate(); out += "\nKILLED at 90 s wall"
        keep = [l for l in out.splitlines() if l.startswith(("TIME:", "CHECK:", "KILLED")) or "rror" in l]
        print(f"== {arm:10s} {fs}  wall={time.time()-t:.0f}s", *keep, sep="\n  ", flush=True)
