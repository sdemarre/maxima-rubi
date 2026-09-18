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

;;; The two RUN switches (exact seen test design
;;; docs/superpowers/specs/2026-09-15-matcher-seen-test-intpart-design.md
;;; 3.3). Unlike the three migration switches above these are not
;;; hard-wired by p6_hardwire.py: they stay run parameters.

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

(defstruct (mr-rule (:constructor make-mr-rule (key n pattern cond repl giveup)))
  key n pattern cond repl giveup)

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
      (vector-push-extend (make-mr-rule key n compiled cond repl
                                        (mr-giveup-repl-p repl))
                          *mr-rules*)
      (fill-pointer *mr-rules*))))

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
              (let ((deferred nil))
                (or (dolist (h (cdr table) nil)
                      (let ((rule (mr-rule-of h)))
                        (if (mr-rule-giveup rule)
                            (push rule deferred)
                            (let ((r (mr-apply-rule rule expr pre f x)))
                              (when r (return r))))))
                    (dolist (rule (nreverse deferred) nil)
                      (let ((r (mr-apply-rule rule expr pre f x)))
                        (when r (return r))))))))))))

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
