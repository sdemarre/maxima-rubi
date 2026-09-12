;;;; test/matcher/spike01.lisp -- the spike-01 cases (probes/matcher/
;;;; 01-mma4max-feasibility.lisp *rules* / *cases*: 71 cases, groups G1-G7, NEG,
;;;; CTL; the 10 SCALE cases live in *scale-cases* and are not read) through
;;;; MR-MATCH + MR-TREE (matcher substrate spec section 4, P2).
;;;;
;;;; The case data is read from the committed spike file as data (its code is
;;;; not loaded -- mma4max is not needed).  Per case: integrand from :target via
;;;; Maxima's simplifier + max->tree, or from :tree; pattern = the rule's compact
;;;; FullForm; condition = the rule's FreeQ[{...}, x] list as the cond hook;
;;;; expected bindings from :expect (Maxima strings, '|' = alternatives).
;;;; Output, read by test/matcher/gate.py --spike:
;;;;   SPIKE <id> <group> <model T|NIL> <ok T|NIL> <detail>

(defpackage :mr-spike01 (:use :cl :mr-match :mr-tree) (:export #:run))
(in-package :mr-spike01)

(defun spike-data (path)
  "-> (values rules cases) from the spike file's defparameter/setf-append forms."
  (unless (find-package :mma) (make-package :mma :use nil))
  (unless (find-package :pat) (make-package :pat :use nil))
  (let ((rules nil) (cases nil) (*read-eval* nil) (*package* (find-package :cl-user)))
    (with-open-file (in path)
      (loop for form = (read in nil :eof)
            until (eq form :eof)
            do (when (consp form)
                 (flet ((data (f) (and (consp f) (eq (car f) 'quote) (second f))))
                   (cond ((and (eq (car form) 'defparameter) (string= (symbol-name (second form)) "*RULES*"))
                          (setf rules (data (third form))))
                         ((and (eq (car form) 'defparameter) (string= (symbol-name (second form)) "*CASES*"))
                          (setf cases (data (third form))))
                         ((and (eq (car form) 'setf) (consp (third form)) (eq (car (third form)) 'append))
                          (let ((more (data (third (third form)))))
                            (cond ((string= (symbol-name (second form)) "*RULES*") (setf rules (append rules more)))
                                  ((string= (symbol-name (second form)) "*CASES*") (setf cases (append cases more)))))))))))
    (values rules cases)))

(defun free-of-p (tree v)
  (cond ((equal tree v) nil)
        ((consp tree) (every (lambda (s) (free-of-p s v)) tree))
        (t t)))

(defun split-on (s ch)
  (loop with start = 0
        for pos = (position ch s :start start)
        collect (subseq s start pos)
        while pos do (setf start (1+ pos))))

(defun parse-expect (s)
  ;; "a=3 b=2 | a=4 b=5" -> ((("a" . tree) ...) ...)
  (mapcar (lambda (alt)
            (loop for tok in (split-on (string-trim " " alt) #\Space)
                  unless (string= tok "")
                    collect (let ((p (position #\= tok)))
                              (cons (subseq tok 0 p) (max->tree (maxima-form (subseq tok (1+ p))))))))
          (split-on s #\|)))

(defun run-case (c rules)
  (destructuring-bind (&key id group model rule target tree swap expect &allow-other-keys) c
    (declare (ignore swap))   ; canonicalize makes the stored factor order irrelevant
    (let* ((r (or (assoc rule rules :test #'string=) (error "no rule ~a" rule)))
           (x (sym "x"))
           (integrand (if tree (canonicalize (read-pattern tree)) (max->tree (maxima-form target))))
           (names (mapcar #'sym (third r)))
           (hook (lambda (b)
                   (let ((xv (cdr (assoc x b))))
                     (every (lambda (n) (let ((cell (assoc n b))) (and cell (free-of-p (cdr cell) xv))))
                            names))))
           (compiled (prepare (read-pattern (second r)))))
      (multiple-value-bind (b matched)
          (match compiled (list (sym "Int") integrand x) :bindings (list (cons x x)) :cond-hook hook)
        (let* ((alts (if (eq expect :none) nil (parse-expect expect)))
               (ok (if (eq expect :none)
                       (not matched)
                       (and matched
                            (some (lambda (alt)
                                    (every (lambda (pair) (equal (cdr (assoc (sym (car pair)) b)) (cdr pair)))
                                           (cons (cons "x" x) alt)))
                                  alts)))))
          (format t "~&SPIKE~c~a~c~a~c~a~c~a~cmatched=~a bindings=~a integrand=~a~%"
                  #\Tab id #\Tab group #\Tab (if model "T" "NIL") #\Tab (if ok "T" "NIL") #\Tab
                  (if matched "T" "NIL")
                  (tree-string (mapcar (lambda (c) (list (car c) (cdr c))) (reverse b)))
                  (tree-string integrand)))))))

(defun run (&optional (path "probes/matcher/01-mma4max-feasibility.lisp"))
  (let ((*print-pretty* nil))
    (multiple-value-bind (rules cases) (spike-data path)
      (format t "~&SPIKE-DATA rules ~a cases ~a~%" (length rules) (length cases))
      (dolist (c cases)
        (handler-case (run-case c rules)
          (error (e) (format t "~&SPIKE~c~a~c~a~cNIL~cNIL~cerror ~a~%"
                             #\Tab (getf c :id) #\Tab (getf c :group) #\Tab #\Tab #\Tab
                             (substitute #\Space #\Newline (princ-to-string e)))))))))
