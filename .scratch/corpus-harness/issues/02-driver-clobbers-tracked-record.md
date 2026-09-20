# corpus_driver.py overwrites a tracked record when run without an out-file

Status: resolved 2026-09-20 (the default changed)
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

## Resolution — 2026-09-20

Fixed as a DEFAULT change, per this ticket's third-hit comment (option 2 plus
the part of option 3 that kills the reflex):

- `corpus_driver.py` no longer resolves a missing `OUT_FILE` to
  `test/corpus_class1_driver.out`. The default is now
  `DEFAULT_OUT_FILE = test/corpus_driver.scratch.out`, gitignored along with
  its `.caps` sidecar, so a committed record can only be written by naming it.
- A first argument starting with `-` is no longer taken as a FILTER: the
  driver writes `USAGE` (the ten positionals, the SUITE_DIR requirement and
  the out-file default) to stderr and exits 2. That is the exact reflex behind
  hit 1.

Guard: `test/test_driver_out_default.py`, four checks, `Results: 4 passed, 0
failed`. Written first and watched fail: the RED run **reproduced hit 1 live**
— its `--help` check overwrote `test/corpus_class1_driver.out` (sha256
8e25f76… -> 6ae0177…), restored with `git checkout --`. The guard's `[usage]`
and `[usage-writes-nothing]` checks are that reproduction, now inverted.

Also removed the orphan 0-byte `test/corpus_class1_driver.caps` (the sidecar
left behind by a clobbering run) and gitignored the ~40 untracked working
files under `test/` that made the `git status` sweep — the only thing that
caught hit 3 — unreadable.
