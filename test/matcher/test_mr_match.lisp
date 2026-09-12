;;;; test/matcher/test_mr_match.lisp -- MR-MATCH unit tests.
;;;; Run: maxima --very-quiet -b test/matcher/test_mr_match.mac
;;;; Ends with "Results: <n> passed, <m> failed".

(defpackage :mr-match-test (:use :cl :mr-match) (:export #:run))
(in-package :mr-match-test)

(defvar *passed* 0)
(defvar *failed* 0)

(defun check (name ok &optional detail)
  (if ok
      (progn (incf *passed*) (format t "  PASS: ~a~%" name))
      (progn (incf *failed*) (format t "  FAIL: ~a~@[~%    ~a~]~%" name detail))))

(defun tr (s) (read-tree s))

(defun m (pattern-string expr-string &key pre cond-hook)
  "Match a compact pattern against a canonicalized tree; PRE names symbols
pre-bound to themselves (the integration variable)."
  (match (prepare (read-pattern pattern-string))
         (canonicalize (tr expr-string))
         :bindings (mapcar (lambda (n) (cons (sym n) (sym n))) pre)
         :cond-hook cond-hook))

(defun bound (alist name) (cdr (assoc (sym name) alist)))

(defun binds-p (alist &rest pairs)
  "PAIRS: name value-string ...; every name bound to the tree of its string."
  (loop for (n v) on pairs by #'cddr
        always (equal (bound alist n) (canonicalize (tr v)))))

(defmacro check-match (name (pattern expr &rest keys) &rest pairs)
  `(multiple-value-bind (b ok) (m ,pattern ,expr ,@keys)
     (check ,name (and ok (binds-p b ,@pairs)) (format nil "matched=~a bindings=~a" ok (tree-string b)))))

(defmacro check-no-match (name (pattern expr &rest keys))
  `(multiple-value-bind (b ok) (m ,pattern ,expr ,@keys)
     (check ,name (not ok) (format nil "unexpected match ~a" (tree-string b)))))

(defun count-bindings (pattern expr &key pre)
  (let ((n 0))
    (m pattern expr :pre pre :cond-hook (lambda (b) (declare (ignore b)) (incf n) nil))
    n))

(defun test-trees ()
  (format t "--- trees ---~%")
  (let ((e (tr "(Power x 1/2)")))
    (check "read-tree keeps case and ratios"
           (and (eq (first e) (sym "Power")) (eq (second e) (sym "x")) (eql (third e) 1/2))))
  (check "tree-string round trip"
         (string= (tree-string (tr "(Times -1 #C(0 2) 1/3 x)")) "(Times -1 #C(0 2) 1/3 x)"))
  (check "canonicalize sorts Plus/Times arguments only"
         (equal (canonicalize (tr "(Plus x 2 (Times b a) (f b a))"))
                (tr "(Plus 2 x (Times a b) (f b a))")))
  (check "tree< is a strict order on equal trees" (not (tree< (tr "(f x)") (tr "(f x)"))))
  (check "read-pattern expands x_ x_. x_H"
         (equal (read-pattern "(f x_ m_. y_Symbol)")
                (tr "(f (Pattern x (Blank)) (Optional (Pattern m (Blank))) (Pattern y (Blank Symbol)))")))
  (check "head-of atoms"
         (equal (mapcar #'head-of (list 3 1/2 0.5d0 #C(0 1) "s" (sym "x") (tr "(Sin x)")))
                (mapcar #'sym '("Integer" "Rational" "Real" "Complex" "String" "Symbol" "Sin")))))

(defun test-prepare ()
  (format t "--- prepare ---~%")
  (check "Optional defaults from the parent"
         (equal (compiled-pattern-tree (prepare (read-pattern "(Power (Plus a_. (Times b_. x_)) m_.)")))
                (tr "(Power (Plus (Optional (Pattern a (Blank)) 0) (Times (Optional (Pattern b (Blank)) 1) (Pattern x (Blank)))) (Optional (Pattern m (Blank)) 1))")))
  (check "variables collected in order"
         (equal (compiled-pattern-vars (prepare (read-pattern "(Plus a_. (Times b_. x_))")))
                (mapcar #'sym '("a" "b" "x"))))
  (flet ((rejects (s) (handler-case (progn (prepare (read-pattern s)) nil) (error () t))))
    (check "rejects Alternatives" (rejects "(Alternatives x_ y_)"))
    (check "rejects a sequence blank under Plus" (rejects "(Plus (Pattern x (BlankSequence)) y)"))
    (check "rejects an Optional under Sin" (rejects "(Sin x_.)"))))

(defun test-ordered ()
  (format t "--- ordered core ---~%")
  (check-match "literal atom" ("3" "3"))
  (check-no-match "different atom" ("3" "4"))
  (check-match "typed blank x_Symbol" ("x_Symbol" "x") "x" "x")
  (check-no-match "typed blank rejects a number" ("x_Symbol" "3"))
  (check-match "repeated name" ("(f x_ x_)" "(f a a)") "x" "a")
  (check-no-match "repeated name must agree" ("(f x_ x_)" "(f a b)"))
  (check-no-match "pre-bound name" ("(f x_)" "(f y)" :pre '("x")))
  (check-match "H1 pattern-variable head" ("(Int (F_ x_) x_Symbol)" "(Int (F x) x)") "F" "F" "x" "x")
  (check-match "H7 compound head" ("(Int (((Derivative n_) f_) x_) x_Symbol)" "(Int (((Derivative 2) f) x) x)")
               "n" "2" "f" "f")
  (check-match "Power exponent explicit" ("(Power x_ m_.)" "(Power y 3)") "x" "y" "m" "3")
  (check-match "Power exponent default through the base" ("(Power x_ m_.)" "y") "x" "y" "m" "1")
  (check-no-match "non-optional exponent needs a Power" ("(Power x_ m_)" "y"))
  (check-match "BlankSequence in order" ("(f a (Pattern x (BlankSequence)) d)" "(f a b c d)")
               "x" "(Sequence b c)")
  (check-match "BlankNullSequence may be empty" ("(f (Pattern x (BlankNullSequence)) a)" "(f a)")
               "x" "(Sequence)")
  (check-match "Complex pattern vs complex atom" ("(Complex 0 fz_)" "#C(0 2)") "fz" "2")
  (let ((*test-hook* (lambda (kind test e b)
                       (declare (ignore test e))
                       (and (eq kind :condition) (> (bound b "x") 2)))))
    (check-match "Condition hook accepts" ("(Condition x_ (Greater x 2))" "3") "x" "3")
    (check-no-match "Condition hook rejects" ("(Condition x_ (Greater x 2))" "1"))))

(defun test-flat ()
  (format t "--- match-flat ---~%")
  (check-match "Times Optional default" ("(Times b_. x_)" "x" :pre '("x")) "b" "1")
  (check-match "Plus/Times explicit" ("(Plus a_. (Times b_. x_))" "(Plus 3 (Times 2 x))" :pre '("x")) "a" "3" "b" "2")
  (check-match "Plus/Times all defaults" ("(Plus a_. (Times b_. x_))" "x" :pre '("x")) "a" "0" "b" "1")
  (check-match "blank takes the leftover run" ("(Times u_ (Power x_ 2))" "(Times a b (Power x 2))" :pre '("x"))
               "u" "(Times a b)")
  (check-match "blank takes a single leftover" ("(Times u_ (Power x_ 2))" "(Times a (Power x 2))" :pre '("x"))
               "u" "a")
  (check-no-match "G-1 N-15: a_ has no default (1.1.1.2.m L4)"
                  ("(Int (Times (Power (Plus a_ (Times b_. x_)) m_.) (Plus c_ (Times d_. x_))) x_Symbol)"
                   "(Int (Times (Power x m) (Plus c (Times d x))) x)" :pre '("x")))
  (check-no-match "G-1 N-07: d_ cannot match nothing (3.1.3.m L4)"
                  ("(Int (Times (Power (Plus d_ (Times e_. (Power x_ r_.))) q_.) (Plus a_. (Times b_. (Log (Times c_. (Power x_ n_.)))))) x_Symbol)"
                   "(Int (Times (Power x 5) (Plus a (Times b (Log (Times c (Power x n)))))) x)" :pre '("x")))
  (check-no-match "G-1: f_ has no default under Times" ("(Times f_ x_)" "x" :pre '("x")))
  (check-match "G-2 H2 pattern head under Times" ("(Int (Times u_ (F_ x_)) x_Symbol)" "(Int (Times u (F x)) x)")
               "u" "u" "F" "F")
  (check-match "G-2 H4 pattern head under Plus" ("(Int (Plus u_ (F_ x_)) x_Symbol)" "(Int (Plus u (F x)) x)")
               "u" "u" "F" "F")
  (check-match "G-2 H8 compound head under Times"
               ("(Int (Times u_ (((Derivative n_) f_) x_)) x_Symbol)" "(Int (Times u (((Derivative 2) f) x)) x)")
               "u" "u" "n" "2" "f" "f")
  (check-match "bound name consumes its parts" ("(Times a_ (Plus a_ x_))" "(Times c (Plus c x))" :pre '("x")) "a" "c")
  (check-no-match "bound name must be present" ("(Times a_ (Plus a_ x_))" "(Times c (Plus d x))" :pre '("x")))
  (check "two bare blanks: every split of three factors"
         (= 6 (count-bindings "(Times u_ v_)" "(Times a b c)"))
         (count-bindings "(Times u_ v_)" "(Times a b c)"))
  (check-match "narrow collapse: (c_.*x_)^m_. takes c*x inside a product (1.1.2.2.m L47)"
               ("(Times (Power (Times c_. x_) m_.) (Power (Plus a_ (Times b_. (Power x_ 2))) p_.))"
                "(Times c x (Power (Plus a (Times b (Power x 2))) p))" :pre '("x"))
               "c" "c" "m" "1" "a" "a" "b" "b" "p" "p")
  (let ((pat "(Times (Plus g_. (Times h_. x_)) (Sin x_))")
        (ex "(Times h x (Sin x))"))
    (check-no-match "G-6 narrow: Optional-reduced Plus does not take a run" (pat ex :pre '("x")))
    (let ((*flat-wide* t))
      (check-match "G-6 wide: Optional-reduced Plus takes a run" (pat ex :pre '("x")) "g" "0" "h" "h"))))

(defun test-hooks ()
  (format t "--- condition hook and retry ---~%")
  (let ((pat "(Times (Power (Plus a_. (Times b_. x_)) m_.) (Power (Plus c_. (Times d_. x_)) n_.))")
        (ex "(Times (Power (Plus 1 (Times 2 x)) 3) (Power (Plus 4 (Times 5 x)) 1/2))")
        (want-m-half (lambda (b) (eql (bound b "m") 1/2))))
    (check-match "retry finds the second assignment" (pat ex :pre '("x") :cond-hook want-m-half)
                 "m" "1/2" "a" "4" "b" "5" "n" "3")
    (let ((*cond-retry* nil))
      (check-no-match "no retry: the first complete binding is final" (pat ex :pre '("x") :cond-hook want-m-half)))
    (check "hook sees exactly the two complete bindings" (= 2 (count-bindings pat ex :pre '("x"))))))

(defun run ()
  (setf *passed* 0 *failed* 0)
  (test-trees)
  (test-prepare)
  (test-ordered)
  (test-flat)
  (test-hooks)
  (format t "Results: ~a passed, ~a failed~%" *passed* *failed*)
  (finish-output))
