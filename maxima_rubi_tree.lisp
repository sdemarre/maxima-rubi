;;;; maxima_rubi_tree.lisp -- MR-TREE: simplified Maxima internal form <-> MR-MATCH trees.
;;;;
;;;; Design: docs/superpowers/specs/2026-09-12-matcher-substrate-design.md
;;;; section 3.3.  max->tree reads a SIMPLIFIED Maxima expression and does no
;;;; simplification of its own beyond two structural steps: numeric %i terms are
;;;; folded into complex atoms (G-3) and Plus/Times arguments are sorted
;;;; (mr-match:canonicalize).  tree->max builds unsimplified internal form and
;;;; simplifies it once.  The head table is derived at load time from Maxima's
;;;; own operators (a call is parsed and its operator read), so a Maxima rename
;;;; shows up as a load-time error, not a silent miss.
;;;;
;;;; Load after maxima_rubi_match.lisp, inside Maxima.

(defpackage :mr-tree
  (:use :cl :mr-match)
  (:export #:max->tree #:tree->max #:maxima-form #:maxima-name #:*unknown-head-hook* #:head-table))

(in-package :mr-tree)

;;; Mathematica head, arity, Maxima call name -- the probe-02 table
;;; (probes/matcher/02-roundtrip.py MAXIMA_FUN), every name measured there.
(defparameter +functions+
  '(("Log" 1 "log") ("Sin" 1 "sin") ("Cos" 1 "cos") ("Tan" 1 "tan") ("Cot" 1 "cot")
    ("Sec" 1 "sec") ("Csc" 1 "csc") ("Sinh" 1 "sinh") ("Cosh" 1 "cosh") ("Tanh" 1 "tanh")
    ("Coth" 1 "coth") ("Sech" 1 "sech") ("Csch" 1 "csch") ("ArcSin" 1 "asin")
    ("ArcCos" 1 "acos") ("ArcTan" 1 "atan") ("ArcCot" 1 "acot") ("ArcSec" 1 "asec")
    ("ArcCsc" 1 "acsc") ("ArcSinh" 1 "asinh") ("ArcCosh" 1 "acosh") ("ArcTanh" 1 "atanh")
    ("ArcCoth" 1 "acoth") ("ArcSech" 1 "asech") ("ArcCsch" 1 "acsch") ("Erf" 1 "erf")
    ("Erfc" 1 "erfc") ("Erfi" 1 "erfi") ("FresnelS" 1 "fresnel_s") ("FresnelC" 1 "fresnel_c")
    ("ExpIntegralEi" 1 "expintegral_ei") ("ExpIntegralE" 2 "expintegral_e")
    ("SinIntegral" 1 "expintegral_si") ("CosIntegral" 1 "expintegral_ci")
    ("SinhIntegral" 1 "expintegral_shi") ("CoshIntegral" 1 "expintegral_chi")
    ("LogIntegral" 1 "expintegral_li") ("Gamma" 1 "gamma") ("Gamma" 2 "gamma_incomplete")
    ("LogGamma" 1 "log_gamma") ("ProductLog" 1 "lambert_w") ("BesselJ" 2 "bessel_j")
    ("Zeta" 1 "zeta") ("Factorial" 1 "factorial") ("Abs" 1 "abs")
    ;; Rubi's six INERT trig heads (inert-trig substrate design 3.1). The
    ;; Maxima side is an undefined operator, so the simplifier leaves it alone
    ;; (probes/maxima/probe-inert-operator-inertness, 44/0); the tree side is
    ;; the lowercase head section 4's rules pattern on. sin and Sin stay
    ;; distinct because read-tree's readtable case is :preserve.
    ("sin" 1 "%mr_isin") ("cos" 1 "%mr_icos") ("tan" 1 "%mr_itan")
    ("cot" 1 "%mr_icot") ("sec" 1 "%mr_isec") ("csc" 1 "%mr_icsc")))

;;; Maxima's subscripted functions li[n](x), psi[n](x): mqapply of an array op.
(defparameter +subscripted+ '(("PolyLog" maxima::$li) ("PolyGamma" maxima::$psi)))

(defvar *unknown-head-hook* nil
  "Nil, or a function (maxima-operator-symbol) -> head symbol or nil, tried
before the default MX_<operator> head for a Maxima operator the table lacks.")

(defvar *op->head* (make-hash-table :test 'eq))
(defvar *head->op* (make-hash-table :test 'equal))   ; (head . arity) -> operator

(defun maxima-form (string)
  "Parse and evaluate a Maxima expression string (simplified internal form)."
  (maxima::meval (maxima::meval (list (list 'maxima::$parse_string) string))))

;;; Maxima operators read as a head but never written back (tree->max uses the
;;; subscripted form): polylog(n, x) stays $polylog for a symbolic n.
(defparameter +read-only-functions+ '(("PolyLog" 2 "polylog")))

(defun function-operator (name arity)
  (let* ((call (format nil "~a(~{q~a~^,~})" name (loop for i below arity collect i)))
         (form (maxima-form call)))
    (unless (and (consp form) (consp (car form)))
      (error "mr-tree: ~a did not parse to a function call: ~s" call form))
    (caar form)))

(defun build-head-table ()
  (clrhash *op->head*)
  (clrhash *head->op*)
  (dolist (entry +functions+)
    (destructuring-bind (head arity name) entry
      (let ((op (function-operator name arity)))
        (setf (gethash op *op->head*) (sym head)
              (gethash (cons (sym head) arity) *head->op*) op))))
  (dolist (entry +read-only-functions+)
    (destructuring-bind (head arity name) entry
      (setf (gethash (function-operator name arity) *op->head*) (sym head)))))

(build-head-table)

(defun head-table ()
  "The load-time table as a list of (head arity maxima-operator)."
  (loop for (head . arity) being the hash-keys of *head->op* using (hash-value op)
        collect (list head arity op)))

;;; ------------------------------------------------------------------
;;; names

(defun invert-case (s)
  (cond ((string= s (string-upcase s)) (string-downcase s))
        ((string= s (string-downcase s)) (string-upcase s))
        (t s)))

(defun maxima-name (sym)
  ;; $x -> "x", |$a| -> "A", %sin -> "sin"
  (let ((s (symbol-name sym)))
    (invert-case (if (and (> (length s) 1) (find (char s 0) "$%")) (subseq s 1) s))))

(defparameter +reserved+ '("E" "Pi" "I"))

(defun symbol->tree (sym)
  (case sym
    (maxima::$%e (sym "E"))
    (maxima::$%pi (sym "Pi"))
    (maxima::$%i #C(0 1))
    (t (let ((n (maxima-name sym)))
         (sym (if (member n +reserved+ :test #'string=) (concatenate 'string "MXS_" n) n))))))

;;; Tree heads a user function must never be read as: MR-MATCH's structural
;;; heads and the names the pattern language reserves.
(defparameter +structural-heads+
  '("Plus" "Times" "Power" "Int" "List" "Pattern" "Blank" "BlankSequence"
    "BlankNullSequence" "Optional" "Condition" "PatternTest" "Alternatives"
    "Complex" "Rational" "Integer" "Real" "Symbol" "String" "True" "False"
    "Derivative" "MRArg"))

(defun user-function-head (op arity)
  "A user function f(...) (a $-prefixed operator the table lacks) reads as the
head named like the function itself, (f ...), the SAME symbol the bare atom f
converts to -- Rubi's 9.1 patterns bind one capture both as a value
(Derivative[1][f_]) and as a head (f_[x_]), so the two must agree (class-8
port, 2026-09-25). Nil (keep the opaque MX_ head) for a %-noun or an
unprefixed internal operator, whose name does not round-trip, and for a name
that is a structural head or a table head of the same arity, which would be
written back as something else."
  (let ((name (symbol-name op)))
    (when (and (> (length name) 1) (char= (char name 0) #\$))
      (let* ((tn (maxima-name op)) (h (sym tn)))
        (unless (or (member tn +structural-heads+ :test #'string=)
                    (member tn +reserved+ :test #'string=)
                    (gethash (cons h arity) *head->op*))
          h)))))

(defun unknown-head (op &optional arity)
  (or (and *unknown-head-hook* (funcall *unknown-head-hook* op))
      (and arity (user-function-head op arity))
      (let ((h (sym (concatenate 'string "MX_" (symbol-name op)))))
        (setf (get h 'maxima-op) op)
        h)))

(defun derivative-form-p (e)
  "Maxima's formal derivative noun 'diff(f(u), u, n): exactly three
arguments, the first a one-argument call whose argument is the
differentiation variable (probes/answer-side/04-class8-answer-side-identities
N1/N2/N12)."
  (let ((args (cdr e)))
    (and (= (length args) 3)
         (let ((call (first args)))
           (and (consp call) (consp (car call))
                (not (eq (caar call) 'maxima::mqapply))
                (= (length (cdr call)) 1)
                (maxima::alike1 (second call) (second args)))))))

;;; ------------------------------------------------------------------
;;; Maxima -> tree

(defun numeric-atom-p (x) (numberp x))

(defun fold-complex (head args)
  ;; G-3: when a complex atom is present, combine it with the numeric atoms
  (if (notany #'complexp args)
      args
      (let ((nums (remove-if-not #'numeric-atom-p args))
            (rest (remove-if #'numeric-atom-p args)))
        (let ((v (if (eq head (sym "Plus")) (reduce #'+ nums) (reduce #'* nums))))
          (if (or (and (eq head (sym "Plus")) (eql v 0)) (and (eq head (sym "Times")) (eql v 1)))
              rest
              (cons v rest))))))

(defun flat-node (head args)
  (let ((args (fold-complex head args)))
    (cond ((null args) (if (eq head (sym "Plus")) 0 1))
          ((null (cdr args)) (car args))
          (t (cons head args)))))

(defun convert (e)
  (cond ((integerp e) e)
        ((floatp e) (coerce e 'double-float))
        ;; Maxima's booleans are the Lisp symbols T and NIL
        ((eq e t) (sym "True"))
        ((null e) (sym "False"))
        ((symbolp e) (symbol->tree e))
        ((stringp e) e)
        ((and (consp e) (consp (car e)))
         (let ((op (caar e)) (args (cdr e)))
           (cond ((eq op 'maxima::rat) (/ (first args) (second args)))
                 ;; CRE (rat()) input: convert its general representation,
                 ;; re-simplified -- ratdisrep's result is not in simplified
                 ;; form (1/(2*y) comes back as (2*y)^-1), which would give a
                 ;; non-canonical tree (plan-2 pre-validation, 2026-09-13)
                 ((eq op 'maxima::mrat) (convert (maxima::resimplify (maxima::$ratdisrep e))))
                 ((eq op 'maxima::bigfloat) (coerce (maxima::$float e) 'double-float))
                 ((eq op 'maxima::mplus) (flat-node (sym "Plus") (mapcar #'convert args)))
                 ((eq op 'maxima::mtimes) (flat-node (sym "Times") (mapcar #'convert args)))
                 ((eq op 'maxima::mexpt) (list (sym "Power") (convert (first args)) (convert (second args))))
                 ;; Rubi's Derivative[n][f][u] is the curried tree
                 ;; (((Derivative n) f) u); Maxima's own spelling of it is
                 ;; the noun 'diff(f(u), u, n) (the class-8 design,
                 ;; .scratch/class-ports/issues/01).
                 ((and (eq op 'maxima::%derivative) (derivative-form-p e))
                  (let ((call (convert (first args))))
                    (if (consp call)
                        (list (list (list (sym "Derivative") (convert (third args)))
                                    (car call))
                              (convert (second args)))
                        (cons (unknown-head op) (mapcar #'convert args)))))
                 ((eq op 'maxima::mqapply)
                  (let* ((sub (first args))
                         (entry (find (caar sub) +subscripted+ :key #'second)))
                    (cons (if entry (sym (first entry)) (unknown-head (caar sub)))
                          (mapcar #'convert (append (cdr sub) (rest args))))))
                 (t (cons (or (gethash op *op->head*) (unknown-head op (length args)))
                          (mapcar #'convert args))))))
        (t (error "mr-tree: cannot convert ~s" e))))

(defun max->tree (e)
  "Simplified Maxima internal form -> canonical MR-MATCH tree."
  (canonicalize (convert e)))

;;; ------------------------------------------------------------------
;;; tree -> Maxima

(defun tree-symbol->maxima (s)
  (let ((n (symbol-name s)))
    (cond ((string= n "E") 'maxima::$%e)
          ((string= n "Pi") 'maxima::$%pi)
          ((string= n "I") 'maxima::$%i)
          ((string= n "True") t)
          ((string= n "False") nil)
          (t (intern (concatenate 'string "$" (invert-case
                                               (if (and (> (length n) 4) (string= "MXS_" n :end2 4))
                                                   (subseq n 4) n)))
                     :maxima)))))

(defun head-operator (h arity)
  "The Maxima operator a tree head symbol H of ARITY writes back as."
  (or (gethash (cons h arity) *head->op*)
      (get h 'maxima-op)
      (tree-symbol->maxima h)))

(defun derivative-head-p (h)
  "The curried head ((Derivative n) f) of Derivative[n][f][u]."
  (and (consp h) (consp (car h)) (eq (caar h) (sym "Derivative"))
       (= (length (car h)) 2) (= (length h) 2) (symbolp (second h))))

(defun unconvert (e)
  (cond ((integerp e) e)
        ((typep e 'ratio) (list '(maxima::rat) (numerator e) (denominator e)))
        ((floatp e) e)
        ((complexp e) (list '(maxima::mplus) (unconvert (realpart e))
                            (list '(maxima::mtimes) (unconvert (imagpart e)) 'maxima::$%i)))
        ((stringp e) e)
        ((symbolp e) (tree-symbol->maxima e))
        (t (let* ((h (car e)) (args (mapcar #'unconvert (cdr e)))
                  (sub (and (symbolp h) (assoc (symbol-name h) +subscripted+ :test #'string=))))
             (cond ((and (derivative-head-p h) (= (length args) 1))
                    ;; (((Derivative n) f) u) -> 'diff(f(u), u, n); order 0
                    ;; is f(u) itself, as Mathematica's Derivative[0][f] is f
                    (let ((n (unconvert (second (car h))))
                          (call (list (list (head-operator (second h) 1)) (first args))))
                      (if (eql n 0)
                          call
                          (list '(maxima::%derivative) call (first args) n))))
                   ((eq h (sym "Plus")) (cons '(maxima::mplus) args))
                   ((eq h (sym "Times")) (cons '(maxima::mtimes) args))
                   ((eq h (sym "Power")) (cons '(maxima::mexpt) args))
                   (sub (list* '(maxima::mqapply) (list (list (second sub) 'maxima::array) (first args))
                               (rest args)))
                   ((and (symbolp h) (gethash (cons h (length args)) *head->op*))
                    (cons (list (gethash (cons h (length args)) *head->op*)) args))
                   ((and (symbolp h) (get h 'maxima-op)) (cons (list (get h 'maxima-op)) args))
                   ((symbolp h) (cons (list (tree-symbol->maxima h)) args))
                   (t (error "mr-tree: no Maxima form for head ~a" (tree-string h))))))))

(defun tree->max (tree)
  "MR-MATCH tree -> simplified Maxima internal form (simplified once)."
  (maxima::simplifya (unconvert tree) nil))
