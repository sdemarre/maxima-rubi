;;;; probes/dispatch-index/01-profile.lisp -- ticket 21 step 1: where does a
;;;; dispatch spend its time?  (.scratch/class-ports/issues/21)
;;;;
;;;; Loaded AFTER the rules (the rules core, or maxima_rubi.mac + mr_load_all).
;;;; Redefines mr-accept / mr-apply-rule with the same behaviour plus counters,
;;;; and wraps %mr_dispatch_tree to count dispatches.  Nothing here changes a
;;;; result: the redefinitions are the committed bodies with timing added.
;;;;
;;;; Every rule attempt lands in exactly one category:
;;;;   :nobind   the pattern produced no complete binding
;;;;   :condfail >= 1 binding reached the condition, none accepted
;;;;   :decline  a binding accepted, the repl declined or misfired
;;;;   :fired    the rule answered
;;;; and is also scored by two STATIC oracles (computed outside the timed
;;;; region) that an index could use to skip it without matching:
;;;;   root   the integrand's root head cannot be the pattern's root head, with
;;;;          Optional collapse (a_.*x^m_. matches a bare x) accounted for
;;;;   heads  the pattern needs a literal non-flat head (sin, %mr_isin, log...)
;;;;          outside every Optional that the integrand does not contain
;;;; A skip that the oracle calls safe but that did not end in :nobind is a
;;;; VIOLATION and is counted: the oracle is then unsound.

