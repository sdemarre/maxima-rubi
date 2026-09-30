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

;;; NOT subclasses of ERROR: Maxima's errcatch catches every Lisp error
;;; (errset.lisp, its second handler-case clause), so a tick landing inside an
;;; errcatch in the stage's own code -- Maxima's numeric hypergeometric has
;;; them -- was swallowed there, and the stage ran on past its limit with a
;;; result decided by where the tick landed (7.4.1 e190, 2026-09-29: the same
;;; residual read `declined' or `mismatch' run to run; test_mr_verify.mac).
;;; A SERIOUS-CONDITION is still signalled with ERROR and still reaches the
;;; handler-case in mr_cpu_timed, and no Maxima handler catches it.
(define-condition mr-cpu-timeout (serious-condition) ())
(define-condition mr-heap-limit (serious-condition) ())

;;; THREADS. The timer signal is process-directed, and SBCL starts a
;;; finalizer thread lazily, so a tick can be delivered to that thread instead
;;; of the one running the stage (4.1.7 e516, measured 2026-09-28: the handler
;;; ran in the finalizer thread, read the tick count there -- unbound, so the
;;; global 0 -- signalled the timeout in that thread and dropped it into its
;;; debugger). So the arming thread is recorded globally and a tick taken by
;;; any other thread is forwarded to it with sb-thread:interrupt-thread (the
;;; mechanism sb-ext:with-timeout uses). *mr-timer-active* is bound true only
;;; inside mr_cpu_timed: a tick that arrives outside a stage -- a forwarded
;;; one landing late -- is ignored rather than signalled at top level.

(defconstant +mr-tick-usec+ 20000)
(defmvar $mr_heap_fraction 0.6)
(defvar *mr-ticks-left* 0)
(defvar *mr-timer-active* nil)
(defvar *mr-timer-thread* nil)

(defun mr-tick ()
  (when *mr-timer-active*
    (cond ((> (sb-kernel:dynamic-usage)
              (* $mr_heap_fraction (sb-ext:dynamic-space-size)))
           (error 'mr-heap-limit))
          ((<= (decf *mr-ticks-left*) 0)
           (error 'mr-cpu-timeout)))))

(defun mr-vtalrm-handler (signal info context)
  (declare (ignore signal info context))
  (let ((owner *mr-timer-thread*))
    (cond ((eq sb-thread:*current-thread* owner) (mr-tick))
          ((and owner (sb-thread:thread-alive-p owner))
           (sb-thread:interrupt-thread owner #'mr-tick)))))

;;; BINDINGS. Maxima unbinds block locals and function parameters from its
;;; own BINDLIST, and a frame is unbound on a non-local exit only when it was
;;; fully set up: mbinding-sub (maxmac.lisp) sets its WIN flag after mbind
;;; returns and unbinds only if it is set. Maxima's own exits are synchronous
;;; and never land in between; a timer tick is asynchronous and does. A
;;; frame stranded there stays on the bindlist, and every enclosing block then
;;; unbinds the wrong variables on its way out (7.4.1 e190, 2026-09-29: x, a,
;;; str, success and the checker's own locals were left bound as globals, and
;;; the next stages ran on a residual with x bound -- a proof in 0.004 s on one
;;; run, none on the next). So mr_cpu_timed does what Maxima's mcatch does
;;; (suprv1.lisp): it records (bindlist . loclist) on entry and unwinds both
;;; back to it with errlfun1 on the way out. On a normal return they are
;;; already back and it does nothing.
(defmspec $mr_cpu_timed (form)
  (let ((*mr-ticks-left* (max 1 (ceiling (* (meval (third form)) 1000000)
                                         +mr-tick-usec+)))
        (*mr-timer-active* t)
        (saved (cons bindlist loclist)))
    (setq *mr-timer-thread* sb-thread:*current-thread*)
    (sb-sys:enable-interrupt sb-unix:sigvtalrm #'mr-vtalrm-handler)
    (unwind-protect
         (handler-case
             (progn
               (sb-unix:unix-setitimer :virtual 0 +mr-tick-usec+ 0 +mr-tick-usec+)
               (list '(mlist simp) (meval (second form))))
           (mr-cpu-timeout () '$timeout)
           (mr-heap-limit () '$heaplimit))
      (sb-unix:unix-setitimer :virtual 0 0 0 0)
      (errlfun1 saved))))

;;; mr_flush() -- push buffered output to the driver's pipe now. The driver
;;; reads a marker line (ANSWERED, NUMERIC) from a process it may then kill
;;; at its CPU cap; an unflushed line would be lost with it.
(defun $mr_flush ()
  (finish-output *standard-output*)
  '$done)

;;; mr_f1_num(ar, ai, b1r, b1i, b2r, b2i, cr, ci, xr, xi, yr, yi) -- Appell's
;;; F1(a; b1, b2; c; x, y) at a numeric point, each argument given as its real
;;; and imaginary part: [re, im], or false when it cannot be evaluated here
;;; (test/mr_verify.mac mr_f1_float is the caller;
;;; .scratch/corpus-harness/issues/06 item 2: 434 of the 968 entries whose
;;; numeric check declined carry AppellF1, probes/verify-stages/09).
;;;
;;; The double series sum (a)_{m+n} (b1)_m (b2)_n / ((c)_{m+n} m! n!) x^m y^n,
;;; after whichever of the identity and three Euler-type transformations
;;;   (1-x)^-b1 (1-y)^-b2 F1(c-a; b1, b2; c; x/(x-1), y/(y-1))
;;;   (1-x)^-a F1(a; c-b1-b2, b2; c; x/(x-1), (y-x)/(1-x))
;;;   (1-y)^-a F1(a; b1, c-b1-b2; c; (x-y)/(1-y), y/(y-1))
;;; leaves the smaller largest argument modulus; none under 0.99 -> false.
;;; NOT a sum of Maxima's own 2F1: its float evaluation is wrong at large
;;; parameters (measured 2026-09-29, branch_5_50_base_84_g4204fb669:
;;; hypergeometric([60.4, 0.7], [62.2], 0.6) floats to 828.9, the true value
;;; is ~1.9), and the one-sum form F1 = sum_k c_k x^k 2F1(a+k, b2; c+k; y)
;;; needs exactly those. Only arithmetic errors are caught here: the stage
;;; timer's conditions must reach mr_cpu_timed.
(defun mr-f1-series (a b1 b2 c x y)
  (declare (type (complex double-float) a b1 b2 c x y))
  (let ((total #c(0d0 0d0)) (am #c(1d0 0d0)) (quiet 0))
    (declare (type (complex double-float) total am))
    (dotimes (m 5000 nil)
      (let ((row #c(0d0 0d0)) (tn am) (iq 0))
        (declare (type (complex double-float) row tn))
        (dotimes (n 5000)
          (incf row tn)
          (if (<= (abs tn) (* 1d-17 (max (abs row) (abs total) 1d-300)))
              (incf iq)
              (setf iq 0))
          (when (>= iq 3) (return))
          (setf tn (/ (* tn (+ a m n) (+ b2 n) y) (* (+ c m n) (+ n 1)))))
        (incf total row)
        (if (<= (abs row) (* 1d-17 (max (abs total) 1d-300)))
            (incf quiet)
            (setf quiet 0))
        (when (>= quiet 3) (return total))
        (setf am (/ (* am (+ a m) (+ b1 m) x) (* (+ c m) (+ m 1))))))))

(defun mr-f1 (a b1 b2 c x y)
  (let* ((cands (list (list 1 a b1 b2 c x y)
                      (list (* (expt (- 1 x) (- b1)) (expt (- 1 y) (- b2)))
                            (- c a) b1 b2 c (/ x (- x 1)) (/ y (- y 1)))
                      (list (expt (- 1 x) (- a)) a (- c b1 b2) b2 c
                            (/ x (- x 1)) (/ (- y x) (- 1 x)))
                      (list (expt (- 1 y) (- a)) a b1 (- c b1 b2) c
                            (/ (- x y) (- 1 y)) (/ y (- y 1)))))
         (size (lambda (k) (max (abs (sixth k)) (abs (seventh k)))))
         (best nil))
    (dolist (k cands)
      ;; a transformation with a pole at this point (x or y = 1) is skipped
      (let ((kk (handler-case
                    (mapcar (lambda (v) (coerce v '(complex double-float))) k)
                  (arithmetic-error () nil))))
        (when (and kk (or (null best) (< (funcall size kk) (funcall size best))))
          (setf best kk))))
    (when (and best (< (funcall size best) 0.99d0))
      (let ((s (apply #'mr-f1-series (rest best))))
        (and s (* (first best) s))))))

(defun $mr_f1_num (ar ai b1r b1i b2r b2i cr ci xr xi yr yi)
  (flet ((z (re im) (complex (float re 1d0) (float im 1d0))))
    (let ((v (handler-case
                 (mr-f1 (z ar ai) (z b1r b1i) (z b2r b2i) (z cr ci) (z xr xi) (z yr yi))
               (arithmetic-error () nil))))
      (if v (list '(mlist simp) (realpart v) (imagpart v)) nil))))
