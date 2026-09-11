#!/usr/bin/env python3
"""Regression guard: MR_RULES_CORE_PATH pins the corpus driver to a
rules core built elsewhere (a pinned worktree's core, for an A/B run).

Motivation (2026-09-11): the class-3 deferred campaign's targeted A/Bs
were run through six hand-edited driver copies
(test/corpus_driver_{c1,c34,b3,c5,c6b}pre.py, corpus_driver_312old.py)
whose only diff was a hard-coded RULES_CORE path under a /tmp worktree
plus a forced "on" core state. The env var replaces the copies.

Four checks (no Maxima; each driver import runs in a child process,
because the driver resolves its core at module level):
  1. pinned: an existing core + <core>.stamp is used as-is — state
     `pinned`, USE_RULES_CORE true, no fingerprint check against this
     tree's rules (the pinned core is deliberately different).
  2. missing pin: the import exits nonzero naming MR_RULES_CORE_PATH —
     never a silent fallback to the standard load path or a rebuild
     (either would run the wrong rules under an A/B label).
  3. default unchanged: without the env var the core is
     test/mr_rules.core with test/mr_rules.core.stamp.
  4. the record header names a pinned core (appended to the `filter:`
     line — the prefix the shard merge accepts), and is empty when
     unpinned (the standing record format is unchanged).

Re-runnable:  python3 test/test_driver_core_pin.py
Exits nonzero if any check fails.
"""

import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

CHILD = r"""
import importlib.util, json, sys
sys.argv = ["corpus_driver.py", "1 Algebraic functions/", "1", "30"]
spec = importlib.util.spec_from_file_location("drv", sys.argv_path)
""".replace("sys.argv_path", repr(os.path.join(HERE, "corpus_driver.py"))) + r"""
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
print(json.dumps({"core": d.RULES_CORE, "stamp": d.RULES_CORE_STAMP,
                  "use": d.USE_RULES_CORE, "state": d.rules_core_state(),
                  "header": d.core_header()}))
"""


def _child(env_extra):
    env = {k: v for k, v in os.environ.items()
           if k not in ("MR_RULES_CORE", "MR_RULES_CORE_PATH")}
    env.update(env_extra)
    return subprocess.run([sys.executable, "-c", CHILD], env=env, cwd=ROOT,
                          capture_output=True, text=True, timeout=60)


def main():
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        core = os.path.join(tmp, "mr_rules.core")
        with open(core, "wb") as fh:
            fh.write(b"not a real image")
        with open(core + ".stamp", "w", encoding="utf-8") as fh:
            fh.write("fingerprint 00000000000000000000000000000000\n")

        # 1. pinned
        p = _child({"MR_RULES_CORE_PATH": core})
        try:
            got = json.loads(p.stdout.strip().splitlines()[-1])
        except (IndexError, ValueError):
            got = None
        if (got is None or got["core"] != core
                or got["stamp"] != core + ".stamp" or got["use"] is not True
                or got["state"] != "pinned"):
            failures.append(f"[pinned] {got} {p.stderr[-600:]}")
        else:
            print("PASS [pinned] core + stamp used as-is, state pinned")

        # 4a. header names the pin
        if got is None or got["header"] != f"  core: pinned {core}":
            failures.append(f"[header] pinned header "
                            f"{got and got['header']!r}")
        else:
            print(f"PASS [header] pinned: {got['header'].strip()!r}")

        # 2. missing pin is fatal
        gone = os.path.join(tmp, "absent.core")
        p = _child({"MR_RULES_CORE_PATH": gone})
        if p.returncode == 0 or "MR_RULES_CORE_PATH" not in p.stderr:
            failures.append(f"[missing] exit {p.returncode} "
                            f"stderr {p.stderr[-400:]!r}")
        else:
            print(f"PASS [missing] exit {p.returncode}, names "
                  "MR_RULES_CORE_PATH")

    # 3 + 4b. default (MR_RULES_CORE=0: no build attempted by the check)
    p = _child({"MR_RULES_CORE": "0"})
    try:
        got = json.loads(p.stdout.strip().splitlines()[-1])
    except (IndexError, ValueError):
        got = None
    want_core = os.path.join(ROOT, "test", "mr_rules.core")
    if (got is None or got["core"] != want_core
            or got["stamp"] != want_core + ".stamp" or got["state"] != "off"
            or got["header"] != ""):
        failures.append(f"[default] {got} {p.stderr[-600:]}")
    else:
        print("PASS [default] test/mr_rules.core(.stamp), empty header")

    for f in failures:
        print(f"FAIL {f}")
    print(f"Results: {5 - len(failures)} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
