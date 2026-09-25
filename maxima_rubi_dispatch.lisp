;; maxima_rubi_dispatch.lisp — the rule records, the dispatcher and the
;; MatchQ entries on MR-MATCH / MR-TREE (matcher substrate spec
;; docs/superpowers/specs/2026-09-12-matcher-substrate-design.md sections
;; 3.4-3.6), and the arity dispatchers for the two Rubi predicates the
;; rules call at more than one arity.
;;
;; Loaded by maxima_rubi.mac after maxima_rubi_utils.mac (geteqR,
;; %mr_containsBoolean, rubi_verbose, %mr_boolcheck),
;; maxima_rubi_match.lisp and maxima_rubi_tree.lisp.
;;
;; Naming (measured 2026-08-27, this build): the Lisp symbol of an
;; ALL-LOWERCASE Maxima name is upper-cased — a defmfun for %mr_defrule
;; must be |$%MR_DEFRULE| — while a name containing an uppercase letter
;; keeps its typed case (|$%mr_matchQ|). A fixed-parameter defmfun does not
;; become a callable Maxima function in this build, so every entry takes
;; (&rest args) and checks its arity.

;; Arity dispatchers for the two Rubi predicates the generated class-1
;; rules call at more than one arity: %mr_binomialQ (2 and 3 args) and
;; %mr_intBinomialQ (7, 8 and 10 args — the three DISTINCT Rubi
;; definitions, 1.1.3.2:118 / 1.1.3.3:73 / 1.1.3.4:89). Maxima has no
;; function overloading and a wrong-arity call to a := function is a
;; hard error (measured, task-7a); each defmfun below catches the args
;; and re-dispatches to the fixed-arity Maxima := body in
;; maxima_rubi_utils.mac (named <name><arity>) via the
;; (mlambda (mget sym 'mexpr) args sym t nil) call primitive (the same
;; primitive mfunction-call-aux uses to invoke a := function,
;; fcall.lisp:89-94).
;;
;; The class-1 arity census (2026-08-23, over rules/class1): binomialQ
;; 2/3 (40/1), intBinomialQ 7/8/10 (21/10/44) — the only two
;; multi-arity names. %mr_integersQ / %mr_fractionQ / %mr_rationalQ
;; are 1-arg only (scalar-or-list in that one arg) and take their calls
;; directly as committed := ports; intLinearQ (7) and intQuadraticQ (8)
;; are fixed-arity.

(defmfun |$%mr_binomialQ| (&rest args)
  (let ((f (case (length args)
             (2 '|$%mr_binomialQ2|)
             (3 '|$%mr_binomialQ3|)
             (t nil))))
    (if f (mlambda (mget f 'mexpr) args f t nil)
        (merror (intl:gettext "%mr_binomialQ: bad arity ~A") (length args)))))

(defmfun |$%mr_intBinomialQ| (&rest args)
  (let ((f (case (length args)
             (7  '|$%mr_intBinomialQ7|)
             (8  '|$%mr_intBinomialQ8|)
             (10 '|$%mr_intBinomialQ10|)
             (t nil))))
    (if f (mlambda (mget f 'mexpr) args f t nil)
        (merror (intl:gettext "%mr_intBinomialQ: bad arity ~A") (length args)))))

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

;;; The RUN switches (exact seen test design
;;; docs/superpowers/specs/2026-09-15-matcher-seen-test-intpart-design.md
;;; 3.3; mr_giveup_last and mr_inert_leak_misfire joined later). Unlike the
;;; three migration switches above these are not hard-wired by
;;; p6_hardwire.py: they stay run parameters.

(defmvar $mr_nested_fallback nil
  "Run switch: false (default) = a nested Int call that finds no rule,
hits the seen test or hits the depth cap returns mr_unintegrable, so a
run answers with Rubi's rules only; true = it falls through to Maxima's
integrate (the pre-2026-09-15 behaviour). The top-level rubi and
rubi_fallback entries are unaffected.")

(defmvar $mr_giveup_last t
  "Run switch: true (default) = %mr_dispatch_tree walks the table in two
passes, trying every ordinary rule before any GIVE-UP rule (one whose
replacement answers with Rubi's Unintegrable marker, mr_unintegrable);
false = the single walk in load order.

WHY. The port's table is LOAD order; Mathematica's is SPECIFICITY order, so
a general give-up catch-all that loads early can pre-empt a specific rule
that loads late. MEASURED 2026-09-17 on b^(3/4)/(b^(3/4) x^2 + sqrt(2)
a^(1/4) sqrt(b) sqrt(d) x + sqrt(a) b^(1/4) d): 1_2_3_5 r24 (a general
trinomial bound with n = 1, n2 = 2) fires and answers the marker, where
9_1 r12 -- Rubi's linearity pull-out Int[a_*u_,x] -> a*Int[u,x], table
position 3038 of 3513 -- binds and its cond ACCEPTS, and would pull b^(3/4)
out and leave 1/den, which integrates. Deferring the 33 class-1 markers
lets it get its turn.

This changes no Rubi SEMANTICS: a give-up rule still answers the marker
when nothing else does, which is what Unintegrable means. It only stops it
winning a race Mathematica would not have run.

NOT load-bearing on its own -- reordering ALONE recovers nothing, because
the seen-cut self-recursion of 1_2_3_5 r12 blocks the same path first. It
is half of a PAIR with the seen-cut fall-through (maxima_rubi_utils.mac,
%mr_top_body). Measured together over the 341-entry class-1 loss list at
the record's 30 s cap: 318 verified, with 300/300 control entries
unchanged.")

(defmvar $mr_inert_leak_misfire t
  "Run switch: true (default) = in the inert-trig domain a non-class-4
rule whose answer carries an inert trig head is a MISFIRE (declined like a
leaked boolean) and the walk goes on; false = the answer stands.

The inert domain is an integrand carrying one of Rubi's six inert trig heads
(%mr_isin ... %mr_icsc); it exists only below the class-4 deactivation
bridge (4_1_0_1 r1, Int[u_,x] := Int[DeactivateTrig[u,x],x]). Class-4
records re-activate as they emit and are exempt.

WHY. The port has only class 4's bridge subset, all in the TAIL, so general
records reach the deactivated integrand before any class-4 one. Most are
sound there: what they emit outside the recursive mr_int is x-free (9_1's
pull-outs) or a substitution of it (9_3 r51, FunctionOfLinear), and the
recursion's own answer is re-activated. 9_3 r41
(Int[u_.*(a_.*v_^m_.)^p_,x]) is not: its prefactor keeps v -- an inert
head -- OUTSIDE mr_int, and it reaches the answer (ticket 15). In
Mathematica a specific 4.x rule outranks r41 there. By induction on the
recursion, declining every such answer keeps every answer in the inert
domain inert-free.

MEASURED 2026-09-23 (probes/section9/07, 08): over the 286 leaking class-6
entries a non-class-4 record fires on an inert integrand in all 284 that
finish (9_3 r41 in 280). The first guard, offering such an integrand to
class-4 records ONLY, stopped every leak but cost 650 class-6 PASSes
against 209 gained: 9_3 r51 fires inertly in 612 of those 650, and the
9.1 pull-outs in most of the rest -- they are what section 9 bought for
class 6. This misfire rule was prototyped over the 859 entries that guard
changed: +151 / -4 against the unguarded branch, zero leaks.")

(defmvar $mr_last_resort_tier t
  "Run switch: true (default) = under mr_giveup_last the walk has FOUR
passes: ordinary rules; the specific give-ups; the TAIL's ordinary
records (%mr_mark_tail); the tail's give-ups. false = the two passes of
mr_giveup_last alone, the tail's ordinary records in pass 1. Ignored when
mr_giveup_last is false (the single walk in load order).

The tail is the bare-u_ records mr_load_all puts after every body list:
Int[u_,x_Symbol] is Mathematica's LEAST specific pattern, so every specific
rule -- a give-up included -- outranks it there. Class-4 tail records are
exempt from pass 3 and stay in pass 1 -- unless mr_general_after_giveups
moves 9.3's body there too, when they follow it: they are the inert-trig bridge,
guarded by their domain conditions, tried there before this switch
existed; only their give-up (4_7_5 r72, the re-activating CannotIntegrate)
waits for pass 4, AFTER 9.3's tail, where it was before this switch too
(pass 2 of mr_giveup_last, behind 9.3's ordinary tail in pass 1).

WHY (ticket 14). Under mr_giveup_last alone, 9.3's ten ordinary tail
records (pass 1) ran before the 72 Unintegrable markers of classes 1-3
(pass 2); Mathematica's specificity order puts the markers first. MEASURED
in the section-9 A/B: 189 PASS->FAIL, the whole of class 3's -96 (e.g. 3.4
e635: 9_3 r51 substitutes, then the marker fires INSIDE, contains-noun,
instead of 3_4 r39 at the top). Turning mr_giveup_last off instead loses
64 of a seeded 2,000-entry class-1 PASS sample
(probes/section9/06-giveup-switch-control.out).")

(defmvar $mr_general_after_giveups t
  "Run switch: true (default) = the ordinary records %mr_mark_general flags
(9.3's BODY, marked by mr_load_all) wait with the tail's ordinary records,
in pass 3 of the mr_last_resort_tier walk, behind the specific give-ups;
false = they stay in pass 1. Needs mr_giveup_last; a flagged
give-up stays in pass 2. Under this switch the class-4 bridge's ordinary
tail records lose their pass-1 exemption and join pass 3 too, in table
order -- i.e. still after 9.3's body, as in the load order.

WHY (ticket 14). The tail tier alone leaves 49 give-up-bucket entries
whose top-level rule is a 9.3 BODY record -- r52 Int[u_/x,x], r54, r46,
r53, r49 -- general patterns that Mathematica's specificity order puts
behind the class-1-3 Unintegrable markers (probes/section9/09). The order
is then Mathematica's by specificity class: specific rules, specific
give-ups, the general body, every bare-u_ record in load order, the bare-u_
give-ups. Moving the body WITHOUT the bridge put 4_1_0_1 r1 ahead of 9.3's
body and cost 24 class-6 answers to the inert route's expense (probe 10's
first run: 0.8-5 s -> timeout). MEASURED with the bridge moved too
(probes/section9/10-general-body.out, same core, paired, tail tier on in
both arms): the give-up bucket +51 / -0 (178 of 214 PASS), probe 06's
2,000 class-1 control unchanged, section 9's 1,132 gains +2 / -1 (the -1
expected -> timeout at 29.8 s).")

(defparameter +mr-inert-ops+
  '($%mr_isin $%mr_icos $%mr_itan $%mr_icot $%mr_isec $%mr_icsc)
  "The Maxima operators of Rubi's six inert trig heads (maxima_rubi_tree.lisp).")

(defun mr-carries-inert-p (e)
  "True when the Maxima expression E contains an inert trig head. A CRE is
read through its general form: its kernels sit in the header, and its body
is an improper list."
  (cond ((or (atom e) (atom (car e))) nil)
        ((eq (caar e) 'mrat) (mr-carries-inert-p ($ratdisrep e)))
        ((member (caar e) +mr-inert-ops+ :test #'eq) t)
        (t (loop for tail on (cdr e) thereis (mr-carries-inert-p (car tail))))))

(defmvar $mr_max_depth 16
  "Run switch: the dispatch depth cap. mr_top counts nested dispatches in
depth_level and takes the cap branch beyond this many; every cap hit is
counted in mr_depth_cap_hits (the run's .caps census). Rubi's own step
counts exceed 16 on 272 / 24 / 358 corpus entries (classes 1 / 2 / 3).")

;; Maxima variables the utils define before this file loads (declared here
;; so their references compile as special).
(defvar $rubi_verbose nil)
(defvar $%mr_boolcheck t)

(defun mr-verbose (fmt &rest args)
  (when $rubi_verbose
    (apply #'mtell fmt args)))

;;; ------------------------------------------------------------------
;;; Rule records (spec 3.4): %mr_defrule(key, n, pattern, cond, repl)
;;; prepares the pattern once, at load, and returns the rule's handle (its
;;; 1-based index in *mr-rules*); mr_rules_<key> and mr_rule_table are
;;; Maxima lists of handles.

(defstruct (mr-rule (:constructor make-mr-rule (key n pattern pattern-text cond repl giveup)))
  key n pattern pattern-text cond repl giveup
  (tail nil)      ; set by %mr_mark_tail: a bare-u_ tail record (mr_load_all)
  (general nil))  ; set by %mr_mark_general: a general body record

(defun mr-class4-rule-p (rule)
  "True when RULE is a class-4 record (its key starts \"4_\")."
  (let ((key (mr-rule-key rule)))
    (and (stringp key) (> (length key) 1) (string= "4_" key :end2 2))))

(defun mr-form-has-symbol-p (sym form)
  "True when SYM occurs anywhere in the cons tree FORM."
  (cond ((eq form sym) t)
        ((consp form) (or (mr-form-has-symbol-p sym (car form))
                          (mr-form-has-symbol-p sym (cdr form))))
        (t nil)))

(defun mr-giveup-repl-p (repl)
  "True when the rule replacement REPL answers with Rubi's Unintegrable
marker, i.e. its body calls mr_unintegrable.

Detected from the body rather than a hand-kept list, so it cannot drift when
a rule file is regenerated with a different rule count. Exact on the pinned
rules: mr_unintegrable occurs 72 times across rules/class{1,2,3}, EVERY one
of them the tail expression of a repl body and nowhere else (census
2026-09-17) -- 33 in class 1 (the set the give-up reordering was measured
on), 8 in class 2, 31 in class 3.

The generated rule files define _mr_repl_<key>_r<n> BEFORE the %mr_defrule
call that registers it, so the mexpr is always in place by the time this
runs at load."
  (let ((body (and (symbolp repl) (mget repl 'mexpr))))
    (and body (mr-form-has-symbol-p '$mr_unintegrable body) t)))

(defvar *mr-rules* (make-array 4096 :adjustable t :fill-pointer 0)
  "Every rule record %mr_defrule registered, in load order.")

(defmfun |$%MR_DEFRULE| (&rest args)
  (unless (= (length args) 5)
    (merror (intl:gettext "%mr_defrule: expected 5 args, found ~A") (length args)))
  (destructuring-bind (key n pattern cond repl) args
    (let ((compiled (handler-case (mr-match:prepare (mr-match:read-tree pattern))
                      (error (e)
                        (merror (intl:gettext "%mr_defrule: ~A r~A: ~A") key n
                                (princ-to-string e))))))
      (vector-push-extend (make-mr-rule key n compiled pattern cond repl
                                        (mr-giveup-repl-p repl))
                          *mr-rules*)
      (fill-pointer *mr-rules*))))

(defmfun |$%MR_RULE_COUNT| (&rest args)
  "%mr_rule_count(): the number of rule records %mr_defrule has registered,
i.e. the largest handle -- every handle is 1..%mr_rule_count(). For the
real-table gate (test/test_rule_table_order.mac, class 4, 2026-09-25): a
registered record that mr_load_all forgot to put in mr_rule_table is then
seen, not only the ones the table holds."
  (unless (null args)
    (merror (intl:gettext "%mr_rule_count: expected no arguments, found ~A") (length args)))
  (fill-pointer *mr-rules*))

(defun mr-rule-of (handle)
  (if (and (integerp handle) (<= 1 handle (fill-pointer *mr-rules*)))
      (aref *mr-rules* (1- handle))
      (merror (intl:gettext "rubi: not a rule handle: ~M") handle)))

;;; ------------------------------------------------------------------
;;; Bindings -> Maxima

(defvar *mr-head-verbs* nil
  "Tree head symbol -> the Maxima operator symbol of the MR-TREE head table
(built on first use; the smallest arity wins).")

;; The table's operator is the symbol Maxima itself reads for the typed name:
;; `asin` reads as the noun %ASIN (the parser's alias), so the cond's literal
;; list [asin, acos, ...] holds %ASIN — a $verbify'd $ASIN is not member of it
;; (measured 2026-09-13, plan-2 pre-validation, probe_f12.mac).
(defun mr-head-verb (sym)
  (unless *mr-head-verbs*
    (let ((table (make-hash-table :test 'eq)))
      (dolist (row (sort (copy-list (mr-tree:head-table)) #'> :key #'second))
        (setf (gethash (first row) table) (third row)))
      (setf *mr-head-verbs* table)))
  (gethash sym *mr-head-verbs*))

(defun mr-binding-value (tree)
  "A bound tree -> its Maxima value. A function head bound to a pattern
variable (F_[...], 3_1_5 r58/r59, 3_3 r58, 3_4 r37) becomes the Maxima
operator symbol the typed name reads as (ArcSinh -> %asinh), which the cond
compares with %mr_memberQ and the repl applies; anything else goes through
tree->max."
  (or (and (symbolp tree) (mr-head-verb tree))
      (mr-tree:tree->max tree)))

(defun mr-binding-list (bindings skip)
  "MR-MATCH bindings -> the Maxima list [name = value, ...] in pattern order,
without the pre-bound name SKIP."
  (cons '(mlist simp)
        (loop for (name . value) in (reverse bindings)
              unless (eq name skip)
                collect (list '(mequal simp) (mr-tree:tree->max name)
                              (mr-binding-value value)))))

;;; ------------------------------------------------------------------
;;; Calling Maxima under errcatch

(defun mr-call (fn &rest args)
  "Call the Maxima function (or lambda) FN on ARGS under errcatch:
(values result t), or (values nil nil) when the call signals an error."
  (let ((r (errcatch (apply #'mfuncall fn args))))
    (if r (values (car r) t) (values nil nil))))

(defun mr-true-p (v)
  "is(v) = true (unknown and false are not true)."
  (eq (meval `(($is) ((mquote) ,v))) t))

(defun mr-contains-boolean-p (e)
  "%mr_containsBoolean(e); an error counts as containing one."
  (multiple-value-bind (r ok) (mr-call '|$%mr_containsBoolean| e)
    (or (not ok) (eq r t))))

(deftype mr-fault ()
  "The condition classes mr-guarded catches: any serious-condition except
sb-sys:interactive-interrupt (a Ctrl-C during matching — the dispatcher must
stay interruptible, not turn every rule into a silent 'no match' and keep
walking the table) and sb-ext:timeout (a future Lisp-level deadline must
propagate, not be swallowed as a rule fault)."
  '(and serious-condition
        (not sb-sys:interactive-interrupt)
        (not sb-ext:timeout)))

(defmacro mr-guarded (fault-form &body body)
  "Run BODY; a signalled fault inside it (an mr-fault — any serious-condition
except an interactive-interrupt or a timeout, which propagate: a Lisp error
that escaped errcatch, a storage-condition) unwinds Maxima's dynamic bindings
as errcatch does and yields FAULT-FORM (spec 3.5 step 5). Not covered: SBCL
control-stack exhaustion hit inside an allocation is fatal before any
condition is signalled — a runaway Maxima recursion in a cond killed the
process in 5 of 6 measured shapes (probes/matcher/07)."
  (let ((saved (gensym "SAVED")) (c (gensym "C")))
    `(let ((,saved (cons bindlist loclist)))
       (handler-case (progn ,@body)
         (mr-fault (,c)
           (errlfun1 ,saved)
           (let ((condition ,c))
             (declare (ignorable condition))
             ,fault-form))))))

;;; ------------------------------------------------------------------
;;; The dispatcher (spec 3.5)

(defun mr-accept (rule expr pre x check-cond)
  "Match RULE's pattern against EXPR (x pre-bound). The condition hook
converts each complete binding into the mm list, rejects one holding a
boolean and — when CHECK-COND — runs the rule's cond under errcatch:
is(cond) = true accepts; false, unknown or an error goes on to the next
binding (mr_cond_retry). Returns the accepted mm list, or nil."
  (let ((accepted nil)
        (xname (car (first pre))))
    (mr-guarded
        (progn (mr-verbose "rubi: rule ~A r~A matcher fault: ~A~%"
                           (mr-rule-key rule) (mr-rule-n rule) (princ-to-string condition))
               (setf accepted nil))
      (mr-match:match
       (mr-rule-pattern rule) expr :bindings pre
       :cond-hook (lambda (b)
                    (let ((r (errcatch
                              (let ((mm (mr-binding-list b xname)))
                                (and (not (mr-contains-boolean-p mm))
                                     (or (not check-cond)
                                         (multiple-value-bind (v ok) (mr-call (mr-rule-cond rule) mm x)
                                           (and ok (mr-true-p v)))
                                         (progn
                                           (mr-verbose "rubi: rule ~A r~A cond not accepted with ~M~%"
                                                       (mr-rule-key rule) (mr-rule-n rule) mm)
                                           nil))
                                     mm)))))
                      (when (car r)
                        (setf accepted (car r))
                        t)))))
    accepted))

(defun mr-integrand (f x)
  "-> (values expr pre) for matching Int[f, x], or nil when f does not
convert."
  (let ((xtree (mr-tree:max->tree x)))
    (mr-guarded (progn (mr-verbose "rubi: integrand does not convert: ~M~%" f) nil)
      (values (list (mr-match:sym "Int") (mr-tree:max->tree f) xtree)
              (list (cons (mr-match:sym "x") xtree))))))

(defun mr-apply-rule (rule expr pre f x)
  "Try one rule on the converted integrand: the answer, or nil (no match,
decline or misfire)."
  (let ((mm (mr-accept rule expr pre x t))
        (key (mr-rule-key rule))
        (n (mr-rule-n rule)))
    (when mm
      (multiple-value-bind (r ok) (mr-call (mr-rule-repl rule) mm x)
        (cond ((not ok)
               (mr-verbose "rubi: rule ~A r~A misfire (repl error) on ~M with ~M~%" key n f mm) nil)
              ((null r)
               (mr-verbose "rubi: rule ~A r~A declined on ~M with ~M~%" key n f mm) nil)
              ((and $%mr_boolcheck (mr-contains-boolean-p r))
               (mr-verbose "rubi: rule ~A r~A misfire (boolean leaked) on ~M with ~M~%" key n f mm) nil)
              ((and $mr_inert_leak_misfire (not (mr-class4-rule-p rule))
                    (mr-carries-inert-p r) (mr-carries-inert-p f))
               (mr-verbose "rubi: rule ~A r~A misfire (inert head leaked) on ~M with ~M~%" key n f mm) nil)
              (t
               (mr-verbose "rubi: rule ~A r~A fired on ~M with ~M~%" key n f mm) r))))))

(defmacro with-mr-switches (&body body)
  `(let ((mr-match:*flat-wide* (not (null $mr_flat_wide)))
         (mr-match:*cond-retry* (not (null $mr_cond_retry))))
     ,@body))

(defmfun |$%MR_DISPATCH_TREE| (&rest args)
  "%mr_dispatch_tree(f, x, table, depth): walk the rule handles of TABLE in
order; the first rule whose pattern binds, whose cond accepts and whose repl
answers wins. false when no rule answers.

Under mr_giveup_last (the default) the walk is TWO passes: pass 1 skips the
give-up rules (mr-rule-giveup: the replacement answers Rubi's Unintegrable
marker) and pass 2 tries them, so a give-up catch-all can only win once
every ordinary rule has declined. See the $mr_giveup_last docstring for what
that buys and why it changes no Rubi semantics.

Under mr_last_resort_tier (the default) the tail records mr_load_all marks
(%mr_mark_tail) wait further: FOUR passes -- ordinary, specific give-up,
tail ordinary, tail give-up (mr-rule-tier; see that switch's docstring).
Under mr_general_after_giveups (the default) 9.3's general body
(%mr_mark_general) and the class-4 bridge join the tail's ordinary records
in pass 3, in table order.

The reordering is done HERE, over the table the caller hands in, rather than
by baking a second reordered table at load: test_maxima_rubi.mac swaps its
own cumulative table into mr_rule_table in ~20 sections, and a table built
once at load would be stale at every one of those sites. Pass 1 costs one
extra slot read per handle; pass 2 allocates at most the handful of give-up
handles (33 of 3,513 in class 1) and only runs when pass 1 found nothing."
  (unless (= (length args) 4)
    (merror (intl:gettext "%mr_dispatch_tree: expected 4 args, found ~A") (length args)))
  ;; (the fourth argument, the recursion depth, is informational: DEPTH is
  ;; a Maxima special variable, so it is not bound here)
  (destructuring-bind (f x table &rest ignored) args
    (declare (ignore ignored))
    (unless ($listp table)
      (merror (intl:gettext "%mr_dispatch_tree: the table is not a list: ~M") table))
    (multiple-value-bind (expr pre) (mr-integrand f x)
      (when expr
        (with-mr-switches
          (if (null $mr_giveup_last)
              (dolist (h (cdr table) nil)
                (let ((r (mr-apply-rule (mr-rule-of h) expr pre f x)))
                  (when r (return r))))
              ;; tiers 0-3: ordinary, give-up, tail ordinary, tail give-up
              ;; (without mr_last_resort_tier: ordinary, give-up only)
              (let ((later (vector nil nil nil nil)))
                (or (dolist (h (cdr table) nil)
                      (let* ((rule (mr-rule-of h))
                             (tier (mr-rule-tier rule)))
                        (if (plusp tier)
                            (push rule (aref later tier))
                            (let ((r (mr-apply-rule rule expr pre f x)))
                              (when r (return r))))))
                    (loop for tier from 1 to 3
                          thereis (dolist (rule (nreverse (aref later tier)) nil)
                                    (let ((r (mr-apply-rule rule expr pre f x)))
                                      (when r (return r)))))))))))))

(defun mr-rule-tier (rule)
  "The pass of %mr_dispatch_tree's give-up-last walk RULE runs in: 0
ordinary, 1 give-up, 2 tail ordinary (and, under
$mr_general_after_giveups, general ordinary), 3 tail give-up (see
$mr_last_resort_tier; without it, a tail record is 0 or 1)."
  (let ((giveup (mr-rule-giveup rule)))
    (cond ((and $mr_last_resort_tier (mr-rule-tail rule))
           (cond (giveup 3)
                 ;; the bridge stays in pass 1 -- unless the general body
                 ;; moved behind the give-ups, when it must follow it there
                 ;; to keep its place after 9.3's body (probe 10)
                 ((and (mr-class4-rule-p rule) (not $mr_general_after_giveups)) 0)
                 (t 2)))
          (giveup 1)
          ((and $mr_general_after_giveups (mr-rule-general rule)) 2)
          (t 0))))

(defmfun |$%MR_MARK_TAIL| (&rest args)
  "%mr_mark_tail(handles): mark the rules of HANDLES as bare-u_ TAIL
records (the last-resort tier of $mr_last_resort_tier); the number marked.
mr_load_all calls it on mr_rule_table_tail_handles."
  (unless (and (= (length args) 1) ($listp (car args)))
    (merror (intl:gettext "%mr_mark_tail: expected one list of handles, found ~M") (cons '(mlist) args)))
  (let ((rules (mapcar #'mr-rule-of (cdar args))))
    (dolist (rule rules (length rules))
      (setf (mr-rule-tail rule) t))))

(defmfun |$%MR_MARK_GENERAL| (&rest args)
  "%mr_mark_general(handles): mark the rules of HANDLES as GENERAL body
records (see $mr_general_after_giveups); the number marked. mr_load_all
calls it on 9.3's body list."
  (unless (and (= (length args) 1) ($listp (car args)))
    (merror (intl:gettext "%mr_mark_general: expected one list of handles, found ~M") (cons '(mlist) args)))
  (let ((rules (mapcar #'mr-rule-of (cdar args))))
    (dolist (rule rules (length rules))
      (setf (mr-rule-general rule) t))))

(defmfun |$%MR_GENERAL_HANDLES| (&rest args)
  "%mr_general_handles(table): the handles of TABLE marked as general body
records, in table order -- for tests and probes."
  (unless (= (length args) 1)
    (merror (intl:gettext "%mr_general_handles: expected 1 arg, found ~A") (length args)))
  (let ((table (car args)))
    (unless ($listp table)
      (merror (intl:gettext "%mr_general_handles: the table is not a list: ~M") table))
    (cons '(mlist simp)
          (remove-if-not (lambda (h) (mr-rule-general (mr-rule-of h))) (cdr table)))))

(defmfun |$%MR_TAIL_HANDLES| (&rest args)
  "%mr_tail_handles(table): the handles of TABLE marked as tail records, in
table order -- for tests and probes."
  (unless (= (length args) 1)
    (merror (intl:gettext "%mr_tail_handles: expected 1 arg, found ~A") (length args)))
  (let ((table (car args)))
    (unless ($listp table)
      (merror (intl:gettext "%mr_tail_handles: the table is not a list: ~M") table))
    (cons '(mlist simp)
          (remove-if-not (lambda (h) (mr-rule-tail (mr-rule-of h))) (cdr table)))))

(defmfun |$%MR_GIVEUP_HANDLES| (&rest args)
  "%mr_giveup_handles(table): the handles of TABLE whose rule is a give-up
rule (its replacement answers Rubi's Unintegrable marker), in table order —
the census entry behind the mr_giveup_last switch, for tests and probes."
  (unless (= (length args) 1)
    (merror (intl:gettext "%mr_giveup_handles: expected 1 arg, found ~A") (length args)))
  (let ((table (first args)))
    (unless ($listp table)
      (merror (intl:gettext "%mr_giveup_handles: the table is not a list: ~M") table))
    (cons '(mlist)
          (remove-if-not (lambda (h) (mr-rule-giveup (mr-rule-of h))) (cdr table)))))

(defmfun |$%MR_RULE_BINDINGS| (&rest args)
  "%mr_rule_bindings(handle, f, x): the mm list of the rule's first complete
binding of Int[f, x] (no cond), or false — a test and debugging entry."
  (unless (= (length args) 3)
    (merror (intl:gettext "%mr_rule_bindings: expected 3 args, found ~A") (length args)))
  (destructuring-bind (h f x) args
    (multiple-value-bind (expr pre) (mr-integrand f x)
      (and expr (with-mr-switches (mr-accept (mr-rule-of h) expr pre x nil))))))

(defmfun |$%MR_RULE_ACCEPT| (&rest args)
  "%mr_rule_accept(handle, f, x): the mm list of the rule's first complete
binding of Int[f, x] that its cond accepts (under mr_cond_retry, as the
dispatcher runs it), or false — a test and debugging entry."
  (unless (= (length args) 3)
    (merror (intl:gettext "%mr_rule_accept: expected 3 args, found ~A") (length args)))
  (destructuring-bind (h f x) args
    (multiple-value-bind (expr pre) (mr-integrand f x)
      (and expr (with-mr-switches (mr-accept (mr-rule-of h) expr pre x t))))))

(defmfun |$%MR_RULE_APPLY| (&rest args)
  "%mr_rule_apply(handle, f, x): the one rule's answer on Int[f, x] (pattern,
cond, repl, as the dispatcher runs it), or false."
  (unless (= (length args) 3)
    (merror (intl:gettext "%mr_rule_apply: expected 3 args, found ~A") (length args)))
  (destructuring-bind (h f x) args
    (multiple-value-bind (expr pre) (mr-integrand f x)
      (and expr (with-mr-switches (mr-apply-rule (mr-rule-of h) expr pre f x))))))

(defmfun |$%MR_RULE_PATTERN_TEXT| (&rest args)
  "%mr_rule_pattern_text(handle): the rule's ORIGINAL pattern string, exactly
as passed to %mr_defrule before mr-match:prepare compiled it — a test and
debugging entry (inert-trig substrate design 3.3, Task 8 fix round 1: the
bare-u_ tail-position gate reads it to classify a handle from the loaded
table, the same structural definition generator/generate_rules.py's
bare_int_clause and test/check_generated_rules.py's INT_BARE_U check
statically)."
  (unless (= (length args) 1)
    (merror (intl:gettext "%mr_rule_pattern_text: expected 1 arg, found ~A") (length args)))
  (mr-rule-pattern-text (mr-rule-of (first args))))

;;; ------------------------------------------------------------------
;;; Rewrite records (inert-trig substrate design 3.2)
;;;
;;; %mr_defrewrite(key, n, pattern, cond, repl) is %mr_defrule's sibling for
;;; Rubi's utility functions whose clauses are `Name[pattern] := rhs /; cond`
;;; -- every clause of UnifyInertTrigFunction (75), FixInertTrigFunction (61)
;;; and ReduceInertTrig (4) is of that shape: 140 in the generated tables,
;;; 137 conditioned, 3 registering `true` as their cond. The pattern's outermost
;;; head is the function name rather than Int, and there is no
;;; integrand/variable split, so there is no mr-accept and no pre-binding.
;;; Placed here (after with-mr-switches / mr-guarded / mr-call / mr-true-p /
;;; mr-binding-list are all defined above) rather than beside mr-rule-of,
;;; since mr-guarded and with-mr-switches are macros: SBCL macroexpands each
;;; top-level form as `load` reads it, so a use ahead of the macro's own
;;; defmacro would not expand as a macro call at all.

(defstruct (mr-rewrite (:constructor make-mr-rewrite (key n pattern cond repl)))
  key n pattern cond repl)

(defvar *mr-rewrites* (make-array 256 :adjustable t :fill-pointer 0)
  "Every rewrite record %mr_defrewrite registered, in load order.")

(defmfun |$%MR_DEFREWRITE| (&rest args)
  (unless (= (length args) 5)
    (merror (intl:gettext "%mr_defrewrite: expected 5 args, found ~A")
            (length args)))
  (destructuring-bind (key n pattern cond repl) args
    (let ((compiled (handler-case (mr-match:prepare (mr-match:read-tree pattern))
                      (error (e)
                        (merror (intl:gettext "%mr_defrewrite: ~A r~A: ~A") key n
                                (princ-to-string e))))))
      (vector-push-extend (make-mr-rewrite key n compiled cond repl) *mr-rewrites*)
      (fill-pointer *mr-rewrites*))))

(defun mr-rewrite-of (handle)
  (if (and (integerp handle) (<= 1 handle (fill-pointer *mr-rewrites*)))
      (aref *mr-rewrites* (1- handle))
      (merror (intl:gettext "%mr_rewrite: not a rewrite handle: ~M") handle)))

(defmfun |$%MR_REWRITE| (&rest args)
  "%mr_rewrite(head, table, u, x): walk TABLE (a Maxima list of
%mr_defrewrite handles) in order; the first record whose pattern binds
(head u x) and whose cond accepts answers with its repl's value. U
unchanged when none does -- Mathematica's own behaviour for a call with no
applicable definition, which is what the callers rely on.

%mr_rewrite(head, table, u) walks a ONE-argument function's table: the
pattern binds (head u), and the cond and repl get false for x (class 4,
2026-09-25: TrigSimplifyAux[u], whose clauses never read x)."
  (unless (member (length args) '(3 4))
    (merror (intl:gettext "%mr_rewrite: expected 3 or 4 args, found ~A") (length args)))
  (destructuring-bind (head table u &optional (x nil x-p)) args
    (unless ($listp table)
      (merror (intl:gettext "%mr_rewrite: the table is not a list: ~M") table))
    (let ((expr (if x-p
                    (list (mr-match:sym head)
                          (mr-tree:max->tree u)
                          (mr-tree:max->tree x))
                    (list (mr-match:sym head)
                          (mr-tree:max->tree u)))))
      (with-mr-switches
        (dolist (h (cdr table) u)
          (let* ((rw (mr-rewrite-of h))
                 (cond-fn (mr-rewrite-cond rw))
                 (accepted nil))
            (mr-guarded (setf accepted nil)
              (mr-match:match
               (mr-rewrite-pattern rw) expr
               :cond-hook (lambda (b)
                            (let ((mb (mr-binding-list b nil)))
                              (when (or (eq cond-fn t)
                                        (multiple-value-bind (v ok)
                                            (mr-call cond-fn mb x)
                                          (and ok (mr-true-p v))))
                                (setf accepted mb))))))
            (when accepted
              (multiple-value-bind (r ok) (mr-call (mr-rewrite-repl rw) accepted x)
                (when (and ok r)
                  (return r))))))))))

;;; ------------------------------------------------------------------
;;; MatchQ (spec 3.4): %mr_matchQ(u, "<pattern>", [<parts>], cond)

(defvar *mr-matchq-trees* (make-hash-table :test 'equal)
  "%mr_matchQ pattern text -> its tree, read once.")

(defvar *mr-matchq-compiled* (make-hash-table :test 'equal)
  "%mr_matchQ pattern text -> its prepared pattern, for part-free calls only
(a call with parts substitutes and prepares per call).")

(defun mr-substitute-parts (tree parts)
  "Replace each (MRArg k) in TREE with the k-th of PARTS (trees), then fold
bottom-up as Mathematica's evaluation of the pattern would (final review,
1.4.2 r17): (Power e 1) -> e, (Power e 0) -> 1; a literal 1 argument of Times
and 0 argument of Plus drop; a Plus/Times argument directly under the same
head is spliced in; a Times/Plus left with one argument is that argument (with
none, 1 / 0). Numeric products and sums are not folded ((Times 2 3) stays). An
(MRArg k) with k outside 1..(length PARTS) is an error."
  (let ((mrarg (mr-match:sym "MRArg"))
        (power (mr-match:sym "Power"))
        (plus (mr-match:sym "Plus"))
        (times (mr-match:sym "Times"))
        (nparts (length parts)))
    (labels ((walk (e)
               (cond ((atom e) e)
                     ((eq (car e) mrarg)
                      (let ((k (second e)))
                        (unless (and (integerp k) (<= 1 k nparts))
                          (error "(MRArg ~A) is out of range: ~A part~:P" k nparts))
                        (nth (1- k) parts)))
                     (t (fold (walk (car e)) (mapcar #'walk (cdr e))))))
             (fold (h args)
               (cond ((and (eq h power) (= (length args) 2) (eql (second args) 1))
                      (first args))
                     ((and (eq h power) (= (length args) 2) (eql (second args) 0))
                      1)
                     ((or (eq h plus) (eq h times))
                      (let* ((unit (if (eq h times) 1 0))
                             (kept (loop for a in args
                                         if (and (consp a) (eq (car a) h))
                                           append (cdr a)
                                         else if (not (eql a unit))
                                           collect a)))
                        (cond ((null kept) unit)
                              ((null (cdr kept)) (car kept))
                              (t (cons h kept)))))
                     (t (cons h args)))))
      (walk tree))))

(defun mr-matchq-pattern (text parts)
  "The prepared pattern of TEXT with PARTS (a Lisp list of Maxima values)
substituted and folded. A part-free pattern is prepared once and cached by its
text. A pattern the substitution or prepare rejects is a Maxima error naming
the pattern text."
  (let ((raw (or (gethash text *mr-matchq-trees*)
                 (setf (gethash text *mr-matchq-trees*) (mr-match:read-tree text))))
        (ptrees (mapcar #'mr-tree:max->tree parts)))
    (flet ((compile-pattern ()
             (handler-case (mr-match:prepare (mr-substitute-parts raw ptrees))
               (error (e)
                 (merror (intl:gettext "%mr_matchQ: ~A: ~A") text
                         (princ-to-string e))))))
      (if parts
          (compile-pattern)
          (or (gethash text *mr-matchq-compiled*)
              (setf (gethash text *mr-matchq-compiled*) (compile-pattern)))))))

(defun mr-matchq (u text parts cond)
  "The Maxima binding list [marker = value, ...] of the first complete binding
of the pattern TEXT (its (MRArg k) placeholders replaced by the values PARTS)
against U that COND accepts, or nil. COND is true or a function of the
binding list. MatchQ semantics: every complete binding is tried
(mr_cond_retry does not apply). A pattern prepare rejects, or an out-of-range
(MRArg k), is a Maxima error naming the pattern text (like %mr_defrule's
load-time rejection) — reading, substituting and preparing the pattern
(mr-matchq-pattern) run outside the fault guard, which covers only the match
call itself."
  (let* ((accepted nil)
         (compiled (mr-matchq-pattern text (cdr parts)))
         (utree (mr-tree:max->tree u)))
    (let ((mr-match:*flat-wide* (not (null $mr_flat_wide)))
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
    accepted))

(defun mr-matchq-args (name args)
  (unless (= (length args) 4)
    (merror (intl:gettext "~A: expected 4 args, found ~A") name (length args)))
  (unless (and (stringp (second args)) ($listp (third args)))
    (merror (intl:gettext "~A: expected (u, \"<pattern>\", [<parts>], cond)") name))
  args)

(defmfun |$%mr_matchQ| (&rest args)
  "%mr_matchQ(u, \"<pattern>\", [<parts>], cond): true iff some binding of the
pattern against u satisfies cond (true or lambda([%mr_mqb], ...))."
  (if (apply #'mr-matchq (mr-matchq-args "%mr_matchQ" args)) t nil))

(defmfun |$%mr_matchQ_bindings| (&rest args)
  "%mr_matchQ_bindings(u, \"<pattern>\", [<parts>], cond): the accepted
binding list [marker = value, ...], or false."
  (apply #'mr-matchq (mr-matchq-args "%mr_matchQ_bindings" args)))
