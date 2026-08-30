# Class-3 Deferred Campaign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Shrink the class-3 `deferred` population (1,033 entries; 788 of them with a
non-noun native `integrate` answer) by measuring the per-entry decline mechanism
(Phase 1 probe), fixing what the distribution says to fix (Phase 2: a per-candidate
implicit-1 dispatch pass, condition port-bugs, rule ports, documented declines), and
re-measuring all three classes against the standing regression gates (Phase 3).

**Architecture:** A gated fourth dispatch pass in the existing implicit-exponent-1
seam (`maxima_rubi_implicit1.lisp` findfun shadow, generalized from one wrapped
candidate to a per-candidate index) plus a committed triage probe that measures, for
every deferred entry: the production dispatch trace, a per-bare-factor wrapped table
sweep (the pass-4 prototype), and a pattern/cond drill over all 333 class-3 rules
generated from the rules source text. Phase 2 is chosen from the measured
distribution only; Phase 3 re-runs the full class-3 corpus (A/B vs the campaign
baseline) and the full class-1 and class-2 corpora (A/B vs the standing accepted
records) — the standing Layer-B regression gate for any shared-dispatch change.

**Tech Stack:** Maxima `branch_5_50_base_84_g4204fb669` (build date
2026-08-29 17:58:20) / SBCL 2.6.7; package Lisp in `maxima_rubi_*.lisp` (defmfun /
findfun shadow / mlambda pipeline); generated rules in `rules/class{1,2,3}/*.mac`;
Python 3 shard harnesses in `test/` and `probes/`; corpus records as merged text
files under `test/`.

