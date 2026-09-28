# Rule code in Lisp: emit the conditions (and maybe more) as Lisp, not Maxima

Status: needs-triage
Type: design + research (generator / dispatcher / utilities)
Filed: 2026-09-28 (from ticket 21's step-1 profile; user suggestion)

## Idea

The generator already translates every Rubi rule from Mathematica into something else: the
pattern into an `mr-match` tree string (Lisp), and the condition and replacement into Maxima
functions (`_mr_cond_<key>_r<n>`, `_mr_repl_<key>_r<n>`, 7,776 of each). The matcher, the tree
converter and the dispatcher are already Lisp. Why stop at Maxima for the rest? The same
generator could emit Lisp. The code would still call Maxima where Maxima does the mathematics
(the simplifier, `ratsimp`, `factor`, `diff`, `integrate` for verification). What it would
remove is the Maxima **interpreter** between those calls.

It may not be worth it. This ticket is to find out, one layer at a time.

## What the profile says (ticket 21, `probes/dispatch-index/01-profile.out`, `02-cond-functions.out`)

On class-4 chain entries, about 95 % of a dispatch is the condition path of attempts whose
pattern binds. Split by what the time is spent on:

- **Interpreter overhead with no mathematics in it:**
  - `%mr_containsBoolean`, a tree walk: 52-66 % of an entry's cpu. Ticket 21 step 1 replaces it
    with native Lisp.
  - `geteqR`, a list lookup at the head of every condition and replacement: 250k calls, ~1.5 s
    on 4.1.2.2 e88. This is ticket 21 revised step 2.
  - The condition bodies themselves: `block`, the `freeof`/`integerp` conjunctions, the
    `%mr_eqQ` wrappers. Each timed at a few ms self per rule, spread over thousands of rules.
- **Real mathematics:** LinearQ, PolyQ, PolyDegQ, DerivativeDivides and BinomialQ, 1-6 s
  inclusive per entry. Part of that is interpreted glue around `ratsimp`/`hipow`/`coeff`, and
  part is the simplifier itself, which a Lisp port does not make faster.

So the first two layers below are already known wins. How much remains after them is the open
question.

## Layers, cheapest first

1. **Hand-port hot utilities to Lisp**, one at a time, when a profile ranks them:
   `%mr_containsBoolean` (ticket 21 step 1), `geteqR` (step 2), then whatever tops the
   re-profile. Each port gets an oracle test against the Maxima original, as ticket 21's
   `ref_containsBoolean` does. Incremental and low risk.
2. **Maxima's own `translate` / `compile_file` on `maxima_rubi_utils.mac`.** This is a cheap
   experiment, but translated code has different semantics in places (mode declarations, `is`,
   special variables), and AGENTS.md's TLS section warns that compiled or translated rule code
   can bring back the special-variable exhaustion. Probe 08 (`probes/matcher/08-runtime-load`)
   has to be re-run with any such change.
3. **The generator emits conditions as Lisp.** A condition is almost always a conjunction of
   `freeof`, `integerp`, comparisons and `%mr_*` predicate calls over the bound variables. As a
   Lisp lambda it could read the bindings straight from the matcher's alist. That removes the
   per-binding `mr-binding-list` → mm list → `geteqR` round trip and the interpreter, and lets a
   cheap conjunct short-circuit before any Maxima call. This is the likely sweet spot.
   Constraints: the P3 static gate (`test/check_generated_rules.py`) compares cond bodies
   byte-for-byte with the P0 base, so it needs a Lisp-emission counterpart. The Mathematica
   `With`/`Module` local handling and the condition-assignment idiom (section-9 spec A2) must
   carry over.
4. **Replacements in Lisp.** A replacement builds a Maxima expression and hands it to the
   simplifier, calling `mr_int` recursively. There is little interpreter time to save there, and
   the risk is large: every replacement's simplification order would change. Probably not worth
   it; measure before deciding.

## Steps

1. Finish ticket 21 steps 1-2 (layer 1), then re-run probes 01/02. What is left in the
   condition path decides whether layer 3 is worth doing.
2. If it is: a prototype on one rule family. The 1_4_2 `u^m v^p w^q` records are the most
   expensive in the profile. Emit their conditions as Lisp and A/B the family against the Maxima
   conditions (identical verdicts, cpu).
3. Spec amendment before any generator-wide change.

## Related

- Ticket 21 (dispatch cost; the profile and the native boolean check).
- Ticket 16 (`9_3 r41` enumeration blow-up): fewer bindings means fewer condition calls,
  whatever language the conditions are in.
- Matcher substrate spec §3.5 (the dispatcher), §3.6 (the mm list, `mr_cond_retry`).
