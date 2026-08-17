# TODO — index

One short entry per item: status + link. The questions to be answered
and the evidence live in the item's file. Items may reference each other.
Status: `open` / `in prog` / `done`.

| id  | title                            | status | item file                                  |
|-----|----------------------------------|--------|--------------------------------------------|
| T1  | Rubi anatomy                     | open   | [t1-rubi-anatomy.md](t1-rubi-anatomy.md)   |
| T2  | Pattern matching in Maxima       | open   | [t2-pattern-matching.md](t2-pattern-matching.md) |
| T3  | Corpus and Maxima baseline       | open   | [t3-corpus-baseline.md](t3-corpus-baseline.md)   |
| T4  | Rule translation (algebraic)     | open   | [t4-rule-translation.md](t4-rule-translation.md) |
| T5  | Package and harness architecture | open   | [t5-package-architecture.md](t5-package-architecture.md) |

Order: T1 first; T3's sample run in parallel with T1; T2 after T1;
T4 after T1 + T2; T5 last. See the design spec, section 5.

## Pinned reference clones

- `reference/rubi` @ (unpinned — clone and pin are T1's first act)
- `reference/maxima-syntax-test-suite` @ (unpinned — clone and pin are T3's first act)
