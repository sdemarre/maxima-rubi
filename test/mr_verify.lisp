;;; test/mr_verify.lisp -- the corpus checker's per-stage CPU limit
;;; (.scratch/corpus-harness/issues/06; loaded by test/mr_verify.mac).
;;;
;;; mr_cpu_timed(expr, secs) evaluates EXPR and returns [value], the
;;; symbol `timeout` once the process has spent SECS more seconds of user
;;; CPU on it, or `heaplimit` when it fills the heap (below). A Maxima
;;; error inside EXPR propagates as usual (the caller errcatches), and the
;;; timer is disarmed on every exit.
;;;
;;; CPU, not wall: the corpus cap is CPU seconds so that a verdict does not
;;; depend on how loaded the machine was (AGENTS.md, "The per-entry cap is
;;; CPU seconds"), and a per-stage limit must follow the same rule. The
;;; timer is ITIMER_VIRTUAL (user CPU of this process), delivered as
;;; SIGVTALRM, which SBCL itself does not use. sb-ext:with-timeout was the
;;; alternative and is WALL time. Measured 2026-09-28 on
;;; branch_5_50_base_84_g4204fb669 / SBCL 2.6.7: a 1.5 s limit on a runaway
;;; factor() returned after 1.70 s of elapsed_run_time (which also counts
;;; system time), a 0.5 s limit after 0.55 s.

(in-package :maxima)

;;; The same timer guards the HEAP. Heap exhaustion is fatal in SBCL (the
;;; process drops into ldb), and a checker stage can allocate a gigabyte well
;;; inside its CPU limit: 4.5.1.2 e714, measured 2026-09-28, filled the 1 GB
;;; dynamic space during a radcan-family stage and the entry died as `error'.
;;; So the timer ticks every +mr-tick-usec+ of CPU and each tick also reads
;;; the dynamic-space usage; above $mr_heap_fraction of the dynamic space the
;;; stage is abandoned with `heaplimit'.
;;;
;;; The reading counts garbage too, and garbage promoted to an older
;;; generation outlives the nursery collections, so after one stage is
;;; stopped the next can read over the limit on that garbage alone and stop
;;; at its first tick. Forcing a collection does not pay here (measured
;;; 2026-09-28 in the rules core: a gen-2 GC 0.8 s with nothing to free,
;;; 26.8 s to reclaim 320 MB; a full GC 2.2 s), and a GC from inside the
;;; handler deadlocks on a futex. So a heap stop may cut the rest of that
;;; entry's stages -- each is named "(heap)" in the tag -- which is the price
;;; of the entry not dying; it concerns the rare entry that fills the heap
;;; (2 of the 1,530 re-checked unverified entries).

(define-condition mr-cpu-timeout (error) ())
(define-condition mr-heap-limit (error) ())

(defconstant +mr-tick-usec+ 20000)
(defmvar $mr_heap_fraction 0.6)
(defvar *mr-ticks-left* 0)

(defun mr-vtalrm-handler (signal info context)
  (declare (ignore signal info context))
  (cond ((> (sb-kernel:dynamic-usage)
            (* $mr_heap_fraction (sb-ext:dynamic-space-size)))
         (error 'mr-heap-limit))
        ((<= (decf *mr-ticks-left*) 0)
         (error 'mr-cpu-timeout))))

(defmspec $mr_cpu_timed (form)
  (let ((*mr-ticks-left* (max 1 (ceiling (* (meval (third form)) 1000000)
                                         +mr-tick-usec+))))
    (sb-sys:enable-interrupt sb-unix:sigvtalrm #'mr-vtalrm-handler)
    (unwind-protect
         (handler-case
             (progn
               (sb-unix:unix-setitimer :virtual 0 +mr-tick-usec+ 0 +mr-tick-usec+)
               (list '(mlist simp) (meval (second form))))
           (mr-cpu-timeout () '$timeout)
           (mr-heap-limit () '$heaplimit))
      (sb-unix:unix-setitimer :virtual 0 0 0 0))))

;;; mr_flush() -- push buffered output to the driver's pipe now. The driver
;;; reads a marker line (ANSWERED, NUMERIC) from a process it may then kill
;;; at its CPU cap; an unflushed line would be lost with it.
(defun $mr_flush ()
  (finish-output *standard-output*)
  '$done)
