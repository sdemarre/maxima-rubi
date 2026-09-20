;;;; probes/matcher/19-flat-absorb-cost.lisp -- the SBCL leg of probe 19
;;;; (spec 3.8, the dispatch-cost task).  No Maxima.
;;;;
;;;; Run: sbcl --script 19-flat-absorb-cost.lisp <matcher.lisp> <patterns.tsv> <k> <label>
;;;;
;;;; Three numbers per (matcher, k), all on Int[x*y1*...*yk, x] -- the
;;;; collapsible-claimer shape probe 06 calls "claim<k>" -- matched against
;;;; every generated rule pattern, with x pre-bound as the dispatcher pre-binds
;;;; the integration variable:
;;;;
;;;;   m1        total M1 calls to reach the FIRST complete binding of each
;;;;             pattern (the matcher's own search cost).  Counted by
;;;;             encapsulating M1, so the recursive calls are counted too and
;;;;             no copy of the matcher's code lives in this probe.
;;;;   bindings  the number of COMPLETE bindings, i.e. how many times the
;;;;             dispatcher's cond hook is called under mr_cond_retry.  This is
;;;;             a property of the rule set, not of the matcher: spec 3.8
;;;;             forbids changing it, so it must not move.
;;;;   enum-s    wall seconds to enumerate ALL of those bindings -- the matcher
;;;;             cost the retry loop actually pays.

(load (nth 1 sb-ext:*posix-argv*))
(in-package :mr-match)

(defvar *n-m1* 0)
(let ((original #'m1))
  (setf (symbol-function 'm1)
        (lambda (p e b k) (incf *n-m1*) (funcall original p e b k))))

(defun claim-expr (k)
  (canonicalize
   (list (sym "Int")
         (cons +times+ (cons (sym "x")
                             (loop for i from 1 to k collect (sym (format nil "y~d" i)))))
         (sym "x"))))

(defun load-patterns (file)
  (with-open-file (in file)
    (loop for line = (read-line in nil) while line
          collect (let ((tab (position #\Tab line)))
                    (cons (subseq line 0 tab)
                          (prepare (read-pattern (subseq line (1+ tab)))))))))

(defun seconds-since (t0)
  (/ (float (- (get-internal-real-time) t0) 1.0d0) internal-time-units-per-second))

(let* ((pats (load-patterns (nth 2 sb-ext:*posix-argv*)))
       (k (parse-integer (nth 3 sb-ext:*posix-argv*)))
       (label (nth 4 sb-ext:*posix-argv*))
       (expr (claim-expr k))
       (pre (list (cons (sym "x") (sym "x"))))
       (hot '()))
  ;; first complete binding only -- the search cost
  (setf *n-m1* 0)
  (dolist (p pats)
    (let ((c0 *n-m1*))
      (match (cdr p) expr :bindings pre)
      (push (cons (- *n-m1* c0) (car p)) hot)))
  (let ((m1-first *n-m1*)
        (total 0))
    ;; every complete binding -- what the mr_cond_retry loop pays
    (let ((t0 (get-internal-real-time)))
      (dolist (p pats)
        (match (cdr p) expr :bindings pre
               :cond-hook (lambda (b) (declare (ignore b)) (incf total) nil)))
      (format t "R ~a k ~a m1 ~a bindings ~a enum-s ~,3f~%"
              label k m1-first total (seconds-since t0)))
    (format t "R ~a k ~a top-m1~{ ~a~}~%" label k
            (loop for r in (subseq (sort hot #'> :key #'car) 0 (min 5 (length hot)))
                  collect (format nil "~a=~a" (cdr r) (car r))))))
