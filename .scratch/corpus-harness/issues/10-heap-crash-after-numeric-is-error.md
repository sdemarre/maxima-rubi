# A fatal heap exhaustion after the numeric check is recorded as `error`

Status: needs-triage
Type: bug (harness fidelity: verdict depends on GC timing)
Filed: 2026-10-02 (found attributing the 2026-10-01 graded run's A/B, records `e5e8f37`)

## Symptom

The 2026-10-01 native-baseline record of section 4 has **6 PASS -> FAIL**
against the `fcc1e19` baseline record, all numeric-only passes before:

| entry | before | 2026-10-01 | re-run alone |
|---|---|---|---|
| 4.3.2.1 e826 | integrate verified 0.5 s, `numeric/timeout:...(heap)` | error | error |
| 4.3.3.1 e604 | verified | error | verified |
| 4.4.2.1 e84 | verified | error | verified |
| 4.5.4.2 e586 | risch verified 12.8 s | timeout (risch error) | verified 5.3 s |
| 4.5.4.2 e1159 | risch verified 0.8 s | timeout (risch error) | verified |
| 4.5.4.2 e1160 | risch verified 1.2 s | timeout (risch error) | timeout, then verified on a third run |

The rubi arm had no such transition (0 PASS -> FAIL in all eight sections),
but nothing in the mechanism is arm-specific.

## Mechanism

Raw output of e826 (integrate, re-run alone, 2026-10-01):

```
OPTIMAL 392 3
GRADE A 383 3
NUMERIC verified ok
NUMERIC expected ok
Heap exhausted during garbage collection: 0 bytes available, 16 requested.
...
fatal error encountered in SBCL ...: Heap exhausted, game over.
ldb>
```

The answers are large (e1160: leaf 3,990 against an optimal of 266). A symbolic
stage of the checker (radcan family) allocates fast enough to fill the 1 GB
dynamic space **between two ticks** of the heap guard (`test/mr_verify.lisp`,
20 ms CPU tick, `mr_heap_fraction` 0.6). When the guard wins, the stage is
stopped and tagged `(heap)` and the entry passes on its numeric lines — the
old records' tags show exactly that. When SBCL loses the race, the process dies
in `ldb`; stdin is `/dev/null`, so it exits rather than hangs.

The driver (`classify_entry`, `test/corpus_driver.py`) then sees `ANSWERED`,
the `NUMERIC` lines, no `CLASS` line, and **not** `timed_out`: it returns
`error`. A process killed by the cap after `ANSWERED` is instead classified from
its `NUMERIC` lines (`/verify-timeout` tag). The two cases differ only in
how the process ended.

For the baseline, an integrate `error` sends the entry to risch; a risch `error`
leaves integrate's `timeout` in the record — hence the `timeout` rows above.

## Options

1. **Classify a crash after `ANSWERED` like a verify timeout**: no `CLASS`
   line, not timed out, `NUMERIC` lines present -> decide from them, tag
   `.../verify-crash`. Small, driver-only, guardable with a synthetic output
   in `test_driver_proof`/`test_driver_grade` style. Keeps the verdict
   independent of the GC race whenever the numeric lines were printed first
   (they are, today: numeric runs before the symbolic stages print `CLASS`).
2. Make the guard win the race: a finer tick, a lower `mr_heap_fraction`,
   or a larger `--dynamic-space-size` for entry processes. Each costs
   something (tick overhead, more `(heap)` stops, memory with 24 workers) and
   none removes the race.

Option 1 is the fix; option 2 at most a mitigation.

## Acceptance

- A synthetic-output guard: `ANSWERED` + `NUMERIC verified ok` + no `CLASS`
  + process exit (not cap) -> `verified`, tag ends `/verify-crash`; without any
  `NUMERIC` ok line -> `unverified` (not `error`).
- The six entries above, re-run a few times each: the same verdict every time.
- The tag counted in the `.proof` census, so the number of crash-decided
  entries is visible per record.

## Comments
