;;;; probes/dispatch-index/04-geteqr-differential.lisp -- ticket 21 step 2:
;;;; does the native geteqR return exactly what the retired Maxima walk
;;;; returned, on the mm lists and names the generated conds and repls really
;;;; look up?
;;;;
;;;; Loaded into a process that already has the rules (the rules core) AND the
;;;; native maxima_rubi_dispatch.lisp.  Wraps |$geteqR|: every call computes
;;;; both the native answer and ref_geteqR (the retired walk, defined by the
;;;; batch file), compares them as Lisp printed forms (the same internal
;;;; object, not merely =), and returns the REFERENCE answer, so the run
;;;; itself follows the old path.  An error on either side is compared too.

(defvar *gd-calls* 0)
(defvar *gd-mismatch* 0)

(defun gd-form (thunk)
  (handler-case (format nil "~s" (funcall thunk))
    (error () :error)))

(let ((native (symbol-function '|$geteqR|)))
  (setf (symbol-function '|$geteqR|)
        (lambda (&rest args)
          (let ((n (gd-form (lambda () (apply native args))))
                (r (gd-form (lambda () (apply #'mfuncall '|$ref_geteqR| args)))))
            (incf *gd-calls*)
            (unless (equal n r)
              (incf *gd-mismatch*)
              (when (<= *gd-mismatch* 50)
                (mtell "GD MISMATCH native ~A reference ~A on ~M~%" n r (cons '(mlist) args))))
            (apply #'mfuncall '|$ref_geteqR| args)))))

(defmfun $gd_report (label)
  (format t "~&GD ~A calls ~D mismatches ~D~%" label *gd-calls* *gd-mismatch*)
  (finish-output)
  '$done)

;; self-check: the oracle must be callable (a mis-cased symbol makes mfuncall
;; return a noun -- probe 03's first run, 2026-09-28)
(unless (eql (mfuncall '|$ref_geteqR| '((mlist) ((mequal) $a 7)) '$a) 7)
  (error "04-geteqr-differential: ref_geteqR is not callable as the oracle"))
(format t "~&GD oracle self-check passed~%")
