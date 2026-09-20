# corpus_driver.py overwrites a tracked record when run without an out-file

Status: open (three hits; default should change)
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

## Comment — 2026-09-20: hit a third time

Hit again during the class-6 port, Step 7. An exploratory slice
(`python3 test/corpus_driver.py "6.2.2 " 8 30 reference/maxima-syntax-test-suite`,
run to prove the positive polarity of the head rewrites) has no out-file
positional, so it silently overwrote the committed 2026-08-25 record —
this time replacing a class-1 record with class-6 content, which is at
least visible in a diff.

Caught only by a `git status` sweep at the Step-10 close, several hours
and fifteen commits after the fact. Restored with `git checkout --`; no
commit carried the damage, but nothing in the workflow would have
stopped one that did.

Three hits now (2026-09-18 x2, 2026-09-20), all from exploratory runs
where an out-file was not the thing on the author's mind. That is the
argument for the fix being a DEFAULT change rather than a discipline
reminder: make the no-out-file default a scratch path (or refuse to
write a path that `git ls-files --error-unmatch` resolves), so the
committed record can only be written deliberately.

Raising Status accordingly.