**Spec:** `docs/superpowers/specs/2026-08-30-class3-deferred-campaign-design.md`
(committed `471bf67` + calibration fix `cd6cc57`). Where this plan refines the spec
mechanism (it does, in one place — the materialization variant of the pass-4
prototype is replaced by the drill's binding evidence; see the Task 1 design note),
the plan says so explicitly.

## Global Constraints

Every task's requirements implicitly include this section.

- **Build (stamp, never pin):** Maxima `branch_5_50_base_84_g4204fb669` (build date
  2026-08-29 17:58:20) / SBCL 2.6.7 / x86_64-pc-linux-gnu — the installed build.
  Every committed measurement output is stamped with `build_info()` fields
  (Maxima-version, build date, host type), the record-header idiom.
- **TLS:** ANY maxima process that loads rule files runs with `-X "--tls-limit
  100000"` (TWO argv tokens, not `--tls-limit=N`). Standalone core runs:
  `<maxima-binary> --tls-limit 100000 --core test/mr_rules.core --noinform
  --very-quiet -b file.mac` (the core's baked toplevel is `cl-user::run` — no
  `--eval`).
- **Layer A gate:** `maxima --very-quiet -b test_maxima_rubi.mac` must end `Results:
  <n> passed, 0 failed`. n = 743 before this campaign's tests land; it grows only by
  the tests a task adds. A mid-run death (no Results line) is a failure.
- **Byte-identity gate:** `python3 generator/generate_rules.py --class 1` (3026 OK),
  `--class 2` (125 OK), `--class 3` (333 OK) reproduce `rules/` byte-identically —
  `git status --porcelain rules/` empty afterwards. A deliberate rule change
  (Phase 2 B/C) regenerates, commits the intended `rules/` diff, and re-runs the gate
  so the OTHER files stay byte-identical.
- **Rules core:** `test/mr_rules.core` bakes loader + utils + dispatch lisp +
  implicit-1 lisp + pass-4 lisp (new) + every `rules/class{1,2,3}/*.mac`. The baked
  file list lives in TWO places that must stay in sync: `test/build_rules_core.sh`
  (FP list, lines 36-39) and `test/corpus_driver.py` `_core_fingerprint()` (lines
  161-169). Rebuild with `sh test/build_rules_core.sh` after any baked-file change;
  the driver refuses a stale core (fingerprint mismatch vs the stamp
  `test/mr_rules.core.stamp`).
- **30 s corpus cap STAYS** (standing user decision 2026-08-27). The triage probe's
  per-entry 60 s cap is a safety cap only, not policy.
- **Maxima build quirks (measured 2026-08-30, production-immune but probe-fatal):**
  - relational operators do NOT auto-evaluate at top level (`0 = 0` stays a noun);
    `is()` and if-test positions force evaluation. Codebase idiom: `is(expr)` for
    boolean use.
  - `for (x : list) do` (iterator form) errors; `for x : a thru b do` works.
  - `#=` and `<>` are parse errors; use lone `#` (is()-guarded / if-test) or `=`.
  - `element(list, i)` and `car` are not Maxima-level functions; use
    `first`/`rest`/`part`.
  - `return(value)` inside a `for` is LOOP-LEVEL in this build (breaks the for,
    value discarded) — the codebase idiom: track the result in `ans`, bare
    `return()` to break, return `ans` after the loop (the `%mr_dispatch` pattern,
    `maxima_rubi_utils.mac:140-176`).
  - a `defmfun` with a fixed parameter list is NOT callable from Maxima in this
    build (the call stays a noun); `(&rest args)` dispatch is the only callable form
    (`maxima_rubi_dispatch.lisp` note).
  - defmfun symbol case: an ALL-UPPERCASE typed name keeps its case
    (`|$%MR_DISPATCH_REV|` → callable as `%mr_dispatch_rev` or `%MR_DISPATCH_REV`);
    a lowercase name is uppercased. Use ALL-UPPERCASE for new defmfun names.
  - a boolean anywhere in a rule replacement is a misfire (`%mr_containsBoolean`,
    `%mr_boolcheck`).
- **Records (the A/B inputs):** `test/corpus_class3.out` — campaign baseline package
  run, 1,736 PASS / 3,085, 1,033 deferred; `test/corpus_class3.baseline.out` —
  integrate baseline, 1,441 PASS; `test/corpus_class1.out` — standing 20,069 /
  25,697; `test/corpus_class2.out` — standing 594 / 965. Entry line format (all
  records): `<class:14s> t=<dt:6.1f>s <rel> e<n> L<lineno>` where `<rel>` =
  `3 Logarithms/<filename>.mac`.
- **Target mass (spec §2.1):** 788 = 329 certain (baseline verified 313 + expected
  16) + 459 baseline-unverified. Per file (788): 3.1.4 216, 3.4 132, 3.2.2 131,
  3.3 110, 3.2.1 81, 3.5 68, 3.1.5 28, 3.2.3 22. The record reports the 329 subset
  separately.
- **Git:** branch `class3-deferred` cut from `master` (`cd6cc57`). NO push (no
  remote access; standing rule). No `Co-Authored-By` trailers. Commit messages in
  repo style (lowercase imperative subject, no trailer).
- **SDD loop (per task):** task brief from this plan's task section → implementer
  subagent (`task`, `general`) → `review-package BASE HEAD` (**bash** only) →
  reviewer subagent → fixes via `task_id` resume → controller appends the ledger
  entry to `.superpowers/sdd/progress.md` (new section `## Campaign: class-3
  deferred`) → controller commits.
- **Measured-claims discipline:** every non-trivial claim in the campaign record
  cites a committed, re-runnable probe or a committed record.
- **Reference clones:** `reference/rubi` (pinned
  `61e9c18ea248061cd83c67882f7c91a73cef912d`, per the rule-file headers) — the
  adjudication reads the 11 class-3 `.m` files under
  `reference/rubi/Rubi/IntegrationRules/3 Logarithms/` (3.1.1 … 3.5, one per
  ported family; the `.nb` siblings are ignored).
- **Pinned mechanism facts (measured 2026-08-30, spec §2.2, close-out ledger):**
  `f2 = (d+e*x)*(a+b*log(c*x^n))` — production pass 3 fires a 3_1_5 rule (r27 the
  catch-all) and answers. `f1 = x^3*(d+e*x)*(a+b*log(c*x^n))` — 0-fires all three
  passes; `_mr_pat_3_1_5_r27(f1, x)` = false (the explicit `x^3` is findfun's
  single candidate for the power slot; the valid binding
  `Polyx := x^3*(d+e*x)`, log factor at exponent 1, is unreachable).
  `f5 = (d+e*x)*(a+b*log(c*x^n))/x` — mquot top, 0-fires;
  `%mr_polynomialQ((d+e*x)/x, x)` = false. F_-domain rows 3.1.5 e186-e197: the
  eight m=1 rows are answered on pass 3 by the 3.5 catch-all `3_5_r43` (4 verified);
  the four m=2 rows (e194-e197) 0-fire in all three passes (deferred); the ported
  F_ headvar rules (3_1_5 r58/r59) fire on none — the e:=0 identity-default corner.

## File Structure

Created:

| File | Responsibility |
|---|---|
| `maxima_rubi_pass4.lisp` | Pass-4 Lisp seam: the `*mr-implicit1-which*` consumers — the two Maxima-level setters (`%mr_p4_setrev`, `%mr_p4_setwhich`), the single gated scan `%mr_dispatch_p4`, and the diagnostic `%mr_p4_diag`. Loads after `maxima_rubi_implicit1.lisp`. |
| `probes/corpus/06-class3-deferred-mechanisms.py` | The triage probe: deferred-set extraction from the two records, per-entry `.mac` generation (production trace + census + sweep + drill, drill blocks generated from the `rules/class3/*.mac` source text), 24-shard LPT launcher (mirror of `test/launch_class_shards.py`), one fresh core subprocess per entry (60 s safety cap), merge + distribution, `--calibrate` mode (the 16-entry calibration set with hard assertions). |
| `probes/corpus/06-class3-deferred-mechanisms.run` | Shell entry: `--calibrate` (asserts) then `--gen` + `--launch`. |
| `probes/corpus/06-class3-deferred-mechanisms.out` | Committed triage distribution (Task 3). |
| `probes/corpus/06-class3-deferred-mechanisms.calibrate.out` | Committed calibration table (Task 1). |
| `docs/corpus-class3-deferred-uplift.md` | Campaign acceptance record: skeleton + Phase-2 decision record (Task 3), completed at close (Task 6). |

Modified:

| File | Change |
|---|---|
| `maxima_rubi_implicit1.lisp` | `*mr-implicit1-which*` defvar; `mr-implicit1-findfun` gains the index branch (nil = byte-identical pass-3 behavior). |
| `maxima_rubi.mac` | Loads `maxima_rubi_pass4.lisp` with witness `mr_witness_pass4`, right after the implicit-1 load (line 90). |
| `maxima_rubi_utils.mac` | `%mr_barefactors`, `%mr_p4_once`, `%mr_pass4_scan` (the shared Maxima driver); Task 4 adds the `mr_top` pass-4 wiring between the pass-3 block (line 321) and the final fall-through (line 322). |
| `test/build_rules_core.sh` | `maxima_rubi_pass4.lisp` added to the FP file list (line 36-39). |
| `test/corpus_driver.py` | `maxima_rubi_pass4.lisp` added to `_core_fingerprint()` rels (lines 161-169). |
| `test_maxima_rubi.mac` | Task 4: `test_pass4_*()` functions + main-list call. |
| `test/mr_rules.core` + `.stamp` | Rebuilt (Task 1, and again after any Task 4 baked-file change). |
| `.scratch/class1-ab-remainders/issues/04-matcher-backtracking-feasibility.md` | Task 6: status → partially answered. |
| `todo/TODO.md`, `AGENTS.md` | Task 6: working state; Layer-A count if it changed. |
| `test/corpus_class{3,1,2}.out` | Task 5: Phase-3 re-run records (each backed up first). |

## Design note: the pass-4 mechanism (plan decision, refines spec §3.1/§2.4)

The spec's prototype text says "each bare factor fᵢ … the integrand with fᵢ
replaced by the raw `(mexpt fᵢ 1)`". Building that product requires a hand-built
MTIMES object, which the measured round-trip note in `maxima_rubi_implicit1.lisp:43-49`
says does NOT survive the lisp→Maxima boundary (only a single raw power does — which
is why pass 3's lift wraps the whole integrand in ONE power). This plan replaces the
materialization with the **shadow-index** mechanism: the existing findfun shadow
(pass 3's measured seam) is generalized from "wrap the first eligible factor" to
"wrap the k-th eligible factor" via a new `*mr-implicit1-which*` index. The wrapped
object is created and consumed entirely inside the matcher (findfun's return value
feeds `compileeach` directly) — it never exists as a product member and never
round-trips, so §2.4's constraint holds strictly (no hand-built product object is
ever constructed). Consequences, measured-derivation in Task 1's calibration:

- For all-bare products (k bare factors, no explicit power) the shadow-index scan
  is binding-equivalent to materialization for the first power slot, and strictly
  MORE powerful for multi-slot rules: the index is re-evaluated against the
  REMAINING factor list at each findfun call, so a second slot can bind a bare
  leftover factor that a one-shot materialization could not offer (its wrapped
  candidate was consumed by the first slot; the leftover is then a single bare
  factor in a `c='times` context, where the e-itself branch does not wrap).
- The e-itself branch (leftover single factor) stays index-blind: it wraps only for
  `which = nil` (pass-3 behavior preserved bit-for-bit when the index is unset).
- A product that CONTAINS an explicit power factor (the f1 shape) is outside the
  shadow's activation (the original findfun returns the explicit factor before the
  shadow runs — measured, that is exactly why f1 0-fires pass 3). The sweep skips
  those entries (zero wasted scans) and emits the **diagnostic** instead: which
  explicit factor the original findfun picks, in both directions. The binding
  question for those entries ("does a ported rule exist that WOULD fire given the
  right candidate?") is answered by the **drill** (pattern + cond evaluation of all
  333 class-3 rules), not by a second wrap mechanism. An entry with an explicit
  power, a drill rule whose pattern fires and whose cond is TRUE, and no sweep fire
  is the documented mechanism strictness (explicit-power candidate shadowing) —
  the general-backtracking research of ticket 04, out of this campaign's fix scope,
  recorded as such with the binding evidence.

Phase-2 production pass 4 (Task 4A) is exactly the sweep: after passes 1-3
0-fire, for each bare factor, a full table scan with the shadow offering that
factor, in both scan directions — top-level, `fb=false` only, so nothing currently
passing can change (a passing entry fired in passes 1-3 and never reaches the
sweep; only currently-failing 0-firings can newly fire). The prototype (probe) and
production share one implementation: the probe's `.mac` loop calls the same
`%mr_p4_once` / `%mr_pass4_scan` primitives the production `mr_top` wiring calls
(spec §5.2).

---

### Task 1: Pass-4 mechanism (Lisp + shared Maxima driver) and the calibration gate

**Files:**
- Modify: `maxima_rubi_implicit1.lisp` (shadow index; `*mr-implicit1-which*`)
- Create: `maxima_rubi_pass4.lisp`
- Modify: `maxima_rubi.mac:90` (load + witness, after the implicit-1 load)
- Modify: `maxima_rubi_utils.mac` (three new `:=` functions, appended after `%mr_dispatch_i1`'s callers — place them directly before `mr_top` at line 252, with the comment block)
- Modify: `test/build_rules_core.sh:36-39` (FP list)
- Modify: `test/corpus_driver.py:161-169` (`_core_fingerprint` rels)
- Create: calibration driver `probes/corpus/06-calibration.pass4.mac` (the 16-entry calibration batch; generated by hand, NOT by the probe — it pins the mechanism before the probe exists)
- Commit outputs: `probes/corpus/06-class3-deferred-mechanisms.calibrate.out`

**Interfaces:**
- Consumes: `%mr_dispatch(f, x, rl, depth)` (utils:140), `%mr_dispatch_i1` (implicit1.lisp:99), `matchreverse` (dispatch.lisp:111), `mr-implicit1-w` (implicit1.lisp:67), `mr_rule_table` (the loaded 3,513-rule table).
- Produces (exact names, later tasks rely on them):
  - Lisp global `maxima::*mr-implicit1-which*` (nil = pass-3 behavior; positive integer = the 1-based index of the eligible factor the shadow offers, evaluated per findfun call against the current factor list).
  - `maxima_rubi_pass4.lisp`: defmfuns `|$%MR_P4_SETREV|`, `|$%MR_P4_SETWHICH|`, `|$%MR_DISPATCH_P4|`, `|$%MR_P4_DIAG|` — all `(&rest args)`, callable from Maxima as `%mr_p4_setrev(0|1)`, `%mr_p4_setwhich(<int>|false)`, `%mr_dispatch_p4(f, x, rl, depth)`, `%mr_p4_diag(f)` (returns a Maxima list of diagnostic strings).
  - `maxima_rubi_utils.mac`: `%mr_barefactors(f)` → Maxima list `[k, hp]` (k = bare top-level factor count, hp = boolean true iff an explicit-power top-level factor exists; non-product tops → `[0, false]`); `%mr_p4_once(f, x, rl, depth, d, i)` → answer-or-false (one gated scan, direction d ∈ {0,1}, index i); `%mr_pass4_scan(f, x, rl, depth)` → answer-or-false (the full sweep: skip when hp or k<2, else d∈{0,1} × i∈1..k, first fire wins).
  - Calibration labels (the probe reuses the vocabulary): `FIRE4`, `0FIRE-EXPL`, `0FIRE-POOL`, `D-NEST`, `PROD-OK`.

- [ ] **Step 1: Cut the campaign branch**

```bash
git -C /home/serge/src/maxima-rubi checkout master
git -C /home/serge/src/maxima-rubi checkout -b class3-deferred
git -C /home/serge/src/maxima-rubi log --oneline -1   # expect cd6cc57
```

- [ ] **Step 2: The shadow index in `maxima_rubi_implicit1.lisp`**

Append to the header comment block (after the existing "No backtracking is added
or removed" paragraph) the measured-design note:

```lisp
;; Pass-4 candidate index (2026-08-30, class-3 deferred campaign,
;; docs/superpowers/specs/2026-08-30-class3-deferred-campaign-design.md,
;; plan docs/superpowers/plans/2026-08-30-class3-deferred-campaign.md):
;; pass 3 offers exactly ONE wrapped candidate (the first eligible
;; non-mexpt factor in scan order); a multi-bare-factor integrand
;; 0-fires whenever that one candidate is the wrong slot (measured
;; f1/f2/f5, spec section 2.2). *mr-implicit1-which* (nil = pass-3
;; behavior, byte-identical; positive integer = 1-based index) makes
;; the shadow offer the k-th eligible factor INSTEAD. The index is
;; evaluated against the factor list CURRENT at each findfun call, so
;; a multi-slot rule's later slots see the remaining factors
;; re-indexed (a slot can bind a bare leftover factor that a one-shot
;; raw-(mexpt f 1) product materialization could not offer — strictly
;; more binding power, same single-candidate-per-slot semantics, no
;; backtracking added or removed). The e-itself branch (leftover
;; single factor) stays index-blind: it wraps only for which = nil,
;; preserving pass 3 bit-for-bit when the index is unset. A product
;; containing an explicit mexpt factor is outside the shadow's
;; activation entirely (the original findfun returns the explicit
;; factor before the shadow runs — why f1 0-fires pass 3); the
;; pass-4 sweep skips those (the %mr_barefactors census) and the
;; %mr_p4_diag diagnostic reports the original pick instead.
```

Add after `(defvar *mr-implicit1-active* nil)`:

```lisp
(defvar *mr-implicit1-which* nil)
```

Replace `mr-implicit1-findfun` (lines 70-82) with the index-aware version —
the `which = nil` arms are the old code verbatim:

```lisp
(defun mr-implicit1-findfun (e p c)
  (cond ((not (eq p 'mexpt)) nil)
	((or (atom e) (not (eq (caar e) c)))
	 ;; e itself is the leftover single factor (or an atom) —
	 ;; index-blind (pass-3 arm only), see the header note
	 (cond ((and (null *mr-implicit1-which*)
		     (or (eq c 'mtimes) (eq c 'mplus)))
	       (mr-implicit1-w e))
	       (t nil)))
	(t (let ((factors (if (null matchreverse)
			      (reverse (cdr e))
			      (cdr e))))
	     (if (null *mr-implicit1-which*)
		 (dolist (f factors)
		   (unless (and (consp f) (eq (caar f) 'mexpt))
		     (return-from mr-implicit1-findfun (mr-implicit1-w f))))
		 (let ((eligible (remove-if
				  #'(lambda (g) (and (consp g)
						     (eq (caar g) 'mexpt)))
				  factors)))
		   (let ((k (1- *mr-implicit1-which*)))
		     (if (and (integerp k) (>= k 0)
			      (< k (length eligible)))
			 (mr-implicit1-w (nth k eligible))
			 nil)))))))
```

- [ ] **Step 3: `maxima_rubi_pass4.lisp` (new file, complete content)**

```lisp
;; maxima_rubi_pass4.lisp — pass-4 per-candidate implicit-1 scans
;; (class-3 deferred campaign: the prototype + production pass 4 share
;; this seam — spec section 5.2).
;;
;; The pass-4 sweep (the Maxima-level driver %mr_pass4_scan,
;; maxima_rubi_utils.mac) runs, for each bare top-level factor f_i of a
;; 0-fired integrand, a full table scan with *mr-implicit1-which* = i
;; (the findfun shadow, maxima_rubi_implicit1.lisp, then offers f_i as
;; the wrapped candidate — the index is re-evaluated against the
;; remaining factor list at each findfun call, so multi-slot rules get
;; their later slots a fresh candidate; see that file's header). The
;; wrapped object is created and consumed inside the matcher (findfun's
;; return feeds compileeach directly) and never round-trips to the
;; Maxima level — the measured round-trip constraint
;; (maxima_rubi_implicit1.lisp header, 2026-08-27) holds strictly.
;;
;; Gating: the sweep is wired into mr_top AFTER passes 1-3 0-fire,
;; top-level, fb=false ONLY (the Task-4 wiring). Nothing currently
;; passing can change: a passing entry fired in passes 1-3 and never
;; reaches the sweep.
;;
;; Symbol naming: ALL-UPPERCASE typed defmfun names (the lowercase-name
;; uppercasing quirk, maxima_rubi_dispatch.lisp note); (&rest args)
;; dispatch (a fixed-parameter defmfun is not callable in this build).
;; matchreverse: the dispatch.lisp lisp global (the Maxima-level value
;; does not reach it, measured there); %mr_p4_setrev is the setter.
;; *mr-implicit1-which* lives in the implicit-1 file (it loads first);
;; this file consumes it.

(defmfun |$%MR_P4_SETREV| (&rest args)
  (unless (= (length args) 1)
    (merror (intl:gettext "%mr_p4_setrev: expected 1 arg, found ~A")
            (length args)))
  (setf matchreverse (if (first args) t nil))
  nil)

(defmfun |$%MR_P4_SETWHICH| (&rest args)
  (unless (= (length args) 1)
    (merror (intl:gettext "%mr_p4_setwhich: expected 1 arg, found ~A")
            (length args)))
  (setf *mr-implicit1-which* (first args))
  nil)

;; One gated pass-4 scan: shadow active (with the current
;; *mr-implicit1-which*), one full table scan, gate off + index reset
;; in unwind-protect. Call with (f, x, table, depth) exactly as
;; %mr_dispatch.
(defmfun |$%MR_DISPATCH_P4| (&rest args)
  (unless (= (length args) 4)
    (merror (intl:gettext "%mr_dispatch_p4: expected 4 args, found ~A")
            (length args)))
  (unwind-protect
      (progn
        (setf *mr-implicit1-active* t)
        (mlambda (mget '|$%MR_DISPATCH| 'mexpr)
                args
                '|$%MR_DISPATCH| t nil))
    (setf *mr-implicit1-active* nil)
    (setf *mr-implicit1-which* nil)))

;; Diagnostic for products that contain an explicit power factor (the
;; shadow-dead case, f1): what the ORIGINAL findfun returns for a
;; non-atomic-base power slot, in both scan directions — the explicit
;; factor that shadows every bare candidate. Returns a Maxima list of
;; strings: ("pick-fwd=<string|none>" "pick-rev=<string|none>"
;;  "nfactors=<n>" "nbare=<b>" "npow=<p>").
(defun |$mr-p4-pick| (e revp)
  (let ((f (mr-orig-findfun-v e 'mexpt 'mtimes)))
    (if f (princ-to-string f) "none")))

(defmfun |$%MR_P4_DIAG| (&rest args)
  (unless (= (length args) 1)
    (merror (intl:gettext "%mr_p4_diag: expected 1 arg, found ~A")
            (length args)))
  (let ((f (first args))
        (nf 0) (nb 0) (np 0))
    (when (and (consp f) (eq (caar f) 'mtimes))
      (dolist (g (cdr f))
        (incf nf)
        (if (and (consp g) (eq (caar g) 'mexpt)) (incf np) (incf nb))))
    (let ((fwd (|$mr-p4-pick| f nil))
          (rev (progn
                 (setf matchreverse t)
                 (let ((r (|$mr-p4-pick| f t)))
                   (setf matchreverse nil)
                   r))))
      (list (format nil "pick-fwd=~A" fwd)
            (format nil "pick-rev=~A" rev)
            (format nil "nfactors=~A" nf)
            (format nil "nbare=~A" nb)
            (format nil "npow=~A" np)))))
```

- [ ] **Step 4: Loader wiring in `maxima_rubi.mac`**

After line 90 (`%mr_load_sibling("maxima_rubi_implicit1.lisp", 'mr_witness_implicit1)$`)
insert:

```maxima
/* The pass-4 per-candidate implicit-1 seam (maxima_rubi_pass4.lisp):
 * %mr_p4_setrev / %mr_p4_setwhich / %mr_dispatch_p4 / %mr_p4_diag for
 * the class-3 deferred campaign (plan
 * docs/superpowers/plans/2026-08-30-class3-deferred-campaign.md).
 * Loads after the implicit-1 file (it consumes *mr-implicit1-which*). */
mr_witness_pass4() := block([r],
  /* %mr_dispatch_p4 on an EMPTY table 0-fires: a missed load leaves it
   * a noun and this fails loudly. The setter round-trip catches a
   * noun setter (string of a noun call would throw in is()). */
  r : %mr_dispatch_p4(1, x, [], 1),
  %mr_p4_setwhich(1),
  %mr_p4_setwhich(false),
  %mr_p4_setrev(1),
  %mr_p4_setrev(0),
  is(r = false))$

%mr_load_sibling("maxima_rubi_pass4.lisp", 'mr_witness_pass4)$
```

- [ ] **Step 5: The shared Maxima driver in `maxima_rubi_utils.mac`**

Insert directly before `mr_top` (line 252):

```maxima
/* Pass-4 top-level factor census (class-3 deferred campaign, Task 1).
   f is a SIMPLIFIED integrand (a real Maxima expression). A factor is
   bare (implicit-1-eligible) iff it is not an explicit power. A mquot
   top (A/x storage — all negative powers are stored as / nodes in this
   build) has no mtimes factor list at the top level: the census reports
   [0, false] and the sweep is a no-op on it (the shadow never
   activates on a mquot top: findfun is called with c = 'mquot, outside
   the {mtimes, mplus} wrap condition — measured consequence: f5
   0-fires pass 3, spec section 2.2). */
%mr_barefactors(f) := block([n, i, bare, haspow],
  if is(op(f) = "*") then (
    n : length(f), bare : 0, haspow : false,
    for i : 1 thru n do (
      if is(op(part(f, i)) = "^") then haspow : true
      else bare : bare + 1
    ),
    [bare, haspow]
  ) else [0, false])$

/* One pass-4 scan (the probe's P4SCAN unit AND the production sweep's
   unit — the shared primitive, spec section 5.2). d in {0,1} selects
   the scan direction; i is the 1-based bare-factor index the shadow
   offers. Resets BOTH matcher-state globals after the scan, so a call
   is side-effect-free wrt pass 1/2/3 semantics. */
%mr_p4_once(f, x, rl, depth, d, i) := block([ans],
  %mr_p4_setrev(d),
  %mr_p4_setwhich(i),
  ans : %mr_dispatch_p4(f, x, rl, depth),
  %mr_p4_setrev(0),
  %mr_p4_setwhich(false),
  ans)$

/* The pass-4 sweep. Skips (returns false, zero scans) when the
   integrand has an explicit-power top-level factor (the shadow-dead
   case — the caller runs %mr_p4_diag instead) or fewer than 2 bare
   factors (nothing to re-order). return() inside a for is loop-level
   in this build (the %mr_dispatch note above): the ans/bare-return
   idiom, checked at BOTH loop levels. */
%mr_pass4_scan(f, x, rl, depth) := block([census, k, hp, d, i, ans],
  census : %mr_barefactors(f),
  k : part(census, 1),
  hp : part(census, 2),
  if hp then return(false),
  if is(k < 2) then return(false),
  ans : false,
  for d : 0 thru 1 do (
    for i : 1 thru k do (
      if is(ans = false) then (
        ans : %mr_p4_once(f, x, rl, depth, d, i),
        if is(ans # false) then return()
      )
    ),
    if is(ans # false) then return()
  ),
  ans)$
```

- [ ] **Step 6: Core-bake file list (both sites, in sync)**

`test/build_rules_core.sh` lines 36-39 — add the pass-4 lisp to the FP list:

```sh
FP=$( { printf '%s\n' maxima_rubi.mac maxima_rubi_utils.mac maxima_rubi_dispatch.lisp \
        maxima_rubi_implicit1.lisp maxima_rubi_pass4.lisp
        ls rules/class1/*.mac rules/class2/*.mac rules/class3/*.mac
      } | LC_ALL=C sort | xargs -d '\n' cat | md5sum | cut -d' ' -f1 )
```

`test/corpus_driver.py` `_core_fingerprint()` lines 161-169 — same file added
(sorted order is computed, so list position is irrelevant; keep it grouped):

```python
    rels = sorted(["maxima_rubi.mac", "maxima_rubi_utils.mac",
                   "maxima_rubi_dispatch.lisp",
                   "maxima_rubi_implicit1.lisp",
                   "maxima_rubi_pass4.lisp"] +
```

Also update the two doc comments that name the file list (build_rules_core.sh
lines 13-15, 30-35; corpus_driver.py line 153-155) to include "pass-4 lisp".

- [ ] **Step 7: Rebuild the core, verify the fingerprint chain**

```bash
cd /home/serge/src/maxima-rubi
sh test/build_rules_core.sh
# expect: "built test/mr_rules.core (...) rules=3513 fingerprint=<new-fp>"
git status --porcelain rules/    # expect EMPTY (no rule changed)
maxima --very-quiet -b test_maxima_rubi.mac | tail -1
# expect: Results: 743 passed, 0 failed   (the shadow edit is behavior-neutral)
```

- [ ] **Step 8: The calibration batch `probes/corpus/06-calibration.pass4.mac`**

Complete content (run under the core image; the 12 F_-domain integrands are the
corpus texts of 3.1.5 e186-e197 verbatim — copy them from
`reference/maxima-syntax-test-suite/3 Logarithms/3.1.5 u (a+b log(c x^n))^p.mac`
lines 229-240; the f1/f2/f5 forms are the spec's generic-parameter shapes):

```maxima
/* Pass-4 mechanism calibration (class-3 deferred campaign, Task 1).
   16 entries: f1, f2, f5 + 3.1.5 e186-e197. Per entry: production
   trace (rubi_verbose), top-level op, factor census, the sweep with
   P4SCAN markers (the "rubi: rule ... fired on" line following a
   P4SCAN marker is that scan's top-level fire — the first such line
   after the marker; nested fires come later, during the repl), the
   diagnostic on products, and the verdict label per the plan's
   label set. Commit the output as
   probes/corpus/06-class3-deferred-mechanisms.calibrate.out. */
cali_entry(name, f, x) := block([ans, census, k, hp, d, i, ans4],
  print("CALI " + name),
  rubi_verbose : true,
  ans : rubi(f, x),
  print("PROD " + (if atom(ans) then "atom" else string(op(ans)))),
  rubi_verbose : false,
  census : %mr_barefactors(f),
  k : part(census, 1),
  hp : part(census, 2),
  print("P4CENSUS " + string(k) + " " + string(hp)),
  if is(op(f) = "*") then
    print("P4DIAG " + sapply(lambda[[s], s], %mr_p4_diag(f))),
  if is(hp = false) and is(k >= 2) then (
    for d : 0 thru 1 do
      for i : 1 thru k do (
        print("P4SCAN " + string(d) + " " + string(i)),
        ans4 : %mr_p4_once(f, x, mr_rule_table, 1, d, i),
        if is(ans4 # false) then
          print("P4FIRE " + string(d) + " " + string(i) + " "
                + (if atom(ans4) then "atom" else string(op(ans4))))
      )
  ) else print("P4SKIP"),
  print("CALIEND " + name))$

/* f2 — production pass 3 fires a 3_1_5 rule and answers (spec 2.2). */
cali_entry("f2", (d+e*x)*(a+b*log(c*x^n)), x)$
/* f1 — 0-fires all three passes; explicit x^3 shadows the sweep. */
cali_entry("f1", x^3*(d+e*x)*(a+b*log(c*x^n)), x)$
/* f5 — mquot top, 0-fires. */
cali_entry("f5", (d+e*x)*(a+b*log(c*x^n))/x, x)$
/* 3.1.5 e186: (d+e*x^2)*asin(a*x)*log(c*x^n)  ... e197:
   (d+e*x^2)*acosh(a*x)^2*log(c*x^n) — the twelve corpus texts,
   verbatim, one cali_entry each, names "e186".."e197". */
print("CALIDONE")$
```

(Expand the ellipsis: the twelve `cali_entry("eNNN", <verbatim corpus text>, x)$`
calls — e186 asin, e187 acos, e188 atan, e189 acot, e190 asinh, e191 acosh,
e192 atanh, e193 acoth (all m=1), e194 asin^2, e195 acos^2, e196 asinh^2,
e197 acosh^2 (m=2).)

- [ ] **Step 9: Run the calibration, assert the expected table**

```bash
cd /home/serge/src/maxima-rubi
maxima --very-quiet --tls-limit 100000 -b probes/corpus/06-calibration.pass4.mac \
  > probes/corpus/06-class3-deferred-mechanisms.calibrate.out 2>&1
```

Expected values (a MISSING assertion is a calibration failure — stop,
investigate, do not ship the mechanism):

| entry | PROD | census (k, hp) | expected |
|---|---|---|---|
| f2 | non-noun | 2, false | sweep: ≥1 `P4FIRE`, first fire's rule in the **3_1_5** family; production trace's first "fired" rule in the 3_1_5 family (r27 per the milestone-3 record) |
| f1 | noun (`unintegrable`) | 2, true | `P4SKIP`; `P4DIAG` pick-fwd = pick-rev = `x^3` |
| f5 | noun | 0, false (mquot top) | `P4SKIP`; no `P4DIAG` (not a `*` top) |
| e186-e193 (m=1) | non-noun | 3, false | sweep: ≥1 `P4FIRE` (the pass-3 candidate is in the sweep's candidate set, so the sweep must fire at least what production fired); production trace's first "fired" rule in the **3_5** family (r43 per the close-out record) |
| e194-e197 (m=2) | noun | 2, true | `P4SKIP`; `P4DIAG` pick-fwd = pick-rev = the `F(a*x)^2` factor |

Check each row against the `.out`; record the exact firing (dir, i, rule name)
per FIRE4 entry in the `.out` header comment (the Task-4 Layer-A test picks its
targets from this table). Also assert, in the `.out` review, that the
`%mr_dispatch_i1` behavior is unchanged: the f2 row's production fire family is
3_1_5 as before the edit (the shadow's nil arm is verbatim — the 743/0 Layer A
run in Step 7 is the global check).

- [ ] **Step 10: Commit**

```bash
git add maxima_rubi_implicit1.lisp maxima_rubi_pass4.lisp maxima_rubi.mac \
        maxima_rubi_utils.mac test/build_rules_core.sh test/corpus_driver.py \
        test/mr_rules.core test/mr_rules.core.stamp \
        probes/corpus/06-calibration.pass4.mac \
        probes/corpus/06-class3-deferred-mechanisms.calibrate.out
git commit -m "pass 4: per-candidate implicit-1 sweep (shadow index) + calibration"
```

---

### Task 2: The triage probe `probes/corpus/06-class3-deferred-mechanisms`

**Files:**
- Create: `probes/corpus/06-class3-deferred-mechanisms.py`
- Create: `probes/corpus/06-class3-deferred-mechanisms.run`

**Interfaces:**
- Consumes: `test/corpus_class3.out` + `test/corpus_class3.baseline.out` (entry lines `<class:14s> t=<dt>s <rel> e<n> L<lineno>`); the suite files under `reference/maxima-syntax-test-suite/3 Logarithms/*.mac` (integrand text, the probe-05 `extract_entries`/`split_elements` mirror); the core (`test/mr_rules.core`, launched like `corpus_driver.maxima_run`'s core path — `SBCL = os.environ.get("MR_SBCL") or <resolved maxima binary>`, `--tls-limit 100000 --core ... --noinform --very-quiet -b fpath`); Task 1's primitives (`%mr_barefactors`, `%mr_p4_once`, `%mr_p4_diag`, `%mr_pass4_scan` — the latter is NOT called by the probe: the probe runs the loop itself so it can emit the P4SCAN markers; it calls the SAME `%mr_p4_once` unit production uses).
- Produces: the per-entry mechanism line (one per entry, in the merged `.out`):
  `MECH <label:14s> t=<dt:6.1f>s <rel> e<n> L<lineno> npat=<j> [fire=<d>,<i>,<rule>] [drill=<facts>]`
  with label ∈ {`FIRE4`, `D-NEST`, `0FIRE-EXPL`, `0FIRE-POOL`}; plus the distribution section (label × file × target-flag 788/329 cross-tab; the measured per-entry sweep cost: mean/p50/p95/max of dt_total − the record's t= for swept entries) — **the Phase-2 design input**.
- CLI: `--gen` (parse records + suite files, assert 1,033 deferred and 788 target-flagged, emit the per-entry `.mac` files + the shard plan to `<workdir>`), `--shard K` (run shard K sequentially), `--launch` (Popen 24 shards, write the pid file `<workdir>/shard-pids`), `--merge <workdir>` (merge shard `.out`s → the committed `.out`, assert completeness 1,033/1,033 no dupes), `--calibrate` (run the Task-1 calibration set through the PROBE's own per-entry measurement and assert the Task-1 table — the "a harness that misclassifies a calibration case does not ship" gate).

- [ ] **Step 1: The deferred-set extraction (the record join)**

Parse both records' entry lines (regex
`^(?P<cls>\S+)\s+t=(?P<t>\d+\.\d)s\s+(?P<rel>\S.*?) e(?P<n>\d+) L(?P<ln>\d+)\s*$`);
deferred keys = `cls == "deferred"` in `corpus_class3.out` (assert count 1,033);
target flag = the baseline record's class for the same (rel, n) ∈
{verified, expected, unverified} (assert flagged count 788, with the 329/459
split). Join on (rel, n) — the (file, entry) key both records share.

- [ ] **Step 2: Per-entry `.mac` generation**

For each deferred entry (integrand `f_text` from the suite file via the
probe-05-style `extract_entries`/`split_elements`; variable `var_text`), emit:

```maxima
f := <f_text>;
x := <var_text>;
rubi_verbose : true;
ans : rubi(f, x);
disp("PROD " + (if atom(ans) then "atom" else string(op(ans))));
rubi_verbose : false;
census : %mr_barefactors(f);
disp("P4CENSUS " + string(part(census, 1)) + " " + string(part(census, 2)));
if is(op(f) = "*") then disp("P4DIAG " + sapply(lambda[[s], s], %mr_p4_diag(f)));
swept : 0,
if is(part(census, 2) = false) and is(part(census, 1) >= 2) then (
  for d : 0 thru 1 do
    for i : 1 thru part(census, 1) do (
      disp("P4SCAN " + string(d) + " " + string(i)),
      ans4 : %mr_p4_once(f, x, mr_rule_table, 1, d, i),
      if is(ans4 # false) then (
        disp("P4FIRE " + string(d) + " " + string(i) + " "
             + (if atom(ans4) then "atom" else string(op(ans4)))),
        swept : 1
      )
    )
) else disp("P4SKIP"),
if swept = 0 then (
  <the 333-rule drill block, Step 3>
),
disp("DONE")$
```

Notes: `swept` is 0-initialized on the SAME line as the `if` (Maxima comma
sequence); the drill runs exactly on 0-firing entries (FIRE4 entries skip it —
the mechanism is already determined); `rubi_verbose` is on around `rubi` only
(the P4SCAN fires are attributed by marker order, not by verbose noise).

- [ ] **Step 3: The drill block (generated from `rules/class3/*.mac` source)**

At generation time, parse each of the 11 `rules/class3/*.mac` files: per rule,
the `defmatch(_mr_pat_<file>_rN, ...)` line (the pattern name) and the
`_mr_cond_<file>_rN(mm, x) := block([...],` body — the block's variable list
(the slots), the assignment lines (`slot : geteqR(mm, 'sym),`), and the FINAL
expression line ending `)$` — the top-level ` and `-chain, split depth-aware at
parens level 0 (the clauses). Emit, per rule, a probe-local function:

```maxima
_drill_<file>_rN(mm, x) := block([<slots>..., c1, ..., cN],
  <verbatim assignment lines>,
  c1 : is(<clause 1>), c2 : is(<clause 2>), ..., cN : is(<clause N>),
  [c1, ..., cN])$
```

and, in the per-entry drill block, per rule:

```maxima
mm : errcatch(_mr_pat_<file>_rN(f, x)),
if mm = [] then disp("DR <file>_rN CRASH")
else if mm # false then (
  if %mr_containsBoolean(mm) then disp("DR <file>_rN BOOL")
  else disp("DR <file>_rN " + string(_drill_<file>_rN(mm, x)))
)
```

(the comma-sequenced statements inside the `if swept = 0 then ( ... )` block;
`errcatch` returns `[value]`/`[]` in this build — the codebase idiom;
`CRASH` = the pattern function errored on this integrand, `BOOL` = a
degenerate boolean binding — both are facts the adjudication reads).
`npat` = the count of `DR` lines that are neither CRASH nor BOOL. The drill
block is IDENTICAL for every entry (generate once, splice into each `.mac`) —
~11×(avg 30 rules) functions ≈ 3,000 lines per entry file; generation is a
string splice, cost negligible.

- [ ] **Step 4: The sharding (24 processes, one fresh core subprocess per entry)**

`--launch`: LPT-pack the 1,033 entries into 24 shards using each entry's
recorded package time `t=` (cost-aware, the `launch_class_shards.py` idea,
self-contained ~40 lines: sort desc, assign each to the currently-lightest
shard; no file-splitting needed — per-entry granularity is the unit). Each
shard = one `--shard K` process; each entry = one fresh subprocess
(core path, 60 s safety cap; a cap-exceeded entry is recorded `t=60.0s` with
label `0FIRE-POOL` + detail `cap` and flagged in the `.out` for manual
follow-up — none are expected: deferred package times are 1-12 s and the
sweep adds ≤ 2k scans ≈ a few seconds). Stdout is captured per entry; the
shard appends the parsed `MECH` line to its shard `.out`.

- [ ] **Step 5: The label logic (deterministic, in the merge)**

Per entry, from its captured lines:
1. `PROD` must be a noun op (`integrate`/`unintegrable`) — otherwise the entry
   was not actually deferred: flag `RECORD-MISMATCH` and count it (assert 0).
2. first production "rubi: rule R fired on" line → `prod_fire = R` (else none).
3. any `P4FIRE` → label `FIRE4`, detail `fire=<d>,<i>,<rule>` (the rule from
   the first "fired on" line following that P4SCAN marker).
4. else `prod_fire` present → label `D-NEST` (a rule fired and the answer is a
   top-level noun — the nested sub-integral 0-fired; out of pass-4 scope, the
   adjudication documents it), detail `rule=<R>`.
5. else census hp=true → `0FIRE-EXPL`, detail = the P4DIAG strings.
6. else → `0FIRE-POOL`, detail = `npat=<j>` + the DR facts (rule:clause-vector
   list, CRASH/BOOL counts) + `nonproduct` when the census was [0,·].

- [ ] **Step 6: The distribution (the merge output)**

`--merge` asserts completeness (1,033/1,033, no dupes/missing/extra), writes
the per-entry MECH lines, then the distribution: label × per-file ×
target-flag (788-flagged vs 150-no-answer vs 76-timeout vs 19-error
baseline classes) cross-tab; per label the per-file counts; the sweep cost
stats (swept entries only: dt_total − record t=: mean/p50/p95/max); the
calibration re-run section (`--calibrate` output embedded — the probe's own
measurement of the 16 calibration entries must reproduce the Task-1 labels:
f2 FIRE4 / f1 0FIRE-EXPL(pick x^3) / f5 0FIRE-POOL(nonproduct) / e186-e193
FIRE4(prod 3_5) / e194-e197 0FIRE-EXPL(pick F^2) — a mismatch FAILS the merge
with the diff printed). Header: date + build_info stamp (one maxima call for
`build_info()`). Commit the merged file as
`probes/corpus/06-class3-deferred-mechanisms.out`.

- [ ] **Step 7: The `.run` entry + a dry validation**

`probes/corpus/06-class3-deferred-mechanisms.run`:

```sh
#!/bin/sh
cd "$(dirname "$0")/../.." || exit 1
python3 probes/corpus/06-class3-deferred-mechanisms.py --calibrate \
  || exit 1
python3 probes/corpus/06-class3-deferred-mechanisms.py --gen
python3 probes/corpus/06-class3-deferred-mechanisms.py --launch
echo "shards launched; merge when the pid file is clean:"
echo "  python3 probes/corpus/06-class3-deferred-mechanisms.py --merge <workdir>"
```

Validate WITHOUT the full run: `--gen` (asserts the 1,033/788 counts, prints
the shard plan), `--calibrate` (16 entries ≈ 2-4 min wall on 24 shards — run
it serially in-process for the dry validation: a `--calibrate-serial` flag is
NOT needed — the calibration is 16 fresh subprocesses run sequentially by the
`--calibrate` path; ~2-4 min is fine), and a 10-entry smoke: `--gen --smoke
10` (a hidden flag: run 10 entries serially, print the MECH lines) — the
smoke's 10 are the calibration's non-calibration neighbors (deterministic
pick: the first 10 deferred keys in record order).

- [ ] **Step 8: Commit**

```bash
git add probes/corpus/06-class3-deferred-mechanisms.py \
        probes/corpus/06-class3-deferred-mechanisms.run
git commit -m "probe: class-3 deferred-mechanisms triage (sweep + drill + distribution)"
```

(The `.out` is committed in Task 3, after the full run.)

---

### Task 3: Run the triage; adjudicate; write the Phase-2 decision record

**Files:**
- Commit: `probes/corpus/06-class3-deferred-mechanisms.out`
- Create: `docs/corpus-class3-deferred-uplift.md` (skeleton + decision record)

**Interfaces:**
- Consumes: Task 2's probe; the pinned `.m` files (the 11 under
  `reference/rubi/Rubi/IntegrationRules/3 Logarithms/*.m`); the spec's
  taxonomy (A / B-port / B-faithful / C-in-Rubi / C-absent / D).
- Produces: the **Phase-2 decision record** (the section of the campaign
  record) — the exact, data-bound list of: (i) the A-mass verdict
  (pass-4 production go/no-go + cost disposition per the rule below), (ii)
  the B list (rule, file, clause, the `.m` clause it should be, the
  generator location), (iii) the C-in-Rubi list (`.m` file, `.m` rule
  number/text, the ported-file gap), (iv) the C-absent list (shape, the
  `.m` section searched), (v) the D documentation set (0FIRE-EXPL
  entries with the binding evidence — the explicit-power shadowing
  clusters — the D-NEST nested-gap clusters, the catch-all/mechanism
  strictness notes). Task 4 executes exactly this list.

- [ ] **Step 1: The full run**

```bash
cd /home/serge/src/maxima-rubi
sh probes/corpus/06-class3-deferred-mechanisms.run    # calibrate + gen + launch
# watch the pid file (the shard-pids under the workdir) until all 24 exit;
# wall estimate 10-30 min (per-entry 3-20 s / 24 procs)
python3 probes/corpus/06-class3-deferred-mechanisms.py --merge <workdir>
# expect: completeness 1033/1033, calibration section green, the distribution
git add probes/corpus/06-class3-deferred-mechanisms.out
git commit -m "probe: class-3 deferred-mechanisms distribution (1033 entries, measured)"
```

- [ ] **Step 2: The adjudication (subagent, general; the controller reviews)**

The brief hands the subagent: the `.out` (the per-entry MECH lines + the
distribution), the spec's taxonomy, the 11 `.m` files, the ported rules
directory, and the pinned mechanism facts. Its work, per cluster (cluster =
per (label, family-file, shape-fingerprint) — shape fingerprint = the
factor-type sequence of the integrand, e.g. `binomial-linear, log, invfunc^2`):

- `FIRE4` clusters → class A. Record the (dir, i, rule) witnesses.
- `0FIRE-EXPL` clusters → read the P4DIAG pick + the drill facts: a drill
  rule with a TRUE clause-vector is the binding evidence (class D,
  mechanism strictness: explicit-power candidate shadowing — the ticket-04
  general-backtracking case, documented with the evidence; NOT fixable by
  pass 4 as designed). No drill fire → the pool: the `.m` search decides
  B-faithful / C-in-Rubi / C-absent / D.
- `0FIRE-POOL` clusters → the drill facts decide: drill rule fire +
  clause-vector all-true-except-one → the candidate B-port (verify: the
  failing clause vs the `.m` rule's condition, line-cited — a port that
  DROPPED a clause or mistranslated one = B-port; a faithful clause that is
  legitimately false on this data = B-faithful → D). No drill fire → the
  `.m` shape search: a `.m` rule covering the shape exists in the pinned
  commit but is not ported (or ported under a different family file that
  still cannot reach the shape) = C-in-Rubi; no `.m` rule = C-absent
  (upstream gap, recorded).
- `D-NEST` clusters → documented (the nested sub-integral 0-fire; the fired
  rule cited; out of pass-4 scope by the fb-gate design).
- Every verdict line: the entry list (or the count + the fingerprint), the
  class, the `.m` citation (file + rule number or "searched, absent"), the
  evidence (drill clause-vectors / diag pick / fire witness).

The controller verifies the decision record against the taxonomy and the
`.out` counts (the class totals must sum to 1,033; the 788/329 split
recomputed per class) before accepting it.

- [ ] **Step 3: The Phase-2 decisions (the controller, from the data)**

- **A verdict:** pass-4 production ships IFF the FIRE4 mass covers ≥ 1
  target-mass (788-flagged) entry AND the measured sweep cost clears:
  p95 added cost ≤ 3 s AND mean added ≤ 1 s (the class-3 wall stays
  ~≤1.5×). Otherwise the cost fallbacks, in order: (a) bound the sweep at
  k = 3 factors (the first 3 in stored order, both directions); (b)
  forward-only (d = 0) + k = 3. The record states which rule fired on the
  numbers. (FIRE4 mass = 0: pass 4 is not wired; the A-class entries — if
  any — are documented as prototype-only. This is a data outcome, not a
  plan gap.)
- **B verdict:** each B-port item becomes a Task-4 sub-brief (rule, file,
  clause, the `.m` citation, the generator location —
  `generator/generate_rules.py` / `generator/translation_table.py`).
- **C verdict:** each C-in-Rubi item becomes a Task-4 sub-brief (`.m`
  rule, target ported file, the translation-table row). C-absent items go
  to the record only.
- **D verdict:** the documentation set (no code).

- [ ] **Step 4: The record skeleton + decision record commit**

`docs/corpus-class3-deferred-uplift.md` — section 1: the distribution
(table, citing the probe `.out`); section 2: the per-cluster adjudication
(Step 2's verdict lines, the `.m` citations); section 3: the Phase-2
decisions (Step 3, with the cost numbers); the stamp header (date,
build_info). Sections 4-7 (the fixes, the re-measurement, the 788
recovery, the regression gates) are stubs Task 5/6 fill — marked as such,
NOT pre-written (the measured-claims discipline: no claim before its
measurement).

```bash
git add docs/corpus-class3-deferred-uplift.md
git commit -m "campaign: triage distribution + adjudication + phase-2 decision record"
```

---

### Task 4: The Phase-2 fixes (exactly the decision record's list)

One SDD brief per selected family (A, then B-items, then C-items; D is
record-only, folded into Task 6). If a family's list is empty, the family
is skipped and the skip is noted in the ledger. Sub-tasks are data-bound —
the decision record's items are the inputs; the patterns below are
complete.

#### Task 4A: Production pass 4 (if the A verdict is go)

**Files:** Modify `maxima_rubi_utils.mac` (the `mr_top` wiring);
`test_maxima_rubi.mac` (tests); rebuild the core.

- [ ] **Step 1: The `mr_top` wiring** — insert between the pass-3 block
  (line 321, `ans : %mr_dispatch_i1(...)`) and the final
  `if ans = false then (` (line 322):

```maxima
    /* Pass 4 — per-candidate implicit-1 sweep (class-3 deferred
       campaign, 2026-08-30): passes 1-3 offer the implicit-1 wrap to a
       SINGLE candidate (pass 3's shadow: the first eligible factor in
       scan order); a multi-bare-factor integrand 0-fires whenever that
       candidate is the wrong slot (the 1,033-entry class-3 deferred
       population's dominant mechanism —
       probes/corpus/06-class3-deferred-mechanisms.out). For each bare
       top-level factor, a full table scan with the shadow offering THAT
       factor, both scan directions; the skip conditions (an explicit-
       power factor present — the shadow-dead f1 case, documented in
       docs/corpus-class3-deferred-uplift.md section 3 — or k < 2) cost
       zero scans. TOP-LEVEL, fb=false ONLY, after passes 1-3 0-fire:
       a passing entry fired earlier and never reaches the sweep, so
       nothing currently passing can change — the same safety argument
       as passes 2-3. Measured cost: the campaign record section 3. */
    if is(ans = false) and not fb then
      ans : %mr_pass4_scan(f, x, mr_rule_table, depth_level),
```

  (the comment's cost sentence is filled with the measured number at
  Task-5 time — a placeholder the implementer MUST fill from the record
  before committing; if the record is not yet written, use the
  decision-record cost line verbatim.)

- [ ] **Step 2: Layer A tests** — `test_pass4()` in `test_maxima_rubi.mac`
  (called from the main list, after `test_class3_headvar()` at line 77):
  - **Sweep rescue:** up to 3 entries taken from the calibration
    `.out`'s FIRE4 table (spanning ≥ 2 families when available):
    `check_not("pass4 <name>", is(string(op(rubi(<f>, x))) = "unintegrable"))`
    plus the suite's verification idiom (the `check_bool` of a
    `simplify(diff(ans, x) - f) = 0`-style zero-chain, mirroring
    `test_class3_headvar`'s checks).
  - **Gating non-interference:** f1 (the shadow-dead explicit-power
    shape): `check("pass4 f1 noun", op(rubi(f1, x)), 'unintegrable)` —
    pass 4 must NOT answer it (its sweep is skipped; the documented
    mechanism strictness stands). A `D-NEST` entry from the decision
    record: `check("pass4 nest noun", op(rubi(<f>, x)), 'integrate)` —
    the nested 0-fire answer is unchanged (fb gates the sweep off for
    nested dispatches by construction; the check pins it).
  - **Pass-3 invariance:** the existing headvar/f2-class checks already
    pin pass-3 behavior — the suite staying green IS the check (no new
    code; the 743+n/0 gate).
- [ ] **Step 3: Gates + commit**

```bash
maxima --very-quiet -b test_maxima_rubi.mac | tail -1      # 0 failed, n = 743 + new
sh test/build_rules_core.sh                                  # rebuilt core bakes the wiring
python3 generator/generate_rules.py --class 3 && git status --porcelain rules/   # byte-identity: empty
git add -A && git commit -m "pass 4: production wiring in mr_top + Layer A mechanics tests"
```

#### Task 4B: B-port fixes (one sub-brief per decision-record item)

Per item (rule R in ported file F, clause C, the `.m` rule M with line
citation, the generator location G):

- [ ] **Step 1:** fix G (the translation in `generator/generate_rules.py`
  or `generator/translation_table.py` — the clause's translation
  corrected to match the `.m` clause line-cited; if G is a
  family-specific code path, the fix is there, still under the
  generator — the rule `.mac` files are generated, never hand-edited).
- [ ] **Step 2:** `python3 generator/generate_rules.py --class 3 --only F`
  → `git diff rules/` shows EXACTLY F changed, the changed rule(s)'
  clause(s) matching the `.m` line-cited; sibling rules in F and all
  other files byte-identical (the diff is reviewed clause-for-clause).
- [ ] **Step 3:** a Layer A test per fixed rule: the failing deferred
  entry (from the decision record) now answers — `check_not` on the
  noun op + the zero-chain verification idiom.
- [ ] **Step 4:** gates (Layer A 0-failed; full `--class 3`
  byte-identity; core rebuild + stamp) + commit
  `fix: <F> r<N> clause port-bug vs <.m>:<line> (class-3 deferred campaign)`.

#### Task 4C: C-in-Rubi ports (one sub-brief per decision-record item)

Per item (`.m` rule M in `.m` file S, target ported file F):

- [ ] **Step 1:** port M through the class-3 generator pipeline (the
  translation-table row for M's conditions/replacement predicates, the
  witness per the `rules/class3/` file convention, the rule appended in
  Rubi order in F's generated list — the generator owns the file, the
  port is generator data + a regeneration, never a hand-edit of
  `rules/`).
- [ ] **Step 2:** regenerate (`--class 3 --only F` then full `--class 3`),
  diff-review (only F gained rule(s); byte-identity of the rest), the
  new rule's pattern + cond checked against the `.m` line-cited.
- [ ] **Step 3:** Layer A: the decision-record entry for this port now
  answers (the check_not + zero-chain idiom) + a direct binding check
  (`_mr_pat_<F>_r<N>(f, x)` non-false on the entry, the
  `test_class3_headvar` idiom).
- [ ] **Step 4:** gates (Layer A; byte-identity; core rebuild + stamp) +
  commit `port: <S>.m r<M> -> rules/class3/<F> (class-3 deferred campaign)`.

(If a C item's `.m` rule uses a predicate the translation table lacks,
the sub-brief adds the table row first — the standing generator
discipline, the milestone-3 pattern.)

---

### Task 5: Phase-3 re-measurement

**Files:** `test/corpus_class3.out` / `test/corpus_class1.out` /
`test/corpus_class2.out` (re-run; each backed up first); the campaign
record sections 4-5 filled.

- [ ] **Step 1: Back up the three records**

```bash
cd /home/serge/src/maxima-rubi
for n in 3 1 2; do cp test/corpus_class$n.out test/corpus_class$n.campaign-baseline.out; done
```

- [ ] **Step 2: Full class-3 run (the campaign A/B)**

```bash
python3 test/launch_class_shards.py "3 Logarithms" test/corpus_class3.out test/corpus_driver.py --launch
setsid sh test/wait_and_merge.sh test/corpus_class3.shard-pids test/merge_class_shards.py test/class3_merge.out "3 Logarithms" test/corpus_class3.out test/corpus_driver.py "corpus_class3.shard*.out" &
# watch; completeness asserted by the merge: 3085/3085
```

- [ ] **Step 3: Entry-level A/B (class 3)** — the controller (or a
  subagent) diffs the new `test/corpus_class3.out` against
  `test/corpus_class3.campaign-baseline.out` on the (rel, n) keys:
  the transition table (PASS→PASS / FAIL→PASS / PASS→FAIL /
  FAIL→FAIL, with per-class detail). **Regression gate: zero
  unattributed PASS→FAIL** — every PASS→FAIL individually attributed
  and dispositioned in the record before acceptance. Expected shape:
  the FIRE4/B/C-fixed entries FAIL→PASS (the 788 shrinks); the D
  clusters unchanged; anything else = an investigation item.

- [ ] **Step 4: Full class-1 + class-2 runs (the standing shared-dispatch
  gate)**

```bash
python3 test/launch_class_shards.py "1 Algebraic functions" test/corpus_class1.out test/corpus_driver.py --launch
setsid sh test/wait_and_merge.sh ... "1 Algebraic functions" test/corpus_class1.out ... &   # same pattern
# then class 2 the same way ("2 Exponentials" -> test/corpus_class2.out)
```

  A/B vs the standing records (20,069 / 594): **FAIL→PASS only** is the
  expected shape (the sweep is additive on the 0-firing path); every
  other transition individually attributed (record + the ticket-02
  7-entry matcher-state families and the ticket-01 slow-form entries
  explicitly checked, per spec §5.3).

- [ ] **Step 5: The 100 s timeout re-check** on the new class-3 record's
  `timeout` class (the standing protocol):

```bash
python3 test/launch_timeout_rerun.py test/corpus_class3.out 100 test/corpus_class3.timeout-rerun2 --launch
setsid sh test/wait_timeout_rerun.sh test/corpus_class3.timeout-rerun2 >> test/corpus_class3.timeout-rerun2/wait.log 2>&1 &
```

- [ ] **Step 6: Standing gates** — Layer A (0 failed), byte-identity
  (all three classes), core fingerprint `on` (the driver's
  `rules_core_state`), and the record sections 4 (the re-measurement
  numbers: the new class-3 PASS count, the transition tables, the
  timeout re-check result) and 5 (the 788/329 recovery per mechanism,
  the per-file residue with the why-not lines from the decision
  record) are written with the measurements.

- [ ] **Step 7: Commit** — the three new records + the backups + the
  record sections 4-5:
  `campaign: phase-3 re-measurement (class-3 A/B + class-1/2 shared-dispatch gate)`.

---

### Task 6: Acceptance record, ticket 04, TODO, ledger, final gates

**Files:** `docs/corpus-class3-deferred-uplift.md` (completed);
`.scratch/class1-ab-remainders/issues/04-matcher-backtracking-feasibility.md`;
`todo/TODO.md`; `AGENTS.md` (Layer-A count line, only if it changed);
`.superpowers/sdd/progress.md` (ledger).

- [ ] **Step 1: Complete the campaign record** — section 6: the
  acceptance criteria scorecard against spec §4 (1: the 788 shrinkage
  with the per-mechanism recovery + the 329 subset, separately, and the
  per-family residue with why-not; 2: the regression-gate result, the
  attributed PASS→FAIL list (empty or dispositioned); 3: the standing
  gates' results; 4: the probe citations for every claim; 5: the
  ticket-04 status line); section 7: the stamp (date, build_info, the
  core fingerprint before/after, the record file hashes). Re-verify
  every number against the committed `.out` files (the record is a view
  over the records, never a new source of numbers).
- [ ] **Step 2: Ticket 04** — status → `partially answered by
  docs/corpus-class3-deferred-uplift.md`: question 3 (the backtracking
  recovery measurement) is answered on the class-3 full population
  (the FIRE4 mass + the 0FIRE-EXPL binding-evidence mass, with the
  numbers); option (ii) (the backtracking findfun shadow generalized —
  implemented as pass 4, the shadow-index form, shipped/NOT shipped per
  the A verdict, with the cost disposition); the remaining questions
  (the annotated match-path map, the loss propagation past `findfun`
  into `matmatch`, the `../maxima-lists` prior art, the upstream patch
  sketch) restated as open.
- [ ] **Step 3: `todo/TODO.md`** — the deferred-remainder work item from
  the milestone-3 close → the campaign's closed state (the new numbers,
  the pointer to the record); no stale "next" left pointing at the
  superseded remainder.
- [ ] **Step 4: `AGENTS.md`** — the Layer-A count line updated to the
  final n (the growth chain appended, the 743 → n entry).
- [ ] **Step 5: Final gates** — Layer A 0-failed (final n), byte-identity
  (all three classes), core fingerprint consistent, and one last
  `git status --porcelain` review (only intended files).
- [ ] **Step 6: The ledger** — the campaign's ledger entries
  (per-task, already appended during SDD; the final entry: the
  acceptance scorecard + the residue) appended to
  `.superpowers/sdd/progress.md` under `## Campaign: class-3 deferred`.
- [ ] **Step 7: Commit** — `campaign: class-3 deferred acceptance record + ticket 04 + TODO`.

---

## Self-review (plan vs spec, run at writing time)

- **Spec coverage:** §3.1 Phase 1 → Task 1 (mechanism) + Task 2 (probe:
  production trace, sweep, drill — the spec's "non-firing drill …
  matchlist binding and cond clauses evaluated clause by clause" is the
  Step-3 drill block; the spec's materialization variant is replaced by
  the design-note mechanism, documented as a plan decision with the
  measured-derivation rationale) + Task 3 (distribution, calibration
  gate, C-shape adjudication as a recorded judgement). §3.2 Phase 2 →
  Task 4 (A/B/C/D per the decision record; the "no fix chosen on
  reasoning before the distribution exists" constraint is the Task-3
  gate). §3.3 Phase 3 → Task 5 (class-3 A/B, class-1/class-2 full A/B,
  100 s re-check, Layer A, byte-identity, core stamp). §4 acceptance →
  Task 6 Step 1 (the scorecard, including "no fixed floor" — the
  record reports what the distribution made achievable). §5 risks →
  5.1 cost (Task 3 Step 3 decision rule with the fallbacks), 5.2 shared
  Lisp implementation (the design note + Task 1/2/4A all call the same
  primitives), 5.3 matcher-state fragility (Task 5 Step 4's explicit
  ticket-01/02 family check), 5.4 ticket 04 (Task 6 Step 2), 5.5 the 459
  caveat (the 329/459 split carried in every cross-tab). §6 process →
  the SDD loop + branch + no-push, the Global Constraints.
- **Placeholder scan:** the only data-bound content is where the spec
  forbids pre-deciding it (the Phase-2 fix lists — Task 4's items come
  from the Task-3 decision record, the patterns are complete; the
  Task-4A cost-comment number is filled from the measured record before
  commit, flagged in-step). No TBD/TODO in any step's code.
- **Type/name consistency:** `%mr_barefactors` → `[k, hp]` used
  identically in Task 1 (calibration), Task 2 (per-entry `.mac`),
  Task 4A (via `%mr_pass4_scan`); `%mr_p4_once(f, x, rl, depth, d, i)`
  6-arg in all three; `%mr_dispatch_p4(f, x, rl, depth)` 4-arg in the
  witness and the pass4 lisp; labels {FIRE4, D-NEST, 0FIRE-EXPL,
  0FIRE-POOL, PROD-OK} consistent between the calibration table (Task 1
  Step 9) and the merge label logic (Task 2 Step 5) — PROD-OK is the
  calibration-only label for the 8 non-deferred m=1 rows (the merge's
  input set is deferred-only, so it never appears in the `.out`).
