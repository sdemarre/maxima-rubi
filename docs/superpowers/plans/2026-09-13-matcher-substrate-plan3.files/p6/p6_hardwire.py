#!/usr/bin/env python3
"""Plan 3 Task 5 (P6): hard-wire the P5 winners; delete the three migration
switches, their runtime paths and rubi_hybrid / rubi_hybrid_exact (spec
docs/superpowers/specs/2026-09-12-matcher-substrate-design.md sections 3.5,
3.6, 4 P6, 7; plan docs/superpowers/plans/2026-09-13-matcher-substrate-plan3.md
deviations 5, 7, 11).

Usage (repo root):
  python3 <this file> --check
      verify every anchor below matches exactly once, for all eight winner
      combinations, on in-memory copies (nothing is written)
  python3 <this file> --flat-wide false|true --cond-retry true|false \\
      --model-flags true|false (--tests-only | --code-only)
      apply the test edits (Task 5 Step 3, red) or the code edits (Step 4)

Every edit is an exact text replacement that must match exactly once; all
edits of a run are computed on in-memory copies first and a mismatch stops
before any file is written.

What the winners select:
  flat-wide    false: *flat-wide* stays nil (narrow); true: its default
               becomes t (wide). Either way it stays in mr-match as the
               regression suite's knob (deviation 5); the dispatcher and
               MatchQ stop binding it.
  cond-retry   true: *cond-retry* and the first-binding path are deleted;
               false: MATCH takes a RETRY keyword (default t, MatchQ's
               semantics) and the rule dispatcher passes :retry nil.
  model-flags  true: mr_top always binds radexpand:false and
               logexpand:false around the dispatch; false: it never does.
"""

import argparse
import itertools
import os
import sys

ROOT = os.getcwd()


def dispatch_suite_edits(w):
    e = [(
        '''  check("switch defaults: mr_flat_wide false, mr_cond_retry true, mr_model_flags true",
        [mr_flat_wide, mr_cond_retry, mr_model_flags], [false, true, true]),
''',
        '''  check("the migration switches are gone (spec 3.6, hard-wired at P6)",
        [?boundp('mr_flat_wide), ?boundp('mr_cond_retry), ?boundp('mr_model_flags)],
        [false, false, false]),
''')]
    old_retry = '''  mr_cond_retry : true,
  check("mr_cond_retry true: the cond reaches the second binding",
        %mr_dispatch_tree((1+2*x)^3*sqrt(4+5*x), x, [hr], 1), 1/2),
  mr_cond_retry : false,
  check("mr_cond_retry false: the first complete binding is final",
        %mr_dispatch_tree((1+2*x)^3*sqrt(4+5*x), x, [hr], 1), false),
  mr_cond_retry : true,
'''
    if w["cond_retry"]:
        e.append((old_retry, '''  check("cond retry (the P5 winner): the cond reaches the second binding",
        %mr_dispatch_tree((1+2*x)^3*sqrt(4+5*x), x, [hr], 1), 1/2),
'''))
    else:
        e.append((old_retry, '''  check("first binding only (the P5 winner): the first complete binding is final",
        %mr_dispatch_tree((1+2*x)^3*sqrt(4+5*x), x, [hr], 1), false),
'''))
    old_flat = '''  mr_flat_wide : false,
  check("mr_flat_wide false: an Optional-reduced Plus takes no run (G-6 narrow)",
        %mr_dispatch_tree(h*x*sin(x), x, [hw], 1), false),
  mr_flat_wide : true,
  check("mr_flat_wide true: an Optional-reduced Plus takes a run (G-6 wide)",
        %mr_dispatch_tree(h*x*sin(x), x, [hw], 1), h),
  mr_flat_wide : false,
'''
    if w["flat_wide"]:
        e.append((old_flat, '''  check("G-6 wide (the P5 winner): an Optional-reduced Plus takes a run",
        %mr_dispatch_tree(h*x*sin(x), x, [hw], 1), h),
'''))
    else:
        e.append((old_flat, '''  check("G-6 narrow (the P5 winner): an Optional-reduced Plus takes no run",
        %mr_dispatch_tree(h*x*sin(x), x, [hw], 1), false),
'''))
    e.append(('''  mr_cond_retry : false,
  check_bool("MatchQ tries every binding whatever mr_cond_retry says",
''', '''  check_bool("MatchQ tries every binding",
'''))
    e.append(('''                        [x], lambda([%mr_mqb], is(%mr_mk(_t_mq4_p, %mr_mqb) = 1/2)))),
  mr_cond_retry : true,
''', '''                        [x], lambda([%mr_mqb], is(%mr_mk(_t_mq4_p, %mr_mqb) = 1/2)))),
'''))
    e.append(("   no TLS flag (mr_top's mr_model_flags binding is pinned in Layer A).",
              "   no TLS flag (mr_top's hard-wired simplifier setting is pinned in Layer A)."))
    return e


