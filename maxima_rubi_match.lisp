;;;; maxima_rubi_match.lisp -- MR-MATCH: structural pattern matcher with
;;;; Mathematica semantics for Rubi rule patterns.
;;;;
;;;; Design: docs/superpowers/specs/2026-09-12-matcher-substrate-design.md
;;;; section 3.2.  A re-implementation, in newmatch.lisp's continuation-passing
;;;; structure (m1 / ordered list / Pattern / Blank), of Fateman's mma4max
;;;; matcher (reference/fateman/lisp/mma4max/newmatch.lisp, 2011-03-21), without
;;;; its stack, evaluator (meval) or the constructs no Rubi LHS uses
;;;; (Alternatives, Except, Repeated, Action).  No Maxima dependency.
;;;;
;;;; Trees: an atom (integer, ratio, double-float, complex, string, or a symbol
;;;; in package MRS, case preserved) or a list (head arg ...) whose head is a
;;;; tree.  Bindings: an alist ((name . value) ...) threaded through
;;;; continuations -- nothing to unwind, no fixed-size stack.
;;;;
;;;; Semantics oracle: verify() in probes/matcher/02-roundtrip.py.

(defpackage :mrs (:use))

(defpackage :mr-match
  (:use :cl)
  (:export #:sym #:read-tree #:read-pattern #:tree-string #:head-of
           #:tree< #:canonicalize
           #:prepare #:compiled-pattern-p #:compiled-pattern-tree #:compiled-pattern-vars
           #:match #:*flat-wide* #:*cond-retry* #:*test-hook*))

(in-package :mr-match)

(defun sym (name) (intern name :mrs))

(defparameter +plus+ (sym "Plus"))
(defparameter +times+ (sym "Times"))
(defparameter +power+ (sym "Power"))
(defparameter +pattern+ (sym "Pattern"))
(defparameter +blank+ (sym "Blank"))
(defparameter +blank-seq+ (sym "BlankSequence"))
(defparameter +blank-null-seq+ (sym "BlankNullSequence"))
(defparameter +optional+ (sym "Optional"))
(defparameter +condition+ (sym "Condition"))
(defparameter +pattern-test+ (sym "PatternTest"))
(defparameter +complex+ (sym "Complex"))
(defparameter +sequence+ (sym "Sequence"))
(defparameter +integer+ (sym "Integer"))
(defparameter +rational+ (sym "Rational"))
(defparameter +real+ (sym "Real"))
(defparameter +string+ (sym "String"))
(defparameter +symbol+ (sym "Symbol"))

(defparameter +unsupported+
  (mapcar #'sym '("Alternatives" "Except" "Repeated" "RepeatedNull" "HoldPattern"
                  "Verbatim" "Longest" "Shortest" "PatternSequence" "OptionsPattern"
                  "KeyValuePattern" "OrderlessPatternSequence")))

(defvar *flat-wide* nil
  "G-6 switch (spec 3.6 mr_flat_wide): when true, a Plus/Times item whose
Optionals all take their defaults but one argument may take a run of the
parent's elements.  Default: the narrow reading.")

(defvar *cond-retry* t
  "Spec 3.6 mr_cond_retry: when true the condition hook is called on every
complete binding until it accepts one; when false the match ends at the first
complete binding.")

(defvar *test-hook* (lambda (kind test expr bindings)
                      (declare (ignore kind test expr bindings))
                      nil)
  "Called for Condition / PatternTest inside a pattern as
(funcall *test-hook* kind test expr bindings), kind :condition or
:pattern-test; a true result lets the match continue.  Default: fail closed.")

;;; ------------------------------------------------------------------
;;; reading, printing, heads, canonical order

(defvar *tree-readtable*
  (let ((rt (copy-readtable nil)))
    (setf (readtable-case rt) :preserve)
    rt))

(defun read-tree (string)
  (let ((*readtable* *tree-readtable*)
        (*package* (find-package :mrs))
        (*read-default-float-format* 'double-float)
        (*read-eval* nil))
    (read-from-string string)))

(defun expand-compact (tree)
  ;; x_ -> (Pattern x (Blank)); x_. -> (Optional (Pattern x (Blank)));
  ;; x_H -> (Pattern x (Blank H)).  Other symbols are left alone.
  (cond ((consp tree) (mapcar #'expand-compact tree))
        ((and tree (symbolp tree))
         (let* ((s (symbol-name tree)) (u (position #\_ s)))
           (if (or (null u) (zerop u))
               tree
               (let ((pat (list +pattern+ (sym (subseq s 0 u))))
                     (tail (subseq s (1+ u))))
                 (cond ((string= tail "") (append pat (list (list +blank+))))
                       ((string= tail ".") (list +optional+ (append pat (list (list +blank+)))))
                       (t (append pat (list (list +blank+ (sym tail))))))))))
        (t tree)))

(defun read-pattern (string)
  "Read a pattern in compact FullForm (x_, x_., x_H) into a full pattern tree."
  (expand-compact (read-tree string)))

(defun tree-string (tree)
  (with-output-to-string (s)
    (labels ((out (e)
               (cond ((null e) (write-string "()" s))
                     ((consp e)
                      (write-char #\( s)
                      (loop for (x . more) on e
                            do (out x) (when more (write-char #\Space s)))
                      (write-char #\) s))
                     ((complexp e)
                      (write-string "#C(" s) (out (realpart e)) (write-char #\Space s)
                      (out (imagpart e)) (write-char #\) s))
                     ((typep e 'ratio) (format s "~d/~d" (numerator e) (denominator e)))
                     ((integerp e) (format s "~d" e))
                     ((floatp e) (format s "~,,,,,,'eE" e))
                     ((stringp e) (prin1 e s))
                     ((symbolp e) (write-string (symbol-name e) s))
                     (t (format s "~a" e)))))
      (out tree))))

(defun head-of (e)
  (cond ((consp e) (car e))
        ((integerp e) +integer+)
        ((typep e 'ratio) +rational+)
        ((floatp e) +real+)
        ((complexp e) +complex+)
        ((stringp e) +string+)
        (t +symbol+)))

(defun rank (e)
  (cond ((realp e) 0) ((complexp e) 1) ((symbolp e) 2) ((stringp e) 3) (t 4)))

(defun real-kind (x) (typecase x (integer 0) (ratio 1) (t 2)))

(defun tree< (a b)
  "A total order on trees: numbers < complex < symbols < strings < lists."
  (let ((ra (rank a)) (rb (rank b)))
    (cond ((/= ra rb) (< ra rb))
          ((= ra 0) (or (< a b) (and (= a b) (< (real-kind a) (real-kind b)))))
          ((= ra 1) (or (tree< (realpart a) (realpart b))
                        (and (not (tree< (realpart b) (realpart a)))
                             (tree< (imagpart a) (imagpart b)))))
          ((= ra 2) (let ((na (symbol-name a)) (nb (symbol-name b)))
                      (or (string< na nb)
                          (and (string= na nb)
                               (string< (package-name (symbol-package a))
                                        (package-name (symbol-package b)))))))
          ((= ra 3) (and (string< a b) t))
          (t (cond ((tree< (car a) (car b)) t)
                   ((tree< (car b) (car a)) nil)
                   ((/= (length a) (length b)) (< (length a) (length b)))
                   (t (loop for x in (cdr a) for y in (cdr b)
                            when (tree< x y) return t
                            when (tree< y x) return nil
                            finally (return nil))))))))

(defun canonicalize (tree)
  "Sort the arguments of every Plus/Times node by tree< (nothing else changes)."
  (if (consp tree)
      (let ((args (mapcar #'canonicalize (cdr tree)))
            (head (canonicalize (car tree))))
        (cons head (if (or (eq head +plus+) (eq head +times+))
                       (stable-sort args #'tree<)
                       args)))
      tree))

;;; ------------------------------------------------------------------
;;; prepare: validate, fill Optional defaults, collect variable names

(defstruct (compiled-pattern (:constructor %make-compiled-pattern (tree vars)))
  tree vars)

(defun flat-head-p (h) (or (eq h +plus+) (eq h +times+)))
(defun seq-blank-head-p (h) (or (eq h +blank-seq+) (eq h +blank-null-seq+)))

(defun prepare (pattern)
  "Validate PATTERN (a full pattern tree), give every Optional its default from
its parent (Plus 0, Times 1, Power exponent 1), return a compiled-pattern."
  (let ((vars nil))
    (labels ((fail (fmt &rest args) (apply #'error (concatenate 'string "mr-match prepare: " fmt) args))
             (walk (p parent pos)
               (if (atom p)
                   p
                   (let ((h (car p)))
                     (cond
                       ((member h +unsupported+) (fail "unsupported construct ~a" (symbol-name h)))
                       ((eq h +optional+)
                        (unless (<= 2 (length p) 3) (fail "bad Optional ~a" (tree-string p)))
                        (let ((default (cond ((cddr p) (third p))
                                             ((eq parent +plus+) 0)
                                             ((eq parent +times+) 1)
                                             ((and (eq parent +power+) (eql pos 2)) 1)
                                             (t (fail "Optional without a default under ~a"
                                                      (if (symbolp parent) parent "a compound head")))))
                              (inner (second p)))
                          (unless (and (consp inner) (eq (car inner) +pattern+)
                                       (consp (third inner)) (eq (car (third inner)) +blank+))
                            (fail "Optional must wrap a named Blank: ~a" (tree-string p)))
                          (list +optional+ (walk inner parent pos) default)))
                       ((eq h +pattern+)
                        (unless (and (= (length p) 3) (symbolp (second p)))
                          (fail "bad Pattern ~a" (tree-string p)))
                        (pushnew (second p) vars)
                        (list +pattern+ (second p) (walk (third p) parent pos)))
                       ((or (eq h +blank+) (seq-blank-head-p h))
                        (unless (<= (length p) 2) (fail "bad blank ~a" (tree-string p)))
                        (when (and (seq-blank-head-p h) (flat-head-p parent))
                          (fail "sequence blank directly under ~a" (symbol-name parent)))
                        p)
                       ((or (eq h +condition+) (eq h +pattern-test+))
                        (unless (= (length p) 3) (fail "bad ~a" (symbol-name h)))
                        (list h (walk (second p) parent pos) (third p)))
                       (t (cons (walk h :head 0)
                                (loop for a in (cdr p) for i from 1
                                      collect (walk a h i)))))))))
      (let ((tree (walk pattern nil nil)))
        (%make-compiled-pattern tree (nreverse vars))))))

;;; ------------------------------------------------------------------
;;; match

(defun match (compiled expr &key bindings cond-hook)
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

(defun optional-p (p) (and (consp p) (eq (car p) +optional+)))

(defun atom-match-p (p e)
  (or (eql p e) (and (stringp p) (stringp e) (string= p e))))

(defun blank-head-ok (blank e)
  (or (null (cdr blank)) (eq (second blank) (head-of e))))

(defun m1 (p e b k)
  (if (atom p)
      (and (atom-match-p p e) (funcall k b))
      (let ((h (car p)))
        (cond
          ((eq h +pattern+) (m-pattern (second p) (third p) e b k))
          ((eq h +blank+) (and (blank-head-ok p e) (funcall k b)))
          ((seq-blank-head-p h) nil)
          ((eq h +optional+) (m1 (second p) e b k))
          ((eq h +condition+)
           (m1 (second p) e b
               (lambda (b2) (and (funcall *test-hook* :condition (third p) e b2) (funcall k b2)))))
          ((eq h +pattern-test+)
           (m1 (second p) e b
               (lambda (b2) (and (funcall *test-hook* :pattern-test (third p) e b2) (funcall k b2)))))
          ((flat-head-p h) (match-flat p e b k))
          ((and (eq h +power+) (= (length p) 3)) (m-power p e b k))
          ((and (eq h +complex+) (complexp e) (= (length p) 3))
           (m-ordered (cdr p) (list (realpart e) (imagpart e)) b k))
          (t (and (consp e)
                  (m1 h (car e) b (lambda (b2) (m-ordered (cdr p) (cdr e) b2 k)))))))))

(defun m-pattern (name sub e b k)
  (let ((cell (assoc name b :test #'eq)))
    (if cell
        (and (equal (cdr cell) e) (m1 sub e b k))
        (m1 sub e (acons name e b) k))))

(defun seq-item-p (p)
  (and (consp p)
       (or (seq-blank-head-p (car p))
           (and (eq (car p) +pattern+) (consp (third p)) (seq-blank-head-p (car (third p)))))))

(defun m-ordered (pl el b k)
  (cond ((null pl) (and (null el) (funcall k b)))
        ((seq-item-p (car pl)) (m-seq pl el b k))
        ((null el) nil)
        (t (m1 (car pl) (car el) b (lambda (b2) (m-ordered (cdr pl) (cdr el) b2 k))))))

(defun m-seq (pl el b k)
  (let* ((p (car pl))
         (name (and (eq (car p) +pattern+) (second p)))
         (blank (if name (third p) p))
         (least (if (eq (car blank) +blank-seq+) 1 0))
         (head (second blank)))
    (loop for n from least to (length el)
          for taken = (subseq el 0 n)
          while (or (null head) (every (lambda (x) (eq (head-of x) head)) taken))
          thereis (let ((value (if (= n 1) (car taken) (cons +sequence+ taken)))
                        (rest (nthcdr n el)))
                    (if name
                        (let ((cell (assoc name b :test #'eq)))
                          (if cell
                              (and (equal (cdr cell) value) (m-ordered (cdr pl) rest b k))
                              (m-ordered (cdr pl) rest (acons name value b) k)))
                        (m-ordered (cdr pl) rest b k))))))

(defun power-p (e) (and (consp e) (eq (car e) +power+) (= (length e) 3)))

(defun m-power (p e b k)
  (let ((base (second p)) (ex (third p)))
    (if (optional-p ex)
        ;; b^m_. : in order against a Power, else (or then) through the base with m = default
        (or (and (power-p e)
                 (m1 base (second e) b (lambda (b2) (m1 (second ex) (third e) b2 k))))
            (m1 (second ex) (third ex) b (lambda (b2) (m1 base e b2 k))))
        (and (power-p e)
             (m1 base (second e) b (lambda (b2) (m1 ex (third e) b2 k)))))))

;;; ------------------------------------------------------------------
;;; match-flat: Plus / Times (Flat + Orderless)

(defun bare-blank-p (p)
  (and (consp p)
       (or (equal p (list +blank+))
           (and (eq (car p) +pattern+) (equal (third p) (list +blank+))))))

(defun absorber-p (item) (or (optional-p item) (bare-blank-p item)))

(defun remove-nth (n list)
  (append (subseq list 0 n) (nthcdr (1+ n) list)))

(defun map-subsets (size list fn)
  "Call (FN chosen rest) for each SIZE-element sub-list of LIST (order kept);
return the first non-nil result."
  (labels ((walk (lst need chosen skipped)
             (cond ((zerop need) (funcall fn (reverse chosen) (append (reverse skipped) lst)))
                   ((< (length lst) need) nil)
                   (t (or (walk (cdr lst) (1- need) (cons (car lst) chosen) skipped)
                          (walk (cdr lst) need chosen (cons (car lst) skipped)))))))
    (walk list size nil nil)))

(defun remove-parts (parts list)
  "LIST without one occurrence of each of PARTS, or :fail."
  (let ((rest (copy-list list)))
    (dolist (x parts rest)
      (let ((pos (position x rest :test #'equal)))
        (if pos (setf rest (remove-nth pos rest)) (return :fail))))))

(defun head-compatible-p (item el)
  ;; cheap pre-filter for a one-element claim; t whenever m1 could still match
  (let ((h (and (consp item) (car item))))
    (cond ((or (null h) (not (symbolp h))) t)
          ((or (eq h +pattern+) (eq h +blank+) (eq h +optional+) (eq h +condition+)
               (eq h +pattern-test+) (flat-head-p h) (eq h +complex+))
           t)
          ((eq h +power+) (or (optional-p (third item)) (eq (head-of el) +power+)))
          (t (eq (head-of el) h)))))

(defun collapsible-p (q h)
  "Can item Q stand for an H-expression (and so take a run of >= 2 elements)?
Narrow reading (verify's _can_collapse_to): Q has head H, or Q is b^m_. with
b collapsible.  Wide reading adds a Plus/Times item other than H with exactly
one non-Optional argument that is collapsible."
  (and (consp q)
       (or (eq (car q) h)
           (and (eq (car q) +power+) (= (length q) 3) (optional-p (third q))
                (collapsible-p (second q) h))
           (and *flat-wide* (flat-head-p (car q)) (not (eq (car q) h))
                (= 1 (count-if-not #'optional-p (cdr q)))
                (collapsible-p (find-if-not #'optional-p (cdr q)) h)))))

(defun match-flat (p e b k)
  (let* ((h (car p))
         (elems (if (and (consp e) (eq (car e) h)) (cdr e) (list e)))
         (items (cdr p)))
    (flat-claim (remove-if #'absorber-p items) elems h b
                (lambda (left b2)
                  (flat-absorb (remove-if-not #'absorber-p items) left h b2 k)))))

(defun flat-claim (claimers elems h b k)
  "Each claimer takes one element (or, if collapsible, a run of >= 2); K gets
the leftover elements and the bindings."
  (if (null claimers)
      (funcall k elems b)
      (let ((item (car claimers)) (more (cdr claimers)))
        (or (loop for el in elems
                  for i from 0
                  thereis (and (head-compatible-p item el)
                               (m1 item el b
                                   (lambda (b2) (flat-claim more (remove-nth i elems) h b2 k)))))
            (and (collapsible-p item h)
                 (loop for size from 2 to (length elems)
                       thereis (map-subsets size elems
                                            (lambda (run rest)
                                              (m1 item (cons h run) b
                                                  (lambda (b2) (flat-claim more rest h b2 k)))))))))))

(defun flat-value (run h default)
  (cond ((null run) default)
        ((null (cdr run)) (car run))
        (t (cons h run))))

(defun flat-absorb (absorbers left h b k)
  "Bound absorbers consume their value's parts; unbound ones share the
leftovers -- a blank takes >= 1 element (G-1), an Optional >= 0 (default).
The last absorber, if unbound, takes the whole leftover run directly: only
that size can leave nothing over, so enumerating smaller sub-runs (2^n of
them) is pure waste.  An absorber's pattern is a named Blank, so matching it
calls no condition hook -- the pruning changes no result and no hook call."
  (if (null absorbers)
      (and (null left) (funcall k b))
      (let* ((item (car absorbers))
             (opt (optional-p item))
             (q (if opt (second item) item))
             (default (and opt (third item)))
             (name (and (eq (car q) +pattern+) (second q)))
             (cell (and name (assoc name b :test #'eq))))
        (if cell
            (let ((v (cdr cell)))
              (or (and opt (equal v default)
                       (flat-absorb (cdr absorbers) left h b k))
                  (let ((left2 (remove-parts (if (and (consp v) (eq (car v) h)) (cdr v) (list v))
                                             left)))
                    (and (not (eq left2 :fail))
                         (flat-absorb (cdr absorbers) left2 h b k)))))
            (if (null (cdr absorbers))
                ;; last absorber: the whole leftover run (a blank needs >= 1 element;
                ;; an Optional on an empty leftover takes its default)
                (and (or opt left)
                     (m1 q (flat-value left h default) b
                         (lambda (b2) (flat-absorb nil nil h b2 k))))
                (loop for size from (if opt 0 1) to (length left)
                      thereis (map-subsets size left
                                           (lambda (run rest)
                                             (m1 q (flat-value run h default) b
                                                 (lambda (b2) (flat-absorb (cdr absorbers) rest h b2 k)))))))))))
