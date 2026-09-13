;;; probes/matcher/01-mma4max-feasibility.lisp
;;;
;;; Matcher spike (handoffs/2026-09-11-matcher-spike.md): does Fateman's
;;; mma4max newmatch.lisp (2011-03-21), loaded into Maxima's SBCL and fed
;;; Maxima integrands through a thin converter, produce the bindings
;;; Mathematica's matcher would produce for Rubi LHS patterns -- with no
;;; false matches and acceptable per-match time?
;;;
;;; Driver: 01-mma4max-feasibility.mac (run by the .run script), after
;;; 01-mma4max-load.lisp.  No rule files are loaded (no TLS flag needed).
;;;
;;; Per case:
;;;  - target: a Maxima string -> parse_string + meval (Maxima's own
;;;    simplifier) -> max2mm, the converter below, which reads the internal
;;;    form and does no simplification -> (Int <tree> x).  :tree gives a
;;;    hand-built Mathematica-form tree instead; :swap reverses the
;;;    top-level Times arguments (the other stored factor order).
;;;  - pattern: the pinned Rubi .m LHS, hand-transcribed into FullForm
;;;    s-expressions (mma4max's parser.lisp pstring blocks on a string in
;;;    this SBCL -- see 01-FINDINGS.md), expanded by pat-expand, then
;;;    prepared the way mma4max prepares a rule (rulefix): fixopts
;;;    (Optional -> Alternatives) then bindfix (pattern variables renamed
;;;    into the PAT package, so matching cannot confuse them with target
;;;    symbols of the same name).
;;;  - condition: only the rule's FreeQ[{...}, x] clause, passed to
;;;    mma::match as the match condition (the matcher may backtrack into it).
;;;  - expected: bindings derived by hand from Mathematica pattern semantics
;;;    (:why).  "|" separates alternatives where Mathematica admits several
;;;    structural matches that FreeQ cannot separate (the rule's other
;;;    conditions pick in Mathematica).  :none = must not match.
;;;  - pattern-variable x is always expected to bind x.
;;;  - :model t marks a case whose Maxima-simplified target differs in
;;;    structure from the Mathematica form (expression model, not matcher);
;;;    it is reported but excluded from the gate.
;;;
;;; After the gated run, one experiment re-runs every case with a nil-guard
;;; on mma::mblank1 (runtime redefinition; the reference file is untouched)
;;; to test whether the false matches are local to that function.

(in-package :cl-user)

;; newmatch.lisp, parser.lisp and simp1.lisp proclaim (speed 3) (safety 0)
;; globally when loaded; this file is compiled with safe settings.
(declaim (optimize (speed 1) (safety 1) (debug 1)))

(defparameter *spike-file* *load-truename*)

(defun mm-sym (name) (intern name :mma))

;;; BEGIN CONVERTER (Maxima internal form -> mma4max tree)

(defparameter *mm-heads*
  '((maxima::mplus . "Plus") (maxima::mtimes . "Times")
    (maxima::mexpt . "Power") (maxima::%log . "Log")
    (maxima::$polylog . "PolyLog") (maxima::%sin . "Sin")
    (maxima::%cos . "Cos") (maxima::%tan . "Tan")
    (maxima::%gamma . "Gamma") (maxima::%erf . "Erf")))