def match_suite_edits(w):
    old_flat = '''  (let ((pat "(Times (Plus g_. (Times h_. x_)) (Sin x_))")
        (ex "(Times h x (Sin x))"))
    (check-no-match "G-6 narrow: Optional-reduced Plus does not take a run" (pat ex :pre '("x")))
    (let ((*flat-wide* t))
      (check-match "G-6 wide: Optional-reduced Plus takes a run" (pat ex :pre '("x")) "g" "0" "h" "h")))
'''
    if w["flat_wide"]:
        new_flat = '''  (check "*flat-wide* defaults to the wide reading (the P5 winner)" (eq *flat-wide* t))
  (let ((pat "(Times (Plus g_. (Times h_. x_)) (Sin x_))")
        (ex "(Times h x (Sin x))"))
    (let ((*flat-wide* nil))
      (check-no-match "G-6 narrow (suite knob): Optional-reduced Plus does not take a run" (pat ex :pre '("x"))))
    (check-match "G-6 wide: Optional-reduced Plus takes a run" (pat ex :pre '("x")) "g" "0" "h" "h"))
'''
    else:
        new_flat = '''  (check "*flat-wide* defaults to the narrow reading (the P5 winner)" (null *flat-wide*))
  (let ((pat "(Times (Plus g_. (Times h_. x_)) (Sin x_))")
        (ex "(Times h x (Sin x))"))
    (check-no-match "G-6 narrow: Optional-reduced Plus does not take a run" (pat ex :pre '("x")))
    (let ((*flat-wide* t))
      (check-match "G-6 wide (suite knob): Optional-reduced Plus takes a run" (pat ex :pre '("x")) "g" "0" "h" "h")))
'''
    e = [(old_flat, new_flat)]
    old_retry = '''    (let ((*cond-retry* nil))
      (check-no-match "no retry: the first complete binding is final" (pat ex :pre '("x") :cond-hook want-m-half)))
'''
    if w["cond_retry"]:
        e.append((old_retry, ""))
    else:
        e.append((old_retry, '''    (check-no-match "no retry: the first complete binding is final" (pat ex :pre '("x") :cond-hook want-m-half :retry nil))
'''))
        e.append(('''(defun m (pattern-string expr-string &key pre cond-hook)
  "Match a compact pattern against a canonicalized tree; PRE names symbols
pre-bound to themselves (the integration variable)."
  (match (prepare (read-pattern pattern-string))
         (canonicalize (tr expr-string))
         :bindings (mapcar (lambda (n) (cons (sym n) (sym n))) pre)
         :cond-hook cond-hook))
''', '''(defun m (pattern-string expr-string &key pre cond-hook (retry t))
  "Match a compact pattern against a canonicalized tree; PRE names symbols
pre-bound to themselves (the integration variable); RETRY as MATCH's."
  (match (prepare (read-pattern pattern-string))
         (canonicalize (tr expr-string))
         :bindings (mapcar (lambda (n) (cons (sym n) (sym n))) pre)
         :cond-hook cond-hook
         :retry retry))
'''))
    return e


def layer_a_edits(w):
    old = '''  /* mr_model_flags (spec 3.6): mr_top binds radexpand:false and
     logexpand:false around the dispatch while the switch is true */
  hfl : %mr_defrule("layerA", 5,
                    "(Int (Power (Pattern x (Blank)) 7) (Pattern x (Blank Symbol)))",
                    t_disp_true, t_disp_flags),
  mr_rule_table : [hfl],
  mr_model_flags : true,
  check("mr_model_flags true: radexpand, logexpand false inside the dispatch",
        rubi(x^7, x), "false false"),
  mr_model_flags : false,
  check("mr_model_flags false: Maxima defaults inside the dispatch",
        rubi(x^7, x), "true true"),
  mr_model_flags : true,
  check("the flags are restored after mr_top", [radexpand, logexpand], [true, true]),
'''
    head = '''  hfl : %mr_defrule("layerA", 5,
                    "(Int (Power (Pattern x (Blank)) 7) (Pattern x (Blank Symbol)))",
                    t_disp_true, t_disp_flags),
  mr_rule_table : [hfl],
'''
    if w["model_flags"]:
        new = ('''  /* the G-5 simplifier setting, hard-wired at P6 (the P5 winner): mr_top
     binds radexpand:false and logexpand:false around the dispatch */
''' + head + '''  check("radexpand, logexpand false inside the dispatch (the P5 winner)",
        rubi(x^7, x), "false false"),
  check("the flags are restored after mr_top", [radexpand, logexpand], [true, true]),
''')
    else:
        new = ('''  /* the G-5 simplifier setting, hard-wired at P6 (the P5 winner: Maxima's
     defaults): mr_top dispatches under the caller's radexpand/logexpand */
''' + head + '''  check("Maxima defaults inside the dispatch (the P5 winner)",
        rubi(x^7, x), "true true"),
  check("the flags are unchanged after mr_top", [radexpand, logexpand], [true, true]),
''')
    return [(old, new)]


