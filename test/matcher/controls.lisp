;;;; test/matcher/controls.lisp -- probe-02 controls (U1/U1r/U2/U2r, H1..H8)
;;;; through MR-MATCH.  Data: `python3 probes/matcher/02-roundtrip.py controls`
;;;; (a Lisp file defining CL-USER::*CONTROLS*), loaded first.  Output, one line
;;;; per control and mode, read by test/matcher/gate.py:
;;;;   CONTROL <mode> <id> <T|NIL> <bindings> <target>
;;;; <target> is the Int expression matched, so gate.py can verify() bindings.

(defpackage :mr-controls (:use :cl :mr-match) (:export #:run))
(in-package :mr-controls)

(defun run (&optional (modes '("narrow" "wide")))
  (let ((*print-pretty* nil) (x (sym "x")))
    (dolist (mode modes)
      (let ((*flat-wide* (string= mode "wide")))
        (dolist (c (symbol-value (find-symbol "*CONTROLS*" :cl-user)))
          (destructuring-bind (id label pat tree note) c
            (declare (ignore label note))
            (let* ((expr (canonicalize (list (sym "Int") (read-tree tree) x)))
                   (compiled (prepare (read-tree pat))))
              (multiple-value-bind (b ok)
                  (match compiled expr :bindings (list (cons x x)))
                (format t "~&CONTROL~c~a~c~a~c~a~c~a~c~a~c~a~%"
                        #\Tab mode #\Tab id #\Tab (if ok "T" "NIL") #\Tab
                        (tree-string (mapcar (lambda (c) (list (car c) (cdr c))) (reverse b)))
                        #\Tab (tree-string (second expr)) #\Tab pat)))))))))
