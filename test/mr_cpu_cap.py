#!/usr/bin/env python3
"""Run a command under a CPU-TIME budget, reporting the CPU it used.

    python3 test/mr_cpu_cap.py <cap-seconds> <cpu-out-file> <cmd> [args...]

Exit status: CAPPED_RC (200) when the child was stopped for exceeding the
budget, otherwise the child's own exit code, or 128+signal if it was
signalled. <cpu-out-file> receives the child's user+system seconds, exactly,
from wait4's rusage.

WHY NOT `ulimit -t` / RLIMIT_CPU. That is the obvious way to cap CPU, and it
was the first implementation, but it cannot be used on this host. RLIMIT_CPU
signals SIGXCPU at the soft limit, and SIGXCPU's default action is terminate
AND DUMP CORE (signal(7)). A cap hit is a NORMAL outcome for this corpus —
thousands of entries per run — not a crash. MEASURED 2026-09-18: the first
CPU-capped class-1 run wrote 111 SBCL cores of 26-82 MB in 35 minutes (4.0 GB
into /var/lib/systemd/coredump), filled the disk, and the resulting ENOSPC
killed 14 of the 24 queue workers inside maxima_run's mkstemp; the run
carried on, silently, with 10.

`ulimit -c 0` does NOT fix it. MEASURED on this host (Linux 7.0.0-28-generic):
the limit is applied correctly (/proc/PID/limits shows a 0 core size) and the
dump still happens, because core_pattern here pipes to systemd-coredump and
the kernel ignores RLIMIT_CORE for a piped dump — the pattern passes the
handler a limit of 9223372036854775808 regardless.

So the budget is enforced from here instead: fork, poll the child's CPU in
/proc/PID/stat, and SIGKILL it when it is over. SIGKILL never dumps, whatever
core_pattern says. wait4 then gives the child's exact CPU, so the recorded
time needs no polling-granularity fudge.
"""

import os
import sys
import time

CAPPED_RC = 200
# The poll interval is the DETERMINISM BAND: the child can overrun the budget
# by up to one interval before the kill lands, and where in that band it dies
# depends on poll phase, so a wide interval reintroduces the run-to-run
# nondeterminism a CPU cap exists to remove. MEASURED 2026-09-18, helper CPU
# against 10 s of child CPU: 20 ms 0.080 s (0.80 %), 100 ms 0.010 s (0.10 %),
# 250 ms and 1 s also 0.010 s. 100 ms is already at the floor — what is left is
# fork/exec/wait4, not polling — so a coarser interval buys nothing and only
# widens the band. Finer than ~20 ms is pointless: /proc CPU accounting is in
# clock ticks, 10 ms on this host.
POLL = 0.1
TICKS = os.sysconf("SC_CLK_TCK")


def child_cpu(pid):
    """The process's user+system seconds from /proc, 0.0 if it is gone.

    Field 14 (utime) and 15 (stime), 1-based, of /proc/PID/stat — split after
    the LAST ')' so a comm containing spaces or parentheses cannot shift them."""
    try:
        with open(f"/proc/{pid}/stat", "rb") as fh:
            fields = fh.read().rsplit(b")", 1)[1].split()
        return (int(fields[11]) + int(fields[12])) / TICKS
    except (OSError, IndexError, ValueError):
        return 0.0


def main(argv):
    if len(argv) < 3:
        sys.stderr.write(__doc__)
        return 2
    cap, cpu_path, cmd = float(argv[0]), argv[1], argv[2:]
    pid = os.fork()
    if pid == 0:
        try:
            os.execv(cmd[0], cmd)
        except OSError:
            os._exit(127)
    capped = False
    while True:
        wpid, status, usage = os.wait4(pid, os.WNOHANG)
        if wpid:
            break
        if not capped and child_cpu(pid) >= cap:
            capped = True
            try:
                os.kill(pid, 9)
            except ProcessLookupError:
                pass
        time.sleep(POLL)
    try:
        with open(cpu_path, "w", encoding="utf-8") as fh:
            fh.write("%.6f\n" % (usage.ru_utime + usage.ru_stime))
    except OSError:
        pass
    if capped:
        return CAPPED_RC
    if os.WIFSIGNALED(status):
        return 128 + os.WTERMSIG(status)
    return os.waitstatus_to_exitcode(status)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