def match_code_edits(w):
    e = [("           #:match #:*flat-wide* #:*cond-retry* #:*test-hook*))",
          "           #:match #:*flat-wide* #:*test-hook*))")]
    old_vars = '''(defvar *flat-wide* nil
  "G-6 switch (spec 3.6 mr_flat_wide): when true, a Plus/Times item whose
Optionals all take their defaults but one argument may take a run of the
parent's elements.  Default: the narrow reading.")

(defvar *cond-retry* t
  "Spec 3.6 mr_cond_retry: when true the condition hook is called on every
complete binding until it accepts one; when false the match ends at the first
complete binding.")
'''
    reading = "wide" if w["flat_wide"] else "narrow"
    e.append((old_vars, f'''(defvar *flat-wide* {"t" if w["flat_wide"] else "nil"}
  "G-6 reading (spec 3.2): when true, a Plus/Times item whose Optionals all take
their defaults but one argument may take a run of the parent's elements (the
wide reading); when false it may not (the narrow reading).  The package runs
the {reading} reading, the P5 winner (docs/matcher-substrate-migration.md); only
the matcher regression suite binds this, to measure both readings
(test/matcher/roundtrip.lisp, controls.lisp).")
'''))
    old_match = '''(defun match (compiled expr &key bindings cond-hook)
  "Match COMPILED against EXPR (a canonical tree).  BINDINGS pre-binds names
(e.g. the integration variable).  COND-HOOK, if given, is called with each
complete binding alist; see *cond-retry*.  Returns (values alist matchedp)."
  (let ((result nil) (found nil))
    (m1 (compiled-pattern-tree compiled) expr bindings
        (lambda (b)
          (cond ((or (null cond-hook) (funcall cond-hook b))
                 (setf result b found t)
                 t)
                ((not *cond-retry*) t)
                (t nil))))
    (values result found)))
'''
    if w["cond_retry"]:
        e.append((old_match, '''(defun match (compiled expr &key bindings cond-hook)
  "Match COMPILED against EXPR (a canonical tree).  BINDINGS pre-binds names
(e.g. the integration variable).  COND-HOOK, if given, is called with each
complete binding alist until it accepts one: a false answer goes on to the
next binding (condition retry, the P5 winner).  Returns (values alist
matchedp)."
  (let ((result nil) (found nil))
    (m1 (compiled-pattern-tree compiled) expr bindings
        (lambda (b)
          (cond ((or (null cond-hook) (funcall cond-hook b))
                 (setf result b found t)
                 t)
                (t nil))))
    (values result found)))
'''))
    else:
        e.append((old_match, '''(defun match (compiled expr &key bindings cond-hook (retry t))
  "Match COMPILED against EXPR (a canonical tree).  BINDINGS pre-binds names
(e.g. the integration variable).  COND-HOOK, if given, is called with each
complete binding alist; with RETRY (the default: MatchQ's semantics) a false
answer goes on to the next binding, without it the first complete binding is
final (the rule dispatcher's P5 winner).  Returns (values alist matchedp)."
  (let ((result nil) (found nil))
    (m1 (compiled-pattern-tree compiled) expr bindings
        (lambda (b)
          (cond ((or (null cond-hook) (funcall cond-hook b))
                 (setf result b found t)
                 t)
                ((not retry) t)
                (t nil))))
    (values result found)))
'''))
    return e


