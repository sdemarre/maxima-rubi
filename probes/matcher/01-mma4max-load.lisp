;;; Load Fateman's mma4max (reference/fateman/lisp/mma4max) into Maxima's SBCL.
;;; File order follows mma4max/init.lisp *mma-files* (plus mma.lisp first, as
;;; load-mma-lisp does).  Loaded from source; any edits are listed in
;;; *mma-load-edits* and reported by the probe.

(in-package :cl-user)

(defparameter *mma-dir*
  (merge-pathnames "reference/fateman/lisp/mma4max/"
                   (or (sb-ext:posix-getenv "MR_ROOT") "/home/serge/src/maxima-rubi/")))

(defparameter *mma-files*
  '("mma" "uconsalt" "parser" "stack1" "disp1" "poly" "rat1" "simp1" "pf"
    "eval" "newmatch" "diffrat" "morefuns" "function" "mma2maxfun" "batch"))

(defparameter *mma-load-log* nil)

(defun mma-load-all ()
  (dolist (f *mma-files*)
    (let ((path (merge-pathnames (concatenate 'string f ".lisp") *mma-dir*)))
      (handler-case
          (handler-bind ((warning #'muffle-warning))
            (let ((*package* (find-package :cl-user)))
              (load path))
            (push (list f :ok) *mma-load-log*))
        (error (e)
          (push (list f :error (princ-to-string e)) *mma-load-log*)))))
  (setf *mma-load-log* (nreverse *mma-load-log*))
  (dolist (r *mma-load-log*) (format t "~&LOAD ~{~a~^ ~}~%" r))
  ;; the symbol table + Plus/Times Flat/Orderless/Default attributes are set
  ;; by initialize-mma, which mma4max's own entry point (tl) calls
  (funcall (intern "INITIALIZE-MMA" :mma))
  (format t "~&LOAD initialize-mma OK~%"))
