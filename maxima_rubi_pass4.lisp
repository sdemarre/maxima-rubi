;; maxima_rubi_pass4.lisp — pass-4 per-candidate implicit-1 scans
;; (class-3 deferred campaign: the prototype + production pass 4 share
;; this seam — spec section 5.2).
;;
;; The pass-4 sweep (the Maxima-level driver %mr_pass4_scan,
;; maxima_rubi_utils.mac) runs, for each bare top-level factor f_i of a
;; 0-fired integrand, a full table scan with *mr-implicit1-which* = i
;; (the findfun shadow, maxima_rubi_implicit1.lisp, then offers f_i as
;; the wrapped candidate — the index is re-evaluated against the
;; remaining factor list at each findfun call, so multi-slot rules get
;; their later slots a fresh candidate; see that file's header). The
;; wrapped object is created and consumed inside the matcher (findfun's
;; return feeds compileeach directly) and never round-trips to the
;; Maxima level — the measured round-trip constraint
;; (maxima_rubi_implicit1.lisp header, 2026-08-27) holds strictly.
;;
;; Gating: the sweep is wired into mr_top AFTER passes 1-3 0-fire,
;; top-level, fb=false ONLY (the Task-4 wiring). Nothing currently
;; passing can change: a passing entry fired in passes 1-3 and never
;; reaches the sweep.
;;
;; Symbol naming: ALL-UPPERCASE typed defmfun names (the lowercase-name
;; uppercasing quirk, maxima_rubi_dispatch.lisp note); (&rest args)
;; dispatch (a fixed-parameter defmfun is not callable in this build).
;; matchreverse: the dispatch.lisp lisp global (the Maxima-level value
;; does not reach it, measured there); %mr_p4_setrev is the setter.
;; *mr-implicit1-which* lives in the implicit-1 file (it loads first);
;; this file consumes it.
;;
;; Measured 2026-08-30 (this build) — return-value and argument
;; conventions that bit the first draft:
;; - a defmfun return is read DIRECTLY as an mobject: a Maxima list is
;;   a cons headed by the (MLIST SIMP) meta (a headless cons of strings
;;   fatals "not of type LIST"; defmfun-check.lisp example shape).
;; - a Maxima string is a plain lisp string (mstringp = stringp);
;;   %mr_p4_diag therefore returns an (MLIST SIMP) cons of strings.
;; - the Maxima integer 0 arrives as a non-NIL object of type BIT —
;;   truthy in CL — so `(if 0 ...)` takes the TRUE arm; the setrev
;;   setter below tests with (not (zerop ...)) instead of plain truth.
;; - rendering a factor the way Maxima string() does (suprv1.lisp
;;   defmspec $string, verbatim body): (coerce (if $grind
;;   (strgrind f) (mstring f)) 'string) under $lispdisp t. A bare
;;   princ-to-string of the meta structure is not Maxima syntax.

(defmfun |$%MR_P4_SETREV| (&rest args)
  (unless (= (length args) 1)
    (merror (intl:gettext "%mr_p4_setrev: expected 1 arg, found ~A")
            (length args)))
  (setf matchreverse (and (first args) (not (zerop (first args)))))
  nil)

(defmfun |$%MR_P4_SETWHICH| (&rest args)
  (unless (= (length args) 1)
    (merror (intl:gettext "%mr_p4_setwhich: expected 1 arg, found ~A")
            (length args)))
  (setf *mr-implicit1-which* (first args))
  nil)

;; One gated pass-4 scan: shadow active (with the current
;; *mr-implicit1-which*), one full table scan, gate off + index reset
;; in unwind-protect. Call with (f, x, table, depth) exactly as
;; %mr_dispatch.
(defmfun |$%MR_DISPATCH_P4| (&rest args)
  (unless (= (length args) 4)
    (merror (intl:gettext "%mr_dispatch_p4: expected 4 args, found ~A")
            (length args)))
  (unwind-protect
      (progn
        (setf *mr-implicit1-active* t)
        (mlambda (mget '|$%MR_DISPATCH| 'mexpr)
                args
                '|$%MR_DISPATCH| t nil))
    (setf *mr-implicit1-active* nil)
    (setf *mr-implicit1-which* nil)))

;; Diagnostic for products that contain an explicit power factor (the
;; shadow-dead case, f1): what the ORIGINAL findfun returns for a
;; non-atomic-base power slot, in both scan directions — the explicit
;; factor that shadows every bare candidate. Returns a Maxima list of
;; strings: ("pick-fwd=<string|none>" "pick-rev=<string|none>"
;;  "nfactors=<n>" "nbare=<b>" "npow=<p>").
(defun |$mr-p4-pick| (e revp)
  (let ((f (mr-orig-findfun-v e 'mexpt 'mtimes)))
    (if f
        (let (($lispdisp t))
          (coerce (if $grind (strgrind f) (mstring f)) 'string))
        "none")))

(defmfun |$%MR_P4_DIAG| (&rest args)
  (unless (= (length args) 1)
    (merror (intl:gettext "%mr_p4_diag: expected 1 arg, found ~A")
            (length args)))
  (let ((f (first args))
        (nf 0) (nb 0) (np 0))
    (when (and (consp f) (eq (caar f) 'mtimes))
      (dolist (g (cdr f))
        (incf nf)
        (if (and (consp g) (eq (caar g) 'mexpt)) (incf np) (incf nb))))
    (let ((fwd (|$mr-p4-pick| f nil))
          (rev (progn
                 (setf matchreverse t)
                 (let ((r (|$mr-p4-pick| f t)))
                   (setf matchreverse nil)
                   r))))
      (list (list 'mlist 'simp)
            (format nil "pick-fwd=~A" fwd)
            (format nil "pick-rev=~A" rev)
            (format nil "nfactors=~A" nf)
            (format nil "nbare=~A" nb)
            (format nil "npow=~A" np)))))
