;;; probes/matcher/02-roundtrip.lisp -- runner for the per-rule round trip
;;; (probes/matcher/02-roundtrip.py documents the method and the verdicts).
;;;
;;; Loaded by 02-roundtrip.mac after 01-mma4max-load.lisp (mma4max) and
;;; 01-mma4max-feasibility.lisp, whose helpers it reuses: fresh-env,
;;; prepare-pattern (fixopts + bindfix), match-once, collect-bindings,
;;; with-cap, now-ns, mm-sym, mm-name, split-on, install-mblank1-nil-guard.
;;;
;;; Environment:  MR_CASES (case file), MR_RESULTS (output), MR_NSHARDS,
;;; MR_SHARD (this process takes the rules whose ordinal mod NSHARDS = SHARD),
;;; MR_LIMIT (optional: only the first N rules of the shard).
;;;
;;; Case file lines (tab-separated):
;;;   H  <Mathematica head>  <Maxima call>   -- converter head table entry
;;;   P  <rule id>  <evaluated LHS, FullForm s-expression>
;;;   C  <rule id>  <variant>  <integrand s-expression>  <Maxima string or empty>
;;; Result lines (tab-separated), written to MR_RESULTS (stray prints of the
;;; matcher go to the maxima log, not into the results):
;;;   PREP  <id>  <mode>  <ok|timeout|error:..>  <ms>
;;;   R  <id>  <variant>  <tree|maxima>  <mode>  <ok|timeout|error|maxerror>
;;;      <T|NIL>  <ms>  <bindings ((name value) ...)>  <converted integrand, maxima leg>
;;;   DONE
;;; mode: pub (mma4max as published), then guard (mblank1 nil-guard installed).

(in-package :cl-user)

(declaim (optimize (speed 1) (safety 1) (debug 1)))

(defvar *rt-readtable*
  (let ((rt (copy-readtable nil)))
    (setf (readtable-case rt) :preserve)
    rt))