(defvar *pf* (make-hash-table :test 'equal))
(defvar *pf-dispatches* 0)
(defvar *pf-depth* 0)
(defvar *pf-max-depth* 0)
(defvar *pf-bindings* 0)
(defvar *pf-cond-time* 0)
(defvar *pf-conv-time* 0)
(defvar *pf-bool-time* 0)
(defvar *pf-bool-calls* 0)
(defvar *pf-heads-cache* (cons nil nil))

(defun pf-add (key n) (incf (gethash key *pf* 0) n))
(defun pf-now () (get-internal-run-time))

(defun pf-reset ()
  (clrhash *pf*)
  (setf *pf-dispatches* 0 *pf-max-depth* 0 *pf-conv-time* 0 *pf-bool-time* 0 *pf-bool-calls* 0))

;;; ---------------- static oracles

(defparameter +pf-int+ (mr-match:sym "Int"))
(defparameter +pf-plus+ (mr-match:sym "Plus"))
(defparameter +pf-times+ (mr-match:sym "Times"))
(defparameter +pf-power+ (mr-match:sym "Power"))
(defparameter +pf-pattern+ (mr-match:sym "Pattern"))
(defparameter +pf-blank+ (mr-match:sym "Blank"))
(defparameter +pf-optional+ (mr-match:sym "Optional"))
(defparameter +pf-condition+ (mr-match:sym "Condition"))
(defparameter +pf-ptest+ (mr-match:sym "PatternTest"))
(defparameter +pf-structural+
  (list +pf-pattern+ +pf-blank+ (mr-match:sym "BlankSequence") (mr-match:sym "BlankNullSequence")
        +pf-optional+ +pf-condition+ +pf-ptest+))

(defun pf-integrand-pattern (tree)
  "The pattern of Int's first argument, or :unknown."
  (loop while (and (consp tree) (member (car tree) (list +pf-condition+ +pf-ptest+)))
        do (setf tree (second tree)))
  (if (and (consp tree) (eq (car tree) +pf-int+)) (second tree) :unknown))

(defun pf-optional-p (p)
  (and (consp p) (eq (car p) +pf-optional+)))

(defun pf-root-heads (p)
  "The set of root heads P can match, or :any."
  (cond ((atom p) (list (mr-match:head-of p)))
        ((eq (car p) +pf-pattern+) (pf-root-heads (third p)))
        ((eq (car p) +pf-blank+) (if (cdr p) (list (second p)) :any))
        ((member (car p) (list +pf-condition+ +pf-ptest+)) (pf-root-heads (second p)))
        ((member (car p) +pf-structural+) :any)
        ((not (symbolp (car p))) :any)            ; compound head, e.g. Derivative[n][f]
        ((member (car p) (list +pf-plus+ +pf-times+))
         ;; collapses to one argument when every other argument is Optional
         (let ((hard (remove-if #'pf-optional-p (cdr p))))
           (cond ((null hard) :any)
                 ((null (cdr hard))
                  (let ((inner (pf-root-heads (car hard))))
                    (if (eq inner :any) :any (adjoin (car p) inner))))
                 (t (list (car p))))))
        ((eq (car p) +pf-power+)
         (if (pf-optional-p (third p))
             (let ((inner (pf-root-heads (second p))))
               (if (eq inner :any) :any (adjoin +pf-power+ inner)))
             (list +pf-power+)))
        (t (list (car p)))))

(defun pf-required-heads (p)
  "Literal non-flat heads P needs outside Optionals (the integrand must
contain each one somewhere)."
  (let ((acc nil))
    (labels ((walk (p)
               (when (consp p)
                 (cond ((eq (car p) +pf-optional+) nil)
                       ((member (car p) (list +pf-condition+ +pf-ptest+)) (walk (second p)))
                       ((eq (car p) +pf-pattern+) (walk (third p)))
                       ((member (car p) +pf-structural+) nil)
                       (t (when (and (symbolp (car p))
                                     (not (member (car p) (list +pf-plus+ +pf-times+ +pf-power+))))
                            (pushnew (car p) acc))
                          (unless (symbolp (car p)) (walk (car p)))
                          (mapc #'walk (cdr p)))))))
      (walk p))
    acc))

(defvar *pf-rule-static* (make-hash-table :test 'eq))

(defun pf-rule-static (rule)
  (or (gethash rule *pf-rule-static*)
      (setf (gethash rule *pf-rule-static*)
            (let ((ip (pf-integrand-pattern (mr-match:compiled-pattern-tree (mr-rule-pattern rule)))))
              (if (eq ip :unknown)
                  (cons :any nil)
                  (cons (pf-root-heads ip) (pf-required-heads ip)))))))

(defun pf-expr-heads (e)
  (let ((acc nil))
    (labels ((walk (e) (when (consp e)
                         (pushnew (car e) acc)
                         (unless (symbolp (car e)) (walk (car e)))
                         (mapc #'walk (cdr e)))))
      (walk e))
    acc))

(defun pf-oracles (rule expr)
  "-> (values root-skip heads-skip) for RULE on the converted EXPR (Int f x)."
  (let* ((f (second expr))
         (st (pf-rule-static rule))
         (heads (if (eq (car *pf-heads-cache*) f)
                    (cdr *pf-heads-cache*)
                    (cdr (setf *pf-heads-cache* (cons f (pf-expr-heads f)))))))
    (values (and (listp (car st)) (not (member (mr-match:head-of f) (car st))))
            (some (lambda (h) (not (member h heads))) (cdr st)))))

;;; ---------------- instrumented dispatcher pieces (bodies = the committed ones)

(defun mr-accept (rule expr pre x check-cond)
  (let ((accepted nil)
        (xname (car (first pre))))
    (mr-guarded
        (progn (mr-verbose "rubi: rule ~A r~A matcher fault: ~A~%"
                           (mr-rule-key rule) (mr-rule-n rule) (princ-to-string condition))
               (setf accepted nil))
      (mr-match:match
       (mr-rule-pattern rule) expr :bindings pre
       :cond-hook (lambda (b)
                    (incf *pf-bindings*)
                    (let* ((t0 (pf-now))
                           (r (errcatch
                               (let ((mm (let ((c0 (pf-now)))
                                           (prog1 (mr-binding-list b xname)
                                             (incf *pf-conv-time* (- (pf-now) c0))))))
                                 (and (not (let ((c0 (pf-now)))
                                             (incf *pf-bool-calls*)
                                             (prog1 (mr-contains-boolean-p mm)
                                               (incf *pf-bool-time* (- (pf-now) c0)))))
                                      (or (not check-cond)
                                          (multiple-value-bind (v ok) (mr-call (mr-rule-cond rule) mm x)
                                            (and ok (mr-true-p v)))
                                          nil)
                                      mm)))))
                      (incf *pf-cond-time* (- (pf-now) t0))
                      (when (car r)
                        (setf accepted (car r))
                        t)))))
    accepted))

(defun pf-class (rule)
  (let* ((k (princ-to-string (mr-rule-key rule)))
         (u (position #\_ k)))
    (if u (subseq k 0 u) k)))

(defun mr-apply-rule (rule expr pre f x)
  (multiple-value-bind (root-skip heads-skip) (pf-oracles rule expr)
    (let* ((*pf-bindings* 0)
           (*pf-cond-time* 0)
           (t0 (pf-now))
           (mm (let ((*pf-depth* *pf-depth*)) (mr-accept rule expr pre x t)))
           (t1 (pf-now))
           (bindings *pf-bindings*)
           (cond-time *pf-cond-time*)
           (result
             (when mm
               (multiple-value-bind (r ok) (mr-call (mr-rule-repl rule) mm x)
                 (cond ((not ok) nil)
                       ((null r) nil)
                       ((and $%mr_boolcheck (mr-contains-boolean-p r)) nil)
                       ((and $mr_inert_leak_misfire (not (mr-class4-rule-p rule))
                             (mr-carries-inert-p r) (mr-carries-inert-p f))
                        nil)
                       (t r)))))
           (t2 (pf-now))
           (cat (cond ((zerop bindings) :nobind)
                      ((null mm) :condfail)
                      ((null result) :decline)
                      (t :fired)))
           ;; time spent inside the pattern matcher proper, excluding the
           ;; condition (which may itself recurse into rubi)
           (match-time (- (- t1 t0) cond-time)))
      (pf-add (list :n cat) 1)
      (pf-add (list :match-t cat) match-time)
      (pf-add (list :cond-t cat) cond-time)
      (pf-add (list :repl-t cat) (- t2 t1))
      (pf-add (list :bindings cat) bindings)
      (pf-add (list :class-n (pf-class rule) cat) 1)
      (pf-add (list :class-match-t (pf-class rule)) match-time)
      (pf-add (list :class-cond-t (pf-class rule)) cond-time)
      (unless (eq cat :fired)
        (pf-add (list :rule-cond-t (mr-rule-key rule) (mr-rule-n rule)) cond-time)
        (pf-add (list :rule-cond-n (mr-rule-key rule) (mr-rule-n rule)) 1)
        (pf-add (list :rule-cond-b (mr-rule-key rule) (mr-rule-n rule)) bindings))
      (when root-skip
        (pf-add (list :root-skip cat) 1)
        (pf-add (list :root-skip-t cat) match-time))
      (when (or root-skip heads-skip)
        (pf-add (list :any-skip cat) 1)
        (pf-add (list :any-skip-t cat) match-time))
      (when heads-skip
        (pf-add (list :heads-skip cat) 1)
        (pf-add (list :heads-skip-t cat) match-time))
      (when (and (or root-skip heads-skip) (not (eq cat :nobind)))
        (pf-add (list :violation (if root-skip :root :heads) (mr-rule-key rule) (mr-rule-n rule)) 1))
      result)))

(let ((orig (symbol-function '|$%MR_DISPATCH_TREE|)))
  (setf (symbol-function '|$%MR_DISPATCH_TREE|)
        (lambda (&rest args)
          (incf *pf-dispatches*)
          (let ((*pf-depth* (1+ *pf-depth*)))
            (setf *pf-max-depth* (max *pf-max-depth* *pf-depth*))
            (apply orig args)))))

;;; ---------------- report

(defun pf-ms (us) (/ (round us 1000) 1.0))

(defmfun $pf_reset () (pf-reset) '$done)

(defmfun $pf_report (label)
  (let ((cats '(:nobind :condfail :decline :fired))
        (total-n 0) (total-match 0) (total-cond 0))
    (dolist (c cats)
      (incf total-n (gethash (list :n c) *pf* 0))
      (incf total-match (gethash (list :match-t c) *pf* 0)))
    ;; condition time is nested: a cond that calls rubi contains inner
    ;; attempts' time, so only the outermost-level sum is meaningful as a
    ;; share; report it per category, flagged as inclusive
    (setf total-cond (loop for c in cats sum (gethash (list :cond-t c) *pf* 0)))
    (format t "~&PROFILE ~A~%" label)
    (format t "  dispatches ~D  max-depth ~D  attempts ~D  attempts/dispatch ~,1F~%"
            *pf-dispatches* *pf-max-depth* total-n
            (if (plusp *pf-dispatches*) (/ total-n *pf-dispatches*) 0))
    (format t "  of the cond time, binding conversion (tree->maxima, exclusive) ~,1F ms~%" (pf-ms *pf-conv-time*))
    (format t "  of the cond time, the boolean-leak check on the binding list (%mr_containsBoolean) ~,1F ms over ~D calls~%"
            (pf-ms *pf-bool-time*) *pf-bool-calls*)
    (format t "  matcher time (exclusive of cond) ~,1F ms; cond time (inclusive, nested) ~,1F ms~%"
            (pf-ms total-match) (pf-ms total-cond))
    (dolist (c cats)
      (format t "  ~9A n=~8D  match=~9,1Fms  cond=~9,1Fms  repl=~9,1Fms  bindings=~D~%"
              c (gethash (list :n c) *pf* 0)
              (pf-ms (gethash (list :match-t c) *pf* 0))
              (pf-ms (gethash (list :cond-t c) *pf* 0))
              (pf-ms (gethash (list :repl-t c) *pf* 0))
              (gethash (list :bindings c) *pf* 0)))
    (format t "  oracle skips (attempts, matcher ms saved):~%")
    (dolist (o '(:root-skip :heads-skip :any-skip))
      (format t "    ~11A nobind=~8D (~,1Fms)  other=~D~%"
              o (gethash (list o :nobind) *pf* 0)
              (pf-ms (gethash (list (intern (format nil "~A-T" o) :keyword) :nobind) *pf* 0))
              (loop for c in (cdr cats) sum (gethash (list o c) *pf* 0))))
    (format t "  per class: attempts (nobind/condfail/decline/fired)  matcher ms  cond ms~%")
    (let ((classes nil))
      (maphash (lambda (k v) (declare (ignore v))
                 (when (eq (car k) :class-match-t) (pushnew (second k) classes :test #'equal)))
               *pf*)
      (dolist (cl (sort classes #'string<))
        (format t "    class ~A: ~D/~D/~D/~D  ~,1F  ~,1F~%" cl
                (gethash (list :class-n cl :nobind) *pf* 0)
                (gethash (list :class-n cl :condfail) *pf* 0)
                (gethash (list :class-n cl :decline) *pf* 0)
                (gethash (list :class-n cl :fired) *pf* 0)
                (pf-ms (gethash (list :class-match-t cl) *pf* 0))
                (pf-ms (gethash (list :class-cond-t cl) *pf* 0)))))
    (let ((v nil))
      (maphash (lambda (k n) (when (eq (car k) :rule-cond-t) (push (cons (cdr k) n) v))) *pf*)
      (setf v (sort v #'> :key #'cdr))
      (format t "  top rules by cond time in non-firing attempts (rule: ms attempts bindings):~%")
      (dolist (x (subseq v 0 (min 25 (length v))))
        (format t "    ~A r~A: ~,1F ~D ~D~%" (first (car x)) (second (car x)) (pf-ms (cdr x))
                (gethash (cons :rule-cond-n (car x)) *pf* 0)
                (gethash (cons :rule-cond-b (car x)) *pf* 0))))
    (let ((v nil))
      (maphash (lambda (k n) (when (eq (car k) :violation) (push (cons (cdr k) n) v))) *pf*)
      (format t "  oracle violations: ~D~%" (length v))
      (dolist (x (subseq v 0 (min 20 (length v))))
        (format t "    ~S x~D~%" (car x) (cdr x))))
    '$done))

(defmfun $pf_report_after (seconds label)
  "For an entry that may not finish: print the report and exit after SECONDS
of wall clock (the counters then cover the run so far)."
  (sb-ext:schedule-timer
   (sb-ext:make-timer (lambda ()
                        ($pf_report (format nil "~A (cut at ~As, partial)" label seconds))
                        (finish-output)
                        (sb-ext:exit :code 0 :abort t)))
   seconds)
  '$done)
