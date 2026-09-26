;;; probes/class-ports/class1/gcstat.lisp -- SBCL GC / heap readings for probes.
(in-package :maxima)
(defun get-gc-ms () (round (* 1000 sb-ext:*gc-run-time*) internal-time-units-per-second))
(defun get-dyn-mb () (round (sb-kernel:dynamic-usage) 1048576))
(defun get-bytes-consed-mb () (round (sb-ext:get-bytes-consed) 1048576))
