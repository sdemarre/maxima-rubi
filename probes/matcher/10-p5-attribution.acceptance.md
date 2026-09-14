# P5 attribution — acceptance document (matcher substrate Plan 3, Task 4 Step 9)

Stop document for the user's acceptance of every entry that is PASS in the P0 record and FAIL in the final record. User decision 2026-09-13: acceptance is per group, and individual entries can be rejected by id. Written 2026-09-14 from committed files, with no Maxima runs. Every figure is copied from the file named next to it; every tally computed here states its rule.

## 1. Header

- **Final records**: `test/corpus_class1.p5-run1.out`, `test/corpus_class2.p5-run1.out`, `test/corpus_class3.p5-run1.out`. All switches are at their defaults, `switches: mr_flat_wide=false mr_cond_retry=true mr_model_flags=true` (FINAL_ARM `""`).
- **P0 records**: `test/corpus_class1.pre-matcher.out`, `test/corpus_class2.pre-matcher.out`, `test/corpus_class3.pre-matcher.out`.
- **Build**: `branch_5_50_base_84_g4204fb669` / 2026-08-31 13:27:47 / SBCL 2.6.7.
- **Cores**: final `built test/mr_rules.core (112775536 bytes) rules=3513 fingerprint=6c396cf8be7a1fe5060d4d17bd37cc58`. P0, rebuilt at `0a6664c` for probe 10: `built test/mr_rules.core (172556912 bytes) rules=3514 fingerprint=5ef9b3bc5ee07ffac0e76f1fea54fbac`.
- **Evidence**: probe 10 (commit 295effa) `probes/matcher/10-p5-attribution.class<N>.summary.out` (every entry of every group) and the raw legs `…class<N>-{final30,p0,final120,newerror}.out`; the mechanism lines `probes/matcher/10-p5-attribution.mechanisms-{class2-3,class1-a,class1-b,class1-c}.md`; the 100 s re-checks `test/corpus_class<N>.p5-final.timeout-rerun/merge.out`; the untracked recovery ledger `.superpowers/sdd/2026-09-13-matcher-substrate-plan3/progress.md`.
- **How to answer** (template in §6): for each group write `accepted`, `accepted except <file> e<n> …` or `rejected`, then one line for the new timeouts and one for the `rubi_hybrid` question (§4). Accepting a group accepts every entry its summary lists. Any rejection stops Plan 3 before Task 5, and the rejected entries become the input of a fix plan.

## 2. Translation defects (pre-existing, byte-identical to P0, made reachable by the substrate)

The generated cond/repl bodies are byte-identical to `0a6664c` outside the P3 static gate's closed exception list (`python3 test/check_generated_rules.py` → `Results: 11 passed, 0 failed`, Step 6). What makes these rules reach the corpus entries is the substrate's binding.

| defect | evidence | scope | class 1 groups / entries | class 2 | class 3 |
|---|---|---|---|---|---|
| `IGtQ`/`ILtQ`/`ILeQ` emitted as a bare `>`/`<`/`<=` (integer test lost) | `generator/generate_rules.py:816-817` (`CMP_OPS`), `:1129-1137` (emitter); `rules/class2/2_1.mac:82` reads `is(_mr_2_1_r10_p < 0) and is(_mr_2_1_r10_m > 0)` for Rubi `ILtQ[p,0] && IGtQ[m,0]` (recovery ledger, controller confirmation) | calls in the Rubi sources the generator reads (grep `I(Gt\|Lt\|Le\|Ge)Q\[`): class 1 1,261 in 74 files, class 2 29 in 3, class 3 145 in 9, 9.1 4 in 1; `IGeQ` is not in `CMP_OPS` (not checked) | 111 / 957 | 2 / 3 (text) | 0 / 0 |
| `%mr_negQ` true for an unknown-sign symbol | `maxima_rubi_utils.mac:446-448` `%mr_negQ(e) := (not %mr_posQ(e)) and %mr_neQ(e, 0)` (recovery ledger); Rubi's `PosAux` reads a bare symbol as positive (IntegrationUtilityFunctions.m:608–634, per the mechanism files) | `%mr_negQ(` calls in the generated rules, counted here with `grep -o '%mr_negQ(' rules/class<N>/*.mac \| wc -l`: class 1 153, class 2 1, class 3 1 | 51 / 223 | 0 / 0 | 1 / 7 (text) |
| Rubi `!=` emitted verbatim, which Maxima reads as `(k!) = 1` | controller ad-hoc `--batch-string` run on this build (recovery ledger): with `k:1`, `quote(k != 1)` → `1 = 1` and `is(k != 1)` → true; with `k:2` → false. Parser: `nparse.lisp:1310–1316` (part A). Not yet a committed probe | 10 generated lines containing ` != `: `1_1_3_2_r17`, `r18`; `1_1_3_4_r30`; `1_1_3_6_r9`; `1_1_3_8_r15`; `1_2_2_4_r29`, `r30`; `1_2_3_2_r8`; `1_2_3_4_r29`, `r30`. None in classes 2–3 | 8 / 29 | 0 / 0 | 0 / 0 |
| space used as multiplication in `1_1_4_1_r1`'s repl | `rules/class1/1_1_4_1.mac:13` `…/(b*(n - j) (p + 1)*x^(n - 1))`; controller ad-hoc `errcatch((n - j) (p + 1))` with n:5, j:2, p:3 → `[]` (recovery ledger). Not yet a committed probe | regex `\)\s+\(` over rule lines outside comments, `%mr_defrule` lines and strings: 1 line (other juxtaposition shapes not scanned) | 2 / 3 | 0 / 0 | 0 / 0 |

Entries carrying at least one of the four: class 1 1072 of 1833 (139 carry both IGtQ and negQ), class 2 3 of 24, class 3 7 of 181. **Counting rule** (joins each file's tags with the summary's group sizes):
- class 1 g1–g17 (part A): the per-group counts of that file's *Defect tally*, which scripted every entry. g7's 42 negQ are marked inferred there. Its 33 *not determined* entries (g7 1, g8 32) count as untagged.
- g18–g80 (part B): the counts in each line's `[defect: …]` bracket. In a group that also carries IGtQ, the negQ entries count as a subset of the IGtQ entries (part B tally: 67 of 76).
- g81–g283 (part C): these tags are per line, not per entry, so every entry of a tagged group counts, with three exceptions:
  - where the line names the affected entries: g105 2 of 3, g111 2 of 3, g168 1 of 2;
  - where the tally withdraws the tag: g258 counts 0, so 65 IGtQ groups here against the file's 66;
  - NE/MUL count an entry of an `[also: NE]`/`[also: MUL]` group only if its `fires final:` list holds one of the 10 ` != ` rules / `1_1_4_1_r1` (g113: 2 of 3).
- classes 2 and 3 (their file predates the tag instruction): read from the text, not from a tag. Class 2: g4 (2) and g11 (1) IGtQ. Class 3: g3 negQ 7 of 11, because Rubi's NegQ is also true for e383/e384/e387/e388.
- not counted: in class-1 groups no file tagged NE, the final fire lists still show an NE-text rule firing — g20 (18), g25 (9), g36 (1), g74 (3), 31 entries. Part B's tags cover IGtQ/negQ only.

## 3. Per class

**Primary family** is a reading aid; each group's full line is in §5. Rule, first match wins:
1. the collapse repl: follows-from names `rubi_hybrid_exact` → 9.1-COLLAPSE;
2. an `as gN` line inherits gN's family;
3. the files' own lists: EXPAND-NOUN = part A g1/g4/g5/g9–g16, part B and part C gap lists, class 2 g1, class 3 g20; CATCH-1 = the part B/C gap lists;
4. top rule `1_1_3_1_r13/r14/r22` or `1_1_3_2_r35/r36` → RT-SUM/PF-EVEN;
5. the first shape family named anywhere in the line: RT-SUM/PF-EVEN, EXPAND-NOUN, CATCH-1, CATCH-3.1, AFX, NOFIRE, ZERO, in that order; then MID-CHAIN / VERIFY-TIMEOUT / POLY, whichever appears first;
6. the earliest cause in the follows-from clause: DEG (G-1), MFLAGS (model flags), RETRY (condition retry), FLAT (narrow Flat), 9.1 (9.1 regeneration), OPT (faithful / Optional binding), P0-NOISE;
7. otherwise *not determined*.

Families, as the mechanism files define them:
- EXPAND-NOUN: a rule answers alone with a top-level noun (class 2 g1 shape).
- RT-SUM/PF-EVEN: Rubi's odd-n partial-fraction rules fire on an even n.
- NOFIRE: no final-core fire.
- VERIFY-TIMEOUT: rubi returned, and the cap went to verification.
- MID-CHAIN: a timeout whose last fire is a nested rule.
- POLY: a Rubi-form polylog/log answer the zero chain does not close.
- CATCH-1 / CATCH-3.1: an `Unintegrable` catch-all binds ahead of Rubi's rule.
- AFX: AFx catch-alls made callable in 6a358db.
- OPT: faithful Optional / Flat+Orderless binding.
- DEG: the P0 route rested on a binding Mathematica does not make (G-1).
- RETRY / MFLAGS / FLAT: the r3 / r4 / r2 arm restores the entry.
- ZERO: an unsimplified zero coefficient.
- 9.1: the manual 9.1 rule is gone after regeneration.

Tag columns count entries by the §2 rule; *no tag* includes class 1's 33 *not determined*.

### Class 2 — 24 PASS→FAIL entries in 12 groups

- **Gate** (the run-1 gate is the final-record gate; tracked ledger Task 2, error line from the recovery ledger): `PASS: complete: same entries (missing 0, extra 0)` / `PASS: switches: mr_flat_wide=false mr_cond_retry=true mr_model_flags=true` / `PASS: pass floor: PASS 770 >= P0 614` / `PASS: wall ceiling: median 0.60 s <= P0 4.30 s` / `INFO: PASS->FAIL 24  FAIL->PASS 180` / `INFO: p90 wall P0 8.1 s -> new 2.3 s` / `INFO: timeout P0 6 -> new 20; timeout in new only: 18` / `Results: 4 passed, 0 failed`; error 1 -> 0 (0 new only)
- **Probe 10**: `PASS->FAIL 24: deterministic 22, slow-correct 2, near-cap 0, noise 0, p0-noise 0, unmeasured 0` / `Results: 24 passed, 0 failed`
- **100 s re-check** (`test/corpus_class2.p5-final.timeout-rerun/merge.out`): `OK: 20/20 re-checked, no dupes/missing/extra`; transitions timeout 17, verified 3 (`now-PASS: 3`); merge rc=0

| family | groups | entries | IGtQ only | negQ only | IGtQ+negQ | NE | MUL | ≥1 tag | no tag |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| EXPAND-NOUN | 1: g1 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| OPT | 5: g2 g4 g5 g6 g11 | 10 | 3 | 0 | 0 | 0 | 0 | 3 | 7 |
| DEG | 1: g3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| RETRY | 3: g8 g9 g12 (slow-correct) | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 4 |
| 9.1-COLLAPSE | 1: g10 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| not determined | 1: g7 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| **total** | 12 | 24 | 3 | 0 | 0 | 0 | 0 | 3 | 21 |

- **New timeouts**: `NEW TIMEOUTS 18: at 100 s timeout 15, verified 3` — the 3 verified at 100 s are 2.3 e527 (49.8 s), e528 (48.1 s), e575 (52.1 s), P0 deferred — not PASS→FAIL entries.
- **New errors**: none (`error 1 -> 0 (0 new only)`).
- **Collapse family**: **g10 = 2.1 e15.** The 9.1 double-root trinomial rule is on both cores (P0 id `9_1_r28`, generated `9_1_r27`). P0's repl `rubi_hybrid_exact(…)` tested the rewrite against the seen stack by exact `member` and dispatched it (`2_1_r4` answered). The generated `mr_int(…)` repl meets the ratsimp seen guard, which returns one top-level noun; the entry is deferred in all arms. See §4.

### Class 3 — 181 PASS→FAIL entries in 55 groups

- **Gate** (the run-1 gate is the final-record gate; tracked ledger Task 2, error line from the recovery ledger): `PASS: complete: same entries (missing 0, extra 0)` / `PASS: switches: mr_flat_wide=false mr_cond_retry=true mr_model_flags=true` / `PASS: pass floor: PASS 2287 >= P0 2058` / `PASS: wall ceiling: median 1.40 s <= P0 3.90 s` / `INFO: PASS->FAIL 181  FAIL->PASS 410` / `INFO: p90 wall P0 16.2 s -> new 7.5 s` / `INFO: timeout P0 201 -> new 145; timeout in new only: 62` / `Results: 4 passed, 0 failed`; error 4 -> 3 (3 new only)
- **Probe 10**: `PASS->FAIL 181: deterministic 180, slow-correct 1, near-cap 0, noise 0, p0-noise 0, unmeasured 0` / `Results: 181 passed, 0 failed`
- **100 s re-check** (`test/corpus_class3.p5-final.timeout-rerun/merge.out`): `OK: 145/145 re-checked, no dupes/missing/extra`; transitions error 16, timeout 113, unverified 8, verified 8 (`now-PASS: 8`); merge rc=0

| family | groups | entries | IGtQ only | negQ only | IGtQ+negQ | NE | MUL | ≥1 tag | no tag |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| EXPAND-NOUN | 1: g20 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| VERIFY-TIMEOUT | 4: g6 g12 g33 g34 | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 15 |
| POLY | 12: g1 g10 g21 g22 g23 g24 g36 g38 g49 g50 g51 g52 | 43 | 0 | 0 | 0 | 0 | 0 | 0 | 43 |
| CATCH-3.1 | 7: g2 g4 g5 g11 g28 g29 g41 | 39 | 0 | 0 | 0 | 0 | 0 | 0 | 39 |
| AFX | 11: g8 g9 g14 g15 g16 g17 g27 g30 g32 g43 g45 | 32 | 0 | 0 | 0 | 0 | 0 | 0 | 32 |
| OPT | 13: g3 g7 g13 g18 g26 g31 g35 g37 g39 g40 g42 g44 g48 | 38 | 0 | 7 | 0 | 0 | 0 | 7 | 31 |
| DEG | 1: g19 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| not determined | 6: g25 g46 g47 g53 g54 g55 (slow-correct) | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 8 |
| **total** | 55 | 181 | 0 | 7 | 0 | 0 | 0 | 7 | 174 |

- **New timeouts**: `NEW TIMEOUTS 62: at 100 s error 6, timeout 46, unverified 6, verified 4` — all 19 P0-verified new timeouts are members of the timeout groups g6, g12, g21, g33, g34, g46, g47, g55 (mechanisms file); the 4 verified at 100 s are 3.1.4 e135, e156, 3.3 e487, 3.4 e528.
- **New errors**: 3 — 3.1.5 e120 (g12; record verified 10.3 s → error 26.1 s), 3.2.3 e81 (timeout → error 22.5 s), 3.5 e172 (timeout → error 27.5 s); probe `newerror` `Results: 0 passed, 3 failed`; only e120 was PASS at P0; error kinds not recorded.
- **Collapse family**: none — no class-3 PASS→FAIL entry has `9_1_r27` or `9_1_r28` in either fire list (checked here over the summary).

### Class 1 — 1833 PASS→FAIL entries in 283 groups

- **Gate** (the run-1 gate is the final-record gate; tracked ledger Task 2, error line from the recovery ledger): `PASS: complete: same entries (missing 0, extra 0)` / `PASS: switches: mr_flat_wide=false mr_cond_retry=true mr_model_flags=true` / `PASS: pass floor: PASS 21202 >= P0 20125` / `PASS: wall ceiling: median 0.40 s <= P0 1.30 s` / `INFO: PASS->FAIL 1833  FAIL->PASS 2910` / `INFO: p90 wall P0 7.0 s -> new 4.5 s` / `INFO: timeout P0 778 -> new 1217; timeout in new only: 941` / `Results: 4 passed, 0 failed`; error 23 -> 63 (60 new only)
- **Probe 10**: `PASS->FAIL 1833: deterministic 1741, slow-correct 85, near-cap 0, noise 6, p0-noise 1, unmeasured 0` / `Results: 1833 passed, 0 failed`
- **100 s re-check** (`test/corpus_class1.p5-final.timeout-rerun/merge.out`): `OK: 1217/1217 re-checked, no dupes/missing/extra`; transitions contains-noun 1, error 56, timeout 1004, unverified 25, verified 131 (`now-PASS: 131`); merge rc=0

| family | groups | entries | IGtQ only | negQ only | IGtQ+negQ | NE | MUL | ≥1 tag | no tag |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| EXPAND-NOUN | 49: g1 g4 g5 g9 g10 g11 g12 g13 g14 g15 g16 g21 g23 g24 g31 g33 g38 g41 g45 g55 g57 g66 g67 g75 g77 g97 g98 g101 g103 g104 g130 g131 g132 g135 g136 g137 g139 g140 g142 g186 g187 g189 g191 g192 g193 g194 g195 g196 g197 | 695 | 621 | 0 | 0 | 0 | 0 | 621 | 74 |
| RT-SUM/PF-EVEN | 46: g8 g18 g19 g25 g26 g28 g29 g35 g39 g43 g48 g49 g54 g60 g61 g79 g80 g81 g107 g108 g109 g110 g112 g144 g145 g147 g148 g160 g171 g200 g201 g202 g204 g209 g211 g213 g214 g216 g217 g238 g239 g240 g252 g256 g259 g260 | 254 | 113 | 1 | 103 | 0 | 0 | 217 | 37 |
| NOFIRE | 2: g2 g3 | 179 | 0 | 0 | 0 | 0 | 0 | 0 | 179 |
| VERIFY-TIMEOUT | 29: g6 g20 g22 g36 g53 g70 g72 g73 g83 g84 g111 g146 g149 g150 g151 g152 g153 g154 g205 g219 g220 g224 g226 g229 g230 g231 g234 g237 g244 | 150 | 26 | 0 | 34 | 0 | 0 | 60 | 90 |
| MID-CHAIN | 6: g7 g37 g50 g52 g62 g71 | 80 | 4 | 42 | 0 | 0 | 0 | 46 | 34 |
| CATCH-1 | 32: g30 g32 g42 g44 g64 g93 g94 g95 g121 g122 g123 g124 g125 g126 g127 g128 g129 g133 g138 g141 g172 g173 g175 g176 g177 g178 g179 g180 g182 g183 g185 g198 | 86 | 1 | 7 | 0 | 0 | 0 | 8 | 78 |
| OPT | 33: g17 g34 g40 g46 g51 g56 g65 g74 g88 g89 g90 g92 g99 g114 g116 g119 g134 g158 g164 g169 g174 g218 g227 g228 g248 g253 g254 g257 g262 g263 g270 g275 g279 | 117 | 30 | 10 | 2 | 22 | 3 | 67 | 50 |
| DEG | 2: g47 g68 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 12 |
| RETRY | 23: g58 g82 g96 g105 g143 g166 g167 g188 g190 g199 g203 g221 g225 g235 g241 g245 g246 g250 g251 g278 g280 g281 (slow-correct) g282 (noise) | 127 | 7 | 0 | 0 | 0 | 0 | 7 | 120 |
| MFLAGS | 21: g76 g102 g115 g118 g161 g162 g206 g207 g208 g210 g222 g233 g242 g243 g249 g264 g265 g266 g267 g268 g277 | 32 | 8 | 0 | 0 | 4 | 0 | 11 | 21 |
| FLAT | 2: g215 g261 | 2 | 2 | 0 | 0 | 0 | 0 | 2 | 0 |
| ZERO | 9: g168 g170 g184 g255 g258 g271 g272 g273 g274 | 11 | 4 | 0 | 0 | 0 | 0 | 4 | 7 |
| 9.1 | 1: g120 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| 9.1-COLLAPSE | 1: g106 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| P0-NOISE | 1: g283 (p0-noise) | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| not determined | 26: g27 g59 g63 g69 g78 g85 g86 g87 g91 g100 g113 g117 g155 g156 g157 g159 g163 g165 g181 g212 g223 g232 g236 g247 g269 g276 | 81 | 2 | 24 | 0 | 3 | 0 | 29 | 52 |
| **total** | 283 | 1833 | 818 | 84 | 139 | 29 | 3 | 1072 | 761 |

- **New timeouts**: `NEW TIMEOUTS 941: at 100 s contains-noun 1, error 41, timeout 756, unverified 22, verified 121` — 708 of the 941 are PASS→FAIL group members (deterministic groups 616, g281 85, g282 6, g283 1); none of the 121 verified at 100 s is a deterministic-group entry (part C).
- **New errors**: 60 — probe `newerror` `Results: 0 passed, 60 failed`; part C's clusters: PF-EVEN on even n in 1.1.3.2 (20), `%mr_negQ` on a symbolic exponent (1.1.3.2 7, 1.2.3.3 3), 1.1.3.3 `1/((a+bx^4)(c+dx^4)^k)` (3), quartics via the x^2 substitution (1.2.2.2 2, 1.2.3.2 21), 1.2.3.4 e39/e40 (2), 1.3.1 e193/e194 = g143 (2); the error kind is not determined for any (probe 10 keeps no error text).
- **Collapse family**: **g106 = 1.2.1.2 e1734, e1735, e1736** has the class 2 g10 mechanism: P0 was expected via `9_1_r28` → `1_1_1_2_r37`, and the final route is `9_1_r27` alone, deferred in every arm. **g1's 1.2.1.4 e810** has `9_1_r28` in its P0 fires only; its final route is `1_2_1_3_r15` alone (EXPAND-NOUN). No other class-1 entry has `9_1_r27`/`9_1_r28` in either fire list (checked here). See §4.

## 4. The `rubi_hybrid` question

Spec §3.5 (`docs/superpowers/specs/2026-09-12-matcher-substrate-design.md:450-454`): "**`rubi_hybrid` / `rubi_hybrid_exact`** are deleted if the P5 A/B shows them unneeded: the regenerated 9.1 calls `mr_int`, as its `.m` source calls `Int`. A PASS→FAIL in the collapse-rule family (the exact-mode seen comparison exists for 1.2.1.3 e839) brings back the exact comparison as a translation fix, not as a pass."

- **The plan's check (Task 4 Step 2, e839 only)**: `0`. 1.2.1.3 e839 reads P0 verified 3.7 s → run 1 expected 0.9 s, so it is not PASS→FAIL (recovery ledger).
- **Collapse-family PASS→FAIL found** (an entry whose P0 or final fire list holds `9_1_r27`/`9_1_r28`, checked over all three summaries): class 2 g10 = 2.1 e15; class 1 g106 = 1.2.1.2 e1734, e1735, e1736; class 1 g1's 1.2.1.4 e810, by its P0 route only (part A confirms: `9_1_r28` in its P0 fires, no 9.1 fire on the final core); class 3 none.
- **Mechanism** (g10, g106): the rewrite of the same 9.1 rule is ratsimp-identical to an integrand already on the seen stack. P0's `rubi_hybrid_exact` compared by exact `member` and dispatched. The generated `mr_int` meets `%mr_seenp`'s ratsimp comparison and returns `integrate(f, x)`, so the entry is deferred in every arm.
- **What each answer implies**:
  - *Keep `rubi_hybrid` and bring the exact seen comparison back as a translation fix* (spec §3.5 applied). Plan 3 calls this a design change outside the plan (deviation 7). Class 2 g10 and class 1 g106 (and e810, if included) become rejected entries for a fix plan. Task 5 does not delete `rubi_hybrid` / `rubi_hybrid_exact` until that plan decides.
  - *Delete as the plan's Task 5 says.* Both functions are deleted as written, and class 2 g10 and class 1 g106 are accepted as PASS→FAIL. The spec §3.5 collapse clause is then not applied to these entries, which is recorded as a deviation.

## 5. Appendix — every group

Per group: the heading; the mechanism line, verbatim from the file named but trimmed (sub-bullet markers flattened, cut at about 280 + 200 characters, `…` marks a cut); and 2–3 sample entries (first, middle, last) as the summary prints them.

### Class 2

Full entry lists: `probes/matcher/10-p5-attribution.class2.summary.out`.

**class 2 g1** — deterministic, 5 entries — final deferred top=2_3_r34 — [no defect named in the text] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class2-3.md`: Both cores end with 2_3_r34 (`u*F^(a+b*(c+d*x)^n)` → `mr_int(ExpandLinearProduct)`). On P0 the expansion sum dispatched: 1_4_1_r7 split it, and 2_3_r15 / 1_4_1_r29 / a nested 2_3_r34 answered the terms (9–16 s). On the substrate 2_3_r34 is the only fire (nfires=1, 0.5–0.9 s) and … — follows from: not determined from the traces

- 2.3 e202: record verified 13.1s -> deferred 0.7s | P0 core verified 11.8s top=2_3_r34 | final30 deferred 0.6s top=2_3_r34
- 2.3 e248: record verified 13.5s -> deferred 0.5s | P0 core verified 11.9s top=2_3_r34 | final30 deferred 0.6s top=2_3_r34
- 2.3 e392: record verified 9.1s -> deferred 0.8s | P0 core verified 8.9s top=2_3_r34 | final30 deferred 0.7s top=2_3_r34

**class 2 g2** — deterministic, 4 entries — final contains-noun top=2_2_r2 — [no defect named in the text] [OPT]
> `10-p5-attribution.mechanisms-class2-3.md`: 2_2_r2 (Rubi 2.2 r5) now binds (P0 literal `(c+d*x)^m*(F^(g*(e+f*x)))^n*(a+b*(F^(g*(e+f*x)))^n)^p` cannot bind `1/x`, `F^(c+d*x)`) ahead of 2_3_r70; its `Int[(c+d x)^(m-1)(a+b F)^(p+1)]` binds 2_1_r14 (the 2.1 Unintegrable catch-all) → marker. This is the corpus's own 1-step … — follows from: faithful Optional binding (with the P0 DEG binding lost)

- 2.2 e86: record verified 5.7s -> contains-noun 1.6s | P0 core verified 7.0s top=2_3_r70 | final30 contains-noun 1.7s top=2_2_r2
- 2.2 e92: record verified 6.7s -> contains-noun 1.5s | P0 core verified 7.8s top=2_3_r70 | final30 contains-noun 1.6s top=2_2_r2
- 2.2 e93: record verified 7.1s -> contains-noun 1.5s | P0 core verified 7.7s top=2_3_r70 | final30 contains-noun 1.7s top=2_2_r2

**class 2 g3** — deterministic, 3 entries — final deferred top=- — [no defect named in the text] [DEG]
> `10-p5-attribution.mechanisms-class2-3.md`: No rule answers on the substrate. Each P0 route rested on a binding Mathematica does not make: **e19** `F^(c(a+bx))*((d+e*x)^n)^m`: P0 1_4_1_r41 `(c.*(d_*(a.+b.*x))^q)^p` read the non-Optional `d_` as 1. Rubi's piecewise pair 1_4_1_r43/r44 (`GeQ[a,0]` / `Not[GeQ[a,0]]`) has … — follows from: G-1 (P0 degenerate / implicit-1 bindings are no longer produced); why Rubi's own 2-step routes don't answer on the substrate is not determined from the traces

- 2.1 e19: record verified 1.9s -> deferred 0.4s | P0 core verified 2.2s top=1_4_1_r41 | final30 deferred 0.5s top=-
- 2.3 e624: record verified 4.4s -> deferred 1.7s | P0 core verified 4.7s top=1_2_1_3b_r68 | final30 deferred 1.6s top=-
- 2.3 e767: record verified 6.4s -> deferred 0.1s | P0 core verified 7.1s top=2_3_r101 | final30 deferred 0.1s top=-

**class 2 g4** — deterministic, 2 entries — final unexpected top=2_1_r10 — [IGtQ 2 (from the text, not a tag)] [OPT]
> `10-p5-attribution.mechanisms-class2-3.md`: Noun-expected `sqrt(c+d*x)/(a+%e^x*b)^k`. P0 was no-answer (literal `(c+d*x)^m*(a+b*(F^(g*(e+f*x)))^n)^p` cannot bind `%e^x`). The substrate binds 2_1_r10, which in Rubi requires `ILtQ[p,0] && IGtQ[m,0]`; it accepts m=1/2 because its cond is `is(p < 0) and is(m > 0)` (IGT). The … — follows from: faithful Optional binding exposing the IGtQ/ILtQ translation (generator, P0 bodies identical); condition retry shapes the chain (r3 contains-noun)

- 2.2 e68: record no-answer 5.9s -> unexpected 6.9s | P0 core no-answer 6.0s top=- | final30 unexpected 5.6s top=2_1_r10
- 2.2 e69: record no-answer 6.5s -> unexpected 8.4s | P0 core no-answer 6.7s top=- | final30 unexpected 7.4s top=2_1_r10

**class 2 g5** — deterministic, 2 entries — final unverified top=2_2_r2 — [no defect named in the text] [OPT]
> `10-p5-attribution.mechanisms-class2-3.md`: 2_2_r2 binds first, as in g2. Rubi's chain 2_1_r9 → 2_2_r1 → 3_5_r14 → 2_3_r96 (e88 also 3_3_r3, 2_3_r93, 2_1_r10) builds the corpus's own `log(1+b F/a)` / `polylog(2)` / `polylog(3)` shape, and the zero chain does not close it (answer not recorded). P0: 2_3_r70 alone with n=0 … — follows from: faithful Optional binding (with the P0 DEG binding lost)

- 2.2 e82: record verified 5.9s -> unverified 3.0s | P0 core verified 6.7s top=2_3_r70 | final30 unverified 3.1s top=2_2_r2
- 2.2 e88: record verified 6.9s -> unverified 5.5s | P0 core verified 8.3s top=2_3_r70 | final30 unverified 5.6s top=2_2_r2

**class 2 g6** — deterministic, 1 entries — final contains-noun top=1_4_1_r7 — [no defect named in the text] [OPT]
> `10-p5-attribution.mechanisms-class2-3.md`: e726. Both cores split the sum with 1_4_1_r7. On P0 that was the only fire: both terms fell through to Maxima integrate (NOUN). On the substrate the terms bind 1_4_1_r18 and 2_3_r28 (`F^(a+b(c+dx)^2)(e+fx)^m`, m<-1), giving 2_3_r11 (erfi) and 2_3_r32 (the `F^(...)/(e+f x)` … — follows from: faithful Optional binding

- 2.3 e726: record verified 3.2s -> contains-noun 0.9s | P0 core verified 4.4s top=1_4_1_r7 | final30 contains-noun 1.0s top=1_4_1_r7

**class 2 g7** — deterministic, 1 entries — final deferred top=1_1_3_7_r45 — [no defect named in the text] [not determined]
> `10-p5-attribution.mechanisms-class2-3.md`: e557. 1_1_3_7_r45 (`Pq*(a+b*x^n)^p` → `mr_int(ExpandIntegrand)`) answers alone with a top-level noun. P0 answered with the next rule 1_1_3_7_r46 (subst), so r45 did not answer there. The only Pq candidate, `(F^(sqrt(1-a*x)/sqrt(1+a*x)))^n`, is not a polynomial. Which binding … — follows from: not determined from the traces

- 2.3 e557: record verified 2.8s -> deferred 1.0s | P0 core verified 3.0s top=1_1_3_7_r46 | final30 deferred 1.0s top=1_1_3_7_r45

**class 2 g8** — deterministic, 1 entries — final deferred top=1_1_3_7_r46 — [no defect named in the text] [RETRY]
> `10-p5-attribution.mechanisms-class2-3.md`: e50 `(F^(c(a+bx)))^n*(d+e*x)^(4/3)`. 1_1_3_7_r46 (class 1, ahead of 2.1) answers a top-level noun; P0 route 2_1_r6 / 2_1_r7. r3 (cond_retry=false) reads verified 0.4 s, so r46 accepts only on a non-first binding. r2/r4 deferred. — follows from: condition retry

- 2.1 e50: record verified 3.0s -> deferred 0.3s | P0 core verified 3.8s top=2_1_r7 | final30 deferred 0.4s top=1_1_3_7_r46

**class 2 g9** — deterministic, 1 entries — final deferred top=1_2_3_5_r24 — [no defect named in the text] [RETRY]
> `10-p5-attribution.mechanisms-class2-3.md`: e741 `(2-3x+x^2)/%e^(4x)`. 1_2_3_5_r24 (the 1.2.3.5 Unintegrable catch-all, class 1) answers at top level; P0 route 2_3_r3 (expand). r3 verified 0.1 s: the catch-all accepts only on a retried binding. r2/r4 deferred. — follows from: condition retry

- 2.3 e741: record verified 0.9s -> deferred 0.2s | P0 core verified 1.1s top=2_3_r3 | final30 deferred 0.2s top=1_2_3_5_r24

**class 2 g10** — deterministic, 1 entries — final deferred top=9_1_r27 — [no defect named in the text; collapse-family: 2.1 e15] [9.1-COLLAPSE]
> `10-p5-attribution.mechanisms-class2-3.md`: e15 `F^(c(a+bx))/(d^2+2dex+e^2x^2)`. This is the same Rubi rule on both cores: the 9.1 double-root trinomial, P0 id 9_1_r28, generated 9_1_r27. P0's repl was `rubi_hybrid_exact(u*cancel(…))`: an exact `member` seen test, so the rewrite dispatched and 2_1_r4 answered. The … — follows from: 9.1 regeneration (rubi_hybrid_exact → mr_int) meeting the seen guard

- 2.1 e15: record verified 3.4s -> deferred 0.8s | P0 core verified 3.5s top=9_1_r28 | final30 deferred 0.8s top=9_1_r27

**class 2 g11** — deterministic, 1 entries — final unexpected top=2_1_r9 — [IGtQ 1 (from the text, not a tag)] [OPT]
> `10-p5-attribution.mechanisms-class2-3.md`: e67, noun-expected `sqrt(c+d*x)/(a+%e^x*b)`. 2_1_r9 (Rubi `IGtQ[m,0]`) accepts m=1/2 via `is(m > 0)` (IGT). Chain 9_1_r12, 3_5_r34, 2_2_r1 → answer, self=1. P0 was no-answer (literal `(c+d*x)^m/(a+b*(F^(g*(e+f*x)))^n)` cannot bind `%e^x`). All arms unexpected. — follows from: faithful Optional binding exposing the IGtQ translation

- 2.2 e67: record no-answer 6.0s -> unexpected 4.8s | P0 core no-answer 6.1s top=- | final30 unexpected 3.8s top=2_1_r9

**class 2 g12** — slow-correct, 2 entries — final class/top per entry (see samples) — [no defect named in the text] [RETRY]
> `10-p5-attribution.mechanisms-class2-3.md`: Same route on both cores (e283: 2_3_r16, 2_3_r19; e342: 2_3_r26). Walls: P0 7.7 / 4.0 s; final 30 s timeout with no fire flushed before the kill; final 120 s verified 55.7 / 54.3 s. r3 (cond_retry=false) verified 0.4 / 0.2 s while r2/r4 time out, so the 7–13× cost is … — follows from: condition retry (cost)

- 2.3 e283: record verified 7.2s -> timeout 30.0s | P0 core verified 7.7s top=2_3_r19 | final30 timeout 30.1s top=- | final120 verified 55.7s top=2_3_r19
- 2.3 e342: record verified 3.1s -> timeout 30.0s | P0 core verified 4.0s top=2_3_r26 | final30 timeout 30.1s top=- | final120 verified 54.3s top=2_3_r26

### Class 3

Full entry lists: `probes/matcher/10-p5-attribution.class3.summary.out`.

**class 3 g1** — deterministic, 17 entries — final unverified top=3_4_r8 — [no defect named in the text] [POLY]
> `10-p5-attribution.mechanisms-class2-3.md`: All 17 read on the substrate with 3_4_r8 at top (`x^m (a+b log(c(d+e x^n)^p))^q`, subst x^n). **Nested chain.** The log/x sub-integral runs 3_3_r8 → 3_3_r46 → 3_1_5_r45 (plus 3_1_5_r54 for p=3), or for e96/e97 3_1_4_r10, 3_3_r3, 3_1_3_r6/r7, 3_1_4_r20, 3_3_r23, 3_3_r10 (POLY). … — follows from: faithful Optional binding; e96/e97 condition retry

- 3.4 e80: record verified 7.8s -> unverified 2.8s | P0 core verified 5.8s top=3_5_r7 | final30 unverified 2.4s top=3_4_r8
- 3.4 e432: record verified 7.1s -> unverified 3.7s | P0 core verified 6.5s top=3_4_r8 | final30 unverified 4.1s top=3_4_r8
- 3.4 e526: record verified 4.6s -> unverified 3.3s | P0 core verified 5.1s top=3_4_r8 | final30 unverified 4.5s top=3_4_r8

**class 3 g2** — deterministic, 13 entries — final contains-noun top=3_2_2_r3 — [no defect named in the text] [CATCH-3.1]
> `10-p5-attribution.mechanisms-class2-3.md`: Both cores put 3_2_2_r3 at top (subst `(a+bx)/(c+dx)` → `Int[x^m (A+B log(e x^n))^p/(b-dx)^k]`). **P0 nested:** answered by 1_4_2_r25 (e122–e152) or 3_1_5_r29 (e173–e203). **Substrate nested:** 3_1_4_r27 answers (CATCH-3.1). The 1_1_1_2_r12/r13 fires in the p=1 entries come from … — follows from: faithful binding / MatchQ rewrite (the traces do not separate them); why 3_1_4_r26 does not answer is not determined

- 3.2.2 e122: record verified 3.1s -> contains-noun 2.5s | P0 core verified 2.9s top=3_2_2_r3 | final30 contains-noun 3.6s top=3_2_2_r3
- 3.2.2 e151: record verified 3.2s -> contains-noun 3.6s | P0 core verified 3.0s top=3_2_2_r3 | final30 contains-noun 5.0s top=3_2_2_r3
- 3.2.2 e203: record verified 2.2s -> contains-noun 4.1s | P0 core verified 2.3s top=3_2_2_r3 | final30 contains-noun 5.5s top=3_2_2_r3

**class 3 g3** — deterministic, 11 entries — final unexpected top=1_4_1_r3 — [negQ 7 of 11 (from the text, not a tag: e413/e414/e416/e417/e419/e385/e386; e383/e384/e387/e388 NegQ true in Rubi too)] [OPT]
> `10-p5-attribution.mechanisms-class2-3.md`: Noun-expected (`Unintegrable`, 0 steps). P0 was no-answer (literal `x^m*(a+b*x^n)^p*Fx`). **Binding.** The substrate binds 1_4_1_r3 (Rubi 1.4.1: `x^m (a+b x^n)^p Fx /; IntegerQ[p] && NegQ[n]`) with n = r (3.1.4 e413–e419), 2n (e385) or n (e386). Those accept only through NEGQ … — follows from: faithful Optional binding exposing `%mr_negQ`'s sign-based reading (utility unchanged since P0); why Rubi itself gives a 0-step Unintegrable on e383/e384/e387/e388 is not determined from the traces

- 3.1.4 e413: record no-answer 8.1s -> unexpected 0.3s | P0 core no-answer 8.3s top=- | final30 unexpected 0.2s top=1_4_1_r3
- 3.4 e383: record no-answer 8.1s -> unexpected 0.4s | P0 core no-answer 7.6s top=- | final30 unexpected 4.9s top=1_4_1_r3
- 3.4 e388: record no-answer 8.4s -> unexpected 0.5s | P0 core no-answer 7.2s top=- | final30 unexpected 30.0s top=1_4_1_r3

**class 3 g4** — deterministic, 10 entries — final deferred top=3_1_4_r27 — [no defect named in the text] [CATCH-3.1]
> `10-p5-attribution.mechanisms-class2-3.md`: 3_1_4_r27 answers the top-level `Unintegrable` (CATCH-3.1). **e92–e119** `x^k (a+b log)^2/(d+ex)^q`: Rubi's r26 conditions (`IntegerQ[q] && IGtQ[p,0] && IntegerQ[m] && IntegerQ[r]`) hold, and Rubi expands (8–26 steps). On the substrate r26 does not answer. P0 route: 3_1_5_r29. … — follows from: faithful Optional binding (the P0 literal bound neither r26 nor r27) + the 9.1 regeneration (e355–e364); why r26 and the earlier 3.1.4 rule do not answer is not determined

- 3.1.4 e92: record verified 1.1s -> deferred 2.4s | P0 core verified 1.1s top=3_1_5_r29 | final30 deferred 2.2s top=3_1_4_r27
- 3.1.4 e112: record verified 1.2s -> deferred 2.1s | P0 core verified 1.2s top=3_1_5_r29 | final30 deferred 2.2s top=3_1_4_r27
- 3.1.4 e364: record verified 6.6s -> deferred 2.9s | P0 core verified 5.6s top=9_1_r16 | final30 deferred 2.3s top=3_1_4_r27

**class 3 g5** — deterministic, 7 entries — final contains-noun top=3_1_4_r15 — [no defect named in the text] [CATCH-3.1]
> `10-p5-attribution.mechanisms-class2-3.md`: Both cores put 3_1_4_r15 at top (`x^m (a+b log)/(d+ex)^q` → `Int[(f x)^(m-1)(d+ex)^(q+1)(a m+b n+b m log)]`). P0 nfires=1 (the nested integral fell through, NOUN). On the substrate the nested integral reaches 3_1_4_r27 (CATCH-3.1; 1_1_1_2_r12 fires inside 3_1_4_r23's cond … — follows from: faithful Optional binding

- 3.1.4 e39: record verified 9.1s -> contains-noun 3.4s | P0 core verified 7.3s top=3_1_4_r15 | final30 contains-noun 2.8s top=3_1_4_r15
- 3.1.4 e53: record verified 8.9s -> contains-noun 7.5s | P0 core verified 7.5s top=3_1_4_r15 | final30 contains-noun 6.3s top=3_1_4_r15
- 3.1.4 e63: record verified 8.8s -> contains-noun 13.0s | P0 core verified 7.6s top=3_1_4_r15 | final30 contains-noun 11.7s top=3_1_4_r15

**class 3 g6** — deterministic, 7 entries — final timeout top=3_4_r8 — [no defect named in the text] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class2-3.md`: VERIFY-TIMEOUT. **Fires.** Every 30 s list ends with the top-level 3_4_r8 (P0's top). **Nested chain.** Substrate: 3_1_5_r45, 3_1_4_r10, 3_3_r3, 3_1_3_r6/r7, 3_1_4_r20 (+ 1_1_1_*), 3_3_r23, 3_3_r10; e438 instead 3_1_5_r54/r45, 3_3_r46, 3_3_r8. P0 had only 3_3_r31 (e438 3_3_r8) … — follows from: faithful Optional binding (the cost is in verification); e484 partly condition retry

- 3.4 e419: record verified 4.4s -> timeout 30.0s | P0 core verified 3.9s top=3_4_r8 | final30 timeout 30.0s top=3_4_r8 | final120 timeout 120.0s top=3_4_r8
- 3.4 e438: record verified 6.7s -> timeout 30.0s | P0 core verified 5.9s top=3_4_r8 | final30 timeout 30.0s top=3_4_r8 | final120 unverified 71.6s top=3_4_r8
- 3.4 e525: record verified 2.0s -> unverified 24.5s | P0 core verified 2.3s top=3_4_r8 | final30 timeout 30.0s top=3_4_r8

**class 3 g7** — deterministic, 7 entries — final unverified top=3_1_5_r47 — [no defect named in the text] [OPT]
> `10-p5-attribution.mechanisms-class2-3.md`: Both cores put 3_1_5_r47 at top (`u = Int[(g x)^q log(d(e+f x^m)^r)]`, Dist). **Substrate:** the inner integral binds 3_4_r8 (subst) → 3_3_r7 → 1_1_1_2_r12/r13 (or 1_1_1_1_r1/r3, 1_1_1_2_r3). The Dist'ed `Int[u/x]` runs 1_4_1_r18 (+ 1_4_1_r7/r9, 9_1_r12). **P0:** 3_5_r34 (+ … — follows from: faithful Optional binding

- 3.1.5 e24: record verified 9.1s -> unverified 2.2s | P0 core verified 7.2s top=3_1_5_r47 | final30 unverified 1.4s top=3_1_5_r47
- 3.1.5 e52: record verified 7.8s -> unverified 9.4s | P0 core verified 7.5s top=3_1_5_r47 | final30 unverified 8.4s top=3_1_5_r47
- 3.1.5 e94: record verified 6.4s -> unverified 2.6s | P0 core verified 6.1s top=3_1_5_r47 | final30 unverified 2.1s top=3_1_5_r47

**class 3 g8** — deterministic, 6 entries — final contains-noun top=3_2_1_r19 — [no defect named in the text] [AFX]
> `10-p5-attribution.mechanisms-class2-3.md`: Both cores put 3_2_1_r19 at top (subst). Nested: P0 3_1_5_r28 answered. On the substrate 3_1_4_r29 (3.1.4, ahead of 3.1.5) binds first, and its `Int[… (a+b log)^(p-1)/x]` reaches 3_1_5_r30 (AFX) → marker. All arms contains-noun. — follows from: faithful Optional binding (3_1_4_r29 nested) + the AFx catch-all made live (6a358db)

- 3.2.1 e67: record verified 3.5s -> contains-noun 18.5s | P0 core verified 2.7s top=3_2_1_r19 | final30 contains-noun 16.5s top=3_2_1_r19
- 3.2.1 e240: record verified 2.0s -> contains-noun 12.2s | P0 core verified 2.6s top=3_2_1_r19 | final30 contains-noun 16.6s top=3_2_1_r19
- 3.2.1 e242: record verified 1.8s -> contains-noun 7.0s | P0 core verified 2.5s top=3_2_1_r19 | final30 contains-noun 9.1s top=3_2_1_r19

**class 3 g9** — deterministic, 6 entries — final contains-noun top=3_2_2_r15 — [no defect named in the text] [AFX]
> `10-p5-attribution.mechanisms-class2-3.md`: Both cores put 3_2_2_r15 at top. Nested: P0 3_5_r8 / 3_5_r11. On the substrate the nested integral binds 3_2_1_r19 (3.2.1 is ahead of 3.5; P0 has no defmatch record for it, i.e. a workaround-emitted rule), then 3_1_4_r29 → 3_1_5_r30 (AFX) → marker. r3 reads deferred 0.2 s (still … — follows from: faithful binding + AFx catch-all live; condition retry shapes the chain

- 3.2.1 e303: record verified 3.3s -> contains-noun 11.8s | P0 core verified 4.4s top=3_2_2_r15 | final30 contains-noun 13.9s top=3_2_2_r15
- 3.2.1 e309: record verified 3.8s -> contains-noun 16.2s | P0 core verified 4.8s top=3_2_2_r15 | final30 contains-noun 21.1s top=3_2_2_r15
- 3.2.1 e314: record verified 4.4s -> contains-noun 10.7s | P0 core verified 5.6s top=3_2_2_r15 | final30 contains-noun 14.8s top=3_2_2_r15

**class 3 g10** — deterministic, 6 entries — final unverified top=3_2_2_r3 — [no defect named in the text] [POLY]
> `10-p5-attribution.mechanisms-class2-3.md`: Both cores put 3_2_2_r3 at top. **P0 nested:** no fires (e163/e172/e182) or 3_1_5_r29 (e164/e174/e185), with fall-throughs. **Substrate nested:** 3_1_5_r45, 3_1_4_r10, 3_3_r3, 3_1_3_r6/r7, 3_1_4_r20 (+ 3_1_3_r3/r8, 1_1_1_*), or 3_1_2_r4/r5, 3_1_5_r45, 3_1_4_r10/r11 (POLY). … — follows from: faithful Optional binding; e164 condition retry

- 3.2.2 e163: record verified 3.0s -> unverified 6.2s | P0 core verified 2.5s top=3_2_2_r3 | final30 unverified 8.2s top=3_2_2_r3
- 3.2.2 e174: record verified 2.9s -> unverified 9.9s | P0 core verified 2.3s top=3_2_2_r3 | final30 unverified 12.7s top=3_2_2_r3
- 3.2.2 e185: record verified 2.5s -> unverified 11.5s | P0 core verified 2.5s top=3_2_2_r3 | final30 unverified 14.9s top=3_2_2_r3

**class 3 g11** — deterministic, 4 entries — final deferred top=3_1_3_r20 — [no defect named in the text] [CATCH-3.1]
> `10-p5-attribution.mechanisms-class2-3.md`: 3_1_3_r20 (the 3.1.3 catch-all) answers `(a+b log)^p/(d+e x^r)^2` (r=2,3) at top level (CATCH-3.1). Rubi's r19 conditions (`IntegerQ[q] && IGtQ[p,0] && IntegerQ[r]`) hold, so Rubi expands (16–26 steps); on the substrate r19 does not answer. P0 route: 3_1_5_r29. All arms deferred. — follows from: faithful Optional binding (P0 bound neither of the pair); why r19 does not answer is not determined

- 3.1.4 e247: record verified 1.3s -> deferred 0.7s | P0 core verified 1.4s top=3_1_5_r29 | final30 deferred 0.7s top=3_1_3_r20
- 3.1.4 e324: record verified 1.5s -> deferred 1.1s | P0 core verified 1.1s top=3_1_5_r29 | final30 deferred 0.7s top=3_1_3_r20
- 3.1.4 e325: record verified 1.2s -> deferred 0.8s | P0 core verified 1.1s top=3_1_5_r29 | final30 deferred 0.7s top=3_1_3_r20

**class 3 g12** — deterministic, 4 entries — final timeout top=3_1_5_r47 — [no defect named in the text] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class2-3.md`: VERIFY-TIMEOUT on the g7 route (1_1_1_2_r13, 3_3_r7, 3_4_r8, 1_4_1_r18, top 3_1_5_r47 fired). **Deaths.** At 120 s three die without a CLASS line at 45–46 s. The 100 s re-check has e51/e119/e121 as error at 99.1 / 71.9 / 73.8 s. **Arms.** e51 verifies 1.5 s under r4 … — follows from: faithful Optional binding (the g7 route); e51 also the model flags (r4 verified)

- 3.1.5 e51: record verified 8.9s -> timeout 30.2s | P0 core verified 7.4s top=3_1_5_r47 | final30 timeout 30.1s top=3_1_5_r47 | final120 error 45.1s top=3_1_5_r47
- 3.1.5 e120: record verified 10.3s -> error 26.1s | P0 core verified 7.4s top=3_1_5_r47 | final30 timeout 30.1s top=3_1_5_r47
- 3.1.5 e121: record verified 7.9s -> timeout 30.1s | P0 core verified 7.5s top=3_1_5_r47 | final30 timeout 30.1s top=3_1_5_r47 | final120 error 45.1s top=3_1_5_r47

**class 3 g13** — deterministic, 3 entries — final contains-noun top=1_4_1_r7 — [no defect named in the text] [OPT]
> `10-p5-attribution.mechanisms-class2-3.md`: Sum integrands; both cores split with 1_4_1_r7. **e207** (P0 expected): the terms reach 3_1_5_r55 and 3_1_5_r57, the polylog catch-all (P0 literal `(d*x)^m*polylog(k,e*x^q)*(a+b*log(c*x^n))^p` cannot bind the `1/x` form), plus 1_4_1_r18. P0 answered one term with 3_1_5_r55 and … — follows from: faithful Optional binding

- 3.1.5 e207: record expected 2.6s -> contains-noun 2.9s | P0 core expected 2.8s top=1_4_1_r7 | final30 contains-noun 2.4s top=1_4_1_r7
- 3.2.3 e74: record verified 3.6s -> contains-noun 9.2s | P0 core verified 3.1s top=1_4_1_r7 | final30 contains-noun 9.9s top=1_4_1_r7
- 3.2.3 e75: record verified 3.1s -> contains-noun 8.6s | P0 core verified 3.1s top=1_4_1_r7 | final30 contains-noun 10.0s top=1_4_1_r7

**class 3 g14** — deterministic, 3 entries — final contains-noun top=3_1_5_r56 — [no defect named in the text] [AFX]
> `10-p5-attribution.mechanisms-class2-3.md`: `(d x)^m (a+b log) polylog(k, e x^q)`. P0 answered via the manual 9.1 `u*(a*x^n)^m` (P0 9_1_r16). On the substrate that rule is gone (generated 9_1_r15 needs a non-Optional `x^n`), and 3_1_5_r56 reduces to nested integrals that reach 3_1_5_r30 (AFX) → marker. The corpus answers … — follows from: 9.1 regeneration + AFx catch-all live

- 3.1.5 e220: record verified 2.2s -> contains-noun 1.8s | P0 core verified 2.3s top=9_1_r16 | final30 contains-noun 1.7s top=3_1_5_r56
- 3.1.5 e221: record verified 2.1s -> contains-noun 3.0s | P0 core verified 2.2s top=9_1_r16 | final30 contains-noun 2.5s top=3_1_5_r56
- 3.1.5 e222: record verified 1.9s -> contains-noun 4.1s | P0 core verified 2.3s top=9_1_r16 | final30 contains-noun 3.3s top=3_1_5_r56

**class 3 g15** — deterministic, 3 entries — final contains-noun top=3_2_1_r20 — [no defect named in the text] [AFX]
> `10-p5-attribution.mechanisms-class2-3.md`: `(f+gx)^m (A+B log(e (a+bx)^2/(c+dx)^2))^2`. The substrate binds 3_2_1_r20, whose LHS `Log[e (a+bx)^n (c+dx)^mn]` is this integrand's form. P0's workaround-emitted 3_2_1_r19 (no defmatch record) bound it instead. Nested 3_1_4_r29 → 3_1_5_r30 (AFX) → marker; P0 nested 3_1_5_r28. … — follows from: faithful binding + AFx catch-all live

- 3.2.1 e272: record verified 1.9s -> contains-noun 12.4s | P0 core verified 2.6s top=3_2_1_r19 | final30 contains-noun 16.7s top=3_2_1_r20
- 3.2.1 e273: record verified 2.0s -> contains-noun 9.9s | P0 core verified 2.4s top=3_2_1_r19 | final30 contains-noun 13.8s top=3_2_1_r20
- 3.2.1 e274: record verified 1.8s -> contains-noun 7.3s | P0 core verified 2.4s top=3_2_1_r19 | final30 contains-noun 9.3s top=3_2_1_r20

**class 3 g16** — deterministic, 3 entries — final contains-noun top=3_3_r10 — [no defect named in the text] [AFX]
> `10-p5-attribution.mechanisms-class2-3.md`: `(a+b log(c(d+ex)^n))^(k/2)/(f+gx)^3`; the corpus answers (1 step) contain `Unintegrable`. **Substrate:** 3_3_r10 (Rubi's 1-step rule; P0's slot literal `m1b*(a+b*log(c*(d+e*x)^n))^p` did not bind). Its sub-integral reaches 3_3_r32 (AFX, e110) or, via 3_3_r23 / 3_1_4_r20 / … — follows from: faithful Optional binding (+ AFx live for e110)

- 3.3 e110: record verified 2.8s -> contains-noun 3.3s | P0 core verified 2.3s top=3_5_r8 | final30 contains-noun 2.9s top=3_3_r10
- 3.3 e116: record verified 2.6s -> contains-noun 13.0s | P0 core verified 2.4s top=3_5_r8 | final30 contains-noun 10.9s top=3_3_r10
- 3.3 e122: record verified 2.7s -> contains-noun 13.3s | P0 core verified 2.5s top=3_5_r8 | final30 contains-noun 13.6s top=3_3_r10

**class 3 g17** — deterministic, 3 entries — final contains-noun top=3_3_r9 — [no defect named in the text] [AFX]
> `10-p5-attribution.mechanisms-class2-3.md`: `(a+b log(…))^(k/2)/(f+gx)^2`; the corpus answers contain `Unintegrable`. Both cores put 3_3_r9 at top. The sub-integral `Int[(a+b log)^(p-1)/(f+gx)]` falls through on P0 (or 3_5_r7 / 3_3_r8). On the substrate it reaches 3_3_r32 (AFX; e109/e115) or 3_1_5_r57 (e121) → marker, the … — follows from: AFx catch-all live (e109/e115); faithful Optional binding (e121)

- 3.3 e109: record verified 2.3s -> contains-noun 1.2s | P0 core verified 2.3s top=3_3_r9 | final30 contains-noun 1.2s top=3_3_r9
- 3.3 e115: record verified 4.6s -> contains-noun 1.7s | P0 core verified 4.5s top=3_3_r9 | final30 contains-noun 1.2s top=3_3_r9
- 3.3 e121: record verified 7.0s -> contains-noun 5.6s | P0 core verified 6.3s top=3_3_r9 | final30 contains-noun 5.2s top=3_3_r9

**class 3 g18** — deterministic, 3 entries — final contains-noun top=3_4_r11 — [no defect named in the text] [OPT]
> `10-p5-attribution.mechanisms-class2-3.md`: 3_4_r11 binds on the substrate (P0 literal `(f*x)^m*(a+b*log(c*(d+e*x^n)^p))^q` did not bind `x^-3` or a bare `log^q`). **e136:** the sub-integral reaches 3_4_r27 (3.4 catch-all). The corpus answer (39 steps) has none; P0 answered via 3_5_r8 and a long class-1 chain. … — follows from: faithful Optional binding (+ 9.1 regeneration for e158/e159); why Rubi's route for e136's sub-integral does not answer before 3_4_r27 is not determined

- 3.4 e136: record verified 5.2s -> contains-noun 1.2s | P0 core verified 4.7s top=3_5_r8 | final30 contains-noun 1.0s top=3_4_r11
- 3.4 e158: record verified 4.7s -> contains-noun 3.0s | P0 core verified 4.9s top=9_1_r16 | final30 contains-noun 2.7s top=3_4_r11
- 3.4 e159: record verified 4.5s -> contains-noun 2.0s | P0 core verified 4.5s top=9_1_r16 | final30 contains-noun 2.0s top=3_4_r11

**class 3 g19** — deterministic, 3 entries — final deferred top=- — [no defect named in the text] [DEG]
> `10-p5-attribution.mechanisms-class2-3.md`: No rule answers (a top-level noun). P0 answered with 3_5_r44 `u.*(a.*x^m.+b.*x^r.*log(c x^n)^q.)^p.`. On `x*log(f x^p)` / `x+log(x)` that needs an absent `x^r` (r=0) or a zero coefficient (DEG). e625's corpus answer contains `Unintegrable`; e292/e293 are Rubi 2/8 steps. All arms … — follows from: G-1 (P0 degenerate binding); Rubi's own route is not reached, why is not determined

- 3.4 e625: record verified 8.9s -> deferred 1.9s | P0 core verified 6.2s top=3_5_r44 | final30 deferred 1.4s top=-
- 3.5 e292: record verified 4.9s -> deferred 1.0s | P0 core verified 5.1s top=3_5_r44 | final30 deferred 1.2s top=-
- 3.5 e293: record verified 3.6s -> deferred 0.8s | P0 core verified 3.7s top=3_5_r44 | final30 deferred 1.1s top=-

**class 3 g20** — deterministic, 3 entries — final deferred top=3_1_4_r26 — [no defect named in the text] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class2-3.md`: `(f x)^m (d+e x^r)^q (a+b log)^p`, q=1..3. 3_1_4_r26 (the q>0 expansion branch) answers alone (nfires=1) with a top-level noun: its ExpandIntegrand sum has no nested fire, the same shape as class 2 g1. P0 route: the manual 9.1 `u*(a*x^n)^m`. All arms deferred. — follows from: 9.1 regeneration + faithful binding; why the nested sum yields no fire is not determined

- 3.1.4 e448: record verified 4.3s -> deferred 2.0s | P0 core verified 5.4s top=9_1_r16 | final30 deferred 2.3s top=3_1_4_r26
- 3.1.4 e449: record verified 4.2s -> deferred 1.8s | P0 core verified 5.3s top=9_1_r16 | final30 deferred 2.2s top=3_1_4_r26
- 3.1.4 e450: record verified 4.2s -> deferred 1.1s | P0 core verified 5.1s top=9_1_r16 | final30 deferred 1.3s top=3_1_4_r26

**class 3 g21** — deterministic, 3 entries — final timeout top=3_1_4_r20 — [no defect named in the text] [POLY]
> `10-p5-attribution.mechanisms-class2-3.md`: At 30 s the fire list is mid-chain (the g6 prefix, last 1_1_1_2_r14). At 120 s the top-level 3_4_r8 has fired and the entries still time out: the corpus answers are 62-step Rubi forms, and verification does not finish. P0: 3_3_r31 + 3_4_r8 at 2.4–4.4 s. All arms timeout. — follows from: faithful Optional binding (POLY; cost in integration and verification)

- 3.4 e462: record verified 4.4s -> timeout 30.0s | P0 core verified 3.9s top=3_4_r8 | final30 timeout 30.0s top=3_1_4_r20 | final120 timeout 120.2s top=3_4_r8
- 3.4 e503: record verified 2.4s -> timeout 30.0s | P0 core verified 2.3s top=3_4_r8 | final30 timeout 30.0s top=3_1_4_r20 | final120 timeout 120.2s top=3_4_r8
- 3.4 e524: record verified 3.5s -> timeout 30.0s | P0 core verified 3.7s top=3_4_r8 | final30 timeout 30.0s top=3_1_4_r20 | final120 timeout 120.3s top=3_4_r8

**class 3 g22** — deterministic, 3 entries — final unverified top=3_1_4_r11 — [no defect named in the text] [POLY]
> `10-p5-attribution.mechanisms-class2-3.md`: `(a+b log)^2/(x^k (d+ex))`. The substrate binds 3_1_4_r11 (P0 literal `x^m*(a+b*log(c*x^n))^p/(d+e*x^r)` cannot bind r=1), then 3_1_2_r4/r5, 3_1_5_r45, 3_1_4_r10 (POLY). P0: 3_1_5_r29. All arms unverified. — follows from: faithful Optional binding

- 3.1.4 e97: record verified 1.2s -> unverified 5.8s | P0 core verified 1.0s top=3_1_5_r29 | final30 unverified 5.8s top=3_1_4_r11
- 3.1.4 e98: record verified 1.4s -> unverified 8.3s | P0 core verified 1.1s top=3_1_5_r29 | final30 unverified 8.4s top=3_1_4_r11
- 3.1.4 e99: record verified 1.2s -> unverified 10.9s | P0 core verified 1.1s top=3_1_5_r29 | final30 unverified 11.7s top=3_1_4_r11

**class 3 g23** — deterministic, 3 entries — final unverified top=3_2_1_r2 — [no defect named in the text] [POLY]
> `10-p5-attribution.mechanisms-class2-3.md`: Both cores put 3_2_1_r2 at top. **Substrate nested chains (POLY):** e311 3_1_5_r45, 3_1_3_r6, 3_2_1_r17; e98 3_1_5_r45, 3_1_4_r10, 3_2_1_r16; e101 3_1_5_r45, 3_1_3_r6, 3_2_1_r18. **P0:** 3_2_2_r15 / 3_3_r3, 1_1_1_1_r1, 3_1_3_r6, 3_2_1_r18 / … 3_1_5_r15, 3_2_1_r16. … — follows from: faithful binding; e311 condition retry

- 3.2.1 e311: record verified 6.0s -> unverified 2.4s | P0 core verified 6.6s top=3_2_1_r2 | final30 unverified 3.3s top=3_2_1_r2
- 3.2.3 e98: record verified 5.5s -> unverified 3.6s | P0 core verified 5.0s top=3_2_1_r2 | final30 unverified 3.3s top=3_2_1_r2
- 3.2.3 e101: record verified 7.0s -> unverified 2.5s | P0 core verified 6.5s top=3_2_1_r2 | final30 unverified 2.1s top=3_2_1_r2

**class 3 g24** — deterministic, 3 entries — final unverified top=3_2_2_r15 — [no defect named in the text] [POLY]
> `10-p5-attribution.mechanisms-class2-3.md`: Both cores put 3_2_2_r15 at top. Nested: P0 3.5 rules (3_5_r7, 3_5_r11, 3_5_r8, 1_3_3_r13). On the substrate, 3.2.1 rules ahead of 3.5 (3_2_1_r15 / 3_2_1_r19) → 3_1_4_r10 / 3_1_3_r6/r7 → 3_1_5_r45 (POLY). r3 reads deferred 0.2–0.3 s; r2/r4 unverified. — follows from: faithful binding; the final route needs condition retry (r3 deferred)

- 3.2.1 e159: record verified 5.6s -> unverified 4.1s | P0 core verified 5.4s top=3_2_2_r15 | final30 unverified 4.7s top=3_2_2_r15
- 3.2.1 e167: record verified 5.0s -> unverified 4.5s | P0 core verified 4.7s top=3_2_2_r15 | final30 unverified 5.9s top=3_2_2_r15
- 3.2.1 e313: record verified 2.7s -> unverified 3.4s | P0 core verified 3.4s top=3_2_2_r15 | final30 unverified 4.5s top=3_2_2_r15

**class 3 g25** — deterministic, 3 entries — final unverified top=3_3_r6 — [no defect named in the text] [not determined]
> `10-p5-attribution.mechanisms-class2-3.md`: `(a+b log(c(d+ex)^n))/(f+gx)`. Both cores put 3_3_r6 at top. **P0:** the sub-integral `Int[log(e(f+gx)/(ef-dg))/(d+ex)]` bound 3_4_r1 (`Pq^m log(u)` → `C polylog(2, 1-u)`), giving the corpus form. **Substrate:** no nested fire (nfires=1), so the sub-integral falls through to … — follows from: not determined from the traces

- 3.3 e40: record expected 3.0s -> unverified 1.5s | P0 core expected 2.3s top=3_3_r6 | final30 unverified 1.1s top=3_3_r6
- 3.3 e220: record expected 2.6s -> unverified 1.5s | P0 core expected 2.3s top=3_3_r6 | final30 unverified 1.0s top=3_3_r6
- 3.3 e245: record expected 2.1s -> unverified 1.0s | P0 core expected 2.3s top=3_3_r6 | final30 unverified 1.1s top=3_3_r6

**class 3 g26** — deterministic, 3 entries — final unverified top=3_5_r15 — [no defect named in the text] [OPT]
> `10-p5-attribution.mechanisms-class2-3.md`: `x^k log(a+%e^x b)`. The substrate binds 3_5_r15 (P0 literal `(f+g*x)^m*log(d+e*(F^(c*(a+b*x)))^n)` cannot bind `x^k` or `%e^x`), then 3_5_r14 (polylog) and 2_3_r96 (e115): the corpus's polylog(k+2) route. P0: 3_5_r34 / 3_5_r37 with fall-throughs. All arms unverified. — follows from: faithful Optional binding

- 3.5 e113: record verified 2.7s -> unverified 0.7s | P0 core verified 2.6s top=3_5_r34 | final30 unverified 0.9s top=3_5_r15
- 3.5 e114: record verified 2.6s -> unverified 0.6s | P0 core verified 2.4s top=3_5_r34 | final30 unverified 0.8s top=3_5_r15
- 3.5 e115: record verified 2.0s -> unverified 0.4s | P0 core verified 2.0s top=3_5_r37 | final30 unverified 0.6s top=3_5_r15

**class 3 g27** — deterministic, 2 entries — final contains-noun top=3_1_4_r29 — [no defect named in the text] [AFX]
> `10-p5-attribution.mechanisms-class2-3.md`: `(f+gx)(a+b log)^p/(d+ex)^3`. 3_1_4_r29 binds (P0 literal `(f+g*x)^m*(d+e*x)^q*(a+b*log(c*x^n))^p` needs an explicit `(f+g*x)^m`), and its `Int[…(a+b log)^(p-1)/x]` reaches 3_1_5_r30 (AFX) → marker. P0: 3_1_5_r28, verified. All arms contains-noun. — follows from: faithful Optional binding + AFx catch-all live

- 3.1.4 e455: record verified 1.0s -> contains-noun 5.0s | P0 core verified 1.3s top=3_1_5_r28 | final30 contains-noun 6.3s top=3_1_4_r29
- 3.1.4 e456: record verified 1.0s -> contains-noun 8.9s | P0 core verified 1.4s top=3_1_5_r28 | final30 contains-noun 10.4s top=3_1_4_r29

**class 3 g28** — deterministic, 2 entries — final contains-noun top=3_1_5_r42 — [no defect named in the text] [CATCH-3.1]
> `10-p5-attribution.mechanisms-class2-3.md`: `(a+b log)^2 log(d(e+f x^2)^m)`. P0 answered at top with 3_5_r44 after 3_1_1_r1 / 1_4_1_r7 / 3_1_1_r2 (21–23 s). On the substrate 3_1_5_r42 (3.1.5, ahead of 3.5) answers: `u = Int[(a+b log)^2]` (the same 3_1_1 fires), then the Dist'ed `Int[x/(e+fx^2) u]` reaches 3_1_4_r27 … — follows from: faithful Optional binding

- 3.1.5 e37: record verified 23.2s -> contains-noun 6.4s | P0 core verified 21.4s top=3_5_r44 | final30 contains-noun 6.5s top=3_1_5_r42
- 3.1.5 e105: record verified 22.8s -> contains-noun 6.8s | P0 core verified 21.6s top=3_5_r44 | final30 contains-noun 6.5s top=3_1_5_r42

**class 3 g29** — deterministic, 2 entries — final contains-noun top=3_3_r38 — [no defect named in the text] [CATCH-3.1]
> `10-p5-attribution.mechanisms-class2-3.md`: `x^k log(f x^m)(a+b log(c(d+ex)^n))`. Both cores put 3_3_r38 at top. The nested `Int[(gx)^(q+1) log(f x^m)/(d+ex)]` gets 1_1_1_2_r13 and a fall-through on P0. On the substrate it gets 1_1_1_2_r12 (inside 3_1_4_r23's cond, INNER) → 3_1_4_r27 (CATCH-3.1) → marker. All arms … — follows from: faithful Optional binding

- 3.3 e358: record verified 3.8s -> contains-noun 3.1s | P0 core verified 3.2s top=3_3_r38 | final30 contains-noun 2.0s top=3_3_r38
- 3.3 e359: record verified 3.9s -> contains-noun 2.0s | P0 core verified 3.2s top=3_3_r38 | final30 contains-noun 1.9s top=3_3_r38

**class 3 g30** — deterministic, 2 entries — final deferred top=3_1_5_r30 — [no defect named in the text] [AFX]
> `10-p5-attribution.mechanisms-class2-3.md`: 3_1_5_r30 (AFX, 3.1.5, ahead of 3.2.3 and 3.5) answers `Unintegrable` at top level. **e350** `log(a x^(1-n))/(a x - x^n)`: AFx with a symbolic exponent, accepted by the new flag. P0 reached expected via 3_5_r1. **e270** `(b+2cx) log(x)/(x(b+cx))`: P0 verified via the manual 9.1 … — follows from: AFx catch-all made live (6a358db) + faithful binding

- 3.1.4 e350: record expected 1.2s -> deferred 0.8s | P0 core expected 1.0s top=3_5_r1 | final30 deferred 0.5s top=3_1_5_r30
- 3.5 e270: record verified 14.0s -> deferred 2.0s | P0 core verified 13.3s top=3_2_3_r16 | final30 deferred 2.8s top=3_1_5_r30

**class 3 g31** — deterministic, 2 entries — final deferred top=3_2_2_r15 — [no defect named in the text] [OPT]
> `10-p5-attribution.mechanisms-class2-3.md`: `1/((f+gx)(ah+bhx)(A+B log(…))^k)`. 3_2_2_r15's sub-integral reaches 3_2_2_r11 (the 3.2.2 catch-all); the subst leaves a top-level noun → deferred. The corpus answers are `_subst(…, Unintegrable(…))`, 1 step, so this is Rubi's own form (yardstick). P0: 3_2_2_r15 alone (nfires=1 … — follows from: faithful Optional binding (NOUN)

- 3.2.2 e253: record verified 2.1s -> deferred 5.5s | P0 core verified 2.2s top=3_2_2_r15 | final30 deferred 5.8s top=3_2_2_r15
- 3.2.2 e254: record verified 2.5s -> deferred 5.1s | P0 core verified 2.6s top=3_2_2_r15 | final30 deferred 6.1s top=3_2_2_r15

**class 3 g32** — deterministic, 2 entries — final deferred top=3_3_r60 — [no defect named in the text] [AFX]
> `10-p5-attribution.mechanisms-class2-3.md`: `log(i(j(hx)^t)^u)^k log(e(f(a+bx)^p(c+dx)^q)^r)/x`. Both cores put 3_3_r60 at top. **Substrate chain:** 3_1_5_r54/r45, 3_1_3_r6, 3_2_3_r8, 3_3_r61 (AFX), 1_1_1_1_r2, 3_1_2_r2 → top-level noun at 22–28 s. **P0:** 3_3_r8, 3_2_3_r8 → verified 15–20 s. **Why the noun survives.** … — follows from: AFx catch-all live; how the marker becomes the top-level noun through 3_3_r60's subst is not determined

- 3.2.3 e56: record verified 20.0s -> deferred 27.8s | P0 core verified 15.1s top=3_3_r60 | final30 deferred 27.6s top=3_3_r60
- 3.2.3 e57: record verified 16.9s -> deferred 21.9s | P0 core verified 14.6s top=3_3_r60 | final30 deferred 22.3s top=3_3_r60

**class 3 g33** — deterministic, 2 entries — final timeout top=3_1_4_r16 — [no defect named in the text] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class2-3.md`: VERIFY-TIMEOUT. Both cores put 3_1_4_r16 at top (P0 nfires=1). **Substrate nested:** 3_1_4_r23, whose cond (INNER) runs `Int[(f x)^m (d+e x^2)^q]` (fires 1_1_2_1_r15, 1_1_1_2_r32/r11, 1_1_2_2_r4, 1_4_1_r18); the repl then runs it again. **Timing.** The top-level fire is in the … — follows from: faithful Optional binding (3_1_4_r23 nested) with the moved inner condition doubling its sub-integral; the remaining cost is verification

- 3.1.4 e291: record verified 11.4s -> timeout 30.0s | P0 core verified 8.5s top=3_1_4_r16 | final30 timeout 30.1s top=3_1_4_r16 | final120 timeout 120.2s top=3_1_4_r16
- 3.1.4 e302: record verified 9.8s -> timeout 30.0s | P0 core verified 8.4s top=3_1_4_r16 | final30 timeout 30.1s top=3_1_4_r16 | final120 timeout 120.3s top=3_1_4_r16

**class 3 g34** — deterministic, 2 entries — final timeout top=3_4_r5 — [no defect named in the text] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class2-3.md`: VERIFY-TIMEOUT. Both cores put 3_4_r5 at top. **Substrate nested:** 3_4_r8 → 3_3_r10/r23 → 3_1_4_r20 / 3_1_3_r6/r7 / 3_3_r3 / 3_1_4_r10 / 3_1_5_r45 (POLY). P0 nested: 3_3_r31, 3_4_r8, fall-throughs. **Timing.** The top-level fire is in the 30 s list, so rubi returned. **Arms.** … — follows from: faithful Optional binding; e504 condition retry

- 3.4 e437: record verified 3.8s -> timeout 30.0s | P0 core verified 3.3s top=3_4_r5 | final30 timeout 30.0s top=3_4_r5 | final120 timeout 120.2s top=3_4_r5
- 3.4 e504: record verified 4.3s -> timeout 30.0s | P0 core verified 4.5s top=3_4_r5 | final30 timeout 30.0s top=3_4_r5 | final120 timeout 120.2s top=3_4_r5

**class 3 g35** — deterministic, 2 entries — final unverified top=3_1_4_r18 — [no defect named in the text] [OPT]
> `10-p5-attribution.mechanisms-class2-3.md`: `(a+b log) x^k/(sqrt(d-ex) sqrt(d+ex))`. The substrate binds 3_1_4_r18 (P0 literal `x^m*(d1+e1*x)^q*(d2+e2*x)^q*(a+b*log(c*x^n))`, shared q slot, did not bind). It feeds nested 3_1_4_r23 (INNER; cond fires 1_1_2_1_r15/r17, 1_1_1_2_r32/r11, 1_1_2_2_r4/r23, 1_4_1_r18) → Dist … — follows from: faithful Optional binding

- 3.1.4 e312: record verified 1.4s -> unverified 8.5s | P0 core verified 1.1s top=1_4_2_r25 | final30 unverified 8.0s top=3_1_4_r18
- 3.1.4 e313: record verified 1.8s -> unverified 8.7s | P0 core verified 1.4s top=1_4_2_r25 | final30 unverified 7.4s top=3_1_4_r18

**class 3 g36** — deterministic, 2 entries — final unverified top=3_2_3_r8 — [no defect named in the text] [POLY]
> `10-p5-attribution.mechanisms-class2-3.md`: e51 has 3_2_3_r8 at top on both cores. e52 (power 1) has P0 top 3_2_3_r9; on the substrate 3_2_3_r8 (`m_.`=1, ahead of r9) binds. Nested: 3_1_5_r54/r45, 3_3_r46, 3_3_r8 (POLY) versus P0 3_3_r31 / 3_3_r8. All arms unverified. — follows from: faithful Optional binding

- 3.2.3 e51: record verified 8.1s -> unverified 12.5s | P0 core verified 7.1s top=3_2_3_r8 | final30 unverified 10.8s top=3_2_3_r8
- 3.2.3 e52: record verified 8.9s -> unverified 7.1s | P0 core verified 7.8s top=3_2_3_r9 | final30 unverified 6.1s top=3_2_3_r8

**class 3 g37** — deterministic, 2 entries — final unverified top=3_4_r17 — [no defect named in the text] [OPT]
> `10-p5-attribution.mechanisms-class2-3.md`: `(d+ex)^k log(c(a+bx^3)^p)`. 3_4_r17 binds (P0 literal `(f+g*x)^r*(a+b*log(c*(d+e*x^n)^p))` needs explicit a, b and r), then 1_1_3_8_r18 (+ 1_1_1_2_r12, 1_1_3_4_r9 / 1_4_1_r18). P0: 3_5_r34 / 3_5_r37. All arms unverified. — follows from: faithful Optional binding

- 3.4 e192: record verified 2.4s -> unverified 3.0s | P0 core verified 2.7s top=3_5_r34 | final30 unverified 2.4s top=3_4_r17
- 3.4 e193: record verified 1.8s -> unverified 2.7s | P0 core verified 1.8s top=3_5_r37 | final30 unverified 2.3s top=3_4_r17

**class 3 g38** — deterministic, 2 entries — final unverified top=3_4_r38 — [no defect named in the text] [POLY]
> `10-p5-attribution.mechanisms-class2-3.md`: `(a+b log(c(d+e/(f+gx))^p))^k`. Both cores run 3_4_r38 → 3_4_r3 → 3_4_r8 → 3_3_r8. The substrate adds 3_3_r46 and 3_1_5_r45 (e636 also 3_1_5_r54), as in g1 (POLY); P0 verified with a fall-through below 3_3_r8. All arms unverified. — follows from: faithful Optional binding

- 3.4 e636: record verified 8.7s -> unverified 5.6s | P0 core verified 5.8s top=3_4_r38 | final30 unverified 4.8s top=3_4_r38
- 3.4 e637: record verified 9.2s -> unverified 3.5s | P0 core verified 6.3s top=3_4_r38 | final30 unverified 3.2s top=3_4_r38

**class 3 g39** — deterministic, 1 entries — final contains-noun top=3_1_3_r7 — [no defect named in the text] [OPT]
> `10-p5-attribution.mechanisms-class2-3.md`: e128 `sqrt(a+b log)/(d+ex)^2`; the corpus answer (1 step) contains `Unintegrable`. Both cores put 3_1_3_r7 at top. The nested `Int[(a+b log)^(-1/2)/(d+ex)]` falls through on P0. On the substrate it reaches 3_1_3_r20 (r19's `IGtQ[p,0]` rightly fails) → marker, the corpus's own … — follows from: faithful Optional binding (NOUN)

- 3.1.4 e128: record verified 2.1s -> contains-noun 0.9s | P0 core verified 2.3s top=3_1_3_r7 | final30 contains-noun 1.1s top=3_1_3_r7

**class 3 g40** — deterministic, 1 entries — final contains-noun top=3_1_3_r8 — [no defect named in the text] [OPT]
> `10-p5-attribution.mechanisms-class2-3.md`: e129 `sqrt(a+b log)/(d+ex)^3`; the corpus answer contains `Unintegrable`. The substrate answers with 3_1_3_r8 (P0 answered at top with the later 3_5_r8). Its nested `Int[(d+ex)^(q+1)(a+b log)^(p-1)/x]` reaches 3_1_4_r27 (r26's `IGtQ[p,0]` fails in Rubi too) → marker, the corpus … — follows from: faithful Optional binding

- 3.1.4 e129: record verified 3.0s -> contains-noun 2.1s | P0 core verified 3.0s top=3_5_r8 | final30 contains-noun 2.7s top=3_1_3_r8

**class 3 g41** — deterministic, 1 entries — final contains-noun top=3_3_r34 — [no defect named in the text] [CATCH-3.1]
> `10-p5-attribution.mechanisms-class2-3.md`: e361 `log(f x^m)(a+b log(c(d+ex)^n))`. Both cores put 3_3_r34 at top. The nested `Int[x log(f x^m)/(d+ex)]` falls through on P0. On the substrate: 1_1_1_2_r12 (INNER) → 3_1_4_r27 (CATCH-3.1) → marker. The corpus answer (8 steps) has none. All arms contains-noun. — follows from: faithful Optional binding

- 3.3 e361: record verified 6.0s -> contains-noun 1.6s | P0 core verified 5.5s top=3_3_r34 | final30 contains-noun 0.9s top=3_3_r34

**class 3 g42** — deterministic, 1 entries — final contains-noun top=3_3_r39 — [no defect named in the text] [OPT]
> `10-p5-attribution.mechanisms-class2-3.md`: e370. Both cores put 3_3_r39 at top. The nested `Int[log(f x^m)^2 (a+b log)/(d+ex)]` falls through on P0. On the substrate it reaches 3_3_r56 (the 3.3 two-log catch-all; P0 literal needs explicit `(k+l*x)^r`, `i+j*x`) → marker. The corpus answer has none. All arms contains-noun. — follows from: faithful Optional binding

- 3.3 e370: record verified 2.8s -> contains-noun 3.7s | P0 core verified 2.1s top=3_3_r39 | final30 contains-noun 2.4s top=3_3_r39

**class 3 g43** — deterministic, 1 entries — final contains-noun top=3_3_r54 — [no defect named in the text] [AFX]
> `10-p5-attribution.mechanisms-class2-3.md`: e391 `(a+b log(c(d+ex)^n))(f+g log(h(i+jx)^m))/x^2`. P0 top was 3_3_r55. On the substrate 3_3_r54 (`x^r`·two logs, ahead of r55) binds; its sub-integral runs 1_1_1_1_r1/r3, 1_1_1_2_r3 → 3_3_r32 (AFX) → marker. The corpus answer (15 steps) has none. All arms contains-noun. — follows from: faithful Optional binding + AFx catch-all live

- 3.3 e391: record verified 1.6s -> contains-noun 4.1s | P0 core verified 1.5s top=3_3_r55 | final30 contains-noun 3.4s top=3_3_r54

**class 3 g44** — deterministic, 1 entries — final contains-noun top=3_4_r5 — [no defect named in the text] [OPT]
> `10-p5-attribution.mechanisms-class2-3.md`: e522 `(a+b log(c(d+e/x^(2/3))^n))^2`. Both cores put 3_4_r5 at top. The subst sub-integral falls through on P0. On the substrate it runs 3_4_r11 → 3_4_r27 (3.4 catch-all) → marker. The corpus answer (14 steps) has none. All arms contains-noun. — follows from: faithful Optional binding; why Rubi's route for 3_4_r11's sub-integral does not answer before 3_4_r27 is not determined

- 3.4 e522: record verified 3.3s -> contains-noun 0.8s | P0 core verified 3.4s top=3_4_r5 | final30 contains-noun 1.2s top=3_4_r5

**class 3 g45** — deterministic, 1 entries — final deferred top=3_3_r32 — [no defect named in the text] [AFX]
> `10-p5-attribution.mechanisms-class2-3.md`: e223 `log(c(a+bx)^p)/(x(d+ex))`. 3_3_r32 (AFX; AFx = `1/(x(d+ex))`; 3.3 is ahead of 3.2.3) answers `Unintegrable` at top level. The preceding 1_1_1_1_r1/r3 and 1_1_1_2_r3 fires have no answering parent (a condition's sub-integral). P0 verified via the manual 9.1 constant rule + … — follows from: AFx catch-all made live (6a358db) + faithful binding

- 3.4 e223: record verified 8.6s -> deferred 1.1s | P0 core verified 10.2s top=3_2_3_r16 | final30 deferred 1.3s top=3_3_r32

**class 3 g46** — deterministic, 1 entries — final timeout top=- — [no defect named in the text] [not determined]
> `10-p5-attribution.mechanisms-class2-3.md`: 3.5 e83 `(d+ex)^3 log(d(a+bx+cx^2)^n)`. No fire captured at 30 s or 120 s; P0 answered with 1_2_1_6_r1 → 3_5_r34 in 2.2 s. Either the top-level dispatch does not return (some rule's match / cond / repl ahead of 3_5_r34 runs unbounded), or its fires stay in the unflushed pipe … — follows from: not determined from the traces

- 3.5 e83: record verified 2.4s -> timeout 30.1s | P0 core verified 2.2s top=3_5_r34 | final30 timeout 30.1s top=- | final120 timeout 120.2s top=-

**class 3 g47** — deterministic, 1 entries — final timeout top=3_5_r42 — [no defect named in the text] [not determined]
> `10-p5-attribution.mechanisms-class2-3.md`: 3.5 e253 `1/(ax + bx log(cx^n)^4)`. Both cores put 3_5_r42 at top (FunctionOfLog). **Nested partial-fraction chains differ:** P0 1_1_2_1_r11, 1_2_1_1_r11, 1_2_1_2_r3/r9, 1_2_2_1_r7; substrate 1_2_1_1_r12, 1_2_1_2_r3/r9, 1_1_1_1_r3/r5, 1_1_3_1_r14. **Timing.** The top-level fire … — follows from: not determined from the traces (which change moves the class-1 chain); the cost is verification

- 3.5 e253: record verified 2.0s -> timeout 30.0s | P0 core verified 2.4s top=3_5_r42 | final30 timeout 30.0s top=3_5_r42 | final120 timeout 120.2s top=3_5_r42

**class 3 g48** — deterministic, 1 entries — final unverified top=3_1_5_r41 — [no defect named in the text] [OPT]
> `10-p5-attribution.mechanisms-class2-3.md`: e29 `(a+b log) log(d(1/d+fx^2))`. P0 answered at top with 3_5_r44 (after 3_1_1_r1 / 1_4_1_r7). The substrate binds 3_1_5_r41 (3.1.5, ahead of 3.5; P0 literal `log(d*(e+f*x^m)^r)*(a+b*log(c*x^n))^p` needs an explicit r). `u = Int[log(…)]` runs 3_4_r2 (+ 1_1_2_1_r15, 1_1_2_2_r23 … — follows from: faithful Optional binding

- 3.1.5 e29: record verified 11.0s -> unverified 1.3s | P0 core verified 9.6s top=3_5_r44 | final30 unverified 0.9s top=3_1_5_r41

**class 3 g49** — deterministic, 1 entries — final unverified top=3_2_1_r1 — [no defect named in the text] [POLY]
> `10-p5-attribution.mechanisms-class2-3.md`: e95 `log(c(b+ax)/x)^3`. P0 top was 3_2_1_r2 (20.9 s, long chain). On the substrate 3_2_1_r1 (`(A.+B.*Log[e.*((a.+b.*x)/(c.+d.*x))^n.])^p.` with the A=0, B=1, n=1 defaults; ahead of r2) binds, then 3_1_5_r45, 3_1_3_r6, 3_2_1_r17 (POLY). All arms unverified. — follows from: faithful Optional binding

- 3.2.3 e95: record verified 20.9s -> unverified 2.2s | P0 core verified 16.8s top=3_2_1_r2 | final30 unverified 1.9s top=3_2_1_r1

**class 3 g50** — deterministic, 1 entries — final unverified top=3_2_1_r17 — [no defect named in the text] [POLY]
> `10-p5-attribution.mechanisms-class2-3.md`: e104. P0 top was 3_2_1_r18 (via 3_3_r51, 3_1_3_r6). On the substrate 3_2_1_r17 (`Log[e((a+bx)/(c+dx))^n]` form, ahead of r18; both have no P0 defmatch record) binds, then 3_1_5_r45 and 3_1_3_r6 (POLY). All arms unverified. — follows from: faithful binding

- 3.2.3 e104: record verified 3.0s -> unverified 2.9s | P0 core verified 2.7s top=3_2_1_r18 | final30 unverified 2.4s top=3_2_1_r17

**class 3 g51** — deterministic, 1 entries — final unverified top=3_3_r37 — [no defect named in the text] [POLY]
> `10-p5-attribution.mechanisms-class2-3.md`: e362. Both cores put 3_3_r37 at top. The nested `Int[log(f x^m)^2/(d+ex)]` runs 3_3_r3, 1_1_1_1_r1, 3_1_3_r6 on P0 and 3_1_5_r45, 3_1_3_r6 on the substrate (P0 literal for 3_1_5_r45 `log(d*(e+f*x^m))*(a+b*log(c*x^n))^p/x`) (POLY). All arms unverified. — follows from: faithful Optional binding

- 3.3 e362: record verified 5.3s -> unverified 2.2s | P0 core verified 4.7s top=3_3_r37 | final30 unverified 2.0s top=3_3_r37

**class 3 g52** — deterministic, 1 entries — final unverified top=3_3_r47 — [no defect named in the text] [POLY]
> `10-p5-attribution.mechanisms-class2-3.md`: e382. Both cores put 3_3_r47 at top. The nested integral falls through on P0 (nfires=1). On the substrate it runs 3_3_r46, 3_1_5_r46, 3_1_3_r6, 3_1_5_r45 (POLY). All arms unverified. — follows from: faithful Optional binding

- 3.3 e382: record verified 4.2s -> unverified 6.1s | P0 core verified 4.0s top=3_3_r47 | final30 unverified 4.4s top=3_3_r47

**class 3 g53** — deterministic, 1 entries — final unverified top=3_3_r60 — [no defect named in the text] [not determined]
> `10-p5-attribution.mechanisms-class2-3.md`: e433. Both cores run 3_3_r60 → 3_3_r9 → 3_3_r6. P0 adds 3_4_r1 (the `polylog(2,1-u)` step) and reads expected; the substrate lacks it and the sub-integral falls through, as in g25. All arms unverified. — follows from: not determined from the traces

- 3.3 e433: record expected 7.1s -> unverified 4.1s | P0 core expected 7.1s top=3_3_r60 | final30 unverified 4.3s top=3_3_r60

**class 3 g54** — deterministic, 1 entries — final unverified top=3_3_r9 — [no defect named in the text] [not determined]
> `10-p5-attribution.mechanisms-class2-3.md`: e49. Both cores run 3_3_r9 → 3_3_r6. P0 adds 3_4_r1 and reads expected; the substrate lacks it, as in g25. All arms unverified. — follows from: not determined from the traces

- 3.3 e49: record expected 3.3s -> unverified 1.8s | P0 core expected 3.0s top=3_3_r9 | final30 unverified 1.7s top=3_3_r9

**class 3 g55** — slow-correct, 1 entries — final class/top per entry (see samples) — [no defect named in the text] [not determined]
> `10-p5-attribution.mechanisms-class2-3.md`: e528 `x^2 (a+b log(c(d+e/x^(2/3))^n))^3`. Walls: P0 4.4 s; final 30 s timeout with the top-level 3_4_r12 fired (nested 1_4_1_r3, 3_4_r11); final 120 s verified 65.7 s; 100 s re-check verified 57.9 s. rubi returns within the cap, so the extra time is verification of a different … — follows from: not determined from the traces (which change alters the nested chain); the cost is verification

- 3.4 e528: record verified 4.4s -> timeout 30.0s | P0 core verified 4.4s top=3_4_r12 | final30 timeout 30.0s top=3_4_r12 | final120 verified 65.7s top=3_4_r12

### Class 1

Full entry lists: `probes/matcher/10-p5-attribution.class1.summary.out`.

**class 1 g1** — deterministic, 147 entries — final deferred top=1_2_1_3_r15 — [IGtQ 144; none seen 3; collapse-family: 1.2.1.4 e810] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-a.md`: EXPAND-NOUN. **Rule.** 1_2_1_3_r15 is Rubi 1.2.1.3 (the `(f+g x)^n` file) r15, `(d.+e.x)^m.(f.+g.x)^n.(a.+b.x+c.x^2)^p. → Int[ExpandIntegrand] /; FreeQ && IGtQ[p,0]`. Its cond is `… and is(p > 0)`. **Final core.** All 147 read r15 alone (nfires=1) at 0.7–1.5 s. P0 verified in … — follows from: faithful Optional binding exposing the IGtQ translation (139); why the rewrite yields no nested fire (all 147) is not determined from the traces

- 1.2.1.3 e200: record verified 13.9s -> deferred 0.8s | P0 core verified 14.1s top=1_4_1_r34 | final30 deferred 0.8s top=1_2_1_3_r15
- 1.2.1.3 e2238: record verified 1.8s -> deferred 0.8s | P0 core verified 2.0s top=1_3_3_r6 | final30 deferred 1.0s top=1_2_1_3_r15
- 1.2.1.4 e946: record verified 5.5s -> deferred 0.6s | P0 core verified 5.2s top=1_2_1_9b_r5 | final30 deferred 0.7s top=1_2_1_3_r15

**class 1 g2** — deterministic, 99 entries — final timeout top=- — [none seen] [NOFIRE]
> `10-p5-attribution.mechanisms-class1-a.md`: NOFIRE timeout. **Fires.** No fire was flushed at 30 s (99/99) or at 120 s (97/99; two 1.1.2.4 entries show 1_1_2_4_r28 at 120 s). The 100 s re-check reads timeout 99/99. **P0.** Verified in 0.4–14.4 s. **Files.** 1.2.1.2 48, 1.1.1.3 13, 1.2.1.4 8, 1.2.1.3 6, 1.3.1 5, 1.2.1.6 4 … — follows from: condition retry (cost), 82 entries; the 17 that also time out with retry off are not determined from the traces

- 1.1.1.3 e573: record verified 1.9s -> timeout 30.0s | P0 core verified 1.9s top=1_1_1_3_r18 | final30 timeout 30.0s top=- | final120 timeout 120.1s top=-
- 1.2.1.2 e1395: record verified 2.4s -> timeout 30.0s | P0 core verified 2.2s top=1_3_4_r1 | final30 timeout 30.0s top=- | final120 timeout 120.1s top=-
- 1.3.2 e162: record verified 17.4s -> timeout 30.0s | P0 core verified 14.4s top=1_1_1_5_r8 | final30 timeout 30.0s top=- | final120 timeout 120.0s top=-

**class 1 g3** — deterministic, 80 entries — final deferred top=- — [none seen] [NOFIRE]
> `10-p5-attribution.mechanisms-class1-a.md`: NOFIRE deferred. **Result.** No rule answers at top level on the substrate (0.1–10.5 s). Deferred in all arms. P0 verified in 0.1–7.4 s. **Sub-bullets by P0 route (all 80 tabulated).** The first five subgroups (47 entries) rested on a binding Mathematica does not make, according … — follows from: G-1 (P0 degenerate bindings) for 47 entries by rule text; why Rubi's own routes do not answer (all 80) is not determined from the traces

- 1.1.2.2 e6: record verified 3.0s -> deferred 0.4s | P0 core verified 2.8s top=1_1_2_2_r4 | final30 deferred 0.4s top=-
- 1.1.4.2 e413: record verified 0.5s -> deferred 0.1s | P0 core verified 0.5s top=1_1_4_1_r9 | final30 deferred 0.1s top=-
- 1.3.2 e836: record verified 0.4s -> deferred 0.1s | P0 core verified 0.6s top=1_4_1_r50 | final30 deferred 0.1s top=-

**class 1 g4** — deterministic, 62 entries — final deferred top=1_2_1_2_r58 — [IGtQ 62] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-a.md`: EXPAND-NOUN. **Integrands.** All in 1.2.1.2: `(b*d+2*c*d*x)^m*(a+b*x+c*x^2)^p` and `(c*e+d*e*x)^m*(…)^p`, with p = 1/2, 3/2, 5/2, 4/3. **Rule.** Rubi 1.2.1.2 r58 is ExpandIntegrand `/; EqQ[2cd-be,0] && IGtQ[p,0] && Not[EqQ[m,3] && NeQ[p,1]]`; its cond is `is(p > 0)` (IGT). … — follows from: the substrate binding reaches r58 (P0 no fire) and exposes the IGtQ translation; the EXPAND-NOUN step is not determined from the traces

- 1.2.1.2 e1197: record verified 1.2s -> deferred 0.4s | P0 core verified 1.6s top=1_3_4_r1 | final30 deferred 0.5s top=1_2_1_2_r58
- 1.2.1.2 e1343: record verified 2.3s -> deferred 0.6s | P0 core verified 2.3s top=1_3_4_r1 | final30 deferred 0.5s top=1_2_1_2_r58
- 1.2.1.2 e1431: record verified 1.7s -> deferred 0.3s | P0 core verified 1.8s top=1_3_4_r1 | final30 deferred 0.4s top=1_2_1_2_r58

**class 1 g5** — deterministic, 61 entries — final deferred top=1_2_1_9b_r5 — [IGtQ 60; none seen 1] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-a.md`: EXPAND-NOUN on the same top rule as P0. **Rule.** Rubi 1.2.1.9 r5 is `(d.+e.x)^m. Pq (a.+b.x+c.x^2)^p. → ExpandIntegrand /; PolyQ[Pq,x] && IGtQ[p,-2]`; its cond is `is(p > -2)`. **P0** (5.3–19.5 s). r5 at top with nested 1_4_1_r7 (46 entries nfires=2), then verified. … — follows from: condition retry (48 of 61); the EXPAND-NOUN step is not determined from the traces

- 1.2.1.9 e192: record verified 8.4s -> deferred 3.2s | P0 core verified 8.2s top=1_2_1_9b_r5 | final30 deferred 2.6s top=1_2_1_9b_r5
- 1.2.1.9 e264: record verified 6.2s -> deferred 2.5s | P0 core verified 6.3s top=1_2_1_9b_r5 | final30 deferred 2.7s top=1_2_1_9b_r5
- 1.2.1.9 e370: record verified 11.1s -> deferred 3.0s | P0 core verified 11.8s top=1_2_1_9b_r5 | final30 deferred 3.2s top=1_2_1_9b_r5

**class 1 g6** — deterministic, 47 entries — final timeout top=1_1_3_2_r13 — [IGtQ 47; negQ 32 (both 32)] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-a.md`: VERIFY-TIMEOUT after an ILtQ-translated recurrence. **Integrands.** All in 1.1.3.2: `x^m/(a+c x^k)^j` with k = 4, 6, 8. **Top rule.** 1_1_3_2_r13 is Rubi `x^m (a+b x^n)^p /; ILtQ[Simplify[(m+1)/n+p+1],0] && NeQ[m,-1]`. Its cond is `is(%mr_simp(…) < 0)`. A script over all 47 … — follows from: not determined from the traces which change reaches r13 (P0's literal `x^m*(a+ b*x^n)^p` gave no r13 fire); its acceptance is the ILtQ translation; the cost is verification (error kinds not recorded)

- 1.1.3.2 e648: record verified 0.4s -> timeout 30.1s | P0 core verified 0.4s top=1_2_2_2_r8 | final30 timeout 30.1s top=1_1_3_2_r13 | final120 timeout 120.1s top=1_1_3_2_r13
- 1.1.3.2 e761: record verified 1.1s -> timeout 30.0s | P0 core verified 1.1s top=1_4_1_r34 | final30 timeout 30.0s top=1_1_3_2_r13 | final120 timeout 120.2s top=1_1_3_2_r13
- 1.1.3.2 e1506: record verified 1.1s -> error 17.6s | P0 core verified 1.2s top=1_3_4_r1 | final30 timeout 30.1s top=1_1_3_2_r13

**class 1 g7** — deterministic, 45 entries — final timeout top=1_2_2_3_r27 — [negQ 42; not determined 1; none seen 2] [MID-CHAIN]
> `10-p5-attribution.mechanisms-class1-a.md`: MID-CHAIN. **Fire lists.** All 45 lists (nfires=9) are identical at 30 s and at 120 s: 1_4_1_r18 (40) or 1_1_2_1_r13 (5), then 1_2_1_1_r12, 1_2_1_2_r3, 1_2_1_2_r9, 1_2_2_3_r27. **Nesting.** r27's LHS `(d+e x^2)/(a+b x^2+c x^4)` is not the integrand's form … — follows from: not determined from the traces (which change moves the route onto r27, and where the time goes after it)

- 1.2.1.2 e361: record verified 0.6s -> timeout 30.1s | P0 core verified 0.6s top=1_4_1_r25 | final30 timeout 30.1s top=1_2_2_3_r27 | final120 timeout 120.2s top=1_2_2_3_r27
- 1.2.1.3 e1231: record verified 0.6s -> timeout 30.1s | P0 core verified 0.6s top=1_4_1_r25 | final30 timeout 30.1s top=1_2_2_3_r27 | final120 timeout 120.2s top=1_2_2_3_r27
- 1.2.2.4 e377: record verified 2.2s -> timeout 30.1s | P0 core verified 3.0s top=1_2_2_4_r9 | final30 timeout 30.1s top=1_2_2_3_r27 | final120 timeout 120.2s top=1_2_2_3_r27

**class 1 g8** — deterministic, 44 entries — final timeout top=1_1_3_1_r14 — [IGtQ 10; negQ 7 (both 6); not determined 32; none seen 1] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-a.md`: **Rule.** 1_1_3_1_r14 is Rubi `1/(a+b x^n) /; IGtQ[(n-3)/2,0] && NegQ[a/b]` (PosQ twin r13). Its cond is `is((n - 3)/2 > 0) and %mr_negQ(a/b)`. **Fire lists.** 42 of 44 read 1_2_1_1_r12, 1_2_1_2_r3, 1_2_1_2_r9, 1_1_1_1_r3 (+ r5 or 1_1_2_1_r13), then r14. These are the Module's … — follows from: not determined from the traces which change reaches r14 (P0 no fire); on the top-level entries its acceptance is IGT/NEGQ; the cost is verification (34) or a non-returning chain (10)

- 1.1.1.2 e1729: record verified 0.7s -> timeout 30.1s | P0 core verified 0.8s top=1_1_1_2_r32 | final30 timeout 30.1s top=1_1_3_1_r14 | final120 timeout 120.2s top=1_1_3_1_r14
- 1.2.2.2 e720: record verified 5.2s -> timeout 30.0s | P0 core verified 5.3s top=1_3_4_r9 | final30 timeout 30.0s top=1_1_3_1_r14 | final120 timeout 120.1s top=1_2_2_2_r35
- 1.3.1 e397: record verified 1.1s -> timeout 30.0s | P0 core verified 1.4s top=1_2_2_1_r7 | final30 timeout 30.0s top=1_1_3_1_r14 | final120 timeout 120.1s top=1_1_3_1_r14

**class 1 g9** — deterministic, 43 entries — final deferred top=1_1_2_2_r5 — [IGtQ 43] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-a.md`: EXPAND-NOUN. **Rule.** Rubi 1.1.2.2 r5 is `(c.x)^m.(a+b.x^2)^p. → ExpandIntegrand /; IGtQ[p,0]`; its cond is `is(p > 0)`. **Integrands.** All in 1.1.2.2, with p = 1/2, 3/2, 1/3, 4/3, 1/4, 3/4, 1/6 (IGT). **Final core.** r5 alone at 0.1–0.4 s. **P0.** 1_3_4_r1 27, 1_1_2_2_r6 10 … — follows from: the substrate binding reaches r5 (P0 no fire) and exposes the IGtQ translation; the EXPAND-NOUN step is not determined from the traces

- 1.1.2.2 e589: record verified 2.6s -> deferred 0.1s | P0 core verified 2.6s top=1_3_4_r1 | final30 deferred 0.2s top=1_1_2_2_r5
- 1.1.2.2 e700: record verified 2.5s -> deferred 0.1s | P0 core verified 2.6s top=1_1_2_11_r4 | final30 deferred 0.4s top=1_1_2_2_r5
- 1.1.2.2 e1017: record verified 1.7s -> deferred 0.1s | P0 core verified 1.7s top=1_1_2_2_r6 | final30 deferred 0.2s top=1_1_2_2_r5

**class 1 g10** — deterministic, 41 entries — final deferred top=1_1_2_8_r7 — [IGtQ 41] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-a.md`: EXPAND-NOUN. **Rule.** Rubi 1.1.2.8 r7 is `(e.x)^m.(c+d.x)^n.(a+b.x^2)^p. → ExpandIntegrand /; IGtQ[p,0]`; its cond is `is(p > 0)`. **Integrands.** 1.2.1.4 (29) and 1.2.1.3 (12), e.g. `sqrt(d^2-e^2*x^2)/(x^2*(d+e*x))`, with p = 1/2 … 5/2. The 1.1.2.8 rules are ahead of 1.2.1.x … — follows from: the substrate binding reaches r7 (P0 no fire) and exposes the IGtQ translation; the EXPAND-NOUN step is not determined from the traces

- 1.2.1.3 e433: record verified 6.3s -> deferred 0.3s | P0 core verified 6.1s top=1_1_2_8_r37 | final30 deferred 0.3s top=1_1_2_8_r7
- 1.2.1.4 e113: record verified 0.1s -> deferred 0.6s | P0 core verified 0.1s top=1_1_2_8_r51 | final30 deferred 0.4s top=1_1_2_8_r7
- 1.2.1.4 e325: record verified 1.1s -> deferred 0.7s | P0 core verified 1.0s top=1_1_2_8_r106 | final30 deferred 0.3s top=1_1_2_8_r7

**class 1 g11** — deterministic, 37 entries — final deferred top=1_1_1_2_r12 — [IGtQ 37] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-a.md`: EXPAND-NOUN. **Rule.** Rubi 1.1.1.2 r12 is `(a.+b.x)^m.(c.+d.x)^n. → ExpandIntegrand /; IGtQ[m,0] && (…)`; its cond is `is(m > 0)`. **Integrands.** 1.1.1.2 (35) and 1.1.1.3 (2). Every positive exponent is non-integer, e.g. `(a-%i*a*x)^(7/4)/(a+%i*a*x)^(1/4)` and … — follows from: the substrate binding reaches r12 (P0 no fire) and exposes the IGtQ translation; e1888 condition retry; the EXPAND-NOUN step is not determined from the traces

- 1.1.1.2 e1171: record verified 1.0s -> deferred 0.2s | P0 core verified 0.9s top=1_1_1_2_r18 | final30 deferred 0.1s top=1_1_1_2_r12
- 1.1.1.2 e1650: record verified 4.2s -> deferred 0.2s | P0 core verified 4.1s top=1_1_1_2_r19 | final30 deferred 0.1s top=1_1_1_2_r12
- 1.1.1.3 e2998: record verified 0.1s -> deferred 0.1s | P0 core verified 0.1s top=1_1_1_2_r19 | final30 deferred 0.1s top=1_1_1_2_r12

**class 1 g12** — deterministic, 32 entries — final deferred top=1_1_2_4_r21 — [IGtQ 32] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-a.md`: EXPAND-NOUN. **Rule.** Rubi 1.1.2.4 r21 is `(e.x)^m.(a+b.x^2)^p.(c+d.x^2)^q. → ExpandIntegrand /; IGtQ[p,0] && IGtQ[q,0]`; its cond is `is(p > 0) and is(q > 0)`. **Integrands.** Every entry has p or q equal to 1/2 or 3/2, e.g. `(e*x)^(3/2)*(A+B*x^2)*sqrt(a+b*x^2)` (IGT). **Final …** — follows from: the substrate binding reaches r21 (P0 no fire) and exposes the IGtQ translation; the EXPAND-NOUN step is not determined from the traces

- 1.1.2.4 e785: record verified 2.2s -> deferred 0.2s | P0 core verified 2.2s top=1_1_2_4_r29 | final30 deferred 0.2s top=1_1_2_4_r21
- 1.1.2.4 e823: record verified 2.7s -> deferred 0.4s | P0 core verified 2.7s top=1_3_4_r3 | final30 deferred 0.3s top=1_1_2_4_r21
- 1.1.2.4 e838: record verified 2.8s -> deferred 0.4s | P0 core verified 2.8s top=1_3_4_r3 | final30 deferred 0.4s top=1_1_2_4_r21

**class 1 g13** — deterministic, 29 entries — final deferred top=1_1_3_4_r13 — [IGtQ 29] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-a.md`: EXPAND-NOUN. **Rule.** Rubi 1.1.3.4 r13 is `(e.x)^m.(a+b.x^n)^p.(c+d.x^n)^q. → ExpandIntegrand /; IGtQ[p,0] && IGtQ[q,0]`; its cond is `is(p > 0) and is(q > 0)`. **Integrands.** `(e*x)^k (A+B*x^3)(a+b*x^3)^p` with p = 1/2 … 5/2 (IGT). **Final core.** r13 alone at 0.2–0.4 s. … — follows from: the substrate binding reaches r13 (P0 no fire) and exposes the IGtQ translation; the EXPAND-NOUN step is not determined from the traces

- 1.1.3.4 e500: record verified 5.1s -> deferred 0.2s | P0 core verified 5.9s top=1_1_3_8_r30 | final30 deferred 0.3s top=1_1_3_4_r13
- 1.1.3.4 e528: record verified 5.3s -> deferred 0.2s | P0 core verified 7.3s top=1_1_3_8_r30 | final30 deferred 0.3s top=1_1_3_4_r13
- 1.1.3.4 e542: record verified 6.1s -> deferred 0.3s | P0 core verified 7.3s top=1_1_3_8_r30 | final30 deferred 0.3s top=1_1_3_4_r13

**class 1 g14** — deterministic, 28 entries — final deferred top=1_1_3_2_r12 — [IGtQ 28] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-a.md`: EXPAND-NOUN. **Rule.** Rubi 1.1.3.2 r12 is `(c.x)^m.(a+b.x^n)^p. → ExpandIntegrand /; IGtQ[p,0]`; its cond is `is(p > 0)`. **Integrands.** `x^k (a±b*x^4)^p` and `(c*x)^m (a+b*x^3)^p` with p = 1/4, 3/4, 5/4, 1/3, 4/3 (IGT). **Final core.** r12 alone at 0.1–0.2 s. **P0.** … — follows from: the substrate binding reaches r12 (P0 no fire) and exposes the IGtQ translation; the EXPAND-NOUN step is not determined from the traces

- 1.1.3.2 e593: record verified 1.7s -> deferred 0.3s | P0 core verified 1.7s top=1_3_4_r1 | final30 deferred 0.1s top=1_1_3_2_r12
- 1.1.3.2 e1028: record verified 2.6s -> deferred 0.1s | P0 core verified 2.6s top=1_2_2_2_r8 | final30 deferred 0.2s top=1_1_3_2_r12
- 1.1.3.2 e1186: record verified 1.0s -> deferred 0.1s | P0 core verified 1.1s top=1_2_2_2_r8 | final30 deferred 0.2s top=1_1_3_2_r12

**class 1 g15** — deterministic, 26 entries — final deferred top=1_1_2_9_r14 — [IGtQ 26] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-a.md`: EXPAND-NOUN. **Rule.** Rubi 1.1.2.9 r14 is `(d.+e.x)^m.(f.+g.x)^n.(a+c.x^2)^p. → ExpandIntegrand /; IGtQ[p,0]`; its cond is `is(p > 0)`. **Integrands.** 1.2.1.3 (23) and 1.2.1.4 (3), e.g. `(5-x)*sqrt(2+3*x^2)/(3+2*x)^3`, with p = 1/2 … 5/2 (IGT). **Final core.** r14 alone at … — follows from: the substrate binding reaches r14 (24 entries; P0 no fire) and exposes the IGtQ translation; the EXPAND-NOUN step (all 26) is not determined from the traces

- 1.2.1.3 e1363: record verified 1.2s -> deferred 0.2s | P0 core verified 1.5s top=1_2_1_9_r22 | final30 deferred 0.2s top=1_1_2_9_r14
- 1.2.1.3 e1390: record verified 1.5s -> deferred 0.2s | P0 core verified 1.7s top=1_2_1_9_r22 | final30 deferred 0.2s top=1_1_2_9_r14
- 1.2.1.4 e630: record verified 6.3s -> deferred 0.3s | P0 core verified 6.2s top=1_1_2_9_r14 | final30 deferred 0.4s top=1_1_2_9_r14

**class 1 g16** — deterministic, 24 entries — final deferred top=1_2_1_9b_r6 — [IGtQ 24] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-a.md`: EXPAND-NOUN. **Rule.** Rubi 1.2.1.9 r6 is `(d+e.x)^m. Pq (a+c.x^2)^p. → ExpandIntegrand /; PolyQ[Pq,x] && IGtQ[p,-2]`; its cond is `is(p > -2)`. **Integrands.** 1.2.1.9 (23) and 1.3.2 e675, with p = ±1/2, 3/2 (IGT). **Final core.** r6 alone at 1.5–1.8 s. **P0.** 22 entries: the … — follows from: faithful Optional binding (P0's b=0 binding lost) with condition retry (19 of 24); the EXPAND-NOUN step is not determined from the traces

- 1.2.1.9 e84: record verified 10.6s -> deferred 2.0s | P0 core verified 10.2s top=1_2_1_9b_r5 | final30 deferred 1.6s top=1_2_1_9b_r6
- 1.2.1.9 e107: record verified 10.6s -> deferred 2.5s | P0 core verified 10.6s top=1_2_1_9b_r5 | final30 deferred 1.6s top=1_2_1_9b_r6
- 1.3.2 e675: record verified 7.4s -> deferred 1.1s | P0 core verified 8.7s top=1_2_1_9b_r5 | final30 deferred 1.5s top=1_2_1_9b_r6

**class 1 g17** — deterministic, 19 entries — final deferred top=1_1_3_2_r17 — [NE 19] [OPT]
> `10-p5-attribution.mechanisms-class1-a.md`: NEQ-BANG. **Integrands.** All in 1.1.3.2: `x^m (a+b x^n)^p` with (m, n) ∈ {(1,3), (2,4), (−2,4), (4,6), (2,8)}. So k = gcd(m+1, n) = 1 in all 19. **Rubi.** r17 is `With[{k=GCD[m+1,n]}, 1/k Subst[Int[x^((m+1)/k-1)(a+b x^(n/k))^p], x, x^k] /; k != 1] /; FreeQ[{a,b,p},x] && …` — follows from: faithful Optional binding (bare `x` as `x^m.`; P0 no fire) with the inner condition moved into cond, exposing the `!=` translation (a third pre-existing translation defect)

- 1.1.3.2 e418: record verified 1.2s -> deferred 0.1s | P0 core verified 1.2s top=1_1_3_2_r46 | final30 deferred 0.1s top=1_1_3_2_r17
- 1.1.3.2 e979: record verified 0.4s -> deferred 0.1s | P0 core verified 0.4s top=1_1_3_2_r48 | final30 deferred 0.2s top=1_1_3_2_r17
- 1.1.3.2 e1532: record verified 1.8s -> deferred 0.1s | P0 core verified 1.8s top=1_1_3_2_r51 | final30 deferred 0.2s top=1_1_3_2_r17

**class 1 g18** — deterministic, 19 entries — final timeout top=1_1_3_2_r36 — [IGtQ 19; negQ 12 (both 12)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-b.md`: RT-SUM + VERIFY-TIMEOUT. `x^m/(a+c x^n)`, n = 4/6/8. 1_1_3_2_r36 is the top-level rule on the substrate and its repl's sub-integral chain precedes it in every list. **P0:** 1_2_2_2_r1 (subst x^2), 1_2_2_2_r23, 1_4_1_r34 or 1_3_4_r1, verified 0.3–5.6 s. **Final 120 s:** timeout … — follows from: the IGtQ translation, reachable once the rule binds/returns on the substrate (P0 0 fires class-wide); no switch

- 1.1.3.2 e646: record verified 0.4s -> timeout 30.0s | P0 core verified 0.3s top=1_2_2_2_r1 | final30 timeout 30.1s top=1_1_3_2_r36 | final120 timeout 120.1s top=1_1_3_2_r36
- 1.1.3.2 e1347: record verified 1.1s -> timeout 30.0s | P0 core verified 1.1s top=1_3_4_r1 | final30 timeout 30.0s top=1_1_3_2_r36 | final120 timeout 120.1s top=1_1_3_2_r36
- 1.1.3.2 e1473: record verified 4.9s -> error 18.0s | P0 core verified 5.2s top=1_3_4_r1 | final30 timeout 30.1s top=1_1_3_2_r36

**class 1 g19** — deterministic, 18 entries — final timeout top=1_1_2_2_r6 — [IGtQ 18; negQ 6 (both 6)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-b.md`: Both cores put 1_1_2_2_r6 (`x^m (a+bx^2)^p`, Rubi `ILtQ[Simplify[(m+1)/2+p+1],0]`) at top. It accepts (m+1)/2+p+1 = -3/4, -1/4, -1/3 … on both cores (IGT, present at P0 too). **e294–e335 (12):** P0 nested 9_1_r9 / 1_2_2_5_r3 / 1_4_1_r34 (or the 1_1_2_1_r11 chain). On the … — follows from: RT-SUM (12); the model flags (6)

- 1.1.2.2 e294: record verified 1.6s -> timeout 30.1s | P0 core verified 1.4s top=1_1_2_2_r6 | final30 timeout 30.1s top=1_1_2_2_r6 | final120 timeout 120.2s top=1_1_2_2_r6
- 1.1.2.2 e331: record verified 1.6s -> timeout 30.1s | P0 core verified 1.5s top=1_1_2_2_r6 | final30 timeout 30.0s top=1_1_2_2_r6 | final120 timeout 120.1s top=1_1_2_2_r6
- 1.1.2.2 e1031: record verified 0.4s -> timeout 30.0s | P0 core verified 0.4s top=1_1_2_2_r6 | final30 timeout 30.0s top=1_1_2_2_r6 | final120 timeout 120.1s top=1_1_2_2_r6

**class 1 g20** — deterministic, 18 entries — final timeout top=1_2_2_2_r6 — [none seen; untagged NE-text rule fire in 18] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-b.md`: VERIFY-TIMEOUT on Rubi's route. **Final:** 1_2_2_2_r6 (the `EqQ[b^2-4ac,0]` perfect-square rule; P0 0 / F 18) answers `(dx)^m/(a^2+2abx^2+b^2x^4)^k` at top level. Nested: 1_1_3_2_r17, 1_1_2_2_r27, 1_1_2_2_r23/r25/r13/r7. The corpus answers carry the matching `(a+bx^2)/sqrt(…)` … — follows from: the P0 literal `(d*x)^m*(a+b*x^2+c*x^4)^p` never completing 1_2_2_2_r6 (why is not traced) versus the substrate binding it; e774/e776 the model flags

- 1.2.2.2 e750: record verified 4.7s -> timeout 30.0s | P0 core verified 5.0s top=1_3_4_r9 | final30 timeout 30.1s top=1_2_2_2_r6 | final120 timeout 120.1s top=1_2_2_2_r6
- 1.2.2.2 e768: record verified 4.4s -> timeout 30.0s | P0 core verified 4.7s top=1_3_4_r9 | final30 timeout 30.1s top=1_2_2_2_r6 | final120 timeout 120.1s top=1_2_2_2_r6
- 1.2.2.2 e784: record verified 4.7s -> timeout 30.0s | P0 core verified 4.7s top=1_3_4_r9 | final30 timeout 30.0s top=1_2_2_2_r6 | final120 timeout 120.2s top=1_2_2_2_r6

**class 1 g21** — deterministic, 17 entries — final deferred top=1_1_1_3_r55 — [IGtQ 17] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-b.md`: EXPAND-NOUN + IGT. **Rule and binding:** 1_1_1_3_r55 (`(a.+bx)^m (c.+dx)^n (e.+fx)^p` → ExpandIntegrand; Rubi `IGtQ[m,0] || ILtQ[m,0] && ILtQ[n,0]`, cond `is(m > 0) or is(m < 0) and is(n < 0)`) accepts m = 5/2, 3/2, 1/2, 1/3 or m = n = -1/2. It answers alone with a top-level … — follows from: condition retry exposing the IGtQ/ILtQ translation of r55 (a retried binding accepts; r3 restores an answer for 9); for the other 8 the moving change is not determined

- 1.1.1.3 e938: record verified 3.7s -> deferred 0.4s | P0 core verified 3.8s top=1_1_1_6_r7 | final30 deferred 0.4s top=1_1_1_3_r55
- 1.1.1.3 e2626: record verified 0.9s -> deferred 1.7s | P0 core verified 0.8s top=1_1_1_4_r29 | final30 deferred 1.4s top=1_1_1_3_r55
- 1.1.1.3 e3165: record verified 0.3s -> deferred 0.3s | P0 core verified 0.3s top=1_1_1_4_r38 | final30 deferred 0.3s top=1_1_1_3_r55

**class 1 g22** — deterministic, 17 entries — final timeout top=1_2_2_2_r8 — [none seen] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-b.md`: Both cores run 1_2_2_2_r8 (subst x^2). **Nested chain.** P0: 1_2_1_6_r1 (`Pq (a+bx+cx^2)^p` expansion, P0 83 / F 1) or nothing. Substrate: 1_2_1_2_r9/r13/r97/r80 → 1_2_1_1_r12 → 1_1_2_1_r13 (atanh), Rubi's route (corpus atanh((b+2cx^2)/sqrt(b^2-4ac))). 1.2.1.2 is ahead of … — follows from: faithful Optional binding (Rubi's route); the cost and the deaths are not attributed to a switch

- 1.2.2.2 e850: record verified 0.9s -> error 28.5s | P0 core verified 1.2s top=1_2_2_2_r8 | final30 timeout 30.1s top=1_2_2_2_r8
- 1.2.2.2 e879: record verified 2.4s -> timeout 30.0s | P0 core verified 2.3s top=1_2_2_2_r8 | final30 timeout 30.1s top=1_2_2_2_r8 | final120 timeout 120.1s top=1_2_2_2_r8
- 1.2.3.2 e658: record verified 0.7s -> error 18.3s | P0 core verified 1.0s top=1_4_2_r24 | final30 timeout 30.1s top=1_2_2_2_r8

**class 1 g23** — deterministic, 16 entries — final deferred top=1_2_2_3_r11 — [IGtQ 16] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-b.md`: EXPAND-NOUN + IGT. 1_2_2_3_r11 (Rubi `IGtQ[p,0] && IGtQ[q,-2]`, cond `is(p > 0) and is(q > -2)`) accepts p = 1/2, 3/2 on `(d+ex^2)^q sqrt(a+bx^2+cx^4)` and answers alone with a top-level noun. It has P0 0 fires class-wide; the P0 literal `(d+e*x^2)^q*(…)^p` has no `q_.` default … — follows from: faithful Optional binding exposing the IGtQ translation

- 1.2.2.3 e227: record verified 0.7s -> deferred 0.2s | P0 core verified 1.0s top=1_2_2_3_r34 | final30 deferred 0.2s top=1_2_2_3_r11
- 1.2.2.3 e351: record verified 0.7s -> deferred 0.2s | P0 core verified 1.0s top=1_2_2_3_r34 | final30 deferred 0.2s top=1_2_2_3_r11
- 1.2.2.4 e328: record verified 2.2s -> deferred 0.4s | P0 core verified 3.0s top=1_2_2_3_r66 | final30 deferred 0.4s top=1_2_2_3_r11

**class 1 g24** — deterministic, 15 entries — final deferred top=1_2_2_4_r19 — [IGtQ 15] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-b.md`: The g23 shape with `(f x)^m`: 1_2_2_4_r19 (IGtQ[p,0] && IGtQ[q,-2]; P0 0) accepts p = 1/2, 3/2 and answers alone with a noun. P0 routes: 1_2_2_4_r31 (e154–e168) and 1_2_2_6_r3 (e204–e226). All arms deferred. — follows from: faithful Optional binding exposing the IGtQ translation

- 1.2.2.4 e154: record verified 4.9s -> deferred 0.4s | P0 core verified 4.9s top=1_2_2_4_r31 | final30 deferred 0.4s top=1_2_2_4_r19
- 1.2.2.4 e206: record verified 15.5s -> deferred 0.3s | P0 core verified 18.1s top=1_2_2_6_r3 | final30 deferred 0.4s top=1_2_2_4_r19
- 1.2.2.4 e226: record verified 5.1s -> deferred 0.3s | P0 core verified 5.3s top=1_2_2_6_r3 | final30 deferred 0.4s top=1_2_2_4_r19

**class 1 g25** — deterministic, 15 entries — final timeout top=1_1_1_2_r11 — [IGtQ 15; untagged NE-text rule fire in 9] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-b.md`: 1_1_1_2_r11 (Rubi `ILtQ[m,-1]`, cond `is(m < -1)`). **1.1.1.2, 11 entries** `1/((a+bx)^(k/3|k/4)(c+dx)^(j/3|j/4))`: r11 accepts m = -4/3 … -11/4 (IGT) as the top-level rule, after 1_1_3_2_r17 (most entries), 1_2_1_1_r17 and 1_1_1_2_r31. VERIFY-TIMEOUT: the top fire is in the 30 … — follows from: the ILtQ translation (1.1.1.2) and RT-SUM (1.1.3.2). The model flags (r4, 5 entries) and condition retry (r3, 6 entries) each restore a subset; the change that moves the route for the 4 entries no …

- 1.1.1.2 e1598: record verified 0.2s -> timeout 30.1s | P0 core verified 0.2s top=1_1_1_2_r39 | final30 timeout 30.1s top=1_1_1_2_r11 | final120 timeout 120.2s top=1_1_1_2_r11
- 1.1.1.2 e1715: record verified 0.2s -> timeout 30.1s | P0 core verified 0.2s top=1_1_1_2_r39 | final30 timeout 30.1s top=1_1_1_2_r11 | final120 timeout 120.2s top=1_1_1_2_r11
- 1.1.3.2 e1239: record verified 0.4s -> timeout 30.1s | P0 core verified 0.4s top=1_2_2_2_r8 | final30 timeout 30.1s top=1_1_1_2_r11 | final120 timeout 120.2s top=1_1_1_2_r11

**class 1 g26** — deterministic, 15 entries — final timeout top=1_1_3_1_r52 — [IGtQ 15] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-b.md`: MID-CHAIN + RT-SUM. **Fires:** 1_1_3_1_r52 (`(a+bx^n)^p` subst) is nested in every entry: the top-level forms are 1.1.1.2/1.1.1.3/1.1.2.x/1.1.3.2 binomials. No top-level fire at 30 s or 120 s (120 s: timeout 14, error e1826 96.9 s). **Chain:** r52's sub-integral `1/(1-b x^4)` … — follows from: RT-SUM in the nested chain; why the top level does not return by 120 s is not determined

- 1.1.1.2 e1179: record verified 1.1s -> timeout 30.1s | P0 core verified 1.1s top=1_1_1_2_r32 | final30 timeout 30.1s top=1_1_3_1_r52 | final120 timeout 120.2s top=1_1_3_1_r52
- 1.1.1.3 e896: record verified 3.0s -> timeout 30.1s | P0 core verified 3.2s top=1_1_1_6_r7 | final30 timeout 30.0s top=1_1_3_1_r52 | final120 timeout 120.3s top=1_1_3_1_r52
- 1.1.3.2 e1095: record verified 0.8s -> timeout 30.0s | P0 core verified 0.7s top=1_2_2_1_r18 | final30 timeout 30.1s top=1_1_3_1_r52 | final120 timeout 120.1s top=1_1_3_1_r52

**class 1 g27** — deterministic, 15 entries — final unverified top=1_2_1_2_r119 — [IGtQ 2; none seen 13] [not determined]
> `10-p5-attribution.mechanisms-class1-b.md`: The substrate answers `(ade+(cd^2+ae^2)x+cdex^2)^p/(d+ex)^m` with 1_2_1_2_r119. 1.2.1.2 is ahead of 1.3.3. **Condition.** Rubi's r119 needs `NeQ[c d^2-b d e+a e^2,0]`. That expression is identically 0 here (the quadratic has d+ex as a factor), so why the cond accepted is not … — follows from: not determined from the traces

- 1.2.1.2 e1916: record verified 1.7s -> unverified 1.3s | P0 core verified 1.7s top=1_3_3_r6 | final30 unverified 1.7s top=1_2_1_2_r119
- 1.2.1.2 e2034: record verified 1.0s -> unverified 7.2s | P0 core verified 1.1s top=1_3_3_r6 | final30 unverified 9.6s top=1_2_1_2_r119
- 1.2.1.2 e2056: record verified 1.0s -> unverified 6.8s | P0 core verified 1.2s top=1_3_3_r6 | final30 unverified 9.0s top=1_2_1_2_r119

**class 1 g28** — deterministic, 14 entries — final timeout top=1_1_3_4_r22 — [IGtQ 14; negQ 14 (both 14)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-b.md`: RT-SUM + VERIFY-TIMEOUT. **Final:** 1_1_3_4_r22 (`(ex)^m (a+bx^n)^p (c+dx^n)`, P0 0 / F 14) is the top-level rule on `x^(k/2)(A+Bx^3)/(a+bx^3)^j`. Nested: 1_1_3_2_r63/r30/r13/r71 (subst k=2 → x^6) → RT-SUM r36/r14 (+1_1_3_1_r14 chain). **P0:** 1_4_1_r34 (+1_3_4_r21 … — follows from: faithful binding of r22 (P0 literal never fired) + RT-SUM

- 1.1.3.4 e163: record verified 1.8s -> timeout 30.1s | P0 core verified 1.9s top=1_4_1_r34 | final30 timeout 30.1s top=1_1_3_4_r22 | final120 timeout 120.2s top=1_1_3_4_r22
- 1.1.3.4 e171: record verified 4.1s -> timeout 30.0s | P0 core verified 4.0s top=1_4_1_r34 | final30 timeout 30.0s top=1_1_3_4_r22 | final120 timeout 120.2s top=1_1_3_4_r22
- 1.1.3.4 e178: record verified 2.1s -> timeout 30.1s | P0 core verified 2.2s top=1_4_1_r34 | final30 timeout 30.1s top=1_1_3_4_r22 | final120 timeout 120.2s top=1_1_3_4_r22

**class 1 g29** — deterministic, 13 entries — final timeout top=1_1_3_2_r63 — [IGtQ 13; negQ 6 (both 6)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-b.md`: RT-SUM + VERIFY-TIMEOUT. **Final:** 1_1_3_2_r63 (P0 0 / F 16) reduces `x^m/(a+bx^n)` (m > n-1) as the top-level rule. The remainder goes to r36 (symbolic or 1-x^k), r35 (2+3x^4, 1+x^k) or r14 (e737). **P0:** 1_2_2_2_r8, 1_3_4_r1, 1_4_1_r34, 1_2_2_2_r22. **Final 120 s:** timeout … — follows from: the IGtQ translation (RT-SUM) with faithful binding of r63

- 1.1.3.2 e644: record verified 0.4s -> timeout 30.0s | P0 core verified 0.4s top=1_2_2_2_r8 | final30 timeout 30.1s top=1_1_3_2_r63 | final120 timeout 120.1s top=1_1_3_2_r63
- 1.1.3.2 e1342: record verified 1.2s -> timeout 30.0s | P0 core verified 1.1s top=1_3_4_r1 | final30 timeout 30.0s top=1_1_3_2_r63 | final120 unverified 73.1s top=1_1_3_2_r63
- 1.1.3.2 e1488: record verified 1.2s -> error 16.8s | P0 core verified 1.1s top=1_3_4_r1 | final30 timeout 30.1s top=1_1_3_2_r63

**class 1 g30** — deterministic, 11 entries — final deferred top=1_2_1_3_r112 — [none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-b.md`: CATCH-1. 1_2_1_3_r112 (the 1.2.1.3 `Unintegrable` catch-all; P0 0) answers at top level. It binds `(ex)^m (A+Bx)/(…)` with `d_.`=0 or `n_.`=1. **Corpus:** the answers (AppellF1 or elementary, 1–5 steps) have no Unintegrable. **P0 routes:** 1_2_1_9b_r5/r25/r32 (1.2.1.9b, later in … — follows from: faithful Optional binding (catch-all reached ahead of 1.2.1.9b); why Rubi's own route does not answer first is not determined

- 1.2.1.3 e1091: record verified 7.1s -> deferred 0.6s | P0 core verified 7.4s top=1_2_1_9b_r5 | final30 deferred 0.8s top=1_2_1_3_r112
- 1.2.1.3 e2289: record verified 4.8s -> deferred 0.9s | P0 core verified 5.5s top=1_2_1_9b_r5 | final30 deferred 0.9s top=1_2_1_3_r112
- 1.2.1.4 e955: record verified 6.1s -> deferred 0.7s | P0 core verified 6.1s top=1_2_1_9b_r32 | final30 deferred 0.8s top=1_2_1_3_r112

**class 1 g31** — deterministic, 10 entries — final deferred top=1_2_2_2_r2 — [IGtQ 10] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-b.md`: EXPAND-NOUN + IGT. 1_2_2_2_r2 (Rubi `IGtQ[p,0] && Not[IntegerQ[(m+1)/2]]`, cond `is(p > 0)`) accepts p = 1/2, 3/2 on `(dx)^m (a+bx^2+cx^4)^p` and answers alone with a noun. P0 route: 1_3_3_r15/r14 → 1_4_1_r34 → 1_3_4_r9 (or 1_4_2_r19 → 1_3_4_r9), verified 2.7–5.6 s. P0 fired r2 … — follows from: the IGtQ translation; the enabling binding change is not determined

- 1.2.2.2 e1089: record verified 4.0s -> deferred 0.3s | P0 core verified 3.8s top=1_3_4_r9 | final30 deferred 0.3s top=1_2_2_2_r2
- 1.2.2.2 e1094: record verified 5.6s -> deferred 0.3s | P0 core verified 5.3s top=1_3_4_r9 | final30 deferred 0.3s top=1_2_2_2_r2
- 1.2.2.2 e1111: record verified 2.7s -> deferred 0.2s | P0 core verified 2.7s top=1_3_4_r9 | final30 deferred 0.3s top=1_2_2_2_r2

**class 1 g32** — deterministic, 10 entries — final deferred top=1_2_2_3_r99 — [none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-b.md`: CATCH-1. 1_2_2_3_r99 (the 1.2.2.3 catch-all; P0 0) answers at top level on perfect-square quartics (b^2-4ac = 0: 1±4x^2+4x^4, 1±2x^2+x^4) with p = -1 or 5. 1_2_2_3_r11 is rightly excluded (`NeQ[b^2-4ac,0]`). The corpus answers (atan/atanh/rational/polynomial, 2–3 steps) have no … — follows from: faithful Optional binding (`q_.`, `p_.`)

- 1.2.2.3 e43: record verified 1.3s -> deferred 0.2s | P0 core verified 1.5s top=1_3_2_r13 | final30 deferred 0.2s top=1_2_2_3_r99
- 1.2.2.3 e76: record verified 1.5s -> deferred 0.2s | P0 core verified 1.9s top=1_3_3_r4 | final30 deferred 0.2s top=1_2_2_3_r99
- 1.2.2.4 e71: record verified 1.4s -> deferred 0.2s | P0 core verified 1.3s top=1_2_2_5_r1 | final30 deferred 0.2s top=1_2_2_3_r99

**class 1 g33** — deterministic, 10 entries — final deferred top=1_2_2_4_r93 — [none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-b.md`: EXPAND-NOUN. 1_2_2_4_r93 (`IGtQ[p,0] || IGtQ[q,0] || IntegersQ[m,q]`) accepts q = 1 as Rubi does on `(fx)^m (d+ex^2)/(a+bx^2+cx^4)^(k/2)` and answers alone with a noun (P0 0). P0 route: 1_2_2_6_r3 → 1_4_1_r7 / 1_1_2_3_r1, verified 5.8–8.8 s. All arms deferred. — follows from: faithful Optional binding (`q_.`); why the expansion yields no nested fire is not determined

- 1.2.2.4 e212: record verified 7.1s -> deferred 0.4s | P0 core verified 8.8s top=1_2_2_6_r3 | final30 deferred 0.4s top=1_2_2_4_r93
- 1.2.2.4 e217: record verified 7.5s -> deferred 0.4s | P0 core verified 8.4s top=1_2_2_6_r3 | final30 deferred 0.4s top=1_2_2_4_r93
- 1.2.2.4 e228: record verified 5.8s -> deferred 0.3s | P0 core verified 6.5s top=1_2_2_6_r3 | final30 deferred 0.5s top=1_2_2_4_r93

**class 1 g34** — deterministic, 10 entries — final deferred top=1_4_1_r18 — [none seen] [OPT]
> `10-p5-attribution.mechanisms-class1-b.md`: 1_4_1_r18 (`u Px^p Qx^q` → quotient rewrite; P0 4 / F 109) answers alone with a top-level noun. **Integrands:** `x^2/((a+bx) sqrt(c x^2))`, `b^2 x^m/(b+ax^2)^2`, `A (cx)^m/(a+bx^2)`, `(ac+adx+bcx^3+bdx^4)/(a+bx^3)^k`, `P(x)/(a+bx^2+cx^4)^2`. **P0 routes:** manual 9.1 … — follows from: faithful Optional binding (`u_.`, `p_.`, `q_.`) with condition retry (r3 answers 4); for the other 6 not determined

- 1.1.1.2 e879: record verified 9.9s -> deferred 0.4s | P0 core verified 10.4s top=9_1_r16 | final30 deferred 0.3s top=1_4_1_r18
- 1.1.2.8 e58: record verified 4.0s -> deferred 0.3s | P0 core verified 4.0s top=1_2_1_9b_r5 | final30 deferred 0.3s top=1_4_1_r18
- 1.2.2.5 e64: record verified 4.7s -> deferred 2.3s | P0 core verified 4.8s top=1_2_2_5_r3 | final30 deferred 2.9s top=1_4_1_r18

**class 1 g35** — deterministic, 10 entries — final timeout top=1_1_3_2_r30 — [IGtQ 10; negQ 10 (both 10)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-b.md`: RT-SUM + VERIFY-TIMEOUT. **Final:** 1_1_3_2_r30 (P0 0 / F 35; `(cx)^m (a+bx^n)^p`, p<-1) is the top-level rule on `x^k/(a+cx^4)^j`, `x^k/(a+bx^6)^2`. Nested: 1_1_3_2_r63/r71 → RT-SUM r36 or r14. **P0:** 1_2_2_2_r8 (after 1_1_2_1_r15, 1_2_1_6_r4), 1_4_1_r34, 1_3_4_r1. **Arms:** … — follows from: faithful binding of r30 + the IGtQ translation

- 1.1.3.2 e657: record verified 1.3s -> timeout 30.1s | P0 core verified 1.4s top=1_2_2_2_r8 | final30 timeout 30.1s top=1_1_3_2_r30 | final120 timeout 120.1s top=1_1_3_2_r30
- 1.1.3.2 e746: record verified 1.5s -> timeout 30.0s | P0 core verified 1.6s top=1_4_1_r34 | final30 timeout 30.1s top=1_1_3_2_r30 | final120 timeout 120.1s top=1_1_3_2_r30
- 1.1.3.2 e1330: record verified 1.3s -> timeout 30.1s | P0 core verified 1.2s top=1_3_4_r1 | final30 timeout 30.1s top=1_1_3_2_r30 | final120 timeout 120.2s top=1_1_3_2_r30

**class 1 g36** — deterministic, 10 entries — final timeout top=1_2_1_2_r109 — [IGtQ 2; none seen 8; untagged NE-text rule fire in 1] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-b.md`: Both cores reach 1_2_1_2_r109 (`(d+ex)^m Q^p`, p>0; P0 20 / F 18). **Nested integrals.** P0 went through 1_2_1_9b_r5 (class-wide P0 186 / F 81). The substrate runs 1_2_1_2_r99 → 1_2_1_1_r15 → 1_1_2_1_r13 and 1_2_1_3_r89 (e2337, e857, e924, e313, e190); the elliptic … — follows from: not determined which binding change moves the nested chain off P0's 1_2_1_9b_r5 expansion; e2442 the model flags

- 1.2.1.2 e2337: record verified 2.7s -> timeout 30.0s | P0 core verified 2.7s top=1_2_1_2_r109 | final30 timeout 30.0s top=1_2_1_2_r109 | final120 timeout 120.2s top=1_2_1_2_r109
- 1.2.1.4 e889: record verified 2.2s -> timeout 30.0s | P0 core verified 2.8s top=1_2_1_2_r109 | final30 timeout 30.0s top=1_2_1_2_r109 | final120 timeout 120.1s top=1_2_1_2_r109
- 1.2.3.2 e190: record verified 1.8s -> timeout 30.1s | P0 core verified 1.7s top=1_3_3_r15 | final30 timeout 30.1s top=1_2_1_2_r109 | final120 timeout 120.1s top=1_2_1_2_r109

**class 1 g37** — deterministic, 10 entries — final timeout top=1_2_2_2_r23 — [none seen] [MID-CHAIN]
> `10-p5-attribution.mechanisms-class1-b.md`: MID-CHAIN. **Top level.** `sqrt(d+ex)/(a+bx+cx^2)`, `sqrt(c+dx)/(a±cx^2)`: P0 finishes with the top-level subst rule 1_2_1_2_r74 or 1_1_2_7_r33, with 1_2_2_2_r23 nested (P0 13 / F 10) and nothing below it (NOUN). On the substrate the list ends in the nested r23 at 30 s and at … — follows from: faithful Optional binding in r23's sub-integrals (1_2_1_2_r9 `d_.`); why the top level does not return by 120 s is not determined

- 1.2.1.2 e364: record verified 5.2s -> timeout 30.1s | P0 core verified 5.2s top=1_2_1_2_r74 | final30 timeout 30.1s top=1_2_2_2_r23 | final120 timeout 120.1s top=1_2_2_2_r23
- 1.2.1.2 e652: record verified 1.3s -> timeout 30.1s | P0 core verified 1.2s top=1_1_2_7_r33 | final30 timeout 30.1s top=1_2_2_2_r23 | final120 timeout 120.2s top=1_2_2_2_r23
- 1.2.1.4 e529: record verified 5.3s -> timeout 30.0s | P0 core verified 5.1s top=1_2_1_2_r74 | final30 timeout 30.1s top=1_2_2_2_r23 | final120 timeout 120.2s top=1_2_2_2_r23

**class 1 g38** — deterministic, 9 entries — final deferred top=1_2_2_7_r41 — [none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-b.md`: EXPAND-NOUN. **Rule:** 1_2_2_7_r41 (P0 0 / F 9) answers `(A+Bx^2)(d+ex^2)^q/(a+cx^4)^(k/2)` alone with a noun. Rubi's conditions hold (PolyQ[Px,x^2], IntegerQ[p+1/2], IntegerQ[q]). Its repl is the 3-arg `%mr_expandIntegrand(1/sqrt(a+cx^4), …, x)`. **P0:** 9_1_r9, 1_2_2_8_r18 … — follows from: faithful Optional binding (`q_.`); why the expansion yields no nested fire is not determined

- 1.2.2.7 e1: record verified 3.2s -> deferred 1.4s | P0 core verified 3.4s top=1_2_2_5_r9 | final30 deferred 1.6s top=1_2_2_7_r41
- 1.2.2.7 e9: record verified 1.9s -> deferred 1.5s | P0 core verified 1.8s top=1_2_2_5_r8 | final30 deferred 1.5s top=1_2_2_7_r41
- 1.2.2.7 e14: record verified 7.1s -> deferred 1.0s | P0 core verified 7.9s top=1_2_2_7_r40 | final30 deferred 1.4s top=1_2_2_7_r41

**class 1 g39** — deterministic, 9 entries — final timeout top=1_1_2_2_r27 — [IGtQ 9; negQ 1 (both 1)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-b.md`: RT-SUM. **1.1.2.2 e292/e317 and 1.3.2 e814** `1/((a+bx^2)√x)`: 1_1_2_2_r27 (subst k=2; P0 4 / F 58) is the top-level rule; its `1/(a+bx^4)` runs RT-SUM r14/r13 (VERIFY-TIMEOUT). P0 used 1_1_2_7_r34, whose literal `1/(sqrt(c+d*x)*(a+b*x^2))` read √x as c=0 (DEG; Rubi `c_` is not … — follows from: G-1 (P0 degenerate binding lost) + the IGtQ translation

- 1.1.2.2 e292: record verified 1.4s -> timeout 30.0s | P0 core verified 1.4s top=1_1_2_7_r34 | final30 timeout 30.1s top=1_1_2_2_r27 | final120 timeout 120.2s top=1_1_2_2_r27
- 1.2.1.2 e1320: record verified 2.3s -> timeout 30.1s | P0 core verified 2.3s top=1_3_4_r1 | final30 timeout 30.0s top=1_1_2_2_r27 | final120 timeout 120.2s top=1_1_2_2_r27
- 1.3.2 e814: record verified 0.1s -> timeout 30.0s | P0 core verified 0.2s top=1_1_2_7_r34 | final30 timeout 30.0s top=1_1_2_2_r27 | final120 timeout 120.1s top=1_1_2_2_r27

**class 1 g40** — deterministic, 9 entries — final timeout top=1_1_3_2_r5 — [negQ 9] [OPT]
> `10-p5-attribution.mechanisms-class1-b.md`: NEGQ. **Rule:** 1_1_3_2_r5 (`x^m (a+bx^n)^p` → `x^(m+np)(b+a x^-n)^p`; Rubi `IntegerQ[p] && NegQ[n]`; P0 0 / F 10) is the only fire on `x^m/(a+bx^n)^k` with symbolic n. `%mr_negQ(n)` is true for the unknown-sign n, while Rubi's NegQ[n] is False. **Timing.** The top fire is … — follows from: faithful binding (P0 literal `x^m*(a+b*x^n)^p` never completed r5) exposing the `%mr_negQ` reading; where the cap is spent after rubi returns is not determined

- 1.1.3.2 e2477: record verified 1.5s -> timeout 30.0s | P0 core verified 1.8s top=1_1_3_2_r110 | final30 timeout 30.1s top=1_1_3_2_r5 | final120 timeout 120.1s top=1_1_3_2_r5
- 1.1.3.2 e2606: record verified 1.4s -> timeout 30.0s | P0 core verified 1.9s top=1_1_3_2_r110 | final30 timeout 30.1s top=1_1_3_2_r5 | final120 timeout 120.1s top=1_1_3_2_r5
- 1.1.3.2 e2738: record verified 3.7s -> timeout 30.0s | P0 core verified 6.1s top=1_1_3_2_r110 | final30 timeout 30.1s top=1_1_3_2_r5 | final120 timeout 120.1s top=1_1_3_2_r5

**class 1 g41** — deterministic, 8 entries — final deferred top=1_2_1_3_r20 — [none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-b.md`: EXPAND-NOUN. 1_2_1_3_r20 (`(d+ex)^m (f+gx)^n/(a+bx+cx^2)`, `IntegersQ[n]`; P0 0) accepts n = 1…4 as Rubi does and answers alone with a noun. P0: 1_2_1_3b_r68 (e1086, e1657, e2643, e2645, e933, after 1_2_1_9b_r5 / 1_4_1_r7) or 1_2_1_3_r109 (e930–e932); verified 3.0–11.2 s. All … — follows from: faithful Optional binding (`d_.`, `m_.`, `n_.`); why the expansion yields no nested fire is not determined

- 1.2.1.3 e1086: record verified 5.4s -> deferred 0.7s | P0 core verified 5.4s top=1_2_1_3b_r68 | final30 deferred 0.7s top=1_2_1_3_r20
- 1.2.1.4 e930: record verified 11.1s -> deferred 1.0s | P0 core verified 11.2s top=1_2_1_3_r109 | final30 deferred 1.2s top=1_2_1_3_r20
- 1.2.1.4 e933: record verified 4.1s -> deferred 0.6s | P0 core verified 4.2s top=1_2_1_3b_r68 | final30 deferred 0.7s top=1_2_1_3_r20

**class 1 g42** — deterministic, 8 entries — final deferred top=1_2_2_4_r96 — [none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-b.md`: CATCH-1. 1_2_2_4_r96 (the 1.2.2.4 catch-all; P0 0) answers `(fx)^m (d+ex^2)(1+2x^2+x^4)^5` at top level. The quartic is a perfect square, so 1_2_2_4_r19/r93 rightly reject on `NeQ[b^2-4ac,0]`. The corpus answers are 3-step polynomials/expansions with no Unintegrable. P0 … — follows from: faithful Optional binding (`m_.`, `q_.`)

- 1.2.2.4 e55: record verified 14.1s -> deferred 0.6s | P0 core verified 14.0s top=1_2_2_6_r3 | final30 deferred 0.4s top=1_2_2_4_r96
- 1.2.2.4 e65: record verified 6.1s -> deferred 0.4s | P0 core verified 6.0s top=1_2_2_6_r3 | final30 deferred 0.4s top=1_2_2_4_r96
- 1.2.2.4 e73: record verified 3.9s -> deferred 0.5s | P0 core verified 4.0s top=1_1_1_5_r4 | final30 deferred 0.4s top=1_2_2_4_r96

**class 1 g43** — deterministic, 8 entries — final timeout top=1_1_2_2_r23 — [IGtQ 5; negQ 2 (both 2); none seen 3] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-b.md`: **e288–e315** `x^(k/2)/(a+bx^2)`: 1_1_2_2_r23 (P0 1 / F 15) is the top-level rule, then 1_1_2_2_r27 → RT-SUM r14/r13 (VERIFY-TIMEOUT). P0: 9_1_r9, 1_2_2_5_r3, 1_4_1_r34 (+1_1_2_2_r36). All arms timeout. **e1025–e1027** `x^k/(a+bx^2)^(5/6)`: 1_1_3_1_r31, 1_1_2_1_r28/r30, top r23. … — follows from: RT-SUM (5); the model flags (e1025–e1027)

- 1.1.2.2 e288: record verified 1.6s -> timeout 30.1s | P0 core verified 1.6s top=1_1_2_2_r36 | final30 timeout 30.1s top=1_1_2_2_r23 | final120 timeout 120.2s top=1_1_2_2_r23
- 1.1.2.2 e1025: record verified 0.7s -> timeout 30.0s | P0 core verified 0.7s top=1_1_2_2_r29 | final30 timeout 30.0s top=1_1_2_2_r23 | final120 timeout 120.1s top=1_1_2_2_r23
- 1.1.3.2 e2382: record verified 0.3s -> timeout 30.0s | P0 core verified 0.3s top=1_1_3_2_r110 | final30 timeout 30.1s top=1_1_2_2_r23 | final120 timeout 120.1s top=1_1_2_2_r23

**class 1 g44** — deterministic, 7 entries — final contains-noun top=1_2_1_3_r53 — [none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-b.md`: CATCH-1 (NOUN). **Final:** 1_2_1_3_r53 / 1_2_1_3_r56 reduce `(2-5x)x^(k/2)/(2+5x+3x^2)^(j/2)` at top level. The `x^m Fx` subst 1_4_1_r34 gives `x^i P(x^2)/(2+5x^2+3x^4)^(j/2)`, and that reaches the 1.2.2.6 / 1.2.2.7 catch-alls 1_2_2_6_r9 (P0 0 / F 7) or 1_2_2_7_r42 (P0 0 / F 9) … — follows from: faithful Optional binding (catch-alls reached ahead of 1.2.2.5)

- 1.2.1.3 e1064: record verified 4.0s -> contains-noun 4.0s | P0 core verified 4.0s top=1_4_1_r34 | final30 contains-noun 4.1s top=1_2_1_3_r53
- 1.2.1.3 e1073: record verified 4.7s -> contains-noun 4.0s | P0 core verified 4.7s top=1_4_1_r34 | final30 contains-noun 4.2s top=1_2_1_3_r53
- 1.2.1.3 e1076: record verified 3.2s -> contains-noun 2.7s | P0 core verified 3.2s top=1_4_1_r34 | final30 contains-noun 2.9s top=1_2_1_3_r53

**class 1 g45** — deterministic, 7 entries — final deferred top=1_1_2_6_r3 — [none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-b.md`: EXPAND-NOUN. 1_1_2_6_r3 (P0 0) answers `(ex)^m (A+Bx^2)(c+dx^2)^k/(a+bx^2)` alone with a noun. Rubi's `IGtQ[p,-2] && IGtQ[q,0] && IGtQ[r,0]` holds (p = -1, q/r positive integers). P0: 1_2_1_9b_r5, 1_1_2_3_r1, 1_4_1_r7, or 1_1_2_6_r9/r12; verified 3.7–28.1 s. r3 reads unverified … — follows from: faithful Optional binding (`g_.`, `m_.`); condition retry shapes 4; why the expansion yields no nested fire is not determined

- 1.1.2.6 e5: record verified 9.4s -> deferred 0.6s | P0 core verified 9.2s top=1_2_1_9b_r5 | final30 deferred 0.7s top=1_1_2_6_r3
- 1.1.2.6 e22: record verified 28.1s -> deferred 1.2s | P0 core verified 27.3s top=1_1_2_6_r12 | final30 deferred 1.5s top=1_1_2_6_r3
- 1.1.2.6 e25: record verified 9.1s -> deferred 0.5s | P0 core verified 9.2s top=1_2_1_9b_r5 | final30 deferred 0.7s top=1_1_2_6_r3

**class 1 g46** — deterministic, 7 entries — final deferred top=1_1_3_2_r112 — [IGtQ 7] [OPT]
> `10-p5-attribution.mechanisms-class1-b.md`: Both cores put 1_1_3_2_r112 (subst for fractional `(c x^q)^n`) at top. **Substrate:** the substituted integral binds 1_1_3_2_r12 (ExpandIntegrand; Rubi `IGtQ[p,0]`, cond `is(p > 0)` accepts p = 1/2; P0 0 / F 35), and r112 returns a noun. **P0 nested:** 1_1_3_1_r67 / 1_4_1_r23 … — follows from: Optional binding (`c_.`, `m_.`) exposing the IGtQ translation of 1_1_3_2_r12; the model flags for e2973/e2974/e2991

- 1.1.3.2 e2967: record verified 0.7s -> deferred 0.2s | P0 core verified 0.7s top=1_4_1_r23 | final30 deferred 0.2s top=1_1_3_2_r112
- 1.1.3.2 e2973: record verified 3.2s -> deferred 0.2s | P0 core verified 3.2s top=1_1_3_2_r112 | final30 deferred 0.2s top=1_1_3_2_r112
- 1.1.3.2 e2991: record verified 1.7s -> deferred 0.3s | P0 core verified 1.7s top=1_1_3_2_r112 | final30 deferred 0.2s top=1_1_3_2_r112

**class 1 g47** — deterministic, 7 entries — final deferred top=1_1_3_7_r46 — [none seen] [DEG]
> `10-p5-attribution.mechanisms-class1-b.md`: **Final:** 1_1_3_7_r46 (`Pq (a+b v^n)^p`, subst v; P0 6 / F 7) answers `x^m/(a+bx)^(k/2)` / `(cx)^m (a+bx)^n` alone with a top-level noun. How the symbolic power x^m passes `%mr_polyPowerQ(Pq, v, n)` is not traced; class 2 g8 has the same top rule. **P0 (e710–e723):** … — follows from: G-1 (P0 degenerate binding lost) + condition retry (3 of 7)

- 1.1.1.2 e710: record expected 0.1s -> deferred 0.8s | P0 core expected 0.1s top=1_1_1_2_r39 | final30 deferred 0.4s top=1_1_3_7_r46
- 1.1.1.2 e715: record expected 0.1s -> deferred 0.9s | P0 core expected 0.1s top=1_1_1_2_r39 | final30 deferred 0.4s top=1_1_3_7_r46
- 1.1.1.2 e752: record verified 2.1s -> deferred 0.5s | P0 core verified 2.1s top=1_3_4_r1 | final30 deferred 0.5s top=1_1_3_7_r46

**class 1 g48** — deterministic, 7 entries — final timeout top=1_1_3_1_r4 — [IGtQ 7; negQ 6 (both 6)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-b.md`: 1_1_3_1_r4 (Rubi `ILtQ[Simplify[1/n+p+1],0]`; P0 0 / F 11) accepts 1/n+p+1 = -3/4, -7/4, -5/6 (IGT) on `1/(a+cx^4)^k`, `1/(a+bx^6)^2` as the top-level rule. **Chain:** its `1/(a+cx^n)` sub-integral runs RT-SUM r14 (r13 for 2+3x^4). **P0:** 1_2_2_1_r5 at top (after 1_1_2_1_r11 … — follows from: the ILtQ/IGtQ translation (r4 + RT-SUM)

- 1.1.3.2 e667: record verified 2.0s -> timeout 30.0s | P0 core verified 2.0s top=1_2_2_1_r5 | final30 timeout 30.1s top=1_1_3_1_r4 | final120 timeout 120.1s top=1_1_3_1_r4
- 1.1.3.2 e1337: record verified 0.7s -> timeout 30.0s | P0 core verified 0.7s top=1_4_1_r23 | final30 timeout 30.1s top=1_1_3_1_r4 | final120 timeout 120.2s top=1_1_3_1_r4
- 1.3.1 e411: record verified 2.2s -> timeout 30.0s | P0 core verified 2.7s top=1_2_2_1_r5 | final30 timeout 30.0s top=1_1_3_1_r4 | final120 timeout 120.1s top=1_1_3_1_r4

**class 1 g49** — deterministic, 7 entries — final timeout top=1_1_3_2_r35 — [IGtQ 7] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-b.md`: RT-SUM + VERIFY-TIMEOUT on numeric positive `x^m/(k+x^n)` (2+3x^4, 1+x^6, 1+x^8). 1_1_3_2_r35 (PosQ legitimately true, n even) is the top-level rule. **P0:** 1_2_2_2_r1 (e689), 1_3_4_r1. **Final 120 s:** timeout e689, unverified e1364 89.5 s / e1366 80.9 s, error e1491 73.3 s. … — follows from: the IGtQ translation

- 1.1.3.2 e689: record verified 0.3s -> timeout 30.0s | P0 core verified 0.3s top=1_2_2_2_r1 | final30 timeout 30.1s top=1_1_3_2_r35 | final120 timeout 120.1s top=1_1_3_2_r35
- 1.1.3.2 e1366: record verified 5.0s -> timeout 30.0s | P0 core verified 5.1s top=1_3_4_r1 | final30 timeout 30.0s top=1_1_3_2_r35 | final120 unverified 80.9s top=1_1_3_2_r35
- 1.1.3.2 e1492: record verified 5.1s -> error 18.2s | P0 core verified 5.2s top=1_3_4_r1 | final30 timeout 30.1s top=1_1_3_2_r35

**class 1 g50** — deterministic, 7 entries — final timeout top=1_2_1_2_r117 — [IGtQ 4; none seen 3] [MID-CHAIN]
> `10-p5-attribution.mechanisms-class1-b.md`: 1_2_1_2_r117 (P0 8 / F 24). **e2374, e955, e956, e968, e969** (P0 top 1_2_1_6_r1 / 1_2_2_2_r8): the substrate chain is 1_1_2_1_r13, 1_2_1_1_r15, 1_2_1_2_r15, 9_1_r8, 1_2_1_9b_r32, r117, with 1_2_1_9b_r5 in e2374, e955, e968. 1_2_1_9b_r5 is Rubi `IGtQ[p,-2]`, cond `is(p > -2)` … — follows from: the IGtQ translation of 1_2_1_9b_r5 (4); condition retry and the model flags (e2441); e2440 not determined

- 1.2.1.2 e2374: record verified 0.8s -> timeout 30.0s | P0 core verified 0.9s top=1_2_1_6_r1 | final30 timeout 30.1s top=1_2_1_2_r117 | final120 timeout 120.2s top=1_2_1_2_r117
- 1.2.2.2 e955: record verified 1.9s -> timeout 30.0s | P0 core verified 1.9s top=1_2_2_2_r8 | final30 timeout 30.0s top=1_2_1_2_r117 | final120 timeout 120.1s top=1_2_2_2_r8
- 1.2.2.2 e969: record verified 1.7s -> timeout 30.0s | P0 core verified 1.7s top=1_2_2_2_r8 | final30 timeout 30.1s top=1_2_1_2_r117 | final120 timeout 120.1s top=1_2_2_2_r8

**class 1 g51** — deterministic, 7 entries — final timeout top=1_2_1_3_r56 — [IGtQ 5; none seen 2] [OPT]
> `10-p5-attribution.mechanisms-class1-b.md`: **Final:** 1_2_1_3_r56 (P0 7 / F 23) reduces `(d+ex)^m(f+gx)/sqrt(Q)` at top level. Nested: 1_2_1_9b_r5 (p = -1/2; e952, e1573, e2466, e902, e169), 1_2_1_9b_r1 (e2209), or 1_1_2_3_r48, 1_2_1_2_r93, 9_1_r8, 1_2_1_9b_r32, 1_4_1_r18 (e2264). **P0:** 1_2_1_6_r1 at top (e952, e1573 … — follows from: faithful Optional binding (1.2.1.3 reductions ahead of P0's 1_2_1_6_r1 expansion) + the IGtQ translation of 1_2_1_9b_r5; e952 narrow Flat binding (r2 verified), e902 the model flags

- 1.2.1.3 e952: record verified 1.5s -> timeout 30.0s | P0 core verified 1.4s top=1_2_1_6_r1 | final30 timeout 30.0s top=1_2_1_3_r56 | final120 timeout 120.1s top=1_2_1_3_r56
- 1.2.1.3 e2264: record verified 3.9s -> timeout 30.0s | P0 core verified 4.3s top=1_2_1_3_r56 | final30 timeout 30.0s top=1_2_1_3_r56 | final120 unverified 45.6s top=1_2_1_3_r56
- 1.2.2.4 e169: record verified 2.7s -> timeout 30.0s | P0 core verified 2.6s top=1_2_2_6_r2 | final30 timeout 30.0s top=1_2_1_3_r56 | final120 timeout 120.0s top=1_2_2_4_r9

**class 1 g52** — deterministic, 7 entries — final timeout top=1_2_1_3_r89 — [none seen] [MID-CHAIN]
> `10-p5-attribution.mechanisms-class1-b.md`: **Final:** 1_2_1_3_r89 (split by `Not[IGtQ[m,0]]`; P0 1 / F 45) is top-level for e1577, e2469, e2500, e2265. Its sub-integrals run 1_2_1_2_r99 → 1_2_1_1_r15 → 1_1_2_1_r13, or the elliptic 1_1_2_3_r48/r42 + 1_2_1_2_r93 (e2265). **MID-CHAIN:** for e172, e333 (1.2.2.4) and e108 … — follows from: faithful Optional binding (`f_.`, `p_.` put 1.2.1.3 ahead of P0's 1.2.1.5 rules); the cost is not attributed

- 1.2.1.3 e1577: record verified 2.1s -> timeout 30.0s | P0 core verified 2.9s top=1_2_1_5_r40 | final30 timeout 30.0s top=1_2_1_3_r89 | final120 timeout 120.1s top=1_2_1_3_r89
- 1.2.1.3 e2500: record verified 4.5s -> timeout 30.0s | P0 core verified 6.2s top=1_2_1_9_r22 | final30 timeout 30.1s top=1_2_1_3_r89 | final120 timeout 120.1s top=1_2_1_3_r89
- 1.2.4.2 e108: record verified 16.0s -> timeout 30.0s | P0 core verified 19.0s top=1_4_1_r34 | final30 timeout 30.1s top=1_2_1_3_r89 | final120 timeout 120.1s top=1_2_1_3_r89

**class 1 g53** — deterministic, 7 entries — final timeout top=1_2_2_4_r9 — [none seen] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-b.md`: VERIFY-TIMEOUT. **Final:** 1_2_2_4_r9 (subst x^2; P0 7 / F 8) is the top-level rule on `x^k(A+Bx^2)/(a+bx^2+cx^4)^j`, ahead of P0's top 1_2_2_6_r2 (the Pq form, later in the table). Nested: the 1.2.1.3 reductions 1_2_1_3_r53/r44/r47/r54/r89/r55, 1_2_1_2_r97/r3/r9/r80 … — follows from: faithful Optional binding (`m_.`, `q_.`); the cost is verification of the reduction-form answer (not recorded)

- 1.2.2.4 e113: record verified 3.7s -> timeout 30.0s | P0 core verified 3.7s top=1_2_2_6_r2 | final30 timeout 30.0s top=1_2_2_4_r9 | final120 timeout 120.2s top=1_2_2_4_r9
- 1.2.2.4 e125: record verified 4.7s -> timeout 30.0s | P0 core verified 4.7s top=1_2_2_6_r2 | final30 timeout 30.0s top=1_2_2_4_r9 | final120 timeout 120.1s top=1_2_2_4_r9
- 1.2.2.4 e128: record verified 3.1s -> timeout 30.0s | P0 core verified 3.1s top=1_2_2_6_r2 | final30 timeout 30.0s top=1_2_2_4_r9 | final120 timeout 120.1s top=1_2_2_4_r9

**class 1 g54** — deterministic, 7 entries — final unverified top=1_4_1_r7 — [IGtQ 6; none seen 1] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-b.md`: Both cores split the sum with 1_4_1_r7. **Terms on the substrate:** 1_1_3_2_r107 (hypergeometric; Rubi `Not[IGtQ[p,0]] && (ILtQ[p,0] || GtQ[a,0])`, cond `… (is(p < 0) or is(a > 0))`; P0 0 / F 10) accepts p = -3/2, -1/2 in e2679, e2692 (+9_1_r12), e2690 (+1_4_1_r18) and e234 … — follows from: faithful binding exposing the ILtQ translation (4) and RT-SUM (2); e500 condition retry

- 1.1.3.2 e2679: record verified 1.7s -> unverified 1.6s | P0 core verified 2.4s top=1_4_1_r7 | final30 unverified 2.9s top=1_4_1_r7
- 1.2.1.3 e500: record verified 1.4s -> unverified 0.5s | P0 core verified 1.3s top=1_4_1_r7 | final30 unverified 0.5s top=1_4_1_r7
- 1.3.2 e234: record verified 3.9s -> unverified 0.4s | P0 core verified 4.0s top=1_4_1_r7 | final30 unverified 0.6s top=1_4_1_r7

**class 1 g55** — deterministic, 6 entries — final deferred top=1_1_1_3_r16 — [IGtQ 6] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-b.md`: EXPAND-NOUN + IGT. 1_1_1_3_r16 (Rubi `IGtQ[n,0] && LtQ[p,-1] && FractionQ[p]`, cond `is(n > 0) …`; P0 2 / F 6) accepts n = 1/2, 3/2, 5/2 on `(1-2x)^(k/2)/((2+3x)(3+5x)^(j/2))` and answers alone with a noun. P0: 1_1_1_3_r32 (5) or r25 (e2311) after 1_1_1_6_r7 etc.; verified … — follows from: faithful Optional binding (`c_.`, `n_.`) exposing the IGtQ translation

- 1.1.1.3 e2302: record verified 2.8s -> deferred 0.1s | P0 core verified 3.5s top=1_1_1_3_r32 | final30 deferred 0.2s top=1_1_1_3_r16
- 1.1.1.3 e2372: record verified 0.9s -> deferred 0.1s | P0 core verified 1.2s top=1_1_1_3_r32 | final30 deferred 0.1s top=1_1_1_3_r16
- 1.1.1.3 e2440: record verified 1.0s -> deferred 0.2s | P0 core verified 1.3s top=1_1_1_3_r32 | final30 deferred 0.2s top=1_1_1_3_r16

**class 1 g56** — deterministic, 6 entries — final deferred top=1_1_1_6_r1 — [IGtQ 6] [OPT]
> `10-p5-attribution.mechanisms-class1-b.md`: **Final:** 1_1_1_6_r1 (`Px(a+bx)^m(c+dx)^n(e+fx)^p` → `Px(ac+bdx^2)^m(e+fx)^p`; P0 0 / F 6) now binds `(A+Bx+Cx^2)/((e+fx)^k sqrt(1-dx) sqrt(1+dx))`. **Sub-integral:** binds 1_2_1_9b_r6 (ExpandIntegrand; Rubi `IGtQ[p,-2]`, cond `is(p > -2)` accepts p = -1/2; P0 0 / F 31) → noun … — follows from: faithful Optional binding exposing the IGtQ translation of 1_2_1_9b_r6

- 1.1.1.6 e5: record verified 2.9s -> deferred 6.0s | P0 core verified 2.8s top=1_1_1_6_r7 | final30 deferred 5.6s top=1_1_1_6_r1
- 1.1.1.6 e12: record verified 2.8s -> deferred 5.7s | P0 core verified 2.8s top=1_1_1_6_r7 | final30 deferred 5.7s top=1_1_1_6_r1
- 1.1.1.6 e14: record verified 6.8s -> deferred 6.7s | P0 core verified 6.7s top=1_1_1_6_r5 | final30 deferred 5.4s top=1_1_1_6_r1

**class 1 g57** — deterministic, 6 entries — final deferred top=1_1_2_8_r100 — [IGtQ 4; none seen 2] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-b.md`: EXPAND-NOUN. **Rule:** 1_1_2_8_r100 (`(ex)^m(c+dx)^n(a+bx^2)^p`; Rubi `ILtQ[p,0]`, cond `is(p < 0)`; P0 1 / F 6) answers alone with a noun. It accepts p = -1/2 or -3/2 in e332, e333, e340, e341 (IGT) and p = -1, -2 in e366, e380 (legit). **P0:** long chains ending in … — follows from: faithful Optional binding (`m_.`) exposing the ILtQ translation (4); e380 is consistent with the 9.1 regeneration; e366 not determined

- 1.2.1.4 e332: record verified 0.5s -> deferred 0.5s | P0 core verified 0.5s top=1_1_2_8_r106 | final30 deferred 0.4s top=1_1_2_8_r100
- 1.2.1.4 e341: record verified 0.9s -> deferred 0.6s | P0 core verified 1.0s top=1_1_2_8_r106 | final30 deferred 0.4s top=1_1_2_8_r100
- 1.2.1.4 e380: record verified 6.3s -> deferred 0.6s | P0 core verified 6.2s top=1_1_2_8_r100 | final30 deferred 0.4s top=1_1_2_8_r100

**class 1 g58** — deterministic, 6 entries — final deferred top=1_4_2_r20 — [none seen] [RETRY]
> `10-p5-attribution.mechanisms-class1-b.md`: 1_4_2_r20 (`u^q v^p` ExpandToSum normalizer; P0 4 / F 6) answers alone with a top-level noun. **Integrands:** `P4(x)/(a+bx^3)^(k/2)` (e68, e69), `P6(x)/sqrt(a+bx^4)` (e220), and `(d+ex^2)/(unexpanded quartic)` (e36, e362, e363). **P0:** 1_3_4_r20/r21, 1_2_2_5_r3 (after 9_1_r9 … — follows from: condition retry (3 of 6); which binding of `u`/`v` the cond accepts is not traced

- 1.1.3.8 e68: record verified 4.0s -> deferred 1.3s | P0 core verified 4.4s top=1_3_4_r21 | final30 deferred 1.0s top=1_4_2_r20
- 1.2.2.3 e36: record verified 1.8s -> deferred 0.4s | P0 core verified 2.1s top=1_2_2_3_r27 | final30 deferred 0.4s top=1_4_2_r20
- 1.3.2 e363: record verified 3.3s -> deferred 0.9s | P0 core verified 4.4s top=1_2_2_3_r27 | final30 deferred 1.2s top=1_4_2_r20

**class 1 g59** — deterministic, 6 entries — final error top=1_2_2_2_r8 — [none seen] [not determined]
> `10-p5-attribution.mechanisms-class1-b.md`: 1.2.3.2 `(d+ex)^k/(a+b(d+ex)^2+c(d+ex)^4)^j`. **P0:** top-level normalizer 1_4_2_r24, verified 0.6–1.0 s. **Substrate:** only a nested 1.2.2.2 route (1_1_2_1_r13, 1_2_1_1_r12, 1_2_1_2_r13, or 1_2_1_2_r3/r9/r80/r115, 1_2_1_3_r89, 1_2_1_1_r8, then 1_2_2_2_r8), with no top-level … — follows from: not determined from the traces

- 1.2.3.2 e622: record verified 0.7s -> error 9.0s | P0 core verified 0.9s top=1_4_2_r24 | final30 error 28.1s top=1_2_2_2_r8
- 1.2.3.2 e647: record verified 0.7s -> error 8.8s | P0 core verified 0.9s top=1_4_2_r24 | final30 error 28.6s top=1_2_2_2_r8
- 1.2.3.2 e655: record verified 0.7s -> error 8.5s | P0 core verified 1.0s top=1_4_2_r24 | final30 error 16.0s top=1_2_2_2_r8

**class 1 g60** — deterministic, 6 entries — final timeout top=1_1_1_2_r10 — [IGtQ 6] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-b.md`: MID-CHAIN. `(a±bx^4)^(k/4)/x^j`. **Substrate:** the list ends in the nested 1_1_1_2_r10 at 30 s and 120 s, after RT-SUM r14 and 1_1_1_2_r32 (/r11/r19). The top-level `x^m(a+bx^4)^p` rule has not fired. **P0:** 1_1_1_2_r12, 1_1_2_2_r4, top 1_2_2_2_r8, verified 0.4 s. **Arms:** r3 … — follows from: RT-SUM in the chain; condition retry for e1179/e1180; why the top level does not return is not determined

- 1.1.3.2 e992: record verified 0.4s -> timeout 30.1s | P0 core verified 0.4s top=1_2_2_2_r8 | final30 timeout 30.1s top=1_1_1_2_r10 | final120 timeout 120.2s top=1_1_1_2_r10
- 1.1.3.2 e1052: record verified 0.4s -> timeout 30.1s | P0 core verified 0.4s top=1_2_2_2_r8 | final30 timeout 30.1s top=1_1_1_2_r10 | final120 timeout 120.2s top=1_1_1_2_r10
- 1.1.3.2 e1180: record verified 0.4s -> timeout 30.0s | P0 core verified 0.4s top=1_2_2_2_r8 | final30 timeout 30.1s top=1_1_1_2_r10 | final120 timeout 120.2s top=1_1_1_2_r10

**class 1 g61** — deterministic, 6 entries — final timeout top=1_1_2_2_r13 — [IGtQ 6; negQ 3 (both 3)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-b.md`: RT-SUM + VERIFY-TIMEOUT. **Final:** 1_1_2_2_r13 (P0 3 / F 25) is the top-level reduction of `x^(k/2)/(a+bx^2)^j`, then 1_1_2_2_r23 → r27 → RT-SUM r14 (a+bx^2) or r13 (1+x^2). **P0:** 9_1_r9, 1_2_2_5_r3, top 1_4_1_r34, verified 1.6–1.8 s. **Timing and arms:** 120 s timeout 6; all … — follows from: the IGtQ translation

- 1.1.2.2 e296: record verified 1.6s -> timeout 30.1s | P0 core verified 1.7s top=1_4_1_r34 | final30 timeout 30.0s top=1_1_2_2_r13 | final120 timeout 120.2s top=1_1_2_2_r13
- 1.1.2.2 e321: record verified 1.6s -> timeout 30.1s | P0 core verified 1.6s top=1_4_1_r34 | final30 timeout 30.0s top=1_1_2_2_r13 | final120 timeout 120.1s top=1_1_2_2_r13
- 1.1.2.2 e329: record verified 1.7s -> timeout 30.0s | P0 core verified 1.7s top=1_4_1_r34 | final30 timeout 30.0s top=1_1_2_2_r13 | final120 timeout 120.2s top=1_1_2_2_r13

**class 1 g62** — deterministic, 6 entries — final timeout top=1_2_1_2_r105 — [none seen] [MID-CHAIN]
> `10-p5-attribution.mechanisms-class1-b.md`: 1_2_1_2_r105 (P0 0 / F 9) and r95/r99 bind `x^m Q^p` with `d_.`=0 after the x^2 (x^3) substitution. **Fire list:** 1_1_2_1_r13, 1_2_1_2_r99, (r95), r105, with no top-level fire at 30 s. **At 120 s:** the 1.2.2.2 entries e927/e945/e960/e973 still end in r105 (MID-CHAIN). For the … — follows from: faithful Optional binding (`d_.`); the cost is not further determined

- 1.2.2.2 e927: record verified 2.3s -> timeout 30.1s | P0 core verified 2.3s top=1_2_2_2_r8 | final30 timeout 30.0s top=1_2_1_2_r105 | final120 timeout 120.1s top=1_2_2_2_r8
- 1.2.2.2 e973: record verified 2.8s -> timeout 30.0s | P0 core verified 2.7s top=1_2_2_2_r8 | final30 timeout 30.1s top=1_2_1_2_r105 | final120 timeout 120.1s top=1_2_2_2_r8
- 1.2.3.2 e211: record verified 1.9s -> timeout 30.0s | P0 core verified 1.8s top=1_3_3_r15 | final30 timeout 30.1s top=1_2_1_2_r105 | final120 timeout 120.1s top=1_2_3_2_r6

**class 1 g63** — deterministic, 6 entries — final timeout top=1_2_2_2_r15 — [none seen] [not determined]
> `10-p5-attribution.mechanisms-class1-b.md`: 1.2.3.2 `1/((d+ex)^k(a+b(d+ex)^2+c(d+ex)^4)^j)`. **P0:** 1_4_2_r24, verified 0.7–1.0 s. **Substrate:** only a nested chain (1_4_1_r18, 1_2_1_1_r12, 1_2_1_2_r3/r9, 1_2_2_3_r27, 1_2_2_4_r39 (/r35), 1_2_2_2_r15); no top-level fire. **Timing:** at 120 s all 6 read error at 75.4–97.4 … — follows from: not determined from the traces (dies during integration; error kind not recorded)

- 1.2.3.2 e627: record verified 0.7s -> timeout 30.1s | P0 core verified 1.0s top=1_4_2_r24 | final30 timeout 30.1s top=1_2_2_2_r15 | final120 error 75.4s top=1_2_2_2_r15
- 1.2.3.2 e651: record verified 0.7s -> timeout 30.1s | P0 core verified 1.0s top=1_4_2_r24 | final30 timeout 30.1s top=1_2_2_2_r15 | final120 error 94.7s top=1_2_2_2_r15
- 1.2.3.2 e659: record verified 0.7s -> timeout 30.1s | P0 core verified 1.0s top=1_4_2_r24 | final30 timeout 30.1s top=1_2_2_2_r15 | final120 error 94.0s top=1_2_2_2_r15

**class 1 g64** — deterministic, 5 entries — final contains-noun top=1_2_1_3_r56 — [none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-b.md`: CATCH-1 (NOUN). **e1056–e1058** `(2-5x)x^(k/2)/sqrt(2+5x+3x^2)`: the g44 route, 1_4_1_r34 → 1_2_2_6_r9 or 1_2_2_7_r42 → marker. P0 top 1_4_1_r34, verified 3.5–4.7 s. **e1095, e1096** `x^k(A+Bx)(a+bx+cx^2)^p`: 1_2_1_3_r56 reduces, and its sub-integral reaches 1_2_1_3_r112 (the … — follows from: faithful Optional binding

- 1.2.1.3 e1056: record verified 4.7s -> contains-noun 4.1s | P0 core verified 4.7s top=1_4_1_r34 | final30 contains-noun 4.3s top=1_2_1_3_r56
- 1.2.1.3 e1058: record verified 3.5s -> contains-noun 2.7s | P0 core verified 3.5s top=1_4_1_r34 | final30 contains-noun 3.1s top=1_2_1_3_r56
- 1.2.1.3 e1096: record verified 4.5s -> contains-noun 1.2s | P0 core verified 4.4s top=1_2_1_3_r56 | final30 contains-noun 1.4s top=1_2_1_3_r56

**class 1 g65** — deterministic, 5 entries — final deferred top=1_1_2_8_r68 — [none seen] [OPT]
> `10-p5-attribution.mechanisms-class1-b.md`: 1_1_2_8_r68 (`EqQ[bc^2+ad^2,0] && ILtQ[n,0]`, n = -1 legit; P0 0 / F 5) rewrites `x^k(d^2-e^2x^2)^p/(d+ex)` and answers alone with a noun. P0: 1_1_2_8_r106 after 1_4_2_r6 / 1_1_1_2_r37 / 1_1_2_2_r4, verified 0.4–2.0 s. All arms deferred. — follows from: faithful Optional binding (`e_.`); why the rewritten integral has no nested fire is not determined

- 1.2.1.4 e267: record verified 0.9s -> deferred 0.7s | P0 core verified 0.8s top=1_1_2_8_r106 | final30 deferred 0.5s top=1_1_2_8_r68
- 1.2.1.4 e272: record verified 0.4s -> deferred 0.8s | P0 core verified 0.4s top=1_1_2_8_r106 | final30 deferred 0.4s top=1_1_2_8_r68
- 1.2.1.4 e274: record verified 0.9s -> deferred 0.6s | P0 core verified 0.8s top=1_1_2_8_r106 | final30 deferred 0.4s top=1_1_2_8_r68

**class 1 g66** — deterministic, 5 entries — final deferred top=1_2_2_3_r86 — [none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-b.md`: Both cores put 1_2_2_3_r86 at top (`ILtQ[q,0]`, q = -3 legit; 2-arg ExpandIntegrand over `1/sqrt(a+bx^2+cx^4)`). On P0 the expansion sum dispatched: 1_4_1_r7 split it, verified 8.6–12.4 s. On the substrate r86 is the only fire (nfires=1) and gives a top-level noun at 0.9–1.3 s. … — follows from: not determined from the traces

- 1.2.2.3 e230: record verified 9.0s -> deferred 1.0s | P0 core verified 12.1s top=1_2_2_3_r86 | final30 deferred 1.0s top=1_2_2_3_r86
- 1.2.2.3 e292: record verified 9.0s -> deferred 1.0s | P0 core verified 12.1s top=1_2_2_3_r86 | final30 deferred 1.3s top=1_2_2_3_r86
- 1.2.2.3 e355: record verified 8.6s -> deferred 0.9s | P0 core verified 11.9s top=1_2_2_3_r86 | final30 deferred 1.3s top=1_2_2_3_r86

**class 1 g67** — deterministic, 5 entries — final deferred top=1_2_2_3_r98 — [none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-b.md`: The g66 shape with 1_2_2_3_r98 (`(a+cx^4)^p/(d+ex^2)^q`, `ILtQ[q,0]`, q = -1…-3 legit). P0 split the expansion with 1_4_1_r7 (+1_4_2_r25), verified 3.8–10.5 s. The substrate has r98 alone → noun at 0.2 s. All arms deferred. — follows from: not determined from the traces

- 1.2.2.3 e180: record verified 3.8s -> deferred 0.2s | P0 core verified 4.8s top=1_2_2_3_r98 | final30 deferred 0.2s top=1_2_2_3_r98
- 1.2.2.3 e186: record verified 4.9s -> deferred 0.2s | P0 core verified 6.0s top=1_2_2_3_r98 | final30 deferred 0.2s top=1_2_2_3_r98
- 1.2.2.3 e188: record verified 8.2s -> deferred 0.2s | P0 core verified 10.5s top=1_2_2_3_r98 | final30 deferred 0.2s top=1_2_2_3_r98

**class 1 g68** — deterministic, 5 entries — final deferred top=1_3_4_r1 — [none seen] [DEG]
> `10-p5-attribution.mechanisms-class1-b.md`: `x^(k+m)/sqrt(a+bx)`. **P0:** expected at 0.1 s via 1_1_1_2_r38/r39 (hypergeometric) on `(a+b*x)^m*(c+d*x)^n`, reading x^(k+m) as (0+1·x)^(k+m). Rubi's `c_` is not Optional (DEG). **Substrate:** 1_3_4_r1 (P0 229 / F 5) substitutes g+hx = a+bx, giving a top-level noun at 1.1–1.9 … — follows from: G-1 (P0 degenerate binding lost); why Rubi's 2-step route is not reached is not determined

- 1.1.1.2 e713: record expected 0.1s -> deferred 1.2s | P0 core expected 0.1s top=1_1_1_2_r39 | final30 deferred 1.1s top=1_3_4_r1
- 1.1.1.2 e716: record expected 0.1s -> deferred 1.8s | P0 core expected 0.1s top=1_1_1_2_r39 | final30 deferred 1.1s top=1_3_4_r1
- 1.1.1.2 e718: record expected 0.1s -> deferred 1.9s | P0 core expected 0.1s top=1_1_1_2_r39 | final30 deferred 1.1s top=1_3_4_r1

**class 1 g69** — deterministic, 5 entries — final deferred top=1_4_2_r19 — [none seen] [not determined]
> `10-p5-attribution.mechanisms-class1-b.md`: 1_4_2_r19 (`(dx)^m u^p`, TrinomialQ[u] && Not[TrinomialMatchQ[u]]) answers alone with a noun. **Integrands:** the 1.3.1/1.3.2 quartics `a+8x-8x^2+4x^3-x^4`, `1+(x^2-1)^2`, and `a+bc^4+…+bd^4x^4`. How the full quartics pass `%mr_trinomialQ` is not traced. **P0:** 1_2_2_5_r10 … — follows from: not determined from the traces

- 1.3.1 e127: record verified 23.1s -> deferred 1.0s | P0 core verified 16.0s top=1_2_2_5_r10 | final30 deferred 1.2s top=1_4_2_r19
- 1.3.2 e631: record verified 2.5s -> deferred 0.8s | P0 core verified 3.4s top=1_2_2_5_r10 | final30 deferred 1.1s top=1_4_2_r19
- 1.3.2 e863: record verified 4.8s -> deferred 1.3s | P0 core verified 5.5s top=1_2_2_5_r10 | final30 deferred 1.6s top=1_4_2_r19

**class 1 g70** — deterministic, 5 entries — final timeout top=1_1_2_4_r20 — [none seen] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-b.md`: VERIFY-TIMEOUT. **Final:** both cores put 1_1_2_4_r20 (subst x^2) at top on `(a+bx^2)^(k/2)/(x^j sqrt(c+dx^2))`. The substrate's nested integral runs 1_1_1_3_r22 (P0 0 / F 7) with r23/r25 and 1_1_2_1_r15 (atanh). **P0:** 1_1_1_3_r61 / r55 / 1_1_1_6_r7, verified 0.2–3.6 s. … — follows from: faithful Optional binding (1_1_1_3_r22 `a_.`, `e_.`); the cost is verification

- 1.1.2.4 e938: record verified 0.3s -> timeout 30.0s | P0 core verified 0.3s top=1_1_2_4_r20 | final30 timeout 30.1s top=1_1_2_4_r20 | final120 timeout 120.2s top=1_1_2_4_r20
- 1.1.2.4 e949: record verified 0.4s -> timeout 30.1s | P0 core verified 0.4s top=1_1_2_4_r20 | final30 timeout 30.1s top=1_1_2_4_r20 | final120 timeout 120.2s top=1_1_2_4_r20
- 1.1.2.4 e973: record verified 0.2s -> timeout 30.1s | P0 core verified 0.2s top=1_1_2_4_r20 | final30 timeout 30.1s top=1_1_2_4_r20 | final120 timeout 120.2s top=1_1_2_4_r20

**class 1 g71** — deterministic, 5 entries — final timeout top=1_2_1_1_r15 — [none seen] [MID-CHAIN]
> `10-p5-attribution.mechanisms-class1-b.md`: MID-CHAIN. **1.2.1.5/1.2.1.6 e102, e111** `sqrt(Q1)/Q2`: P0 finishes with 1_2_1_4_r27, verified 1.1–1.7 s. The substrate list ends in the nested 1_2_1_1_r15 at 30 s and 120 s. **1.2.4.2 e106, e111, e113** `x^k(ax+bx^3+cx^5)^(j/2)`: P0 1_3_3_r15/r14/r10 → top 1_4_1_r34, verified … — follows from: not determined from the traces

- 1.2.1.5 e102: record verified 1.1s -> timeout 30.0s | P0 core verified 1.6s top=1_2_1_4_r27 | final30 timeout 30.0s top=1_2_1_1_r15 | final120 timeout 120.1s top=1_2_1_1_r15
- 1.2.4.2 e106: record verified 1.8s -> timeout 30.0s | P0 core verified 2.6s top=1_4_1_r34 | final30 timeout 30.1s top=1_2_1_1_r15 | final120 timeout 120.0s top=1_2_4_2_r8
- 1.2.4.2 e113: record verified 2.8s -> timeout 30.0s | P0 core verified 3.8s top=1_4_1_r34 | final30 timeout 30.0s top=1_2_1_1_r15 | final120 timeout 120.1s top=1_2_4_2_r4

**class 1 g72** — deterministic, 5 entries — final timeout top=1_2_1_2_r107 — [none seen] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-b.md`: 1_2_1_2_r107 (P0 0 / F 6). **Fire list:** 1_1_2_1_r13, 1_2_1_1_r15, then 1_2_1_2_r99 or 1_1_1_4_r46 + 1_2_1_2_r133, then 1_2_1_3_r89 (+r51), then r107. **Timing:** r107 is top-level only for e1913 (P0 top 1_3_3_r6: VERIFY-TIMEOUT). For e925/e941 (P0 top 1_2_2_2_r8) and the … — follows from: faithful Optional binding (`d_.`=0 on `x^m Q^p`); the cost is not further determined

- 1.2.1.2 e1913: record verified 1.7s -> timeout 30.0s | P0 core verified 1.7s top=1_3_3_r6 | final30 timeout 30.1s top=1_2_1_2_r107 | final120 timeout 120.1s top=1_2_1_2_r107
- 1.2.2.2 e941: record verified 2.3s -> timeout 30.0s | P0 core verified 2.3s top=1_2_2_2_r8 | final30 timeout 30.1s top=1_2_1_2_r107 | final120 timeout 120.1s top=1_2_1_2_r107
- 1.2.3.2 e207: record verified 1.9s -> timeout 30.1s | P0 core verified 1.8s top=1_3_3_r15 | final30 timeout 30.1s top=1_2_1_2_r107 | final120 timeout 120.2s top=1_2_1_2_r107

**class 1 g73** — deterministic, 5 entries — final timeout top=1_2_1_3_r53 — [IGtQ 2; none seen 3] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-b.md`: **Final:** 1_2_1_3_r53 (P0 1 / F 14) is the top-level reduction. Nested: 1_2_1_9b_r5 (p = -3/2, IGT) with 1_2_1_2_r117/r15, 9_1_r8, 1_2_1_9b_r32 (e962, e2473); 1_2_1_9b_r1 (e2223, e2224); or 1_1_2_3_r48, 1_2_1_2_r93, 9_1_r8, 1_2_1_9b_r32, 1_4_1_r18 (e2271). **P0:** 1_2_1_6_r1 … — follows from: faithful Optional binding (1.2.1.3 ahead of P0's 1_2_1_6_r1) + the IGtQ translation of 1_2_1_9b_r5; e962 narrow Flat binding (r2 verified)

- 1.2.1.3 e962: record verified 1.4s -> timeout 30.1s | P0 core verified 1.4s top=1_2_1_6_r1 | final30 timeout 30.1s top=1_2_1_3_r53 | final120 timeout 120.1s top=1_2_1_3_r53
- 1.2.1.3 e2224: record verified 2.2s -> timeout 30.0s | P0 core verified 2.4s top=1_2_1_6_r4 | final30 timeout 30.0s top=1_2_1_3_r53 | final120 timeout 120.1s top=1_2_1_3_r53
- 1.2.1.3 e2473: record verified 0.7s -> timeout 30.0s | P0 core verified 0.9s top=1_2_1_6_r1 | final30 timeout 30.1s top=1_2_1_3_r53 | final120 timeout 120.1s top=1_2_1_3_r53

**class 1 g74** — deterministic, 5 entries — final unverified top=1_1_3_8_r18 — [IGtQ 5; untagged NE-text rule fire in 3] [OPT]
> `10-p5-attribution.mechanisms-class1-b.md`: 1_1_3_8_r18 (Rubi `IGtQ[n/2,0]`, cond `is(n/2 > 0)` accepts n = 3; P0 0 / F 8) splits `P2(x)/(a±x^3)` into parts. The parts go to 1_1_3_2_r17 (e307, e311, e312) or 1_1_3_2_r107 (hypergeometric; e366, e368). P0: Rubi's `P2/(a+bx^3)` rules 1_1_3_7_r25/r26/r14 (later in the table) … — follows from: faithful Optional binding (`c_.`, `m_.`) exposing the IGtQ translation

- 1.1.3.8 e307: record verified 1.6s -> unverified 0.9s | P0 core verified 1.5s top=1_1_3_7_r25 | final30 unverified 0.9s top=1_1_3_8_r18
- 1.1.3.8 e312: record verified 1.6s -> unverified 0.9s | P0 core verified 1.6s top=1_1_3_7_r26 | final30 unverified 1.0s top=1_1_3_8_r18
- 1.1.3.8 e368: record verified 1.1s -> unverified 1.2s | P0 core verified 1.1s top=1_1_3_7_r14 | final30 unverified 1.2s top=1_1_3_8_r18

**class 1 g75** — deterministic, 4 entries — final deferred top=1_1_2_5_r1 — [IGtQ 4] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-b.md`: EXPAND-NOUN + IGT. 1_1_2_5_r1 (`IGtQ[p,0] && IGtQ[q,0] && IGtQ[r,0]`; P0 0 / F 4) accepts q, r = 1/2, 3/2 on `(a+bx^2)(c+dx^2)^(k/2)(e+fx^2)^(j/2)` and gives a noun. P0: 1_1_2_5_r8, verified 1.3 s. All arms deferred. — follows from: faithful Optional binding (`p_.`) exposing the IGtQ translation

- 1.1.2.5 e23: record verified 1.3s -> deferred 0.5s | P0 core verified 1.8s top=1_1_2_5_r8 | final30 deferred 0.3s top=1_1_2_5_r1
- 1.1.2.5 e29: record verified 1.3s -> deferred 0.4s | P0 core verified 1.8s top=1_1_2_5_r8 | final30 deferred 0.3s top=1_1_2_5_r1
- 1.1.2.5 e54: record verified 1.3s -> deferred 0.3s | P0 core verified 1.9s top=1_1_2_5_r8 | final30 deferred 0.3s top=1_1_2_5_r1

**class 1 g76** — deterministic, 4 entries — final deferred top=1_2_1_2_r89 — [IGtQ 4] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-b.md`: `sqrt(d+ex)^±1/sqrt(±2x-3x^2)`. Both cores fire 1_1_1_3_r55 (IGT: m or n = ±1/2). **Substrate:** 1_2_1_2_r89 (P0 0 / F 4; `LtQ[c,0] && RationalQ[b]` legit) then answers with a top-level noun. **P0:** 1_3_3_r17 (e428, e430) or 1_4_2_r25 / 1_4_1_r34 / 1_2_1_4_r30 (e429, e431) … — follows from: the model flags (all 4) and condition retry (2)

- 1.2.1.2 e428: record verified 1.3s -> deferred 0.6s | P0 core verified 1.4s top=1_3_3_r17 | final30 deferred 0.6s top=1_2_1_2_r89
- 1.2.1.2 e430: record verified 2.9s -> deferred 0.6s | P0 core verified 2.8s top=1_3_3_r17 | final30 deferred 0.6s top=1_2_1_2_r89
- 1.2.1.2 e431: record verified 1.2s -> deferred 0.7s | P0 core verified 1.2s top=1_3_3_r17 | final30 deferred 0.7s top=1_2_1_2_r89

**class 1 g77** — deterministic, 4 entries — final deferred top=1_2_2_4_r20 — [IGtQ 4] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-b.md`: EXPAND-NOUN + IGT. 1_2_2_4_r20 (`IGtQ[p,0] && IGtQ[q,-2]`; P0 0 / F 4) accepts p = 1/2, 3/2 on `(2+3x^2)(5+x^4)^(k/2)/x^j` and gives a noun. P0: 1_1_3_1_r32, 1_2_2_3_r53/r55, 1_2_2_4_r39, top 1_2_2_4_r31, verified 4.2–5.4 s. All arms deferred. — follows from: faithful Optional binding exposing the IGtQ translation

- 1.2.2.4 e18: record verified 4.2s -> deferred 0.4s | P0 core verified 3.9s top=1_2_2_4_r31 | final30 deferred 0.2s top=1_2_2_4_r20
- 1.2.2.4 e30: record verified 4.7s -> deferred 0.5s | P0 core verified 4.6s top=1_2_2_4_r31 | final30 deferred 0.2s top=1_2_2_4_r20
- 1.2.2.4 e31: record verified 5.4s -> deferred 0.5s | P0 core verified 5.4s top=1_2_2_4_r31 | final30 deferred 0.3s top=1_2_2_4_r20

**class 1 g78** — deterministic, 4 entries — final error top=1_2_2_2_r1 — [none seen] [not determined]
> `10-p5-attribution.mechanisms-class1-b.md`: 1.2.3.2 `(d+ex)/(a+b(d+ex)^2+c(d+ex)^4)^j`. **P0:** top-level normalizer 1_3_3_r4, verified 1.1 s. **Substrate:** only a nested route (1_1_2_1_r13, 1_2_1_1_r12, 1_2_1_1_r8, 1_2_2_2_r1); no top-level fire. **Error:** record error 7.6–14.7 s; final30 probe 14.5–27.5 s; newerror … — follows from: not determined from the traces

- 1.2.3.2 e624: record verified 1.1s -> error 14.7s | P0 core verified 1.5s top=1_3_3_r4 | final30 error 27.5s top=1_2_2_2_r1
- 1.2.3.2 e649: record verified 1.1s -> error 12.9s | P0 core verified 1.5s top=1_3_3_r4 | final30 error 23.9s top=1_2_2_2_r1
- 1.2.3.2 e657: record verified 1.1s -> error 7.6s | P0 core verified 1.5s top=1_3_3_r4 | final30 error 14.5s top=1_2_2_2_r1

**class 1 g79** — deterministic, 4 entries — final timeout top=1_1_3_2_r15 — [IGtQ 4; negQ 3 (both 3)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-b.md`: 1_1_3_2_r15 (Rubi `ILtQ[Simplify[(m+1)/n+p+1],0]`; P0 0 / F 7) accepts -1/2, -2/3 (IGT) as the top-level rule on `x/(a+cx^4)^k`, `x/(a+bx^6)^2`. **Chain:** its sub-integral runs RT-SUM r36 (r35 for 2+3x^4). VERIFY-TIMEOUT. **P0:** 1_1_2_1_r15/r10, 1_1_2_1_r3, top 1_2_2_2_r1 … — follows from: the ILtQ/IGtQ translation

- 1.1.3.2 e661: record verified 0.4s -> timeout 30.1s | P0 core verified 0.4s top=1_2_2_2_r1 | final30 timeout 30.1s top=1_1_3_2_r15 | final120 timeout 120.2s top=1_1_3_2_r15
- 1.1.3.2 e698: record verified 0.4s -> timeout 30.0s | P0 core verified 0.3s top=1_2_2_2_r1 | final30 timeout 30.1s top=1_1_3_2_r15 | final120 timeout 120.1s top=1_1_3_2_r15
- 1.1.3.2 e1336: record verified 5.5s -> timeout 30.0s | P0 core verified 5.6s top=1_3_4_r1 | final30 timeout 30.1s top=1_1_3_2_r15 | final120 timeout 120.2s top=1_1_3_2_r15

**class 1 g80** — deterministic, 4 entries — final timeout top=1_1_3_3_r46 — [IGtQ 4; negQ 4 (both 4)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-b.md`: MID-CHAIN, then verification. `1/((a+bx^2)^j(c+dx^2)^k √x)`. **Chain:** 1_1_3_5_r2 (partial fractions over x^4) → RT-SUM r14 on `1/(a+bx^4)` and `1/(c+dx^4)`. **Timing:** 1_1_3_3_r46 is nested at 30 s; by 120 s the top-level 1_1_2_4_r34 (subst k=2) has fired, and the entries … — follows from: the IGtQ translation (RT-SUM)

- 1.1.2.4 e476: record verified 2.1s -> timeout 30.1s | P0 core verified 2.0s top=1_4_1_r34 | final30 timeout 30.0s top=1_1_3_3_r46 | final120 timeout 120.1s top=1_1_2_4_r34
- 1.1.2.4 e492: record verified 3.0s -> timeout 30.1s | P0 core verified 3.0s top=1_4_1_r34 | final30 timeout 30.1s top=1_1_3_3_r46 | final120 timeout 120.1s top=1_1_2_4_r34
- 1.1.2.4 e500: record verified 4.9s -> timeout 30.0s | P0 core verified 4.8s top=1_4_1_r34 | final30 timeout 30.1s top=1_1_3_3_r46 | final120 timeout 120.1s top=1_1_2_4_r34

**class 1 g81** — deterministic, 4 entries — final timeout top=1_1_3_4_r24 — [group-level: IGtQ 4; negQ 4 (both 4)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md`: `x^k (A+Bx^3)/(a+bx^3)`, k = 7/2, 3/2, 1/2, -1/2. **Substrate.** `1_1_3_4_r24` binds `(e x)^m` with e=1 through `e_.`. The P0 literal `(e*x)^m*(a+b*x^n)^p*(c+d*x^n)` has no default, so P0 answered with the x^(1/2) substitution `1_4_1_r34` and a fall-through. **Nested.** r24's … — follows from: faithful Optional binding, exposing the IGtQ and NegQ translations

- 1.1.3.4 e155: record verified 1.8s -> timeout 30.1s | P0 core verified 1.7s top=1_4_1_r34 | final30 timeout 30.1s top=1_1_3_4_r24 | final120 timeout 120.1s top=1_1_3_4_r24
- 1.1.3.4 e158: record verified 1.8s -> timeout 30.1s | P0 core verified 1.8s top=1_4_1_r34 | final30 timeout 30.1s top=1_1_3_4_r24 | final120 timeout 120.2s top=1_1_3_4_r24
- 1.1.3.4 e159: record verified 0.8s -> timeout 30.1s | P0 core verified 0.9s top=1_4_1_r34 | final30 timeout 30.1s top=1_1_3_4_r24 | final120 timeout 120.2s top=1_1_3_4_r24

**class 1 g82** — deterministic, 4 entries — final timeout top=1_2_1_2_r119 — [group-level: none seen] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md`: `(a+bx+cx^2)^(3/2)/(d+ex)^7`, `^8`, `sqrt(quad)/(d+ex)^(5/2)`, `1/((d+ex)^(3/2) sqrt(quad))`. Both cores put r119 at top. **Nested chains.** P0: `1_2_1_9b_r5/r27/r1`. Substrate: `1_4_1_r18` (e2353/e2354), or the elliptic chain `1_1_2_3_r48`, `1_2_1_2_r93`, `9_1_r8` … — follows from: condition retry (e2353, e2445); not determined for e2354/e2466

- 1.2.1.2 e2353: record verified 3.7s -> timeout 30.1s | P0 core verified 3.7s top=1_2_1_2_r119 | final30 timeout 30.1s top=1_2_1_2_r119 | final120 timeout 120.1s top=1_2_1_2_r119
- 1.2.1.2 e2445: record verified 5.4s -> timeout 30.1s | P0 core verified 5.2s top=1_2_1_2_r119 | final30 timeout 30.0s top=1_2_1_2_r119 | final120 timeout 120.2s top=1_2_1_2_r119
- 1.2.1.2 e2466: record verified 2.9s -> timeout 30.0s | P0 core verified 2.9s top=1_2_1_2_r119 | final30 timeout 30.0s top=1_2_1_2_r119 | final120 timeout 120.1s top=1_2_1_2_r119

**class 1 g83** — deterministic, 4 entries — final timeout top=1_2_1_2_r15 — [group-level: none seen] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md`: `x^3/sqrt(a±bx^2±cx^4)`, `x^5/(…)^(3/2)`, `x^5/sqrt(a+bx^3+cx^6)`. **At 30 s.** Only the nested `1_1_2_1_r13, 1_2_1_1_r15, 1_2_1_2_r15` (+`1_2_1_2_r113`) have fired. The substitution's `(x)/sqrt(quad)` binds `1_2_1_2_r15` with d=0 through `d_.` (P0 literal `(d + e*x)*(a + b*x + …` — follows from: faithful Optional binding

- 1.2.2.2 e957: record verified 1.3s -> timeout 30.0s | P0 core verified 1.3s top=1_2_2_2_r8 | final30 timeout 30.1s top=1_2_1_2_r15 | final120 timeout 120.1s top=1_2_2_2_r8
- 1.2.2.2 e983: record verified 5.4s -> timeout 30.0s | P0 core verified 5.0s top=1_2_2_5_r3 | final30 timeout 30.0s top=1_2_1_2_r15 | final120 timeout 120.0s top=1_2_2_4_r5
- 1.2.3.2 e222: record verified 3.4s -> timeout 30.0s | P0 core verified 3.4s top=1_3_4_r20 | final30 timeout 30.1s top=1_2_1_2_r15 | final120 timeout 120.1s top=1_2_3_2_r6

**class 1 g84** — deterministic, 4 entries — final timeout top=1_2_1_2_r95 — [group-level: none seen] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md`: `(a+bx^k+cx^2k)^(j/2)/x^i`. Same shape as g83. **Nested.** `1_1_2_1_r13, 1_2_1_2_r99, 1_2_1_2_r95`; r95 binds `sqrt(quad)/x^3` with d=0 (OPT). **Timing.** At 120 s the top-level substitution has fired and the entries still time out (VERIFY-TIMEOUT). **P0.** P0's top alone … — follows from: faithful Optional binding

- 1.2.2.2 e926: record verified 2.3s -> timeout 30.0s | P0 core verified 2.3s top=1_2_2_2_r8 | final30 timeout 30.1s top=1_2_1_2_r95 | final120 timeout 120.1s top=1_2_2_2_r8
- 1.2.3.2 e192: record verified 1.8s -> timeout 30.0s | P0 core verified 1.8s top=1_3_3_r15 | final30 timeout 30.1s top=1_2_1_2_r95 | final120 timeout 120.1s top=1_2_3_2_r6
- 1.2.3.2 e210: record verified 1.8s -> timeout 30.1s | P0 core verified 1.9s top=1_3_3_r15 | final30 timeout 30.0s top=1_2_1_2_r95 | final120 timeout 120.1s top=1_2_3_2_r6

**class 1 g85** — deterministic, 4 entries — final timeout top=1_2_2_2_r13 — [group-level: negQ 4] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `(d+ex)^2/(a+b(d+ex)^2+c(d+ex)^4)^k`, k = 2, 3. **P0.** `1_4_2_r24` alone (the expandToSum normalization, nested fall-through). **Substrate nested chain.** `1_4_1_r18`, `1_2_1_1_r12`, `1_2_1_2_r3/r9`, `1_2_2_3_r27` (+`r36`), `1_2_2_2_r13`. **Wrong branch.** `1_2_2_3_r27` is … — follows from: not determined which change routes the substituted integrand to 1_2_2_2_r13; the r27 branch is the pre-existing NegQ reading

- 1.2.3.2 e623: record verified 0.7s -> timeout 30.1s | P0 core verified 0.9s top=1_4_2_r24 | final30 timeout 30.2s top=1_2_2_2_r13 | final120 error 114.3s top=1_2_2_2_r13
- 1.2.3.2 e648: record verified 0.7s -> timeout 30.1s | P0 core verified 1.0s top=1_4_2_r24 | final30 timeout 30.1s top=1_2_2_2_r13 | final120 error 117.9s top=1_2_2_2_r13
- 1.2.3.2 e656: record verified 0.7s -> timeout 30.1s | P0 core verified 1.0s top=1_4_2_r24 | final30 timeout 30.1s top=1_2_2_2_r13 | final120 error 85.7s top=1_2_2_2_r13

**class 1 g86** — deterministic, 4 entries — final timeout top=1_2_2_2_r14 — [group-level: negQ 4] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `(d+ex)^4/(…)^2`, `(…)^3`. The g85 chain with `1_2_2_2_r14` (m>3). **Arms.** e646: r2 error 24.2 s, r4 error 28.7 s, r3 timeout. The rest time out in all arms. — follows from: as g85

- 1.2.3.2 e621: record verified 0.7s -> timeout 30.1s | P0 core verified 0.9s top=1_4_2_r24 | final30 timeout 30.1s top=1_2_2_2_r14 | final120 error 72.1s top=1_2_2_2_r14
- 1.2.3.2 e646: record verified 0.7s -> error 23.8s | P0 core verified 0.9s top=1_4_2_r24 | final30 timeout 30.1s top=1_2_2_2_r14
- 1.2.3.2 e654: record verified 0.7s -> timeout 30.1s | P0 core verified 1.1s top=1_4_2_r24 | final30 timeout 30.1s top=1_2_2_2_r14 | final120 error 94.5s top=1_2_2_2_r14

**class 1 g87** — deterministic, 4 entries — final timeout top=1_2_2_2_r17 — [group-level: negQ 4] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/((d+ex)^k (…))`, k = 2, 4. The g85 chain with `1_2_2_2_r17` (m<-1), plus `1_2_2_4_r39` for k = 4. r4 e620 error 24.2 s. — follows from: as g85

- 1.2.3.2 e618: record verified 0.6s -> timeout 30.1s | P0 core verified 0.9s top=1_4_2_r24 | final30 timeout 30.1s top=1_2_2_2_r17 | final120 error 116.9s top=1_2_2_2_r17
- 1.2.3.2 e643: record verified 0.6s -> timeout 30.1s | P0 core verified 0.8s top=1_4_2_r24 | final30 timeout 30.1s top=1_2_2_2_r17 | final120 error 93.0s top=1_2_2_2_r17
- 1.2.3.2 e645: record verified 0.6s -> timeout 30.1s | P0 core verified 0.9s top=1_4_2_r24 | final30 timeout 30.1s top=1_2_2_2_r17 | final120 error 95.6s top=1_2_2_2_r17

**class 1 g88** — deterministic, 4 entries — final timeout top=1_2_3_2_r6 — [group-level: none seen] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md`: `x^5/(a+bx^3+cx^6)`, `1/(x(…))`, and the n = 4 pair. **Substrate.** The top-level x^n substitution `1_2_3_2_r6` has fired in the 30 s list, so rubi returned. Nested: `1_2_1_2_r9` → `r3` (log) and `1_2_1_1_r12` → `1_1_2_1_r13` (atanh), plus `1_1_1_1_r1`, `1_2_1_2_r80` for the 1/x … — follows from: faithful binding; the cost is verification

- 1.2.3.2 e139: record verified 3.2s -> timeout 30.1s | P0 core verified 3.1s top=1_3_4_r19 | final30 timeout 30.1s top=1_2_3_2_r6 | final120 error 56.5s top=1_2_3_2_r6
- 1.2.3.2 e312: record verified 3.2s -> timeout 30.1s | P0 core verified 3.1s top=1_3_4_r19 | final30 timeout 30.2s top=1_2_3_2_r6 | final120 error 59.6s top=1_2_3_2_r6
- 1.2.3.2 e316: record verified 14.5s -> timeout 30.1s | P0 core verified 14.3s top=1_4_1_r29 | final30 timeout 30.2s top=1_2_3_2_r6 | final120 error 64.8s top=1_2_3_2_r6

**class 1 g89** — deterministic, 4 entries — final unverified top=1_1_1_3_r25 — [group-level: none seen] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md`: `(a+bx)^n/(x^3(c+dx)^n)`, `(1-x)^n/(x^3(1+x)^n)`, `(a+bx)^m(c+dx)^(-1-m)/(e+fx)^2`, `…/(e+fx)`. **Substrate.** `1_1_1_3_r25` binds x^-3 as `(a_.+b_.x)^m` with a=0 (the P0 literal `(a + b*x)^m*(c + d*x)^n*(e + f*x)^p` has no defaults). Its nested integral is answered by … — follows from: faithful Optional binding

- 1.1.1.3 e964: record verified 3.7s -> unverified 0.4s | P0 core verified 3.8s top=1_1_1_6_r7 | final30 unverified 0.5s top=1_1_1_3_r25
- 1.1.1.3 e3064: record verified 4.3s -> unverified 18.3s | P0 core verified 4.2s top=1_1_1_3_r25 | final30 unverified 20.1s top=1_1_1_3_r25
- 1.1.1.3 e3072: record verified 4.8s -> unverified 15.5s | P0 core verified 4.5s top=1_1_1_6_r7 | final30 unverified 16.2s top=1_1_1_3_r25

**class 1 g90** — deterministic, 4 entries — final unverified top=1_1_2_8_r49 — [group-level: none seen] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/(x^k(d+ex)sqrt(d^2-e^2x^2))`, k = 1, 3. **Substrate.** `1_1_2_8_r49` (m, n = -1, -3 / -1, integers) binds, then `9_1_r8` + `1_1_3_8_r18`, or `1_1_2_11_r2`. **P0.** The later `1_1_2_8_r54` (`x^m(a+bx^2)^p/(c+dx)` literal) after `1_4_2_r25` or a class-1 chain. All arms … — follows from: faithful binding

- 1.2.1.4 e124: record verified 0.6s -> unverified 2.6s | P0 core verified 0.6s top=1_1_2_8_r54 | final30 unverified 2.1s top=1_1_2_8_r49
- 1.2.1.4 e154: record verified 0.6s -> unverified 2.8s | P0 core verified 0.6s top=1_1_2_8_r54 | final30 unverified 2.1s top=1_1_2_8_r49
- 1.2.1.4 e156: record verified 0.3s -> unverified 1.9s | P0 core verified 0.3s top=1_1_2_8_r54 | final30 unverified 1.7s top=1_1_2_8_r49

**class 1 g91** — deterministic, 4 entries — final unverified top=1_2_1_2_r117 — [group-level: none seen] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `(d+ex)^(k/2)/sqrt(ade+(cd^2+ae^2)x+cdex^2)` (the quadratic factors as (d+ex)(ae+cdx)). Both cores put r117 at top. **P0 nested.** `1_2_1_9b_r5` → `9b_r1` (divide out d+ex). **Substrate nested.** The elliptic chain `1_1_2_3_r48, 1_2_1_2_r93, 1_1_2_3_r42, 1_2_1_3_r89` (+`r56`). … — follows from: not determined from the traces (why 9b_r1 no longer answers)

- 1.2.1.2 e2057: record verified 3.5s -> unverified 4.6s | P0 core verified 4.0s top=1_2_1_2_r117 | final30 unverified 6.2s top=1_2_1_2_r117
- 1.2.1.2 e2059: record verified 3.8s -> unverified 2.3s | P0 core verified 4.0s top=1_2_1_2_r117 | final30 unverified 3.1s top=1_2_1_2_r117
- 1.2.1.4 e787: record verified 3.8s -> unverified 2.3s | P0 core verified 3.9s top=1_2_1_2_r117 | final30 unverified 3.2s top=1_2_1_2_r117

**class 1 g92** — deterministic, 4 entries — final unverified top=1_2_1_3_r15 — [group-level: IGtQ 4] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md`: `(f+gx)(cd^2-bde-be^2x-ce^2x^2)^(3/2 or 5/2)/(d+ex)^(1 or 2)`. **Substrate.** `1_2_1_3_r15` (Rubi `IGtQ[p,0]` → ExpandIntegrand) accepts p = 3/2, 5/2 through `is(p > 0)`. nfires=1; the answer is unverified. **P0.** `1_4_2_r25` → `1_3_3_r6` (polyGCD cancel); P0's r15 literal did … — follows from: binding change exposing the IGtQ translation

- 1.2.1.3 e2186: record verified 1.8s -> unverified 1.1s | P0 core verified 1.8s top=1_3_3_r6 | final30 unverified 1.2s top=1_2_1_3_r15
- 1.2.1.3 e2198: record verified 1.9s -> unverified 1.4s | P0 core verified 2.0s top=1_3_3_r6 | final30 unverified 1.5s top=1_2_1_3_r15
- 1.2.1.3 e2199: record verified 2.0s -> unverified 1.0s | P0 core verified 2.0s top=1_3_3_r6 | final30 unverified 1.1s top=1_2_1_3_r15

**class 1 g93** — deterministic, 3 entries — final contains-noun top=1_1_2_8_r20 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(A+Bx)(a+cx^2)^k/x`, k = 2, 3, 4. Both cores put r20 at top. **Nested.** P0: fall-through (nfires=1). Substrate: `1_1_2_8_r123` (CATCH-1) → marker. **Corpus.** 2 steps, no Unintegrable. All arms contains-noun. — follows from: faithful binding (NOUN); why r20's reduced integral reaches the catch-all is not determined

- 1.2.1.3 e262: record verified 1.2s -> contains-noun 0.3s | P0 core verified 1.2s top=1_1_2_8_r20 | final30 contains-noun 0.4s top=1_1_2_8_r20
- 1.2.1.3 e269: record verified 1.2s -> contains-noun 0.6s | P0 core verified 1.2s top=1_1_2_8_r20 | final30 contains-noun 0.6s top=1_1_2_8_r20
- 1.2.1.3 e276: record verified 1.3s -> contains-noun 0.8s | P0 core verified 1.3s top=1_1_2_8_r20 | final30 contains-noun 0.6s top=1_1_2_8_r20

**class 1 g94** — deterministic, 3 entries — final contains-noun top=1_2_1_3_r54 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(2-5x)x^(k/2)/(2+5x+3x^2)^(j/2)`. **Substrate.** `1_2_1_3_r54` binds x^(k/2) as `(d+ex)^m` with d=0 (OPT). Its sub-integral runs `1_4_1_r34` (substitution), then `1_2_2_7_r42` (CATCH-1; e1077 `1_2_2_6_r9`) → marker. **P0.** `1_4_1_r34` at top after a 1.2.2 chain. **Corpus.** … — follows from: faithful Optional binding; why the quartic sub-integral reaches the catch-all is not determined

- 1.2.1.3 e1067: record verified 2.8s -> contains-noun 2.3s | P0 core verified 2.7s top=1_4_1_r34 | final30 contains-noun 2.3s top=1_2_1_3_r54
- 1.2.1.3 e1077: record verified 3.0s -> contains-noun 3.5s | P0 core verified 2.9s top=1_4_1_r34 | final30 contains-noun 3.6s top=1_2_1_3_r54
- 1.2.1.3 e1078: record verified 2.9s -> contains-noun 2.3s | P0 core verified 2.9s top=1_4_1_r34 | final30 contains-noun 2.2s top=1_2_1_3_r54

**class 1 g95** — deterministic, 3 entries — final contains-noun top=1_2_2_8_r4 — [group-level: negQ 3] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/((d+ex)^k sqrt(a+cx^4))`. **Substrate.** `1_2_2_8_r4` (Rubi's own rule, ahead of 1.3.4) binds. Nested: `1_2_2_8_r19` (/r16), `1_2_2_7_r37`, `1_2_2_3_r87`, `1_2_2_3_r59` (`%mr_negQ(c/a)` on symbolic c/a), `1_2_2_3_r100` (CATCH-1) → marker, plus `1_2_2_4_r94`. **P0.** … — follows from: faithful binding; the nested NegQ reading

- 1.2.2.8 e2: record verified 3.2s -> contains-noun 5.1s | P0 core verified 3.8s top=1_3_4_r9 | final30 contains-noun 4.8s top=1_2_2_8_r4
- 1.3.2 e194: record verified 3.9s -> contains-noun 3.5s | P0 core verified 3.8s top=1_3_4_r9 | final30 contains-noun 5.2s top=1_2_2_8_r4
- 1.3.2 e195: record verified 3.8s -> contains-noun 6.4s | P0 core verified 3.9s top=1_3_4_r9 | final30 contains-noun 8.7s top=1_2_2_8_r4

**class 1 g96** — deterministic, 3 entries — final deferred top=1_1_1_3_r17 — [group-level: none seen] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md`: `x^2(a+bx)^n/(c+dx)`, `(2+3x)^m(3+5x)^k/(1-2x)`. **Substrate.** `1_1_1_3_r17` (ExpandIntegrand; x^2 bound as (0+x)^2) answers alone with a top-level noun. **P0.** `1_1_1_3_r19` / `r29`. **Arms.** r3 reads expected for e925 and e3182 (0.1 / 0.3 s), so r17 accepts only on a … — follows from: condition retry (e925, e3182); e3181 not determined

- 1.1.1.3 e925: record verified 1.5s -> deferred 0.1s | P0 core verified 1.5s top=1_1_1_3_r19 | final30 deferred 0.2s top=1_1_1_3_r17
- 1.1.1.3 e3181: record verified 0.8s -> deferred 0.1s | P0 core verified 0.8s top=1_1_1_3_r29 | final30 deferred 0.1s top=1_1_1_3_r17
- 1.1.1.3 e3182: record verified 0.8s -> deferred 0.1s | P0 core verified 0.8s top=1_1_1_3_r19 | final30 deferred 0.1s top=1_1_1_3_r17

**class 1 g97** — deterministic, 3 entries — final deferred top=1_1_2_8_r107 — [group-level: none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(a+bx^2)^p/(x^k(d+ex)^j)`. Both cores put r107 at top (`ILtQ[n,-1]`; n = -2, -3 are integers). **P0.** The ExpandIntegrand sum dispatched through `1_4_1_r7`. **Substrate.** nfires=1, a top-level noun: the class 2 g1 shape. All arms deferred. — follows from: not determined from the traces

- 1.2.1.4 e422: record verified 11.4s -> deferred 0.6s | P0 core verified 11.0s top=1_1_2_8_r107 | final30 deferred 0.4s top=1_1_2_8_r107
- 1.2.1.4 e428: record verified 13.1s -> deferred 0.6s | P0 core verified 13.0s top=1_1_2_8_r107 | final30 deferred 0.4s top=1_1_2_8_r107
- 1.2.1.4 e429: record verified 13.4s -> deferred 0.6s | P0 core verified 13.3s top=1_1_2_8_r107 | final30 deferred 0.4s top=1_1_2_8_r107

**class 1 g98** — deterministic, 3 entries — final deferred top=1_1_3_4_r26 — [group-level: IGtQ 3] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(ex)^(k/2) sqrt(c+dx^4)/(a+bx^4)`. **Substrate.** `1_1_3_4_r26` (Rubi `IGtQ[n,0] && IGtQ[p,0]`) accepts p = 1/2: EXPAND-NOUN. **P0.** `1_4_2_r8` → `1_3_4_r3` (the corpus's 3-step AppellF1). All arms deferred. — follows from: binding change (P0's r26 literal did not bind) exposing the IGtQ translation

- 1.1.3.4 e633: record verified 1.8s -> deferred 0.3s | P0 core verified 2.2s top=1_3_4_r3 | final30 deferred 0.4s top=1_1_3_4_r26
- 1.1.3.4 e634: record verified 1.7s -> deferred 0.3s | P0 core verified 2.2s top=1_3_4_r3 | final30 deferred 0.4s top=1_1_3_4_r26
- 1.1.3.4 e635: record verified 1.5s -> deferred 0.3s | P0 core verified 1.9s top=1_3_4_r3 | final30 deferred 0.4s top=1_1_3_4_r26

**class 1 g99** — deterministic, 3 entries — final deferred top=1_1_3_4_r30 — [group-level: NE 3] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md`: `x/((4c+dx^3)sqrt(c+dx^3))`, `x/((1-x^3)^(1/3)(1+x^3))`, `x/((1-x^3)^(2/3)(1+x^3))`. **Substrate.** `1_1_3_4_r30` binds x as `x^m_.` (m=1), so k = gcd(2,3) = 1 and `is(k != 1)` reads true (NE). The x → x^1 substitution re-dispatches the integrand, which the seen guard returns as … — follows from: faithful Optional binding exposing the `!=` translation

- 1.1.3.4 e276: record verified 0.2s -> deferred 0.3s | P0 core verified 0.2s top=1_1_3_4_r52 | final30 deferred 0.4s top=1_1_3_4_r30
- 1.1.3.4 e582: record verified 1.4s -> deferred 0.3s | P0 core verified 1.7s top=1_1_3_4_r56 | final30 deferred 0.3s top=1_1_3_4_r30
- 1.1.3.4 e592: record verified 0.2s -> deferred 0.3s | P0 core verified 0.2s top=1_1_3_4_r57 | final30 deferred 0.3s top=1_1_3_4_r30

**class 1 g100** — deterministic, 3 entries — final deferred top=1_1_4_4_r11 — [group-level: none seen] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `(-1+x^3)/(-4x+x^4)^(2/3)`, `(2-x^2)(6x-x^3)^(1/4)`, `(1+x^4)sqrt(5x+x^5)` (1-step derivative-divides in the corpus). **P0.** `1_1_4_4_r2` alone. **Substrate.** `1_1_4_4_r2` declines (its `integerp((m+1)/n)` with the Optional m=0), and the later `1_1_4_4_r11` (ExpandIntegrand) … — follows from: not determined from the traces (P0's r2 binding is not recorded)

- 1.3.2 e440: record verified 0.7s -> deferred 0.4s | P0 core verified 1.0s top=1_1_4_4_r2 | final30 deferred 0.6s top=1_1_4_4_r11
- 1.3.2 e441: record verified 0.7s -> deferred 0.4s | P0 core verified 1.0s top=1_1_4_4_r2 | final30 deferred 0.6s top=1_1_4_4_r11
- 1.3.2 e442: record verified 0.8s -> deferred 0.3s | P0 core verified 1.1s top=1_1_4_4_r2 | final30 deferred 0.5s top=1_1_4_4_r11

**class 1 g101** — deterministic, 3 entries — final deferred top=1_2_1_1_r5 — [group-level: IGtQ 3] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(bx+cx^2)^(5/4, 3/4, 1/4)`. **Substrate.** `1_2_1_1_r5` (Rubi `IGtQ[p,0] && (EqQ[a,0] || …)`) binds a=0 through `a_.` and accepts p = 1/4..5/4 through `is(p > 0)`: EXPAND-NOUN. **P0.** `1_2_1_1_r4` (non-Optional `a_`, bound a=0; PerfectSquareQ) → `1_1_1_2_r12`, verified. On the … — follows from: G-1 plus faithful Optional binding, exposing the IGtQ translation

- 1.2.1.1 e40: record verified 0.3s -> deferred 0.2s | P0 core verified 0.3s top=1_2_1_1_r4 | final30 deferred 0.1s top=1_2_1_1_r5
- 1.2.1.1 e41: record verified 0.3s -> deferred 0.2s | P0 core verified 0.3s top=1_2_1_1_r4 | final30 deferred 0.1s top=1_2_1_1_r5
- 1.2.1.1 e42: record verified 0.3s -> deferred 0.2s | P0 core verified 0.3s top=1_2_1_1_r4 | final30 deferred 0.1s top=1_2_1_1_r5

**class 1 g102** — deterministic, 3 entries — final deferred top=1_2_2_1_r19 — [group-level: none seen] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md`: `(4ac+4c^2x^2+4cdx^3+d^2x^4)^(k/2)`. Both cores put r19 at top (the depressed-quartic substitution). **Nested.** P0: `1_4_1_r29` / `1_2_2_5_r1`. Substrate: `1_4_2_r18` only, then a top-level noun. **Arms.** r4 verified 0.5 / 0.6 / 4.1 s (MFLAGS); r2/r3 deferred. — follows from: model flags

- 1.3.2 e617: record verified 2.1s -> deferred 0.3s | P0 core verified 3.0s top=1_2_2_1_r19 | final30 deferred 0.5s top=1_2_2_1_r19
- 1.3.2 e618: record verified 0.6s -> deferred 0.3s | P0 core verified 0.9s top=1_2_2_1_r19 | final30 deferred 0.5s top=1_2_2_1_r19
- 1.3.2 e620: record verified 0.8s -> deferred 0.3s | P0 core verified 1.2s top=1_2_2_1_r19 | final30 deferred 0.5s top=1_2_2_1_r19

**class 1 g103** — deterministic, 3 entries — final deferred top=1_2_3_4_r100 — [group-level: none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(fx)^m(d+ex^n)^k(a+cx^2n)^p`, k = 3, 2, 1. **Substrate.** `1_2_3_4_r100` (IGtQ[q,0] with q = k, an integer, so Rubi applies it too) expands, and the sum yields no nested fire: a top-level noun (class 2 g1 shape). **P0.** The manual 9.1 `u*(a*x^n)^m` (P0 `9_1_r16`). All arms … — follows from: 9.1 regeneration; why the expansion yields no fire is not determined

- 1.2.3.4 e87: record verified 4.4s -> deferred 0.5s | P0 core verified 5.5s top=9_1_r16 | final30 deferred 0.5s top=1_2_3_4_r100
- 1.2.3.4 e88: record verified 4.7s -> deferred 0.6s | P0 core verified 5.4s top=9_1_r16 | final30 deferred 0.5s top=1_2_3_4_r100
- 1.2.3.4 e89: record verified 4.8s -> deferred 0.4s | P0 core verified 5.7s top=9_1_r16 | final30 deferred 0.3s top=1_2_3_4_r100

**class 1 g104** — deterministic, 3 entries — final deferred top=1_2_3_4_r99 — [group-level: none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(fx)^m(d+ex^n)^k(a+bx^n+cx^2n)^p`. As g103 with `1_2_3_4_r99` (q = 1, 2, 1). — follows from: as g103

- 1.2.3.4 e141: record verified 4.6s -> deferred 0.6s | P0 core verified 5.3s top=9_1_r16 | final30 deferred 0.5s top=1_2_3_4_r99
- 1.2.3.4 e152: record verified 4.8s -> deferred 0.8s | P0 core verified 5.5s top=9_1_r16 | final30 deferred 0.7s top=1_2_3_4_r99
- 1.2.3.4 e153: record verified 5.5s -> deferred 0.5s | P0 core verified 5.9s top=9_1_r16 | final30 deferred 0.5s top=1_2_3_4_r99

**class 1 g105** — deterministic, 3 entries — final deferred top=1_3_3_r7 — [group-level: IGtQ 2; none seen 1] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md`: `(1-x)/((2+x)sqrt(1∓x^3))`, `(1-x^2)/((1-x+x^2)(1-x^3)^(2/3))`. **Substrate.** `1_3_3_r7` (Rubi `ILtQ[q,0]`) accepts q = -1/2, -2/3 through `is(q < 0)`. Its polyGCD rewrite ends in a top-level noun (e52/e53 add nested `1_4_1_r18`). **P0.** Rubi's `1_4_3_r36` / `r55`. **Arms.** … — follows from: condition retry exposing the ILtQ translation (e52/e53); e878 not determined

- 1.3.2 e52: record verified 1.2s -> deferred 2.0s | P0 core verified 1.1s top=1_4_3_r36 | final30 deferred 2.7s top=1_3_3_r7
- 1.3.2 e53: record verified 1.1s -> deferred 1.7s | P0 core verified 1.1s top=1_4_3_r36 | final30 deferred 2.6s top=1_3_3_r7
- 1.3.2 e878: record verified 3.9s -> deferred 7.7s | P0 core verified 4.6s top=1_4_3_r55 | final30 deferred 9.0s top=1_3_3_r7

**class 1 g106** — deterministic, 3 entries — final deferred top=9_1_r27 — [group-level: none seen; collapse-family: 1.2.1.2 e1734, 1.2.1.2 e1735, 1.2.1.2 e1736] [9.1-COLLAPSE]
> `10-p5-attribution.mechanisms-class1-c.md`: 1.2.1.2 e1734–e1736, `(d+ex)^m/(a^2+2abx+b^2x^2)^k`, k = 1, 2, 3 (P0 expected). [collapse-family] See **Collapse family**. **P0.** The collapse rule `9_1_r28` (`rubi_hybrid_exact`) → `1_1_1_2_r37`. **Substrate.** The same Rubi rule, generated `9_1_r27`, alone: its rewrite hits … — follows from: 9.1 regeneration (`rubi_hybrid_exact` → `mr_int`) meeting the ratsimp seen guard

- 1.2.1.2 e1734: record expected 1.1s -> deferred 1.3s | P0 core expected 1.1s top=9_1_r28 | final30 deferred 1.4s top=9_1_r27
- 1.2.1.2 e1735: record expected 1.3s -> deferred 1.0s | P0 core expected 1.2s top=9_1_r28 | final30 deferred 1.4s top=9_1_r27
- 1.2.1.2 e1736: record expected 1.3s -> deferred 1.0s | P0 core expected 1.2s top=9_1_r28 | final30 deferred 1.4s top=9_1_r27

**class 1 g107** — deterministic, 3 entries — final error top=1_1_3_2_r13 — [group-level: IGtQ 3] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/(x^3(1∓x^8))`, `1/(x^7(1-x^8))`. **Top level.** `1_1_3_2_r13` (Rubi `ILtQ[Simplify[(m+1)/n+p+1],0]`) accepts -1/4 and -3/4. Its fire is in every list, so rubi returned. **Nested.** `x^(m+8)/(1∓x^8)` runs `1_1_3_2_r35/r36` on n = 8 ((8-1)/2 = 7/2) and the PF-EVEN prefix. The … — follows from: faithful binding exposing the IGtQ translation

- 1.1.3.2 e1475: record verified 1.1s -> error 6.2s | P0 core verified 1.1s top=1_3_4_r1 | final30 error 14.3s top=1_1_3_2_r13
- 1.1.3.2 e1477: record verified 1.1s -> error 28.6s | P0 core verified 1.1s top=1_3_4_r1 | final30 error 29.7s top=1_1_3_2_r13
- 1.1.3.2 e1494: record verified 1.1s -> error 6.5s | P0 core verified 1.1s top=1_3_4_r1 | final30 error 19.8s top=1_1_3_2_r13

**class 1 g108** — deterministic, 3 entries — final timeout top=1_1_2_4_r29 — [group-level: IGtQ 3; negQ 3 (both 3)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md`: `x^k(A+Bx^2)/(a+bx^2)`, k = 7/2, 3/2, -1/2. **Substrate.** `1_1_2_4_r29` binds e=1 through `e_.`. Nested: the x^(1/2) substitution `1_1_2_2_r27` (+`r23`), then PF-EVEN `1_1_3_1_r14` on 1/(a+bt^4) ((4-3)/2 = 1/2; a/b symbolic). **Timing.** Top-level fire in the 30 s list; timeout … — follows from: faithful Optional binding exposing IGtQ and NegQ

- 1.1.2.4 e367: record verified 1.5s -> timeout 30.1s | P0 core verified 1.5s top=1_4_1_r34 | final30 timeout 30.0s top=1_1_2_4_r29 | final120 timeout 120.1s top=1_1_2_4_r29
- 1.1.2.4 e369: record verified 1.5s -> timeout 30.1s | P0 core verified 1.5s top=1_4_1_r34 | final30 timeout 30.0s top=1_1_2_4_r29 | final120 timeout 120.1s top=1_1_2_4_r29
- 1.1.2.4 e371: record verified 0.9s -> timeout 30.0s | P0 core verified 0.9s top=1_4_1_r34 | final30 timeout 30.0s top=1_1_2_4_r29 | final120 timeout 120.1s top=1_1_2_4_r29

**class 1 g109** — deterministic, 3 entries — final timeout top=1_1_3_3_r21 — [group-level: IGtQ 3; negQ 3 (both 3)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/((a+bx^2)(c+dx^2)sqrt(x))`, `1/((a+bx^4)(c+dx^4))` ×2. **Substrate.** `1_1_3_3_r21` (partial fractions; no P0 defmatch record) → PF-EVEN `1_1_3_1_r14` (n = 4, symbolic). **Timing.** For e466 the top-level x^(1/2) substitution fires only by 120 s. **P0.** `1_4_1_r34` / … — follows from: faithful binding exposing IGtQ and NegQ

- 1.1.2.4 e466: record verified 1.9s -> timeout 30.0s | P0 core verified 1.9s top=1_4_1_r34 | final30 timeout 30.0s top=1_1_3_3_r21 | final120 timeout 120.1s top=1_1_2_4_r34
- 1.1.3.3 e65: record verified 6.3s -> timeout 30.1s | P0 core verified 6.2s top=1_4_1_r29 | final30 timeout 30.1s top=1_1_3_3_r21 | final120 error 97.9s top=1_1_3_3_r21
- 1.1.3.4 e615: record verified 4.5s -> timeout 30.1s | P0 core verified 6.4s top=1_4_1_r29 | final30 timeout 30.1s top=1_1_3_3_r21 | final120 error 86.2s top=1_1_3_3_r21

**class 1 g110** — deterministic, 3 entries — final timeout top=1_1_3_4_r18 — [group-level: IGtQ 3; negQ 3 (both 3)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(A+Bx^3)/(x^(k/2)(a+bx^3))`, k = 3, 5, 7. **Substrate.** `1_1_3_4_r18` (m<-1, e=1 through `e_.`) fired in the 30 s list. Nested: PF-EVEN through `1_1_3_2_r36`, or `1_1_3_2_r71` → t^6 → `1_1_3_1_r14`. **P0.** `1_4_1_r34`. VERIFY-TIMEOUT; all arms timeout. — follows from: faithful Optional binding exposing IGtQ and NegQ

- 1.1.3.4 e160: record verified 1.9s -> timeout 30.1s | P0 core verified 1.8s top=1_4_1_r34 | final30 timeout 30.0s top=1_1_3_4_r18 | final120 timeout 120.3s top=1_1_3_4_r18
- 1.1.3.4 e161: record verified 1.7s -> timeout 30.1s | P0 core verified 1.9s top=1_4_1_r34 | final30 timeout 30.1s top=1_1_3_4_r18 | final120 timeout 120.2s top=1_1_3_4_r18
- 1.1.3.4 e162: record verified 1.8s -> timeout 30.1s | P0 core verified 1.8s top=1_4_1_r34 | final30 timeout 30.1s top=1_1_3_4_r18 | final120 timeout 120.2s top=1_1_3_4_r18

**class 1 g111** — deterministic, 3 entries — final timeout top=1_2_1_2_r113 — [group-level: IGtQ 2; none seen 1] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md`: `(d+ex)^4/(quad)^(3/2)`, `x^9/(quartic)^(3/2)`, `x^7/(quartic)^(3/2)`. **Substrate.** `1_2_1_2_r113` binds (P0's literal did not; P0 answered with `1_2_1_6_r1` alone). **Nested (e2382/e981).** `1_2_1_9b_r5` (Rubi `IGtQ[p,-2]`; accepts p = -3/2 through `is(p > -2)`), `9b_r32` … — follows from: faithful binding exposing the IGtQ translation (e2382, e981)

- 1.2.1.2 e2382: record verified 0.8s -> timeout 30.0s | P0 core verified 0.8s top=1_2_1_6_r1 | final30 timeout 30.1s top=1_2_1_2_r113 | final120 timeout 120.1s top=1_2_1_2_r113
- 1.2.2.2 e981: record verified 2.0s -> timeout 30.0s | P0 core verified 1.9s top=1_2_2_2_r8 | final30 timeout 30.0s top=1_2_1_2_r113 | final120 timeout 120.0s top=1_2_2_2_r8
- 1.2.2.2 e982: record verified 1.9s -> timeout 30.0s | P0 core verified 1.9s top=1_2_2_2_r8 | final30 timeout 30.0s top=1_2_1_2_r113 | final120 timeout 120.1s top=1_2_1_2_r113

**class 1 g112** — deterministic, 3 entries — final timeout top=1_4_1_r25 — [group-level: IGtQ 3; negQ 3 (both 3)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(A+Bx^2)/(x^(k/2)(bx^2+cx^4))`. Both cores put `1_4_1_r25` (x^r content removal) at top. **Nested.** P0: `1_4_1_r34` only. Substrate: `1_1_2_4_r25` (e=1 through `e_.`) → `1_1_2_2_r27` → PF-EVEN `1_1_3_1_r14` (n = 4, symbolic). e192/e194 add `1_1_2_2_r6` on a quarter-integer … — follows from: faithful Optional binding exposing IGtQ and NegQ

- 1.1.4.3 e190: record verified 2.7s -> timeout 30.0s | P0 core verified 2.6s top=1_4_1_r25 | final30 timeout 30.1s top=1_4_1_r25 | final120 timeout 120.1s top=1_4_1_r25
- 1.1.4.3 e192: record verified 2.6s -> timeout 30.0s | P0 core verified 2.5s top=1_4_1_r25 | final30 timeout 30.1s top=1_4_1_r25 | final120 timeout 120.1s top=1_4_1_r25
- 1.1.4.3 e194: record verified 2.5s -> timeout 30.0s | P0 core verified 2.6s top=1_4_1_r25 | final30 timeout 30.1s top=1_4_1_r25 | final120 timeout 120.2s top=1_4_1_r25

**class 1 g113** — deterministic, 3 entries — final unverified top=1_1_1_3_r29 — [group-level: NE 2; none seen 1] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `x^k/((1-x)^(1/3)(2-x)^(1/3))`, k = 4, 3; `(1-x)^n x^3/(1+x)^n`. **Top.** Both cores put r29 at top for e863/e864; e966 P0 `1_1_1_6_r7`. **Substrate nested.** `1_1_3_2_r17` (NE: a fire means k = 1, an identity substitution and Maxima `integrate`), `1_2_1_1_r17`, `1_1_1_2_r30` … — follows from: not determined from the traces; the r17 fire carries the `!=` misreading

- 1.1.1.3 e863: record verified 1.9s -> unverified 0.6s | P0 core verified 1.9s top=1_1_1_3_r29 | final30 unverified 0.6s top=1_1_1_3_r29
- 1.1.1.3 e864: record verified 1.9s -> unverified 0.5s | P0 core verified 1.9s top=1_1_1_3_r29 | final30 unverified 0.6s top=1_1_1_3_r29
- 1.1.1.3 e966: record verified 3.0s -> unverified 0.4s | P0 core verified 3.4s top=1_1_1_6_r7 | final30 unverified 0.4s top=1_1_1_3_r29

**class 1 g114** — deterministic, 3 entries — final unverified top=1_1_1_3_r57 — [group-level: none seen] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md`: `(a+bx)^(1+n)/(x^2(a-bx)^n)`, `(a+bx)^(1∓n)(c+dx)^(1±n)/(bc+ad+2bdx)^2` (m+n = 1, 2 are integers). **e995.** Both cores put r57 at top; the nested chain differs (substrate `1_1_1_4_r46, 1_1_1_2_r39, 1_1_1_3_r61, 1_3_4_r3, 1_1_1_3_r25`). **e3126/e3130.** r57 binds where P0's … — follows from: faithful binding

- 1.1.1.3 e995: record verified 0.3s -> unverified 3.4s | P0 core verified 0.3s top=1_1_1_3_r57 | final30 unverified 3.5s top=1_1_1_3_r57
- 1.1.1.3 e3126: record verified 6.1s -> unverified 3.4s | P0 core verified 5.9s top=1_1_1_6_r5 | final30 unverified 3.8s top=1_1_1_3_r57
- 1.1.1.3 e3130: record verified 6.2s -> unverified 1.1s | P0 core verified 6.3s top=1_1_1_6_r5 | final30 unverified 1.4s top=1_1_1_3_r57

**class 1 g115** — deterministic, 3 entries — final unverified top=1_1_2_2_r6 — [group-level: IGtQ 3] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/(x^k(-2-3x^2)^(3/4))`, k = 2, 4, 6. **Fires.** The same fire list on both cores (`1_1_3_1_r32, 1_1_2_1_r26, 1_1_2_2_r6`). **Arms.** r4 verified 0.1–0.2 s: MFLAGS. **IGT on both cores.** `1_1_2_2_r6`'s `is((m+1)/2+p+1 < 0)` (Rubi ILtQ) accepts -1/4, -5/4, -9/4 on both cores … — follows from: model flags

- 1.1.2.2 e916: record verified 0.2s -> unverified 0.4s | P0 core verified 0.2s top=1_1_2_2_r6 | final30 unverified 0.6s top=1_1_2_2_r6
- 1.1.2.2 e917: record verified 0.2s -> unverified 0.4s | P0 core verified 0.2s top=1_1_2_2_r6 | final30 unverified 0.5s top=1_1_2_2_r6
- 1.1.2.2 e918: record verified 0.2s -> unverified 0.6s | P0 core verified 0.2s top=1_1_2_2_r6 | final30 unverified 0.6s top=1_1_2_2_r6

**class 1 g116** — deterministic, 3 entries — final unverified top=1_2_1_2_r105 — [group-level: none seen] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md`: `(ade+(cd^2+ae^2)x+cdex^2)^(k/2)/(d+ex)^(k+3)` (2-step algebraic corpus answers). **Substrate.** `1_2_1_2_r105` binds (P0's literal did not; P0 `1_4_2_r25` → `1_3_3_r6` polyGCD cancel). Nested: `1_2_1_2_r133/r95`, `1_1_1_4_r46`, `1_1_2_1_r13`. All arms unverified. — follows from: faithful binding; why the Rubi-form answer is unverified is not determined

- 1.2.1.2 e1915: record verified 1.7s -> unverified 1.1s | P0 core verified 1.8s top=1_3_3_r6 | final30 unverified 1.6s top=1_2_1_2_r105
- 1.2.1.2 e1928: record verified 1.5s -> unverified 1.4s | P0 core verified 1.8s top=1_3_3_r6 | final30 unverified 2.0s top=1_2_1_2_r105
- 1.2.1.2 e1943: record verified 1.7s -> unverified 1.7s | P0 core verified 1.7s top=1_3_3_r6 | final30 unverified 2.4s top=1_2_1_2_r105

**class 1 g117** — deterministic, 3 entries — final unverified top=1_2_1_2_r109 — [group-level: none seen] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `sqrt(d+ex)sqrt(quad)`, `sqrt(quad)/sqrt(d+ex)` ×2 (1-step corpus answers). **Substrate.** r109, with the g91 elliptic chain nested. **P0.** r109 with the `9b_r1` cancel (e2030), or `1_1_1_2_r12` → `1_3_3_r6`. All arms unverified. — follows from: not determined from the traces

- 1.2.1.2 e2030: record verified 3.8s -> unverified 3.4s | P0 core verified 3.9s top=1_2_1_2_r109 | final30 unverified 4.5s top=1_2_1_2_r109
- 1.2.1.2 e2031: record verified 1.0s -> unverified 2.3s | P0 core verified 1.1s top=1_3_3_r6 | final30 unverified 3.1s top=1_2_1_2_r109
- 1.2.1.4 e683: record verified 1.1s -> unverified 2.8s | P0 core verified 1.0s top=1_3_3_r6 | final30 unverified 3.3s top=1_2_1_2_r109

**class 1 g118** — deterministic, 3 entries — final unverified top=1_2_1_2_r111 — [group-level: none seen] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md`: `sqrt(d+ex)/(quad)^k`, k = 3, 3/2, 5/2. The three entries do not share a mechanism: **e2068.** Identical fire lists on both cores; r4 verified 2.2 s (MFLAGS). **e2025.** P0 `1_4_1_r18` alone; the substrate adds `1_2_1_3_r55` and top r111; all arms unverified. **e2076.** The … — follows from: model flags (e2068); faithful binding (e2025, e2076)

- 1.2.1.2 e2025: record verified 0.6s -> unverified 2.4s | P0 core verified 0.8s top=1_4_1_r18 | final30 unverified 3.2s top=1_2_1_2_r111
- 1.2.1.2 e2068: record verified 3.4s -> unverified 3.0s | P0 core verified 3.9s top=1_2_1_2_r111 | final30 unverified 4.0s top=1_2_1_2_r111
- 1.2.1.2 e2076: record verified 2.3s -> unverified 5.3s | P0 core verified 3.0s top=1_2_1_2_r111 | final30 unverified 7.2s top=1_2_1_2_r111

**class 1 g119** — deterministic, 3 entries — final unverified top=1_2_1_2_r95 — [group-level: none seen] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md`: `(quad)^(k/2)/(d+ex)^(k+2)` (1-step corpus answers). **Substrate.** r95 → `1_2_1_2_r133` → `1_1_1_4_r46` → `1_1_2_1_r13`. **P0.** `1_4_2_r25` → `1_3_3_r6`. All arms unverified. — follows from: faithful binding (as g116)

- 1.2.1.2 e1914: record verified 1.7s -> unverified 0.8s | P0 core verified 1.7s top=1_3_3_r6 | final30 unverified 1.1s top=1_2_1_2_r95
- 1.2.1.2 e1927: record verified 1.7s -> unverified 1.1s | P0 core verified 1.8s top=1_3_3_r6 | final30 unverified 1.5s top=1_2_1_2_r95
- 1.2.1.2 e1942: record verified 1.6s -> unverified 1.4s | P0 core verified 1.7s top=1_3_3_r6 | final30 unverified 1.9s top=1_2_1_2_r95

**class 1 g120** — deterministic, 3 entries — final unverified top=1_2_3_2_r34 — [group-level: none seen] [9.1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(dx)^m(a+bx^n+cx^2n)^p` (n = 3, n). **Substrate.** `1_2_3_2_r34` (the FracPart rewrite) → `1_1_3_4_r78` (AppellF1): Rubi's 2-step AppellF1 answer, not closed by the zero chain. **P0.** The manual 9.1 `u*(a*x^n)^m`. All arms unverified. — follows from: 9.1 regeneration

- 1.2.3.2 e256: record verified 5.4s -> unverified 1.0s | P0 core verified 5.3s top=9_1_r16 | final30 unverified 1.1s top=1_2_3_2_r34
- 1.2.3.2 e606: record verified 4.1s -> unverified 0.7s | P0 core verified 5.7s top=9_1_r16 | final30 unverified 1.1s top=1_2_3_2_r34
- 1.2.3.4 e154: record verified 5.2s -> unverified 1.3s | P0 core verified 5.9s top=9_1_r16 | final30 unverified 1.2s top=1_2_3_2_r34

**class 1 g121** — deterministic, 2 entries — final contains-noun top=1_1_1_3_r27 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(c+dx)^3/(x(a+bx)^k)`, k = 2, 3. **Substrate.** `1_1_1_3_r27`; its nested integral binds `1_1_1_4_r42` (CATCH-1) → marker. **P0.** `1_1_1_3_r29` / `r59`. **Arms.** r3 verified 0.2 / 0.5 s. — follows from: condition retry

- 1.1.1.3 e243: record verified 2.0s -> contains-noun 0.4s | P0 core verified 1.8s top=1_1_1_3_r29 | final30 contains-noun 0.2s top=1_1_1_3_r27
- 1.1.1.3 e275: record verified 2.9s -> contains-noun 0.2s | P0 core verified 2.5s top=1_1_1_3_r59 | final30 contains-noun 0.3s top=1_1_1_3_r27

**class 1 g122** — deterministic, 2 entries — final contains-noun top=1_1_1_3_r29 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(5-4x)^k(1+2x)^(-3-m)(2+3x)^m`. **Substrate.** r29 → nested `1_1_1_4_r42` (CATCH-1; +`1_1_1_4_r12`) → marker. **P0.** `1_1_1_4_r47` alone. r3 verified 1.0–1.2 s. — follows from: condition retry

- 1.1.1.3 e3076: record verified 0.2s -> contains-noun 0.5s | P0 core verified 0.2s top=1_1_1_4_r47 | final30 contains-noun 0.4s top=1_1_1_3_r29
- 1.1.1.3 e3077: record verified 0.2s -> contains-noun 0.3s | P0 core verified 0.2s top=1_1_1_4_r47 | final30 contains-noun 0.3s top=1_1_1_3_r29

**class 1 g123** — deterministic, 2 entries — final contains-noun top=1_1_2_4_r20 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(c+dx^2)^3/(x(a+bx^2)^k)`. Both cores put r20 (x^2 substitution) at top. **Nested.** Substrate: `1_1_1_4_r42` (CATCH-1) + `1_1_1_3_r13/r27`. P0: `1_1_1_3_r13/r29`. **Arms.** r3 verified for e285 (0.2 s); CN for e224. — follows from: condition retry (e285); e224 not determined

- 1.1.2.4 e224: record verified 1.9s -> contains-noun 0.4s | P0 core verified 1.9s top=1_1_2_4_r20 | final30 contains-noun 0.4s top=1_1_2_4_r20
- 1.1.2.4 e285: record verified 2.0s -> contains-noun 0.6s | P0 core verified 2.0s top=1_1_2_4_r20 | final30 contains-noun 0.5s top=1_1_2_4_r20

**class 1 g124** — deterministic, 2 entries — final contains-noun top=1_1_2_7_r47 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(d+ex)^3(a+cx^2)^p`. **Substrate.** `1_1_2_7_r47` binds (P0's literal did not); its reduced integral reaches `1_1_2_9_r107` (CATCH-1) → marker. **P0.** `1_2_1_9b_r29` after `1_2_1_1_r18, 1_1_2_3_r20, 1_1_2_11_r1`. All arms contains-noun. — follows from: faithful binding (NOUN); why the reduction reaches the catch-all is not determined

- 1.2.1.2 e732: record verified 3.1s -> contains-noun 0.3s | P0 core verified 3.6s top=1_2_1_9b_r29 | final30 contains-noun 0.4s top=1_1_2_7_r47
- 1.2.1.4 e404: record verified 3.9s -> contains-noun 0.4s | P0 core verified 3.7s top=1_2_1_9b_r29 | final30 contains-noun 0.3s top=1_1_2_7_r47

**class 1 g125** — deterministic, 2 entries — final contains-noun top=1_2_1_2_r117 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(d+ex)^3(quad)^p`. Both cores put r117 at top. **Nested.** P0 fell through. The substrate reaches `1_2_1_3_r112` (CATCH-1) → marker. **Corpus.** 3-step hypergeometric, no Unintegrable. All arms contains-noun. — follows from: faithful binding (NOUN)

- 1.2.1.2 e2092: record verified 3.6s -> contains-noun 1.1s | P0 core verified 3.7s top=1_2_1_2_r117 | final30 contains-noun 1.5s top=1_2_1_2_r117
- 1.2.1.2 e2563: record verified 3.2s -> contains-noun 0.9s | P0 core verified 3.6s top=1_2_1_2_r117 | final30 contains-noun 1.6s top=1_2_1_2_r117

**class 1 g126** — deterministic, 2 entries — final contains-noun top=1_2_1_3_r55 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(2-5x)/(x^(3/2)(…)^(3/2))`, `(2-5x)/((…)^(5/2)sqrt(x))`. As g94 with `1_2_1_3_r55` (+`r57`). All arms contains-noun. — follows from: faithful Optional binding

- 1.2.1.3 e1069: record verified 2.6s -> contains-noun 2.8s | P0 core verified 2.7s top=1_4_1_r34 | final30 contains-noun 2.9s top=1_2_1_3_r55
- 1.2.1.3 e1079: record verified 1.8s -> contains-noun 2.9s | P0 core verified 1.9s top=1_4_1_r34 | final30 contains-noun 2.8s top=1_2_1_3_r55

**class 1 g127** — deterministic, 2 entries — final contains-noun top=1_2_2_3_r22 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(1-2x^2)/(1±2x^2+4x^4)`. Both cores put r22 at top. **Nested.** P0 fell through. The substrate's quadratic sub-integrals bind `1_2_3_5_r24` (CATCH-1, through `x^n_.` n=1) → marker. **Arms.** r3 verified 1.4 s for e63 (as class 2 g9: the catch-all accepts only on a retried … — follows from: condition retry (e63); e59 not determined

- 1.2.2.3 e59: record verified 2.6s -> contains-noun 3.5s | P0 core verified 3.5s top=1_2_2_3_r22 | final30 contains-noun 4.0s top=1_2_2_3_r22
- 1.2.2.3 e63: record verified 2.8s -> contains-noun 4.0s | P0 core verified 3.6s top=1_2_2_3_r22 | final30 contains-noun 4.0s top=1_2_2_3_r22

**class 1 g128** — deterministic, 2 entries — final contains-noun top=1_2_2_3_r59 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(d+ex^2)/sqrt(a-cx^4)`, `/sqrt(-a+cx^4)`. Both cores put r59 at top. **Nested.** P0: the long elliptic chain. Substrate: `1_2_2_3_r100` (CATCH-1) → marker. **NegQ.** `NegQ[-c/a]` (and `c/(-a)`) is true in Rubi as well, so this is not tagged. All arms contains-noun. — follows from: not determined why r59's `mr_int((1+qx^2)/sqrt(a+cx^4))` reaches the catch-all

- 1.2.2.3 e159: record verified 1.1s -> contains-noun 0.4s | P0 core verified 1.4s top=1_2_2_3_r59 | final30 contains-noun 0.4s top=1_2_2_3_r59
- 1.2.2.3 e164: record verified 1.1s -> contains-noun 0.4s | P0 core verified 1.5s top=1_2_2_3_r59 | final30 contains-noun 0.4s top=1_2_2_3_r59

**class 1 g129** — deterministic, 2 entries — final contains-noun top=1_2_2_7_r17 — [group-level: negQ 2] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(A+Bx^2)/((d+ex^2)^k sqrt(a+cx^4))`. **Substrate.** `1_2_2_7_r17` (Rubi's binomial rule, q integer). Nested: `1_2_2_7_r37`, `1_2_2_3_r87`, `1_2_2_3_r59` (`%mr_negQ(c/a)` symbolic), `1_2_2_3_r100` (CATCH-1) → marker. **P0.** `1_2_2_7_r16`, the trinomial variant, with b bound to … — follows from: G-1 / faithful binding; the nested NegQ reading

- 1.2.2.7 e6: record verified 5.8s -> contains-noun 3.1s | P0 core verified 6.2s top=1_2_2_7_r16 | final30 contains-noun 4.0s top=1_2_2_7_r17
- 1.2.2.7 e7: record verified 7.6s -> contains-noun 7.2s | P0 core verified 7.9s top=1_2_2_7_r16 | final30 contains-noun 8.3s top=1_2_2_7_r17

**class 1 g130** — deterministic, 2 entries — final deferred top=1_1_1_3_r5 — [group-level: IGtQ 2] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md`: `x sqrt(a+bx)/(c+dx)^(5/2)`, `(A+Bx)(d+ex)^(7/2)/(a+bx)^(5/2)`. **Substrate.** `1_1_1_3_r5` (Rubi `… || IGtQ[p,0] && (…)`) accepts p = 1/2 / 7/2 through `is(p > 0)`: EXPAND-NOUN. **P0.** `1_1_1_3_r26` / `r6`. r3 verified 0.3 s for e2241. — follows from: faithful Optional binding (e581, x as (0+x)) / condition retry (e2241), exposing the IGtQ translation

- 1.1.1.3 e581: record verified 4.4s -> deferred 0.1s | P0 core verified 4.2s top=1_1_1_3_r26 | final30 deferred 0.2s top=1_1_1_3_r5
- 1.1.1.3 e2241: record verified 0.2s -> deferred 0.2s | P0 core verified 0.2s top=1_1_1_3_r6 | final30 deferred 0.2s top=1_1_1_3_r5

**class 1 g131** — deterministic, 2 entries — final deferred top=1_1_2_3_r11 — [group-level: IGtQ 2] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(a-bx^2)^(2/3 or 5/3)(3a+bx^2)`. **Substrate.** `1_1_2_3_r11` (Rubi `IGtQ[p,0] && IGtQ[q,0]`) binds q=1 through `q_.` and accepts p = 2/3, 5/3: EXPAND-NOUN. **P0.** `1_1_2_3_r20` after `1_1_2_1_r4`. All arms deferred. — follows from: faithful Optional binding exposing the IGtQ translation

- 1.1.2.3 e111: record verified 0.2s -> deferred 0.2s | P0 core verified 0.2s top=1_1_2_3_r20 | final30 deferred 0.1s top=1_1_2_3_r11
- 1.1.2.3 e118: record verified 0.2s -> deferred 0.2s | P0 core verified 0.2s top=1_1_2_3_r20 | final30 deferred 0.4s top=1_1_2_3_r11

**class 1 g132** — deterministic, 2 entries — final deferred top=1_1_2_6_r12 — [group-level: none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(ex)^m(A+Bx^2)/((a+bx^2)(c+dx^2))`, `(ex)^m(a+bx^2)^p(A+Bx^2)/(c+dx^2)`. Both cores put r12 (ExpandIntegrand) at top. **Nested.** P0's expansion dispatched (`1_1_2_3_r1, 1_4_1_r7`). The substrate has nfires=1: a top-level noun. All arms deferred. — follows from: not determined from the traces

- 1.1.2.6 e27: record verified 4.8s -> deferred 0.9s | P0 core verified 4.7s top=1_1_2_6_r12 | final30 deferred 1.3s top=1_1_2_6_r12
- 1.1.2.6 e47: record verified 9.7s -> deferred 1.2s | P0 core verified 9.5s top=1_1_2_6_r12 | final30 deferred 1.3s top=1_1_2_6_r12

**class 1 g133** — deterministic, 2 entries — final deferred top=1_1_2_8_r123 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: 1.2.1.3 e255 `(A+Bx)(a+cx^2)/x`, 1.3.1 e261 `(3+2x^2)/((-1+x)^2 x)`. **Substrate.** The catch-all `1_1_2_8_r123` (CATCH-1) binds `(a+bx^2)^p` with p=1 through `p_.` and answers at top level. **P0.** `1_2_1_9b_r32` / `1_1_2_8_r91`. **Rubi.** The 2-step reductions are not reached … — follows from: faithful Optional binding / G-1

- 1.2.1.3 e255: record verified 8.8s -> deferred 0.1s | P0 core verified 8.7s top=1_2_1_9b_r32 | final30 deferred 0.2s top=1_1_2_8_r123
- 1.3.1 e261: record verified 5.5s -> deferred 0.2s | P0 core verified 6.3s top=1_1_2_8_r91 | final30 deferred 0.3s top=1_1_2_8_r123

**class 1 g134** — deterministic, 2 entries — final deferred top=1_1_2_9_r19 — [group-level: none seen] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md`: `(A+Bx)(d+ex)^(m or 1+m)/(a+cx^2)`. **Substrate.** `1_1_2_9_r19` (IntegersQ[n], n=1 through `n_.`) expands a symbolic power, giving nfires=1 and a top-level noun. **P0.** `1_2_1_3b_r68`, whose 3-arg `%mr_expandIntegrand((d+ex)^m, (f+gx)/(quad))` dispatched. All arms deferred. — follows from: faithful Optional binding

- 1.2.1.3 e1490: record verified 3.6s -> deferred 0.2s | P0 core verified 4.9s top=1_2_1_3b_r68 | final30 deferred 0.3s top=1_1_2_9_r19
- 1.2.1.3 e1492: record verified 3.7s -> deferred 0.2s | P0 core verified 4.9s top=1_2_1_3b_r68 | final30 deferred 0.3s top=1_1_2_9_r19

**class 1 g135** — deterministic, 2 entries — final deferred top=1_1_3_4_r77 — [group-level: IGtQ 2] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(ex)^m/((a+bx^4)(c+dx^4)^(k/2))`. **Substrate.** `1_1_3_4_r77` (Rubi `IGtQ[p,-2] && (IGtQ[q,-2] || …)`) accepts q = -1/2, -3/2 through `is(q > -2)`: EXPAND-NOUN. **P0.** `1_4_2_r8` → `1_3_4_r3` (AppellF1). All arms deferred. — follows from: binding change exposing the IGtQ translation

- 1.1.3.4 e676: record verified 1.2s -> deferred 0.5s | P0 core verified 1.8s top=1_3_4_r3 | final30 deferred 0.5s top=1_1_3_4_r77
- 1.1.3.4 e682: record verified 1.2s -> deferred 0.5s | P0 core verified 1.7s top=1_3_4_r3 | final30 deferred 0.5s top=1_1_3_4_r77

**class 1 g136** — deterministic, 2 entries — final deferred top=1_1_3_6_r31 — [group-level: none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(ex)^m(A+Bx^n)/((a+bx^n)(c+dx^n))`, `(ex)^m(a+bx^n)^p(A+Bx^n)/(c+dx^n)`. **Substrate.** `1_1_3_6_r31` (ExpandIntegrand) answers alone with a top-level noun. **P0.** The manual 9.1 `u*(a*x^n)^m`. All arms deferred. — follows from: 9.1 regeneration; why the expansion yields no fire is not determined

- 1.1.3.6 e26: record verified 5.5s -> deferred 1.7s | P0 core verified 5.4s top=9_1_r16 | final30 deferred 1.3s top=1_1_3_6_r31
- 1.1.3.6 e43: record verified 5.5s -> deferred 1.8s | P0 core verified 5.4s top=9_1_r16 | final30 deferred 1.3s top=1_1_3_6_r31

**class 1 g137** — deterministic, 2 entries — final deferred top=1_1_3_7_r37 — [group-level: none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(c+dx)/sqrt(-a+bx^4)`, `(c+dx+ex^2+fx^3)(a+bx^4)^p`. **Substrate.** `1_1_3_7_r37` (n = 4, so IGtQ[2,0] holds) splits Pq with `mr_sum(lambda…)`; the split has no nested fire, giving a top-level noun. **P0.** `1_2_2_5_r3` (the same split for the quartic). All arms deferred. — follows from: faithful binding; why the `mr_sum` split yields no fire is not determined

- 1.1.3.8 e212: record verified 3.0s -> deferred 0.8s | P0 core verified 3.0s top=1_2_2_5_r3 | final30 deferred 0.5s top=1_1_3_7_r37
- 1.1.3.8 e552: record verified 2.2s -> deferred 1.2s | P0 core verified 2.1s top=1_2_2_5_r3 | final30 deferred 0.8s top=1_1_3_7_r37

**class 1 g138** — deterministic, 2 entries — final deferred top=1_2_2_3_r100 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(√a+x^2√c)/sqrt(-a+cx^4)`, `(1+x^2 sqrt(c/a))/sqrt(-a+cx^4)`. **Substrate.** `1_2_2_3_r100` (CATCH-1) answers at top level. **P0.** `1_2_2_3_r60` (trinomial) with b bound to 0 (DEG). **Rubi.** The 3-step elliptic_e rule is not reached; why is not determined. All arms deferred. — follows from: G-1

- 1.2.2.3 e166: record verified 0.7s -> deferred 0.1s | P0 core verified 0.9s top=1_2_2_3_r60 | final30 deferred 0.1s top=1_2_2_3_r100
- 1.2.2.3 e167: record verified 0.7s -> deferred 0.1s | P0 core verified 0.9s top=1_2_2_3_r60 | final30 deferred 0.1s top=1_2_2_3_r100

**class 1 g139** — deterministic, 2 entries — final deferred top=1_2_2_3_r12 — [group-level: IGtQ 2] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(2+3x^2)(5+x^4)^(1/2 or 3/2)`. **Substrate.** `1_2_2_3_r12` (Rubi `IGtQ[p,0] && IGtQ[q,-2]`) accepts p = 1/2, 3/2: EXPAND-NOUN. **P0.** `1_2_2_3_r34` (trinomial) with b=0 (DEG). All arms deferred. — follows from: G-1 exposing the IGtQ translation

- 1.2.2.4 e17: record verified 0.9s -> deferred 0.2s | P0 core verified 0.9s top=1_2_2_3_r34 | final30 deferred 0.1s top=1_2_2_3_r12
- 1.2.2.4 e29: record verified 1.1s -> deferred 0.2s | P0 core verified 1.0s top=1_2_2_3_r34 | final30 deferred 0.1s top=1_2_2_3_r12

**class 1 g140** — deterministic, 2 entries — final deferred top=1_2_3_2_r2 — [group-level: IGtQ 2] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(dx)^m(a+bx^n+cx^2n)^(3/2 or 1/2)`. **Substrate.** `1_2_3_2_r2` (Rubi `IGtQ[p,0]`) accepts p = 3/2, 1/2: EXPAND-NOUN. **P0.** The manual 9.1 `u*(a*x^n)^m`. All arms deferred. — follows from: 9.1 regeneration exposing the IGtQ translation

- 1.2.3.2 e602: record verified 4.2s -> deferred 0.2s | P0 core verified 5.8s top=9_1_r16 | final30 deferred 0.3s top=1_2_3_2_r2
- 1.2.3.2 e603: record verified 4.2s -> deferred 0.2s | P0 core verified 5.8s top=9_1_r16 | final30 deferred 0.3s top=1_2_3_2_r2

**class 1 g141** — deterministic, 2 entries — final deferred top=1_2_3_5_r24 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(1±x^4)/(1∓2x^4+x^8)`. **Substrate.** `1_2_3_5_r24` (CATCH-1) answers at top level. **P0.** `1_3_3_r10` (factor). **Arms.** r3 verified 0.3 s: the catch-all accepts only on a retried binding (as class 2 g9). — follows from: condition retry

- 1.2.3.3 e15: record verified 0.9s -> deferred 0.5s | P0 core verified 1.3s top=1_3_3_r10 | final30 deferred 0.7s top=1_2_3_5_r24
- 1.2.3.3 e22: record verified 1.0s -> deferred 0.5s | P0 core verified 1.4s top=1_3_3_r10 | final30 deferred 0.8s top=1_2_3_5_r24

**class 1 g142** — deterministic, 2 entries — final deferred top=1_3_4_r3 — [group-level: none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(a+bx)^n(c+dx)^p/x`, `(a+bx)^m(c+dx)^(-1-m)(e+fx)^p`. **Substrate.** `1_3_4_r3` answers alone in 8.8–10.6 s with a top-level noun; its substitution has no nested fire. **P0.** `1_1_1_6_r7` alone. The corpus's 2–3-step AppellF1 rules are not reached. **Arms.** r3 deferred … — follows from: not determined from the traces

- 1.1.1.3 e949: record verified 3.8s -> deferred 8.8s | P0 core verified 3.9s top=1_1_1_6_r7 | final30 deferred 9.0s top=1_3_4_r3
- 1.1.1.3 e3058: record verified 5.2s -> deferred 10.2s | P0 core verified 5.1s top=1_1_1_6_r7 | final30 deferred 10.6s top=1_3_4_r3

**class 1 g143** — deterministic, 2 entries — final error top=- — [group-level: none seen] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md`: `(b+2cx+3dx^2)(bx+cx^2+dx^3)^7`, `x^7(b+cx+dx^2)^7(b+2cx+3dx^2)` (1-step derivative-divides). **Death.** No fire; error at 9.1 / 9.7 s (record), 16.0 / 15.5 s (final30), 8.7 / 9.2 s (newerror). The kind is not recorded. **P0.** Verified through `1_4_1_r20` / `1_2_1_6_r1`. … — follows from: condition retry

- 1.3.1 e193: record verified 0.5s -> error 9.1s | P0 core verified 0.5s top=1_4_1_r20 | final30 error 16.0s top=-
- 1.3.1 e194: record verified 0.9s -> error 9.7s | P0 core verified 0.9s top=1_2_1_6_r1 | final30 error 15.5s top=-

**class 1 g144** — deterministic, 2 entries — final timeout top=1_1_1_2_r32 — [group-level: IGtQ 2; negQ 2 (both 2)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/(x(a±bx^4)^(3/4))`. **Substrate nested.** `1_1_1_2_r32` (the t^4 linear-pair substitution) → PF-EVEN `1_1_3_1_r14` on n = 4 with symbolic a. The top-level x^4 substitution fire is absent at 30 s and 120 s. **P0.** `1_2_2_2_r8`, with a nested r32 that led to `1_1_2_2_r4`. … — follows from: condition retry (e1237) exposing IGtQ and NegQ

- 1.1.3.2 e1113: record verified 0.6s -> timeout 30.1s | P0 core verified 0.6s top=1_2_2_2_r8 | final30 timeout 30.1s top=1_1_1_2_r32 | final120 timeout 120.2s top=1_1_1_2_r32
- 1.1.3.2 e1237: record verified 0.7s -> timeout 30.1s | P0 core verified 0.6s top=1_2_2_2_r8 | final30 timeout 30.1s top=1_1_1_2_r32 | final120 timeout 120.2s top=1_1_1_2_r32

**class 1 g145** — deterministic, 2 entries — final timeout top=1_1_1_3_r15 — [group-level: IGtQ 2] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/(x(2-3x^2)^(3/4)(4-3x^2))`, `1/(x(-2+3x^2)(-1+3x^2)^(3/4))`. **Substrate nested.** `1_1_1_2_r32/r13` → PF-EVEN `1_1_3_1_r14` / `r13` on n = 4. The coefficients are numeric, so NegQ reads exactly. The top-level fire is absent. **P0.** `1_1_2_4_r20` at top, verified 0.2 / 1.3 … — follows from: condition retry (e1085) exposing the IGtQ translation

- 1.1.2.4 e1065: record verified 0.2s -> timeout 30.1s | P0 core verified 0.2s top=1_1_2_4_r20 | final30 timeout 30.1s top=1_1_1_3_r15 | final120 timeout 120.1s top=1_1_1_3_r15
- 1.1.2.4 e1085: record verified 1.0s -> timeout 30.0s | P0 core verified 1.3s top=1_1_2_4_r20 | final30 timeout 30.1s top=1_1_1_3_r15 | final120 timeout 120.2s top=1_1_1_3_r15

**class 1 g146** — deterministic, 2 entries — final timeout top=1_1_1_3_r6 — [group-level: IGtQ 2] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md`: `(A+Bx)sqrt(a+bx)/(d+ex)^(5/2)` and its mirror. Both cores put r6 at top (fired at 30 s: VERIFY-TIMEOUT). **Nested.** P0: `1_1_1_2_r12`. Substrate: `1_1_1_2_r10` (Rubi `ILtQ[m,-1] && Not[IntegerQ[n]] && GtQ[n,0]`), which accepts m = -3/2 through `is(m < -1)`, then `1_1_1_2_r23` … — follows from: condition retry + model flags, exposing the ILtQ translation

- 1.1.1.3 e2193: record verified 2.1s -> timeout 30.0s | P0 core verified 2.5s top=1_1_1_3_r6 | final30 timeout 30.1s top=1_1_1_3_r6 | final120 timeout 120.2s top=1_1_1_3_r6
- 1.1.1.3 e2244: record verified 0.1s -> timeout 30.1s | P0 core verified 0.1s top=1_1_1_3_r6 | final30 timeout 30.1s top=1_1_1_3_r6 | final120 timeout 120.2s top=1_1_1_3_r6

**class 1 g147** — deterministic, 2 entries — final timeout top=1_1_3_1_r13 — [group-level: IGtQ 2] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/(2+3x^4)`, `1/(1+x^6)`. **Top level.** `1_1_3_1_r13` (Rubi `IGtQ[(n-3)/2,0] && PosQ[a/b]`, odd n) accepts n = 4, 6 ((n-3)/2 = 1/2, 3/2) and fired in the 30 s list, so rubi returned. **P0.** Rubi's n = 4 rule `1_1_3_1_r23` (it sits after r13) / `1_4_1_r23`. All arms timeout. — follows from: faithful binding (P0's r13 literal did not bind) exposing the IGtQ translation

- 1.1.3.2 e695: record verified 6.4s -> timeout 30.0s | P0 core verified 6.3s top=1_1_3_1_r23 | final30 timeout 30.0s top=1_1_3_1_r13 | final120 timeout 120.1s top=1_1_3_1_r13
- 1.1.3.2 e1367: record verified 0.6s -> timeout 30.0s | P0 core verified 0.6s top=1_4_1_r23 | final30 timeout 30.0s top=1_1_3_1_r13 | final120 unverified 114.1s top=1_1_3_1_r13

**class 1 g148** — deterministic, 2 entries — final timeout top=1_1_3_3_r14 — [group-level: IGtQ 2; negQ 2 (both 2)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(a+bx^4)/(c+dx^4)^k`, k = 2, 3. **Substrate.** The top-level `1_1_3_3_r14` (no P0 defmatch record) fired. Nested: `1_1_3_1_r4` (ILtQ on -3/4) and PF-EVEN `1_1_3_1_r14` (n = 4, symbolic). **P0.** `1_1_3_3_r60` alone. VERIFY-TIMEOUT; all arms timeout. — follows from: faithful binding exposing IGtQ and NegQ

- 1.1.3.3 e52: record verified 0.3s -> timeout 30.0s | P0 core verified 0.3s top=1_1_3_3_r60 | final30 timeout 30.1s top=1_1_3_3_r14 | final120 timeout 120.1s top=1_1_3_3_r14
- 1.1.3.3 e53: record verified 0.3s -> timeout 30.1s | P0 core verified 0.3s top=1_1_3_3_r60 | final30 timeout 30.1s top=1_1_3_3_r14 | final120 timeout 120.2s top=1_1_3_3_r14

**class 1 g149** — deterministic, 2 entries — final timeout top=1_1_3_4_r11 — [group-level: none seen] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/(x^k sqrt(a+bx^3)sqrt(c+dx^3))`. **Substrate.** The top-level x^3 substitution `1_1_3_4_r11` fired → `1_1_1_3_r22` (+`r25`) → `1_1_2_1_r15` (atanh; the corpus's own form). **P0.** `1_3_4_r3` alone. VERIFY-TIMEOUT; all arms timeout. — follows from: faithful binding; the cost is verification

- 1.1.3.4 e508: record verified 1.0s -> timeout 30.1s | P0 core verified 1.0s top=1_3_4_r3 | final30 timeout 30.1s top=1_1_3_4_r11 | final120 timeout 120.2s top=1_1_3_4_r11
- 1.1.3.4 e509: record verified 1.1s -> timeout 30.0s | P0 core verified 1.1s top=1_3_4_r3 | final30 timeout 30.1s top=1_1_3_4_r11 | final120 timeout 120.2s top=1_1_3_4_r11

**class 1 g150** — deterministic, 2 entries — final timeout top=1_2_1_2_r111 — [group-level: IGtQ 2] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md`: `(d+ex)^(3/2 or 1/2)/(quad)^(5/2)`. Both cores put r111 at top (fired at 30 s: VERIFY-TIMEOUT). **Nested.** P0: `1_2_1_9b_r5` only. Substrate: `1_1_2_3_r48`, `1_2_1_2_r93`, `1_2_1_9b_r5/r32`, `1_2_1_3_r54/r55`. **IGT (inferred).** `9b_r5` accepts the reduced p = -3/2 through … — follows from: faithful binding

- 1.2.1.2 e2478: record verified 2.9s -> timeout 30.0s | P0 core verified 2.9s top=1_2_1_2_r111 | final30 timeout 30.0s top=1_2_1_2_r111 | final120 timeout 120.1s top=1_2_1_2_r111
- 1.2.1.2 e2479: record verified 3.0s -> timeout 30.0s | P0 core verified 3.0s top=1_2_1_2_r111 | final30 timeout 30.0s top=1_2_1_2_r111 | final120 timeout 120.1s top=1_2_1_2_r111

**class 1 g151** — deterministic, 2 entries — final timeout top=1_2_1_2_r93 — [group-level: none seen] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/(sqrt(d+ex)sqrt(quad))`, `1/(sqrt(f+gx)sqrt(quad))`. **Substrate.** The top-level `1_2_1_2_r93` (elliptic substitution) fired after `1_1_2_3_r42`. **P0.** `1_2_1_4_r30` after `1_1_1_3_r55`. VERIFY-TIMEOUT; all arms timeout. — follows from: faithful binding

- 1.2.1.2 e2465: record verified 0.5s -> timeout 30.0s | P0 core verified 0.5s top=1_2_1_4_r30 | final30 timeout 30.0s top=1_2_1_2_r93 | final120 timeout 120.1s top=1_2_1_2_r93
- 1.2.1.4 e912: record verified 0.5s -> timeout 30.0s | P0 core verified 0.5s top=1_2_1_4_r30 | final30 timeout 30.0s top=1_2_1_2_r93 | final120 timeout 120.1s top=1_2_1_2_r93

**class 1 g152** — deterministic, 2 entries — final timeout top=1_2_1_3_r55 — [group-level: none seen] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md`: **e1647.** Both cores put r55 at top. Nested: P0 `9b_r5/9b_r1`; substrate the elliptic chain (`1_1_2_3_r48`, `1_2_1_2_r93`, `9_1_r8`, `1_2_1_9b_r32`, `1_4_1_r18`). The top-level fire is at 30 s. **e130** `(A+Bx^2)/(x(quartic)^3)`. P0: `1_2_2_6_r2` alone. At 30 s the substrate … — follows from: faithful binding; the cost is verification

- 1.2.1.3 e1647: record verified 4.4s -> timeout 30.0s | P0 core verified 4.2s top=1_2_1_3_r55 | final30 timeout 30.1s top=1_2_1_3_r55 | final120 timeout 120.1s top=1_2_1_3_r55
- 1.2.2.4 e130: record verified 3.3s -> timeout 30.0s | P0 core verified 3.3s top=1_2_2_6_r2 | final30 timeout 30.0s top=1_2_1_3_r55 | final120 timeout 120.1s top=1_2_2_4_r9

**class 1 g153** — deterministic, 2 entries — final timeout top=1_2_1_3_r90 — [group-level: none seen] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md`: `sqrt(ade+…)/(x(d+ex))`, `(…)^(3/2)/(x(d+ex))`. Both cores put r90 at top (fired at 30 s). **Nested.** P0: `1_2_1_1_r3, 1_2_1_2_r99` / `1_4_2_r25, 1_3_3_r6`. Substrate: `1_1_2_1_r13`, `1_2_1_2_r99`, `1_2_1_1_r15`, `1_2_1_3_r1` (+`r89`, `1_2_1_2_r109`, `1_1_1_4_r46` … — follows from: not determined which change moves the nested chain

- 1.2.1.4 e441: record verified 2.9s -> timeout 30.1s | P0 core verified 2.9s top=1_2_1_3_r90 | final30 timeout 30.0s top=1_2_1_3_r90 | final120 timeout 120.1s top=1_2_1_3_r90
- 1.2.1.4 e450: record verified 4.8s -> timeout 30.0s | P0 core verified 4.8s top=1_2_1_3_r90 | final30 timeout 30.0s top=1_2_1_3_r90 | final120 timeout 120.1s top=1_2_1_3_r90

**class 1 g154** — deterministic, 2 entries — final timeout top=1_2_1_5_r26 — [group-level: none seen] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md`: `x(quad)^(k/2)/(d-fx^2)`. **Substrate.** The top-level `1_2_1_5_r26` binds g=0 through `g_.` (P0 literal `(a+b*x+c*x^2)^p*(d+f*x^2)^q*(g+h*x)`); nested `1_4_1_r18`. **P0.** `1_4_2_r17` alone. VERIFY-TIMEOUT; all arms timeout. — follows from: faithful Optional binding

- 1.2.1.6 e79: record verified 4.6s -> timeout 30.0s | P0 core verified 4.7s top=1_4_2_r17 | final30 timeout 30.1s top=1_2_1_5_r26 | final120 timeout 120.1s top=1_2_1_5_r26
- 1.2.1.6 e86: record verified 4.3s -> timeout 30.0s | P0 core verified 4.7s top=1_4_2_r17 | final30 timeout 30.0s top=1_2_1_5_r26 | final120 timeout 120.1s top=1_2_1_5_r26

**class 1 g155** — deterministic, 2 entries — final timeout top=1_2_2_1_r5 — [group-level: negQ 2] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/(a+b(d+ex)^2+c(d+ex)^4)^k`, k = 2, 3. **Substrate.** The g85 chain (`1_2_2_3_r27` NegQ branch) ending in `1_2_2_1_r5`. **P0.** `1_4_2_r18` alone. e634: r2/r4 error 24–25 s. — follows from: as g85

- 1.2.3.2 e625: record verified 0.7s -> timeout 30.1s | P0 core verified 0.9s top=1_4_2_r18 | final30 timeout 30.1s top=1_2_2_1_r5 | final120 error 85.8s top=1_2_2_1_r5
- 1.2.3.2 e634: record verified 0.7s -> timeout 30.1s | P0 core verified 0.9s top=1_4_2_r18 | final30 timeout 30.1s top=1_2_2_1_r5 | final120 timeout 120.3s top=1_2_2_1_r5

**class 1 g156** — deterministic, 2 entries — final timeout top=1_2_2_1_r7 — [group-level: negQ 2] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/(sqrt(d+ex)(quad))`, `(b+2cx)sqrt(d+ex)/(quad)^2`. **Both cores.** Both run the nested `1_2_1_1_r12`, `1_2_1_2_r3/r9` and `1_2_2_1_r7`. r7 is Rubi's `NegQ[b^2-4*a*c]` split; the corpus answers are the real-root atanh(√2√c√(d+ex)/√(2cd-e(b-√…))) form. **P0.** Went on to the … — follows from: not determined from the traces; the NegQ branch is on both cores' routes

- 1.2.1.2 e2292: record verified 2.9s -> timeout 30.1s | P0 core verified 2.8s top=1_2_1_2_r82 | final30 timeout 30.1s top=1_2_2_1_r7 | final120 timeout 120.2s top=1_2_2_1_r7
- 1.2.1.3 e1620: record verified 4.9s -> timeout 30.1s | P0 core verified 6.8s top=1_2_1_3_r42 | final30 timeout 30.1s top=1_2_2_1_r7 | final120 timeout 120.2s top=1_2_2_1_r7

**class 1 g157** — deterministic, 2 entries — final timeout top=1_2_2_2_r16 — [group-level: negQ 2] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `(d+ex)^4/(a+b(d+ex)^2+c(d+ex)^4)` (and the f-scaled form). The g85 chain with `1_2_2_2_r16`. r3 error 27.3 / 28.7 s. — follows from: as g85

- 1.2.3.2 e613: record verified 0.6s -> timeout 30.1s | P0 core verified 0.9s top=1_4_2_r24 | final30 timeout 30.1s top=1_2_2_2_r16 | final120 error 95.1s top=1_2_2_2_r16
- 1.2.3.2 e638: record verified 0.6s -> timeout 30.1s | P0 core verified 0.9s top=1_4_2_r24 | final30 timeout 30.1s top=1_2_2_2_r16 | final120 error 94.5s top=1_2_2_2_r16

**class 1 g158** — deterministic, 2 entries — final timeout top=1_2_2_6_r1 — [group-level: none seen] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md`: **e30** `x^3(A+Bx+Cx^2)/(quartic)^2`. P0 answered with `1_2_2_5_r3` at top after a long chain. On the substrate `1_2_2_6_r1` (d=1 through `d_.`) answers, with nested `1_1_2_1_r13, 1_2_1_1_r12, 1_2_1_3_r44, 1_2_2_4_r9, 1_4_1_r18`. r3 CN 12.2 s. **e40** … — follows from: faithful Optional binding (e30); not determined (e40)

- 1.2.2.6 e30: record verified 5.2s -> timeout 30.0s | P0 core verified 5.6s top=1_2_2_5_r3 | final30 timeout 30.0s top=1_2_2_6_r1 | final120 timeout 120.1s top=1_2_2_6_r1
- 1.2.2.6 e40: record verified 21.0s -> timeout 30.1s | P0 core verified 26.4s top=1_2_2_6_r1 | final30 timeout 30.1s top=1_2_2_6_r1 | final120 timeout 120.1s top=1_2_2_6_r1

**class 1 g159** — deterministic, 2 entries — final timeout top=1_2_3_1_r6 — [group-level: negQ 2] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/(sqrt(x)(a+bx^2+cx^4)^k)`, k = 2, 3. **Substrate nested.** The prefix, `1_2_2_3_r27` and `1_2_3_3_r33` (both `NegQ[b^2-4*a*c]`), `r40`, `1_2_3_1_r6`. The top-level sqrt(x) substitution fire is absent. **Corpus.** `(-b-sqrt(b^2-4*a*c))^(1/4)` forms: the other branch. **P0.** … — follows from: not determined which change routes the substituted integrand; the NegQ reading

- 1.2.2.2 e1078: record verified 2.3s -> timeout 30.1s | P0 core verified 2.2s top=1_4_1_r34 | final30 timeout 30.0s top=1_2_3_1_r6 | final120 timeout 120.1s top=1_2_3_1_r6
- 1.2.2.2 e1088: record verified 2.3s -> timeout 30.0s | P0 core verified 2.2s top=1_4_1_r34 | final30 timeout 30.0s top=1_2_3_1_r6 | final120 timeout 120.1s top=1_2_3_1_r6

**class 1 g160** — deterministic, 2 entries — final timeout top=1_2_3_2_r17 — [group-level: IGtQ 2] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/(x^k(1-3x^4+x^8))`, k = 3, 7. **Substrate.** The top-level `1_2_3_2_r17` fired → `1_2_3_4_r49` (+`r43`) partial fractions → PF-EVEN `1_1_3_2_r36` on n = 4 (numeric) + prefix. **P0.** `1_3_3_r10` alone. **Arms.** r3 deferred 0.4 s; r2/r4 timeout. — follows from: faithful binding exposing the IGtQ translation

- 1.2.3.2 e393: record verified 1.7s -> timeout 30.1s | P0 core verified 1.7s top=1_3_3_r10 | final30 timeout 30.1s top=1_2_3_2_r17 | final120 timeout 120.2s top=1_2_3_2_r17
- 1.2.3.2 e395: record verified 1.7s -> timeout 30.1s | P0 core verified 1.7s top=1_3_3_r10 | final30 timeout 30.1s top=1_2_3_2_r17 | final120 timeout 120.3s top=1_2_3_2_r17

**class 1 g161** — deterministic, 2 entries — final timeout top=1_4_2_r26 — [group-level: none seen] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g161, g242, g243): `1/(sqrt(x)sqrt(x(a+bx+cx^2)))`, `…(a+bx^2+cx^4)`, `sqrt(x)/sqrt(x^3(…))`. **Substrate.** `1_4_2_r26/r27` (expandToSum of the generalized trinomial) → `1_2_4_1_r4` / `1_2_4_2_r3`, `1_1_2_1_r13`. The top-level `1_4_1_r34` fires by 30 s (g242) or by 120 s (g161, g243). **P0.** … — follows from: model flags

- 1.2.4.2 e131: record verified 1.0s -> timeout 30.0s | P0 core verified 1.5s top=1_4_1_r34 | final30 timeout 30.1s top=1_4_2_r26 | final120 timeout 120.1s top=1_4_1_r34
- 1.2.4.2 e135: record verified 1.0s -> timeout 30.0s | P0 core verified 1.4s top=1_4_1_r34 | final30 timeout 30.1s top=1_4_2_r26 | final120 timeout 120.1s top=1_4_1_r34

**class 1 g162** — deterministic, 2 entries — final timeout top=9_1_r8 — [group-level: none seen] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/((quad)sqrt(1-dx)sqrt(1+dx))`, `1/((d+ex+fx^2)sqrt(a+cx^2))`. **Fires.** Only `9_1_r8` (the constant rule; not a collapse rule) at 30 s and 120 s. **P0.** `1_2_1_4_r24` (+`1_2_1_3_r8`). **Arms.** e795 r4 verified 1.6 s (MFLAGS); e67 timeout in all arms. **Reading.** Either … — follows from: model flags (e795); not determined (e67)

- 1.2.1.4 e795: record verified 4.4s -> timeout 30.0s | P0 core verified 5.0s top=1_2_1_3_r8 | final30 timeout 30.0s top=9_1_r8 | final120 timeout 120.1s top=9_1_r8
- 1.2.1.6 e67: record verified 2.6s -> timeout 30.0s | P0 core verified 2.7s top=1_2_1_4_r24 | final30 timeout 30.0s top=9_1_r8 | final120 timeout 120.1s top=9_1_r8

**class 1 g163** — deterministic, 2 entries — final unexpected top=1_3_3_r17 — [group-level: none seen] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `F(x)sqrt(x-x^2)`, `F(x)/sqrt(x-x^2)`; noun-expected (CannotIntegrate, 0 steps). **P0.** No-answer. **Substrate.** `1_3_3_r17` removes the x content, and its nested integral has no fire. Maxima integrate then returns an answer that differentiates back (self=1): unexpected, a … — follows from: not determined from the traces (P0's r17 literal / its moved `ExponMin` test)

- 1.3.2 e758: record no-answer 0.5s -> unexpected 1.0s | P0 core no-answer 0.8s top=1_2_3_5_r25 | final30 unexpected 1.3s top=1_3_3_r17
- 1.3.2 e759: record no-answer 0.5s -> unexpected 1.0s | P0 core no-answer 0.8s top=1_2_3_5_r25 | final30 unexpected 1.4s top=1_3_3_r17

**class 1 g164** — deterministic, 2 entries — final unverified top=1_1_1_3_r61 — [group-level: none seen] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md`: `(1-x)^n/(x^2(1+x)^n)`, `(a+bx)^m(c+dx)^(-1-m)/(e+fx)`. **Substrate.** `1_1_1_3_r61` (hypergeometric closed form; x^-2 as (0+x)^-2) answers at top: the corpus's own 1-step form, not closed by the zero chain. **P0.** `1_1_1_6_r7`. All arms unverified. — follows from: faithful Optional binding

- 1.1.1.3 e971: record verified 3.1s -> unverified 0.3s | P0 core verified 3.0s top=1_1_1_6_r7 | final30 unverified 0.4s top=1_1_1_3_r61
- 1.1.1.3 e3063: record verified 4.5s -> unverified 12.9s | P0 core verified 4.4s top=1_1_1_6_r7 | final30 unverified 13.5s top=1_1_1_3_r61

**class 1 g165** — deterministic, 2 entries — final unverified top=1_1_2_7_r56 — [group-level: negQ 2] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `(a+cx^2)^p/(d+ex)^2`, `(a+bx^2)^p/(d+ex)^2`. Both cores put r56 at top. **NegQ.** r56 is Rubi `ILtQ[n,-1] && NegQ[a/b]`; symbolic a/c reads NegQ on both cores. **Nested.** P0: `1_1_1_4_r47`. Substrate: `1_1_1_3_r65` (AppellF1). **Result.** AppellF1, unverified. All arms … — follows from: not determined from the traces

- 1.2.1.2 e737: record verified 2.0s -> unverified 2.7s | P0 core verified 2.1s top=1_1_2_7_r56 | final30 unverified 3.5s top=1_1_2_7_r56
- 1.2.1.4 e420: record verified 2.1s -> unverified 7.7s | P0 core verified 2.1s top=1_1_2_7_r56 | final30 unverified 6.9s top=1_1_2_7_r56

**class 1 g166** — deterministic, 2 entries — final unverified top=1_1_2_8_r12 — [group-level: none seen] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g166, g167): `x^2(d+ex)/(d^2-e^2x^2)^(3/2)`, `x^2/((d+ex)sqrt(d^2-e^2x^2))` (+ the a-forms). **Substrate.** Rubi's `1_1_2_8_r12/r48` (integer m, n) bind; nested `1_1_3_2_r115`, `1_1_2_2_r2`. **P0.** `1_2_1_3b_r35` / `1_1_2_8_r90`. **Arms.** r3 verified 0.3–0.4 s in all four entries. — follows from: condition retry

- 1.2.1.4 e17: record verified 0.6s -> unverified 0.5s | P0 core verified 0.5s top=1_2_1_3b_r35 | final30 unverified 0.3s top=1_1_2_8_r12
- 1.2.1.4 e32: record verified 0.5s -> unverified 0.3s | P0 core verified 0.5s top=1_2_1_3b_r35 | final30 unverified 0.3s top=1_1_2_8_r12

**class 1 g167** — deterministic, 2 entries — final unverified top=1_1_2_8_r48 — [group-level: none seen] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g166, g167): `x^2(d+ex)/(d^2-e^2x^2)^(3/2)`, `x^2/((d+ex)sqrt(d^2-e^2x^2))` (+ the a-forms). **Substrate.** Rubi's `1_1_2_8_r12/r48` (integer m, n) bind; nested `1_1_3_2_r115`, `1_1_2_2_r2`. **P0.** `1_2_1_3b_r35` / `1_1_2_8_r90`. **Arms.** r3 verified 0.3–0.4 s in all four entries. — follows from: condition retry

- 1.2.1.4 e121: record verified 0.8s -> unverified 0.7s | P0 core verified 0.8s top=1_1_2_8_r90 | final30 unverified 0.4s top=1_1_2_8_r48
- 1.2.1.4 e151: record verified 0.8s -> unverified 0.7s | P0 core verified 0.8s top=1_1_2_8_r90 | final30 unverified 0.4s top=1_1_2_8_r48

**class 1 g168** — deterministic, 2 entries — final unverified top=1_1_3_2_r107 — [group-level: IGtQ 1; none seen 1] [ZERO]
> `10-p5-attribution.mechanisms-class1-c.md`: **e2762** `(cx)^(-1-3n/2)/(a+bx^n)`. The hypergeometric catch-all r107 (p=-1) answers at top; P0 `1_1_3_2_r110`. **e1024** `x/sqrt(2+2a-2(1+a)+cx^4)` (ZERO). r107 accepts p=-1/2 through `is(p < 0)`, where Rubi needs ILtQ or GtQ[a,0], with a the zero form. P0 `1_2_2_6_r2`. All … — follows from: not determined (e2762); binding change exposing the ILtQ translation (e1024)

- 1.1.3.2 e2762: record verified 1.2s -> unverified 0.1s | P0 core verified 1.7s top=1_1_3_2_r110 | final30 unverified 0.2s top=1_1_3_2_r107
- 1.2.2.2 e1024: record verified 2.5s -> unverified 0.1s | P0 core verified 2.4s top=1_2_2_6_r2 | final30 unverified 0.2s top=1_1_3_2_r107

**class 1 g169** — deterministic, 2 entries — final unverified top=1_1_4_1_r1 — [group-level: MUL 2] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g169, g279): `sqrt(1/x+sqrt(1/x))`, `(ax^m+bx^(1+m+mp))^p`, `(x^m(a+bx^(1+mp)))^p`. **Substrate.** `1_1_4_1_r1` answers (at top, or nested under `1_4_2_r11`). Its repl `b*(n - j) (p + 1)*x^(n - 1)` lacks a `*` (MUL), so the answer cannot equal Rubi's. **P0.** `1_2_3_1_r2` / `1_1_4_4_r11` / … — follows from: faithful binding reaching a repl with the MUL translation defect

- 1.1.3.2 e3061: record verified 1.6s -> unverified 0.2s | P0 core verified 1.7s top=1_2_3_1_r2 | final30 unverified 0.1s top=1_1_4_1_r1
- 1.1.4.2 e444: record verified 0.9s -> unverified 0.1s | P0 core verified 0.9s top=1_1_4_4_r11 | final30 unverified 0.2s top=1_1_4_1_r1

**class 1 g170** — deterministic, 2 entries — final unverified top=1_2_2_2_r17 — [group-level: IGtQ 2] [ZERO]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/(x^k sqrt(2+2a-2(1+a)+bx^2+cx^4))`, k = 2, 4 (ZERO). **Substrate nested.** `1_1_4_4_r10`, `1_2_2_6_r3` (Rubi `IGtQ[p,-2]`; accepts p=-1/2 through `is(p > -2)`), `1_2_2_4_r39`, top r17. **P0.** `1_3_3_r17`. All arms unverified. — follows from: binding change on the zero-form coefficient exposing the IGtQ translation

- 1.2.2.2 e1000: record verified 5.5s -> unverified 2.2s | P0 core verified 5.4s top=1_3_3_r17 | final30 unverified 2.7s top=1_2_2_2_r17
- 1.2.2.2 e1002: record verified 5.5s -> unverified 2.8s | P0 core verified 5.5s top=1_3_3_r17 | final30 unverified 3.0s top=1_2_2_2_r17

**class 1 g171** — deterministic, 2 entries — final unverified top=1_2_3_1_r4 — [group-level: IGtQ 2] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/(1±2x^4+x^8)`. **Substrate.** The top-level `1_2_3_1_r4` (perfect square → `1/(1±x^4)^2`) → `1_1_3_1_r4` (ILtQ on -3/4) → PF-EVEN `1_1_3_1_r13/r14` on n = 4 (numeric). **P0.** `1_3_3_r10`. r3 verified 0.2 s. — follows from: condition retry exposing the IGtQ translation

- 1.2.3.2 e285: record verified 1.6s -> unverified 3.7s | P0 core verified 1.5s top=1_3_3_r10 | final30 unverified 4.0s top=1_2_3_1_r4
- 1.2.3.2 e304: record verified 1.4s -> unverified 2.0s | P0 core verified 1.4s top=1_3_3_r10 | final30 unverified 2.2s top=1_2_3_1_r4

**class 1 g172** — deterministic, 1 entries — final contains-noun top=1_1_1_3_r13 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g172, g173, g175): `(c+dx)^3/(x(a+bx))`, `(a+bx)^n(c+dx^3)/x`, `x^7(quartic)^p`. Each has the same top rule on both cores. **P0.** Fell through (nfires=1). **Substrate.** The nested integral reaches CATCH-1: `1_1_1_4_r42`, `1_1_2_8_r123`, and `1_2_1_2_r117` → `1_2_1_3_r112` → marker. All arms … — follows from: faithful binding (NOUN)

- 1.1.1.3 e195: record verified 1.8s -> contains-noun 0.4s | P0 core verified 1.8s top=1_1_1_3_r13 | final30 contains-noun 0.2s top=1_1_1_3_r13

**class 1 g173** — deterministic, 1 entries — final contains-noun top=1_1_1_5_r8 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g172, g173, g175): `(c+dx)^3/(x(a+bx))`, `(a+bx)^n(c+dx^3)/x`, `x^7(quartic)^p`. Each has the same top rule on both cores. **P0.** Fell through (nfires=1). **Substrate.** The nested integral reaches CATCH-1: `1_1_1_4_r42`, `1_1_2_8_r123`, and `1_2_1_2_r117` → `1_2_1_3_r112` → marker. All arms … — follows from: faithful binding (NOUN)

- 1.3.2 e154: record verified 3.0s -> contains-noun 1.0s | P0 core verified 2.9s top=1_1_1_5_r8 | final30 contains-noun 1.4s top=1_1_1_5_r8

**class 1 g174** — deterministic, 1 entries — final contains-noun top=1_2_1_3_r57 — [group-level: none seen] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md`: `(2-5x)/(x^(5/2)sqrt(2+5x+3x^2))`. As g94 with r57. — follows from: faithful Optional binding

- 1.2.1.3 e1062: record verified 2.9s -> contains-noun 2.8s | P0 core verified 2.8s top=1_4_1_r34 | final30 contains-noun 3.0s top=1_2_1_3_r57

**class 1 g175** — deterministic, 1 entries — final contains-noun top=1_2_2_2_r8 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g172, g173, g175): `(c+dx)^3/(x(a+bx))`, `(a+bx)^n(c+dx^3)/x`, `x^7(quartic)^p`. Each has the same top rule on both cores. **P0.** Fell through (nfires=1). **Substrate.** The nested integral reaches CATCH-1: `1_1_1_4_r42`, `1_1_2_8_r123`, and `1_2_1_2_r117` → `1_2_1_3_r112` → marker. All arms … — follows from: faithful binding (NOUN)

- 1.2.2.2 e1115: record verified 2.5s -> contains-noun 0.9s | P0 core verified 2.4s top=1_2_2_2_r8 | final30 contains-noun 1.0s top=1_2_2_2_r8

**class 1 g176** — deterministic, 1 entries — final contains-noun top=1_2_2_3_r23 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(2-3x^2)/(4+9x^4)`. **Substrate.** `1_2_2_3_r23` (binomial form; NegQ[de] numeric) replaces P0's `1_2_2_3_r22`, which bound b=0 (DEG). Nested `1_2_3_5_r24` (CATCH-1) → marker, as g127. All arms contains-noun. — follows from: G-1 (NOUN)

- 1.2.2.3 e6: record verified 3.6s -> contains-noun 4.2s | P0 core verified 3.8s top=1_2_2_3_r22 | final30 contains-noun 4.3s top=1_2_2_3_r23

**class 1 g177** — deterministic, 1 entries — final contains-noun top=1_2_2_3_r64 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(c+ex^2)^3(a+cx^2+bx^4)^p`. Both cores put r64 at top. **Nested.** Substrate: `1_2_3_5_r24` (CATCH-1) → marker. **Arms.** r3 verified 1.3 s. — follows from: condition retry

- 1.2.2.3 e400: record verified 2.7s -> contains-noun 12.9s | P0 core verified 3.7s top=1_2_2_3_r64 | final30 contains-noun 14.4s top=1_2_2_3_r64

**class 1 g178** — deterministic, 1 entries — final contains-noun top=1_2_2_3_r65 — [group-level: negQ 1] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g178, g179): `(d+ex^2)^2/sqrt(a+cx^4)`, `1/((d+ex^2)^3 sqrt(a+cx^4))`. **Substrate.** Rubi's binomial rules bind where P0 used the trinomial variants with b=0 (DEG: `1_2_2_5_r9` / `1_2_2_3_r81`). Nested `1_2_2_3_r59` (`%mr_negQ(c/a)` symbolic; g179 also `1_2_2_7_r17/r37`, `r87`) → … — follows from: G-1; the nested NegQ reading

- 1.2.2.3 e152: record verified 1.3s -> contains-noun 0.6s | P0 core verified 1.7s top=1_2_2_5_r9 | final30 contains-noun 0.5s top=1_2_2_3_r65

**class 1 g179** — deterministic, 1 entries — final contains-noun top=1_2_2_3_r82 — [group-level: negQ 1] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g178, g179): `(d+ex^2)^2/sqrt(a+cx^4)`, `1/((d+ex^2)^3 sqrt(a+cx^4))`. **Substrate.** Rubi's binomial rules bind where P0 used the trinomial variants with b=0 (DEG: `1_2_2_5_r9` / `1_2_2_3_r81`). Nested `1_2_2_3_r59` (`%mr_negQ(c/a)` symbolic; g179 also `1_2_2_7_r17/r37`, `r87`) → … — follows from: G-1; the nested NegQ reading

- 1.2.2.3 e156: record verified 4.9s -> contains-noun 4.6s | P0 core verified 6.2s top=1_2_2_3_r81 | final30 contains-noun 5.5s top=1_2_2_3_r82

**class 1 g180** — deterministic, 1 entries — final contains-noun top=1_2_2_4_r10 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(d+ex^2)(a+cx^4)^5/x`. **Substrate.** `1_2_2_4_r10` (x^2 substitution) → `1_1_2_8_r20` → `1_1_2_8_r123` (CATCH-1), as g93. **P0.** `1_2_2_6_r2` → `1_1_2_8_r20`. All arms contains-noun. — follows from: faithful binding (NOUN)

- 1.2.2.4 e5: record verified 2.3s -> contains-noun 0.9s | P0 core verified 2.3s top=1_2_2_6_r2 | final30 contains-noun 0.9s top=1_2_2_4_r10

**class 1 g181** — deterministic, 1 entries — final contains-noun top=1_2_2_5_r3 — [group-level: none seen] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `(1+2x+x^2+x^3)/(1+2x^2+x^4)`. Both cores put r3 at top. **Nested.** P0: `1_3_2_r13, 1_2_1_6_r1, 1_2_2_6_r2`. Substrate: `1_2_2_3_r99, 1_2_1_6_r1, 1_2_2_4_r5`, which yields the marker. All arms contains-noun. — follows from: not determined from the traces

- 1.3.1 e287: record verified 3.3s -> contains-noun 1.7s | P0 core verified 4.0s top=1_2_2_5_r3 | final30 contains-noun 2.0s top=1_2_2_5_r3

**class 1 g182** — deterministic, 1 entries — final contains-noun top=1_2_3_2_r15 — [group-level: IGtQ 1] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(dx)^m/(a+bx^3+cx^6)^(3/2)`. **Substrate.** `1_2_3_2_r15` (Rubi `IGtQ[n,0] && ILtQ[p,-1]`) accepts p=-3/2 through `is(p < -1)`, then `1_2_3_6_r28` (CATCH-1) → marker. **P0.** The manual 9.1 `u*(a*x^n)^m`. All arms contains-noun. — follows from: 9.1 regeneration exposing the ILtQ translation

- 1.2.3.2 e255: record verified 5.5s -> contains-noun 2.9s | P0 core verified 5.6s top=9_1_r16 | final30 contains-noun 3.4s top=1_2_3_2_r15

**class 1 g183** — deterministic, 1 entries — final contains-noun top=1_2_3_4_r101 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(fx)^m(a+cx^2n)^p/(d+ex^n)^2`. **Substrate.** `1_2_3_4_r101` (q=-2) → `1_2_3_4_r102` (CATCH-1), `9_1_r12`, `1_4_1_r7`, at 26.6 s. **P0.** The manual 9.1 rule. All arms contains-noun. — follows from: 9.1 regeneration

- 1.2.3.4 e91: record verified 4.7s -> contains-noun 26.6s | P0 core verified 5.3s top=9_1_r16 | final30 contains-noun 27.1s top=1_2_3_4_r101

**class 1 g184** — deterministic, 1 entries — final deferred top=1_1_1_2_r34 — [group-level: none seen] [ZERO]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/(x sqrt(a+(2+2c-2(1+c))x^4))` (ZERO). **Substrate.** `1_1_2_1_r15` then `1_1_1_2_r34` (hypergeometric) give a top-level noun. **P0.** `1_2_2_8_r1` chain. All arms deferred. — follows from: not determined from the traces

- 1.2.2.2 e1035: record verified 4.3s -> deferred 0.8s | P0 core verified 4.0s top=1_2_2_8_r1 | final30 deferred 0.9s top=1_1_1_2_r34

**class 1 g185** — deterministic, 1 entries — final deferred top=1_1_1_4_r42 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(a+bx)^m(c+dx)^(-3-m)(e+fx)(g+hx)`. The catch-all `1_1_1_4_r42` answers at top level; P0 used `1_1_1_4_r19`. All arms deferred. — follows from: not determined why r19 no longer answers

- 1.1.1.4 e129: record verified 2.3s -> deferred 0.1s | P0 core verified 2.2s top=1_1_1_4_r19 | final30 deferred 0.1s top=1_1_1_4_r42

**class 1 g186** — deterministic, 1 entries — final deferred top=1_1_1_4_r7 — [group-level: IGtQ 1] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(7+5x)sqrt(2-3x)sqrt(1+4x)/sqrt(-5+2x)`. **Substrate.** `1_1_1_4_r7` (Rubi `IntegersQ[m,n,p] || IGtQ[n,0] && IGtQ[p,0]`) accepts n = p = 1/2 through `is(n > 0) and is(p > 0)`: EXPAND-NOUN. **P0.** `1_1_1_4_r13`. All arms deferred. — follows from: binding change exposing the IGtQ translation

- 1.1.1.4 e46: record verified 3.9s -> deferred 0.1s | P0 core verified 3.6s top=1_1_1_4_r13 | final30 deferred 0.1s top=1_1_1_4_r7

**class 1 g187** — deterministic, 1 entries — final deferred top=1_1_1_5_r5 — [group-level: none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g187, g188): `(c+dx)^n(A+Bx+Cx^2+Dx^3)/(a+bx)`, `(cx)^m(A+Bx+Cx^2)/(a+bx^2)`. **Substrate.** ExpandIntegrand rules whose Rubi conditions hold for these integer bindings (m = -1; p = -1) answer alone with a top-level noun. **P0.** `1_1_1_5_r8` / `1_2_1_9b_r5` chain. **Arms.** r3 verified 1.1 … — follows from: not determined (g187); condition retry (g188)

- 1.1.1.5 e29: record verified 3.6s -> deferred 2.8s | P0 core verified 3.5s top=1_1_1_5_r8 | final30 deferred 1.9s top=1_1_1_5_r5

**class 1 g188** — deterministic, 1 entries — final deferred top=1_1_2_11_r3 — [group-level: none seen] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g187, g188): `(c+dx)^n(A+Bx+Cx^2+Dx^3)/(a+bx)`, `(cx)^m(A+Bx+Cx^2)/(a+bx^2)`. **Substrate.** ExpandIntegrand rules whose Rubi conditions hold for these integer bindings (m = -1; p = -1) answer alone with a top-level noun. **P0.** `1_1_1_5_r8` / `1_2_1_9b_r5` chain. **Arms.** r3 verified 1.1 … — follows from: not determined (g187); condition retry (g188)

- 1.1.2.8 e61: record verified 7.4s -> deferred 2.5s | P0 core verified 7.2s top=1_2_1_9b_r5 | final30 deferred 1.8s top=1_1_2_11_r3

**class 1 g189** — deterministic, 1 entries — final deferred top=1_1_2_3_r53 — [group-level: IGtQ 1] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md`: `sqrt(4+x^2)/sqrt(c+dx^2)`. **Substrate.** `1_1_2_3_r53` (Rubi `IGtQ[p,0]`) accepts p=1/2: EXPAND-NOUN. **P0.** `1_1_2_5_r19`. All arms deferred. — follows from: binding change exposing the IGtQ translation

- 1.1.2.3 e180: record verified 0.1s -> deferred 0.3s | P0 core verified 0.1s top=1_1_2_5_r19 | final30 deferred 0.3s top=1_1_2_3_r53

**class 1 g190** — deterministic, 1 entries — final deferred top=1_1_2_4_r20 — [group-level: none seen] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md`: `sqrt(a+bx^2)/(x sqrt(c+dx^2))`. Both cores put the x^2 substitution r20 at top. **Nested.** P0: `1_1_1_3_r61/r62`. Substrate: `1_1_1_2_r32, 1_4_1_r34, 1_1_1_3_r59`, ending in a top-level noun. **Arms.** r3 verified 0.4 s. — follows from: condition retry

- 1.1.2.4 e937: record verified 1.7s -> deferred 4.5s | P0 core verified 1.7s top=1_1_2_4_r20 | final30 deferred 4.8s top=1_1_2_4_r20

**class 1 g191** — deterministic, 1 entries — final deferred top=1_1_2_7_r27 — [group-level: IGtQ 1] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/((3-x)(1-x^2)^(1/3))`. **Substrate.** `1_1_2_7_r27` (Rubi `ILtQ[p,0] && …`) accepts p=-1/3 through `is(p < 0)`: EXPAND-NOUN. **P0.** Rubi's `1_1_2_7_r52`. All arms deferred. — follows from: binding change exposing the ILtQ translation

- 1.2.1.2 e714: record verified 0.1s -> deferred 0.5s | P0 core verified 0.1s top=1_1_2_7_r52 | final30 deferred 0.6s top=1_1_2_7_r27

**class 1 g192** — deterministic, 1 entries — final deferred top=1_1_2_9_r23 — [group-level: none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g192, g194): `sqrt(d+ex)/((a+cx^2 or quad)sqrt(f+gx))` (m=1/2, m+1/2=1 integer). Each has the same top rule on both cores. **Nested.** P0's 3-arg ExpandIntegrand sum dispatched (`1_2_1_8_r2, 1_4_1_r7`). The substrate has nfires=1: a top-level noun. All arms deferred. — follows from: not determined from the traces

- 1.2.1.4 e611: record verified 4.3s -> deferred 0.4s | P0 core verified 4.3s top=1_1_2_9_r23 | final30 deferred 0.4s top=1_1_2_9_r23

**class 1 g193** — deterministic, 1 entries — final deferred top=1_1_3_8_r18 — [group-level: none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md`: `x^3(c+dx+ex^2+fx^3)(a+bx^4)^p`. The g137 shape: the `mr_sum` split has no nested fire. P0: `1_2_2_5_r3` chain. All arms deferred. — follows from: faithful binding; the split's missing fire is not determined

- 1.1.3.8 e553: record verified 5.6s -> deferred 3.5s | P0 core verified 5.6s top=1_2_2_5_r3 | final30 deferred 2.1s top=1_1_3_8_r18

**class 1 g194** — deterministic, 1 entries — final deferred top=1_2_1_3_r24 — [group-level: none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g192, g194): `sqrt(d+ex)/((a+cx^2 or quad)sqrt(f+gx))` (m=1/2, m+1/2=1 integer). Each has the same top rule on both cores. **Nested.** P0's 3-arg ExpandIntegrand sum dispatched (`1_2_1_8_r2, 1_4_1_r7`). The substrate has nfires=1: a top-level noun. All arms deferred. — follows from: not determined from the traces

- 1.2.1.4 e851: record verified 3.2s -> deferred 0.8s | P0 core verified 4.1s top=1_2_1_3_r24 | final30 deferred 1.2s top=1_2_1_3_r24

**class 1 g195** — deterministic, 1 entries — final deferred top=1_2_1_9b_r2 — [group-level: none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(1+x^3)sqrt(1+x)/(1+x^2)`. **Substrate.** `1_2_1_9b_r6` → `1_2_1_9b_r2` (divide out 1+x) → top-level noun. **P0.** The trinomial variant `9b_r1` after `9b_r5`, `1_2_1_9_r21`. All arms deferred. — follows from: not determined from the traces

- 1.3.2 e569: record verified 3.3s -> deferred 1.7s | P0 core verified 4.3s top=1_2_1_9b_r1 | final30 deferred 2.5s top=1_2_1_9b_r2

**class 1 g196** — deterministic, 1 entries — final deferred top=1_2_2_7_r12 — [group-level: none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g196, g197): `(A+Bx^2)(d+ex^2)^q/(a+bx^2+cx^4)`, `…/(a+cx^4)`. **Substrate.** The 1.2.2.7 ExpandIntegrand rules answer alone with a top-level noun. **P0.** P0's r12 sum dispatched (`1_4_1_r7`); for g197 P0 used r12 with b=0 (DEG). All arms deferred. — follows from: not determined (g196); G-1 (g197)

- 1.2.2.7 e33: record verified 6.0s -> deferred 1.3s | P0 core verified 6.3s top=1_2_2_7_r12 | final30 deferred 1.8s top=1_2_2_7_r12

**class 1 g197** — deterministic, 1 entries — final deferred top=1_2_2_7_r13 — [group-level: none seen] [EXPAND-NOUN]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g196, g197): `(A+Bx^2)(d+ex^2)^q/(a+bx^2+cx^4)`, `…/(a+cx^4)`. **Substrate.** The 1.2.2.7 ExpandIntegrand rules answer alone with a top-level noun. **P0.** P0's r12 sum dispatched (`1_4_1_r7`); for g197 P0 used r12 with b=0 (DEG). All arms deferred. — follows from: not determined (g196); G-1 (g197)

- 1.2.2.7 e15: record verified 6.0s -> deferred 1.2s | P0 core verified 6.4s top=1_2_2_7_r12 | final30 deferred 1.3s top=1_2_2_7_r13

**class 1 g198** — deterministic, 1 entries — final deferred top=1_2_3_4_r102 — [group-level: none seen] [CATCH-1]
> `10-p5-attribution.mechanisms-class1-c.md`: `(fx)^m(d+ex^n)^q/(a+bx^n+cx^2n)`. **Substrate.** `1_2_3_4_r102` (CATCH-1) answers at top level. **P0.** The manual 9.1 rule; Rubi's 5-step route is not reached. All arms deferred. — follows from: 9.1 regeneration

- 1.2.3.4 e145: record verified 3.9s -> deferred 7.2s | P0 core verified 4.8s top=9_1_r16 | final30 deferred 6.6s top=1_2_3_4_r102

**class 1 g199** — deterministic, 1 entries — final deferred top=1_3_3_r12 — [group-level: IGtQ 1] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md`: `(-1+x^2)/((1+x^2)sqrt(x+x^3))`. Both cores put `1_3_3_r12` at top. Rubi's condition is `ILtQ[p,0]`, and the cond accepts p=-1/2 on both cores. **P0.** Its expansion dispatched (`9_1_r9, 1_2_2_5_r3, 1_4_1_r34, 1_1_2_2_r6, 1_4_1_r7`). **Substrate.** nfires=1: a top-level noun. … — follows from: condition retry + model flags

- 1.3.2 e733: record verified 3.2s -> deferred 1.1s | P0 core verified 4.1s top=1_3_3_r12 | final30 deferred 1.6s top=1_3_3_r12

**class 1 g200** — deterministic, 1 entries — final error top=1_1_3_1_r14 — [group-level: IGtQ 1] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g200, g201, g202): `1/(1-x^10)`, `x^5/(9+x^12)`, `x^5/(9-x^12)`. **Top level.** The top-level PF-EVEN rule accepts n = 10 / 12 ((n-3)/2 = 7/2, (n-1)/2 = 11/2; numeric coefficients) and fired, so rubi returned. **Death.** error 7.1 / 9.6 / 9.0 s (record), 19.3–28.2 s (final30). The kind is not … — follows from: faithful binding exposing the IGtQ translation

- 1.1.3.2 e1538: record verified 0.6s -> error 7.1s | P0 core verified 0.6s top=1_4_1_r23 | final30 error 19.3s top=1_1_3_1_r14

**class 1 g201** — deterministic, 1 entries — final error top=1_1_3_2_r35 — [group-level: IGtQ 1] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g200, g201, g202): `1/(1-x^10)`, `x^5/(9+x^12)`, `x^5/(9-x^12)`. **Top level.** The top-level PF-EVEN rule accepts n = 10 / 12 ((n-3)/2 = 7/2, (n-1)/2 = 11/2; numeric coefficients) and fired, so rubi returned. **Death.** error 7.1 / 9.6 / 9.0 s (record), 19.3–28.2 s (final30). The kind is not … — follows from: faithful binding exposing the IGtQ translation

- 1.1.3.2 e1541: record verified 1.2s -> error 9.6s | P0 core verified 1.1s top=1_3_4_r1 | final30 error 28.2s top=1_1_3_2_r35

**class 1 g202** — deterministic, 1 entries — final error top=1_1_3_2_r36 — [group-level: IGtQ 1] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g200, g201, g202): `1/(1-x^10)`, `x^5/(9+x^12)`, `x^5/(9-x^12)`. **Top level.** The top-level PF-EVEN rule accepts n = 10 / 12 ((n-3)/2 = 7/2, (n-1)/2 = 11/2; numeric coefficients) and fired, so rubi returned. **Death.** error 7.1 / 9.6 / 9.0 s (record), 19.3–28.2 s (final30). The kind is not … — follows from: faithful binding exposing the IGtQ translation

- 1.1.3.2 e1542: record verified 1.1s -> error 9.0s | P0 core verified 1.1s top=1_3_4_r1 | final30 error 24.8s top=1_1_3_2_r36

**class 1 g203** — deterministic, 1 entries — final timeout top=1_1_1_2_r14 — [group-level: none seen] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/(x(a+b sqrt(x))^8)`. **Fires.** Nested `1_1_1_1_r1/r3, 1_1_1_2_r3/r14` at 30 s; `1_1_3_2_r15` by 120 s. The top-level sqrt(x) substitution fire is absent. **P0.** `1_1_3_2_r110` alone. r3 verified 0.5 s. — follows from: condition retry

- 1.1.3.2 e2227: record verified 0.7s -> timeout 30.0s | P0 core verified 0.7s top=1_1_3_2_r110 | final30 timeout 30.1s top=1_1_1_2_r14 | final120 timeout 120.0s top=1_1_3_2_r15

**class 1 g204** — deterministic, 1 entries — final timeout top=1_1_1_2_r19 — [group-level: IGtQ 1; negQ 1 (both 1)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(a-bx^4)^(1/4)/x`. **Substrate.** Nested `1_1_1_2_r32` (t^4) → PF-EVEN `1_1_3_1_r14` (n = 4, symbolic a) → r19. The top-level fire is absent. **P0.** `1_2_2_2_r8` after `1_1_1_2_r37, 1_1_2_2_r4`. r3 verified 0.1 s. — follows from: condition retry exposing IGtQ and NegQ

- 1.1.3.2 e1178: record verified 0.5s -> timeout 30.1s | P0 core verified 0.4s top=1_2_2_2_r8 | final30 timeout 30.1s top=1_1_1_2_r19 | final120 timeout 120.2s top=1_1_1_2_r19

**class 1 g205** — deterministic, 1 entries — final timeout top=1_1_1_4_r15 — [group-level: none seen] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md`: `(a+bx)^m(A+Bx)/((c+dx)^m(e+fx))`. Both cores put r15 at top (fired at 30 s). **Nested.** P0: `1_1_1_6_r7`. Substrate: `1_1_1_3_r61, 1_1_1_4_r47`. VERIFY-TIMEOUT; all arms timeout. — follows from: not determined from the traces

- 1.1.1.4 e137: record verified 6.4s -> timeout 30.0s | P0 core verified 6.5s top=1_1_1_4_r15 | final30 timeout 30.1s top=1_1_1_4_r15 | final120 unverified 119.8s top=1_1_1_4_r15

**class 1 g206** — deterministic, 1 entries — final timeout top=1_1_2_1_r26 — [group-level: none seen] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g206, g207, g208, g249): `1/(-2+3x^2)^(3/4)`, `1/(a+bx^2)^(5/6)`, `1/((-2+3x^2)(-1+3x^2)^(3/4))`, `1/(-2-3x^2)^(3/4)`. **Fires.** Identical fire lists on both cores. Each top-level rule fired, so rubi returned. **Arms.** r4 verified 0.1–0.3 s in all four (MFLAGS). — follows from: model flags

- 1.1.2.2 e908: record verified 0.2s -> timeout 30.0s | P0 core verified 0.2s top=1_1_2_1_r26 | final30 timeout 30.1s top=1_1_2_1_r26 | final120 timeout 120.1s top=1_1_2_1_r26

**class 1 g207** — deterministic, 1 entries — final timeout top=1_1_2_1_r30 — [group-level: none seen] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g206, g207, g208, g249): `1/(-2+3x^2)^(3/4)`, `1/(a+bx^2)^(5/6)`, `1/((-2+3x^2)(-1+3x^2)^(3/4))`, `1/(-2-3x^2)^(3/4)`. **Fires.** Identical fire lists on both cores. Each top-level rule fired, so rubi returned. **Arms.** r4 verified 0.1–0.3 s in all four (MFLAGS). — follows from: model flags

- 1.1.2.2 e1028: record verified 0.2s -> timeout 30.0s | P0 core verified 0.2s top=1_1_2_1_r30 | final30 timeout 30.0s top=1_1_2_1_r30 | final120 timeout 120.1s top=1_1_2_1_r30

**class 1 g208** — deterministic, 1 entries — final timeout top=1_1_2_3_r32 — [group-level: none seen] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g206, g207, g208, g249): `1/(-2+3x^2)^(3/4)`, `1/(a+bx^2)^(5/6)`, `1/((-2+3x^2)(-1+3x^2)^(3/4))`, `1/(-2-3x^2)^(3/4)`. **Fires.** Identical fire lists on both cores. Each top-level rule fired, so rubi returned. **Arms.** r4 verified 0.1–0.3 s in all four (MFLAGS). — follows from: model flags

- 1.1.2.4 e1090: record verified 0.2s -> timeout 30.0s | P0 core verified 0.2s top=1_1_2_3_r32 | final30 timeout 30.0s top=1_1_2_3_r32 | final120 timeout 120.1s top=1_1_2_3_r32

**class 1 g209** — deterministic, 1 entries — final timeout top=1_1_2_4_r25 — [group-level: IGtQ 1; negQ 1 (both 1)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md`: `(A+Bx^2)/(x^(5/2)(a+bx^2))`. As g108/g112. **Substrate.** The top-level `1_1_2_4_r25` (e=1 through `e_.`) fired → `1_1_2_2_r27` → PF-EVEN `1_1_3_1_r14` (n = 4, symbolic). **P0.** `1_4_1_r34`. VERIFY-TIMEOUT. — follows from: faithful Optional binding exposing IGtQ and NegQ

- 1.1.2.4 e373: record verified 2.0s -> timeout 30.1s | P0 core verified 2.0s top=1_4_1_r34 | final30 timeout 30.0s top=1_1_2_4_r25 | final120 timeout 120.1s top=1_1_2_4_r25

**class 1 g210** — deterministic, 1 entries — final timeout top=1_1_2_7_r54 — [group-level: NE 1] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/((a+bx)(c+dx^2)^(1/4))`. Both cores put r54 at top (fired at 30 s). **Nested.** The substrate's `1_1_3_4_r30` (NE: k = 1, identity substitution, Maxima integrate) replaces P0's `1_2_2_3_r76, 1_1_3_4_r58`. **Arms.** r4 verified 0.8 s. — follows from: model flags

- 1.2.1.2 e717: record verified 0.7s -> timeout 30.1s | P0 core verified 0.8s top=1_1_2_7_r54 | final30 timeout 30.0s top=1_1_2_7_r54 | final120 unverified 116.2s top=1_1_2_7_r54

**class 1 g211** — deterministic, 1 entries — final timeout top=1_1_3_2_r71 — [group-level: IGtQ 1; negQ 1 (both 1)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/((a+cx^4)sqrt(x))`. **Substrate.** The top-level `1_1_3_2_r71` (x^(1/2)) fired → t^8 → PF-EVEN `1_1_3_1_r14` (n = 8, symbolic). **P0.** `1_4_1_r34`. VERIFY-TIMEOUT. — follows from: faithful binding exposing IGtQ and NegQ

- 1.1.3.2 e741: record verified 1.1s -> timeout 30.1s | P0 core verified 1.1s top=1_4_1_r34 | final30 timeout 30.1s top=1_1_3_2_r71 | final120 timeout 120.1s top=1_1_3_2_r71

**class 1 g212** — deterministic, 1 entries — final timeout top=1_1_3_2_r84 — [group-level: NE 1] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `x^(1/3)/(-1+x^(5/6))`. **Substrate.** `1_1_3_2_r84` (x^(1/6) substitution) → nested `1_1_3_2_r17` (NE), `r44`, `r107` (p=-1). **P0.** `1_1_3_2_r110` alone. All arms timeout. — follows from: not determined from the traces

- 1.1.3.2 e2383: record verified 0.3s -> timeout 30.0s | P0 core verified 0.3s top=1_1_3_2_r110 | final30 timeout 30.0s top=1_1_3_2_r84 | final120 timeout 120.0s top=1_1_3_2_r107

**class 1 g213** — deterministic, 1 entries — final timeout top=1_1_3_3_r17 — [group-level: IGtQ 1; negQ 1 (both 1)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g213, g214, g259, g260): `(a+bx^4)/(c+dx^4)`, `(a+bx^4)^2/(c+dx^4)^3`, `(c+dx^4)/(a+bx^4)^2`, `(c+dx^4)/(a+bx^4)`. **Substrate.** The top-level 1.1.3.3 reduction fired → PF-EVEN `1_1_3_1_r14` (n = 4, symbolic) + prefix. **Classes.** g213/g214 time out (VERIFY-TIMEOUT); g259/g260 read unverified at … — follows from: faithful binding exposing IGtQ and NegQ (g214 also condition retry)

- 1.1.3.3 e51: record verified 0.2s -> timeout 30.1s | P0 core verified 0.2s top=1_1_3_3_r19 | final30 timeout 30.1s top=1_1_3_3_r17 | final120 timeout 120.3s top=1_1_3_3_r17

**class 1 g214** — deterministic, 1 entries — final timeout top=1_1_3_3_r45 — [group-level: IGtQ 1; negQ 1 (both 1)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g213, g214, g259, g260): `(a+bx^4)/(c+dx^4)`, `(a+bx^4)^2/(c+dx^4)^3`, `(c+dx^4)/(a+bx^4)^2`, `(c+dx^4)/(a+bx^4)`. **Substrate.** The top-level 1.1.3.3 reduction fired → PF-EVEN `1_1_3_1_r14` (n = 4, symbolic) + prefix. **Classes.** g213/g214 time out (VERIFY-TIMEOUT); g259/g260 read unverified at … — follows from: faithful binding exposing IGtQ and NegQ (g214 also condition retry)

- 1.1.3.3 e60: record verified 0.3s -> timeout 30.1s | P0 core verified 0.3s top=1_1_3_3_r60 | final30 timeout 30.1s top=1_1_3_3_r45 | final120 timeout 120.1s top=1_1_3_3_r45

**class 1 g215** — deterministic, 1 entries — final timeout top=1_1_3_4_r25 — [group-level: IGtQ 1] [FLAT]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g215, g261): `x^k(a+bx^2)/((-c+dx)^(j/2)(c+dx)^(j/2))`. **Substrate.** The top-level `1_1_3_4_r25` fired. Nested: `1_1_2_2_r39` (hypergeometric; accepts p = -3/2 / -1/2 through `is(p < 0)` with a = -c^2; Rubi needs ILtQ or GtQ[a,0]; binding inferred), `1_1_1_6_r2`, `1_1_2_11_r3` … — follows from: the narrow Flat reading (both) + condition retry (g215), exposing the ILtQ translation

- 1.1.3.3 e271: record verified 2.1s -> timeout 30.0s | P0 core verified 2.0s top=1_1_1_6_r2 | final30 timeout 30.1s top=1_1_3_4_r25 | final120 timeout 120.1s top=1_1_3_4_r25

**class 1 g216** — deterministic, 1 entries — final timeout top=1_1_3_4_r44 — [group-level: IGtQ 1; negQ 1 (both 1)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g216, g217): `x^(7/2)/((a+bx^2)(c+dx^2))`, `1/(x^(5/2)(a+bx^2)(c+dx^2))`. **Substrate.** Nested `1_1_3_5_r2` (partial fractions) → PF-EVEN `1_1_3_1_r14` (n = 4, symbolic). g216's top-level x^(1/2) substitution fires by 120 s. **P0.** `1_4_1_r34` / `1_1_2_4_r48`. **Arms.** r4 verified 3.9 s … — follows from: faithful binding exposing IGtQ and NegQ (g217 also model flags)

- 1.1.2.4 e462: record verified 1.9s -> timeout 30.1s | P0 core verified 1.9s top=1_4_1_r34 | final30 timeout 30.0s top=1_1_3_4_r44 | final120 timeout 120.1s top=1_1_2_4_r34

**class 1 g217** — deterministic, 1 entries — final timeout top=1_1_3_4_r45 — [group-level: IGtQ 1; negQ 1 (both 1)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g216, g217): `x^(7/2)/((a+bx^2)(c+dx^2))`, `1/(x^(5/2)(a+bx^2)(c+dx^2))`. **Substrate.** Nested `1_1_3_5_r2` (partial fractions) → PF-EVEN `1_1_3_1_r14` (n = 4, symbolic). g216's top-level x^(1/2) substitution fires by 120 s. **P0.** `1_4_1_r34` / `1_1_2_4_r48`. **Arms.** r4 verified 3.9 s … — follows from: faithful binding exposing IGtQ and NegQ (g217 also model flags)

- 1.1.2.4 e468: record verified 8.2s -> timeout 30.1s | P0 core verified 8.1s top=1_1_2_4_r48 | final30 timeout 30.1s top=1_1_3_4_r45 | final120 timeout 120.1s top=1_1_3_4_r45

**class 1 g218** — deterministic, 1 entries — final timeout top=1_1_3_4_r47 — [group-level: IGtQ 1; negQ 1 (both 1)] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g218, g262): `x/((a+bx^4)(c+dx^4))`, `x^5/(…)`. **Substrate.** The top-level partial-fraction rule fired → `1_1_3_2_r36` on `x/(a+bx^4)` ((4-1)/2 = 3/2; symbolic a/b) + prefix. **Walls.** 25–30 s; arms unverified at 14.7–26.2 s, i.e. at the cap. **P0.** `1_3_4_r3`. — follows from: faithful binding exposing IGtQ and NegQ

- 1.1.3.4 e608: record verified 3.7s -> unverified 24.7s | P0 core verified 4.7s top=1_3_4_r3 | final30 timeout 30.0s top=1_1_3_4_r47

**class 1 g219** — deterministic, 1 entries — final timeout top=1_1_3_7_r37 — [group-level: IGtQ 1; negQ 1 (both 1)] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g219, g220): `(c+dx+ex^2)/sqrt(a+bx^3)`, `x(c+dx+ex^2)/(a+bx^3)^(3/2)`. **Top level.** The top-level rule fired; `1_1_3_7_r37` (Rubi `IGtQ[n/2,0]`) accepts n = 3. **Nested.** `1_4_1_r23` and `1_1_3_1_r31`. r31's `%mr_negQ(a)` on symbolic a takes Rubi's NegQ branch; the corpus answers carry … — follows from: faithful binding exposing IGtQ and NegQ

- 1.1.3.8 e433: record verified 3.0s -> timeout 30.1s | P0 core verified 3.2s top=1_3_4_r20 | final30 timeout 30.1s top=1_1_3_7_r37 | final120 timeout 120.1s top=1_1_3_7_r37

**class 1 g220** — deterministic, 1 entries — final timeout top=1_1_3_8_r13 — [group-level: IGtQ 1; negQ 1 (both 1)] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g219, g220): `(c+dx+ex^2)/sqrt(a+bx^3)`, `x(c+dx+ex^2)/(a+bx^3)^(3/2)`. **Top level.** The top-level rule fired; `1_1_3_7_r37` (Rubi `IGtQ[n/2,0]`) accepts n = 3. **Nested.** `1_4_1_r23` and `1_1_3_1_r31`. r31's `%mr_negQ(a)` on symbolic a takes Rubi's NegQ branch; the corpus answers carry … — follows from: faithful binding exposing IGtQ and NegQ

- 1.1.3.8 e441: record verified 2.4s -> timeout 30.0s | P0 core verified 3.4s top=1_3_4_r21 | final30 timeout 30.1s top=1_1_3_8_r13 | final120 timeout 120.1s top=1_1_3_8_r13

**class 1 g221** — deterministic, 1 entries — final timeout top=1_1_4_3_r1 — [group-level: none seen] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g221, g225): `x^5(A+Bx^2)/(bx^2+cx^4)^(3/2)`, `x^2(A+Bx)/(bx+cx^2)^(3/2)`. **Substrate.** The top-level rule fired (g225: x^2 as (0+x)^2, OPT). Nested `1_2_1_3_r31`, `1_1_4_2_r21`, `1_2_1_2_r15`, `1_2_1_1_r14`, `1_1_2_1_r13`. **P0.** `1_2_2_6_r2` / `1_2_1_6_r1`. **Arms.** r3 verified 0.5 s … — follows from: condition retry

- 1.1.4.3 e147: record verified 1.8s -> timeout 30.0s | P0 core verified 1.8s top=1_2_2_6_r2 | final30 timeout 30.1s top=1_1_4_3_r1 | final120 timeout 120.1s top=1_1_4_3_r1

**class 1 g222** — deterministic, 1 entries — final timeout top=1_2_1_2_r133 — [group-level: none seen] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/((d+ex)(c^2d^2-bcde+b^2e^2+3bce^2x+3c^2e^2x^2)^(1/3))`. Both cores put r133 at top (fired). **Nested.** P0: `9_1_r16, 1_4_1_r34, 1_4_1_r30`. Substrate: `1_1_1_4_r47`. **Arms.** r4 verified 3.3 s. — follows from: model flags

- 1.2.1.2 e2496: record verified 16.1s -> timeout 30.0s | P0 core verified 16.4s top=1_2_1_2_r133 | final30 timeout 30.0s top=1_2_1_2_r133 | final120 timeout 120.1s top=1_2_1_2_r133

**class 1 g223** — deterministic, 1 entries — final timeout top=1_2_1_2_r99 — [group-level: negQ 1] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/((d+ex)sqrt(a+bx^2+cx^4))`. **Substrate nested.** `1_1_2_3_r42`, `1_1_2_5_r20/r31`, `1_2_2_3_r78` (`%mr_negQ(c/a)`, symbolic), `1_1_2_1_r13`, `1_2_1_2_r99`. The top-level `1_2_2_8_r1` (P0's top) is absent at 30 s and 120 s. **P0.** P0 also ran r78. All arms timeout. — follows from: not determined from the traces

- 1.2.2.8 e3: record verified 1.6s -> timeout 30.1s | P0 core verified 2.4s top=1_2_2_8_r1 | final30 timeout 30.1s top=1_2_1_2_r99 | final120 timeout 120.1s top=1_2_1_2_r99

**class 1 g224** — deterministic, 1 entries — final timeout top=1_2_1_3_r104 — [group-level: none seen] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g224, g229, g234): `sqrt(f+gx)/((d+ex)sqrt(quad))`, `1/(sqrt(2+3x+5x^2)sqrt(3-x+2x^2))`, `x/((d+ex^2)(a+bx^2+cx^4))`. **Both cores.** Same top rule, fired at 30 s. The substrate's nested chain differs: g224 elliptic (`1_1_2_3_r42`, `1_2_1_2_r93`, `1_2_1_3_r99`); g229 `1_1_2_3_r54`, `1_2_2_1_r18` … — follows from: not determined which change moves the nested chain

- 1.2.1.4 e904: record verified 1.3s -> timeout 30.0s | P0 core verified 1.8s top=1_2_1_3_r104 | final30 timeout 30.0s top=1_2_1_3_r104 | final120 timeout 120.1s top=1_2_1_3_r104

**class 1 g225** — deterministic, 1 entries — final timeout top=1_2_1_3_r31 — [group-level: none seen] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g221, g225): `x^5(A+Bx^2)/(bx^2+cx^4)^(3/2)`, `x^2(A+Bx)/(bx+cx^2)^(3/2)`. **Substrate.** The top-level rule fired (g225: x^2 as (0+x)^2, OPT). Nested `1_2_1_3_r31`, `1_1_4_2_r21`, `1_2_1_2_r15`, `1_2_1_1_r14`, `1_1_2_1_r13`. **P0.** `1_2_2_6_r2` / `1_2_1_6_r1`. **Arms.** r3 verified 0.5 s … — follows from: condition retry

- 1.2.1.3 e122: record verified 1.0s -> timeout 30.0s | P0 core verified 1.0s top=1_2_1_6_r1 | final30 timeout 30.0s top=1_2_1_3_r31 | final120 timeout 120.1s top=1_2_1_3_r31

**class 1 g226** — deterministic, 1 entries — final timeout top=1_2_1_3_r42 — [group-level: IGtQ 1] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md`: `(b+2cx)(d+ex)^4/(quad)^(3/2)`. **Substrate.** The top-level `1_2_1_3_r42` fired. Nested `1_2_1_9b_r5` (accepts p=-3/2 through `is(p > -2)`), `9b_r32`, `1_2_1_2_r117`, `9_1_r8`, `1_2_1_2_r15`, `1_2_1_1_r15`, `1_1_2_1_r13`. **P0.** `1_2_1_6_r1` alone. VERIFY-TIMEOUT. — follows from: faithful binding exposing the IGtQ translation

- 1.2.1.3 e1581: record verified 0.7s -> timeout 30.0s | P0 core verified 0.9s top=1_2_1_6_r1 | final30 timeout 30.0s top=1_2_1_3_r42 | final120 timeout 120.1s top=1_2_1_3_r42

**class 1 g227** — deterministic, 1 entries — final timeout top=1_2_1_3_r45 — [group-level: none seen] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g227, g228): `x^3(A+Bx^2)/sqrt(quartic)`, `(A+Bx^2)/(x^3 sqrt(quartic))`. As g83/g84. **At 30 s.** Nested `1_1_2_1_r13, 1_2_1_1_r15` / `1_2_1_2_r99` and `r45/r48`, binding the substitution's x through `d_.` (OPT). **At 120 s.** The top-level x^2 substitution has fired and the entries still … — follows from: faithful Optional binding

- 1.2.2.4 e170: record verified 2.0s -> timeout 30.0s | P0 core verified 2.0s top=1_2_2_6_r2 | final30 timeout 30.0s top=1_2_1_3_r45 | final120 timeout 120.1s top=1_2_2_4_r9

**class 1 g228** — deterministic, 1 entries — final timeout top=1_2_1_3_r48 — [group-level: none seen] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g227, g228): `x^3(A+Bx^2)/sqrt(quartic)`, `(A+Bx^2)/(x^3 sqrt(quartic))`. As g83/g84. **At 30 s.** Nested `1_1_2_1_r13, 1_2_1_1_r15` / `1_2_1_2_r99` and `r45/r48`, binding the substitution's x through `d_.` (OPT). **At 120 s.** The top-level x^2 substitution has fired and the entries still … — follows from: faithful Optional binding

- 1.2.2.4 e173: record verified 3.0s -> timeout 30.1s | P0 core verified 3.2s top=1_2_2_6_r2 | final30 timeout 30.1s top=1_2_1_3_r48 | final120 timeout 120.1s top=1_2_2_4_r9

**class 1 g229** — deterministic, 1 entries — final timeout top=1_2_1_4_r30 — [group-level: none seen] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g224, g229, g234): `sqrt(f+gx)/((d+ex)sqrt(quad))`, `1/(sqrt(2+3x+5x^2)sqrt(3-x+2x^2))`, `x/((d+ex^2)(a+bx^2+cx^4))`. **Both cores.** Same top rule, fired at 30 s. The substrate's nested chain differs: g224 elliptic (`1_1_2_3_r42`, `1_2_1_2_r93`, `1_2_1_3_r99`); g229 `1_1_2_3_r54`, `1_2_2_1_r18` … — follows from: not determined which change moves the nested chain

- 1.2.1.5 e123: record verified 1.0s -> timeout 30.0s | P0 core verified 1.5s top=1_2_1_4_r30 | final30 timeout 30.0s top=1_2_1_4_r30 | final120 timeout 120.1s top=1_2_1_4_r30

**class 1 g230** — deterministic, 1 entries — final timeout top=1_2_1_9_r12 — [group-level: none seen] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g230, g231): `x^2/((quad)^(k/2)(d-fx^2))`. **Substrate.** The top-level 1.2.1.9 rule fired; nested `1_4_1_r18` (+`1_1_2_1_r13, 1_2_1_1_r15`). **P0.** `1_4_2_r17` alone. VERIFY-TIMEOUT. — follows from: faithful binding

- 1.2.1.6 e104: record verified 0.8s -> timeout 30.0s | P0 core verified 0.8s top=1_4_2_r17 | final30 timeout 30.0s top=1_2_1_9_r12 | final120 timeout 120.1s top=1_2_1_9_r12

**class 1 g231** — deterministic, 1 entries — final timeout top=1_2_1_9_r19 — [group-level: none seen] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g230, g231): `x^2/((quad)^(k/2)(d-fx^2))`. **Substrate.** The top-level 1.2.1.9 rule fired; nested `1_4_1_r18` (+`1_1_2_1_r13, 1_2_1_1_r15`). **P0.** `1_4_2_r17` alone. VERIFY-TIMEOUT. — follows from: faithful binding

- 1.2.1.6 e96: record verified 0.6s -> timeout 30.0s | P0 core verified 0.8s top=1_4_2_r17 | final30 timeout 30.0s top=1_2_1_9_r19 | final120 timeout 120.2s top=1_2_1_9_r19

**class 1 g232** — deterministic, 1 entries — final timeout top=1_2_2_1_r17 — [group-level: none seen] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/(sqrt(quad)sqrt(quad))`. **Substrate nested.** `1_1_2_3_r42` → `1_2_2_1_r17` (`%mr_negQ(c/a)` on coefficients built from r30's substitution; Rubi's reading of that composite is not determined, so not tagged). The top-level `1_2_1_4_r30` (P0's top) is absent. All arms timeout. — follows from: not determined from the traces

- 1.2.1.5 e122: record verified 1.0s -> timeout 30.0s | P0 core verified 1.5s top=1_2_1_4_r30 | final30 timeout 30.1s top=1_2_2_1_r17 | final120 timeout 120.1s top=1_2_2_1_r17

**class 1 g233** — deterministic, 1 entries — final timeout top=1_2_2_2_r35 — [group-level: IGtQ 1; NE 1] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md`: `(dx)^(5/2)/(a^2+2abx^2+b^2x^4)^3`. **Substrate.** The top-level FracPart rewrite `1_2_2_2_r35` fired. Nested: `1_1_3_2_r17` (NE), `1_1_2_2_r27/r13`, `1_1_2_2_r7`. r7 is Rubi `ILtQ[Simplify[(m+1)/2+p+1],0]` and accepts a quarter-integer. **P0.** `1_3_3_r10, 1_4_1_r34, 1_3_4_r9`. … — follows from: model flags, with IGtQ and NE on the route

- 1.2.2.2 e721: record verified 4.7s -> timeout 30.0s | P0 core verified 5.3s top=1_3_4_r9 | final30 timeout 30.1s top=1_2_2_2_r35 | final120 timeout 120.1s top=1_2_2_2_r35

**class 1 g234** — deterministic, 1 entries — final timeout top=1_2_2_4_r5 — [group-level: none seen] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g224, g229, g234): `sqrt(f+gx)/((d+ex)sqrt(quad))`, `1/(sqrt(2+3x+5x^2)sqrt(3-x+2x^2))`, `x/((d+ex^2)(a+bx^2+cx^4))`. **Both cores.** Same top rule, fired at 30 s. The substrate's nested chain differs: g224 elliptic (`1_1_2_3_r42`, `1_2_1_2_r93`, `1_2_1_3_r99`); g229 `1_1_2_3_r54`, `1_2_2_1_r18` … — follows from: not determined which change moves the nested chain

- 1.2.2.4 e299: record verified 2.9s -> timeout 30.0s | P0 core verified 3.4s top=1_2_2_4_r5 | final30 timeout 30.0s top=1_2_2_4_r5 | final120 timeout 120.2s top=1_2_2_4_r5

**class 1 g235** — deterministic, 1 entries — final timeout top=1_2_2_6_r2 — [group-level: none seen] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md`: `(d+ex^2+fx^4)/(x(a+bx^2+cx^4))`. Both cores put r2 at top (fired). **Nested.** Substrate: the log/atanh prefix + `1_2_1_2_r80`, `1_2_1_3_r89`, `1_2_1_9b_r32`. P0: `1_2_1_6_r1, 1_4_1_r19, 1_2_1_9_r16`. **Arms.** r3 verified 2.0 s. — follows from: condition retry

- 1.2.2.6 e51: record verified 2.5s -> timeout 30.0s | P0 core verified 2.7s top=1_2_2_6_r2 | final30 timeout 30.0s top=1_2_2_6_r2 | final120 timeout 120.2s top=1_2_2_6_r2

**class 1 g236** — deterministic, 1 entries — final timeout top=1_2_3_1_r7 — [group-level: negQ 1] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/(sqrt(x)(a+bx^2+cx^4))`. **Substrate nested.** The prefix, `1_2_2_3_r27` and `1_2_3_1_r7` (both `NegQ[b^2-4*a*c]`). The corpus has the `(-b-sqrt(b^2-4ac))^(1/4)` form. The top-level sqrt(x) substitution fire is absent. **P0.** `1_4_1_r34`. All arms timeout. — follows from: not determined which change routes the substituted integrand; the NegQ reading

- 1.2.2.2 e1067: record verified 2.2s -> timeout 30.1s | P0 core verified 2.1s top=1_4_1_r34 | final30 timeout 30.1s top=1_2_3_1_r7 | final120 timeout 120.2s top=1_2_3_1_r7

**class 1 g237** — deterministic, 1 entries — final timeout top=1_2_3_2_r1 — [group-level: none seen] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md`: `x^(n-1)/(a+bx^n+cx^2n)`. **Substrate.** The top-level x^n substitution fired → `1_2_1_1_r12` → `1_1_2_1_r13`: the corpus's 3-step atanh form. **P0.** The manual 9.1 rule. VERIFY-TIMEOUT; all arms timeout. — follows from: 9.1 regeneration; the cost is verification

- 1.2.3.2 e552: record verified 4.2s -> timeout 30.1s | P0 core verified 5.8s top=9_1_r16 | final30 timeout 30.1s top=1_2_3_2_r1 | final120 timeout 120.2s top=1_2_3_2_r1

**class 1 g238** — deterministic, 1 entries — final timeout top=1_2_3_2_r16 — [group-level: IGtQ 1] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g238, g239, g240): `x^9`, `x^5`, `x` over `(1-3x^4+x^8)`. **Substrate.** The top-level rule fired → partial fractions (`1_2_3_4_r49` for g238) → PF-EVEN `1_1_3_2_r36` on n = 4 (numeric) + prefix. **P0.** `1_3_3_r10`. **Arms.** r3 deferred 0.4 s (g238, g239) and verified 0.3 s (g240). — follows from: faithful binding exposing the IGtQ translation (g240 also condition retry)

- 1.2.3.2 e387: record verified 1.7s -> timeout 30.1s | P0 core verified 1.7s top=1_3_3_r10 | final30 timeout 30.1s top=1_2_3_2_r16 | final120 timeout 120.2s top=1_2_3_2_r16

**class 1 g239** — deterministic, 1 entries — final timeout top=1_2_3_2_r23 — [group-level: IGtQ 1] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g238, g239, g240): `x^9`, `x^5`, `x` over `(1-3x^4+x^8)`. **Substrate.** The top-level rule fired → partial fractions (`1_2_3_4_r49` for g238) → PF-EVEN `1_1_3_2_r36` on n = 4 (numeric) + prefix. **P0.** `1_3_3_r10`. **Arms.** r3 deferred 0.4 s (g238, g239) and verified 0.3 s (g240). — follows from: faithful binding exposing the IGtQ translation (g240 also condition retry)

- 1.2.3.2 e389: record verified 1.7s -> timeout 30.1s | P0 core verified 1.7s top=1_3_3_r10 | final30 timeout 30.1s top=1_2_3_2_r23 | final120 timeout 120.1s top=1_2_3_2_r23

**class 1 g240** — deterministic, 1 entries — final timeout top=1_2_3_2_r24 — [group-level: IGtQ 1] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g238, g239, g240): `x^9`, `x^5`, `x` over `(1-3x^4+x^8)`. **Substrate.** The top-level rule fired → partial fractions (`1_2_3_4_r49` for g238) → PF-EVEN `1_1_3_2_r36` on n = 4 (numeric) + prefix. **P0.** `1_3_3_r10`. **Arms.** r3 deferred 0.4 s (g238, g239) and verified 0.3 s (g240). — follows from: faithful binding exposing the IGtQ translation (g240 also condition retry)

- 1.2.3.2 e391: record verified 1.1s -> timeout 30.1s | P0 core verified 1.1s top=1_3_3_r10 | final30 timeout 30.1s top=1_2_3_2_r24 | final120 timeout 120.2s top=1_2_3_2_r24

**class 1 g241** — deterministic, 1 entries — final timeout top=1_4_1_r23 — [group-level: none seen] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/((cx)^(2/3)(a+bx^2)^(2/3))`. **Substrate.** Nested `1_1_3_1_r37, r53, 1_4_1_r23`. P0's top-level x^(1/3) substitution `1_4_1_r34` is absent at 30 s and 120 s. **Arms.** r3 verified 0.2 s. — follows from: condition retry

- 1.1.2.2 e781: record verified 1.9s -> timeout 30.1s | P0 core verified 1.7s top=1_4_1_r34 | final30 timeout 30.1s top=1_4_1_r23 | final120 timeout 120.1s top=1_4_1_r23

**class 1 g242** — deterministic, 1 entries — final timeout top=1_4_1_r34 — [group-level: none seen] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g161, g242, g243): `1/(sqrt(x)sqrt(x(a+bx+cx^2)))`, `…(a+bx^2+cx^4)`, `sqrt(x)/sqrt(x^3(…))`. **Substrate.** `1_4_2_r26/r27` (expandToSum of the generalized trinomial) → `1_2_4_1_r4` / `1_2_4_2_r3`, `1_1_2_1_r13`. The top-level `1_4_1_r34` fires by 30 s (g242) or by 120 s (g161, g243). **P0.** … — follows from: model flags

- 1.2.4.2 e136: record verified 1.0s -> timeout 30.0s | P0 core verified 1.6s top=1_4_1_r34 | final30 timeout 30.0s top=1_4_1_r34 | final120 timeout 120.1s top=1_4_1_r34

**class 1 g243** — deterministic, 1 entries — final timeout top=1_4_2_r27 — [group-level: none seen] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g161, g242, g243): `1/(sqrt(x)sqrt(x(a+bx+cx^2)))`, `…(a+bx^2+cx^4)`, `sqrt(x)/sqrt(x^3(…))`. **Substrate.** `1_4_2_r26/r27` (expandToSum of the generalized trinomial) → `1_2_4_1_r4` / `1_2_4_2_r3`, `1_1_2_1_r13`. The top-level `1_4_1_r34` fires by 30 s (g242) or by 120 s (g161, g243). **P0.** … — follows from: model flags

- 1.2.4.2 e132: record verified 1.0s -> timeout 30.0s | P0 core verified 1.5s top=1_4_1_r34 | final30 timeout 30.1s top=1_4_2_r27 | final120 timeout 120.1s top=1_4_1_r34

**class 1 g244** — deterministic, 1 entries — final timeout top=1_4_3_r19 — [group-level: none seen] [VERIFY-TIMEOUT]
> `10-p5-attribution.mechanisms-class1-c.md`: `(d+ex+f sqrt(…))^n/(…)`. Both cores put r19 at top (fired). **Nested.** P0: `1_1_2_7_r35`. Substrate: `1_1_2_2_r39` (hypergeometric; binding not inferable). VERIFY-TIMEOUT; all arms timeout. — follows from: not determined from the traces

- 1.3.2 e348: record verified 1.9s -> timeout 30.0s | P0 core verified 2.4s top=1_4_3_r19 | final30 timeout 30.0s top=1_4_3_r19 | final120 timeout 120.1s top=1_4_3_r19

**class 1 g245** — deterministic, 1 entries — final unexpected top=1_1_2_5_r30 — [group-level: IGtQ 1] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g245, g246): `(a+bx^2)^(±3/2)/(sqrt(c+dx^2)sqrt(e+fx^2))`; noun-expected (Unintegrable, 0 steps). **P0.** No-answer through the catch-all `1_1_2_5_r39`. **Substrate.** `1_1_2_5_r30` / `r31` (Rubi `ILtQ[p,0] && GtQ[q,0]` / `LeQ[q,-1]`) accept p=-1/2 through `is(p < 0)`. They reduce through … — follows from: condition retry exposing the ILtQ translation

- 1.1.2.5 e112: record no-answer 0.1s -> unexpected 9.8s | P0 core no-answer 0.1s top=1_1_2_5_r39 | final30 unexpected 9.5s top=1_1_2_5_r30

**class 1 g246** — deterministic, 1 entries — final unexpected top=1_1_2_5_r31 — [group-level: IGtQ 1] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g245, g246): `(a+bx^2)^(±3/2)/(sqrt(c+dx^2)sqrt(e+fx^2))`; noun-expected (Unintegrable, 0 steps). **P0.** No-answer through the catch-all `1_1_2_5_r39`. **Substrate.** `1_1_2_5_r30` / `r31` (Rubi `ILtQ[p,0] && GtQ[q,0]` / `LeQ[q,-1]`) accept p=-1/2 through `is(p < 0)`. They reduce through … — follows from: condition retry exposing the ILtQ translation

- 1.1.2.5 e115: record no-answer 0.1s -> unexpected 2.3s | P0 core no-answer 0.1s top=1_1_2_5_r39 | final30 unexpected 1.8s top=1_1_2_5_r31

**class 1 g247** — deterministic, 1 entries — final unverified top=1_1_1_2_r14 — [group-level: none seen] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `(a+bx)^((-2bc+ad)/(bc-ad))(c+dx)^((bc-2ad)/(-bc+ad))`. Identical fire lists on both cores. All arms unverified, including r4. — follows from: not determined from the traces (answers not recorded)

- 1.1.1.2 e1884: record verified 0.2s -> unverified 0.3s | P0 core verified 0.2s top=1_1_1_2_r14 | final30 unverified 0.3s top=1_1_1_2_r14

**class 1 g248** — deterministic, 1 entries — final unverified top=1_1_1_3_r65 — [group-level: none seen] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md`: `(bx)^m(%pi+dx)^n(%e+fx)^p`. **Substrate.** `1_1_1_3_r65` (AppellF1; c = π, e = %e > 0): the corpus's own 1-step answer, not closed by the zero chain. **P0.** `1_1_1_6_r7`. All arms unverified. — follows from: faithful binding

- 1.1.1.3 e954: record verified 4.7s -> unverified 0.4s | P0 core verified 5.0s top=1_1_1_6_r7 | final30 unverified 0.4s top=1_1_1_3_r65

**class 1 g249** — deterministic, 1 entries — final unverified top=1_1_2_1_r26 — [group-level: none seen] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g206, g207, g208, g249): `1/(-2+3x^2)^(3/4)`, `1/(a+bx^2)^(5/6)`, `1/((-2+3x^2)(-1+3x^2)^(3/4))`, `1/(-2-3x^2)^(3/4)`. **Fires.** Identical fire lists on both cores. Each top-level rule fired, so rubi returned. **Arms.** r4 verified 0.1–0.3 s in all four (MFLAGS). — follows from: model flags

- 1.1.2.2 e915: record verified 0.2s -> unverified 0.4s | P0 core verified 0.2s top=1_1_2_1_r26 | final30 unverified 0.5s top=1_1_2_1_r26

**class 1 g250** — deterministic, 1 entries — final unverified top=1_1_2_7_r13 — [group-level: none seen] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g250, g251): `(a^2-b^2x^2)^(3/2)/(a+bx)^3`, `(d^2-e^2x^2)^(7/2)/(d+ex)^7`. **Substrate.** Rubi's `1_1_2_7_r13/r15` bind; nested `1_1_3_2_r115, 1_1_2_2_r2`. **P0.** `1_4_2_r21` alone. **Arms.** r3 verified 0.4 / 0.5 s. — follows from: condition retry

- 1.2.1.2 e793: record verified 0.6s -> unverified 0.3s | P0 core verified 0.7s top=1_4_2_r21 | final30 unverified 0.3s top=1_1_2_7_r13

**class 1 g251** — deterministic, 1 entries — final unverified top=1_1_2_7_r15 — [group-level: none seen] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g250, g251): `(a^2-b^2x^2)^(3/2)/(a+bx)^3`, `(d^2-e^2x^2)^(7/2)/(d+ex)^7`. **Substrate.** Rubi's `1_1_2_7_r13/r15` bind; nested `1_1_3_2_r115, 1_1_2_2_r2`. **P0.** `1_4_2_r21` alone. **Arms.** r3 verified 0.4 / 0.5 s. — follows from: condition retry

- 1.2.1.2 e809: record verified 0.5s -> unverified 0.3s | P0 core verified 0.7s top=1_4_2_r21 | final30 unverified 0.4s top=1_1_2_7_r15

**class 1 g252** — deterministic, 1 entries — final unverified top=1_1_3_1_r22 — [group-level: IGtQ 1; negQ 1 (both 1)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md`: `1/(1+a+(-1+a)x^4)`. **Substrate.** The top-level `1_1_3_1_r22` (Rubi `IGtQ[(n-2)/4,0] && NegQ[a/b]`) accepts n = 4 ((4-2)/4 = 1/2) with `NegQ[(1+a)/(a-1)]` read true for an unknown sign. Then the prefix chain. **Corpus.** Rubi's n = 4 form `atan((1-a)^(1/4)x/(1+a)^(1/4))`. … — follows from: faithful binding exposing IGtQ and NegQ

- 1.1.3.2 e706: record verified 1.5s -> unverified 1.7s | P0 core verified 1.4s top=1_2_2_1_r7 | final30 unverified 2.3s top=1_1_3_1_r22

**class 1 g253** — deterministic, 1 entries — final unverified top=1_1_3_2_r112 — [group-level: IGtQ 1] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md`: `(dx)^m/sqrt(a+b/(c/x)^(3/2))`. Both cores put r112 at top. **Nested.** Substrate: `1_1_3_2_r107` (accepts p=-1/2 through `is(p < 0)` with symbolic a), `r84`, `r86`. P0 nfires=1. — follows from: faithful binding exposing the ILtQ translation

- 1.1.3.2 e2995: record verified 1.9s -> unverified 0.6s | P0 core verified 1.7s top=1_1_3_2_r112 | final30 unverified 0.5s top=1_1_3_2_r112

**class 1 g254** — deterministic, 1 entries — final unverified top=1_1_3_2_r114 — [group-level: IGtQ 1] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md`: `x^3/(a+b(c+dx)^3)`. Both cores put r114 at top. **Nested.** Substrate: the prefix, `1_1_3_1_r12`, `1_1_3_3_r17`, `1_1_3_7_r37` (n = 3, IGtQ[3/2,0]). P0 nfires=1. — follows from: faithful binding exposing the IGtQ translation

- 1.3.1 e103: record verified 1.3s -> unverified 1.6s | P0 core verified 1.3s top=1_1_3_2_r114 | final30 unverified 1.7s top=1_1_3_2_r114

**class 1 g255** — deterministic, 1 entries — final unverified top=1_1_3_2_r13 — [group-level: IGtQ 1] [ZERO]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g255, g258): `1/(x^4 sqrt(2+2a-2(1+a)+cx^4))`, `1/(x^3 sqrt(…))` (ZERO). **g255.** `1_1_3_2_r13` accepts (m+1)/n+p+1 = -1/4 through `is(… < 0)`, with a the zero form (binding inferred). **g258.** `1_1_3_2_r6`'s closed form divides by the zero form. **P0.** `1_3_3_r17` / `1_2_2_6_r2`. All … — follows from: binding change on the zero-form coefficient (g255 exposing the ILtQ translation)

- 1.2.2.2 e1029: record verified 4.8s -> unverified 0.4s | P0 core verified 4.6s top=1_3_3_r17 | final30 unverified 0.4s top=1_1_3_2_r13

**class 1 g256** — deterministic, 1 entries — final unverified top=1_1_3_2_r35 — [group-level: IGtQ 1] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md`: `sqrt(x)/(1+x^3)`. **Substrate.** `1_1_3_2_r35` accepts m = 1/2 at top level through `is(m > 0)` (Rubi `IGtQ[m,0]`): an integer-m partial-fraction formula applied to m = 1/2, unverified at 0.5 s. The x^(1/2) substitution rule does not fire. **P0.** `1_3_4_r1` → `1_4_1_r34`. All … — follows from: faithful binding exposing the IGtQ translation

- 1.1.3.2 e367: record verified 1.5s -> unverified 0.8s | P0 core verified 1.6s top=1_4_1_r34 | final30 unverified 0.5s top=1_1_3_2_r35

**class 1 g257** — deterministic, 1 entries — final unverified top=1_1_3_2_r5 — [group-level: negQ 1] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md`: `x^(-1-3n/2)/(a+bx^n)`. **Substrate.** The top-level `1_1_3_2_r5` (Rubi `IntegerQ[p] && NegQ[n]`) accepts symbolic n through `%mr_negQ(n)`. Its rewrite `x^(m+np)(b+ax^-n)^p` is algebraically the integrand, so the seen guard hands it to Maxima integrate (rule-text inference). … — follows from: faithful binding exposing the NegQ reading

- 1.1.3.2 e2639: record verified 1.3s -> unverified 0.1s | P0 core verified 1.9s top=1_1_3_2_r110 | final30 unverified 0.1s top=1_1_3_2_r5

**class 1 g258** — deterministic, 1 entries — final unverified top=1_1_3_2_r6 — [group-level: none seen] [ZERO]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g255, g258): `1/(x^4 sqrt(2+2a-2(1+a)+cx^4))`, `1/(x^3 sqrt(…))` (ZERO). **g255.** `1_1_3_2_r13` accepts (m+1)/n+p+1 = -1/4 through `is(… < 0)`, with a the zero form (binding inferred). **g258.** `1_1_3_2_r6`'s closed form divides by the zero form. **P0.** `1_3_3_r17` / `1_2_2_6_r2`. All … — follows from: binding change on the zero-form coefficient (g255 exposing the ILtQ translation)

- 1.2.2.2 e1028: record verified 3.7s -> unverified 0.1s | P0 core verified 3.8s top=1_2_2_6_r2 | final30 unverified 0.1s top=1_1_3_2_r6

**class 1 g259** — deterministic, 1 entries — final unverified top=1_1_3_3_r14 — [group-level: IGtQ 1; negQ 1 (both 1)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g213, g214, g259, g260): `(a+bx^4)/(c+dx^4)`, `(a+bx^4)^2/(c+dx^4)^3`, `(c+dx^4)/(a+bx^4)^2`, `(c+dx^4)/(a+bx^4)`. **Substrate.** The top-level 1.1.3.3 reduction fired → PF-EVEN `1_1_3_1_r14` (n = 4, symbolic) + prefix. **Classes.** g213/g214 time out (VERIFY-TIMEOUT); g259/g260 read unverified at … — follows from: faithful binding exposing IGtQ and NegQ (g214 also condition retry)

- 1.1.3.3 e71: record verified 0.3s -> unverified 2.4s | P0 core verified 0.3s top=1_1_3_3_r60 | final30 unverified 4.7s top=1_1_3_3_r14

**class 1 g260** — deterministic, 1 entries — final unverified top=1_1_3_3_r17 — [group-level: IGtQ 1; negQ 1 (both 1)] [RT-SUM/PF-EVEN]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g213, g214, g259, g260): `(a+bx^4)/(c+dx^4)`, `(a+bx^4)^2/(c+dx^4)^3`, `(c+dx^4)/(a+bx^4)^2`, `(c+dx^4)/(a+bx^4)`. **Substrate.** The top-level 1.1.3.3 reduction fired → PF-EVEN `1_1_3_1_r14` (n = 4, symbolic) + prefix. **Classes.** g213/g214 time out (VERIFY-TIMEOUT); g259/g260 read unverified at … — follows from: faithful binding exposing IGtQ and NegQ (g214 also condition retry)

- 1.1.3.3 e64: record verified 0.2s -> unverified 1.4s | P0 core verified 0.2s top=1_1_3_3_r19 | final30 unverified 2.3s top=1_1_3_3_r17

**class 1 g261** — deterministic, 1 entries — final unverified top=1_1_3_4_r25 — [group-level: IGtQ 1] [FLAT]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g215, g261): `x^k(a+bx^2)/((-c+dx)^(j/2)(c+dx)^(j/2))`. **Substrate.** The top-level `1_1_3_4_r25` fired. Nested: `1_1_2_2_r39` (hypergeometric; accepts p = -3/2 / -1/2 through `is(p < 0)` with a = -c^2; Rubi needs ILtQ or GtQ[a,0]; binding inferred), `1_1_1_6_r2`, `1_1_2_11_r3` … — follows from: the narrow Flat reading (both) + condition retry (g215), exposing the ILtQ translation

- 1.1.3.3 e260: record verified 2.2s -> unverified 1.4s | P0 core verified 2.2s top=1_1_1_6_r2 | final30 unverified 2.0s top=1_1_3_4_r25

**class 1 g262** — deterministic, 1 entries — final unverified top=1_1_3_4_r46 — [group-level: IGtQ 1; negQ 1 (both 1)] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g218, g262): `x/((a+bx^4)(c+dx^4))`, `x^5/(…)`. **Substrate.** The top-level partial-fraction rule fired → `1_1_3_2_r36` on `x/(a+bx^4)` ((4-1)/2 = 3/2; symbolic a/b) + prefix. **Walls.** 25–30 s; arms unverified at 14.7–26.2 s, i.e. at the cap. **P0.** `1_3_4_r3`. — follows from: faithful binding exposing IGtQ and NegQ

- 1.1.3.4 e607: record verified 0.8s -> unverified 25.0s | P0 core verified 1.0s top=1_3_4_r3 | final30 unverified 28.0s top=1_1_3_4_r46

**class 1 g263** — deterministic, 1 entries — final unverified top=1_1_3_7_r37 — [group-level: IGtQ 1] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md`: `(c+dx+ex^2)(a+bx^3)^p`. **Substrate.** The top-level `1_1_3_7_r37` accepts n = 3 (IGtQ[3/2,0]); nested `1_4_1_r23`, `1_3_1_r11`. **P0.** `1_3_4_r20`. — follows from: faithful binding exposing the IGtQ translation

- 1.1.3.8 e474: record verified 1.9s -> unverified 0.7s | P0 core verified 2.4s top=1_3_4_r20 | final30 unverified 0.8s top=1_1_3_7_r37

**class 1 g264** — deterministic, 1 entries — final unverified top=1_1_3_8_r17 — [group-level: none seen] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md`: `(e+fx)/(x sqrt(-1-x^3))`. **Substrate.** The top-level r17 → nested `1_1_3_1_r31` (numeric a = -1, exact), `1_4_1_r23`, `1_1_3_2_r8`, `1_1_1_2_r32`, `1_1_2_1_r11`. **P0.** `1_4_3_r42`. **Arms.** r4 verified 1.0 s; r3 timeout. — follows from: model flags

- 1.3.2 e148: record verified 2.8s -> unverified 2.9s | P0 core verified 2.7s top=1_4_3_r42 | final30 unverified 4.8s top=1_1_3_8_r17

**class 1 g265** — deterministic, 1 entries — final unverified top=1_2_1_1_r17 — [group-level: NE 1] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g265, g267): `1/(quad)^(7/3)`, `(d+ex)/(quad)^(7/3)`. Each has the same top rule on both cores. **Nested.** P0: `1_3_4_r1` (+`1_2_1_1_r17`). Substrate: `1_1_3_2_r17` (NE), `1_1_3_2_r13`, `1_2_1_1_r17`. **Arms.** r4 verified 0.3 s for g267; g265 unverified in all arms. — follows from: not determined (g265); model flags (g267)

- 1.2.1.2 e2492: record verified 2.0s -> unverified 0.6s | P0 core verified 2.0s top=1_2_1_1_r17 | final30 unverified 0.7s top=1_2_1_1_r17

**class 1 g266** — deterministic, 1 entries — final unverified top=1_2_1_2_r107 — [group-level: none seen] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g266, g268): `sqrt(ade+…)/(d+ex)^(3/2)`, `1/(sqrt(d+ex)sqrt(ade+…))`. **Substrate.** The elliptic chain (`1_1_2_3_r42/r48`, `1_2_1_2_r93`, `1_2_1_3_r89`). **P0.** `1_1_1_3_r55` → `1_3_3_r6` / `1_2_1_4_r30`. **Arms.** r4 verified 2.2 / 0.6 s. — follows from: model flags

- 1.2.1.2 e2032: record verified 0.9s -> unverified 2.7s | P0 core verified 1.1s top=1_3_3_r6 | final30 unverified 3.8s top=1_2_1_2_r107

**class 1 g267** — deterministic, 1 entries — final unverified top=1_2_1_2_r13 — [group-level: NE 1] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g265, g267): `1/(quad)^(7/3)`, `(d+ex)/(quad)^(7/3)`. Each has the same top rule on both cores. **Nested.** P0: `1_3_4_r1` (+`1_2_1_1_r17`). Substrate: `1_1_3_2_r17` (NE), `1_1_3_2_r13`, `1_2_1_1_r17`. **Arms.** r4 verified 0.3 s for g267; g265 unverified in all arms. — follows from: not determined (g265); model flags (g267)

- 1.2.1.2 e2491: record verified 2.2s -> unverified 0.4s | P0 core verified 2.2s top=1_2_1_2_r13 | final30 unverified 0.6s top=1_2_1_2_r13

**class 1 g268** — deterministic, 1 entries — final unverified top=1_2_1_2_r93 — [group-level: none seen] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g266, g268): `sqrt(ade+…)/(d+ex)^(3/2)`, `1/(sqrt(d+ex)sqrt(ade+…))`. **Substrate.** The elliptic chain (`1_1_2_3_r42/r48`, `1_2_1_2_r93`, `1_2_1_3_r89`). **P0.** `1_1_1_3_r55` → `1_3_3_r6` / `1_2_1_4_r30`. **Arms.** r4 verified 2.2 / 0.6 s. — follows from: model flags

- 1.2.1.2 e2061: record verified 1.3s -> unverified 0.8s | P0 core verified 1.3s top=1_2_1_4_r30 | final30 unverified 1.1s top=1_2_1_2_r93

**class 1 g269** — deterministic, 1 entries — final unverified top=1_2_1_3_r104 — [group-level: none seen] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `sqrt(d+ex)/((f+gx)sqrt(ade+…))`. Both cores put r104 at top. **Nested.** Substrate: `1_1_2_3_r42`, `1_2_1_2_r93`, `1_1_2_5_r20/r31`, `1_1_1_4_r29`, `1_2_1_3_r99`. P0: `1_4_2_r25, 1_1_1_4_r29, 1_2_1_4_r30`. **Arms.** r3 CN 1.6 s. — follows from: not determined from the traces

- 1.2.1.4 e661: record verified 2.9s -> unverified 14.7s | P0 core verified 2.8s top=1_2_1_3_r104 | final30 unverified 16.0s top=1_2_1_3_r104

**class 1 g270** — deterministic, 1 entries — final unverified top=1_2_1_3_r55 — [group-level: none seen] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md`: `x/((d+ex)(ade+…)^(3/2))`. **Substrate.** `1_2_1_3_r55` binds x as f+gx with f=0 (OPT); nested `1_4_1_r18`. **P0.** `1_2_1_9b_r5` alone. All arms unverified. — follows from: faithful Optional binding

- 1.2.1.4 e481: record verified 3.4s -> unverified 1.9s | P0 core verified 3.5s top=1_2_1_9b_r5 | final30 unverified 2.1s top=1_2_1_3_r55

**class 1 g271** — deterministic, 1 entries — final unverified top=1_2_2_1_r17 — [group-level: none seen] [ZERO]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g271, g272, g273, g274): `1/sqrt(a+bx^2+(2+2c-2(1+c))x^4)`, `1/sqrt(2+2a-2(1+a)+bx^2+cx^4)`, `x^4/sqrt(…)`, `x^2/sqrt(…)` (ZERO). **Substrate.** Quartic rules bind the zero form as a or c (NegQ/Rt/IntPart of it), with nested `1_1_2_3_r42/r48`, `1_2_2_3_r60`, `1_1_2_5_r4`, `1_1_2_4_r55`. **P0.** … — follows from: not determined which binding change (ZERO)

- 1.2.2.2 e1016: record verified 0.3s -> unverified 0.5s | P0 core verified 0.3s top=1_2_1_1_r15 | final30 unverified 0.6s top=1_2_2_1_r17

**class 1 g272** — deterministic, 1 entries — final unverified top=1_2_2_1_r18 — [group-level: none seen] [ZERO]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g271, g272, g273, g274): `1/sqrt(a+bx^2+(2+2c-2(1+c))x^4)`, `1/sqrt(2+2a-2(1+a)+bx^2+cx^4)`, `x^4/sqrt(…)`, `x^2/sqrt(…)` (ZERO). **Substrate.** Quartic rules bind the zero form as a or c (NegQ/Rt/IntPart of it), with nested `1_1_2_3_r42/r48`, `1_2_2_3_r60`, `1_1_2_5_r4`, `1_1_2_4_r55`. **P0.** … — follows from: not determined which binding change (ZERO)

- 1.2.2.2 e998: record verified 0.5s -> unverified 0.5s | P0 core verified 0.5s top=1_1_4_1_r9 | final30 unverified 0.6s top=1_2_2_1_r18

**class 1 g273** — deterministic, 1 entries — final unverified top=1_2_2_2_r16 — [group-level: none seen] [ZERO]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g271, g272, g273, g274): `1/sqrt(a+bx^2+(2+2c-2(1+c))x^4)`, `1/sqrt(2+2a-2(1+a)+bx^2+cx^4)`, `x^4/sqrt(…)`, `x^2/sqrt(…)` (ZERO). **Substrate.** Quartic rules bind the zero form as a or c (NegQ/Rt/IntPart of it), with nested `1_1_2_3_r42/r48`, `1_2_2_3_r60`, `1_1_2_5_r4`, `1_1_2_4_r55`. **P0.** … — follows from: not determined which binding change (ZERO)

- 1.2.2.2 e1012: record verified 1.4s -> unverified 1.4s | P0 core verified 1.4s top=1_4_2_r6 | final30 unverified 1.7s top=1_2_2_2_r16

**class 1 g274** — deterministic, 1 entries — final unverified top=1_2_2_2_r34 — [group-level: none seen] [ZERO]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g271, g272, g273, g274): `1/sqrt(a+bx^2+(2+2c-2(1+c))x^4)`, `1/sqrt(2+2a-2(1+a)+bx^2+cx^4)`, `x^4/sqrt(…)`, `x^2/sqrt(…)` (ZERO). **Substrate.** Quartic rules bind the zero form as a or c (NegQ/Rt/IntPart of it), with nested `1_1_2_3_r42/r48`, `1_2_2_3_r60`, `1_1_2_5_r4`, `1_1_2_4_r55`. **P0.** … — follows from: not determined which binding change (ZERO)

- 1.2.2.2 e1014: record verified 1.4s -> unverified 1.6s | P0 core verified 1.4s top=1_4_2_r6 | final30 unverified 1.8s top=1_2_2_2_r34

**class 1 g275** — deterministic, 1 entries — final unverified top=1_2_2_2_r35 — [group-level: none seen] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md`: `(dx)^m(a+bx^2+cx^4)^p`. **Substrate.** `1_2_2_2_r35` (FracPart rewrite) → `1_1_2_4_r66` (AppellF1): Rubi's 2-step answer, not closed. **P0.** `1_4_2_r19` → `1_3_4_r9`. All arms unverified. — follows from: faithful binding (as g120)

- 1.2.2.2 e1114: record verified 3.0s -> unverified 0.8s | P0 core verified 2.6s top=1_3_4_r9 | final30 unverified 0.9s top=1_2_2_2_r35

**class 1 g276** — deterministic, 1 entries — final unverified top=1_2_2_7_r7 — [group-level: none seen] [not determined]
> `10-p5-attribution.mechanisms-class1-c.md`: `(√a+x^2√c)/((d+ex^2)sqrt(a+bx^2+cx^4))` (1-step corpus). **Substrate.** `1_2_2_7_r7` (Pr split) → nested `1_4_1_r18`, `9_1_r8`. **P0.** `1_2_2_7_r30` after a chain. **Arms.** r3 CN 0.6 s. — follows from: not determined from the traces

- 1.2.2.7 e30: record verified 2.4s -> unverified 3.1s | P0 core verified 2.6s top=1_2_2_7_r30 | final30 unverified 4.1s top=1_2_2_7_r7

**class 1 g277** — deterministic, 1 entries — final unverified top=1_2_4_2_r9 — [group-level: none seen] [MFLAGS]
> `10-p5-attribution.mechanisms-class1-c.md`: `x^(3/2)(ax+bx^3+cx^5)^(3/2)`. **Substrate.** The top-level r9 fired; nested `1_2_4_4_r6/r10`, `1_3_3_r6` (binding not inferable), `1_4_1_r34`. **P0.** `1_3_3_r15/r14` → `1_4_1_r34`. **Arms.** r4 verified 17.3 s; r3 unverified 4.5 s. — follows from: model flags

- 1.2.4.2 e109: record verified 2.4s -> unverified 18.6s | P0 core verified 3.4s top=1_4_1_r34 | final30 unverified 29.6s top=1_2_4_2_r9

**class 1 g278** — deterministic, 1 entries — final unverified top=1_3_3_r7 — [group-level: IGtQ 1] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g278, g280): `(1+x)/((1+x-√3)sqrt(1+x^3))`, `(e+fx)/((2+x)sqrt(1-x^3))`. **Substrate.** The nested `1_3_3_r7` (Rubi `ILtQ[q,0]`) accepts q=-1/2 on the shared factor. Also nested: `1_1_3_1_r30`, `1_2_1_2_r88`, `1_4_3_r42/r34`, `1_2_1_3_r30/r104` (g278) and `1_4_1_r18` (g280). **P0.** … — follows from: condition retry exposing the ILtQ translation

- 1.3.2 e103: record verified 2.5s -> unverified 4.5s | P0 core verified 2.5s top=1_4_3_r42 | final30 unverified 6.6s top=1_3_3_r7

**class 1 g279** — deterministic, 1 entries — final unverified top=1_4_2_r11 — [group-level: MUL 1] [OPT]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g169, g279): `sqrt(1/x+sqrt(1/x))`, `(ax^m+bx^(1+m+mp))^p`, `(x^m(a+bx^(1+mp)))^p`. **Substrate.** `1_1_4_1_r1` answers (at top, or nested under `1_4_2_r11`). Its repl `b*(n - j) (p + 1)*x^(n - 1)` lacks a `*` (MUL), so the answer cannot equal Rubi's. **P0.** `1_2_3_1_r2` / `1_1_4_4_r11` / … — follows from: faithful binding reaching a repl with the MUL translation defect

- 1.1.4.2 e445: record verified 0.7s -> unverified 0.2s | P0 core verified 0.7s top=1_4_2_r11 | final30 unverified 0.2s top=1_4_2_r11

**class 1 g280** — deterministic, 1 entries — final unverified top=1_4_3_r37 — [group-level: IGtQ 1] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md` (one line for g278, g280): `(1+x)/((1+x-√3)sqrt(1+x^3))`, `(e+fx)/((2+x)sqrt(1-x^3))`. **Substrate.** The nested `1_3_3_r7` (Rubi `ILtQ[q,0]`) accepts q=-1/2 on the shared factor. Also nested: `1_1_3_1_r30`, `1_2_1_2_r88`, `1_4_3_r42/r34`, `1_2_1_3_r30/r104` (g278) and `1_4_1_r18` (g280). **P0.** … — follows from: condition retry exposing the ILtQ translation

- 1.3.2 e61: record verified 2.3s -> unverified 3.2s | P0 core verified 2.3s top=1_4_3_r37 | final30 unverified 4.5s top=1_4_3_r37

**class 1 g281** — slow-correct, 85 entries — final class/top per entry (see samples) — [group-level: none seen] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md`: P0 core verified in all 85 (0.9–25.6 s, median 2.5 s). **30 s.** final30 times out in all 85; 75 have no fire flushed. **120 s.** final120 verifies all 85 at 30.5–118.9 s (q1 46.5, median 55.5, q3 62.1 s). Histogram by 10 s bins: 30s 8, 40s 20, 50s 32, 60s 6, 70s 6, 80s 5, 90s … — follows from: condition retry (cost; 75/85 verify in 0.2–7.9 s with it off)

- 1.1.1.3 e536: record verified 1.9s -> timeout 30.1s | P0 core verified 1.8s top=1_1_1_3_r19 | final30 timeout 30.0s top=- | final120 verified 59.6s top=1_1_1_3_r19
- 1.2.1.3 e781: record verified 2.9s -> timeout 30.0s | P0 core verified 2.9s top=1_4_1_r34 | final30 timeout 30.1s top=- | final120 verified 44.3s top=1_2_1_3_r4
- 1.3.2 e477: record verified 1.6s -> timeout 30.0s | P0 core verified 2.4s top=1_1_3_2_r114 | final30 timeout 30.0s top=- | final120 verified 75.0s top=1_1_3_2_r114

**class 1 g282** — noise, 6 entries — final class/top per entry (see samples) — [group-level: none seen] [RETRY]
> `10-p5-attribution.mechanisms-class1-c.md`: the record reads timeout at 30.0–30.1 s. final30 verifies at 25.9–29.4 s and final120 at 26.4–31.0 s; the 100 s re-check verifies at 24.9–30.7 s. **P0.** 1.0–14.5 s. **Routes.** e832–e835 run `9_1_r12, 1_4_1_r7, 1_1_1_3_r5, 1_2_1_3_r7` against P0's `1_4_1_r34`; e262 runs … — follows from: condition retry (cost puts the walls at the cap)

- 1.1.1.7 e7: record verified 15.2s -> timeout 30.0s | P0 core verified 14.5s top=1_1_1_7_r15 | final30 verified 25.9s top=1_1_1_7_r15 | final120 verified 26.4s top=1_1_1_7_r15
- 1.2.1.3 e833: record verified 2.8s -> timeout 30.0s | P0 core verified 2.8s top=1_4_1_r34 | final30 verified 29.4s top=1_2_1_3_r7 | final120 verified 29.7s top=1_2_1_3_r7
- 1.2.1.3 e835: record verified 2.8s -> timeout 30.0s | P0 core verified 2.8s top=1_4_1_r34 | final30 verified 28.9s top=1_2_1_3_r7 | final120 verified 30.3s top=1_2_1_3_r7

**class 1 g283** — p0-noise, 1 entries — final class/top per entry (see samples) — [group-level: none seen] [P0-NOISE]
> `10-p5-attribution.mechanisms-class1-c.md`: 1.2.1.5 e112. **P0.** The P0 record verified at 29.6 s, at the cap; the probe's P0 core times out at 30.0 s with no fire. **Final.** 30.0 / 120.1 s timeout (only `9_1_r8` fired); 100 s re-check timeout 100.1 s. All arms timeout. — follows from: P0-side timing noise (P0's own PASS was at the cap)

- 1.2.1.5 e112: record verified 29.6s -> timeout 30.0s | P0 core timeout 30.0s top=- | final30 timeout 30.0s top=9_1_r8 | final120 timeout 120.1s top=9_1_r8

## 6. Acceptance template

Answer each line with `accepted`, `accepted except <file> e<n> …` or `rejected`.

- class 2 g1 (5 entries): 
- class 2 g2 (4 entries): 
- class 2 g3 (3 entries): 
- class 2 g4 (2 entries): 
- class 2 g5 (2 entries): 
- class 2 g6 (1 entries): 
- class 2 g7 (1 entries): 
- class 2 g8 (1 entries): 
- class 2 g9 (1 entries): 
- class 2 g10 (1 entries): 
- class 2 g11 (1 entries): 
- class 2 g12 (2 entries): 
- class 3 g1 (17 entries): 
- class 3 g2 (13 entries): 
- class 3 g3 (11 entries): 
- class 3 g4 (10 entries): 
- class 3 g5 (7 entries): 
- class 3 g6 (7 entries): 
- class 3 g7 (7 entries): 
- class 3 g8 (6 entries): 
- class 3 g9 (6 entries): 
- class 3 g10 (6 entries): 
- class 3 g11 (4 entries): 
- class 3 g12 (4 entries): 
- class 3 g13 (3 entries): 
- class 3 g14 (3 entries): 
- class 3 g15 (3 entries): 
- class 3 g16 (3 entries): 
- class 3 g17 (3 entries): 
- class 3 g18 (3 entries): 
- class 3 g19 (3 entries): 
- class 3 g20 (3 entries): 
- class 3 g21 (3 entries): 
- class 3 g22 (3 entries): 
- class 3 g23 (3 entries): 
- class 3 g24 (3 entries): 
- class 3 g25 (3 entries): 
- class 3 g26 (3 entries): 
- class 3 g27 (2 entries): 
- class 3 g28 (2 entries): 
- class 3 g29 (2 entries): 
- class 3 g30 (2 entries): 
- class 3 g31 (2 entries): 
- class 3 g32 (2 entries): 
- class 3 g33 (2 entries): 
- class 3 g34 (2 entries): 
- class 3 g35 (2 entries): 
- class 3 g36 (2 entries): 
- class 3 g37 (2 entries): 
- class 3 g38 (2 entries): 
- class 3 g39 (1 entries): 
- class 3 g40 (1 entries): 
- class 3 g41 (1 entries): 
- class 3 g42 (1 entries): 
- class 3 g43 (1 entries): 
- class 3 g44 (1 entries): 
- class 3 g45 (1 entries): 
- class 3 g46 (1 entries): 
- class 3 g47 (1 entries): 
- class 3 g48 (1 entries): 
- class 3 g49 (1 entries): 
- class 3 g50 (1 entries): 
- class 3 g51 (1 entries): 
- class 3 g52 (1 entries): 
- class 3 g53 (1 entries): 
- class 3 g54 (1 entries): 
- class 3 g55 (1 entries): 
- class 1 g1 (147 entries): 
- class 1 g2 (99 entries): 
- class 1 g3 (80 entries): 
- class 1 g4 (62 entries): 
- class 1 g5 (61 entries): 
- class 1 g6 (47 entries): 
- class 1 g7 (45 entries): 
- class 1 g8 (44 entries): 
- class 1 g9 (43 entries): 
- class 1 g10 (41 entries): 
- class 1 g11 (37 entries): 
- class 1 g12 (32 entries): 
- class 1 g13 (29 entries): 
- class 1 g14 (28 entries): 
- class 1 g15 (26 entries): 
- class 1 g16 (24 entries): 
- class 1 g17 (19 entries): 
- class 1 g18 (19 entries): 
- class 1 g19 (18 entries): 
- class 1 g20 (18 entries): 
- class 1 g21 (17 entries): 
- class 1 g22 (17 entries): 
- class 1 g23 (16 entries): 
- class 1 g24 (15 entries): 
- class 1 g25 (15 entries): 
- class 1 g26 (15 entries): 
- class 1 g27 (15 entries): 
- class 1 g28 (14 entries): 
- class 1 g29 (13 entries): 
- class 1 g30 (11 entries): 
- class 1 g31 (10 entries): 
- class 1 g32 (10 entries): 
- class 1 g33 (10 entries): 
- class 1 g34 (10 entries): 
- class 1 g35 (10 entries): 
- class 1 g36 (10 entries): 
- class 1 g37 (10 entries): 
- class 1 g38 (9 entries): 
- class 1 g39 (9 entries): 
- class 1 g40 (9 entries): 
- class 1 g41 (8 entries): 
- class 1 g42 (8 entries): 
- class 1 g43 (8 entries): 
- class 1 g44 (7 entries): 
- class 1 g45 (7 entries): 
- class 1 g46 (7 entries): 
- class 1 g47 (7 entries): 
- class 1 g48 (7 entries): 
- class 1 g49 (7 entries): 
- class 1 g50 (7 entries): 
- class 1 g51 (7 entries): 
- class 1 g52 (7 entries): 
- class 1 g53 (7 entries): 
- class 1 g54 (7 entries): 
- class 1 g55 (6 entries): 
- class 1 g56 (6 entries): 
- class 1 g57 (6 entries): 
- class 1 g58 (6 entries): 
- class 1 g59 (6 entries): 
- class 1 g60 (6 entries): 
- class 1 g61 (6 entries): 
- class 1 g62 (6 entries): 
- class 1 g63 (6 entries): 
- class 1 g64 (5 entries): 
- class 1 g65 (5 entries): 
- class 1 g66 (5 entries): 
- class 1 g67 (5 entries): 
- class 1 g68 (5 entries): 
- class 1 g69 (5 entries): 
- class 1 g70 (5 entries): 
- class 1 g71 (5 entries): 
- class 1 g72 (5 entries): 
- class 1 g73 (5 entries): 
- class 1 g74 (5 entries): 
- class 1 g75 (4 entries): 
- class 1 g76 (4 entries): 
- class 1 g77 (4 entries): 
- class 1 g78 (4 entries): 
- class 1 g79 (4 entries): 
- class 1 g80 (4 entries): 
- class 1 g81 (4 entries): 
- class 1 g82 (4 entries): 
- class 1 g83 (4 entries): 
- class 1 g84 (4 entries): 
- class 1 g85 (4 entries): 
- class 1 g86 (4 entries): 
- class 1 g87 (4 entries): 
- class 1 g88 (4 entries): 
- class 1 g89 (4 entries): 
- class 1 g90 (4 entries): 
- class 1 g91 (4 entries): 
- class 1 g92 (4 entries): 
- class 1 g93 (3 entries): 
- class 1 g94 (3 entries): 
- class 1 g95 (3 entries): 
- class 1 g96 (3 entries): 
- class 1 g97 (3 entries): 
- class 1 g98 (3 entries): 
- class 1 g99 (3 entries): 
- class 1 g100 (3 entries): 
- class 1 g101 (3 entries): 
- class 1 g102 (3 entries): 
- class 1 g103 (3 entries): 
- class 1 g104 (3 entries): 
- class 1 g105 (3 entries): 
- class 1 g106 (3 entries): 
- class 1 g107 (3 entries): 
- class 1 g108 (3 entries): 
- class 1 g109 (3 entries): 
- class 1 g110 (3 entries): 
- class 1 g111 (3 entries): 
- class 1 g112 (3 entries): 
- class 1 g113 (3 entries): 
- class 1 g114 (3 entries): 
- class 1 g115 (3 entries): 
- class 1 g116 (3 entries): 
- class 1 g117 (3 entries): 
- class 1 g118 (3 entries): 
- class 1 g119 (3 entries): 
- class 1 g120 (3 entries): 
- class 1 g121 (2 entries): 
- class 1 g122 (2 entries): 
- class 1 g123 (2 entries): 
- class 1 g124 (2 entries): 
- class 1 g125 (2 entries): 
- class 1 g126 (2 entries): 
- class 1 g127 (2 entries): 
- class 1 g128 (2 entries): 
- class 1 g129 (2 entries): 
- class 1 g130 (2 entries): 
- class 1 g131 (2 entries): 
- class 1 g132 (2 entries): 
- class 1 g133 (2 entries): 
- class 1 g134 (2 entries): 
- class 1 g135 (2 entries): 
- class 1 g136 (2 entries): 
- class 1 g137 (2 entries): 
- class 1 g138 (2 entries): 
- class 1 g139 (2 entries): 
- class 1 g140 (2 entries): 
- class 1 g141 (2 entries): 
- class 1 g142 (2 entries): 
- class 1 g143 (2 entries): 
- class 1 g144 (2 entries): 
- class 1 g145 (2 entries): 
- class 1 g146 (2 entries): 
- class 1 g147 (2 entries): 
- class 1 g148 (2 entries): 
- class 1 g149 (2 entries): 
- class 1 g150 (2 entries): 
- class 1 g151 (2 entries): 
- class 1 g152 (2 entries): 
- class 1 g153 (2 entries): 
- class 1 g154 (2 entries): 
- class 1 g155 (2 entries): 
- class 1 g156 (2 entries): 
- class 1 g157 (2 entries): 
- class 1 g158 (2 entries): 
- class 1 g159 (2 entries): 
- class 1 g160 (2 entries): 
- class 1 g161 (2 entries): 
- class 1 g162 (2 entries): 
- class 1 g163 (2 entries): 
- class 1 g164 (2 entries): 
- class 1 g165 (2 entries): 
- class 1 g166 (2 entries): 
- class 1 g167 (2 entries): 
- class 1 g168 (2 entries): 
- class 1 g169 (2 entries): 
- class 1 g170 (2 entries): 
- class 1 g171 (2 entries): 
- class 1 g172 (1 entries): 
- class 1 g173 (1 entries): 
- class 1 g174 (1 entries): 
- class 1 g175 (1 entries): 
- class 1 g176 (1 entries): 
- class 1 g177 (1 entries): 
- class 1 g178 (1 entries): 
- class 1 g179 (1 entries): 
- class 1 g180 (1 entries): 
- class 1 g181 (1 entries): 
- class 1 g182 (1 entries): 
- class 1 g183 (1 entries): 
- class 1 g184 (1 entries): 
- class 1 g185 (1 entries): 
- class 1 g186 (1 entries): 
- class 1 g187 (1 entries): 
- class 1 g188 (1 entries): 
- class 1 g189 (1 entries): 
- class 1 g190 (1 entries): 
- class 1 g191 (1 entries): 
- class 1 g192 (1 entries): 
- class 1 g193 (1 entries): 
- class 1 g194 (1 entries): 
- class 1 g195 (1 entries): 
- class 1 g196 (1 entries): 
- class 1 g197 (1 entries): 
- class 1 g198 (1 entries): 
- class 1 g199 (1 entries): 
- class 1 g200 (1 entries): 
- class 1 g201 (1 entries): 
- class 1 g202 (1 entries): 
- class 1 g203 (1 entries): 
- class 1 g204 (1 entries): 
- class 1 g205 (1 entries): 
- class 1 g206 (1 entries): 
- class 1 g207 (1 entries): 
- class 1 g208 (1 entries): 
- class 1 g209 (1 entries): 
- class 1 g210 (1 entries): 
- class 1 g211 (1 entries): 
- class 1 g212 (1 entries): 
- class 1 g213 (1 entries): 
- class 1 g214 (1 entries): 
- class 1 g215 (1 entries): 
- class 1 g216 (1 entries): 
- class 1 g217 (1 entries): 
- class 1 g218 (1 entries): 
- class 1 g219 (1 entries): 
- class 1 g220 (1 entries): 
- class 1 g221 (1 entries): 
- class 1 g222 (1 entries): 
- class 1 g223 (1 entries): 
- class 1 g224 (1 entries): 
- class 1 g225 (1 entries): 
- class 1 g226 (1 entries): 
- class 1 g227 (1 entries): 
- class 1 g228 (1 entries): 
- class 1 g229 (1 entries): 
- class 1 g230 (1 entries): 
- class 1 g231 (1 entries): 
- class 1 g232 (1 entries): 
- class 1 g233 (1 entries): 
- class 1 g234 (1 entries): 
- class 1 g235 (1 entries): 
- class 1 g236 (1 entries): 
- class 1 g237 (1 entries): 
- class 1 g238 (1 entries): 
- class 1 g239 (1 entries): 
- class 1 g240 (1 entries): 
- class 1 g241 (1 entries): 
- class 1 g242 (1 entries): 
- class 1 g243 (1 entries): 
- class 1 g244 (1 entries): 
- class 1 g245 (1 entries): 
- class 1 g246 (1 entries): 
- class 1 g247 (1 entries): 
- class 1 g248 (1 entries): 
- class 1 g249 (1 entries): 
- class 1 g250 (1 entries): 
- class 1 g251 (1 entries): 
- class 1 g252 (1 entries): 
- class 1 g253 (1 entries): 
- class 1 g254 (1 entries): 
- class 1 g255 (1 entries): 
- class 1 g256 (1 entries): 
- class 1 g257 (1 entries): 
- class 1 g258 (1 entries): 
- class 1 g259 (1 entries): 
- class 1 g260 (1 entries): 
- class 1 g261 (1 entries): 
- class 1 g262 (1 entries): 
- class 1 g263 (1 entries): 
- class 1 g264 (1 entries): 
- class 1 g265 (1 entries): 
- class 1 g266 (1 entries): 
- class 1 g267 (1 entries): 
- class 1 g268 (1 entries): 
- class 1 g269 (1 entries): 
- class 1 g270 (1 entries): 
- class 1 g271 (1 entries): 
- class 1 g272 (1 entries): 
- class 1 g273 (1 entries): 
- class 1 g274 (1 entries): 
- class 1 g275 (1 entries): 
- class 1 g276 (1 entries): 
- class 1 g277 (1 entries): 
- class 1 g278 (1 entries): 
- class 1 g279 (1 entries): 
- class 1 g280 (1 entries): 
- class 1 g281 (85 entries): 
- class 1 g282 (6 entries): 
- class 1 g283 (1 entries): 
- new timeouts (class 2 18, class 3 62, class 1 941; entries in each summary's `NEW TIMEOUTS` block): 
- rubi_hybrid (§4): keep + exact comparison as a translation fix | delete as planned: 
