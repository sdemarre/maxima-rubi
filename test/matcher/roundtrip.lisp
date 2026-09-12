;;;; test/matcher/roundtrip.lisp -- the probe-02 per-rule round trip through
;;;; MR-MATCH (matcher substrate spec section 4, P1/P2 gates).
;;;;
;;;; Reads the case file written by `python3 probes/matcher/02-roundtrip.py gen`
;;;; and writes result lines in probe 02's format, so
;;;; `02-roundtrip.py judge` scores them unchanged:
;;;;   PREP <id> <mode> <ok|error:..> <ms>
;;;;   R <id> <variant> <tree|maxima> <mode> <ok|timeout|error|maxerror> <T|NIL> <ms> <bindings> <converted>
;;;;   DONE
;;;; Environment: MR_CASES, MR_RESULTS, MR_NSHARDS, MR_SHARD, MR_LIMIT (as
;;;; probe 02); MR_MODES (default "narrow,wide": *flat-wide* nil / t);
;;;; MR_LEGS (default "tree"; "tree,maxima" once MR-TREE is loaded, Task 8).

(defpackage :mr-roundtrip (:use :cl :mr-match) (:export #:run))
(in-package :mr-roundtrip)

(defun getenv (name default) (or (sb-ext:posix-getenv name) default))

(defun split-on (s ch)
  (loop with start = 0
        for pos = (position ch s :start start)
        collect (subseq s start pos)
        while pos do (setf start (1+ pos))))

(defun now-ns ()
  (multiple-value-bind (s ns) (sb-unix:clock-gettime sb-unix:clock-monotonic)
    (+ (* s 1000000000) ns)))

(defun ms (ns) (format nil "~,4f" (/ ns 1000000.0)))

(defun line (out &rest fields)
  (format out "~{~a~^	~}~%"
          (mapcar (lambda (f) (substitute #\Space #\Newline (substitute #\Space #\Tab (princ-to-string f))))
                  fields)))

(defun load-cases (file nshards shard limit)
  ;; -> list of (id pattern-string cases), cases = ((variant tree maxima) ...)
  (let ((rules nil) (cur nil) (ordinal -1) (taken 0))
    (with-open-file (in file)
      (loop for l = (read-line in nil) while l
            do (let ((f (split-on l #\Tab)))
                 (cond ((string= (first f) "P")
                        (incf ordinal)
                        (setf cur (and (= (mod ordinal nshards) shard)
                                       (or (zerop limit) (< taken limit))
                                       (list (second f) (third f) nil)))
                        (when cur (incf taken) (push cur rules)))
                       ((and cur (string= (first f) "C"))
                        (push (list (third f) (fourth f) (or (fifth f) "")) (third cur)))))))
    (dolist (r rules) (setf (third r) (nreverse (third r))))
    (nreverse rules)))

(defun bindings-string (alist)
  (tree-string (mapcar (lambda (c) (list (car c) (cdr c))) (reverse alist))))

(defun x-name (pattern)
  ;; the Int pattern's second argument (Pattern NAME (Blank Symbol))
  (let ((second (third pattern)))
    (if (and (consp second) (eq (car second) (sym "Pattern"))) (second second) (sym "x"))))

(defvar *converter* nil
  "Task 8: a function (maxima-string) -> tree or :maxima-error; nil = no maxima leg.")

(defun run-one (out id variant leg mode compiled xname integrand convp)
  (let* ((expr (list (sym "Int") (canonicalize integrand) (sym "x")))
         (t0 (now-ns))
         (r (handler-case
                (sb-ext:with-timeout 2
                  (multiple-value-list (match compiled expr :bindings (list (cons xname (sym "x"))))))
              (sb-ext:timeout () :timeout)
              (error (e) (list :error (princ-to-string e)))))
         (dt (- (now-ns) t0))
         (conv (if convp (tree-string integrand) "")))
    (cond ((eq r :timeout) (line out "R" id variant leg mode "timeout" "" (ms dt) "" conv))
          ((eq (first r) :error) (line out "R" id variant leg mode "error" "" (ms dt) (second r) conv))
          (t (line out "R" id variant leg mode "ok" (if (second r) "T" "NIL") (ms dt)
                   (if (second r) (bindings-string (first r)) "()") conv)))))

(defun run-rule (r mode legs out)
  (destructuring-bind (id pat-string cases) r
    (let* ((t0 (now-ns))
           (compiled (handler-case (prepare (read-tree pat-string))
                       (error (e) (list :error (princ-to-string e)))))
           (dt (- (now-ns) t0)))
      (if (consp compiled)
          (line out "PREP" id mode (format nil "error:~a" (second compiled)) (ms dt))
          (let ((xname (x-name (compiled-pattern-tree compiled))))
            (line out "PREP" id mode "ok" (ms dt))
            (dolist (c cases)
              (destructuring-bind (variant tree maxima) c
                (when (member "tree" legs :test #'string=)
                  (run-one out id variant "tree" mode compiled xname (read-tree tree) nil))
                (when (and (member "maxima" legs :test #'string=) *converter* (plusp (length maxima)))
                  (let ((conv (funcall *converter* maxima)))
                    (if (eq conv :maxima-error)
                        (line out "R" id variant "maxima" mode "maxerror" "" "" "" "")
                        (run-one out id variant "maxima" mode compiled xname conv t)))))))))))

(defun run ()
  (let* ((nshards (parse-integer (getenv "MR_NSHARDS" "1")))
         (shard (parse-integer (getenv "MR_SHARD" "0")))
         (limit (parse-integer (getenv "MR_LIMIT" "0")))
         (modes (split-on (getenv "MR_MODES" "narrow,wide") #\,))
         (legs (split-on (getenv "MR_LEGS" "tree") #\,))
         (rules (load-cases (getenv "MR_CASES" "") nshards shard limit))
         (*print-pretty* nil))
    (format t "~&ROUNDTRIP shard ~a/~a: ~a rules, modes ~a, legs ~a~%" shard nshards (length rules) modes legs)
    (with-open-file (out (getenv "MR_RESULTS" "") :direction :output :if-exists :supersede)
      (dolist (mode modes)
        (let ((*flat-wide* (string= mode "wide")))
          (dolist (r rules) (run-rule r mode legs out)))
        (finish-output out))
      (format out "DONE~%"))
    (format t "~&ROUNDTRIP shard ~a done~%" shard)))
