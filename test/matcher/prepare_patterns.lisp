;;;; test/matcher/prepare_patterns.lisp -- prepare every generated pattern
;;;; string in MR-MATCH: part of the P3 static gate
;;;; (test/check_generated_rules.py; matcher substrate spec section 4 P3).
;;;; No Maxima: plain SBCL.
;;;;
;;;; Run: sbcl --script test/matcher/prepare_patterns.lisp <maxima_rubi_match.lisp> <patterns.tsv>
;;;; TSV lines: <id> TAB <pattern s-expression>.  One FAIL: line per pattern
;;;; that does not read or prepare; ends with "Results: <n> passed, <m> failed".

(let* ((args (last sb-ext:*posix-argv* 2))
       (passed 0)
       (failed 0))
  (load (first args))
  (let ((read-tree (find-symbol "READ-TREE" :mr-match))
        (prepare (find-symbol "PREPARE" :mr-match)))
    (with-open-file (in (second args))
      (loop for line = (read-line in nil)
            while line
            do (let ((tab (position #\Tab line)))
                 (handler-case
                     (progn (funcall prepare (funcall read-tree (subseq line (1+ tab))))
                            (incf passed))
                   (error (e)
                     (incf failed)
                     (format t "FAIL: ~a ~a~%" (subseq line 0 tab)
                             (substitute #\Space #\Newline (princ-to-string e)))))))))
  (format t "Results: ~a passed, ~a failed~%" passed failed))
