#!/usr/bin/env python3
"""Run-record helpers shared by the corpus driver, the shard launcher, the
shard mergers and the P5 gate (matcher substrate plan 3).

The matcher substrate has three migration switches (spec
docs/superpowers/specs/2026-09-12-matcher-substrate-design.md section 3.6)
and three run switches: mr_nested_fallback, which decides whether a nested
Int call with no route falls through to Maxima's integrate, and the integer
depth cap mr_max_depth (both exact seen test design
docs/superpowers/specs/2026-09-15-matcher-seen-test-intpart-design.md 3.3),
and mr_giveup_last, which defers the give-up rules (those answering Rubi's
Unintegrable marker) to a second dispatch pass — half of the faithful pair
with the seen-cut fall-through in %mr_top_body, and mr_inert_leak_misfire,
which declines a non-class-4 answer that leaks an inert trig head out of the
inert-trig domain (ticket 15), and mr_last_resort_tier, which walks the
bare-u_ tail after the specific give-ups (ticket 14), and
mr_general_after_giveups, which does the same for 9.3's general body. Every corpus record states
the arm it ran: the driver writes `switches: mr_flat_wide=<v>
mr_cond_retry=<v> mr_model_flags=<v> mr_nested_fallback=<v>
mr_giveup_last=<v> mr_inert_leak_misfire=<v> mr_last_resort_tier=<v>
mr_general_after_giveups=<v> mr_max_depth=<n>` on its
`filter:` header line, and the
mergers carry it into the merged record. Records written before a switch
was added state a shorter set and so read as None here; the mergers and the
P5 gate read the arm from the NEW record and tolerate that.

- SWITCHES, SWITCH_DEFAULTS: the switches in record order, with the
  dispatcher's defaults (the defmvars of maxima_rubi_dispatch.lisp;
  test/test_run_records.py holds the two in step).
- INT_SWITCHES, valid_value(name, value): mr_max_depth takes a positive
  integer, the rest true|false.
- switch_settings(env): the arm a driver process runs. MR_SWITCHES holds
  space-separated `<switch>=<value>` overrides; unset switches keep
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

# Record order matches the defmvar order of maxima_rubi_dispatch.lisp;
# test/test_run_records.py holds the names and defaults in step with it.
SWITCHES = ("mr_flat_wide", "mr_cond_retry", "mr_model_flags",
            "mr_nested_fallback", "mr_giveup_last", "mr_inert_leak_misfire",
            "mr_last_resort_tier", "mr_general_after_giveups", "mr_max_depth",
            "mr_eqq_symbolic")
SWITCH_DEFAULTS = {"mr_flat_wide": "false",
                   "mr_cond_retry": "true",
                   "mr_model_flags": "true",
                   "mr_nested_fallback": "false",
                   "mr_giveup_last": "true",
                   "mr_inert_leak_misfire": "true",
                   "mr_last_resort_tier": "true",
                   "mr_general_after_giveups": "true",
                   "mr_max_depth": "32",
                   "mr_eqq_symbolic": "true"}
# mr_max_depth is the one INTEGER switch (a positive depth cap); the rest
# are booleans. Both kinds are read from the record's filter: line, so the
# mergers' one-arm check covers them all.
INT_SWITCHES = ("mr_max_depth",)
_VALUE_RE = {s: (r"\d+" if s in INT_SWITCHES else r"(?:true|false)")
             for s in SWITCHES}
SWITCHES_RE = re.compile(
    r"\bswitches: (" + " ".join(rf"{s}={_VALUE_RE[s]}" for s in SWITCHES) + r")")
SHARD_FILE_RE = re.compile(r"\.shard(?:\d+\.(?:out|log|files|caps)|-pids)$")

# A native-`integrate` baseline (probes/corpus/probe-integrate-sample.py)
# runs no package code, so it has no switch arm to report — but a record
# that states NOTHING is exactly the pre-P5 shape common_switches() exists
# to reject, and a class-6 baseline merge hit that on 2026-09-20. It
# therefore states its arm EXPLICITLY, as a value distinct from every
# package arm: baseline shards agree with each other, and a baseline shard
# can never be merged with a package shard (the guard reports two arms).
BASELINE_ARM = "none (native integrate baseline)"
BASELINE_RE = re.compile(r"\bswitches: (none \(native integrate baseline\))")


def valid_value(name, value):
    """Is `value` a legal setting for switch `name`?"""
    if name in INT_SWITCHES:
        return value.isdigit() and int(value) > 0
    return value in ("true", "false")


def switch_settings(env):
    settings = dict(SWITCH_DEFAULTS)
    for item in env.get("MR_SWITCHES", "").split():
        name, sep, value = item.partition("=")
        if not sep or name not in SWITCH_DEFAULTS or not valid_value(name, value):
            raise ValueError(
                f"MR_SWITCHES item {item!r}: expected <switch>=<value> with "
                f"<switch> one of {', '.join(SWITCHES)} — true|false for the "
                f"booleans, a positive integer for {', '.join(INT_SWITCHES)}")
        settings[name] = value
    return settings


def switches_text(settings):
    return " ".join(f"{s}={settings[s]}" for s in SWITCHES)


def record_switches(path):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("filter:"):
                m = SWITCHES_RE.search(line)
                if m:
                    return m.group(1)
                m = BASELINE_RE.search(line)
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