(defparameter *mm-constants*
  '((maxima::$%e . "E") (maxima::$%pi . "Pi")))

(defun mm-name (sym)
  ;; Maxima inverts symbol case (x is $X, A is |$a|); undo it, drop $ / %.
  (let* ((s (symbol-name sym))
         (s (if (and (> (length s) 1) (find (char s 0) "$%")) (subseq s 1) s)))
    (mm-sym (cond ((string= s (string-upcase s)) (string-downcase s))
                  ((string= s (string-downcase s)) (string-upcase s))
                  (t s)))))

(defun max2mm (e)
  (cond ((numberp e) e)
        ((symbolp e)
         (let ((c (assoc e *mm-constants*)))
           (if c (mm-sym (cdr c)) (mm-name e))))
        ((eq (caar e) 'maxima::rat) (/ (second e) (third e)))
        (t (let ((h (assoc (caar e) *mm-heads*)))
             (cons (if h (mm-sym (cdr h)) (mm-name (caar e)))
                   (mapcar #'max2mm (cdr e)))))))

;;; END CONVERTER

(defun maxima-form (string)
  (maxima::meval (maxima::meval (list (list 'maxima::$parse_string) string))))

(defun now-ns ()
  ;; get-internal-real-time advances in ~1 ms steps in this SBCL (measured,
  ;; 01-FINDINGS.md), so time with the monotonic clock directly.
  (multiple-value-bind (s ns) (sb-unix:clock-gettime sb-unix:clock-monotonic)
    (+ (* s 1000000000) ns)))

;; Compact FullForm: a symbol  n_  is Pattern[n, Blank[]],  n_.  is
;; Optional[Pattern[n, Blank[]]],  n_H  is Pattern[n, Blank[H]].
(defun pat-expand (p)
  (cond ((consp p) (mapcar #'pat-expand p))
        ((and p (symbolp p))
         (let* ((s (symbol-name p)) (u (position #\_ s)))
           (if (or (null u) (zerop u))
               p
               (let ((pattern (list (mm-sym "Pattern") (mm-sym (subseq s 0 u))))
                     (tail (subseq s (1+ u))))
                 (cond ((string= tail "")
                        (append pattern (list (list (mm-sym "Blank")))))
                       ((string= tail ".")
                        (list (mm-sym "Optional")
                              (append pattern (list (list (mm-sym "Blank"))))))
                       (t (append pattern
                                  (list (list (mm-sym "Blank") (mm-sym tail))))))))))
        (t p)))

(defun read-mm (string)
  (let ((*readtable* (copy-readtable nil))
        (*package* (find-package :mma)))
    (setf (readtable-case *readtable*) :preserve)
    (pat-expand (read-from-string string))))

(defun prepare-pattern (lhs)
  ;; mma4max's rulefix path: bindfix (fixopts (Rule lhs rhs)).
  (let* ((t0 (now-ns))
         (rule (mma::bindfix
                (mma::fixopts (list (mm-sym "Rule") lhs (mm-sym "Null"))))))
    (values (second rule) (- (now-ns) t0))))

(defun mm-free-of (tree v)
  (cond ((equal tree v) nil)
        ((consp tree) (every (lambda (s) (mm-free-of s v)) (cdr tree)))
        (t t)))

(defun freeq-condition (names)
  (let ((vars (mapcar (lambda (n) (mma::patvar (mm-sym n))) names))
        (xv (mma::patvar (mm-sym "x"))))
    (lambda ()
      (multiple-value-bind (xval xfound) (mma::sfind mma::env xv)
        (and xfound
             (every (lambda (v)
                      (multiple-value-bind (val found) (mma::sfind mma::env v)
                        (and found (mm-free-of val xval))))
                    vars))))))

(defun fresh-env ()
  ;; stack1.lisp's make-stack sizes its arrays from the special SIZE (100)
  (setf mma::env (let ((mma::size 5000)) (mma::make-stack :size 5000)))
  (mma::spushframe mma::env 'mma::bot))

(defun collect-bindings ()
  (let ((seen nil) (out nil) (pat (find-package :pat)))
    (dolist (b (mma::env2alist mma::env) (nreverse out))
      (let ((k (car b)))
        (when (and (symbolp k) (eq (symbol-package k) pat) (not (member k seen)))
          (push k seen)
          (push (cons (symbol-name k) (cdr b)) out))))))

(defun match-once (pat expr cond)
  (let ((ok (mma::match pat expr cond)))
    (multiple-value-prog1
        (values (and ok t) (and ok (collect-bindings)))
      (mma::spopframe mma::env))))

(defmacro with-cap ((seconds) &body body)
  `(handler-case (sb-ext:with-timeout ,seconds ,@body)
     (sb-ext:timeout () (fresh-env) :timeout)
     (error (e) (fresh-env)
       (list :error (substitute #\Space #\Newline (princ-to-string e))))))

(defun mm-equal (a b)
  (cond ((and (consp a) (consp b))
         (and (eq (car a) (car b))
              (= (length a) (length b))
              (if (member (car a) (list (mm-sym "Plus") (mm-sym "Times")))
                  (let ((rest (copy-list (cdr b))))
                    (every (lambda (u)
                             (let ((hit (member u rest :test #'mm-equal)))
                               (when hit
                                 (setf rest (remove (car hit) rest :count 1 :test #'eq))
                                 t)))
                           (cdr a)))
                  (every #'mm-equal (cdr a) (cdr b)))))
        ((and (numberp a) (numberp b)) (= a b))
        (t (equal a b))))

(defun split-on (s ch)
  (loop with start = 0
        for pos = (position ch s :start start)
        collect (subseq s start pos)
        while pos do (setf start (1+ pos))))

(defun parse-expect (s)
  (unless (eq s :none)
    (mapcar (lambda (alt)
              (loop for tok in (split-on (string-trim " " alt) #\Space)
                    unless (string= tok "")
                      collect (let ((p (position #\= tok)))
                                (cons (subseq tok 0 p) (subseq tok (1+ p))))))
            (split-on s #\|))))

(defun bindings-ok (bindings alternatives)
  (some (lambda (alt)
          (every (lambda (pair)
                   (let ((b (assoc (car pair) bindings :test #'string=)))
                     (and b (mm-equal (cdr b) (max2mm (maxima-form (cdr pair)))))))
                 (cons '("x" . "x") alt)))
        alternatives))

(defun swap-top (tree)
  (if (and (consp tree) (eq (car tree) (mm-sym "Times")))
      (cons (car tree) (reverse (cdr tree)))
      tree))

(defun time-matches (pat expr cond singles batch)
  ;; -> (median-ns max-ns mean-ns)
  (let ((v (make-array singles)))
    (dotimes (i singles)
      (let ((t0 (now-ns)))
        (mma::match pat expr cond)
        (mma::spopframe mma::env)
        (setf (aref v i) (- (now-ns) t0))))
    (setf v (sort v #'<))
    (let ((t0 (now-ns)))
      (dotimes (i batch)
        (mma::match pat expr cond)
        (mma::spopframe mma::env))
      (list (aref v (floor singles 2)) (aref v (1- singles))
            (if (plusp batch)
                (/ (float (- (now-ns) t0)) batch)
                (aref v (floor singles 2)))))))

;;; ------------------------------------------------------------------
;;; Rules: pinned .m LHS (reference/rubi @ 61e9c18e, file + line) in compact
;;; FullForm, with the FreeQ[{...}, x] list of the same rule.

(defparameter *rules*
  '(("1.1.1.1.m L5" "(Int (Power x_ m_.) x_Symbol)" ("m"))
    ("1.1.1.1.m L7" "(Int (Power (Plus a_. (Times b_. x_)) m_) x_Symbol)" ("a" "b" "m"))
    ("1.1.1.2.m L4"
     "(Int (Times (Power (Plus a_ (Times b_. x_)) m_.) (Plus c_ (Times d_. x_))) x_Symbol)"
     ("a" "b" "c" "d" "m"))
    ("1.1.1.2.m L8"
     "(Int (Times (Power (Plus a_ (Times b_. x_)) m_) (Power (Plus c_ (Times d_. x_)) m_)) x_Symbol)"
     ("a" "b" "c" "d"))
    ("1.1.1.2.m L15"
     "(Int (Times (Power (Plus a_. (Times b_. x_)) m_.) (Power (Plus c_. (Times d_. x_)) n_.)) x_Symbol)"
     ("a" "b" "c" "d" "n"))
    ("1.1.2.2.m L47"
     "(Int (Times (Power (Times c_. x_) m_.) (Power (Plus a_ (Times b_. (Power x_ 2))) p_.)) x_Symbol)"
     ("a" "b" "c" "m"))
    ("1.1.2.6.m L48"
     "(Int (Times (Power (Times g_. x_) m_.) (Power (Plus a_ (Times b_. (Power x_ 2))) p_) (Power (Plus c_ (Times d_. (Power x_ 2))) q_.) (Plus e_ (Times f_. (Power x_ 2)))) x_Symbol)"
     ("a" "b" "c" "d" "e" "f" "g" "m"))
    ("1.2.1.2.m L26"
     "(Int (Times (Power (Times e_. x_) m_.) (Power (Plus (Times b_. x_) (Times c_. (Power x_ 2))) p_.)) x_Symbol)"
     ("b" "c" "e" "m"))
    ("2.1.m L8"
     "(Int (Times (Power (Plus c_. (Times d_. x_)) m_.) (Power F_ (Times g_. (Plus e_. (Times f_. x_))))) x_Symbol)"
     ("F" "c" "d" "e" "f" "g"))
    ("3.1.2.m L13"
     "(Int (Times (Power (Times d_. x_) m_.) (Power (Plus a_. (Times b_. (Log (Times c_. (Power x_ n_.))))) p_)) x_Symbol)"
     ("a" "b" "c" "d" "m" "n" "p"))
    ("3.1.2.m L14"
     "(Int (Times (Power (Times d_. (Power x_ q_)) m_) (Power (Plus a_. (Times b_. (Log (Times c_. (Power x_ n_.))))) p_.)) x_Symbol)"
     ("a" "b" "c" "d" "m" "n" "p" "q"))
    ("3.1.3.m L4"
     "(Int (Times (Power (Plus d_ (Times e_. (Power x_ r_.))) q_.) (Plus a_. (Times b_. (Log (Times c_. (Power x_ n_.)))))) x_Symbol)"
     ("a" "b" "c" "d" "e" "n" "r"))
    ("3.1.3.m L6"
     "(Int (Times (Power (Plus d_ (Times e_. (Power x_ r_.))) q_) (Plus a_. (Times b_. (Log (Times c_. (Power x_ n_.)))))) x_Symbol)"
     ("a" "b" "c" "d" "e" "n" "q" "r"))
    ("3.1.4.m L5"
     "(Int (Times (Power x_ m_.) (Power (Plus d_ (Times e_. (Power x_ r_.))) q_.) (Plus a_. (Times b_. (Log (Times c_. (Power x_ n_.)))))) x_Symbol)"
     ("a" "b" "c" "d" "e" "n" "r"))
    ("3.1.4.m L7"
     "(Int (Times (Power (Times f_. x_) m_.) (Power (Plus d_ (Times e_. (Power x_ r_.))) q_) (Plus a_. (Times b_. (Log (Times c_. (Power x_ n_.)))))) x_Symbol)"
     ("a" "b" "c" "d" "e" "f" "m" "n" "q" "r"))
    ("3.1.4.m L29"
     "(Int (Times (Power (Times f_. x_) m_.) (Power (Plus d_ (Times e_. (Power x_ r_.))) q_.) (Plus a_. (Times b_. (Log (Times c_. (Power x_ n_.)))))) x_Symbol)"
     ("a" "b" "c" "d" "e" "f" "m" "n" "q" "r"))
    ("3.1.5.m L45"
     "(Int (Times (Log (Times d_. (Power (Plus e_ (Times f_. (Power x_ m_.))) r_.))) (Power (Plus a_. (Times b_. (Log (Times c_. (Power x_ n_.))))) p_.)) x_Symbol)"
     ("a" "b" "c" "d" "e" "f" "r" "m" "n"))
    ("3.1.5.m L51"
     "(Int (Times (Power (Times g_. x_) q_.) (Log (Times d_. (Power (Plus e_ (Times f_. (Power x_ m_.))) r_.))) (Plus a_. (Times b_. (Log (Times c_. (Power x_ n_.)))))) x_Symbol)"
     ("a" "b" "c" "d" "e" "f" "g" "r" "m" "n" "q"))
    ("3.1.5.m L56"
     "(Int (Times (PolyLog k_ (Times e_. (Power x_ q_.))) (Plus a_. (Times b_. (Log (Times c_. (Power x_ n_.)))))) x_Symbol)"
     ("a" "b" "c" "e" "n" "q"))
    ("3.1.5.m L60"
     "(Int (Times (Power (Times d_. x_) m_.) (PolyLog k_ (Times e_. (Power x_ q_.))) (Plus a_. (Times b_. (Log (Times c_. (Power x_ n_.)))))) x_Symbol)"
     ("a" "b" "c" "d" "e" "m" "n" "q"))
    ("3.2.1.m L19"
     "(Int (Times (Power (Plus f_. (Times g_. x_)) m_.) (Power (Plus A_. (Times B_. (Log (Times e_. (Power (Times (Plus a_. (Times b_. x_)) (Power (Plus c_. (Times d_. x_)) -1)) n_.))))) p_.)) x_Symbol)"
     ("a" "b" "c" "d" "e" "f" "g" "A" "B" "n"))
    ("3.2.1.m L21"
     "(Int (Times (Power (Plus f_. (Times g_. x_)) m_.) (Power (Plus A_. (Times B_. (Log (Times e_. (Power (Times (Plus a_. (Times b_. x_)) (Power (Plus c_. (Times d_. x_)) -1)) n_.))))) p_.)) x_Symbol)"
     ("a" "b" "c" "d" "e" "f" "g" "A" "B" "n"))
    ("3.2.1.m L23"
     "(Int (Times (Power (Plus f_. (Times g_. x_)) m_.) (Power (Plus A_. (Times B_. (Log (Times e_. (Power (Times (Plus a_. (Times b_. x_)) (Power (Plus c_. (Times d_. x_)) -1)) n_.))))) p_.)) x_Symbol)"
     ("a" "b" "c" "d" "e" "f" "g" "A" "B" "n"))
    ("3.2.2.m L6"
     "(Int (Times (Power (Plus f_. (Times g_. x_)) m_.) (Power (Plus h_. (Times i_. x_)) q_.) (Power (Plus A_. (Times B_. (Log (Times e_. (Power (Times (Plus a_. (Times b_. x_)) (Power (Plus c_. (Times d_. x_)) -1)) n_.))))) p_.)) x_Symbol)"
     ("a" "b" "c" "d" "e" "f" "g" "h" "i" "A" "B" "n" "p"))
    ("3.2.2.m L8"
     "(Int (Times (Power (Plus f_. (Times g_. x_)) m_.) (Power (Plus h_. (Times i_. x_)) q_.) (Power (Plus A_. (Times B_. (Log (Times e_. (Power (Times (Plus a_. (Times b_. x_)) (Power (Plus c_. (Times d_. x_)) -1)) n_.))))) p_.)) x_Symbol)"
     ("a" "b" "c" "d" "e" "f" "g" "h" "i" "A" "B" "m" "n" "p" "q"))
    ("3.3.m L4"
     "(Int (Power (Plus a_. (Times b_. (Log (Times c_. (Power (Plus d_ (Times e_. x_)) n_.))))) p_.) x_Symbol)"
     ("a" "b" "c" "d" "e" "n" "p"))
    ("3.4.m L5"
     "(Int (Log (Times c_. (Power (Plus d_ (Times e_. (Power x_ n_))) p_.))) x_Symbol)"
     ("c" "d" "e" "n" "p"))
    ("3.4.m L12"
     "(Int (Times (Power x_ m_.) (Power (Plus a_. (Times b_. (Log (Times c_. (Power (Plus d_ (Times e_. (Power x_ n_))) p_.))))) q_.)) x_Symbol)"
     ("a" "b" "c" "d" "e" "m" "n" "p" "q"))
    ("3.4.m L14"
     "(Int (Times (Power (Times f_ x_) m_) (Power (Plus a_. (Times b_. (Log (Times c_. (Power (Plus d_ (Times e_. (Power x_ n_))) p_.))))) q_.)) x_Symbol)"
     ("a" "b" "c" "d" "e" "f" "m" "n" "p" "q"))))

;;; ------------------------------------------------------------------
;;; Cases.  :doc = what the committed records/docs say defmatch does today
;;; (cited, not re-measured here).

(defparameter *cases*
  '(
    ;; G1 -- Optional defaults
    (:id "G1-01" :group "G1" :rule "1.1.1.1.m L5" :target "x^3" :expect "m=3"
     :why "Power[x,3] vs Power[x_,m_.]" :doc "synthetic")
    (:id "G1-02" :group "G1" :rule "1.1.1.1.m L5" :target "x^m" :expect "m=m"
     :why "symbolic exponent" :doc "synthetic")
    (:id "G1-03" :group "G1" :rule "1.1.1.1.m L7" :target "(3+2*x)^4" :expect "a=3 b=2 m=4"
     :why "all slots explicit" :doc "synthetic")
    (:id "G1-04" :group "G1" :model t :rule "1.1.1.1.m L7" :target "(2*x)^m" :expect "a=0 b=2 m=m"
     :why "Maxima's simplifier stores (2*x)^m as 2^m*x^m; Mathematica keeps Power[Times[2,x],m]"
     :doc "matcher-probe-series.md:62 dead shape C 'numeric-literal factor in the power base'")
    (:id "G1-04t" :group "G1" :rule "1.1.1.1.m L7" :tree "(Power (Times 2 x) m)" :expect "a=0 b=2 m=m"
     :why "Mathematica-form tree of G1-04: Plus[a_.,..] vs Times -> a=Default[Plus]=0" :doc "synthetic")
    (:id "G1-05" :group "G1" :rule "1.1.1.1.m L7" :target "(1+x)^m" :expect "a=1 b=1 m=m"
     :why "Times[b_.,x_] vs x -> b=Default[Times]=1" :doc "synthetic")
    (:id "G1-06" :group "G1" :rule "1.1.1.1.m L7" :target "x^3" :expect "a=0 b=1 m=3"
     :why "both linear-coefficient defaults" :doc "synthetic")
    (:id "G1-07" :group "G1" :rule "1.1.1.2.m L15" :target "(1+2*x)^3*(4+5*x)^(1/2)"
     :expect "a=1 b=2 m=3 c=4 d=5 n=1/2 | a=4 b=5 m=1/2 c=1 d=2 n=3"
     :why "two linear powers, either assignment (IGtQ[m,0] picks in .m)" :doc "synthetic")
    (:id "G1-08" :group "G1" :rule "2.1.m L8" :target "x*exp(2*x)"
     :expect "c=0 d=1 m=1 F=%e g=2 e=0 f=1 | c=0 d=1 m=1 F=%e g=1 e=0 f=2"
     :why "x -> (0+1*x)^1; g_.*(e_.+f_.*x_) vs 2*x: g=2,f=1 or g=1,f=2" :doc "synthetic")
    (:id "G1-09" :group "G1" :rule "1.1.2.2.m L47" :target "x*(a+b*x^2)^p" :expect "c=1 m=1 a=a b=b p=p"
     :why "(c_.*x_)^m_. vs bare x" :doc "synthetic")
    (:id "G1-10" :group "G1" :rule "3.3.m L4" :target "log(c*(d+e*x)^n)" :expect "a=0 b=1 c=c d=d e=e n=n p=1"
     :why "three nested defaults: p, a, b" :doc "synthetic")
    (:id "G1-11" :group "G1" :rule "3.3.m L4" :target "(a+b*log(d+e*x))^2" :expect "a=a b=b c=1 d=d e=e n=1 p=2"
     :why "c_. and n_. defaults inside Log" :doc "synthetic")

    ;; G2 -- product factor order (both stored orders)
    (:id "G2-01" :group "G2" :rule "1.2.1.2.m L26" :target "(d*x)^m/(b*x+c*x^2)" :expect "e=d m=m b=b c=c p=-1"
     :why "1.2.1.2 e115 L136" :doc "record class1: deferred; maxima_rubi_dispatch.lisp:88 cites e115 (pass 2)")
    (:id "G2-02" :group "G2" :rule "1.2.1.2.m L26" :target "(d*x)^m/(b*x+c*x^2)" :swap t :expect "e=d m=m b=b c=c p=-1"
     :why "e115, other stored order" :doc "as G2-01")
    (:id "G2-03" :group "G2" :rule "1.1.2.2.m L47" :target "(c*x)^m*(a+b*x^2)^p" :expect "c=c m=m a=a b=b p=p"
     :why "(c x)^m family" :doc "synthetic; dispatch.lisp:83 (c x)^m first-^-factor rule")
    (:id "G2-04" :group "G2" :rule "1.1.2.2.m L47" :target "(c*x)^m*(a+b*x^2)^p" :swap t :expect "c=c m=m a=a b=b p=p"
     :why "other stored order" :doc "as G2-03")
    (:id "G2-05" :group "G2" :rule "1.2.1.2.m L26" :target "(d*x)^m*sqrt(b*x+c*x^2)" :expect "e=d m=m b=b c=c p=1/2"
     :why "fractional tail" :doc "synthetic")
    (:id "G2-06" :group "G2" :rule "1.2.1.2.m L26" :target "(d*x)^m*sqrt(b*x+c*x^2)" :swap t :expect "e=d m=m b=b c=c p=1/2"
     :why "other stored order" :doc "synthetic")
    (:id "G2-07" :group "G2" :rule "3.1.2.m L13" :target "(d*x)^m*(a+b*log(c*x^n))^2" :expect "d=d m=m a=a b=b c=c n=n p=2"
     :why "product-base power head x powered tail" :doc "matcher-probe-series.md:61 dead shape B")
    (:id "G2-08" :group "G2" :rule "3.1.2.m L13" :target "(d*x)^m*(a+b*log(c*x^n))^2" :swap t :expect "d=d m=m a=a b=b c=c n=n p=2"
     :why "other stored order" :doc "as G2-07")

    ;; G3 -- exponent 1 dropped at construction
    (:id "G3-01" :group "G3" :rule "1.1.1.1.m L5" :target "x" :expect "m=1"
     :why "x_^m_. vs x -> m=Default[Power]=1" :doc "maxima_rubi_implicit1.lisp:14 x^pm vs x -> false")
    (:id "G3-02" :group "G3" :rule "1.1.1.2.m L15" :target "x*(a+b*x)"
     :expect "a=0 b=1 m=1 c=a d=b n=1 | a=a b=b m=1 c=0 d=1 n=1"
     :why "both factors bare" :doc "maxima_rubi_implicit1.lisp:16 factor gap -> false")
    (:id "G3-03" :group "G3" :rule "1.1.1.2.m L15" :target "x*(a+b*x)^2"
     :expect "a=0 b=1 m=1 c=a d=b n=2 | a=a b=b m=2 c=0 d=1 n=1"
     :why "atom base bare" :doc "maxima_rubi_implicit1.lisp:17 -> TRUE")
    (:id "G3-04" :group "G3" :rule "1.1.2.6.m L48" :target "(e*x)^m*(A+B*x^2)*(c+d*x^2)^3/(a+b*x^2)^2"
     :expect "g=e m=m a=a b=b p=-2 c=c d=d q=3 e=A f=B | g=e m=m a=c b=d p=3 c=a d=b q=-2 e=A f=B"
     :why "1.1.2.6 e20 L31: bare (e_+f_.*x_^2) takes A+B*x^2; the two powers either way" :doc "record class1: verified")
    (:id "G3-05" :group "G3" :rule "3.1.4.m L5" :target "x^5*(d+e*x^2)*(a+b*log(c*x^n))"
     :expect "m=5 d=d e=e r=2 q=1 a=a b=b c=c n=n"
     :why "3.1.4 e171 L224: (d_+e_.*x_^r_.)^q_. has q_. optional -> bare binomial q=1"
     :doc "adjudication-g1.md:213 M1+M2 'faithful 0-bind in both systems'")
    (:id "G3-06" :group "G3" :rule "3.1.2.m L13" :target "x/(a+b*log(c*x^n))" :expect "d=1 m=1 a=a b=b c=c n=n p=-1"
     :why "3.1.2 e67 L84: bare x head" :doc "uplift sec.2 Wave1 M6 0-bind")
    (:id "G3-07" :group "G3" :rule "3.1.4.m L29" :target "x*(d+e*x^2)*(a+b*log(c*x^n))"
     :expect "f=1 m=1 d=d e=e r=2 q=1 a=a b=b c=c n=n"
     :why "bare x and bare binomial together" :doc "synthetic")

    ;; G4 -- bare-factor permutation (pass-4 A class)
    (:id "G4-01" :group "G4" :rule "3.1.5.m L45" :target "(a+b*log(c*x^n))*log(1+e*x)"
     :expect "d=1 e=1 f=e m=1 r=1 a=a b=b c=c n=n p=1"
     :why "3.1.5 e5 L18" :doc "uplift sec.2 Wave1 A: pass-4-only rescue")
    (:id "G4-02" :group "G4" :rule "3.1.5.m L51" :target "x*(a+b*log(c*x^n))*log(d*(e+f*x^2)^m)"
     :expect "g=1 q=1 d=d e=e f=f m=2 r=m a=a b=b c=c n=n"
     :why "3.1.5 e91 L116" :doc "uplift sec.2 Wave1 A: pass-4 reverse-only rescue")
    (:id "G4-03" :group "G4" :rule "3.1.5.m L60" :target "x*(a+b*log(c*x^n))*polylog(2,e*x)"
     :expect "d=1 m=1 k=2 e=e q=1 a=a b=b c=c n=n"
     :why "3.1.5 e209 L258" :doc "uplift sec.2 Wave1 A: pass-4-only rescue")
    (:id "G4-04" :group "G4" :rule "3.1.5.m L60" :target "x*(a+b*log(c*x^n))*polylog(3,e*x)"
     :expect "d=1 m=1 k=3 e=e q=1 a=a b=b c=c n=n"
     :why "3.1.5 e215 L264" :doc "uplift sec.2 Wave1 A: pass-4-only rescue")
    (:id "G4-05" :group "G4" :rule "3.1.5.m L56" :target "(a+b*log(c*x^n))*polylog(2,e*x^2)"
     :expect "k=2 e=e q=2 a=a b=b c=c n=n"
     :why "two bare factors, slotted q" :doc "synthetic")
    (:id "G4-06" :group "G4" :rule "3.1.5.m L51" :target "x*(a+b*log(c*x^n))*log(d*(e+f*x^2)^m)" :swap t
     :expect "g=1 q=1 d=d e=e f=f m=2 r=m a=a b=b c=c n=n"
     :why "e91, reversed factor order" :doc "as G4-02")

    ;; G5 -- slotted inner exponent (C1/C5)
    (:id "G5-01" :group "G5" :rule "3.1.4.m L5" :target "x^3*(d+e*x)*(a+b*log(c*x^n))"
     :expect "m=3 d=d e=e r=1 q=1 a=a b=b c=c n=n"
     :why "3.1.4 e1 L12: r=1 literal, q=1 bare" :doc "adjudication-g1.md:207 Q1 r2@e1 [false]")
    (:id "G5-02" :group "G5" :rule "3.1.4.m L5" :target "x^5*(d+e*x^2)^2*(a+b*log(c*x^n))"
     :expect "m=5 d=d e=e r=2 q=2 a=a b=b c=c n=n"
     :why "3.1.4 e183 L236" :doc "adjudication-g1.md:216 Q2 r2@e183 [false]")
    (:id "G5-03" :group "G5" :rule "3.1.4.m L5" :target "x^5*(d+e*x^r)^2*(a+b*log(c*x^n))"
     :expect "m=5 d=d e=e r=r q=2 a=a b=b c=c n=n"
     :why "K1 target (3.1.4 e379 L484 family)" :doc "adjudication-g1.md:223 K1 r2 [false]")
    (:id "G5-04" :group "G5" :rule "3.1.4.m L5" :target "x^5*(d+e*x^r)*(a+b*log(c*x^n))"
     :expect "m=5 d=d e=e r=r q=1 a=a b=b c=c n=n"
     :why "3.1.4 e367 L472" :doc "adjudication-g1.md:222 M1")
    (:id "G5-05" :group "G5" :rule "3.1.4.m L29" :target "x^3*(a+b*log(c*x^n))*sqrt(d+e*x)"
     :expect "f=1 m=3 d=d e=e r=1 q=1/2 a=a b=b c=c n=n"
     :why "3.1.4 e130 L165" :doc "adjudication-g1.md:234 M1 r23")
    (:id "G5-06" :group "G5" :rule "3.1.4.m L29" :target "x^5*(a+b*log(c*x^n))*sqrt(d+e*x^2)"
     :expect "f=1 m=5 d=d e=e r=2 q=1/2 a=a b=b c=c n=n"
     :why "3.1.4 e251 L328" :doc "adjudication-g1.md:237 Q3/Q5 [false]")
    (:id "G5-07" :group "G5" :rule "3.1.3.m L6" :target "(d+e/x^(1/(q+1)))^q*(a+b*log(c*x^n))"
     :expect "d=d e=e r=-1/(1+q) q=q a=a b=b c=c n=n"
     :why "3.1.4 e446 L565" :doc "adjudication-g1.md:252 3_1_3_r3 0-binds (P1)")
    (:id "G5-08" :group "G5" :rule "3.1.3.m L4" :target "(d+e*x^r)^2*(a+b*log(c*x^n))"
     :expect "d=d e=e r=r q=2 a=a b=b c=c n=n"
     :why "3.1.4 e387 L492" :doc "adjudication-g1.md:246 K2 r24 [false]")
    (:id "G5-09" :group "G5" :rule "3.4.m L12" :target "x^3*log(c*(a+b*sqrt(x))^p)"
     :expect "m=3 a=0 b=1 c=c d=a e=b n=1/2 p=p q=1"
     :why "3.4 suite L63: x_^n_ vs sqrt(x)" :doc "adjudication-g3.md:57 3_4 matcher-gap")
    (:id "G5-10" :group "G5" :rule "3.4.m L5" :target "log(c*(a+b*sqrt(x))^p)"
     :expect "c=c d=a e=b n=1/2 p=p"
     :why "3.4 suite L66" :doc "adjudication-g3.md:57 3_4 matcher-gap")
    (:id "G5-11" :group "G5" :rule "3.4.m L12" :target "log(c*(a+b*sqrt(x))^p)/x"
     :expect "m=-1 a=0 b=1 c=c d=a e=b n=1/2 p=p q=1"
     :why "3.4 suite L67" :doc "adjudication-g3.md:57 3_4 matcher-gap")

    ;; G6 -- ratio log-argument (C3)
    (:id "G6-01" :group "G6" :rule "3.2.1.m L19" :target "(A+B*log(e*(a+b*x)/(c+d*x)))/(a*g+b*g*x)^2"
     :expect "f=a*g g=b*g m=-2 A=A B=B e=e a=a b=b c=c d=d n=1 p=1"
     :why "3.2.1 e93 L130: Times[e,P,Q^-1] regrouped under Power[..,n_.] n=1"
     :doc "adjudication-g2.md:97 D2 0-bind (probe pA)")
    (:id "G6-02" :group "G6" :rule "3.2.1.m L21" :target "(A+B*log(e*(c+d*x)/(a+b*x)))/(a*g+b*g*x)^2"
     :expect "f=a*g g=b*g m=-2 A=A B=B e=e a=c b=d c=a d=b n=1 p=1"
     :why "3.2.1 e178 L235" :doc "adjudication-g2.md:98 D2")
    (:id "G6-03" :group "G6" :rule "3.2.1.m L23" :target "(A+B*log(e*(a+b*x)/(c+d*x)))/(f+g*x)^2"
     :expect "f=f g=g m=-2 A=A B=B e=e a=a b=b c=c d=d n=1 p=1"
     :why "3.2.1 e236 L313" :doc "adjudication-g2.md:99 D2")
    (:id "G6-04" :group "G6" :rule "3.2.2.m L6" :target "(a*g+b*g*x)^3*(c*i+d*i*x)^2*(A+B*log(e*(a+b*x)/(c+d*x)))"
     :expect "f=a*g g=b*g m=3 h=c*i i=d*i q=2 A=A B=B e=e a=a b=b c=c d=d n=1 p=1 | f=c*i g=d*i m=2 h=a*g i=b*g q=3 A=A B=B e=e a=a b=b c=c d=d n=1 p=1"
     :why "3.2.2 e10 L21" :doc "adjudication-g2.md:101 D2 r3 cluster")
    (:id "G6-05" :group "G6" :rule "3.2.2.m L8" :target "(a*g+b*g*x)^m*(c*i+d*i*x)^(-2-m)*(A+B*log(e*((a+b*x)/(c+d*x))^n))"
     :expect "f=a*g g=b*g m=m h=c*i i=d*i q=-2-m A=A B=B e=e a=a b=b c=c d=d n=n p=1 | f=c*i g=d*i m=-2-m h=a*g i=b*g q=m A=A B=B e=e a=a b=b c=c d=d n=n p=1"
     :why "3.2.2 e214 L247: explicit ratio power n" :doc "adjudication-g2.md:103 D2 L8 r5")

    ;; G7 -- monomial head (C2/M6)
    (:id "G7-01" :group "G7" :rule "3.1.2.m L13" :target "x^3/(a+b*log(c*x^n))" :expect "d=1 m=3 a=a b=b c=c n=n p=-1"
     :why "3.1.2 e65 L82: (d_.*x_)^m_. vs x^3 -> d=1" :doc "uplift sec.2 Wave1 M6 0-bind")
    (:id "G7-02" :group "G7" :rule "3.1.2.m L13" :target "x^2/(a+b*log(c*x^n))" :expect "d=1 m=2 a=a b=b c=c n=n p=-1"
     :why "3.1.2 e66 L83" :doc "uplift sec.2 Wave1 M6 0-bind")
    (:id "G7-03" :group "G7" :rule "3.1.2.m L14"
     :tree "(Times (Power (Times d (Power x 2)) m) (Plus a (Times b (Log (Times c (Power x n))))))"
     :expect "d=d q=2 m=m a=a b=b c=c n=n p=1"
     :why "(d x^2)^m (a+b log), Mathematica-form tree (Maxima rewrites it: G7-M1)" :doc "synthetic")
    (:id "G7-04" :group "G7" :rule "3.1.2.m L13" :target "x^(-1+n)*(a+b*log(c*x^n))^p" :expect "d=1 m=-1+n a=a b=b c=c n=n p=p"
     :why "3.1.2 e191 L224: FreeQ[-1+n,x] is True -> binds m=-1+n"
     :doc "uplift sec.2 Wave1 D: 'faithful reject ... FreeQ[m,x] rejects m=-1+n'")
    (:id "G7-M1" :group "G7" :model t :rule "3.1.2.m L14" :target "(d*x^2)^m*(a+b*log(c*x^n))"
     :expect "d=d q=2 m=m a=a b=b c=c n=n p=1"
     :why "same integrand as G7-03 through Maxima's simplifier (d^m*abs(x)^(2*m)*...)" :doc "expression-model note")

    ;; NEG -- must not match
    (:id "N-01" :group "NEG" :rule "1.1.1.1.m L7" :target "5*(3+2*x)^4" :expect :none
     :why "Times head vs Power pattern; x_ cannot take (3+2x)^4 under x_Symbol" :doc "")
    (:id "N-02" :group "NEG" :rule "3.1.4.m L7" :target "x^5*(d+e*x^2)*(a+b*log(c*x^n))" :expect :none
     :why "q_ non-optional vs bare binomial" :doc "matcher-probe-series.md:63 M2 (the real non-optional case)")
    (:id "N-03" :group "NEG" :rule "1.1.1.1.m L7" :target "(a+b*x)^x" :expect :none
     :why "FreeQ[m,x] veto" :doc "")
    (:id "N-04" :group "NEG" :rule "1.1.1.1.m L7" :target "(x^2+b*x)^3" :expect :none
     :why "only decompositions have a=x^2 or b=... containing x: FreeQ veto" :doc "")
    (:id "N-05" :group "NEG" :rule "3.3.m L4" :target "log(5+2*z)" :expect :none
     :why "x_ would bind z inside, x_Symbol binds x" :doc "handoff NEG FreeQ/variable guard")
    (:id "N-06" :group "NEG" :rule "1.1.1.2.m L8" :target "(1+x)^(1/2)*(1-x)^(1/3)" :expect :none
     :why "repeated m_ must be consistent" :doc "")
    (:id "N-07" :group "NEG" :rule "3.1.3.m L4" :target "x^5*(a+b*log(c*x^n))" :expect :none
     :why "d_ (no default) cannot match nothing: x^5 is not (d+e*x^r)^q" :doc "")
    (:id "N-08" :group "NEG" :rule "1.1.2.2.m L47" :target "(a+b*x^2)^p" :expect :none
     :why "(c_.*x_)^m_. is not optional as a whole factor" :doc "")
    (:id "N-09" :group "NEG" :rule "2.1.m L8" :target "%e^(a+b*x)" :expect :none
     :why "(c_.+d_.*x_)^m_. is not optional as a whole factor" :doc "")
    (:id "N-10" :group "NEG" :rule "3.2.1.m L19" :target "(A+B*log(x*(a+b*x)/(c+d*x)))/(f+g*x)^2" :expect :none
     :why "every decomposition puts x into e or b: FreeQ veto" :doc "")
    (:id "N-11" :group "NEG" :rule "1.1.1.1.m L5" :target "z^3" :expect :none
     :why "x_ binds z in the integrand, x in x_Symbol" :doc "")
    (:id "N-12" :group "NEG" :rule "3.1.4.m L29" :target "(d+e*x^r)^2*(a+b*log(c*x^n))" :expect :none
     :why "3.1.4 e387: no (f x)^m factor; L29/L30 need one" :doc "adjudication-g1.md:246 cites r24/L30 as the cover")
    (:id "N-13" :group "NEG" :rule "1.1.1.1.m L7" :target "a+b*x" :expect :none
     :why "m_ non-optional vs bare linear" :doc "")
    (:id "N-14" :group "NEG" :rule "3.4.m L14" :target "x^m*log(c*(d+e*x^n)^p)" :expect :none
     :why "f_ has no default: Times[f_,x_] cannot match bare x (3.4.m L12 is the x^m rule)" :doc "")
    (:id "N-15" :group "NEG" :rule "1.1.1.2.m L4" :target "x^m*(c+d*x)" :expect :none
     :why "a_ has no default: Plus[a_,b_.*x_] cannot match bare x" :doc "")

    ;; control -- repeated name, consistent
    (:id "C-01" :group "CTL" :rule "1.1.1.2.m L8" :target "(1+x)^m*(1-x)^m"
     :expect "a=1 b=1 c=1 d=-1 m=m | a=1 b=-1 c=1 d=1 m=m"
     :why "twin of N-06 with equal exponents" :doc "")))

;;; ------------------------------------------------------------------

;; Ungated control: two Optionals directly under one Times.  remopts
;; (newmatch.lisp l.568-596) rewrites only the first Optional of an argument
;; list; mapremopts does not revisit the level.  Synthetic pattern (no .m
;; source); printed as a CTL line.
(setf *rules*
      (append *rules*
              '(("synthetic two-optionals" "(Int (Times a_. b_. (Power x_ m_)) x_Symbol)"
                 ("a" "b" "m")))))
(setf *cases*
      (append *cases*
              '((:id "C-02" :group "CTL" :rule "synthetic two-optionals" :target "x^3"
                 :expect "a=1 b=1 m=3"
                 :why "Times[a_.,b_.,x_^m_] vs x^3: both factors default to 1" :doc "code reading only"))))

(defstruct res id group model matched struct ok bindings med max mean prep status)

(defun fmt-bindings (bs)
  (format nil "~{~a~^ ~}"
          (mapcar (lambda (b) (format nil "~a=~s" (car b) (cdr b))) bs)))

(defun ms (ns) (/ (or ns 0) 1000000.0))

(defun run-case (c &key quiet)
  (destructuring-bind (&key id group rule target tree swap expect why doc model) c
    (let* ((r (or (assoc rule *rules* :test #'string=) (error "no rule ~a" rule)))
           (integrand (if tree (read-mm tree) (max2mm (maxima-form target))))
           (integrand (if swap (swap-top integrand) integrand))
           (expr (list (mm-sym "Int") integrand (mm-sym "x")))
           (alts (parse-expect expect))
           (res (make-res :id id :group group :model model)))
      (fresh-env)
      (multiple-value-bind (pat prep) (prepare-pattern (read-mm (second r)))
        (setf (res-prep res) prep)
        (let* ((cond (freeq-condition (third r)))
               (s (with-cap (5) (match-once pat expr #'mma::truth)))
               (m (with-cap (5) (multiple-value-list (match-once pat expr cond)))))
          (setf (res-struct res) (eq s t))
          (cond ((eq m :timeout) (setf (res-status res) :timeout))
                ((eq (car m) :error) (setf (res-status res) m))
                (t (setf (res-matched res) (first m)
                         (res-bindings res) (second m)
                         (res-ok res) (if alts
                                          (and (first m) (bindings-ok (second m) alts) t)
                                          (not (first m))))
                   (let* ((t0 (now-ns))
                          (_ (match-once pat expr cond))
                          (one (- (now-ns) t0))
                          (tm (with-cap (60)
                                (if (> one 20000000)
                                    (time-matches pat expr cond 20 0)
                                    (time-matches pat expr cond 200 1000)))))
                     (declare (ignore _))
                     (if (and (consp tm) (numberp (first tm)))
                         (setf (res-med res) (first tm) (res-max res) (second tm)
                               (res-mean res) (third tm))
                         (setf (res-status res) tm)))))))
      (unless quiet
        (format t "~&CASE ~a [~a~:[~;, model~]] ~a~:[~; swap~]~%  target: ~a~%  tree:   ~s~%  expect: ~a~%  why:    ~a~%  doc:    ~a~%"
                id group model rule swap (or target tree) integrand
                (if alts expect "no match") why doc)
        (format t "  result: ~a  matched=~a struct=~a~@[ status=~s~]~%  bound:  ~a~%  time:   median ~,4f ms  max ~,4f ms  mean ~,4f ms  (pattern prep ~,3f ms)~%"
                (if (res-ok res) "OK" "WRONG")
                (res-matched res) (res-struct res) (res-status res)
                (fmt-bindings (res-bindings res))
                (ms (res-med res)) (ms (res-max res)) (ms (res-mean res)) (ms (res-prep res))))
      (finish-output)
      res)))

(defun converter-lines ()
  (with-open-file (in *spike-file*)
    (let ((inside nil) (total 0) (code 0))
      (loop for line = (read-line in nil) while line
            do (let ((l (string-trim " " line)))
                 (cond ((search ";;; BEGIN CONVERTER" l) (setf inside t))
                       ((search ";;; END CONVERTER" l) (setf inside nil))
                       (inside (incf total)
                               (unless (or (string= l "") (char= (char l 0) #\;))
                                 (incf code))))))
      (values total code))))

(defun summarize (results prefix)
  ;; -> (values groups-pass false-matches median-ns over50 failed)
  (let ((groups-pass t))
    (dolist (g '("G1" "G2" "G3" "G4" "G5" "G6" "G7"))
      (let* ((pos (remove-if-not (lambda (r) (and (string= (res-group r) g) (not (res-model r))))
                                 results))
             (ok (count-if #'res-ok pos))
             (pct (if pos (/ (* 100.0 ok) (length pos)) 0.0)))
        (unless (>= pct 90.0) (setf groups-pass nil))
        (format t "~aGROUP ~a correct ~a/~a (~,1f%)~@[  wrong: ~{~a~^ ~}~]~%"
                prefix g ok (length pos) pct
                (mapcar #'res-id (remove-if #'res-ok pos)))))
    (dolist (r (remove-if-not #'res-model results))
      (format t "~aMODEL ~a correct=~a matched=~a (excluded from the gate)~%"
              prefix (res-id r) (res-ok r) (res-matched r)))
    (let* ((neg (remove-if-not (lambda (r) (string= (res-group r) "NEG")) results))
           (false (remove-if-not #'res-matched neg))
           (timed (remove-if-not #'res-med results))
           (meds (sort (mapcar #'res-med timed) #'<))
           (maxs (mapcar #'res-max timed))
           (n (length meds))
           (median (if meds (nth (floor n 2) meds) 0))
           (p90 (if meds (nth (min (1- n) (floor (* 9 n) 10)) meds) 0))
           (worst (if maxs (reduce #'max maxs) 0))
           (over50 (count-if (lambda (m) (> m 50000000)) maxs))
           (failed (remove-if-not #'res-status results))
           (slow (subseq (sort (copy-list timed) #'> :key #'res-mean) 0 (min 5 n))))
      (format t "~aNEG false matches ~a/~a~@[: ~{~a~^ ~}~]~%"
              prefix (length false) (length neg) (mapcar #'res-id false))
      (dolist (r (remove-if-not (lambda (r) (string= (res-group r) "CTL")) results))
        (format t "~aCTL ~a correct=~a~%" prefix (res-id r) (res-ok r)))
      (format t "~aTIMING cases=~a per-case median: min ~,4f p50 ~,4f p90 ~,4f max ~,4f ms; worst single ~,4f ms; cases with a single >50 ms: ~a~%"
              prefix n (ms (first meds)) (ms median) (ms p90) (ms (car (last meds))) (ms worst) over50)
      (format t "~aTIMING slowest by mean: ~{~a~^, ~}~%" prefix
              (mapcar (lambda (r) (format nil "~a ~,4f ms (prep ~,3f ms)"
                                          (res-id r) (ms (res-mean r)) (ms (res-prep r))))
                      slow))
      (format t "~aSTATUS timeouts/errors: ~a~@[: ~{~a~^ ~}~]~%"
              prefix (length failed) (mapcar #'res-id failed))
      (values groups-pass false median over50 failed))))

(defun install-mblank1-nil-guard ()
  ;; newmatch.lisp mblank1 (l.1041) binds a named Blank to
  ;; (or e (|Default| gh)) -- the identity -- when E is NIL, i.e. when the
  ;; Flat/Orderless remainder is empty.  Experiment: a Blank needs an element.
  (let ((orig (fdefinition 'mma::mblank1)))
    (setf (fdefinition 'mma::mblank1)
          (lambda (plist e name gh condition)
            (and e (funcall orig plist e name gh condition))))))

(defun matchtests-run (label)
  ;; Fateman's own suite (mma4max/matchtests.lisp: tests, rubit, tests2).
  ;; The file is read with the standard reader, so its Sin is CL:SIN; it is
  ;; mapped to |Sin| (the reader-case artifact found in the smoke run).
  (let ((*package* (find-package :mma))
        (*print-right-margin* 100000)
        (*print-pretty* nil)
        (i 0) (fails nil))
    (unless (boundp 'mma::tests)
      (load (merge-pathnames "reference/fateman/lisp/mma4max/matchtests.lisp"
                             (or (sb-ext:posix-getenv "MR_ROOT") "/home/serge/src/maxima-rubi/"))))
    (fresh-env)
    (setf mma::kp (subst (mm-sym "Sin") 'cl:sin mma::kp))
    (loop for (form exp) on (subst (mm-sym "Sin") 'cl:sin
                                   (append (symbol-value 'mma::tests)
                                           (symbol-value 'mma::rubit)
                                           (symbol-value 'mma::tests2)))
            by #'cddr
          do (let ((got (with-cap (5) (eval form))))
               (incf i)
               (unless (equal got (cadr exp))
                 (push i fails)
                 (format t "~a FAIL ~a ~s => ~s EXPECTED ~s~%" label i (cdr form) got (cadr exp)))))
    (fresh-env)
    (format t "~a matchtests ~a/~a pass; failing: ~{~a~^ ~}~%"
            label (- i (length fails)) i (reverse fails))))

(defun spike-run ()
  (let* ((*print-right-margin* 100000)
         (*print-pretty* nil)
         (results (mapcar #'run-case *cases*)))
    (format t "~&~%=== SUMMARY (mma4max as published)~%")
    (multiple-value-bind (groups-pass false median over50 failed) (summarize results "")
      (multiple-value-bind (total code) (converter-lines)
        (format t "CONVERTER ~a lines (~a code lines) between the markers; no simplification (reads the simplified internal form)~%"
                total code)
        (format t "GATE LIBRARY clause groups>=90%: ~:[FAIL~;pass~]~%" groups-pass)
        (format t "GATE LIBRARY clause zero NEG false matches: ~:[FAIL~;pass~]~%" (null false))
        (format t "GATE LIBRARY clause median<=0.5ms and no case>50ms: ~:[FAIL~;pass~]~%"
                (and (<= median 500000) (zerop over50) (null failed)))
        (format t "GATE LIBRARY clause converter<=~~300 lines, no simplification: ~:[FAIL~;pass~]~%"
                (<= total 300))))
    (format t "~&~%=== EXPERIMENT: mblank1 nil-guard (not gated; FORK evidence)~%")
    (install-mblank1-nil-guard)
    (let ((patched (mapcar (lambda (c) (run-case c :quiet t)) *cases*)))
      (loop for a in results
            for b in patched
            unless (and (eq (res-ok a) (res-ok b)) (eq (res-matched a) (res-matched b)))
              do (format t "PCASE ~a ok ~a->~a matched ~a->~a bound: ~a~%"
                         (res-id a) (res-ok a) (res-ok b) (res-matched a) (res-matched b)
                         (fmt-bindings (res-bindings b))))
      (summarize patched "PATCHED "))))

;;; ------------------------------------------------------------------
;;; Scaling series (not gated): matchfol (newmatch.lisp l.1543) tries every
;;; subset of the expression's summands/factors (docomb) per pattern term.
;;; The gated cases have <= 4 factors; this series grows a Plus from 4 to 13
;;; terms under the 1.2.1.1 trinomial LHS.  "N" targets have no x^2 term (a
;;; failing search); "M" targets carry free z_i summands that a_. must absorb
;;; (Flat Plus: a = 1+z1+...+zk).  Each case: 3 single matches, 30 s cap.

(setf *rules*
      (append *rules*
              '(("1.2.1.1.m L9"
                 "(Int (Power (Plus a_. (Times b_. x_) (Times c_. (Power x_ 2))) p_) x_Symbol)"
                 ("a" "b" "c")))))

(defparameter *scale-cases*
  '((:id "S-N04" :rule "1.2.1.1.m L9" :target "sqrt(1+x+x^3+x^4)" :expect :none)
    (:id "S-N06" :rule "1.2.1.1.m L9" :target "sqrt(1+x+x^3+x^4+x^5+x^6)" :expect :none)
    (:id "S-N08" :rule "1.2.1.1.m L9" :target "sqrt(1+x+x^3+x^4+x^5+x^6+x^7+x^8)" :expect :none)
    (:id "S-N10" :rule "1.2.1.1.m L9" :target "sqrt(1+x+x^3+x^4+x^5+x^6+x^7+x^8+x^9+x^10)" :expect :none)
    (:id "S-N12" :rule "1.2.1.1.m L9" :target "sqrt(1+x+x^3+x^4+x^5+x^6+x^7+x^8+x^9+x^10+x^11+x^12)" :expect :none)
    (:id "S-M05" :rule "1.2.1.1.m L9" :target "sqrt(1+2*x+3*x^2+z1+z2)"
     :expect "a=1+z1+z2 b=2 c=3 p=1/2")
    (:id "S-M07" :rule "1.2.1.1.m L9" :target "sqrt(1+2*x+3*x^2+z1+z2+z3+z4)"
     :expect "a=1+z1+z2+z3+z4 b=2 c=3 p=1/2")
    (:id "S-M09" :rule "1.2.1.1.m L9" :target "sqrt(1+2*x+3*x^2+z1+z2+z3+z4+z5+z6)"
     :expect "a=1+z1+z2+z3+z4+z5+z6 b=2 c=3 p=1/2")
    (:id "S-M11" :rule "1.2.1.1.m L9" :target "sqrt(1+2*x+3*x^2+z1+z2+z3+z4+z5+z6+z7+z8)"
     :expect "a=1+z1+z2+z3+z4+z5+z6+z7+z8 b=2 c=3 p=1/2")
    (:id "S-M13" :rule "1.2.1.1.m L9" :target "sqrt(1+2*x+3*x^2+z1+z2+z3+z4+z5+z6+z7+z8+z9+z10)"
     :expect "a=1+z1+z2+z3+z4+z5+z6+z7+z8+z9+z10 b=2 c=3 p=1/2")))

(defun scale-run (label)
  (let ((*print-right-margin* 100000) (*print-pretty* nil))
    (dolist (c *scale-cases*)
      (destructuring-bind (&key id rule target expect) c
        (let* ((r (assoc rule *rules* :test #'string=))
               (expr (list (mm-sym "Int") (max2mm (maxima-form target)) (mm-sym "x")))
               (pat (prepare-pattern (read-mm (second r))))
               (cond (freeq-condition (third r)))
               (alts (parse-expect expect))
               (terms (1- (length (second (second expr)))))
               (times nil) (verdict nil))
          (dotimes (k 3)
            (fresh-env)
            (let* ((t0 (now-ns))
                   (m (with-cap (30) (multiple-value-list (match-once pat expr cond))))
                   (dt (- (now-ns) t0)))
              (push dt times)
              (setf verdict
                    (cond ((eq m :timeout) :timeout)
                          ((eq (car m) :error) m)
                          (t (list :matched (first m)
                                   :correct (if alts
                                                (and (first m) (bindings-ok (second m) alts) t)
                                                (not (first m)))
                                   :bound (fmt-bindings (second m))))))))
          (format t "~&~a ~a terms=~a ~s  time min ~,3f max ~,3f ms~%"
                  label id terms verdict (ms (reduce #'min times)) (ms (reduce #'max times)))
          (finish-output))))))
