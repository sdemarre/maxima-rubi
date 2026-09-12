;;;; test/matcher/maxima-leg.lisp -- the round trip's Maxima leg through MR-TREE
;;;; (matcher substrate spec section 4, P2).  Loaded by test/matcher/roundtrip.mac
;;;; after maxima_rubi_tree.lisp and test/matcher/roundtrip.lisp; binds
;;;; mr-roundtrip::*converter*.  With MR_MODEL_FLAGS=1 the witnesses are
;;;; simplified under radexpand:false and logexpand:false (spec section 3.3 arm).

(in-package :mr-roundtrip)

(when (equal (sb-ext:posix-getenv "MR_MODEL_FLAGS") "1")
  (setf maxima::$radexpand nil
        maxima::$logexpand nil))

(defun maxima-safe (string)
  ;; parse_string, then evaluate/simplify, each inside errcatch (probe 02's maxima-safe)
  (let ((p (maxima::meval `((maxima::$errcatch) ((maxima::$parse_string) ,string)))))
    (if (null (cdr p))
        :maxima-error
        (let ((v (maxima::meval `((maxima::$errcatch) ,(second p)))))
          (if (null (cdr v)) :maxima-error (second v))))))

(defun mm-head (op)
  ;; probe 02 writes heads without a Maxima function as mm_<Head>(...); Maxima's
  ;; reader inverts the case of an all-lowercase name (mm_sin -> $MM_SIN), so
  ;; compare the case-restored name
  (let ((n (mr-tree:maxima-name op)))
    (and (> (length n) 3) (string= "mm_" n :end2 3) (sym (subseq n 3)))))

(setf *converter*
      (lambda (string)
        (handler-case
            (sb-ext:with-timeout 20
              (let ((f (maxima-safe string)))
                (if (eq f :maxima-error)
                    f
                    (let ((mr-tree:*unknown-head-hook* #'mm-head))
                      (mr-tree:max->tree f)))))
          (sb-ext:timeout () :maxima-error)
          (error () :maxima-error))))