def dispatch_code_edits(w):
    e = [('''
;;; ------------------------------------------------------------------
;;; Migration switches (spec 3.6). Maxima option variables; the dispatcher
;;; and MatchQ read the first two, mr_top the third.

(defmvar $mr_flat_wide nil
  "Matcher substrate switch: true = the wide G-6 run-grouping of an
Optional-reduced Plus/Times item; false (default) = the narrow reading.")

(defmvar $mr_cond_retry t
  "Matcher substrate switch: true (default) = a rule's cond runs on every
complete binding until one is accepted; false = on the first complete
binding only.")

(defmvar $mr_model_flags t
  "Matcher substrate switch: true (default) = mr_top binds radexpand:false
and logexpand:false around the dispatch (the G-5 arm); false = Maxima
defaults.")
''', "")]
    old_doc = '''is(cond) = true accepts; false, unknown or an error goes on to the next
binding (mr_cond_retry). Returns the accepted mm list, or nil."'''
    if w["cond_retry"]:
        e.append((old_doc, '''is(cond) = true accepts; false, unknown or an error goes on to the next
binding (condition retry, the P5 winner). Returns the accepted mm list, or
nil."'''))
    else:
        e.append((old_doc, '''is(cond) = true accepts; false, unknown or an error ends the match: the
first complete binding is final (the P5 winner). Returns the accepted mm
list, or nil."'''))
        e.append(('''       (mr-rule-pattern rule) expr :bindings pre
''', '''       (mr-rule-pattern rule) expr :bindings pre :retry nil
'''))
    e.append(('''(defmacro with-mr-switches (&body body)
  `(let ((mr-match:*flat-wide* (not (null $mr_flat_wide)))
         (mr-match:*cond-retry* (not (null $mr_cond_retry))))
     ,@body))

''', ""))
    e.append(('''        (with-mr-switches
          (dolist (h (cdr table) nil)
            (let ((r (mr-apply-rule (mr-rule-of h) expr pre f x)))
              (when r (return r)))))))))''', '''        (dolist (h (cdr table) nil)
          (let ((r (mr-apply-rule (mr-rule-of h) expr pre f x)))
            (when r (return r))))))))'''))
    e.append(("(with-mr-switches (mr-accept (mr-rule-of h) expr pre x nil))",
              "(mr-accept (mr-rule-of h) expr pre x nil)"))
    e.append(("(with-mr-switches (mr-accept (mr-rule-of h) expr pre x t))",
              "(mr-accept (mr-rule-of h) expr pre x t)"))
    e.append(("(with-mr-switches (mr-apply-rule (mr-rule-of h) expr pre f x))",
              "(mr-apply-rule (mr-rule-of h) expr pre f x)"))
    e.append(('''binding of Int[f, x] that its cond accepts (under mr_cond_retry, as the
dispatcher runs it), or false — a test and debugging entry."''', '''binding of Int[f, x] that its cond accepts (as the dispatcher runs it), or
false — a test and debugging entry."'''))
    e.append(('''binding list. MatchQ semantics: every complete binding is tried
(mr_cond_retry does not apply). A pattern prepare rejects, or an out-of-range''', '''binding list. MatchQ semantics: every complete binding is tried (whatever
the rule dispatcher does). A pattern prepare rejects, or an out-of-range'''))
    e.append(('''    (let ((mr-match:*flat-wide* (not (null $mr_flat_wide)))
          (mr-match:*cond-retry* t))
      (mr-guarded (setf accepted nil)
        (mr-match:match
         compiled utree
         :cond-hook (lambda (b)
                      (let ((r (errcatch
                                (let ((mb (mr-binding-list b nil)))
                                  (and (or (eq cond t)
                                           (multiple-value-bind (v ok) (mr-call cond mb)
                                             (and ok (mr-true-p v))))
                                       mb)))))
                        (when (car r)
                          (setf accepted (car r))
                          t))))))
    accepted))''', '''    (mr-guarded (setf accepted nil)
      (mr-match:match
       compiled utree
       :cond-hook (lambda (b)
                    (let ((r (errcatch
                              (let ((mb (mr-binding-list b nil)))
                                (and (or (eq cond t)
                                         (multiple-value-bind (v ok) (mr-call cond mb)
                                           (and ok (mr-true-p v))))
                                     mb)))))
                      (when (car r)
                        (setf accepted (car r))
                        t)))))
    accepted))'''))
    return e


