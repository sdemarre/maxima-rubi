#!/usr/bin/env python3
"""Run-record helpers shared by the corpus driver, the shard launcher, the
shard mergers and the P5 gate (matcher substrate plan 3).

The matcher substrate has three migration switches (spec
docs/superpowers/specs/2026-09-12-matcher-substrate-design.md section 3.6).
Every corpus record states the arm it ran: the driver writes
`switches: mr_flat_wide=<v> mr_cond_retry=<v> mr_model_flags=<v>` on its
`filter:` header line, and the mergers carry it into the merged record.

- SWITCHES, SWITCH_DEFAULTS: the switches in record order, with the
  dispatcher's defaults (the defmvars of maxima_rubi_dispatch.lisp;
  test/test_run_records.py holds the two in step).
- switch_settings(env): the arm a driver process runs. MR_SWITCHES holds
  space-separated `<switch>=true|false` overrides; unset switches keep
  their defaults. Anything else is a ValueError (a typo must not run the
  default arm under a flipped label).
- switches_text(settings): the header text.
- record_switches(path): the switches text of a record or shard, or None.
- common_switches(paths): the one switches text every shard carries;
  ValueError when a shard has none or two shards differ.
- clear_stale_shards(test_dir, slug): delete a finished run's shard files
  before a launch (a stale shard from a run with more jobs used to reach
  the merge: the P0 class-3 shard23 of 2026-09-04); RuntimeError while a
  pid of the previous run is alive.
"""

import glob
import os
import re

SWITCHES = ("mr_flat_wide", "mr_cond_retry", "mr_model_flags")
SWITCH_DEFAULTS = {"mr_flat_wide": "false",
                   "mr_cond_retry": "true",
                   "mr_model_flags": "true"}
SWITCHES_RE = re.compile(
    r"\bswitches: (" + " ".join(rf"{s}=(?:true|false)" for s in SWITCHES) + r")")
SHARD_FILE_RE = re.compile(r"\.shard(?:\d+\.(?:out|log|files)|-pids)$")


def switch_settings(env):
    settings = dict(SWITCH_DEFAULTS)
    for item in env.get("MR_SWITCHES", "").split():
        name, sep, value = item.partition("=")
        if not sep or name not in SWITCH_DEFAULTS or value not in ("true", "false"):
            raise ValueError(f"MR_SWITCHES item {item!r}: expected <switch>=true|false "
                             f"with <switch> one of {', '.join(SWITCHES)}")
        settings[name] = value
    return settings


def switches_text(settings):
    return " ".join(f"{s}={settings[s]}" for s in SWITCHES)


def record_switches(path):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("filter:"):
                m = SWITCHES_RE.search(line)
                return m.group(1) if m else None
    return None


def common_switches(paths):
    if not paths:
        raise ValueError("no shard files")
    seen = {}
    for p in paths:
        seen.setdefault(record_switches(p), []).append(os.path.basename(p))
    if None in seen:
        raise ValueError("no switches on the filter: line of "
                         + ", ".join(seen[None][:5]))
    if len(seen) != 1:
        raise ValueError("shards ran different switch arms: " + "; ".join(
            f"{k} ({len(v)} shards: {', '.join(v[:3])})" for k, v in sorted(seen.items())))
    return next(iter(seen))


def _alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def clear_stale_shards(test_dir, slug):
    pidfile = os.path.join(test_dir, f"corpus_{slug}.shard-pids")
    if os.path.exists(pidfile):
        with open(pidfile, encoding="utf-8") as fh:
            for line in fh:
                parts = line.split()
                if len(parts) >= 2 and parts[1].isdigit() and _alive(int(parts[1])):
                    raise RuntimeError(f"{pidfile}: {parts[0]} (pid {parts[1]}) is still "
                                       "running; wait for it or kill it before a new launch")
    removed = 0
    for path in sorted(glob.glob(os.path.join(test_dir, f"corpus_{slug}.shard*"))):
        if SHARD_FILE_RE.search(path):
            os.unlink(path)
            removed += 1
    return removed