(defun rt-read (string)
  (let ((*readtable* *rt-readtable*)
        (*package* (find-package :mma))
        (*read-default-float-format* 'double-float))
    (read-from-string string)))

(defun rt-getenv (name &optional default)
  (or (sb-ext:posix-getenv name) default))

;;; ------------------------------------------------------------------
;;; s-expression printer (package-free names; ratios n/d; #C(re im))

(defun rt-sx (e s)
  (cond ((null e) (write-string "()" s))
        ((consp e)
         (write-char #\( s)
         (loop for (x . more) on e
               do (rt-sx x s)
                  (when more (write-char #\Space s)))
         (write-char #\) s))
        ((complexp e)
         (write-string "#C(" s) (rt-sx (realpart e) s) (write-char #\Space s)
         (rt-sx (imagpart e) s) (write-char #\) s))
        ((typep e 'ratio) (format s "~d/~d" (numerator e) (denominator e)))
        ((integerp e) (format s "~d" e))
        ((floatp e) (format s "~,,,,,,'eE" e))
        ((stringp e) (prin1 e s))
        ((symbolp e) (write-string (symbol-name e) s))
        (t (format s "~a" e))))

(defun rt-sxs (e)
  (with-output-to-string (s) (rt-sx e s)))

;;; ------------------------------------------------------------------
;;; Maxima side: safe parse+simplify, and the converter back to trees

(defun maxima-safe (string)
  ;; parse_string, then evaluate/simplify, each inside errcatch
  (let ((p (maxima::meval `((maxima::$errcatch) ((maxima::$parse_string) ,string)))))
    (if (null (cdr p))
        :maxima-error
        (let ((v (maxima::meval `((maxima::$errcatch) ,(second p)))))
          (if (null (cdr v)) :maxima-error (second v))))))

(defvar *rt-heads* (make-hash-table :test 'eq))

(defun rt-register-head (mm-head call)
  (let ((f (handler-case (maxima-safe call) (error () :maxima-error))))
    (if (and (consp f) (consp (car f)))
        (setf (gethash (caar f) *rt-heads*) (mm-sym mm-head))
        (format t "~&HEAD-FAIL ~a ~a -> ~s~%" mm-head call f))))

(defun rt-unprefix (sym headp)
  (let ((n (symbol-name sym)))
    (cond ((and (> (length n) 3) (string= "mm_" n :end2 3)) (mm-sym (subseq n 3)))
          (headp (mm-sym (format nil "MX_~a" n)))
          (t sym))))

(defun rt-mx->mm (e)
  (cond ((numberp e) e)
        ((symbolp e)
         (case e
           (maxima::$%e (mm-sym "E"))
           (maxima::$%pi (mm-sym "Pi"))
           (maxima::$%i (mm-sym "I"))
           (t (rt-unprefix (mm-name e) nil))))
        ((not (and (consp e) (consp (car e)))) (list (mm-sym "MX_badform")))
        (t
         (let ((op (caar e)))
           (cond ((eq op 'maxima::mplus) (cons (mm-sym "Plus") (mapcar #'rt-mx->mm (cdr e))))
                 ((eq op 'maxima::mtimes) (cons (mm-sym "Times") (mapcar #'rt-mx->mm (cdr e))))
                 ((eq op 'maxima::mexpt) (cons (mm-sym "Power") (mapcar #'rt-mx->mm (cdr e))))
                 ((eq op 'maxima::rat) (/ (second e) (third e)))
                 ((eq op 'maxima::mqapply)
                  (let* ((sub (second e)) (sop (caar sub)))
                    (cons (cond ((eq sop 'maxima::$li) (mm-sym "PolyLog"))
                                ((eq sop 'maxima::$psi) (mm-sym "PolyGamma"))
                                (t (mm-sym (format nil "MX_~a" (symbol-name sop)))))
                          (mapcar #'rt-mx->mm (append (cdr sub) (cddr e))))))
                 (t (cons (or (gethash op *rt-heads*) (rt-unprefix (mm-name op) t))
                          (mapcar #'rt-mx->mm (cdr e)))))))))

(defvar *rt-conv* (make-hash-table :test 'equal))

(defun rt-convert (s)
  (multiple-value-bind (v found) (gethash s *rt-conv*)
    (if found
        v
        (setf (gethash s *rt-conv*)
              (let ((f (handler-case (sb-ext:with-timeout 20 (maxima-safe s))
                         (sb-ext:timeout () :maxima-error)
                         (error () :maxima-error))))
                (if (eq f :maxima-error)
                    f
                    (handler-case (rt-mx->mm f) (error () :maxima-error))))))))

;;; ------------------------------------------------------------------

(defun rt-line (out &rest fields)
  (format out "~{~a~^	~}~%"
          (mapcar (lambda (f) (substitute #\Space #\Newline (substitute #\Space #\Tab (princ-to-string f))))
                  fields)))

(defun rt-ms (ns) (format nil "~,4f" (/ ns 1000000.0)))

(defun rt-failed-p (x)
  (or (eq x :timeout) (and (consp x) (eq (car x) :error))))

(defun rt-status (x)
  (cond ((eq x :timeout) "timeout")
        ((and (consp x) (eq (car x) :error)) (format nil "error:~a" (second x)))
        (t "ok")))

(defun rt-load-cases (file nshards shard limit)
  ;; -> list of (id pattern-string cases), cases = ((variant tree maxima) ...)
  (let ((rules nil) (cur nil) (ordinal -1) (taken 0))
    (with-open-file (in file)
      (loop for line = (read-line in nil) while line
            do (let ((f (split-on line #\Tab)))
                 (cond ((string= (first f) "H") (rt-register-head (second f) (third f)))
                       ((string= (first f) "P")
                        (incf ordinal)
                        (setf cur (and (= (mod ordinal nshards) shard)
                                       (or (zerop limit) (< taken limit))
                                       (list (second f) (third f) nil)))
                        (when cur (incf taken) (push cur rules)))
                       ((and cur (string= (first f) "C"))
                        (push (list (third f) (fourth f) (or (fifth f) "")) (third cur)))))))
    (dolist (r rules) (setf (third r) (nreverse (third r))))
    (nreverse rules)))

(defun rt-match (out id variant leg mode pat integrand convp)
  (let* ((expr (list (mm-sym "Int") integrand (mm-sym "x")))
         (t0 (now-ns))
         (m (with-cap (2) (multiple-value-list (match-once pat expr #'mma::truth))))
         (dt (- (now-ns) t0))
         (conv (if convp (rt-sxs integrand) "")))
    (cond ((eq m :timeout)
           (rt-line out "R" id variant leg mode "timeout" "" (rt-ms dt) "" conv))
          ((eq (car m) :error)
           (rt-line out "R" id variant leg mode "error" "" (rt-ms dt) (second m) conv))
          (t
           (rt-line out "R" id variant leg mode "ok" (if (first m) "T" "NIL") (rt-ms dt)
                    (rt-sxs (mapcar (lambda (b) (list (car b) (cdr b))) (second m)))
                    conv)))))

(defun rt-run-rule (r mode out)
  (destructuring-bind (id pat-string cases) r
    (fresh-env)
    (let* ((t0 (now-ns))
           (pat (with-cap (10) (prepare-pattern (rt-read pat-string))))
           (dt (- (now-ns) t0)))
      (rt-line out "PREP" id mode (rt-status pat) (rt-ms dt))
      (unless (rt-failed-p pat)
        (dolist (c cases)
          (destructuring-bind (variant tree maxima) c
            (rt-match out id variant "tree" mode pat (rt-read tree) nil)
            (when (plusp (length maxima))
              (let ((conv (rt-convert maxima)))
                (if (eq conv :maxima-error)
                    (rt-line out "R" id variant "maxima" mode "maxerror" "" "" "" "")
                    (rt-match out id variant "maxima" mode pat conv t))))))))))

(defun roundtrip-run ()
  (let* ((nshards (parse-integer (rt-getenv "MR_NSHARDS" "1")))
         (shard (parse-integer (rt-getenv "MR_SHARD" "0")))
         (limit (parse-integer (rt-getenv "MR_LIMIT" "0")))
         (rules (rt-load-cases (rt-getenv "MR_CASES") nshards shard limit))
         (*print-pretty* nil)
         (*print-right-margin* 1000000))
    (format t "~&ROUNDTRIP shard ~a/~a: ~a rules~%" shard nshards (length rules))
    (with-open-file (out (rt-getenv "MR_RESULTS") :direction :output :if-exists :supersede)
      (dolist (mode '("pub" "guard"))
        (when (string= mode "guard")
          (install-mblank1-nil-guard))
        (dolist (r rules)
          (rt-run-rule r mode out))
        (finish-output out))
      (format out "DONE~%"))
    (format t "~&ROUNDTRIP shard ~a done~%" shard)))
