;;;; probes/dispatch-index/03-boolcheck-differential.lisp -- ticket 21 step 1:
;;;; does the native boolean-leak check answer exactly what the retired
;;;; Maxima walk answered, on the binding lists and answers the dispatcher
;;;; really checks?
;;;;
;;;; Loaded into a process that already has the rules (the rules core) AND the
;;;; native maxima_rubi_dispatch.lisp.  Wraps mr-contains-boolean-p: every call
;;;; computes both the native answer and ref_containsBoolean (the retired walk,
;;;; defined by the batch file; an error counts as a hit, as under mr-call) and
;;;; returns the REFERENCE answer, so the run itself follows the old path.

(defvar *bd-calls* 0)
(defvar *bd-hits* 0)
(defvar *bd-mismatch* 0)

(let ((native (symbol-function 'mr-contains-boolean-p)))
  (setf (symbol-function 'mr-contains-boolean-p)
        (lambda (e)
          (let ((n (funcall native e))
                (r (multiple-value-bind (v ok) (mr-call '|$ref_containsBoolean| e)
                     (or (not ok) (eq v t)))))
            (incf *bd-calls*)
            (when r (incf *bd-hits*))
            (unless (eq (and n t) (and r t))
              (incf *bd-mismatch*)
              (when (<= *bd-mismatch* 50)
                (mtell "BD MISMATCH native ~A reference ~A on ~M~%" n r e)))
            r))))

(defmfun $bd_report (label)
  (format t "~&BD ~A calls ~D hits ~D mismatches ~D~%" label *bd-calls* *bd-hits* *bd-mismatch*)
  (finish-output)
  '$done)

;; self-check: a reference that cannot be called (a mis-cased symbol makes
;; mfuncall return a noun, which reads as "no boolean" -- the first run of this
;; probe, 2026-09-28, did exactly that) would void the run
(unless (and (eq (mfuncall '|$ref_containsBoolean| '((mtimes) 126 nil)) t)
             (null (mfuncall '|$ref_containsBoolean| '((mplus) $a $b))))
  (error "03-boolcheck-differential: ref_containsBoolean is not callable as the oracle"))
(format t "~&BD oracle self-check passed~%")
