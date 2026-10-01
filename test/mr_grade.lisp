;;; test/mr_grade.lisp -- leaf size and the A/B/C/F grade of an antiderivative
;;; (user request 2026-09-30). The full story -- the reference's definitions,
;;; the choices made here, how well the leaf size reproduces Mathematica's, how
;;; to read the grades -- is docs/grading-and-leaf-size.md. Graded as the independent CAS integration tests of
;;; Nasser M. Abbasi grade them (12000.org, "Computer algebra independent
;;; integration tests", summer 2022 edition, section 4.2: the grading
;;; functions). Their grade is Albert Rich's GradeAntiderivative, written for
;;; Mathematica and ported by Abbasi to Maple, SymPy and SageMath:
;;;
;;;   ExpnType(result) <= ExpnType(optimal):
;;;       result has the imaginary unit, optimal does not   -> C
;;;       LeafCount(result) <= 2 LeafCount(optimal)         -> A
;;;       otherwise                                         -> B
;;;   ExpnType(result) > ExpnType(optimal):
;;;       result holds an unevaluated integral               -> F
;;;       otherwise                                          -> C
;;;
;;; mr_leaf_count(e) is Mathematica's LeafCount read off Maxima's simplified
;;; internal form, which has Mathematica's shape for everything that matters
;;; here: a - b is a + (-1)*b, a/b is a*b^(-1), sqrt(x) is x^(1/2), %e^x is
;;; a power of the atom %e. Every atom counts 1 and every compound 1 (its
;;; head) plus its parts, except where Mathematica's own representation
;;; differs:
;;;   - a rational number is Rational[n, d]: 3;
;;;   - a complex number is Complex[re, im]: 1 + LeafCount(re) + LeafCount(im),
;;;     so %i is 3, and the numeric terms of a sum and the numeric factors of
;;;     a product that carry %i are folded into ONE such number, as
;;;     Mathematica's evaluator does (2*%i*x is Times[Complex[0, 2], x]: 5);
;;;   - a subscripted function is one head with its subscripts as leading
;;;     arguments (li[2](z) is PolyLog[2, z]: 3; psi[n](x) is PolyGamma[n, x]);
;;;   - 2F1 and 1F1 take their parameters flat (hypergeometric([a,b],[c],z)
;;;     is Hypergeometric2F1[a, b, c, z]: 5); other pFq keep their lists, as
;;;     HypergeometricPFQ does.
;;; Measured against the report's own optimal leaf sizes (Mathematica's
;;; LeafCount of the same antiderivatives): probes/leaf-size/02-leaf-count-vs-reference.
;;;
;;; mr_expn_type(e) is ExpnType: 1 rational, 2 algebraic, 3 elementary,
;;; 4 special, 5 hypergeometric, 6 Appell, 8 unevaluated integral, 9 unknown
;;; function. The function lists are the SageMath port's (the one the report
;;; grades Maxima with), which is Mathematica's plus abs, signum, floor and
;;; atan2 as elementary; Maxima names map to them one to one. Unknown heads
;;; (bessel_j, elliptic_kc, realpart, ...) are 9, as in every port.

(in-package :maxima)