def utils_edits(w):
    old_top = '''  /* One dispatch on MR-MATCH (maxima_rubi_dispatch.lisp
     %mr_dispatch_tree): Mathematica matching semantics, so the
     compensating rescans of the defmatch runner (passes 2-4) are gone
     (matcher substrate spec section 3.5). mr_model_flags (spec 3.6,
     the G-5 arm) binds radexpand:false and logexpand:false around the
     dispatch, so the intermediate integrands keep Mathematica's shape. */
  ans : if mr_model_flags
        then block([radexpand : false, logexpand : false],
                   %mr_dispatch_tree(f, x, mr_rule_table, depth_level))
        else %mr_dispatch_tree(f, x, mr_rule_table, depth_level),
'''
    intro = '''  /* One dispatch on MR-MATCH (maxima_rubi_dispatch.lisp
     %mr_dispatch_tree): Mathematica matching semantics, so the
     compensating rescans of the defmatch runner (passes 2-4) are gone
     (matcher substrate spec section 3.5). '''
    if w["model_flags"]:
        new_top = intro + '''The dispatch runs under
     radexpand:false and logexpand:false (the G-5 arm, spec 3.3, won the
     P5 A/B: docs/matcher-substrate-migration.md), so the intermediate
     integrands keep Mathematica's shape. */
  ans : block([radexpand : false, logexpand : false],
              %mr_dispatch_tree(f, x, mr_rule_table, depth_level)),
'''
    else:
        new_top = intro + '''The dispatch runs under
     the caller's radexpand/logexpand (Maxima's defaults won the G-5 A/B,
     spec 3.3: docs/matcher-substrate-migration.md). */
  ans : %mr_dispatch_tree(f, x, mr_rule_table, depth_level),
'''
    return [(old_top, new_top)]


HYBRID_START = "/* The legacy 9.1 re-dispatch entry. The manual 9.1 port called it from\n"
HYBRID_END = 'rubi_hybrid_exact(f, x) := %mr_hybrid_body(f, x, "exact")$\n\n'


def static_gate_edits(w):
    return [('ENTRY_CALL = re.compile(r"\\b(mr_int|mr_top|rubi|rubi_fallback|rubi_hybrid|rubi_hybrid_exact)\\(")',
             'ENTRY_CALL = re.compile(r"\\b(mr_int|mr_top|rubi|rubi_fallback)\\(")')]


TESTS = [("test/matcher/test_mr_dispatch.mac", dispatch_suite_edits),
         ("test/matcher/test_mr_match.lisp", match_suite_edits),
         ("test_maxima_rubi.mac", layer_a_edits)]
CODE = [("maxima_rubi_match.lisp", match_code_edits),
        ("maxima_rubi_dispatch.lisp", dispatch_code_edits),
        ("maxima_rubi_utils.mac", utils_edits),
        ("test/check_generated_rules.py", static_gate_edits)]


def apply_all(groups, w):
    out = {}
    for rel, fn in groups:
        s = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        for old, new in fn(w):
            n = s.count(old)
            if n != 1:
                raise SystemExit(f"{rel}: anchor matches {n} times: {old[:90]!r}")
            s = s.replace(old, new)
        if rel == "maxima_rubi_utils.mac":
            i, j = s.find(HYBRID_START), s.find(HYBRID_END)
            if s.count(HYBRID_START) != 1 or s.count(HYBRID_END) != 1 or not i < j:
                raise SystemExit("maxima_rubi_utils.mac: rubi_hybrid block markers not found once, in order")
            s = s[:i] + s[j + len(HYBRID_END):]
        out[rel] = s
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--flat-wide", choices=["false", "true"])
    ap.add_argument("--cond-retry", choices=["true", "false"])
    ap.add_argument("--model-flags", choices=["true", "false"])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--tests-only", action="store_true")
    mode.add_argument("--code-only", action="store_true")
    a = ap.parse_args()
    if a.check:
        for fw, cr, mf in itertools.product([False, True], repeat=3):
            w = {"flat_wide": fw, "cond_retry": cr, "model_flags": mf}
            apply_all(TESTS + CODE, w)
        print("anchors ok: 8 combinations")
        return 0
    if None in (a.flat_wide, a.cond_retry, a.model_flags) or not (a.tests_only or a.code_only):
        ap.error("give the three winners and --tests-only or --code-only (or --check)")
    w = {"flat_wide": a.flat_wide == "true", "cond_retry": a.cond_retry == "true",
         "model_flags": a.model_flags == "true"}
    files = apply_all(TESTS if a.tests_only else CODE, w)
    for rel, s in files.items():
        with open(os.path.join(ROOT, rel), "w", encoding="utf-8") as fh:
            fh.write(s)
        print(f"wrote {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
