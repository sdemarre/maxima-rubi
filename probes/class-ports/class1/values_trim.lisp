;;; probes/class-ports/class1/values_trim.lisp -- PROBE OVERLAY (not a fix as
;;; written): drop the rule-record globals _mr_rule_<key>_r<n> from Maxima's
;;; `values` infolist. The symbols stay bound (nothing reads them after
;;; load: the handles live in mr_rules_<key>). Every binding of a globally
;;; unbound variable (a function parameter, a block local) goes through MSET
;;; -> ADD2LNC (a MEMALIKE scan of `values`) and back through
;;; MUNBIND-MAKUNBOUND (a DELETE over `values`), mlisp.lisp L518-594/L2523,
;;; so each such binding costs two walks of this list.
(in-package :maxima)
(let ((n0 (length (cdr $values))))
  (setf $values
        (cons (car $values)
              (remove-if (lambda (s)
                           (and (symbolp s)
                                (let ((n (symbol-name s)))
                                  (and (> (length n) 9) (string-equal "$_mr_rule_" n :end2 10)))))
                         (cdr $values))))
  (format t "~&VALUES-TRIM ~d -> ~d~%" n0 (length (cdr $values))))