(defun mr-grade-name (op)
  "The lower-case print name of operator OP without Maxima's $/% prefix."
  (let ((s (string-downcase (symbol-name op))))
    (if (and (> (length s) 1) (member (char s 0) '(#\$ #\%))) (subseq s 1) s)))

(defun mr-grade-head (e)
  "The name of E's head, for a subscripted function the array's name."
  (let ((op (caar e)))
    (if (eq op 'mqapply) (mr-grade-name (caar (cadr e))) (mr-grade-name op))))

(defun mr-grade-real-number-p (e)
  (or (numberp e) (and (consp e) (member (caar e) '(rat bigfloat)))))

(defun mr-grade-complex-parts (e)
  "(re . im) when E is a numeric complex constant with a nonzero imaginary
part built from real numbers and %i, else nil."
  (cond ((eq e '$%i) (cons 0 1))
        ((atom e) nil)
        ((eq (caar e) 'mtimes)
         (let ((args (cdr e)))
           (and (= (length args) 2) (mr-grade-real-number-p (first args))
                (eq (second args) '$%i) (cons 0 (first args)))))
        ((eq (caar e) 'mplus)
         (let ((args (cdr e)))
           (and (= (length args) 2) (mr-grade-real-number-p (first args))
                (let ((im (mr-grade-complex-parts (second args))))
                  (and im (eql (car im) 0) (cons (first args) (cdr im)))))))
        (t nil)))

(defun mr-grade-number-leaves (n)
  (cond ((and (consp n) (eq (caar n) 'rat)) 3)
        (t 1)))

(defun mr-grade-complex-leaves (parts)
  (+ 1 (mr-grade-number-leaves (car parts)) (mr-grade-number-leaves (cdr parts))))

(defun mr-leaf (e)
  (cond ((eq e '$%i) 3)
        ((atom e) 1)
        ((member (caar e) '(rat)) 3)
        ((eq (caar e) 'bigfloat) 1)
        ((mr-grade-complex-parts e) (mr-grade-complex-leaves (mr-grade-complex-parts e)))
        ((eq (caar e) 'mtimes) (mr-leaf-fold e 'mtimes))
        ((eq (caar e) 'mplus) (mr-leaf-fold e 'mplus))
        ((eq (caar e) 'mqapply)
         ;; f[s1, ...](a1, ...) -> F[s1, ..., a1, ...]
         (+ 1 (reduce #'+ (mapcar #'mr-leaf (cdr (cadr e))))
            (reduce #'+ (mapcar #'mr-leaf (cddr e)))))
        ((and (eq (caar e) '%hypergeometric) (= (length (cdr e)) 3)
              (let ((p (length (cdr (second e)))) (q (length (cdr (third e)))))
                (and (= q 1) (member p '(1 2)))))
         (+ 1 (reduce #'+ (mapcar #'mr-leaf (cdr (second e))))
            (reduce #'+ (mapcar #'mr-leaf (cdr (third e))))
            (mr-leaf (fourth e))))
        (t (+ 1 (reduce #'+ (mapcar #'mr-leaf (cdr e)))))))

(defun mr-leaf-fold (e kind)
  "LeafCount of a sum or product whose numeric complex parts Mathematica
would hold as one Complex number. A product: the real coefficient and %i. A
sum: every real-number term and every numeric complex term."
  (let ((args (cdr e)))
    (if (eq kind 'mtimes)
        (if (member '$%i args)
            (let* ((coef (if (mr-grade-real-number-p (first args)) (first args) 1))
                   (rest (remove '$%i (if (mr-grade-real-number-p (first args)) (cdr args) args)
                                 :count 1)))
              (if rest
                  (+ 1 (mr-grade-complex-leaves (cons 0 coef))
                     (reduce #'+ (mapcar #'mr-leaf rest)))
                  (mr-grade-complex-leaves (cons 0 coef))))
            (+ 1 (reduce #'+ (mapcar #'mr-leaf args))))
        (let* ((cplx (find-if #'mr-grade-complex-parts args))
               (re (and cplx (find-if #'mr-grade-real-number-p args))))
          (if cplx
              (let ((rest (remove cplx (if re (remove re args :count 1) args) :count 1))
                    (num (mr-grade-complex-leaves
                          (cons (or re 0) (cdr (mr-grade-complex-parts cplx))))))
                (if rest (+ 1 num (reduce #'+ (mapcar #'mr-leaf rest))) num))
              (+ 1 (reduce #'+ (mapcar #'mr-leaf args))))))))

(defun mr-grade-general (e)
  "E in general form, simplified. Rubi can answer in CRE (rat) form, anywhere
in the expression; the walks below would read the CRE's internal gensyms as
leaves and fail on them (measured 2026-10-01: 136 corpus answers ungraded,
`#:G823 is not of type LIST')."
  (simplify ($totaldisrep e)))

(defmfun $mr_leaf_count (e)
  (mr-leaf (mr-grade-general e)))

(defparameter *mr-grade-elementary*
  '("exp" "log" "sin" "cos" "tan" "cot" "sec" "csc"
    "asin" "acos" "atan" "acot" "asec" "acsc"
    "sinh" "cosh" "tanh" "coth" "sech" "csch"
    "asinh" "acosh" "atanh" "acoth" "asech" "acsch"
    ;; the SageMath port's additions (report section 4.2.4)
    "signum" "atan2" "floor" "abs" "mabs"))

(defparameter *mr-grade-special*
  '("erf" "erfc" "erfi" "fresnel_s" "fresnel_c"
    "expintegral_e" "expintegral_e1" "expintegral_ei" "expintegral_li"
    "expintegral_si" "expintegral_ci" "expintegral_shi" "expintegral_chi"
    "gamma" "gamma_incomplete" "log_gamma" "psi" "zeta" "li" "lambert_w"
    "elliptic_f" "elliptic_e" "elliptic_pi" "elliptic_ec"))

(defparameter *mr-grade-integral* '("integrate" "unintegrable"))

(defun mr-type-args (e)
  "The parts ExpnType takes the maximum over: every argument, list elements
and subscripts included."
  (let ((parts (if (eq (caar e) 'mqapply) (append (cdr (cadr e)) (cddr e)) (cdr e))))
    (loop for p in parts
          append (if (and (consp p) (eq (caar p) 'mlist)) (cdr p) (list p)))))

(defun mr-type (e)
  (cond ((atom e) 1)
        ((member (caar e) '(rat bigfloat)) 1)
        ((mr-grade-complex-parts e) 1)
        ((eq (caar e) 'mlist) (reduce #'max (mapcar #'mr-type (cdr e)) :initial-value 1))
        ((eq (caar e) 'mexpt)
         (let ((b (second e)) (x (third e)))
           (cond ((integerp x) (mr-type b))
                 ((and (consp x) (eq (caar x) 'rat))
                  (if (or (integerp b) (and (consp b) (eq (caar b) 'rat))) 1
                      (max (mr-type b) 2)))
                 (t (max (mr-type b) (mr-type x) 3)))))
        ((member (caar e) '(mplus mtimes))
         (reduce #'max (mapcar #'mr-type (cdr e)) :initial-value 1))
        (t (let ((h (mr-grade-head e)))
             (cond ((member h *mr-grade-elementary* :test #'string=)
                    (max 3 (mr-type (if (eq (caar e) 'mqapply) (caddr e) (cadr e)))))
                   ((member h *mr-grade-special* :test #'string=)
                    (reduce #'max (mapcar #'mr-type (mr-type-args e)) :initial-value 4))
                   ((string= h "hypergeometric")
                    (reduce #'max (mapcar #'mr-type (mr-type-args e)) :initial-value 5))
                   ((string= h "appellf1")
                    (reduce #'max (mapcar #'mr-type (mr-type-args e)) :initial-value 6))
                   ((member h *mr-grade-integral* :test #'string=)
                    (reduce #'max (mapcar #'mr-type (mr-type-args e)) :initial-value 8))
                   (t 9))))))

(defmfun $mr_expn_type (e)
  (mr-type (mr-grade-general e)))

(defun mr-grade-has (e pred)
  (cond ((atom e) (funcall pred e))
        ((funcall pred (caar e)) t)
        (t (some (lambda (a) (mr-grade-has a pred)) (cdr e)))))

(defun mr-grade-has-i (e) (mr-grade-has e (lambda (a) (eq a '$%i))))

(defun mr-grade-has-integral (e)
  (mr-grade-has e (lambda (a) (and (symbolp a)
                                   (member (mr-grade-name a) *mr-grade-integral*
                                           :test #'string=)))))

(defmfun $mr_grade (result optimal)
  "[grade, leaf(result), leaf(optimal), type(result), type(optimal)]:
GradeAntiderivative (see the file header)."
  (let* ((r (mr-grade-general result)) (o (mr-grade-general optimal))
         (lr (mr-leaf r)) (lo (mr-leaf o)) (tr (mr-type r)) (to (mr-type o))
         (g (if (<= tr to)
                (cond ((and (mr-grade-has-i r) (not (mr-grade-has-i o))) "C")
                      ((<= lr (* 2 lo)) "A")
                      (t "B"))
                (if (mr-grade-has-integral r) "F" "C"))))
    (list '(mlist) g lr lo tr to)))

;;; The corpus driver's lines (test/corpus_driver.py classify_entry):
;;;   mr_grade_line("OPTIMAL", false, [opt] | [])  -> "OPTIMAL <leaf> <type>"
;;;   mr_grade_line("GRADE", r, [opt] | [])        -> "GRADE <g> <leaf> <type>"
;;; with `-' for what could not be computed (an optimal that failed to
;;; evaluate: the errcatch list is empty).
(defmfun $mr_grade_line (tag r opt)
  (let ((o (and ($listp opt) (cdr opt) (mr-grade-general (cadr opt)))))
    (if (equal tag "OPTIMAL")
        (if o (format nil "OPTIMAL ~d ~d" (mr-leaf o) (mr-type o)) "OPTIMAL - -")
        (let ((rs (mr-grade-general r)))
          (if o
              (let ((g (cdr ($mr_grade rs o))))
                (format nil "GRADE ~a ~d ~d" (first g) (second g) (fourth g)))
              (format nil "GRADE - ~d ~d" (mr-leaf rs) (mr-type rs)))))))
