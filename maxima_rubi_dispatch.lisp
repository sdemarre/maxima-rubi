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

(defstruct (mr-rule (:constructor make-mr-rule (key n pattern cond repl)))
  key n pattern cond repl)

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
      (vector-push-extend (make-mr-rule key n compiled cond repl) *mr-rules*)
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
                                           (and ok (mr-true-p v))))
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
               (mr-verbose "rubi: rule ~A r~A misfire (repl error) on ~M~%" key n f) nil)
              ((null r)
               (mr-verbose "rubi: rule ~A r~A declined on ~M~%" key n f) nil)
              ((and $%mr_boolcheck (mr-contains-boolean-p r))
               (mr-verbose "rubi: rule ~A r~A misfire (boolean leaked) on ~M~%" key n f) nil)
              (t
               (mr-verbose "rubi: rule ~A r~A fired on ~M with ~M~%" key n f mm) r))))))

(defmacro with-mr-switches (&body body)
  `(let ((mr-match:*flat-wide* (not (null $mr_flat_wide)))
         (mr-match:*cond-retry* (not (null $mr_cond_retry))))
     ,@body))

(defmfun |$%MR_DISPATCH_TREE| (&rest args)
  "%mr_dispatch_tree(f, x, table, depth): walk the rule handles of TABLE in
order; the first rule whose pattern binds, whose cond accepts and whose repl
answers wins. false when no rule answers."
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
          (dolist (h (cdr table) nil)
            (let ((r (mr-apply-rule (mr-rule-of h) expr pre f x)))
              (when r (return r)))))))))

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

(defun mr-substitute-parts (tree parts)
  "Replace each (MRArg k) in TREE with the k-th of PARTS (trees); a
substituted Plus/Times directly under the same head is spliced in, as
Mathematica's evaluation of the pattern would flatten it."
  (let ((mrarg (mr-match:sym "MRArg"))
        (flat (list (mr-match:sym "Plus") (mr-match:sym "Times"))))
    (labels ((walk (e)
               (cond ((atom e) e)
                     ((eq (car e) mrarg) (nth (1- (second e)) parts))
                     (t (let ((h (walk (car e)))
                              (args (mapcar #'walk (cdr e))))
                          (cons h (if (member h flat)
                                      (loop for a in args
                                            if (and (consp a) (eq (car a) h))
                                              append (cdr a)
                                            else collect a)
                                      args)))))))
      (walk tree))))

(defun mr-matchq (u text parts cond)
  "The Maxima binding list [marker = value, ...] of the first complete binding
of the pattern TEXT (its (MRArg k) placeholders replaced by the values PARTS)
against U that COND accepts, or nil. COND is true or a function of the
binding list. MatchQ semantics: every complete binding is tried
(mr_cond_retry does not apply). A pattern prepare rejects is a Maxima error
naming the pattern text (like %mr_defrule's load-time rejection) — reading,
substituting and preparing the pattern run outside the fault guard, which
covers only the match call itself."
  (let* ((accepted nil)
         (raw (or (gethash text *mr-matchq-trees*)
                  (setf (gethash text *mr-matchq-trees*) (mr-match:read-tree text))))
         (substituted (if (cdr parts)
                          (mr-substitute-parts raw (mapcar #'mr-tree:max->tree (cdr parts)))
                          raw))
         (compiled (handler-case (mr-match:prepare substituted)
                     (error (e)
                       (merror (intl:gettext "%mr_matchQ: ~A: ~A") text
                               (princ-to-string e)))))
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
