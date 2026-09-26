;;;; test/matcher/test_mr_tree.lisp -- MR-TREE unit tests (inside Maxima).
;;;; Run: maxima --very-quiet -b test/matcher/test_mr_tree.mac

(defpackage :mr-tree-test (:use :cl :mr-match :mr-tree) (:export #:run))
(in-package :mr-tree-test)

(defvar *passed* 0)
(defvar *failed* 0)

(defun check (name ok &optional detail)
  (if ok
      (progn (incf *passed*) (format t "  PASS: ~a~%" name))
      (progn (incf *failed*) (format t "  FAIL: ~a~@[~%    ~a~]~%" name detail))))

(defun conv (s) (max->tree (maxima-form s)))

(defmacro check-conv (s expected)
  `(let ((got (conv ,s)) (want (canonicalize (read-tree ,expected))))
     (check (format nil "max->tree ~a" ,s) (equal got want)
            (format nil "got ~a want ~a" (tree-string got) (tree-string want)))))

(defun round-trips-p (s)
  (let* ((e (maxima-form s)) (back (tree->max (max->tree e))))
    (values (maxima::alike1 e back) back)))

(defun test-table ()
  (format t "--- head table ---~%")
  (let ((table (head-table)))
    ;; 45 from the probe-02 table, +6 for the inert-trig substrate's six rows
    ;; (inert-trig substrate design 3.1).
    (check "one entry per (head, arity) of the probe-02 table" (= (length table) 51) (length table))
    (flet ((op (head arity) (third (find-if (lambda (r) (and (string= (symbol-name (first r)) head)
                                                             (= (second r) arity)))
                                            table))))
      (check "abs -> mabs" (eq (op "Abs" 1) 'maxima::mabs))
      (check "factorial -> mfactorial" (eq (op "Factorial" 1) 'maxima::mfactorial))
      (check "Gamma/2 -> %gamma_incomplete" (eq (op "Gamma" 2) 'maxima::%gamma_incomplete)))))

(defun test-max->tree ()
  (format t "--- max->tree ---~%")
  (check-conv "a+b*x" "(Plus a (Times b x))")
  (check-conv "x^(1/3)" "(Power x 1/3)")
  (check-conv "sqrt(x)" "(Power x 1/2)")
  (check-conv "1/x" "(Power x -1)")
  (check-conv "-x" "(Times -1 x)")
  (check-conv "exp(2*x)" "(Power E (Times 2 x))")
  (check-conv "%pi*x" "(Times Pi x)")
  (check-conv "A*x" "(Times A x)")
  (check-conv "log(x)" "(Log x)")
  (check-conv "abs(x)" "(Abs x)")
  (check-conv "x!" "(Factorial x)")
  (check-conv "gamma_incomplete(a,x)" "(Gamma a x)")
  (check-conv "li[2](x)" "(PolyLog 2 x)")
  (check-conv "psi[1](x)" "(PolyGamma 1 x)")
  (check-conv "0.1*x" "(Times 0.1d0 x)")
  (check-conv "1.5b0*x" "(Times 1.5d0 x)")
  (check-conv "2*%i*x" "(Times #C(0 2) x)")
  (check-conv "1+%i" "#C(1 1)")
  (check-conv "%i" "#C(0 1)")
  (check-conv "b*a+c" "(Plus c (Times a b))")
  ;; a user function reads as the head named like it (class-8 port,
  ;; 2026-09-25): 9.1's f_ binds the atom f and the head of f(x) alike
  (check-conv "foo(x)" "(foo x)")
  (check-conv "F(x)" "(F x)")
  (check "a user function's head is the symbol its bare name converts to"
         (eq (car (conv "f(x)")) (conv "f")))
  ;; ... but a %-noun, and a user function colliding with a table head of
  ;; its arity or a structural head, keep the opaque MX_ head
  (dolist (s '("'foo(x)" "Log(x)" "Plus(x,y)" "Derivative(x)"))
    (let ((got (conv s)))
      (check (format nil "~a -> MX_ head" s)
             (and (consp got) (symbolp (car got)) (search "MX_" (symbol-name (car got))))
             (tree-string got))))
  ;; a 2-arg Zeta is no table head (the table's Zeta is 1-arg): Hurwitz
  (check-conv "Zeta(2,x)" "(Zeta 2 x)")
  ;; the formal derivative (class 8 / 9.1): the noun 'diff(f(u), u, n) is
  ;; the curried tree (((Derivative n) f) u)
  (check-conv "'diff(f(x),x,1)" "(((Derivative 1) f) x)")
  (check-conv "'diff(f(x),x,3)" "(((Derivative 3) f) x)")
  (check-conv "'diff(f(x),x,m-1)" "(((Derivative (Plus -1 m)) f) x)")
  (check-conv "'diff(f(x),x,-2)" "(((Derivative -2) f) x)")
  (check-conv "'diff(F(x),x,1)*g(x)" "(Times (((Derivative 1) F) x) (g x))")
  (check-conv "subst(f(x)*g(x), x, 'diff(F(x),x,1))"
              "(((Derivative 1) F) (Times (f x) (g x)))")
  ;; not the formal-derivative shape: stays the opaque noun
  (let ((got (conv "'diff(f(x,y),x,1)")))
    (check "'diff(f(x,y),x,1) -> MX_ head" (and (consp got) (symbolp (car got))
                                               (search "MX_" (symbol-name (car got))))
           (tree-string got)))
  (check-conv "polylog(2,x)" "(PolyLog 2 x)")
  ;; the dispatcher converts integrands and bindings, which can be CRE or boolean
  (check-conv "rat(a+b*x)" "(Plus a (Times b x))")
  ;; (a CRE numerator is an expanded polynomial)
  (check-conv "rat((1+x)^2/(2*y))" "(Times 1/2 (Plus 1 (Power x 2) (Times 2 x)) (Power y -1))")
  (check-conv "true" "True")
  (check-conv "false" "False")
  (check "tree->max True/False -> the Maxima booleans"
         (and (eq (tree->max (sym "True")) t) (null (tree->max (sym "False")))))
  (check "maxima-name restores case" (equal (list (maxima-name 'maxima::$mm_sin) (maxima-name 'maxima::|$a|)
                                                  (maxima-name 'maxima::%sin))
                                            '("mm_sin" "A" "sin")))
  (let ((*unknown-head-hook* (lambda (op)
                               (let ((n (maxima-name op)))
                                 (and (> (length n) 3) (string= "mm_" n :end2 3) (sym (subseq n 3)))))))
    (check-conv "mm_Foo(x)" "(Foo x)")
    (check-conv "mm_sin(x)" "(sin x)")))

(defun test-inert-trig ()
  (format t "--- inert trig heads ---~%")
  ;; The inert trig heads (inert-trig substrate design 3.1). Rubi's section-4
  ;; rules pattern on the LOWERCASE heads; these are the Maxima operators that
  ;; carry them. The active heads must stay untouched: the reader's readtable
  ;; case is :preserve, so sin and Sin are different symbols.
  (check-conv "%mr_isin(x)" "(sin x)")
  (check-conv "%mr_icos(x)" "(cos x)")
  (check-conv "%mr_itan(x)" "(tan x)")
  (check-conv "%mr_icot(x)" "(cot x)")
  (check-conv "%mr_isec(x)" "(sec x)")
  (check-conv "%mr_icsc(x)" "(csc x)")
  ;; Inert and active in ONE expression, as a half-deactivated integrand is.
  (check-conv "sin(x) + %mr_isin(x)" "(Plus (Sin x) (sin x))"))

(defun test-round-trip ()
  (format t "--- tree->max round trip ---~%")
  (dolist (s '("a+b*x" "(a+b*x)^m*(c+d*x)^n" "x/(a+b*x)" "2*%i*x" "1+%i" "li[2](x)" "psi[1](x)"
               "sin(x)^2*log(c*x)" "A*x" "abs(x)" "x!" "0.1*x" "exp(2*x)" "foo(x,y)"
               "gamma_incomplete(a,x)" "sqrt(1-x^2)" "%pi*x"
               ;; class 8: user functions, Hurwitz Zeta, the formal derivative
               "f(x)*g(x)" "F(f(x)*g(x))" "'foo(x)" "Log(x)" "Zeta(2,a+b*x)"
               "'diff(f(x),x,1)" "'diff(f(x),x,m)" "'diff(f(x),x,-1)"
               "'diff(g(x),x,2)*f(x)^2" "subst(f(x)*g(x), x, 'diff(F(x),x,1))"
               "'diff(f(x,y),x,1)"))
    (multiple-value-bind (ok back) (round-trips-p s)
      (check (format nil "round trip ~a" s) ok (format nil "back ~s" back))))
  ;; order 0 writes back as f(u) itself
  (let ((back (tree->max (read-tree "(((Derivative 0) f) x)"))))
    (check "tree->max (((Derivative 0) f) x) = f(x)"
           (maxima::alike1 back (maxima-form "f(x)")) (format nil "back ~s" back))))

(defun run ()
  (setf *passed* 0 *failed* 0)
  (test-table)
  (test-max->tree)
  (test-inert-trig)
  (test-round-trip)
  (format t "Results: ~a passed, ~a failed~%" *passed* *failed*)
  (finish-output))
