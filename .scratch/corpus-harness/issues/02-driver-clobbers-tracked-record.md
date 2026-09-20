# corpus_driver.py overwrites a tracked record when run without an out-file

Status: needs-triage
Type: task (small)
Filed: 2026-09-18 (hit twice in one session)

## Problem

`test/corpus_driver.py`'s `OUT_FILE` is `sys.argv[8]`, and when it is absent the driver
writes to `test/corpus_class1_driver.out` — a COMMITTED record. Any exploratory
invocation from the repo root silently destroys it, and the `.caps` sidecar beside it.

Measured 2026-09-18: `python3 test/corpus_driver.py --help` (there is no `--help`; the
string became the FILTER, matching 0 files) overwrote the committed 2026-08-25 record —
a real 77-entry 1.2.1.6 run — with a 0-entry `filter: '--help'` stub. Caught only
because `git status` was checked before committing; reverted with `git checkout`.

The same hazard applies to every `test/corpus_class<N>.out` for the merge scripts, but
those are at least named explicitly on the command line. This one is a DEFAULT.

## Why it is easy to hit

The driver has no argparse: nine positional arguments, no `--help`, so the natural
reflex for finding out how to call it destroys data. The written file also looks
plausible (correct header, correct summary block), so a stale clobber can survive
review.

## Options

- Refuse to write the default path unless an explicit flag says so; require `OUT_FILE`.
- Default to a scratch path (`test/corpus_driver.scratch.out`, gitignored) and make the
  committed record something only an explicit argument can name.
- Give the driver an argparse front-end with `--help`, keeping the positional order for
  the existing callers (`launch_class_shards.py`, `run_corpus_queue.py`, the probes).

The second is the smallest change that removes the hazard; the third also removes the
reflex that triggers it.

## Comments
